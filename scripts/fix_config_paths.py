#!/usr/bin/env python3
"""
Script para corregir temporalmente la configuración de rutas en ClasificadorV2.

Este script modifica la configuración para usar rutas relativas del proyecto
en lugar de rutas absolutas hardcoded como "/app" que pueden causar
problemas de permisos.
"""

import os
import sys
from pathlib import Path
import traceback
import importlib.util

# Configurar rutas base
script_dir = Path(__file__).parent
project_dir = script_dir.parent
backend_dir = project_dir / "backend"

# Crear directorios de almacenamiento si no existen
storage_dir = project_dir / "storage"
for subdir in ["uploads", "thumbnails", "processed", "models/opencv_dnn"]:
    dir_path = storage_dir / subdir
    os.makedirs(dir_path, exist_ok=True)

# Función para cargar dinámicamente un módulo
def load_module(module_name, module_path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if not spec:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Asegurarse de que el backend está en el path
sys.path.insert(0, str(backend_dir))

# Crear archivos __init__.py necesarios
app_dir = backend_dir / "app"
for directory in [
    app_dir, 
    app_dir / "core", 
    app_dir / "services",
    app_dir / "api",
    app_dir / "api" / "v1"
]:
    if directory.exists() and not (directory / "__init__.py").exists():
        try:
            with open(directory / "__init__.py", 'w') as f:
                pass
            print(f"Creado archivo __init__.py en {directory}")
        except Exception as e:
            print(f"No se pudo crear __init__.py en {directory}: {e}")

try:
    # Cargar el módulo de configuración dinámicamente
    config_path = backend_dir / "app" / "core" / "config.py"
    config = load_module("config", config_path)
    
    # Obtener el objeto settings
    settings = getattr(config, "settings")
    
    print("=== CORRECTOR DE CONFIGURACIÓN DE RUTAS ===")
    
    # Mostrar la configuración actual
    print(f"\nConfiguración actual:")
    print(f"  STORAGE_DIR: {settings.STORAGE_DIR}")
    print(f"  UPLOADS_DIR: {settings.UPLOADS_DIR}")
    print(f"  THUMBNAILS_DIR: {settings.THUMBNAILS_DIR}")
    print(f"  PROCESSED_DIR: {settings.PROCESSED_DIR}")
    print(f"  SQLITE_URL: {settings.SQLITE_URL}")
    
    # Corregir rutas para usar el directorio del proyecto
    print("\nAplicando corrección de rutas...")
    
    # Establecer el directorio de storage relativo al proyecto
    settings.STORAGE_DIR = project_dir / "storage"
    
    # Actualizar directorios dependientes
    settings.UPLOADS_DIR = settings.STORAGE_DIR / "uploads"
    settings.THUMBNAILS_DIR = settings.STORAGE_DIR / "thumbnails"
    settings.PROCESSED_DIR = settings.STORAGE_DIR / "processed"
    
    # Actualizar URL de SQLite
    settings.SQLITE_URL = f"sqlite:///{settings.STORAGE_DIR}/db.sqlite3"
    
    # Mostrar la configuración actualizada
    print(f"\nConfiguración actualizada:")
    print(f"  STORAGE_DIR: {settings.STORAGE_DIR}")
    print(f"  UPLOADS_DIR: {settings.UPLOADS_DIR}")
    print(f"  THUMBNAILS_DIR: {settings.THUMBNAILS_DIR}")
    print(f"  PROCESSED_DIR: {settings.PROCESSED_DIR}")
    print(f"  SQLITE_URL: {settings.SQLITE_URL}")
    
    # Asegurarse de que los directorios existen
    for dir_path in [
        settings.STORAGE_DIR,
        settings.UPLOADS_DIR,
        settings.THUMBNAILS_DIR,
        settings.PROCESSED_DIR,
        settings.STORAGE_DIR / "models" / "opencv_dnn"
    ]:
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  Creado directorio: {dir_path}")
        else:
            print(f"  Directorio existente: {dir_path}")
    
    print("\n=== CORRECCIÓN COMPLETADA ===")
    print("\nAhora puede ejecutar los scripts con este ajuste temporal")
    print("Para una solución permanente, modifique el archivo backend/app/core/config.py")
    
except Exception as e:
    print(f"Error al corregir la configuración: {e}")
    traceback.print_exc()
    sys.exit(1)
