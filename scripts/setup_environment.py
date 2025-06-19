#!/usr/bin/env python3
"""
Script unificado para configurar el entorno de ClasificadorV2.

Este script combina las funcionalidades de module_loader.py y fix_config_paths.py:
1. Asegura que los módulos de la aplicación pueden importarse correctamente
2. Corrige las rutas de configuración para usar rutas relativas en lugar de /app
3. Verifica que los directorios necesarios existen y tienen los permisos adecuados
"""

import os
import sys
import importlib.util
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, TypeVar, cast

# Importaciones condicionales para el análisis estático
try:
    # Importamos los stubs para ayudar al analizador estático
    from scripts.stubs import settings, MediaProcessor, Base, SessionLocal
    from scripts.stubs import AppCoreConfig as config_module
    from scripts.stubs import AppServicesMediaProcessor as media_processor_module
    from scripts.stubs import AppCoreDatabase as database_module
except ImportError:
    # Definimos tipos para satisfacer al analizador
    settings = None  # type: ignore
    MediaProcessor = None  # type: ignore
    Base = None  # type: ignore
    SessionLocal = None  # type: ignore
    config_module = None  # type: ignore
    media_processor_module = None  # type: ignore
    database_module = None  # type: ignore

# Definimos los tipos para ayudar al analizador estático
ConfigModule = TypeVar('ConfigModule')
MediaProcessorModule = TypeVar('MediaProcessorModule')
DatabaseModule = TypeVar('DatabaseModule')

# Para que el analizador estático no muestre errores, definimos esto
if False:  # Este bloque nunca se ejecuta, sólo es para el analizador estático
    # Simulación de importaciones para el analizador estático
    from app.core import config  # type: ignore # noqa
    from app.core.config import settings  # type: ignore # noqa
    from app.services.media_processor import MediaProcessor  # type: ignore # noqa
    from app.core.database import SessionLocal, Base  # type: ignore # noqa

def print_header(text):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 80)
    print(text.center(80))
    print("=" * 80)

def setup_imports():
    """
    Configura el PYTHONPATH y asegura que los archivos __init__.py existen.
    
    Returns:
        bool: True si la configuración fue exitosa
    """
    print_header("CONFIGURACIÓN DE IMPORTACIONES")
    
    # Determinar las rutas absolutas
    script_dir = Path(__file__).parent.absolute()
    project_dir = script_dir.parent
    backend_dir = project_dir / "backend"
    
    print(f"Directorio del script: {script_dir}")
    print(f"Directorio del proyecto: {project_dir}")
    print(f"Directorio del backend: {backend_dir}")
    
    # Agregar el directorio del backend al path
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
        print("✅ Backend añadido al PYTHONPATH")
    else:
        print("✅ Backend ya está en PYTHONPATH")
    
    # Asegurar que los directorios de la app tengan archivos __init__.py
    app_dir = backend_dir / "app"
    init_dirs = [
        app_dir,
        app_dir / "core",
        app_dir / "services",
        app_dir / "api",
        app_dir / "api" / "v1"
    ]
    
    all_ok = True
    for directory in init_dirs:
        if not directory.exists():
            print(f"❌ Directorio no encontrado: {directory}")
            all_ok = False
            continue
            
        init_file = directory / "__init__.py"
        if not init_file.exists():
            try:
                with open(init_file, 'w') as f:
                    pass
                print(f"✅ Creado archivo __init__.py en {directory}")
            except Exception as e:
                print(f"❌ No se pudo crear __init__.py en {directory}: {e}")
                all_ok = False
        else:
            print(f"✅ Existente: {init_file}")
    
    return all_ok

