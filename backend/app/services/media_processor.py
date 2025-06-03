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
        
    def _get_thumbnail_path(self, original_file_path: str) -> Tuple[Path, str]:
        """
        Genera la ruta de la miniatura en el directorio dedicado /thumbnails.
        
        Args:
            original_file_path: Ruta al archivo original
            
        Returns:
            Tuple[Path, str]: La ruta absoluta del sistema (Path) y el nombre del archivo de miniatura
        """
        original_path = Path(original_file_path)
        file_stem = original_path.stem
        thumbnail_name = f"thumb_{file_stem}.jpg"
        
        # Asegurar que el directorio dedicado existe
        settings.THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
        os.chmod(str(settings.THUMBNAILS_DIR), 0o777)
        print(f"Usando directorio dedicado para miniaturas: {settings.THUMBNAILS_DIR}")
        
        # Siempre usar el directorio dedicado para miniaturas
        return settings.THUMBNAILS_DIR / thumbnail_name, thumbnail_name
    
    def create_thumbnail(self, file_path: str, mime_type: str) -> Optional[str]:
        try:
            # Crear la miniatura según el tipo de archivo
            if mime_type.startswith('image/'):
                thumbnail_path = self._create_image_thumbnail(file_path)
            elif mime_type.startswith('video/'):
                thumbnail_path = self._create_video_thumbnail(file_path)
            else:
                return None
            
            # Los métodos _create_*_thumbnail ya devuelven la ruta web estandarizada
            # con el formato "/thumbnails/thumb_nombre.jpg"
            if thumbnail_path:
                print(f"DEBUG - Miniatura creada correctamente, ruta web: {thumbnail_path}")
                
                # Establecer permisos correctos
                try:
                    # Asegurar que el directorio de miniaturas tiene permisos adecuados
                    os.chmod(str(settings.THUMBNAILS_DIR), 0o777)
                    
                    # Convertir la ruta web a una ruta física para chmod
                    if thumbnail_path.startswith('/thumbnails/'):
                        thumb_name = Path(thumbnail_path).name
                        abs_path = settings.THUMBNAILS_DIR / thumb_name
                        
                        if abs_path.exists():
                            os.chmod(str(abs_path), 0o777)
                            print(f"Permisos establecidos correctamente para: {abs_path}")
                except Exception as e:
                    print(f"Warning: Error setting permissions: {e}")
                
            return thumbnail_path
        except Exception as e:
            print(f"Error en create_thumbnail: {e}")
            return None
    
    def _create_image_thumbnail(self, file_path: str) -> Optional[str]:
        try:
            # Obtener la ruta de la miniatura según la estrategia configurada
            thumbnail_path, thumbnail_name = self._get_thumbnail_path(file_path)
            print(f"Ruta ABSOLUTA de miniatura a crear: {thumbnail_path}")
            
            # Si la miniatura ya existe, devolverla
            if thumbnail_path.exists():
                print(f"La miniatura ya existe en: {thumbnail_path}")
                # Devolver la ruta web para uso en la aplicación
                return f"/thumbnails/{thumbnail_name}"
            
            with Image.open(file_path) as img:
                # Manejar orientación EXIF
                try:
                    if hasattr(img, '_getexif') and img._getexif() is not None:
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
                    print(f"Warning: Error handling EXIF orientation: {e}")
                
                # Convertir a RGB si es necesario
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Crear miniatura
                img.thumbnail(settings.THUMBNAIL_SIZE)
                print(f"Guardando miniatura en: {thumbnail_path}")
                img.save(str(thumbnail_path), 'JPEG', quality=85)
                # Verificar si el archivo se creó correctamente
                if os.path.exists(str(thumbnail_path)):
                    os.chmod(str(thumbnail_path), 0o777)
                    print(f"Miniatura creada correctamente en {thumbnail_path}")
                else:
                    print(f"ERROR: No se pudo crear la miniatura en {thumbnail_path}")
            
            # Devolver la ruta web para uso en la aplicación
            return f"/thumbnails/{thumbnail_name}"
            
        except Exception as e:
            print(f"Error creating image thumbnail: {e}")
            return None
    
    def _create_video_thumbnail(self, file_path: str) -> Optional[str]:
        try:
            # Obtener la ruta de la miniatura según la estrategia configurada
            thumbnail_path, thumbnail_name = self._get_thumbnail_path(file_path)
            print(f"Ruta ABSOLUTA de miniatura de video a crear: {thumbnail_path}")
            
            # Si la miniatura ya existe, devolverla
            if thumbnail_path.exists():
                print(f"La miniatura de video ya existe en: {thumbnail_path}")
                # Devolver la ruta web para uso en la aplicación
                return f"/thumbnails/{thumbnail_name}"
            
            cap = cv2.VideoCapture(str(file_path))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames > 0:
                # Tomar frame al 25% del video
                target_frame = min(int(total_frames * 0.25), total_frames - 1)
                cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Redimensionar manteniendo proporción
                height, width = frame.shape[:2]
                max_size = max(settings.THUMBNAIL_SIZE)
                
                if width > height:
                    new_width = max_size
                    new_height = int(height * (max_size / width))
                else:
                    new_height = max_size
                    new_width = int(width * (max_size / height))
                
                frame = cv2.resize(frame, (new_width, new_height))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                img = Image.fromarray(frame)
                print(f"Guardando miniatura de video en: {thumbnail_path}")
                img.save(str(thumbnail_path), 'JPEG', quality=85)
                # Verificar si el archivo se creó correctamente
                if os.path.exists(str(thumbnail_path)):
                    os.chmod(str(thumbnail_path), 0o777)
                    print(f"Miniatura de video creada correctamente en {thumbnail_path}")
                else:
                    print(f"ERROR: No se pudo crear la miniatura de video en {thumbnail_path}")
                
                # Devolver la ruta web para uso en la aplicación
                return f"/thumbnails/{thumbnail_name}"
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
