#!/bin/bash

echo "=== Script de Depuración Avanzada ==="

# Verificar el problema directamente en el sistema de archivos
docker exec clasificadorv2-backend-1 bash -c "
echo '===== CONTENIDO DE DIRECTORIOS ====='
echo 'Directorio de uploads:'
ls -la /app/storage/uploads/
echo
echo 'Directorio de miniaturas:'
ls -la /app/storage/thumbnails/
echo

# Verificar permisos
echo '===== PERMISOS DE DIRECTORIOS ====='
echo 'Permisos de /app/storage:'
ls -ld /app/storage
echo 'Permisos de /app/storage/uploads:'
ls -ld /app/storage/uploads
echo 'Permisos de /app/storage/thumbnails:'
ls -ld /app/storage/thumbnails
"

echo
echo "=== Actualizando código para una corrección más directa ==="

# Este comando va a modificar el archivo de media_processor.py en el contenedor
docker exec clasificadorv2-backend-1 bash -c "
cat > /app/app/services/media_processor.py << 'EOL'
import os
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import cv2
import exifread
from datetime import datetime
import torch
from app.core.config import settings

class MediaProcessor:
    def __init__(self):
        self.clip_model = None
        self.clip_processor = None
    
    def create_thumbnail(self, file_path: str, mime_type: str) -> Optional[str]:
        try:
            # Forzar que los directorios existan
            os.makedirs('/app/storage/thumbnails', exist_ok=True)
            os.chmod('/app/storage/thumbnails', 0o777)
            
            # Crear nombre de archivo para la miniatura
            file_stem = Path(file_path).stem
            thumbnail_name = f'thumb_{file_stem}.jpg'
            thumbnail_path = Path('/app/storage/thumbnails') / thumbnail_name
            
            print(f'DEBUG: Generando miniatura para {file_path}')
            print(f'DEBUG: Ruta de miniatura: {thumbnail_path}')
            
            try:
                # Intentar crear la miniatura
                if mime_type.startswith('image/'):
                    with Image.open(file_path) as img:
                        img.thumbnail((200, 200))
                        img.save(str(thumbnail_path), 'JPEG', quality=85)
                elif mime_type.startswith('video/'):
                    cap = cv2.VideoCapture(file_path)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret:
                            frame = cv2.resize(frame, (200, 200))
                            cv2.imwrite(str(thumbnail_path), frame)
                        cap.release()
                
                # Verificar que se creó correctamente
                if os.path.exists(str(thumbnail_path)):
                    os.chmod(str(thumbnail_path), 0o777)
                    print(f'DEBUG: Miniatura creada con éxito en {thumbnail_path}')
                    return '/thumbnails/' + thumbnail_name
                else:
                    print(f'DEBUG: No se pudo crear la miniatura en {thumbnail_path}')
                    return None
            except Exception as e:
                print(f'DEBUG: Error creando miniatura: {e}')
                return None
        except Exception as e:
            print(f'DEBUG: Error general: {e}')
            return None
    
    # Resto de los métodos se mantienen igual...
    def _extract_image_metadata(self, file_path: str) -> dict:
        metadata = {}
        try:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f)
                
            # Dimensiones
            with Image.open(file_path) as img:
                metadata['width'], metadata['height'] = img.size
            
            # GPS
            if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                lat = self._convert_to_degrees(tags['GPS GPSLatitude'].values)
                lon = self._convert_to_degrees(tags['GPS GPSLongitude'].values)
                if 'GPS GPSLatitudeRef' in tags and tags['GPS GPSLatitudeRef'].values[0] == 'S':
                    lat = -lat
                if 'GPS GPSLongitudeRef' in tags and tags['GPS GPSLongitudeRef'].values[0] == 'W':
                    lon = -lon
                metadata['latitude'] = lat
                metadata['longitude'] = lon
            
            # Fecha de creación
            if 'EXIF DateTimeOriginal' in tags:
                date_str = str(tags['EXIF DateTimeOriginal'])
                try:
                    metadata['creation_date'] = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                except:
                    pass
                    
        except Exception as e:
            print(f'Error extracting image metadata: {e}')
        
        return metadata
    
    def _extract_video_metadata(self, file_path: str) -> dict:
        metadata = {}
        try:
            import cv2
            cap = cv2.VideoCapture(file_path)
            
            # Dimensiones
            metadata['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            metadata['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Duración
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            metadata['duration'] = frame_count / fps if fps > 0 else None
            
            cap.release()
        except Exception as e:
            print(f'Error extracting video metadata: {e}')
        
        return metadata
    
    def extract_metadata(self, file_path: str, mime_type: str) -> dict:
        metadata = {}
        
        if mime_type.startswith('image/'):
            img_metadata = self._extract_image_metadata(file_path)
            metadata.update(img_metadata)
        elif mime_type.startswith('video/'):
            video_metadata = self._extract_video_metadata(file_path)
            metadata.update(video_metadata)
        
        return metadata
        
    def _convert_to_degrees(self, values) -> float:
        d, m, s = values
        degrees = float(d.num) / float(d.den)
        minutes = float(m.num) / float(m.den)
        seconds = float(s.num) / float(s.den)
        return degrees + (minutes / 60.0) + (seconds / 3600.0)
    
    def predict_event(self, file_path: str) -> Tuple[str, float]:
        try:
            self._load_clip_model()
            
            # Lista de eventos posibles
            events = [
                'beach day', 'hiking trip', 'birthday party', 'wedding ceremony',
                'graduation ceremony', 'concert', 'sports event', 'family gathering',
                'vacation', 'holiday celebration', 'business meeting', 'conference',
                'outdoor adventure', 'camping trip', 'city tour'
            ]
            
            # Cargar y preprocesar la imagen
            image = Image.open(file_path)
            inputs = self.clip_processor(
                images=image,
                text=events,
                return_tensors='pt',
                padding=True
            )
            
            # Obtener predicciones
            outputs = self.clip_model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = torch.softmax(logits_per_image, dim=1)[0]
            
            # Obtener el evento más probable
            max_prob, max_idx = torch.max(probs, dim=0)
            predicted_event = events[max_idx]
            confidence = float(max_prob)
            
            return predicted_event, confidence
            
        except Exception as e:
            print(f'Error predicting event: {e}')
            return 'unknown', 0.0
            
    def _load_clip_model(self):
        # Solo cargar el modelo si no está ya cargado
        if self.clip_model is None:
            try:
                from transformers import CLIPProcessor, CLIPModel
                
                # Cargar modelo CLIP
                model_name = 'openai/clip-vit-base-patch32'
                self.clip_model = CLIPModel.from_pretrained(model_name)
                self.clip_processor = CLIPProcessor.from_pretrained(model_name)
                
                print('Modelo CLIP cargado correctamente')
            except Exception as e:
                print(f'Error al cargar el modelo CLIP: {e}')
EOL

# También modificar el archivo media.py para asegurar que las rutas se manejen correctamente
cat > /app/app/api/v1/media.py << 'EOL'
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
    return f'{name}{ext.lower()}'

@router.post('/upload/', response_model=Media)
async def upload_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validar tipo de archivo
    if not (file.content_type.startswith('image/') or file.content_type.startswith('video/')):
        raise HTTPException(status_code=400, detail='Tipo de archivo no soportado')
    
    # Sanitizar nombre de archivo
    safe_filename = sanitize_filename(file.filename)
    
    # Crear directorio de uploads si no existe
    uploads_dir = settings.UPLOADS_DIR
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Guardar archivo
    file_path = uploads_dir / safe_filename
    try:
        with file_path.open('wb') as buffer:
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
    file_relative_path = f'/uploads/{safe_filename}'
    db_media = media_crud.create_media(db, media_create, file_relative_path)
    
    # Procesar archivo
    try:
        # Crear miniatura
        print(f'Procesando archivo: {file_path}')
        thumbnail_path = media_processor.create_thumbnail(str(file_path), file.content_type)
        if thumbnail_path:
            print(f'Miniatura creada: {thumbnail_path}')
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
        print(f'Error processing file: {e}')
    
    return db_media

@router.get('/', response_model=List[Media])
def list_media(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return media_crud.get_all_media(db, skip=skip, limit=limit)

@router.get('/{media_id}', response_model=Media)
def get_media(
    media_id: int,
    db: Session = Depends(get_db)
):
    db_media = media_crud.get_media(db, media_id)
    if db_media is None:
        raise HTTPException(status_code=404, detail='Media not found')
    return db_media

@router.patch('/{media_id}', response_model=Media)
def update_media(
    media_id: int,
    media_update: MediaUpdate,
    db: Session = Depends(get_db)
):
    db_media = media_crud.update_media(db, media_id, media_update)
    if db_media is None:
        raise HTTPException(status_code=404, detail='Media not found')
    return db_media

@router.delete('/{media_id}')
def delete_media(
    media_id: int,
    db: Session = Depends(get_db)
):
    success = media_crud.delete_media(db, media_id)
    if not success:
        raise HTTPException(status_code=404, detail='Media not found')
    return {'message': 'Media deleted successfully'}
EOL
"

# Reiniciar el contenedor para aplicar los cambios
echo "=== Reiniciando contenedor para aplicar los cambios ==="
docker restart clasificadorv2-backend-1

# Esperar a que el contenedor esté listo
echo "Esperando a que el contenedor esté listo..."
sleep 5

echo "=== Verificando si el problema se ha resuelto ==="
# Subir un archivo de prueba y verificar la respuesta
curl -s -X POST http://localhost:8000/api/v1/media/upload/ -F "file=@test_real.jpg" | grep -o '"thumbnail_path":"[^"]*"'

echo
echo "=== Verificando los archivos en el sistema ==="
docker exec clasificadorv2-backend-1 bash -c "ls -la /app/storage/thumbnails/"

echo
echo "=== Script de Depuración Avanzada Completado ==="
