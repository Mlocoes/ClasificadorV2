#!/bin/bash

echo "=== Script de Corrección de Miniaturas ==="
echo "Este script moverá las miniaturas del directorio uploads/ al directorio thumbnails/ con el nombre correcto"
echo

# Confirmar antes de proceder
read -p "¿Está seguro de que desea mover las miniaturas? (s/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[sS]$ ]]; then
    echo "Operación cancelada."
    exit 1
fi

echo "Moviendo miniaturas..."
# Buscar archivos *.thumb.jpg en uploads y moverlos a thumbnails con el nombre correcto
find storage/uploads/ -name "*.thumb.jpg" | while read file; do
    filename=$(basename "$file")
    basefile=${filename%.thumb.jpg}
    newname="thumb_${basefile}.jpg"
    echo "Moviendo $file a storage/thumbnails/$newname"
    mv "$file" "storage/thumbnails/$newname"
done

# Actualizar permisos
echo "Actualizando permisos..."
chmod -R 777 storage/thumbnails/

echo
echo "=== Verificando resultado ==="
ls -la storage/thumbnails/

echo 
echo "Proceso completado."

# Actualizar base de datos
echo "¿Desea actualizar la base de datos para corregir las rutas de las miniaturas? (s/N): "
read UPDATE_DB
if [[ "$UPDATE_DB" =~ ^[sS]$ ]]; then
    echo "Ejecutando actualización de base de datos..."
    docker exec clasificadorv2-backend-1 python3 -c '
import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect("/app/storage/db.sqlite3")
cursor = conn.cursor()

# Actualizar las rutas de las miniaturas
cursor.execute("UPDATE media SET thumbnail_path = REPLACE(thumbnail_path, ''/app/storage/uploads/'', ''/thumbnails/'')")
cursor.execute("UPDATE media SET thumbnail_path = REPLACE(thumbnail_path, ''.thumb.jpg'', ''_thumb.jpg'')")
conn.commit()

# Verificar los cambios
cursor.execute("SELECT id, file_path, thumbnail_path FROM media")
print("ID\tFile Path\t\tThumbnail Path")
for row in cursor.fetchall():
    print(f"{row[0]}\t{row[1]}\t{row[2]}")

conn.close()
print("Base de datos actualizada correctamente.")
'
fi

echo "Todo el proceso ha finalizado."
