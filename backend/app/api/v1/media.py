from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
import os
import re
import shutil
import hashlib
import json
from pathlib import Path
from app.core.config import settings
from app.core.database import get_db
from app.schemas.media import Media, MediaCreate, MediaUpdate
from app.crud import media as media_crud
from app.services.media_processor import MediaProcessor

router = APIRouter()
media_processor = MediaProcessor()

def sanitize_filename(filename: str) -> str:
    """
    Convierte un nombre de archivo a uno seguro para usar en el sistema de archivos.
    - Elimina caracteres no permitidos
    - Reemplaza espacios con guiones bajos
    - Asegura que sea único
    """
    # Obtener nombre y extensión
    name, ext = os.path.splitext(filename)
    # Limpiar caracteres no permitidos
    name = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    # Evitar nombres vacíos
    if not name:
        name = 'file'
    # Reconstruir nombre con extensión
    return f"{name}{ext.lower()}"

def is_supported_file(file: UploadFile) -> bool:
    """Verifica si el archivo es de un tipo soportado"""
    mime_type = get_correct_mime_type(file)
    return mime_type.startswith('image/') or mime_type.startswith('video/')

# Definir una función para obtener el tipo MIME correcto
def get_correct_mime_type(file: UploadFile) -> str:
    """Determina el tipo MIME correcto para el archivo."""
    if file.filename:
        ext = Path(file.filename).suffix.lower()
        if ext in ['.heic', '.heif']:
            return 'image/heic'
    return file.content_type

@router.post("/upload/", response_model=Media)
async def upload_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Log de información del archivo
    print(f"DEBUG: Intento de subida de archivo:")
    print(f"DEBUG: Nombre del archivo: {file.filename}")
    print(f"DEBUG: Tipo de contenido original: {file.content_type}")
    print(f"DEBUG: Tamaño: {file.size if hasattr(file, 'size') else 'desconocido'}")

    # Determinar tipo MIME correcto
    content_type = get_correct_mime_type(file)
    print(f"DEBUG: Tipo de contenido ajustado: {content_type}")

    if not is_supported_file(file):
        error_msg = f"Tipo de archivo no soportado: {content_type}"
        print(f"DEBUG: ERROR - {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Sanitizar nombre de archivo
    safe_filename = sanitize_filename(file.filename)
    print(f"DEBUG: Nombre sanitizado: {safe_filename}")
    
    # Crear directorio de uploads si no existe
    uploads_dir = settings.UPLOADS_DIR
    uploads_dir.mkdir(parents=True, exist_ok=True)
    print(f"DEBUG: Directorio de uploads verificado: {uploads_dir}")
    
    # Guardar archivo
    file_path = uploads_dir / safe_filename
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"DEBUG: Archivo guardado exitosamente en: {file_path}")
    except Exception as e:
        print(f"DEBUG: ERROR guardando archivo - {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error guardando archivo: {str(e)}")
    finally:
        file.file.close()
    
    # Crear entrada en la base de datos
    media_create = MediaCreate(
        filename=safe_filename,
        mime_type=content_type,  # Usamos el tipo MIME corregido
        file_size=os.path.getsize(file_path)
    )
    
    # Guardar rutas relativas en la base de datos
    file_relative_path = f"/uploads/{safe_filename}"
    print(f"DEBUG: Guardando en BD con ruta relativa: {file_relative_path}")
    db_media = media_crud.create_media(db, media_create, file_relative_path)
    
    # Procesar archivo
    try:            # Crear miniatura
        thumbnail_path = media_processor.create_thumbnail(str(file_path), content_type)
        if thumbnail_path:
            print(f"DEBUG: Miniatura creada con éxito. Ruta: {thumbnail_path}")
            
            # La ruta ya viene en formato web estandarizado: /thumbnails/thumb_nombre.jpg
            # Verificar que sigue el formato correcto
            if not str(thumbnail_path).startswith('/thumbnails/'):
                print(f"DEBUG: Normalizando ruta de miniatura")
                # Normalizar la ruta en caso de error
                thumb_name = Path(str(thumbnail_path)).name
                thumbnail_path = f"/thumbnails/{thumb_name}"
            
            # Guardar la ruta web en la base de datos
            print(f"DEBUG: Actualizando ruta de miniatura en BD: {thumbnail_path}")
            db_media.thumbnail_path = thumbnail_path
        
        # Extraer metadatos
        print(f"DEBUG: Extrayendo metadatos del archivo")
        metadata = media_processor.extract_metadata(str(file_path), content_type)
        for key, value in metadata.items():
            setattr(db_media, key, value)
            print(f"DEBUG: Metadato extraído - {key}: {value}")
        
        # Predecir evento si es imagen
        if content_type.startswith('image/'):
            print(f"DEBUG: Prediciendo evento para imagen")
            event_type, confidence = media_processor.predict_event(str(file_path))
            db_media.event_type = event_type
            db_media.event_confidence = confidence
            print(f"DEBUG: Evento predicho - {event_type} ({confidence})")
        
        # Crear copia del archivo con formato fecha-evento en directorio processed
        print(f"DEBUG: Creando copia procesada del archivo con formato fecha-evento")
        processed_path = media_processor.create_processed_copy(
            str(file_path), 
            db_media.creation_date, 
            db_media.event_type
        )
        if processed_path:
            print(f"DEBUG: Copia procesada creada exitosamente en: {processed_path}")
            db_media.processed_file_path = processed_path
        
        print(f"DEBUG: Guardando cambios en BD")
        db.commit()
        db.refresh(db_media)
        print(f"DEBUG: Proceso completado exitosamente")
        
    except Exception as e:
        print(f"DEBUG: ERROR procesando archivo - {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")
    
    return db_media

