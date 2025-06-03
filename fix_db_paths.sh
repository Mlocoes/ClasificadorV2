#!/bin/bash

echo "=== Script para corregir rutas de miniaturas ==="

# Entrar al contenedor y ejecutar un comando SQL para actualizar las rutas
docker exec -it clasificadorv2-backend-1 python -c "
import sqlite3
import os
from pathlib import Path
from app.core.config import settings

# Conectar a la base de datos
conn = sqlite3.connect('/app/storage/db.sqlite3')
cursor = conn.cursor()

# Verificar estructura de la tabla media
cursor.execute('PRAGMA table_info(media)')
columns = cursor.fetchall()
print('Estructura de la tabla media:')
for col in columns:
    print(col)

# Seleccionar todos los registros
cursor.execute('SELECT id, file_path, thumbnail_path FROM media')
rows = cursor.fetchall()
print('\nRegistros actuales:')
for row in rows:
    print(f'ID: {row[0]}, file_path: {row[1]}, thumbnail_path: {row[2]}')

# Actualizar las rutas incorrectas
cursor.execute('UPDATE media SET thumbnail_path = REPLACE(thumbnail_path, \"/app/storage/uploads/\", \"/thumbnails/\")')
cursor.execute('UPDATE media SET thumbnail_path = REPLACE(thumbnail_path, \".thumb.jpg\", \"_thumb.jpg\")')
conn.commit()

# Verificar corrección
cursor.execute('SELECT id, file_path, thumbnail_path FROM media')
rows = cursor.fetchall()
print('\nRegistros actualizados:')
for row in rows:
    print(f'ID: {row[0]}, file_path: {row[1]}, thumbnail_path: {row[2]}')

# Cerrar conexión
conn.close()
"

echo "Verificando archivos físicos en el directorio de miniaturas..."
docker exec clasificadorv2-backend-1 ls -la /app/storage/thumbnails/

echo "Verificando archivos físicos en el directorio de uploads..."
docker exec clasificadorv2-backend-1 ls -la /app/storage/uploads/

echo
echo "=== Script completado ==="
