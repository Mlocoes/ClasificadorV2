# Este archivo contiene los stubs para API de backend usado en scripts
# Nota: No borrar ni modificar este archivo, es necesario para el análisis estático de código

from typing import Dict, List, Any, Optional, Union, Tuple

# Stub para settings de app.core.config
class Settings:
    """Stub de Settings para uso en scripts"""
    PROJECT_NAME: str = "ClasificadorV2"
    API_V1_STR: str = "/api/v1"
    AI_MODEL: str = "clip"
    STORAGE_DIR: str = "/app/storage"
    UPLOADS_DIR: str = "/app/storage/uploads"
    THUMBNAILS_DIR: str = "/app/storage/thumbnails"  
    PROCESSED_DIR: str = "/app/storage/processed"

settings = Settings()

# Stub para MediaProcessor
class MediaProcessor:
    """Stub de MediaProcessor para uso en scripts"""
    
    def __init__(self, model_type: str = "clip"):
        self.model_type = model_type
        
    def process_media(self, file_path: str) -> Dict[str, Any]:
        """Procesa un archivo multimedia y devuelve metadatos"""
        return {
            "tags": ["example", "stub"],
            "colors": ["#FFFFFF", "#000000"],
            "dominant_color": "#FFFFFF",
            "confidence": 0.95
        }
        
    def regenerate_thumbnails(self, directory: str) -> Dict[str, int]:
        """Regenera miniaturas para un directorio"""
        return {
            "processed": 0,
            "failed": 0,
            "skipped": 0
        }
        
    @classmethod
    def get_supported_models(cls) -> List[str]:
        """Devuelve lista de modelos soportados"""
        return ["clip", "opencv_dnn", "opencv_yolo"]
