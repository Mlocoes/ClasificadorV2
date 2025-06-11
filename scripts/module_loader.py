#!/usr/bin/env python3
"""
Módulo de utilidad para cargar los módulos de la aplicación desde scripts externos.

Este módulo configura el PYTHONPATH correctamente para permitir importar los módulos
de la aplicación desde scripts que se ejecutan fuera del directorio principal.
"""

import os
import sys
from pathlib import Path

def setup_module_imports():
    """
    Configura el PYTHONPATH para importar módulos de la aplicación desde cualquier script.
    
    Returns:
        bool: True si se pudieron importar los módulos correctamente, False en caso contrario
    """
    # Determinar las rutas absolutas
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(script_dir, ".."))
    backend_dir = os.path.join(project_dir, "backend")
    
    # Agregar el directorio del backend al path
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    # Asegurar que los directorios de la app tengan archivos __init__.py
    app_dir = os.path.join(backend_dir, "app")
    for directory in [app_dir, 
                      os.path.join(app_dir, "core"), 
                      os.path.join(app_dir, "services"),
                      os.path.join(app_dir, "api"),
                      os.path.join(app_dir, "api", "v1")]:
        if os.path.isdir(directory) and not os.path.exists(os.path.join(directory, "__init__.py")):
            try:
                with open(os.path.join(directory, "__init__.py"), 'w') as f:
                    pass
                print(f"Creado archivo __init__.py en {directory}")
            except:
                pass
    
    # Intentar importar los módulos
    try:
        # Intentamos importar los módulos para verificar que funciona
        from app.core.config import settings
        from app.services.media_processor import MediaProcessor
        print("✅ Módulos importados correctamente")
        
        # Asegurarnos de que las rutas de storage apunten al directorio correcto
        if hasattr(settings, 'STORAGE_DIR') and str(settings.STORAGE_DIR).startswith('/app'):
            print("⚠️ La configuración está usando rutas absolutas (/app).")
            print("   Considere ejecutar fix_config_paths.py para corregir las rutas.")
            
        return True
    except ImportError as e:
        print(f"❌ Error al importar módulos: {e}")
        
        # Intentar método alternativo: cambiar al directorio del backend
        print("Intentando método alternativo: cambiar al directorio del backend")
        original_dir = os.getcwd()
        os.chdir(backend_dir)
        
        try:
            from app.core.config import settings
            from app.services.media_processor import MediaProcessor
            print("✅ Módulos importados correctamente con el método alternativo")
            # Volver al directorio original
            os.chdir(original_dir)
            return True
        except ImportError as e2:
            print(f"❌ Error persistente al importar módulos: {e2}")
            # Volver al directorio original
            os.chdir(original_dir)
            
            # Mostrar información de depuración
            print(f"\nInformación de depuración:")
            print(f"- Directorio del script: {script_dir}")
            print(f"- Directorio del proyecto: {project_dir}")
            print(f"- Directorio del backend: {backend_dir}")
            print(f"- PYTHONPATH: {sys.path}")
            
            # Verificar la estructura de directorios
            print("\nEstructura de directorios del backend:")
            if os.path.exists(backend_dir):
                print(f"✅ Directorio backend existe")
                for subdir in ["app", "app/core", "app/services"]:
                    full_path = os.path.join(backend_dir, subdir)
                    if os.path.exists(full_path):
                        print(f"  ✅ {subdir} existe")
                    else:
                        print(f"  ❌ {subdir} NO existe")
            else:
                print(f"❌ Directorio backend NO existe")
                
            return False

if __name__ == "__main__":
    # Si se ejecuta este script directamente, mostrar información
    setup_module_imports()
