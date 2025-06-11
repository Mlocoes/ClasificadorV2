#!/bin/bash

# Script para regenerar miniaturas en ClasificadorV2
# Compatible con entorno local y Docker

echo "=== Script de Regeneración de Miniaturas ==="
echo "Este script eliminará las miniaturas existentes y las regenerará"
echo

# Determinar el entorno (Docker o local)
if command -v docker &> /dev/null && docker ps | grep -q "clasificadorv2-backend"; then
    ENVIRONMENT="docker"
    echo "Detectado entorno Docker"
else
    ENVIRONMENT="local"
    echo "Detectado entorno local"
fi

# Confirmar antes de proceder
read -p "¿Está seguro de que desea eliminar todas las miniaturas existentes? (s/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[sS]$ ]]; then
    echo "Operación cancelada."
    exit 1
fi

# Función para ejecutar en Docker
run_in_docker() {
    echo "Eliminando miniaturas existentes en Docker..."
    docker exec clasificadorv2-backend-1 rm -rf /app/storage/thumbnails/*

    echo "Regenerando miniaturas en Docker..."
    docker exec clasificadorv2-backend-1 python3 -c '
import os
import sys
from pathlib import Path
from app.core.config import settings
from app.services.media_processor import MediaProcessor
from app.core.database import SessionLocal
from app.models.media import Media

def regenerate_thumbnails():
    print("Iniciando regeneración de miniaturas...")
    mp = MediaProcessor()
    db = SessionLocal()
    
    try:
        # Obtener todos los archivos de medios
        media_files = db.query(Media).all()
        print(f"Encontrados {len(media_files)} archivos de medios")
        
        count = 0
        for media in media_files:
            # Crear miniatura solo para archivos que existen
            file_path = os.path.join(settings.UPLOADS_DIR, media.filename)
            if os.path.exists(file_path):
                # Generar miniatura
                thumbnail = mp.create_thumbnail(file_path, media.mime_type)
                if thumbnail:
                    count += 1
                    print(f"Regenerada miniatura {count}/{len(media_files)}: {media.filename}")
                else:
                    print(f"Error al regenerar miniatura para: {media.filename}")
            else:
                print(f"Archivo no encontrado: {file_path}")
        
        print(f"Regeneración completada. {count} miniaturas regeneradas.")
    
    finally:
        db.close()

if __name__ == "__main__":
    regenerate_thumbnails()
'
}

# Función para ejecutar en entorno local
run_local() {
    SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    THUMBNAILS_DIR="$PROJECT_DIR/storage/thumbnails"
    
    echo "Eliminando miniaturas existentes en entorno local..."
    rm -rf "$THUMBNAILS_DIR"/*
    
    echo "Regenerando miniaturas en entorno local..."
    
    # Primero corregimos las rutas de configuración
    cd "$PROJECT_DIR"
    python scripts/fix_config_paths.py > /dev/null
    
    # Luego ejecutamos el script de regeneración
    python -c "
import os
import sys
from pathlib import Path

# Configurar rutas correctas
project_dir = Path('$PROJECT_DIR')
sys.path.append(str(project_dir / 'backend'))

# Cargar los módulos necesarios
try:
    from app.core.config import settings
    from app.services.media_processor import MediaProcessor
    from app.core.database import SessionLocal
    from app.models.media import Media
    
    def regenerate_thumbnails():
        print('Iniciando regeneración de miniaturas...')
        mp = MediaProcessor()
        db = SessionLocal()
        
        try:
            # Obtener todos los archivos de medios
            media_files = db.query(Media).all()
            print(f'Encontrados {len(media_files)} archivos de medios')
            
            count = 0
            for media in media_files:
                # Crear miniatura solo para archivos que existen
                file_path = os.path.join(settings.UPLOADS_DIR, media.filename)
                if os.path.exists(file_path):
                    # Generar miniatura
                    thumbnail = mp.create_thumbnail(file_path, media.mime_type)
                    if thumbnail:
                        count += 1
                        print(f'Regenerada miniatura {count}/{len(media_files)}: {media.filename}')
                    else:
                        print(f'Error al regenerar miniatura para: {media.filename}')
                else:
                    print(f'Archivo no encontrado: {file_path}')
            
            print(f'Regeneración completada. {count} miniaturas regeneradas.')
        
        finally:
            db.close()
    
    # Ejecutar la regeneración
    regenerate_thumbnails()
    
except ImportError as e:
    print(f'Error al importar módulos: {e}')
    print('Asegúrese de que todas las dependencias estén instaladas y que el entorno esté configurado correctamente.')
    sys.exit(1)
except Exception as e:
    print(f'Error durante la regeneración: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"
}

# Ejecutar según el entorno detectado
if [[ "$ENVIRONMENT" == "docker" ]]; then
    run_in_docker
else
    run_local
fi

echo "=== Proceso de regeneración finalizado ==="