@router.get("/", response_model=List[Media])
def list_media(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de medios con caché efectiva"""
    
    # Generar ETag basado en los parámetros de consulta
    params = f"{skip}-{limit}"
    etag = hashlib.md5(params.encode()).hexdigest()
    
    # Obtener media items
    media_items = media_crud.get_all_media(db, skip=skip, limit=limit)
    
    # Generar nuevo ETag basado en los datos
    data_etag = hashlib.md5(json.dumps([m.id for m in media_items]).encode()).hexdigest()
    
    # Configurar headers de caché
    headers = {
        'ETag': data_etag,
        'Cache-Control': 'public, max-age=30',  # Cache por 30 segundos
        'Vary': 'Accept-Encoding'  # Variar caché por compresión
    }
    
    print(f"DEBUG: Recuperados {len(media_items)} elementos de media (skip={skip}, limit={limit})")
    
    # Convertir objetos SQLAlchemy a diccionarios serializables
    media_dicts = []
    for m in media_items:
        media_dict = {
            'id': m.id,
            'filename': m.filename,
            'file_path': m.file_path,
            'thumbnail_path': m.thumbnail_path,
            'processed_file_path': m.processed_file_path,
            'mime_type': m.mime_type,
            'file_size': m.file_size,
            'width': m.width,
            'height': m.height,
            'duration': m.duration,
            'latitude': m.latitude,
            'longitude': m.longitude,
            'creation_date': m.creation_date.isoformat() if m.creation_date else None,
            'event_type': m.event_type,
            'event_confidence': m.event_confidence,
            'uploaded_at': m.uploaded_at.isoformat() if m.uploaded_at else None,
            'updated_at': m.updated_at.isoformat() if m.updated_at else None
        }
        media_dicts.append(media_dict)
    
    return Response(
        content=json.dumps(media_dicts),
        media_type='application/json',
        headers=headers
    )

@router.get("/{media_id}", response_model=Media)
def get_media(
    media_id: int,
    db: Session = Depends(get_db)
):
    db_media = media_crud.get_media(db, media_id)
    if db_media is None:
        raise HTTPException(status_code=404, detail="Media not found")
    return db_media

@router.patch("/{media_id}", response_model=Media)
def update_media(
    media_id: int,
    media_update: MediaUpdate,
    db: Session = Depends(get_db)
):
    # Obtener el medio antes de actualizar
    db_media = media_crud.get_media(db, media_id)
    if db_media is None:
        raise HTTPException(status_code=404, detail="Media not found")
        
    # Actualizar datos
    updated_media = media_crud.update_media(db, media_id, media_update)
    
    # Si se actualizó el tipo de evento, regenerar el archivo procesado
    if media_update.event_type is not None:
        print(f"DEBUG: Se actualizó el evento a {media_update.event_type}. Regenerando archivo procesado...")
        
        # Construir ruta absoluta al archivo original
        original_file_path = settings.STORAGE_DIR / db_media.file_path.lstrip('/')
        
        # Si existe el archivo, crear una nueva versión procesada
        if original_file_path.exists():
            processed_path = media_processor.create_processed_copy(
                str(original_file_path),
                db_media.creation_date, 
                updated_media.event_type
            )
            
            if processed_path:
                print(f"DEBUG: Nueva versión del archivo procesado creada en: {processed_path}")
                updated_media.processed_file_path = processed_path
                db.commit()
                db.refresh(updated_media)
    
    return updated_media

@router.delete("/{media_id}")
def delete_media(
    media_id: int,
    db: Session = Depends(get_db)
):
    success = media_crud.delete_media(db, media_id)
    if not success:
        raise HTTPException(status_code=404, detail="Media not found")
    return {"message": "Media deleted successfully"}

@router.post("/regenerate-processed-files/", response_model=dict)
def regenerate_processed_files(
    db: Session = Depends(get_db)
):
    """
    Regenera todos los archivos procesados basados en la fecha y tipo de evento.
    """
    try:
        # Obtener todos los archivos
        all_media = media_crud.get_all_media(db)
        
        count_success = 0
        count_failed = 0
        
        for media_item in all_media:
            try:
                # Solo procesar si tiene ruta de archivo
                if not media_item.file_path:
                    continue
                    
                # Construir ruta absoluta al archivo original
                original_file_path = settings.STORAGE_DIR / media_item.file_path.lstrip('/')
                
                # Verificar que el archivo exista
                if not original_file_path.exists():
                    print(f"Archivo no encontrado: {original_file_path}")
                    count_failed += 1
                    continue
                    
                # Crear archivo procesado
                processed_path = media_processor.create_processed_copy(
                    str(original_file_path),
                    media_item.creation_date,
                    media_item.event_type
                )
                
                if processed_path:
                    # Actualizar la ruta en la base de datos
                    media_item.processed_file_path = processed_path
                    db.commit()
                    print(f"Archivo procesado regenerado: {processed_path}")
                    count_success += 1
                else:
                    count_failed += 1
                    
            except Exception as e:
                print(f"Error procesando archivo {media_item.id} - {media_item.filename}: {str(e)}")
                count_failed += 1
        
        return {
            "message": f"Proceso completado. {count_success} archivos procesados correctamente. {count_failed} archivos fallaron.",
            "success_count": count_success,
            "failed_count": count_failed
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerando archivos: {str(e)}")
