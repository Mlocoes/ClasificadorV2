import os
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image
import exifread
from datetime import datetime
from transformers import CLIPProcessor, CLIPModel
import torch
from app.core.config import settings

class MediaProcessor:
    def __init__(self):
        self.clip_model = None
        self.clip_processor = None
        
    def _load_clip_model(self):
        if self.clip_model is None:
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    
    def create_thumbnail(self, file_path: str, mime_type: str) -> Optional[str]:
        if mime_type.startswith('image/'):
            return self._create_image_thumbnail(file_path)
        elif mime_type.startswith('video/'):
            return self._create_video_thumbnail(file_path)
        return None
    
    def _create_image_thumbnail(self, file_path: str) -> Optional[str]:
        try:
            with Image.open(file_path) as img:
                img.thumbnail(settings.THUMBNAIL_SIZE)
                thumbnail_path = str(Path(file_path).with_suffix('.thumb.jpg'))
                img.save(thumbnail_path, 'JPEG')
                return thumbnail_path
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return None
    
    def _create_video_thumbnail(self, file_path: str) -> Optional[str]:
        try:
            import cv2
            cap = cv2.VideoCapture(file_path)
            ret, frame = cap.read()
            if ret:
                thumbnail_path = str(Path(file_path).with_suffix('.thumb.jpg'))
                cv2.imwrite(thumbnail_path, frame)
                return thumbnail_path
            return None
        except Exception as e:
            print(f"Error creating video thumbnail: {e}")
            return None
    
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
            print(f"Error extracting image metadata: {e}")
        
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
