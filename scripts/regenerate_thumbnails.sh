#!/bin/bash

echo "=== Script de Regeneración de Miniaturas ==="
echo "Este script eliminará las miniaturas existentes y las regenerará"
echo

# Confirmar antes de proceder
read -p "¿Está seguro de que desea eliminar todas las miniaturas existentes? (s/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[sS]$ ]]; then
    echo "Operación cancelada."
    exit 1
fi

echo "Eliminando miniaturas existentes..."
docker exec clasificadorv2-backend-1 rm -rf /app/storage/thumbnails/*

echo "Regenerando miniaturas..."
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
        # Asegurar que el directorio existe
        settings.THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
        os.chmod(str(settings.THUMBNAILS_DIR), 0o777)
        
        # Obtener todos los archivos de la base de datos
        media_files = db.query(Media).all()
        total = len(media_files)
        print(f"Se encontraron {total} archivos para procesar")
        
        success = 0
        failed = 0
        
        for media in media_files:
            file_path = str(settings.UPLOADS_DIR / Path(media.file_path).name)
            if not os.path.exists(file_path):
                print(f"❌ Archivo no encontrado: {file_path}")
                failed += 1
                continue
                
            print(f"Procesando: {media.filename}")
            thumbnail_path = mp.create_thumbnail(file_path, media.mime_type)
            
            if thumbnail_path:
                # Actualizar ruta en la base de datos
                media.thumbnail_path = thumbnail_path
                db.commit()
                print(f"✅ Miniatura creada correctamente")
                success += 1
            else:
                print(f"❌ Error al crear miniatura")
                failed += 1
        
        print(f"\nResumen de regeneración:")
        print(f"- Total procesados: {total}")
        print(f"- Exitosos: {success}")
        print(f"- Fallidos: {failed}")
        
        # Verificar permisos finales
        print("\nVerificando permisos de archivos...")
        os.system(f"chmod -R 777 {settings.THUMBNAILS_DIR}")
        print("Permisos actualizados para garantizar acceso")
        
    except Exception as e:
        print(f"Error durante la regeneración: {e}")
    finally:
        db.close()

regenerate_thumbnails()
'

echo
echo "=== Verificando resultado ==="
docker exec clasificadorv2-backend-1 ls -la /app/storage/thumbnails/

echo 
echo "Proceso completado. Si continúan los problemas, verifique los logs del contenedor."
