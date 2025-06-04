#!/bin/bash

echo "=== Script de Verificación de Miniaturas ==="
echo "Este script verificará y corregirá el almacenamiento y las rutas de las miniaturas"
echo

# Asegurar permisos correctos
echo "Asegurando permisos correctos en directorios..."
chmod -R 777 storage/thumbnails/
chmod -R 777 storage/uploads/

# Buscar miniaturas en uploads
echo "Buscando miniaturas mal ubicadas en uploads..."
THUMBS_IN_UPLOADS=$(find storage/uploads/ -name "thumb_*.jpg" | wc -l)

if [ "$THUMBS_IN_UPLOADS" -gt 0 ]; then
    echo "¡Se encontraron $THUMBS_IN_UPLOADS miniaturas en el directorio incorrecto!"
    echo "Moviendo miniaturas a la ubicación correcta..."
    
    find storage/uploads/ -name "thumb_*.jpg" | while read file; do
        filename=$(basename "$file")
        echo "Moviendo $file a storage/thumbnails/$filename"
        mv "$file" "storage/thumbnails/$filename"
    done
else
    echo "No se encontraron miniaturas en la ubicación incorrecta. ¡Bien!"
fi

# Verificar base de datos
echo "¿Desea verificar y corregir las rutas en la base de datos? (s/N): "
read VERIFY_DB
if [[ "$VERIFY_DB" =~ ^[sS]$ ]]; then
    echo "Ejecutando verificación de base de datos..."
    docker exec clasificadorv2-backend-1 python3 -c '
import sqlite3
import os

# Conectar a la base de datos
conn = sqlite3.connect("/app/storage/db.sqlite3")
cursor = conn.cursor()

# Contar registros con rutas incorrectas
cursor.execute("SELECT COUNT(*) FROM media WHERE thumbnail_path NOT LIKE \"/thumbnails/%\"")
incorrect_count = cursor.fetchone()[0]

if incorrect_count > 0:
    print(f"Se encontraron {incorrect_count} registros con rutas de miniaturas incorrectas.")
    
    # Corregir rutas absolutas
    cursor.execute("UPDATE media SET thumbnail_path = REPLACE(thumbnail_path, \"/app/storage/thumbnails/\", \"/thumbnails/\") WHERE thumbnail_path LIKE \"/app/storage/thumbnails/%\"")
    
    # Corregir rutas en uploads
    cursor.execute("UPDATE media SET thumbnail_path = REPLACE(thumbnail_path, \"/app/storage/uploads/thumb_\", \"/thumbnails/thumb_\") WHERE thumbnail_path LIKE \"/app/storage/uploads/thumb_%\"")
    cursor.execute("UPDATE media SET thumbnail_path = REPLACE(thumbnail_path, \"/uploads/thumb_\", \"/thumbnails/thumb_\") WHERE thumbnail_path LIKE \"/uploads/thumb_%\"")
    
    conn.commit()
    print("Rutas corregidas en la base de datos.")
else:
    print("Todas las rutas en la base de datos son correctas.")

# Verificar los cambios
cursor.execute("SELECT id, file_path, thumbnail_path FROM media LIMIT 10")
print("\nMuestreo de 10 registros:")
print("ID\tFile Path\t\tThumbnail Path")
for row in cursor.fetchall():
    print(f"{row[0]}\t{row[1]}\t{row[2]}")

conn.close()
'
fi

echo
echo "=== Verificando estructura final ==="
ls -la storage/thumbnails/ | head -n 10
echo "... (mostrando primeros 10 elementos)"

echo 
echo "Proceso de verificación completado."
