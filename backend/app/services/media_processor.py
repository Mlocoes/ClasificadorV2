import os
from pathlib import Path
from typing import Optional, Tuple, Any, cast
from PIL import Image
import cv2
import exifread
from datetime import datetime
import torch
from app.core.config import settings

# Importación condicional de pyheif
HEIC_SUPPORT = False
pyheif: Any = None  # Usar Any para evitar advertencias

try:
    import pyheif as pyheif_module
    pyheif = pyheif_module
    if hasattr(pyheif, 'read'):
        HEIC_SUPPORT = True
        print("pyheif está instalado y funcionando. El soporte para archivos HEIC/HEIF está disponible.")
except ImportError as e:
    print(f"pyheif no está disponible: {str(e)}. El soporte para archivos HEIC/HEIF no estará disponible.")

class MediaProcessor:
    def __init__(self):
        self.clip_model = None
        self.clip_processor = None

    def create_thumbnail(self, file_path: str, mime_type: str) -> Optional[str]:
        try:
            # Crear la miniatura según el tipo de archivo
            if mime_type.startswith('image/'):
                thumbnail_path = self._create_image_thumbnail(file_path)
            elif mime_type.startswith('video/'):
                thumbnail_path = self._create_video_thumbnail(file_path)
            else:
                return None
            return thumbnail_path
        except Exception as e:
            print(f"Error en create_thumbnail: {e}")
            return None

    def _create_image_thumbnail(self, file_path: str) -> Optional[str]:
        try:
            # Obtener la ruta de la miniatura según la estrategia configurada
            thumbnail_absolute_path, thumbnail_web_path = self._get_thumbnail_path(file_path)
            
            # Si la miniatura ya existe, devolverla
            if thumbnail_absolute_path.exists():
                print(f"La miniatura ya existe en: {thumbnail_absolute_path}")
                return thumbnail_web_path
            
            # Procesar la imagen según su formato
            if file_path.lower().endswith(('.heic', '.heif')):
                if not HEIC_SUPPORT:
                    print(f"No se puede procesar archivo HEIC/HEIF {file_path}: pyheif no está instalado")
                    return None
                
                try:
                    print(f"Procesando archivo HEIC/HEIF: {file_path}")
                    heif_file = pyheif.read(file_path)
                    img = Image.frombytes(
                        heif_file.mode, 
                        heif_file.size, 
                        heif_file.data,
                        "raw", 
                        heif_file.mode, 
                        heif_file.stride,
                    )
                except Exception as e:
                    print(f"Error al procesar archivo HEIC/HEIF {file_path}: {e}")
                    return None
            else:
                # Para otros formatos de imagen
                img = Image.open(file_path)
            
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
            print(f"Guardando miniatura en: {thumbnail_absolute_path}")
            img.save(str(thumbnail_absolute_path), 'JPEG', quality=85)
            
            # Verificar si el archivo se creó correctamente
            if os.path.exists(str(thumbnail_absolute_path)):
                os.chmod(str(thumbnail_absolute_path), 0o777)
                print(f"Miniatura creada correctamente en {thumbnail_absolute_path}")
                return thumbnail_web_path
            else:
                print(f"ERROR: No se pudo crear la miniatura en {thumbnail_absolute_path}")
                return None
            
        except Exception as e:
            print(f"Error creating image thumbnail: {e}")
            return None

    def _create_video_thumbnail(self, file_path: str) -> Optional[str]:
        try:
            # Obtener la ruta de la miniatura según la estrategia configurada
            thumbnail_absolute_path, thumbnail_web_path = self._get_thumbnail_path(file_path)
            
            # Si la miniatura ya existe, devolverla
            if thumbnail_absolute_path.exists():
                print(f"La miniatura de video ya existe en: {thumbnail_absolute_path}")
                return thumbnail_web_path
            
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
                print(f"Guardando miniatura de video en: {thumbnail_absolute_path}")
                img.save(str(thumbnail_absolute_path), 'JPEG', quality=85)
                
                # Verificar si el archivo se creó correctamente
                if os.path.exists(str(thumbnail_absolute_path)):
                    os.chmod(str(thumbnail_absolute_path), 0o777)
                    print(f"Miniatura de video creada correctamente en {thumbnail_absolute_path}")
                    return thumbnail_web_path
                else:
                    print(f"ERROR: No se pudo crear la miniatura de video en {thumbnail_absolute_path}")
                    return None
            return None
        except Exception as e:
            print(f"Error creating video thumbnail: {e}")
            return None

    def _get_thumbnail_path(self, original_file_path: str) -> Tuple[Path, str]:
        """
        Genera la ruta de la miniatura en el directorio dedicado.
        
        Args:
            original_file_path: Ruta al archivo original
            
        Returns:
            Tuple[Path, str]: La ruta absoluta del sistema (Path) y la ruta web relativa
        """
        original_path = Path(original_file_path)
        file_stem = original_path.stem
        thumbnail_name = f"thumb_{file_stem}.jpg"
        
        # Asegurar que el directorio dedicado existe
        settings.THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
        os.chmod(str(settings.THUMBNAILS_DIR), 0o777)
        
        # Ruta absoluta del archivo
        absolute_path = settings.THUMBNAILS_DIR / thumbnail_name
        
        # Ruta web relativa (debe coincidir con tu estructura de directorios)
        web_path = f"/thumbnails/{thumbnail_name}"
        
        return absolute_path, web_path

    def _load_clip_model(self):
        if self.clip_model is None:
            from transformers import CLIPProcessor, CLIPModel
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    
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
        """Convierte valores EXIF GPS a grados decimales"""
        d = float(values[0].num) / float(values[0].den)
        m = float(values[1].num) / float(values[1].den)
        s = float(values[2].num) / float(values[2].den)
        return d + (m / 60.0) + (s / 3600.0)

    def predict_event(self, file_path: str) -> Tuple[str, float]:
        """
        Predice el tipo de evento en una imagen usando CLIP.
        """
        try:
            self._load_clip_model()
            
            # Cargar y preprocesar la imagen
            image = Image.open(file_path)
            inputs = self.clip_processor(images=image, return_tensors="pt", padding=True)
            
            # Lista de eventos para clasificar
            event_texts = [
                "a sports event or game",
                "a conference or meeting",
                "a party or celebration",
                "a concert or musical performance",
                "a wedding ceremony",
                "a graduation ceremony",
                "a protest or demonstration",
                "a religious ceremony",
                "a parade or festival",
                "an exhibition or art show",
                "a family gathering",
                "a food event or dining",
                "an outdoor activity or adventure",
                "a business event",
                "an educational event"
            ]
            
            # Preprocesar textos
            text_inputs = self.clip_processor(
                text=event_texts,
                return_tensors="pt",
                padding=True
            )
            
            # Obtener embeddings de imagen y texto
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
                text_features = self.clip_model.get_text_features(**text_inputs)
            
            # Normalizar features
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            # Calcular similaridad
            similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
            
            # Obtener el evento más probable y su confianza
            values, indices = similarity[0].topk(1)
            event_type = event_texts[indices[0]].replace("a ", "").replace("an ", "")
            confidence = float(values[0])
            
            return event_type, confidence
            
        except Exception as e:
            print(f"Error predicting event: {e}")
            return "unknown", 0.0
