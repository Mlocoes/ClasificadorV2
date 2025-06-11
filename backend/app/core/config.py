from pathlib import Path
from typing import List, Literal
from pydantic_settings import BaseSettings
import json
import os

# Determinar si estamos en un entorno Docker o local
# En Docker, tendremos el directorio /app, en local usaremos el directorio del proyecto
def get_base_dir():
    if os.path.exists("/app"):
        return "/app"
    else:
        # Estamos en un entorno de desarrollo local
        # Obtener la ruta del proyecto (dos niveles arriba desde config.py)
        return str(Path(__file__).parent.parent.parent.parent)

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ClasificadorV2"
    
    # Configuración del modelo de IA
    AI_MODEL: Literal["clip", "opencv_dnn", "opencv_yolo"] = "clip"
    
    # Directorios de almacenamiento
    BASE_DIR: str = os.getenv("CLASIFICADOR_BASE_DIR", get_base_dir())
    STORAGE_DIR: Path = Path(BASE_DIR) / "storage"
    UPLOADS_DIR: Path = STORAGE_DIR / "uploads"
    THUMBNAILS_DIR: Path = STORAGE_DIR / "thumbnails"
    PROCESSED_DIR: Path = STORAGE_DIR / "processed"
    
    # Base de datos
    SQLITE_URL: str = f"sqlite:///{STORAGE_DIR}/db.sqlite3"
    
    # Configuración CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://frontend:3000",
        "http://127.0.0.1:3000",
        "http://192.168.0.7:3000",  # IP de red específica
        "*"  # Permitir todos los orígenes para desarrollo
    ]
    
    # Configuración de archivos
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/heic"]
    ALLOWED_VIDEO_TYPES: List[str] = ["video/mp4", "video/quicktime"]
    
    # Configuración de miniaturas
    THUMBNAIL_SIZE: tuple = (200, 200)
    # La única estrategia soportada es el directorio dedicado (/thumbnails)
    THUMBNAIL_STORAGE_STRATEGY: str = "dedicated_dir"
    
    class Config:
        case_sensitive = True

    # Función para guardar la configuración actual en un archivo JSON
    def save_config_to_file(self):
        """
        Guarda la configuración actual en un archivo JSON para persistencia.
        """
        config_dir = self.STORAGE_DIR / "config"
        config_dir.mkdir(exist_ok=True)
        config_path = config_dir / "app_config.json"
        
        try:
            # Crear configuración para guardar
            config_data = {
                "ai_model": self.AI_MODEL
            }
            
            # Guardar en formato JSON
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
                
            print(f"Configuración guardada en {config_path}")
            return True
        except Exception as e:
            print(f"Error al guardar la configuración: {e}")
            return False

    # Función para cargar la configuración desde un archivo JSON
    def load_config_from_file(self):
        """
        Carga la configuración desde un archivo JSON si existe.
        """
        config_path = self.STORAGE_DIR / "config" / "app_config.json"
        
        if not os.path.exists(config_path):
            print(f"No existe archivo de configuración en {config_path}")
            return False
            
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                
            # Actualizar la configuración global
            if "ai_model" in config_data:
                self.AI_MODEL = config_data["ai_model"]
                print(f"Modelo de IA cargado de la configuración: {self.AI_MODEL}")
                
            return True
        except Exception as e:
            print(f"Error al cargar la configuración: {e}")
            return False

settings = Settings()