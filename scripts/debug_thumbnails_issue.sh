#!/bin/bash

echo "=== DIAGNÓSTICO DEL PROBLEMA DE MINIATURAS ==="
echo ""

# Verificar que el sistema esté ejecutándose
echo "1. Verificando estado de contenedores:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Si no están ejecutándose, intentar iniciarlos
if [ "$(docker ps -q)" = "" ]; then
    echo "Los contenedores no están ejecutándose. Iniciando..."
    docker-compose up -d
    echo "Esperando 10 segundos para que los servicios se inicien..."
    sleep 10
fi

echo "2. Verificando estructura de directorios de miniaturas:"
echo "Directorio físico de miniaturas en el contenedor:"
docker exec backend ls -la /app/storage/thumbnails/ 2>/dev/null || echo "Error: No se puede acceder al directorio de miniaturas"
echo ""

echo "3. Verificando rutas en la base de datos:"
docker exec backend python3 -c "
import sqlite3
conn = sqlite3.connect('/app/storage/db.sqlite3')
cursor = conn.cursor()
cursor.execute('SELECT id, filename, file_path, thumbnail_path FROM media LIMIT 5')
rows = cursor.fetchall()
print('Muestra de registros en la base de datos:')
print('ID | Filename | File Path | Thumbnail Path')
print('-' * 60)
for row in rows:
    print(f'{row[0]} | {row[1]} | {row[2]} | {row[3]}')
conn.close()
" 2>/dev/null || echo "Error: No se puede acceder a la base de datos"
echo ""

echo "4. Verificando endpoints del backend:"
echo "Probando acceso directo a una miniatura:"
# Intentar obtener la primera miniatura disponible
THUMBNAIL_PATH=$(docker exec backend python3 -c "
import sqlite3
conn = sqlite3.connect('/app/storage/db.sqlite3')
cursor = conn.cursor()
cursor.execute('SELECT thumbnail_path FROM media WHERE thumbnail_path IS NOT NULL LIMIT 1')
row = cursor.fetchone()
if row:
    print(row[0])
conn.close()
" 2>/dev/null)

if [ ! -z "$THUMBNAIL_PATH" ]; then
    echo "Ruta de miniatura encontrada: $THUMBNAIL_PATH"
    echo "Probando acceso HTTP:"
    curl -s -I "http://localhost:8000$THUMBNAIL_PATH" | head -n 1
else
    echo "No se encontraron miniaturas en la base de datos"
fi
echo ""

echo "5. Verificando configuración del frontend:"
echo "URL configurada en MediaGrid.tsx:"
grep -n "localhost:8000" /home/mloco/Escritorio/ClasificadorV2/frontend/src/components/MediaGrid.tsx 2>/dev/null || echo "No se encontró la configuración de URL"
echo ""

echo "6. Probando crear una miniatura de prueba:"
docker exec backend python3 -c "
import os
from pathlib import Path
from PIL import Image

# Crear directorio si no existe
os.makedirs('/app/storage/thumbnails', exist_ok=True)
os.chmod('/app/storage/thumbnails', 0o777)

# Crear imagen de prueba
img = Image.new('RGB', (200, 200), color='red')
test_path = '/app/storage/thumbnails/test_thumb.jpg'
img.save(test_path, 'JPEG')
os.chmod(test_path, 0o777)

print(f'Miniatura de prueba creada en: {test_path}')
print(f'Existe: {os.path.exists(test_path)}')
print(f'Permisos: {oct(os.stat(test_path).st_mode)[-3:]}')
" 2>/dev/null || echo "Error: No se pudo crear miniatura de prueba"

echo ""
echo "7. Probando acceso HTTP a la miniatura de prueba:"
curl -s -I "http://localhost:8000/thumbnails/test_thumb.jpg" | head -n 1

echo ""
echo "=== FIN DEL DIAGNÓSTICO ==="
