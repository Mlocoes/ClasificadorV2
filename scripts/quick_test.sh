#!/bin/bash

echo "=== PRUEBA RÁPIDA DEL SISTEMA ==="
echo ""

# Verificar si los puertos están ocupados
echo "Verificando puertos:"
netstat -tuln 2>/dev/null | grep -E ":(3000|8000)" || echo "Puertos no ocupados, iniciando servicios..."

# Cambiar al directorio del proyecto
cd /home/mloco/Escritorio/ClasificadorV2

# Iniciar servicios si no están corriendo
echo "Iniciando servicios..."
docker-compose up -d

# Esperar un poco para que los servicios se inicien
echo "Esperando que los servicios se inicien..."
sleep 10

# Verificar estado
echo ""
echo "Estado de los servicios:"
docker-compose ps

# Probar conectividad
echo ""
echo "Probando conectividad:"
echo "Frontend (puerto 3000):"
curl -s -o /dev/null -w "HTTP Code: %{http_code}\n" http://localhost:3000 || echo "Error al conectar"

echo "Backend (puerto 8000):"
curl -s -o /dev/null -w "HTTP Code: %{http_code}\n" http://localhost:8000 || echo "Error al conectar"

# Probar API
echo ""
echo "Probando API de media:"
curl -s http://localhost:8000/api/media | head -c 200
echo ""

# Verificar thumbnails
echo ""
echo "Verificando storage de thumbnails:"
ls -la /home/mloco/Escritorio/ClasificadorV2/storage/thumbnails/ | head -5

# Probar una thumbnail específica si existe
first_thumb=$(ls /home/mloco/Escritorio/ClasificadorV2/storage/thumbnails/ 2>/dev/null | grep "thumb_" | head -1)
if [ ! -z "$first_thumb" ]; then
    echo ""
    echo "Probando acceso a thumbnail: $first_thumb"
    curl -s -I "http://localhost:8000/thumbnails/$first_thumb" | head -3
else
    echo "No se encontraron thumbnails para probar"
fi

echo ""
echo "=== FIN DE LA PRUEBA ==="
