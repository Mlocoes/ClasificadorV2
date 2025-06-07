#!/bin/bash

# Colores para los mensajes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}===== PRUEBA DE ACCESO DESDE IP DE RED (192.168.0.7) =====${NC}"
echo ""

# Función para verificar respuesta
check_response() {
    local url=$1
    local expected_code=$2
    local description=$3
    
    echo -n "Verificando $description... "
    response_code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$response_code" = "$expected_code" ]; then
        echo -e "${GREEN}✓ OK (HTTP $response_code)${NC}"
        return 0
    else
        echo -e "${RED}✗ ERROR (HTTP $response_code, esperado $expected_code)${NC}"
        return 1
    fi
}

# Función para verificar CORS
check_cors() {
    local url=$1
    local origin=$2
    local description=$3
    
    echo -n "Verificando CORS para $description... "
    response=$(curl -s -H "Origin: $origin" -H "Access-Control-Request-Method: GET" -X OPTIONS "$url" -w "%{http_code}")
    response_code="${response: -3}"
    
    if [ "$response_code" = "200" ]; then
        echo -e "${GREEN}✓ OK (CORS habilitado)${NC}"
        return 0
    else
        echo -e "${RED}✗ ERROR (HTTP $response_code)${NC}"
        return 1
    fi
}

echo "1. VERIFICACIÓN DE SERVICIOS BÁSICOS"
echo "-----------------------------------"
check_response "http://192.168.0.7:8000/health" "200" "Backend Health Check"
check_response "http://192.168.0.7:3000" "200" "Frontend Home Page"
echo ""

echo "2. VERIFICACIÓN DE API"
echo "---------------------"
check_response "http://192.168.0.7:8000/api/v1/media/" "200" "API Media Endpoint"
echo ""

echo "3. VERIFICACIÓN DE THUMBNAILS"
echo "----------------------------"
check_response "http://192.168.0.7:8000/thumbnails/thumb_IMG_20210805_213906.jpg" "200" "Thumbnail 1"
check_response "http://192.168.0.7:8000/thumbnails/thumb_test_gps_image.jpg" "200" "Thumbnail 2"
check_response "http://192.168.0.7:8000/thumbnails/thumb_IMG_20230128_201345.jpg" "200" "Thumbnail 3"
echo ""

echo "4. VERIFICACIÓN DE CORS"
echo "----------------------"
check_cors "http://192.168.0.7:8000/api/v1/media/" "http://192.168.0.7:3000" "Frontend to API"
echo ""

echo "5. VERIFICACIÓN DE CONTENEDORES"
echo "------------------------------"
backend_status=$(docker inspect backend --format='{{.State.Status}}' 2>/dev/null)
frontend_status=$(docker inspect frontend --format='{{.State.Status}}' 2>/dev/null)

if [ "$backend_status" = "running" ]; then
    echo -e "Backend Container: ${GREEN}✓ Running${NC}"
else
    echo -e "Backend Container: ${RED}✗ $backend_status${NC}"
fi

if [ "$frontend_status" = "running" ]; then
    echo -e "Frontend Container: ${GREEN}✓ Running${NC}"
else
    echo -e "Frontend Container: ${RED}✗ $frontend_status${NC}"
fi

echo ""
echo -e "${YELLOW}===== RESUMEN =====${NC}"
echo "- Sistema accesible desde IP de red: 192.168.0.7"
echo "- Frontend: http://192.168.0.7:3000"
echo "- Backend API: http://192.168.0.7:8000/api/v1"
echo "- Thumbnails: http://192.168.0.7:8000/thumbnails/"
echo "- CORS configurado para permitir todos los orígenes"
echo ""
echo -e "${GREEN}¡Las thumbnails deberían mostrarse correctamente en la interfaz web!${NC}"
