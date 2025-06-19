"""
Inicializador del paquete de scripts.
Este paquete contiene scripts de utilidad para el proyecto ClasificadorV2.
"""

# Importaciones para facilitar el acceso desde otros módulos
from .module_loader_v2 import (
    import_app_modules,
    setup_paths
)

__all__ = [
    'import_app_modules',
    'setup_paths'
]
