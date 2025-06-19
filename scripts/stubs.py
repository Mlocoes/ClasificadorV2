"""
Stubs para importación de tipos utilizados en scripts externos.
Este archivo simula la estructura de app.core.config, app.services.media_processor
y app.core.database para satisfacer al analizador estático.
"""
from typing import Any, Dict, List, Optional, Tuple, Union, TypeVar, Generic, Callable

# ----- Simulación de app.core.config -----

class Settings:
    """Stub para la clase Settings de app.core.config"""
    PROJECT_NAME: str = "ClasificadorV2"
    API_V1_STR: str = "/api/v1"
    STORAGE_DIR: str = "/path/to/storage"
    UPLOADS_DIR: str = "/path/to/uploads"
    THUMBNAILS_DIR: str = "/path/to/thumbnails"
    PROCESSED_DIR: str = "/path/to/processed"
    AI_MODEL: str = "clip"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "sqlite:///./test.db"
    DATABASE_PATH: str = "./database.sqlite"
    TEST_MODE: bool = False

# Crear una instancia global para importarla
settings = Settings()

# ----- Simulación de app.services.media_processor -----

class MediaProcessor:
    """Stub para la clase MediaProcessor de app.services.media_processor"""
    
    def __init__(self, model_type: str = "clip"):
        self.model_type = model_type
        
    def process_media(self, file_path: str) -> Dict[str, Any]:
        """Stub para process_media"""
        return {"tags": ["sample"], "colors": ["#ffffff"], "confidence": 0.95}
    
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

# ----- Simulación de app.core.database -----

T = TypeVar('T')

class Base:
    """Stub para la clase Base de SQLAlchemy"""
    __tablename__: str = "stub_base"
    metadata: Any = None

class SessionLocal:
    """Stub para SessionLocal de SQLAlchemy"""
    
    def __init__(self):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Cierra la sesión"""
        pass
    
    def commit(self):
        """Commit de cambios"""
        pass
    
    def rollback(self):
        """Rollback de cambios"""
        pass
    
    def query(self, *entities: Any) -> 'Query':
        """Inicia una consulta"""
        return Query()
    
    def add(self, instance: Any):
        """Agrega una instancia a la sesión"""
        pass
    
    def delete(self, instance: Any):
        """Elimina una instancia"""
        pass

class Query:
    """Stub para Query de SQLAlchemy"""
    
    def filter(self, *criterion: Any) -> 'Query':
        return self
    
    def all(self) -> List[Any]:
        return []
    
    def first(self) -> Optional[Any]:
        return None
    
    def get(self, ident: Any) -> Optional[Any]:
        return None

# ----- Creación de módulos ficticios para el analizador estático -----

class AppCoreConfig:
    """Módulo ficticio para app.core.config"""
    settings = settings

class AppServicesMediaProcessor:
    """Módulo ficticio para app.services.media_processor"""
    MediaProcessor = MediaProcessor
    
class AppCoreDatabase:
    """Módulo ficticio para app.core.database"""
    Base = Base
    SessionLocal = SessionLocal
    
    @staticmethod
    def get_db() -> Any:
        """Función para obtener una sesión de base de datos"""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