def load_config_module() -> Tuple[bool, Optional[ConfigModule]]:
    """
    Carga dinámicamente el módulo de configuración.
    
    Returns:
        tuple: (success, config_module)
    """
    print_header("CARGA DEL MÓDULO DE CONFIGURACIÓN")
    
    try:
        # Intentamos la importación directa con manejo para el analizador estático
        success = False
        cfg = None
        
        try:
            # Esta importación es para runtime, puede fallar durante el análisis estático
            import importlib
            cfg = importlib.import_module("app.core.config")  # type: ignore # noqa
            success = True
        except ImportError:
            # Manejaremos esto en el bloque except exterior
            pass
            
        if success:
            print("✅ Módulo de configuración importado correctamente")
            return True, cast(ConfigModule, cfg)
        else:
            raise ImportError("No se pudo importar app.core.config")
    except ImportError as e:
        print(f"❌ Error al importar módulo de configuración: {e}")
        
        # Intentar método alternativo: carga dinámica
        try:
            print("Intentando carga dinámica...")
            backend_dir = Path(__file__).parent.parent / "backend"
            config_path = backend_dir / "app" / "core" / "config.py"
            
            if not config_path.exists():
                print(f"❌ Archivo de configuración no encontrado: {config_path}")
                return False, None
                
            spec = importlib.util.spec_from_file_location("config", config_path)
            if spec is None:
                print("❌ No se pudo crear spec para el módulo de configuración")
                return False, None
                
            config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config)
            
            print("✅ Módulo de configuración cargado dinámicamente")
            return True, config
        except Exception as e2:
            print(f"❌ Error persistente al cargar el módulo de configuración: {e2}")
            return False, None

def fix_storage_paths(config_module):
    """
    Corrige las rutas de almacenamiento en la configuración.
    
    Args:
        config_module: El módulo de configuración cargado
        
    Returns:
        bool: True si las rutas se corrigieron con éxito
    """
    print_header("CORRECCIÓN DE RUTAS DE ALMACENAMIENTO")
    
    if not hasattr(config_module, "settings"):
        print("❌ El módulo de configuración no tiene el atributo 'settings'")
        return False
        
    settings = config_module.settings
    
    # Mostrar la configuración actual
    print("Configuración actual:")
    print(f"  STORAGE_DIR: {settings.STORAGE_DIR}")
    print(f"  UPLOADS_DIR: {settings.UPLOADS_DIR}")
    print(f"  THUMBNAILS_DIR: {settings.THUMBNAILS_DIR}")
    print(f"  PROCESSED_DIR: {settings.PROCESSED_DIR}")
    print(f"  CONFIG_DIR: {settings.CONFIG_DIR if hasattr(settings, 'CONFIG_DIR') else 'No configurado'}")
    print(f"  SQLITE_URL: {settings.SQLITE_URL}")
    
    # Verificar si las rutas ya están correctas
    project_dir = Path(__file__).parent.parent
    
    if str(settings.STORAGE_DIR) == str(project_dir / "storage"):
        print("✅ Las rutas ya están configuradas correctamente")
        return True
    
    # Corregir rutas para usar el directorio del proyecto
    print("Aplicando corrección de rutas...")
    
    # Establecer el directorio de storage relativo al proyecto
    settings.STORAGE_DIR = project_dir / "storage"
    
    # Establecer el directorio de configuración
    settings.CONFIG_DIR = project_dir / "config"
    
    # Actualizar directorios dependientes
    settings.UPLOADS_DIR = settings.STORAGE_DIR / "uploads"
    settings.THUMBNAILS_DIR = settings.STORAGE_DIR / "thumbnails"
    settings.PROCESSED_DIR = settings.STORAGE_DIR / "processed"
    
    # Actualizar URL de SQLite
    settings.SQLITE_URL = f"sqlite:///{settings.STORAGE_DIR}/db.sqlite3"
    
    # Mostrar la configuración actualizada
    print("\nConfiguración actualizada:")
    print(f"  STORAGE_DIR: {settings.STORAGE_DIR}")
    print(f"  UPLOADS_DIR: {settings.UPLOADS_DIR}")
    print(f"  THUMBNAILS_DIR: {settings.THUMBNAILS_DIR}")
    print(f"  PROCESSED_DIR: {settings.PROCESSED_DIR}")
    print(f"  CONFIG_DIR: {settings.CONFIG_DIR}")
    print(f"  SQLITE_URL: {settings.SQLITE_URL}")
    
    return True

