"""
Tests de configuración y utilidades básicas.
"""
import os
import pytest
from pathlib import Path
from app.core.config import Settings

def test_settings_load():
    """Prueba que las configuraciones se carguen correctamente."""
    # Crear configuración para test
    settings = Settings()
    
    # Verificar que los directorios se configuran correctamente
    assert settings.PROJECT_NAME == "ClasificadorV2"
    assert isinstance(settings.STORAGE_DIR, Path)
    assert isinstance(settings.UPLOADS_DIR, Path)
    assert isinstance(settings.THUMBNAILS_DIR, Path)
    assert isinstance(settings.PROCESSED_DIR, Path)
    assert isinstance(settings.CONFIG_DIR, Path)
    assert isinstance(settings.LOG_DIR, Path)
    
    # Verificar configuración de logging
    assert settings.LOG_LEVEL in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    assert isinstance(settings.LOG_TO_FILE, bool)

def test_directories_structure():
    """Prueba que la estructura de directorios sea correcta."""
    settings = Settings()
    
    # Verificar relaciones de directorios
    assert settings.UPLOADS_DIR.parent == settings.STORAGE_DIR
    assert settings.THUMBNAILS_DIR.parent == settings.STORAGE_DIR
    assert settings.PROCESSED_DIR.parent == settings.STORAGE_DIR
    
    # Verificar nomenclatura correcta
    assert settings.UPLOADS_DIR.name == "uploads"
    assert settings.THUMBNAILS_DIR.name == "thumbnails"
    assert settings.PROCESSED_DIR.name == "processed"
