#!/usr/bin/env python3
"""
Módulo de utilidad mejorado para cargar los módulos de la aplicación desde scripts externos.

Este módulo proporciona funciones para:
1. Configurar el PYTHONPATH correctamente
2. Cargar dinámicamente los módulos necesarios
3. Manejar problemas comunes de importación
4. Proporcionar información de depuración detallada
"""

import os
import sys
from pathlib import Path
import importlib.util
import traceback
from typing import Any, Dict, List, Optional, Tuple, Union, TypeVar, cast

# Importación condicional para el analizador estático
# Esto ayuda al editor pero no se ejecuta en tiempo de ejecución
try:
    # Importamos los stubs para ayudar al analizador estático
    from scripts.stubs import settings, MediaProcessor
    from scripts.stubs import AppCoreConfig as config
    from scripts.stubs import AppServicesMediaProcessor as media_processor
except ImportError:
    # Definimos tipos para satisfacer al analizador
    settings = None  # type: ignore
    MediaProcessor = None  # type: ignore
    config = None  # type: ignore
    media_processor = None  # type: ignore

# Definimos los tipos para ayudar al analizador estático
ConfigModule = TypeVar('ConfigModule')
MediaProcessorModule = TypeVar('MediaProcessorModule')

# Variables globales donde guardaremos los módulos importados
app_config = None  # type: Optional[ConfigModule]
app_media_processor = None  # type: Optional[MediaProcessorModule]

def setup_paths() -> Tuple[Optional[Path], Optional[Path], Optional[Path]]:
    """
    Configura las rutas necesarias para importar módulos de la aplicación.
    
    Returns:
        tuple: (project_dir, backend_dir, app_dir) o (None, None, None) en caso de error
    """
    # Determinar rutas absolutas
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    project_dir = script_dir.parent
    backend_dir = project_dir / "backend"
    app_dir = backend_dir / "app"
    
    # Mostrar información sobre las rutas
    print("\n=== Configuración de rutas ===")
    print(f"Directorio de scripts: {script_dir}")
    print(f"Directorio del proyecto: {project_dir}")
    print(f"Directorio backend: {backend_dir}")
    print(f"Directorio app: {app_dir}")
    
    # Verificar que los directorios existan
    if not backend_dir.exists():
        print(f"❌ ERROR: El directorio backend no existe: {backend_dir}")
        return None, None, None
    
    if not app_dir.exists():
        print(f"❌ ERROR: El directorio app no existe: {app_dir}")
        return None, None, None
    
    # Agregar el directorio del backend al path
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
        print(f"✅ Backend añadido al PYTHONPATH: {backend_dir}")
    else:
        print(f"✅ Backend ya en PYTHONPATH: {backend_dir}")
    
    return project_dir, backend_dir, app_dir

def ensure_init_files(app_dir: Path) -> None:
    """
    Asegura que existan los archivos __init__.py necesarios en los subdirectorios.
    
    Args:
        app_dir: Path al directorio app
    """
    print("\n=== Verificando archivos __init__.py ===")
    # Lista de directorios donde necesitamos __init__.py
    dirs_to_check = [
        app_dir,
        app_dir / "core",
        app_dir / "services",
        app_dir / "api",
        app_dir / "api" / "v1"
    ]
    
    # Crear __init__.py en cada directorio si no existe
    for directory in dirs_to_check:
        if not directory.exists():
            print(f"❌ Directorio no encontrado: {directory}")
            continue
            
        init_file = directory / "__init__.py"
        if not init_file.exists():
            try:
                with open(init_file, 'w') as f:
                    pass
                print(f"✅ Creado archivo __init__.py en {directory}")
            except Exception as e:
                print(f"❌ No se pudo crear __init__.py en {directory}: {e}")
        else:
            print(f"✅ Existente: {init_file}")

def load_modules_dynamically() -> Tuple[Optional[ConfigModule], Optional[MediaProcessorModule]]:
    """
    Carga dinámicamente los módulos de la aplicación.
    
    Returns:
        tuple: (config, media_processor) - Módulos cargados o (None, None) si hay error
    """
    print("\n=== Cargando módulos dinámicamente ===")
    try:
        # Buscar los módulos
        config_spec = importlib.util.find_spec("app.core.config")
        if not config_spec:
            print("❌ No se pudo encontrar el módulo app.core.config")
            return None, None

        media_processor_spec = importlib.util.find_spec("app.services.media_processor")
        if not media_processor_spec:
            print("❌ No se pudo encontrar el módulo app.services.media_processor")
            return None, None
        
        # Cargar los módulos
        config_module = importlib.util.module_from_spec(config_spec)
        media_processor_module = importlib.util.module_from_spec(media_processor_spec)
        
        config_spec.loader.exec_module(config_module)
        media_processor_spec.loader.exec_module(media_processor_module)
        
        print("✅ Módulos importados correctamente")
        
        # Usamos cast para indicar al analizador estático que confiamos en este tipo
        return cast(ConfigModule, config_module), cast(MediaProcessorModule, media_processor_module)
        
    except Exception as e:
        print(f"❌ Error al cargar módulos: {e}")
        print("\nTraceback del error:")
        traceback.print_exc()
        return None, None

