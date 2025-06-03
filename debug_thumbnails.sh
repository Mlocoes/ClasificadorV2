#!/bin/bash

echo "=== Script de Depuración Profunda ==="

# Entrar al contenedor y ejecutar un comando para depurar
docker exec -it clasificadorv2-backend-1 python -c "
import os
import sys
from pathlib import Path
from app.core.config import settings
from app.models.media import Media
from app.core.database import SessionLocal
from app.services.media_processor import MediaProcessor

# Verificar configuración
print('===== CONFIGURACIÓN =====')
print(f'STORAGE_DIR: {settings.STORAGE_DIR}')
print(f'UPLOADS_DIR: {settings.UPLOADS_DIR}')
print(f'THUMBNAILS_DIR: {settings.THUMBNAILS_DIR}')

# Verificar directorios
print('\n===== DIRECTORIOS =====')
print(f'UPLOADS_DIR existe: {settings.UPLOADS_DIR.exists()}')
print(f'THUMBNAILS_DIR existe: {settings.THUMBNAILS_DIR.exists()}')

# Listar contenido
print('\n===== CONTENIDO DE DIRECTORIOS =====')
print('Contenido de UPLOADS_DIR:')
for item in settings.UPLOADS_DIR.iterdir():
    print(f'  {item.name}')

print('\nContenido de THUMBNAILS_DIR:')
try:
    for item in settings.THUMBNAILS_DIR.iterdir():
        print(f'  {item.name}')
except Exception as e:
    print(f'  Error al listar: {e}')

# Verificar base de datos
print('\n===== BASE DE DATOS =====')
db = SessionLocal()
media_records = db.query(Media).all()
print(f'Total de registros: {len(media_records)}')
for media in media_records:
    print(f'ID: {media.id}, filename: {media.filename}')
    print(f'  file_path: {media.file_path}')
    print(f'  thumbnail_path: {media.thumbnail_path}')

# Probar crear una miniatura
print('\n===== PRUEBA DE CREACIÓN DE MINIATURA =====')
test_file = None
for item in settings.UPLOADS_DIR.iterdir():
    if item.is_file() and item.suffix.lower() in ['.jpg', '.jpeg', '.png']:
        test_file = item
        break

if test_file:
    print(f'Archivo de prueba: {test_file}')
    mp = MediaProcessor()
    thumb_path = mp.create_thumbnail(str(test_file), 'image/jpeg')
    print(f'Resultado: {thumb_path}')
    
    # Verificar si el archivo de miniatura existe físicamente
    if isinstance(thumb_path, str) and thumb_path.startswith('/thumbnails/'):
        physical_path = settings.THUMBNAILS_DIR / Path(thumb_path).name
        print(f'Verificando existencia física en: {physical_path}')
        print(f'Existe: {physical_path.exists()}')
    else:
        print(f'La ruta devuelta no tiene el formato esperado: {thumb_path}')
else:
    print('No se encontró un archivo de imagen para probar')

# Forzar la creación de una miniatura correcta
print('\n===== FORZANDO CREACIÓN DE MINIATURA =====')
if test_file:
    try:
        # Asegurar que el directorio existe
        settings.THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Crear miniatura directamente
        from PIL import Image
        thumb_name = f'thumb_{test_file.stem}.jpg'
        thumb_path = settings.THUMBNAILS_DIR / thumb_name
        
        with Image.open(test_file) as img:
            img.thumbnail(settings.THUMBNAIL_SIZE)
            print(f'Guardando miniatura en: {thumb_path}')
            img.save(str(thumb_path), 'JPEG', quality=85)
        
        if thumb_path.exists():
            print(f'ÉXITO: Miniatura creada en {thumb_path}')
            os.chmod(str(thumb_path), 0o777)
        else:
            print(f'FALLO: No se pudo crear la miniatura en {thumb_path}')
    except Exception as e:
        print(f'Error al crear miniatura: {e}')
"

echo
echo "=== Script de Depuración Completado ==="
