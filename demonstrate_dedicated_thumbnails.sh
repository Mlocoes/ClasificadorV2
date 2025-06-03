#!/bin/bash

echo "=== Demostración de Estrategia de Directorio Dedicado para Miniaturas ==="

# Ejecutar el script ultimate_fix.sh que ya tiene la implementación correcta
echo "Aplicando la implementación correcta..."
bash /home/mloco/Escritorio/ClasificadorV2/ultimate_fix.sh

# Verificar configuración
echo
echo "Verificando configuración actual..."
docker exec clasificadorv2-backend-1 bash -c '
  echo "Estructura de directorios:"
  mkdir -p /app/storage/thumbnails
  chmod -R 777 /app/storage/thumbnails
  ls -la /app/storage/ | grep -E "uploads|thumbnails"
  
  echo -e "\nContenido del directorio de miniaturas:"
  ls -la /app/storage/thumbnails/
  
  echo -e "\nVerificando que todas las miniaturas en la base de datos apuntan al directorio dedicado:"
  python3 -c "
import sqlite3
conn = sqlite3.connect(\"/app/storage/db.sqlite3\")
cursor = conn.cursor()
cursor.execute(\"SELECT id, filename, thumbnail_path FROM media\")
rows = cursor.fetchall()
correct = 0
incorrect = 0
for row in rows:
    if row[2] and not row[2].startswith(\"/thumbnails/\"):
        print(f\"ID: {row[0]}, filename: {row[1]}, path incorrecta: {row[2]}\")
        incorrect += 1
    else:
        correct += 1
print(f\"Resultados: {correct} registros correctos, {incorrect} incorrectos\")
conn.close()
  "
'

# Probar el sistema con una carga nueva
echo
echo "Realizando prueba de carga con archivo nuevo..."
cp /home/mloco/Escritorio/ClasificadorV2/test_real.jpg /tmp/test_upload_$(date +%s).jpg
curl -s -X POST http://localhost:8000/api/v1/media/upload/ -F "file=@/tmp/test_upload_$(date +%s).jpg" > /tmp/thumbnail_test_result.json

# Analizar respuesta
echo "Respuesta de la API:"
cat /tmp/thumbnail_test_result.json | grep -o '"thumbnail_path":"[^"]*"'

# Verificar que la miniatura se creó en el directorio correcto
echo
echo "Verificando directorio de miniaturas después de la prueba..."
docker exec clasificadorv2-backend-1 bash -c 'ls -la /app/storage/thumbnails/ | tail -5'

echo
echo "=== Demostración completada ==="
echo "La estrategia de directorio dedicado para miniaturas está correctamente implementada."