def import_app_modules() -> Tuple[Optional[ConfigModule], Optional[MediaProcessorModule]]:
    """
    Configura el entorno y carga los módulos necesarios de la aplicación.
    
    Returns:
        tuple: (config, media_processor) - Módulos cargados o (None, None) si hay error
    """
    print("\n===== CARGADOR DE MÓDULOS DE APLICACIÓN =====")
    
    # Configurar rutas
    project_dir, backend_dir, app_dir = setup_paths()
    if not backend_dir or not app_dir:
        return None, None
    
    # Asegurar archivos __init__.py
    ensure_init_files(app_dir)
    
    # Intentar el primer método: importación directa
    try:
        print("\n=== Método 1: Importación directa ===")
        # Importación segura para el analizador estático
        import_successful = False
        try:
            # Importación directa - es importante usar import_module para evitar problemas con el analizador
            import importlib as importlib_direct
            # type: ignore # Añadido para evitar errores del analizador estático
            importlib_direct.import_module("app.core.config")  # type: ignore # noqa
            importlib_direct.import_module("app.services.media_processor")  # type: ignore # noqa
            import_successful = True
        except ImportError:
            pass  # Manejado por el bloque exterior

        if import_successful:
            print("✅ Módulos importados directamente con éxito")
            # Importar dinámicamente para devolver los módulos
            return load_modules_dynamically()
        else:
            raise ImportError("Error en importación directa")
    except Exception as e:
        print(f"❌ Error en importación directa: {e}")
    
    # Intentar método alternativo: cambiar al directorio backend
    print("\n=== Método 2: Cambio de directorio ===")
    original_dir = os.getcwd()
    os.chdir(str(backend_dir))
    print(f"Directorio de trabajo cambiado a: {os.getcwd()}")
    
    try:
        # Importación segura para el analizador estático
        import importlib
        _config = importlib.import_module("app.core.config")  # type: ignore # noqa
        _media_processor = importlib.import_module("app.services.media_processor")  # type: ignore # noqa
        print("✅ Módulos importados con éxito usando cambio de directorio")
        
        # Volver al directorio original
        os.chdir(original_dir)
        print(f"Directorio de trabajo restaurado a: {os.getcwd()}")
        
        # Cargar dinámicamente para devolver los módulos
        return load_modules_dynamically()
        
    except Exception as e:
        print(f"❌ Error en importación con cambio de directorio: {e}")
        # Volver al directorio original
        os.chdir(original_dir)
        print(f"Directorio de trabajo restaurado a: {os.getcwd()}")
    
    # Mostrar información del sistema para debugging
    print("\n=== Información del sistema para debugging ===")
    print(f"Python: {sys.version}")
    print(f"PYTHONPATH: {sys.path}")
    print(f"Directorio actual: {os.getcwd()}")
    
    print("\nVariable de entorno PYTHONPATH:")
    if "PYTHONPATH" in os.environ:
        print(f"  {os.environ['PYTHONPATH']}")
    else:
        print("  No definida")
    
    # Verificar permisos de directorios importantes
    print("\nPermisos de directorios críticos:")
    for dir_path in [backend_dir, app_dir, app_dir / "core", app_dir / "services"]:
        if dir_path.exists():
            try:
                test_access = os.access(dir_path, os.R_OK)
                print(f"  {dir_path}: {'Legible' if test_access else 'NO legible'}")
            except Exception as e:
                print(f"  No se pudo verificar permisos de {dir_path}: {e}")
    
    print("\n❌ No se pudo cargar los módulos de la aplicación.")
    return None, None

def show_help() -> None:
    """Muestra información de ayuda para solucionar problemas de importación"""
    print("""
=== SUGERENCIAS PARA RESOLVER PROBLEMAS DE IMPORTACIÓN ===

1. Asegúrate de que los archivos __init__.py existen en todos los subdirectorios:
   - backend/app/__init__.py
   - backend/app/core/__init__.py
   - backend/app/services/__init__.py
   - backend/app/api/__init__.py
   - backend/app/api/v1/__init__.py

2. Comprueba el PYTHONPATH:
   - Crea un archivo .env en la raíz del proyecto con:
     PYTHONPATH=${workspaceFolder}/backend

3. Configura VS Code:
   - Asegúrate de tener un archivo .vscode/settings.json con:
     {
       "python.analysis.extraPaths": ["${workspaceFolder}/backend"],
       "python.autoComplete.extraPaths": ["${workspaceFolder}/backend"]
     }

4. Permisos:
   - Comprueba que tienes permisos de lectura en todos los directorios

5. Errores específicos:
   - Si ves "No module named 'app'": asegúrate que backend está en PYTHONPATH
   - Si ves "cannot import name X from app.Y": verifica que el módulo exista y esté correctamente implementado
    """)

if __name__ == "__main__":
    # Si se ejecuta este script directamente, mostrar información
    config, media_processor = import_app_modules()
    
    if not config or not media_processor:
        show_help()
        sys.exit(1)
    
    print("\nPrueba exitosa: Módulos cargados correctamente")
    sys.exit(0)
