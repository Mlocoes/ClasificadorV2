"""
Configuración para pruebas con pytest.
Define fixtures y configuraciones comunes.
"""
import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

# Crear motor de base de datos en memoria para tests
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear estructura de directorios temporales para test
@pytest.fixture(scope="session")
def temp_media_dirs(tmp_path_factory):
    """Crea directorios temporales para pruebas de archivos multimedia."""
    base_dir = tmp_path_factory.mktemp("testmedia")
    uploads_dir = base_dir / "uploads"
    thumbnails_dir = base_dir / "thumbnails"
    processed_dir = base_dir / "processed"
    
    # Crear directorios
    uploads_dir.mkdir()
    thumbnails_dir.mkdir()
    processed_dir.mkdir()
    
    return {
        "base_dir": base_dir,
        "uploads_dir": uploads_dir,
        "thumbnails_dir": thumbnails_dir,
        "processed_dir": processed_dir
    }

@pytest.fixture
def test_db():
    """Configurar base de datos de prueba."""
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Usar la sesión de prueba
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
    # Eliminar todas las tablas después de la prueba
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    """Cliente de prueba para la API."""
    # Sobrescribir la dependencia get_db para usar la base de datos de test
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
        
    # Limpiar las sobreescrituras de dependencias
    app.dependency_overrides = {}
