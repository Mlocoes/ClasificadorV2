from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from pathlib import Path
import re
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

@router.post("/upload/", response_model=Media)
async def upload_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validar tipo de archivo
    if not (file.content_type.startswith('image/') or file.content_type.startswith('video/')):
        raise HTTPException(status_code=400, detail="Tipo de archivo no soportado")
    
    # Sanitizar nombre de archivo
    safe_filename = sanitize_filename(file.filename)
    
    # Crear directorio de uploads si no existe
    uploads_dir = settings.UPLOADS_DIR
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Guardar archivo
    file_path = uploads_dir / safe_filename
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()
    
    # Crear entrada en la base de datos
    media_create = MediaCreate(
        filename=safe_filename,
        mime_type=file.content_type,
        file_size=os.path.getsize(file_path)
    )
    
    # Guardar rutas relativas en la base de datos
    file_relative_path = f"/uploads/{safe_filename}"
    db_media = media_crud.create_media(db, media_create, file_relative_path)
    
    # Procesar archivo
    try:
        # Crear miniatura
        thumbnail_path = media_processor.create_thumbnail(str(file_path), file.content_type)
        if thumbnail_path:
            print(f"ENDPOINT: Miniatura creada con éxito. Ruta recibida: {thumbnail_path}")
            
            # La ruta ya viene en formato web estandarizado: /thumbnails/thumb_nombre.jpg
            # Verificar que sigue el formato correcto
            if not str(thumbnail_path).startswith('/thumbnails/'):
                print(f"ENDPOINT: ADVERTENCIA - La ruta no tiene el formato correcto: {thumbnail_path}")
                # Normalizar la ruta en caso de error
                thumb_name = Path(str(thumbnail_path)).name
                thumbnail_path = f"/thumbnails/{thumb_name}"
                print(f"ENDPOINT: CORRECCIÓN - Ruta normalizada: {thumbnail_path}")
            
            # Guardar la ruta web en la base de datos
            print(f"ENDPOINT: Ruta final a guardar en BD: {thumbnail_path}")
            db_media.thumbnail_path = thumbnail_path
        
        # Extraer metadatos
        metadata = media_processor.extract_metadata(str(file_path), file.content_type)
        for key, value in metadata.items():
            setattr(db_media, key, value)
        
        # Predecir evento
        if file.content_type.startswith('image/'):
            event_type, confidence = media_processor.predict_event(str(file_path))
            db_media.event_type = event_type
            db_media.event_confidence = confidence
        
        db.commit()
        db.refresh(db_media)
        
    except Exception as e:
        print(f"Error processing file: {e}")
    
    return db_media

@router.get("/", response_model=List[Media])
def list_media(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return media_crud.get_all_media(db, skip=skip, limit=limit)

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
    db_media = media_crud.update_media(db, media_id, media_update)
    if db_media is None:
        raise HTTPException(status_code=404, detail="Media not found")
    return db_media

@router.delete("/{media_id}")
def delete_media(
    media_id: int,
    db: Session = Depends(get_db)
):
    success = media_crud.delete_media(db, media_id)
    if not success:
        raise HTTPException(status_code=404, detail="Media not found")
    return {"message": "Media deleted successfully"}
