#!/bin/bash

echo "=== REINICIO COMPLETO DEL SISTEMA ==="
echo ""

cd /home/mloco/Escritorio/ClasificadorV2

echo "1. Deteniendo servicios actuales..."
docker-compose down

echo ""
echo "2. Limpiando containers e imágenes (opcional)..."
docker system prune -f

echo ""
echo "3. Reconstruyendo imágenes..."
docker-compose build --no-cache

echo ""
echo "4. Iniciando servicios con nueva configuración..."
docker-compose up -d

echo ""
echo "5. Esperando que los servicios se inicien..."
sleep 15

echo ""
echo "6. Verificando estado de los servicios..."
docker-compose ps

echo ""
echo "7. Verificando logs del frontend (últimas 10 líneas)..."
docker-compose logs --tail=10 frontend

echo ""
echo "8. Verificando logs del backend (últimas 10 líneas)..."
docker-compose logs --tail=10 backend

echo ""
echo "9. Probando conectividad..."
echo "Frontend:"
curl -s -o /dev/null -w "HTTP Code: %{http_code}\n" http://localhost:3000 || echo "Error"

echo "Backend:"
curl -s -o /dev/null -w "HTTP Code: %{http_code}\n" http://localhost:8000 || echo "Error"

echo ""
echo "10. Probando API de media..."
curl -s http://localhost:8000/api/media | head -c 100
echo ""

echo ""
echo "=== SISTEMA REINICIADO ==="
echo "Accede a: http://localhost:3000"
echo "API disponible en: http://localhost:8000"
echo ""
echo "Si las miniaturas aún no aparecen:"
echo "1. Abre las herramientas de desarrollador del navegador (F12)"
echo "2. Ve a la pestaña Network"
echo "3. Recarga la página"
echo "4. Verifica si hay errores 404 para las imágenes thumbnail"
echo "5. Revisa la consola para errores JavaScript"
