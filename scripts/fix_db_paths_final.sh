#!/bin/bash

echo "=== Script de Corrección Final de Rutas ==="

# Actualizar las rutas en la base de datos
docker exec clasificadorv2-backend-1 python -c "
import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('/app/storage/db.sqlite3')
cursor = conn.cursor()

# 1. Actualizar rutas absolutas a relativas
cursor.execute(\"\"\"
UPDATE media 
SET thumbnail_path = '/thumbnails/' || substr(thumbnail_path, instr(thumbnail_path, 'thumb_'))
WHERE thumbnail_path LIKE '/app/storage/thumbnails/thumb_%'
\"\"\")

# 2. Actualizar rutas incorrectas que apuntan a uploads
cursor.execute(\"\"\"
UPDATE media 
SET thumbnail_path = REPLACE(
    REPLACE(thumbnail_path, '/app/storage/uploads/', '/thumbnails/'),
    '.thumb.jpg', '_thumb.jpg'
)
WHERE thumbnail_path LIKE '/app/storage/uploads/%'
\"\"\")

conn.commit()

# Verificar los cambios
cursor.execute('SELECT id, filename, thumbnail_path FROM media')
print('Registros actualizados:')
for row in cursor.fetchall():
    print(f'ID: {row[0]}, filename: {row[1]}, path: {row[2]}')

conn.close()
"

echo
echo "=== Script Completado ==="
