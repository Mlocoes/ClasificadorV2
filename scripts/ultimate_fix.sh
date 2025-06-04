#!/bin/bash

echo "=== Corrección Final y Definitiva ==="

# Acceder al contenedor y modificar el archivo directamente
docker exec clasificadorv2-backend-1 bash -c 'cat > /app/app/services/media_processor.py << "EOF"
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
        """
        Crea una miniatura para un archivo de imagen o video.
        Devuelve la ruta web (/thumbnails/thumb_name.jpg) a la miniatura creada.
        """
        print(f"DIAGNOST: Creando miniatura para {file_path}")
        
        try:
            # Forzar que exista el directorio
            thumbnails_dir = Path("/app/storage/thumbnails")
            os.makedirs(str(thumbnails_dir), exist_ok=True)
            os.chmod(str(thumbnails_dir), 0o777)
            
            # Crear nombre para la miniatura
            file_stem = Path(file_path).stem
            thumbnail_name = f"thumb_{file_stem}.jpg"
            thumbnail_path = thumbnails_dir / thumbnail_name
            
            print(f"DIAGNOST: Utilizando ruta: {thumbnail_path}")
            
            # Crear la miniatura según el tipo de archivo
            if mime_type.startswith("image/"):
                thumbnail_created = self._create_image_thumbnail_direct(file_path, thumbnail_path)
            elif mime_type.startswith("video/"):
                thumbnail_created = self._create_video_thumbnail_direct(file_path, thumbnail_path)
            else:
                print(f"DIAGNOST: Tipo MIME no soportado: {mime_type}")
                return None
            
            # Verificar si la miniatura se creó
            if thumbnail_created and os.path.exists(str(thumbnail_path)):
                print(f"DIAGNOST: Miniatura creada correctamente en: {thumbnail_path}")
                return f"/thumbnails/{thumbnail_name}"
            else:
                print(f"DIAGNOST: No se pudo crear la miniatura en: {thumbnail_path}")
                return None
        except Exception as e:
            print(f"DIAGNOST ERROR: {str(e)}")
            return None
    
    def _create_image_thumbnail_direct(self, source_path: str, target_path: Path) -> bool:
        """Crea una miniatura de imagen directamente en la ruta especificada"""
        try:
            print(f"DIAGNOST: Creando miniatura de imagen: {source_path} -> {target_path}")
            with Image.open(source_path) as img:
                # Gestionar orientación EXIF
                try:
                    if hasattr(img, "_getexif") and img._getexif() is not None:
                        exif = dict(img._getexif().items())
                        if orientation := exif.get(0x0112):  # Orientation tag
                            if orientation == 2:
                                img = img.transpose(Image.FLIP_LEFT_RIGHT)
                            elif orientation == 3:
                                img = img.transpose(Image.ROTATE_180)
                            elif orientation == 4:
                                img = img.transpose(Image.FLIP_TOP_BOTTOM)
                            elif orientation == 5:
                                img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)
                            elif orientation == 6:
                                img = img.transpose(Image.ROTATE_270)
                            elif orientation == 7:
                                img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
                            elif orientation == 8:
                                img = img.transpose(Image.ROTATE_90)
                except Exception as e:
                    print(f"DIAGNOST: Error procesando EXIF: {str(e)}")
                
                # Convertir a RGB si es necesario
                if img.mode in ("RGBA", "LA"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != "RGB":
                    img = img.convert("RGB")
                
                # Crear miniatura
                img.thumbnail((200, 200))  # Usar tamaño fijo para asegurar compatibilidad
                img.save(str(target_path), "JPEG", quality=85)
                
                # Establecer permisos
                if os.path.exists(str(target_path)):
                    os.chmod(str(target_path), 0o777)
                    return True
                return False
        except Exception as e:
            print(f"DIAGNOST ERROR: Error creando miniatura de imagen: {str(e)}")
            return False
    
    def _create_video_thumbnail_direct(self, source_path: str, target_path: Path) -> bool:
        """Crea una miniatura de video directamente en la ruta especificada"""
        try:
            print(f"DIAGNOST: Creando miniatura de video: {source_path} -> {target_path}")
            cap = cv2.VideoCapture(source_path)
            if not cap.isOpened():
                print(f"DIAGNOST: No se pudo abrir el video: {source_path}")
                return False
            
            # Tomar frame al 25% del video o el primer frame si es muy corto
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames > 0:
                target_frame = min(int(total_frames * 0.25), total_frames - 1)
                cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                print(f"DIAGNOST: No se pudo leer frame del video: {source_path}")
                return False
            
            # Redimensionar manteniendo proporción
            height, width = frame.shape[:2]
            max_size = 200  # Tamaño fijo para asegurar compatibilidad
            
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            
            frame = cv2.resize(frame, (new_width, new_height))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            img = Image.fromarray(frame)
            img.save(str(target_path), "JPEG", quality=85)
            
            # Establecer permisos
            if os.path.exists(str(target_path)):
                os.chmod(str(target_path), 0o777)
                return True
            return False
        except Exception as e:
            print(f"DIAGNOST ERROR: Error creando miniatura de video: {str(e)}")
            return False
    
    def extract_metadata(self, file_path: str, mime_type: str) -> dict:
        metadata = {}
        
        if mime_type.startswith("image/"):
            img_metadata = self._extract_image_metadata(file_path)
            metadata.update(img_metadata)
        elif mime_type.startswith("video/"):
            video_metadata = self._extract_video_metadata(file_path)
            metadata.update(video_metadata)
        
        return metadata
    
    def _extract_image_metadata(self, file_path: str) -> dict:
        metadata = {}
        try:
            with open(file_path, "rb") as f:
                tags = exifread.process_file(f)
                
            # Dimensiones
            with Image.open(file_path) as img:
                metadata["width"], metadata["height"] = img.size
            
            # GPS
            if "GPS GPSLatitude" in tags and "GPS GPSLongitude" in tags:
                lat = self._convert_to_degrees(tags["GPS GPSLatitude"].values)
                lon = self._convert_to_degrees(tags["GPS GPSLongitude"].values)
                if "GPS GPSLatitudeRef" in tags and tags["GPS GPSLatitudeRef"].values[0] == "S":
                    lat = -lat
                if "GPS GPSLongitudeRef" in tags and tags["GPS GPSLongitudeRef"].values[0] == "W":
                    lon = -lon
                metadata["latitude"] = lat
                metadata["longitude"] = lon
            
            # Fecha de creación
            if "EXIF DateTimeOriginal" in tags:
                date_str = str(tags["EXIF DateTimeOriginal"])
                try:
                    metadata["creation_date"] = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                except:
                    pass
                    
        except Exception as e:
            print(f"Error extracting image metadata: {e}")
        
        return metadata
    
    def _extract_video_metadata(self, file_path: str) -> dict:
        metadata = {}
        try:
            import cv2
            cap = cv2.VideoCapture(file_path)
            
            # Dimensiones
            metadata["width"] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            metadata["height"] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Duración
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            metadata["duration"] = frame_count / fps if fps > 0 else None
            
            cap.release()
        except Exception as e:
            print(f"Error extracting video metadata: {e}")
        
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
                "beach day", "hiking trip", "birthday party", "wedding ceremony",
                "graduation ceremony", "concert", "sports event", "family gathering",
                "vacation", "holiday celebration", "business meeting", "conference",
                "outdoor adventure", "camping trip", "city tour"
            ]
            
            # Cargar y preprocesar la imagen
            image = Image.open(file_path)
            inputs = self.clip_processor(
                images=image,
                text=events,
                return_tensors="pt",
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
            print(f"Error predicting event: {e}")
            return "unknown", 0.0
            
    def _load_clip_model(self):
        # Solo cargar el modelo si no está ya cargado
        if self.clip_model is None:
            try:
                from transformers import CLIPProcessor, CLIPModel
                
                # Cargar modelo CLIP
                model_name = "openai/clip-vit-base-patch32"
                self.clip_model = CLIPModel.from_pretrained(model_name)
                self.clip_processor = CLIPProcessor.from_pretrained(model_name)
                
                print("Modelo CLIP cargado correctamente")
            except Exception as e:
                print(f"Error al cargar el modelo CLIP: {e}")
EOF'

# Reiniciar el contenedor para aplicar los cambios
echo "Reiniciando el contenedor para aplicar los cambios..."
docker restart clasificadorv2-backend-1

# Esperar a que el contenedor esté listo
echo "Esperando a que el contenedor esté listo..."
sleep 10

# Limpiar archivos existentes para una prueba limpia
echo "Limpiando archivos de prueba anteriores..."
docker exec clasificadorv2-backend-1 bash -c "
  rm -f /app/storage/uploads/test_real.thumb.jpg
  rm -f /app/storage/thumbnails/thumb_test_real.jpg
"

# Probar subir un archivo
echo "Probando la carga de archivos..."
cd /home/mloco/Escritorio/ClasificadorV2
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/media/upload/ -F "file=@test_real.jpg")

# Mostrar la respuesta completa
echo "Respuesta de la API:"
echo $RESPONSE | python -m json.tool

# Verificar archivos en el sistema
echo -e "\nVerificando archivos en el sistema:"
docker exec clasificadorv2-backend-1 bash -c "
  echo 'Archivos en directorio de uploads:'
  ls -la /app/storage/uploads/ | grep test_real
  
  echo -e '\nArchivos en directorio de thumbnails:'
  ls -la /app/storage/thumbnails/ | grep test_real
"

echo -e "\n=== Corrección Completada ==="
