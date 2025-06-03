#!/bin/bash

echo "=== Script para actualizar la estrategia de miniaturas ==="

# Comprobar si se proporcionó el argumento
if [ -z "$1" ]; then
    echo "Error: Debe especificar una estrategia."
    echo "Uso: $0 <estrategia>"
    echo "Estrategias disponibles:"
    echo "  - dedicated_dir: Todas las miniaturas en un directorio dedicado"
    echo "  - subdir: Crear subdirectorios 'thumbnails' en cada directorio de archivos"
    echo "  - base_dir: Usar el directorio raíz + 'thumbnails'"
    exit 1
fi

STRATEGY=$1

# Validar la estrategia
if [ "$STRATEGY" != "dedicated_dir" ] && [ "$STRATEGY" != "subdir" ] && [ "$STRATEGY" != "base_dir" ]; then
    echo "Error: Estrategia no válida."
    echo "Las estrategias disponibles son: dedicated_dir, subdir, base_dir"
    exit 1
fi

echo "Actualizando la estrategia de miniaturas a: $STRATEGY"

# Actualizar la configuración en el contenedor
docker exec clasificadorv2-backend-1 python -c "
import re
from pathlib import Path

# Actualizar el archivo de configuración
config_path = Path('/app/app/core/config.py')
config_content = config_path.read_text()

# Reemplazar la línea de configuración
updated_content = re.sub(
    r'THUMBNAIL_STORAGE_STRATEGY: str = \".*?\"',
    f'THUMBNAIL_STORAGE_STRATEGY: str = \"{STRATEGY}\"',
    config_content
)

# Guardar el archivo actualizado
config_path.write_text(updated_content)

print('Configuración actualizada correctamente.')
"

# Reiniciar el contenedor para aplicar los cambios
echo "Reiniciando el contenedor para aplicar los cambios..."
docker restart clasificadorv2-backend-1

echo "Esperando a que el servidor esté listo..."
sleep 5

# Preguntar si se desea regenerar las miniaturas
read -p "¿Desea regenerar todas las miniaturas con la nueva estrategia? (s/N): " REGEN
if [[ "$REGEN" =~ ^[sS]$ ]]; then
    echo "Regenerando miniaturas..."
    
    # Ejecutar el script de regeneración de miniaturas
    bash regenerate_thumbnails.sh
else
    echo "Las miniaturas no se han regenerado."
    echo "Las nuevas miniaturas se crearán con la estrategia seleccionada."
fi

echo "Proceso completado."
echo "La estrategia de miniaturas se ha actualizado a: $STRATEGY"
