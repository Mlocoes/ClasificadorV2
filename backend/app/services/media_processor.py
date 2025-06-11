import os
from pathlib import Path
from typing import Optional, Tuple, Any, cast
from PIL import Image
import cv2
import exifread
from datetime import datetime
import torch
import shutil
import numpy as np
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
        self.opencv_dnn_model = None
        self.opencv_classes = None

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
    
    def _load_opencv_dnn_model(self):
        if self.opencv_dnn_model is None:
            try:
                # Rutas para el modelo YOLO
                model_dir = settings.STORAGE_DIR / "models" / "opencv_dnn"
                model_dir.mkdir(parents=True, exist_ok=True)
                
                # Rutas de los archivos del modelo YOLO
                config_path = model_dir / "yolov4.cfg"
                weights_path = model_dir / "yolov4.weights"
                classes_path = model_dir / "coco.names"
                
                # Si los archivos no existen, los descargamos
                if not config_path.exists() or not weights_path.exists() or not classes_path.exists():
                    print("Descargando modelo YOLO para OpenCV DNN...")
                    self._download_opencv_dnn_model(config_path, weights_path, classes_path)
                
                # Cargar el modelo YOLO
                print(f"Cargando modelo YOLO desde {weights_path}...")
                self.opencv_dnn_model = cv2.dnn.readNetFromDarknet(str(config_path), str(weights_path))
                
                # Seleccionar backend preferido para mejor rendimiento
                self.opencv_dnn_model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                self.opencv_dnn_model.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
                
                # Verificar si el modelo se cargó correctamente
                if self.opencv_dnn_model.empty():
                    raise ValueError("No se pudo cargar el modelo YOLO")
                    
                print("Modelo YOLO cargado exitosamente")
                
                # Cargar las clases de COCO
                print(f"Cargando clases desde {classes_path}...")
                with open(classes_path, 'r') as f:
                    self.opencv_classes = [line.strip() for line in f.readlines()]
                print(f"Cargadas {len(self.opencv_classes)} clases")
                
                # Agregar la configuración para las capas de salida de YOLO
                self.yolo_output_layers = self.opencv_dnn_model.getUnconnectedOutLayersNames()
                
            except Exception as e:
                print(f"Error al cargar el modelo OpenCV DNN: {e}")
                # Inicializar con valores vacíos en caso de error
                self.opencv_dnn_model = None
                self.opencv_classes = []
                self.yolo_output_layers = []
                raise
    
    def _download_opencv_dnn_model(self, config_path, weights_path, classes_path):
        """Descarga los archivos necesarios para el modelo YOLO"""
        import requests
        import os
        
        # URLs de los archivos del modelo YOLO
        config_url = "https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg"
        weights_url = "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights"
        classes_url = "https://raw.githubusercontent.com/AlexeyAB/darknet/master/data/coco.names"
        
        print(f"Descargando archivo de configuración desde {config_url}")
        try:
            # Descargar el archivo de configuración
            with open(config_path, 'wb') as f:
                response = requests.get(config_url, timeout=30)
                response.raise_for_status()
                f.write(response.content)
            print(f"Archivo de configuración guardado en {config_path}")
            
            # Descargar el archivo de pesos (archivo grande, puede tardar)
            print(f"Descargando pesos del modelo desde {weights_url} (esto puede tardar varios minutos)...")
            with open(weights_path, 'wb') as f:
                response = requests.get(weights_url, timeout=300)  # tiempo de espera más largo para archivos grandes
                response.raise_for_status()
                f.write(response.content)
            print(f"Archivo de pesos guardado en {weights_path}, tamaño: {os.path.getsize(weights_path)/1024/1024:.2f} MB")
            
            # Descargar el archivo de clases
            print(f"Descargando archivo de clases desde {classes_url}")
            with open(classes_path, 'wb') as f:
                response = requests.get(classes_url, timeout=30)
                response.raise_for_status()
                f.write(response.content)
            print(f"Archivo de clases guardado en {classes_path}")
        except Exception as e:
            print(f"Error al descargar archivos del modelo: {e}")
            raise
    
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
        Predice el tipo de evento en una imagen usando el modelo seleccionado.
        """
        try:
            # Usar el modelo seleccionado en la configuración
            if settings.AI_MODEL == "opencv_dnn":
                return self._predict_event_opencv_dnn(file_path)
            elif settings.AI_MODEL == "opencv_yolo":
                return self._predict_event_opencv_dnn(file_path)  # Usamos el mismo método ya que ahora carga YOLO
            else:  # Modelo por defecto: CLIP
                return self._predict_event_clip(file_path)
        except Exception as e:
            print(f"Error al predecir evento: {e}")
            return "unknown", 0.0
    
    def _predict_event_clip(self, file_path: str) -> Tuple[str, float]:
        """
        Predice el tipo de evento en una imagen usando CLIP.
        """
        try:
            self._load_clip_model()
            
            # Cargar y preprocesar la imagen
            image = Image.open(file_path)
            inputs = self.clip_processor(images=image, return_tensors="pt", padding=True)
            
            # Lista de eventos para clasificar (en inglés para el modelo CLIP)
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
            
            # Mapeo de eventos en inglés a español
            event_translation = {
                "sports event or game": "evento deportivo",
                "conference or meeting": "conferencia",
                "party or celebration": "fiesta",
                "concert or musical performance": "concierto",
                "wedding ceremony": "boda",
                "graduation ceremony": "graduación",
                "protest or demonstration": "protesta",
                "religious ceremony": "ceremonia religiosa",
                "parade or festival": "festival",
                "exhibition or art show": "exhibición",
                "family gathering": "reunión familiar",
                "food event or dining": "evento gastronómico",
                "outdoor activity or adventure": "actividad al aire libre",
                "business event": "evento de negocios",
                "educational event": "evento educativo"
            }
            
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
            english_event = event_texts[indices[0]].replace("a ", "").replace("an ", "")
            confidence = float(values[0])
            
            # Traducir el evento al español
            event_type = event_translation.get(english_event, english_event)
            
            return event_type, confidence
            
        except Exception as e:
            print(f"Error predicting event with CLIP: {e}")
            return "unknown", 0.0
            
    def _predict_event_opencv_dnn(self, file_path: str) -> Tuple[str, float]:
        """
        Predice el tipo de evento en una imagen usando OpenCV DNN con YOLO.
        """
        try:
            self._load_opencv_dnn_model()
            
            # Cargar la imagen
            img = cv2.imread(file_path)
            if img is None:
                raise ValueError(f"No se pudo cargar la imagen desde {file_path}")
            
            # Obtener las dimensiones de la imagen
            height, width = img.shape[:2]
            
            # Preprocesar la imagen para YOLO (transformar a blob)
            # YOLO espera un blob 416x416 con valores entre [0,1] y canales BGR
            blob = cv2.dnn.blobFromImage(
                img, 
                1/255.0,  # Factor de escala para normalizar píxeles a [0,1]
                (416, 416),  # Tamaño de entrada para YOLO
                swapRB=False,  # OpenCV ya usa BGR, YOLO también espera BGR
                crop=False
            )
            
            # Pasar la imagen por la red
            self.opencv_dnn_model.setInput(blob)
            
            # Obtener las predicciones de todas las capas de salida de YOLO
            # Esto contendrá información sobre los objetos detectados
            outputs = self.opencv_dnn_model.forward(self.yolo_output_layers)
            
            # Listas para almacenar los resultados
            detected_objects = []
            confidences = []
            class_ids = []
            
            # Umbral de confianza para las detecciones
            conf_threshold = 0.5
            
            # Procesar cada salida
            for output in outputs:
                # Cada fila es una detección
                for detection in output:
                    # Los primeros 4 valores son x, y, w, h (centro y dimensiones del bounding box)
                    # Resto de valores son las confianzas para cada clase
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    
                    if confidence > conf_threshold:
                        detected_objects.append(self.opencv_classes[class_id])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)
            
            # Mostrar los objetos detectados con su confianza
            print(f"Objetos detectados ({len(detected_objects)}):")
            for i, obj in enumerate(detected_objects):
                print(f"  - {obj}: {confidences[i]:.4f}")
            
            # Mapeo mejorado de objetos detectados por YOLO a eventos
            event_categories = {
                # Categorías deportivas
                "evento deportivo": {
                    "objects": ["sports ball", "baseball bat", "baseball glove", "tennis racket", 
                               "soccer ball", "football", "basketball", "baseball", "frisbee", 
                               "skis", "snowboard", "sports ball", "kite", "baseball bat", 
                               "baseball glove", "skateboard", "surfboard", "tennis racket"],
                    "weight": 1.2
                },
                
                # Categorías de conferencias/eventos educativos
                "conferencia": {
                    "objects": ["laptop", "tv", "book", "cell phone", "keyboard", "mouse",
                               "microphone", "projector", "presentation", "whiteboard"],
                    "weight": 1.0
                },
                
                # Celebraciones y fiestas
                "fiesta": {
                    "objects": ["wine glass", "cup", "cake", "bottle", "balloon",
                               "wine glass", "fork", "knife", "spoon", "bowl", "chair"],
                    "weight": 1.1
                },
                
                # Conciertos y eventos musicales
                "concierto": {
                    "objects": ["microphone", "chair", "person", "cell phone", "tv", "speaker"],
                    "weight": 1.15
                },
                
                # Bodas y ceremonias matrimoniales
                "boda": {
                    "objects": ["person", "tie", "dress", "suit", "cake", "wine glass", 
                               "chair", "dining table", "flower", "candle"],
                    "weight": 1.3
                },
                
                # Graduaciones
                "graduación": {
                    "objects": ["person", "book", "chair", "tie", "gown", "hat"],
                    "weight": 1.25
                },
                
                # Protestas y manifestaciones
                "protesta": {
                    "objects": ["person", "sign", "banner", "flag", "backpack"],
                    "weight": 1.0
                },
                
                # Ceremonias religiosas
                "ceremonia religiosa": {
                    "objects": ["person", "book", "chair", "vase", "candle"],
                    "weight": 1.0
                },
                
                # Desfiles y festivales
                "desfile o festival": {
                    "objects": ["person", "flag", "umbrella", "balloon", "backpack", "handbag"],
                    "weight": 1.0
                },
                
                # Eventos gastronómicos
                "evento gastronómico": {
                    "objects": ["dining table", "bottle", "wine glass", "cup", "fork", "knife", 
                               "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", 
                               "carrot", "hot dog", "pizza", "donut", "cake", "chair", "food"],
                    "weight": 1.0
                },
                
                # Actividades al aire libre
                "actividad al aire libre": {
                    "objects": ["bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", 
                               "boat", "bird", "cat", "dog", "horse", "sheep", "cow", "backpack", 
                               "umbrella", "handbag", "suitcase", "frisbee", "skis", "snowboard",
                               "kite", "skateboard", "surfboard", "tennis racket", "bottle", "tree", 
                               "mountain", "beach", "lake", "river"],
                    "weight": 1.0
                },
                
                # Reuniones familiares
                "reunión familiar": {
                    "objects": ["person", "chair", "couch", "potted plant", "dining table", "tv", 
                               "laptop", "cell phone", "book", "clock", "vase"],
                    "weight": 1.0
                },
                
                # Grupo general de personas
                "evento social": {
                    "objects": ["person"],
                    "weight": 0.8  # Menor peso ya que personas aparecen en muchos eventos
                }
            }
            
            # Sistema de puntuación para determinar el evento
            event_scores = {event: 0.0 for event in event_categories.keys()}
            
            # Analizar cada objeto detectado y acumular puntuaciones
            for obj, confidence in zip(detected_objects, confidences):
                # Comprobar cada categoría de evento
                for event, data in event_categories.items():
                    if obj in data["objects"]:
                        # Sumar puntuación ponderada si hay coincidencia
                        event_scores[event] += confidence * data["weight"]
                        print(f"  - Coincidencia '{obj}' para evento '{event}', score+={confidence * data['weight']:.4f}")
            
            # Factor de peso para eventos con múltiples objetos relevantes detectados
            # Esto favorece escenas con varios objetos de la misma categoría
            for event in event_scores:
                # Contar objetos únicos detectados para este evento
                unique_objects = set()
                for obj in detected_objects:
                    if obj in event_categories[event]["objects"]:
                        unique_objects.add(obj)
                
                # Aplicar multiplicador basado en la cantidad de objetos únicos
                if len(unique_objects) > 1:
                    multiplier = 1.0 + (min(len(unique_objects), 5) - 1) * 0.15  # Cap at +60% boost
                    event_scores[event] *= multiplier
                    print(f"  - Bonus para '{event}' por {len(unique_objects)} objetos únicos: x{multiplier:.2f}")
            
            # Encontrar el evento con mayor puntuación
            best_event = max(event_scores.items(), key=lambda x: x[1]) if event_scores else ("unknown", 0.0)
            event_type, score = best_event
            
            # Si no hay suficiente puntuación, es un evento desconocido
            if score <= 0.3:
                print("Puntuación baja, clasificando como evento desconocido")
                return "evento desconocido", max(confidences) if confidences else 0.0
                
            print(f"Evento clasificado como '{event_type}' con puntuación {score:.4f}")
            return event_type, score
            
        except Exception as e:
            print(f"Error predicting event with OpenCV DNN YOLO: {e}")
            import traceback
            traceback.print_exc()
            return "unknown", 0.0
    
    def create_processed_copy(self, original_file_path: str, creation_date: Optional[datetime] = None, event_type: Optional[str] = None) -> Optional[str]:
        """
        Crea una copia del archivo original con un nuevo nombre basado en la fecha y tipo de evento
        en el directorio processed.
        
        Args:
            original_file_path: Ruta al archivo original
            creation_date: Fecha de creación del archivo, si está disponible
            event_type: Tipo de evento asociado al archivo, si está disponible
            
        Returns:
            Optional[str]: Ruta web relativa al archivo procesado, o None si hay un error
        """
        try:
            # Asegurar que el directorio processed existe
            settings.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
            os.chmod(str(settings.PROCESSED_DIR), 0o777)
            
            # Obtener la fecha
            date_str = "sin-fecha"
            if creation_date:
                date_str = creation_date.strftime('%Y-%m-%d')
            else:
                # Intentar obtener la fecha de la última modificación del archivo
                try:
                    file_mtime = os.path.getmtime(original_file_path)
                    date_obj = datetime.fromtimestamp(file_mtime)
                    date_str = date_obj.strftime('%Y-%m-%d')
                except Exception as e:
                    print(f"No se pudo obtener la fecha de modificación: {e}")
            
            # Normalizar el tipo de evento
            event_str = "sin-evento"
            if event_type:
                # Reemplazar espacios y caracteres especiales
                event_str = event_type.lower().replace(" ", "-").replace("/", "-")
                event_str = ''.join(c for c in event_str if c.isalnum() or c == '-')
            
            # Crear el nuevo nombre de archivo
            original_path = Path(original_file_path)
            file_ext = original_path.suffix.lower()
            new_filename = f"{date_str}-{event_str}{file_ext}"
            
            # Verificar si ya existe un archivo con ese nombre y añadir un sufijo si es necesario
            target_path = settings.PROCESSED_DIR / new_filename
            counter = 1
            while target_path.exists():
                new_filename = f"{date_str}-{event_str}-{counter}{file_ext}"
                target_path = settings.PROCESSED_DIR / new_filename
                counter += 1
            
            # Copiar el archivo
            print(f"Copiando archivo a: {target_path}")
            shutil.copy2(original_file_path, str(target_path))
            
            # Verificar que la copia fue exitosa
            if target_path.exists():
                os.chmod(str(target_path), 0o777)
                print(f"Archivo procesado creado correctamente en {target_path}")
                # Ruta web relativa
                web_path = f"/processed/{new_filename}"
                return web_path
            else:
                print(f"ERROR: No se pudo crear el archivo procesado en {target_path}")
                return None
                
        except Exception as e:
            print(f"Error al crear copia procesada: {e}")
            return None
