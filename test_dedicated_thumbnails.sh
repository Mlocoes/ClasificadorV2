#!/bin/bash

echo "=== Script para verificar el almacenamiento de miniaturas ==="

# Reiniciar el contenedor para aplicar cambios
echo "Reiniciando contenedor para aplicar cambios..."
docker-compose -f /home/mloco/Escritorio/ClasificadorV2/docker-compose.yml restart backend

# Esperar a que el servidor esté listo
echo "Esperando a que el servidor se inicie..."
sleep 5

# Verificar configuración actual
echo "Verificando configuración actual..."
docker exec clasificadorv2-backend-1 python -c "
from app.core.config import settings

print(f'Directorio de miniaturas: {settings.THUMBNAILS_DIR}')
print(f'Estrategia configurada: {settings.THUMBNAIL_STORAGE_STRATEGY}')
"

# Verificar directorios existentes
echo
echo "Verificando directorios..."
docker exec clasificadorv2-backend-1 bash -c "
echo 'Directorio de uploads:'
ls -la /app/storage/uploads/
echo
echo 'Directorio de miniaturas:'
ls -la /app/storage/thumbnails/
"

# Preguntar si se desea limpiar el directorio de miniaturas
echo
echo "¿Desea limpiar el directorio de miniaturas para realizar una prueba completa? (s/N): "
read CLEAN
if [[ "$CLEAN" =~ ^[sS]$ ]]; then
    echo "Limpiando directorio de miniaturas..."
    docker exec clasificadorv2-backend-1 bash -c "rm -rf /app/storage/thumbnails/*"
    echo "Directorio limpiado."
fi

# Subir un archivo de prueba
echo
echo "Realizando prueba de carga de archivo..."
curl -s -X POST http://localhost:8000/api/v1/media/upload/ -F "file=@/home/mloco/Escritorio/ClasificadorV2/test_real.jpg" > /tmp/thumbnail_test_response.json

# Analizar respuesta
echo "Respuesta de la API:"
cat /tmp/thumbnail_test_response.json | grep -o '"thumbnail_path":"[^"]*"'

# Verificar directorios después de la prueba
echo
echo "Verificando directorios después de la prueba..."
docker exec clasificadorv2-backend-1 bash -c "
echo 'Directorio de miniaturas:'
ls -la /app/storage/thumbnails/
"

echo
echo "=== Verificación completada ==="
