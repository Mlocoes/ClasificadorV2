#!/bin/bash

echo "=== Corrección Final - MediaProcessor ==="

# Corregir directamente el método create_thumbnail
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
            
            print(f'MEDIA_PROCESSOR: Generando miniatura para {file_path}')
            print(f'MEDIA_PROCESSOR: Ruta de miniatura: {thumbnail_path}')
            
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
                    print(f'MEDIA_PROCESSOR: Miniatura creada con éxito en {thumbnail_path}')
                    # IMPORTANTE: Devolver siempre la ruta en formato /thumbnails/
                    return f'/thumbnails/{thumbnail_name}'
                else:
                    print(f'MEDIA_PROCESSOR: No se pudo crear la miniatura en {thumbnail_path}')
                    return None
            except Exception as e:
                print(f'MEDIA_PROCESSOR: Error creando miniatura: {e}')
                return None
        except Exception as e:
            print(f'MEDIA_PROCESSOR: Error general: {e}')
            return None
    
    # Resto de los métodos se mantienen igual...
    def extract_metadata(self, file_path: str, mime_type: str) -> dict:
        metadata = {}
        
        if mime_type.startswith('image/'):
            img_metadata = self._extract_image_metadata(file_path)
            metadata.update(img_metadata)
        elif mime_type.startswith('video/'):
            video_metadata = self._extract_video_metadata(file_path)
            metadata.update(video_metadata)
        
        return metadata
    
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
"

# Reiniciar el backend
docker restart clasificadorv2-backend-1

# Esperar a que el contenedor esté listo
echo "Esperando a que el contenedor esté listo..."
sleep 5

# Probar subiendo un archivo
echo "=== Probando la carga de archivos ==="
cd /home/mloco/Escritorio/ClasificadorV2
curl -s -X POST http://localhost:8000/api/v1/media/upload/ -F "file=@test_real.jpg" | grep thumbnail_path

# Verificar los archivos
echo
echo "=== Archivos en /app/storage/thumbnails ==="
docker exec clasificadorv2-backend-1 ls -la /app/storage/thumbnails/

echo
echo "=== Script Completado ==="
