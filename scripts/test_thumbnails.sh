#!/bin/bash

echo "=== Prueba Completa del Sistema de Miniaturas ==="

# Limpiar archivos antiguos para una prueba limpia
echo "Limpiando archivos antiguos de test_real.jpg..."
docker exec clasificadorv2-backend-1 bash -c "
  rm -f /app/storage/uploads/test_real.jpg
  rm -f /app/storage/thumbnails/thumb_test_real.jpg
"

# Subir un archivo nuevo
echo "Subiendo archivo de prueba..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/media/upload/ -F "file=@test_real.jpg")
echo "Respuesta de la API:"
echo $RESPONSE | python -m json.tool

# Extraer información relevante
THUMBNAIL_PATH=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['thumbnail_path'])")
ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

echo "ID del archivo: $ID"
echo "Ruta de miniatura: $THUMBNAIL_PATH"

# Verificar si la ruta tiene el formato correcto
if [[ $THUMBNAIL_PATH == "/thumbnails/thumb_"* ]]; then
  echo -e "\n✅ CORRECTO: La ruta de la miniatura tiene el formato adecuado"
else
  echo -e "\n❌ ERROR: La ruta de la miniatura no tiene el formato adecuado"
fi

# Verificar si el archivo existe en el sistema
echo -e "\nVerificando archivos en el sistema..."
docker exec clasificadorv2-backend-1 bash -c "
  echo 'Archivos en /app/storage/thumbnails/:'
  ls -la /app/storage/thumbnails/
  
  if [ -f /app/storage/thumbnails/thumb_test_real.jpg ]; then
    echo -e '\n✅ CORRECTO: El archivo existe físicamente en el directorio de miniaturas'
  else
    echo -e '\n❌ ERROR: El archivo NO existe en el directorio de miniaturas'
  fi
  
  echo -e '\nVerificando permisos...'
  ls -la /app/storage/thumbnails/thumb_test_real.jpg
"

# Verificar si la miniatura se puede ver en el navegador
echo -e "\nVerificando accesibilidad web de la miniatura..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/thumbnails/thumb_test_real.jpg)
if [ "$HTTP_CODE" -eq 200 ]; then
  echo "✅ CORRECTO: La miniatura es accesible vía HTTP (código $HTTP_CODE)"
else
  echo "❌ ERROR: La miniatura NO es accesible vía HTTP (código $HTTP_CODE)"
fi

echo -e "\n=== Prueba Completada ==="
