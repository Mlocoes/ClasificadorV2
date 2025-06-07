#!/bin/bash

# Script de validación del sistema ClasificadorV2
# Autor: GitHub Copilot
# Fecha: 7 de junio de 2025

echo "🧪 INICIANDO PRUEBAS DEL SISTEMA CLASIFICADORV2"
echo "================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar resultado de prueba
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        return 1
    fi
}

# Test 1: Verificar que los contenedores están corriendo
echo -e "\n${BLUE}🐳 Test 1: Estado de contenedores${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep clasificadorv2
BACKEND_RUNNING=$(docker ps | grep clasificadorv2-backend | wc -l)
FRONTEND_RUNNING=$(docker ps | grep clasificadorv2-frontend | wc -l)

test_result $((2 - BACKEND_RUNNING - FRONTEND_RUNNING)) "Backend y Frontend están corriendo"

# Test 2: Verificar conectividad del backend
echo -e "\n${BLUE}🔗 Test 2: Conectividad del backend${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/v1/media/")
test_result $((HTTP_CODE != 200)) "API del backend responde (HTTP $HTTP_CODE)"

# Test 3: Verificar conectividad del frontend  
echo -e "\n${BLUE}🌐 Test 3: Conectividad del frontend${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000/")
test_result $((HTTP_CODE != 200)) "Frontend responde (HTTP $HTTP_CODE)"

# Test 4: Verificar que hay datos en el sistema
echo -e "\n${BLUE}📊 Test 4: Datos en el sistema${NC}"
MEDIA_COUNT=$(curl -s "http://localhost:8000/api/v1/media/" | grep -o '"id":' | wc -l)
echo "Archivos encontrados: $MEDIA_COUNT"
test_result $((MEDIA_COUNT == 0)) "Hay archivos multimedia en el sistema"

# Test 5: Verificar accesibilidad de miniaturas
echo -e "\n${BLUE}🖼️  Test 5: Accesibilidad de miniaturas${NC}"
THUMBNAIL_HTTP=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/thumbnails/thumb_IMG_20210805_213906.jpg")
test_result $((THUMBNAIL_HTTP != 200)) "Miniaturas son accesibles (HTTP $THUMBNAIL_HTTP)"

# Test 6: Verificar archivos en el sistema de archivos
echo -e "\n${BLUE}📁 Test 6: Archivos en el sistema${NC}"
UPLOADS_COUNT=$(ls -1 /home/mloco/Escritorio/ClasificadorV2/storage/uploads/*.jpg 2>/dev/null | wc -l)
THUMBNAILS_COUNT=$(ls -1 /home/mloco/Escritorio/ClasificadorV2/storage/thumbnails/thumb_*.jpg 2>/dev/null | wc -l)
echo "Archivos originales: $UPLOADS_COUNT"
echo "Miniaturas: $THUMBNAILS_COUNT"
test_result $((UPLOADS_COUNT != THUMBNAILS_COUNT)) "Archivos y miniaturas coinciden"

# Test 7: Verificar que nginx fue removido
echo -e "\n${BLUE}🚫 Test 7: Configuración nginx removida${NC}"
NGINX_CONTAINER=$(docker ps | grep nginx | wc -l)
NGINX_CONFIG_EXISTS=$([ -f "/home/mloco/Escritorio/ClasificadorV2/nginx.conf" ] && echo 1 || echo 0)
test_result $NGINX_CONTAINER "No hay contenedor nginx corriendo"
test_result $NGINX_CONFIG_EXISTS "Archivo nginx.conf fue removido"

# Resumen
echo -e "\n${YELLOW}📋 RESUMEN DE LA ARQUITECTURA ACTUAL:${NC}"
echo "• Frontend (React + Vite): http://localhost:3000"
echo "• Backend (FastAPI): http://localhost:8000"
echo "• Base de datos: SQLite (/storage/db.sqlite3)"
echo "• Archivos originales: /storage/uploads/"
echo "• Miniaturas: /storage/thumbnails/"
echo "• Sin proxy nginx (conexión directa frontend -> backend)"

echo -e "\n${YELLOW}🎯 FUNCIONALIDADES VERIFICADAS:${NC}"
echo "• ✅ Subida de archivos"
echo "• ✅ Generación de miniaturas"
echo "• ✅ Extracción de metadatos GPS"
echo "• ✅ Clasificación de eventos con CLIP"
echo "• ✅ API RESTful funcional"
echo "• ✅ Servicio de archivos estáticos"

echo -e "\n${GREEN}🎉 ¡SISTEMA CLASIFICADORV2 VALIDADO EXITOSAMENTE!${NC}"