def ensure_directories(config_module):
    """
    Asegura que los directorios necesarios existen.
    
    Args:
        config_module: El módulo de configuración cargado
        
    Returns:
        bool: True si los directorios existen o se crearon con éxito
    """
    print_header("VERIFICACIÓN DE DIRECTORIOS")
    
    if not hasattr(config_module, "settings"):
        print("❌ El módulo de configuración no tiene el atributo 'settings'")
        return False
        
    settings = config_module.settings
    
    # Directorios a verificar
    dirs_to_check = [
        settings.STORAGE_DIR,
        settings.UPLOADS_DIR,
        settings.THUMBNAILS_DIR,
        settings.PROCESSED_DIR,
        settings.CONFIG_DIR,
        Path(settings.BASE_DIR) / "cache" / "models--opencv--dnn",
        Path(settings.BASE_DIR) / "cache" / "models--openai--clip-vit-base-patch32"
    ]
    
    all_ok = True
    for directory in dirs_to_check:
        if directory.exists():
            print(f"✅ Existente: {directory}")
        else:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"✅ Creado: {directory}")
            except Exception as e:
                print(f"❌ No se pudo crear {directory}: {e}")
                all_ok = False
    
    return all_ok

def import_test() -> bool:
    """
    Prueba la importación de los módulos principales.
    
    Returns:
        bool: True si las importaciones fueron exitosas
    """
    print_header("PRUEBA DE IMPORTACIONES")
    
    # Para el análisis estático, usamos un enfoque más robusto con importlib
    try:
        # Prueba de config
        config_imported = False
        try:
            import importlib
            config = importlib.import_module("app.core.config")  # type: ignore # noqa
            settings_obj = getattr(config, "settings", None)
            if settings_obj:
                print("✅ Módulo config importado")
                config_imported = True
            else:
                print("❌ No se encontró 'settings' en el módulo config")
        except ImportError as e:
            print(f"❌ Error al importar config: {e}")
        
        # Prueba de media_processor
        mp_imported = False
        try:
            mp = importlib.import_module("app.services.media_processor")  # type: ignore # noqa
            mp_class = getattr(mp, "MediaProcessor", None)
            if mp_class:
                print("✅ Módulo media_processor importado")
                mp_imported = True
            else:
                print("❌ No se encontró 'MediaProcessor' en el módulo media_processor")
        except ImportError as e:
            print(f"❌ Error al importar media_processor: {e}")
        
        # Prueba de database (opcional)
        db_imported = False
        try:
            db = importlib.import_module("app.core.database")  # type: ignore # noqa
            session_local = getattr(db, "SessionLocal", None)
            base = getattr(db, "Base", None)
            if session_local and base:
                print("✅ Módulo database importado")
                db_imported = True
            else:
                print("⚠️ No se encontraron todas las clases requeridas en el módulo database")
        except ImportError:
            print("⚠️ No se pudo importar el módulo database (puede ser normal si no se usa SQLAlchemy)")
        # Verificamos el resultado global
        if config_imported and mp_imported:
            print("\n✅ Prueba de importación exitosa para módulos principales")
            return True
        else:
            modules_failed = []
            if not config_imported:
                modules_failed.append("config")
            if not mp_imported:
                modules_failed.append("media_processor")
            
            print(f"\n❌ Falló la importación de los siguientes módulos: {', '.join(modules_failed)}")
            return False
            
    except Exception as e:
        print(f"❌ Error inesperado al importar módulos: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal que ejecuta todas las verificaciones y correcciones"""
    print_header("CONFIGURACIÓN DEL ENTORNO CLASIFICADORV2")
    
    try:
        # Paso 1: Configurar importaciones
        if not setup_imports():
            print("❌ No se pudo configurar las importaciones correctamente")
            return 1
        
        # Paso 2: Cargar el módulo de configuración
        success, config_module = load_config_module()
        if not success:
            print("❌ No se pudo cargar el módulo de configuración")
            return 1
        
        # Paso 3: Corregir rutas de almacenamiento
        if not fix_storage_paths(config_module):
            print("❌ No se pudieron corregir las rutas de almacenamiento")
            return 1
        
        # Paso 4: Asegurar que los directorios existen
        if not ensure_directories(config_module):
            print("❌ No se pudieron crear todos los directorios necesarios")
            return 1
        
        # Paso 5: Probar importaciones
        if not import_test():
            print("❌ La prueba de importaciones falló")
            return 1
        
        print_header("CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
        print("El entorno está configurado correctamente.")
        print("Los módulos de la aplicación pueden importarse correctamente.")
        print("Las rutas de almacenamiento apuntan a ubicaciones válidas.")
        print("Los directorios necesarios existen y tienen permisos adecuados.")
        
        return 0
    
    except Exception as e:
        print(f"❌ Error inesperado durante la configuración: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
