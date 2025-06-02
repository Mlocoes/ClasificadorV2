from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ClasificadorV2"
    
    # Directorios de almacenamiento
    STORAGE_DIR: Path = Path("../storage")
    UPLOADS_DIR: Path = STORAGE_DIR / "uploads"
    THUMBNAILS_DIR: Path = STORAGE_DIR / "thumbnails"
    
    # Base de datos
    SQLITE_URL: str = f"sqlite:///{STORAGE_DIR}/db.sqlite3"
    
    # Configuración CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Configuración de archivos
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/heic"]
    ALLOWED_VIDEO_TYPES: List[str] = ["video/mp4", "video/quicktime"]
    
    # Configuración de miniaturas
    THUMBNAIL_SIZE: tuple = (200, 200)
    
    class Config:
        case_sensitive = True

settings = Settings()