#!/bin/bash

echo "=== DIAGNÓSTICO COMPLETO DEL PROBLEMA DE MINIATURAS ==="
echo "Fecha: $(date)"
echo ""

# Función para mostrar separadores
separator() {
    echo "=============================================="
}

# 1. Verificar si los containers están corriendo
separator
echo "1. ESTADO DE CONTAINERS"
echo "Frontend container:"
docker ps | grep clasificadorv2-frontend || echo "❌ Frontend container no está corriendo"
echo "Backend container:"
docker ps | grep clasificadorv2-backend || echo "❌ Backend container no está corriendo"
echo ""

# 2. Verificar puertos y conectividad
separator
echo "2. CONECTIVIDAD"
echo "Verificando puerto 3000 (frontend):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "❌ Puerto 3000 no responde"
echo "Verificando puerto 8000 (backend):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 2>/dev/null || echo "❌ Puerto 8000 no responde"
echo ""

# 3. Verificar API endpoint de media
separator
echo "3. API ENDPOINT DE MEDIA"
echo "Probando GET /api/media:"
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://localhost:8000/api/media 2>/dev/null)
echo "$response"
echo ""

# 4. Verificar thumbnails específicas
separator
echo "4. VERIFICACIÓN DE THUMBNAILS"
echo "Listando primeros 5 thumbnails en storage:"
ls -la /home/mloco/Escritorio/ClasificadorV2/storage/thumbnails/ | head -6
echo ""

# 5. Probar acceso directo a thumbnails
separator
echo "5. ACCESO DIRECTO A THUMBNAILS"
first_thumb=$(ls /home/mloco/Escritorio/ClasificadorV2/storage/thumbnails/ | grep "thumb_" | head -1)
if [ ! -z "$first_thumb" ]; then
    echo "Probando acceso directo a thumbnail: $first_thumb"
    thumb_response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "http://localhost:8000/thumbnails/$first_thumb" 2>/dev/null)
    echo "Response length: $(echo "$thumb_response" | head -n -1 | wc -c) bytes"
    echo "HTTP Code: $(echo "$thumb_response" | tail -1)"
else
    echo "❌ No se encontraron thumbnails"
fi
echo ""

# 6. Verificar logs del frontend
separator
echo "6. LOGS DEL FRONTEND (últimas 20 líneas)"
docker logs clasificadorv2-frontend --tail=20 2>/dev/null || echo "❌ No se pueden obtener logs del frontend"
echo ""

# 7. Verificar logs del backend
separator
echo "7. LOGS DEL BACKEND (últimas 20 líneas)"
docker logs clasificadorv2-backend --tail=20 2>/dev/null || echo "❌ No se pueden obtener logs del backend"
echo ""

# 8. Verificar archivos de código actualizados
separator
echo "8. VERIFICACIÓN DE CÓDIGO ACTUALIZADO"
echo "Verificando getMediaUrl en mediaService.ts:"
grep -n "getMediaUrl" /home/mloco/Escritorio/ClasificadorV2/frontend/src/services/mediaService.ts 2>/dev/null || echo "❌ No se encuentra getMediaUrl"
echo ""
echo "Verificando import en MediaGrid.tsx:"
grep -n "import.*getMediaUrl" /home/mloco/Escritorio/ClasificadorV2/frontend/src/components/MediaGrid.tsx 2>/dev/null || echo "❌ No se encuentra import"
echo ""
echo "Verificando uso en MediaGrid.tsx:"
grep -n "getMediaUrl" /home/mloco/Escritorio/ClasificadorV2/frontend/src/components/MediaGrid.tsx 2>/dev/null || echo "❌ No se encuentra uso"
echo ""

# 9. Verificar proceso de build del frontend
separator
echo "9. VERIFICACIÓN DE BUILD"
echo "Verificando si hay archivos de build recientes:"
if [ -d "/home/mloco/Escritorio/ClasificadorV2/frontend/dist" ]; then
    echo "Directorio dist existe"
    echo "Fecha del último build:"
    ls -la /home/mloco/Escritorio/ClasificadorV2/frontend/dist/ | head -3
else
    echo "❌ No existe directorio dist"
fi
echo ""

# 10. Probar una URL completa de miniatura
separator
echo "10. PRUEBA DE URL COMPLETA"
echo "Construyendo URL como lo haría el frontend:"
echo "URL base: http://localhost:8000"
if [ ! -z "$first_thumb" ]; then
    full_url="http://localhost:8000/thumbnails/$first_thumb"
    echo "URL completa: $full_url"
    echo "Probando URL completa:"
    curl -s -I "$full_url" 2>/dev/null | head -5
else
    echo "❌ No hay thumbnails para probar"
fi

separator
echo "=== FIN DEL DIAGNÓSTICO ==="
echo ""
echo "RESUMEN DE ACCIONES RECOMENDADAS:"
echo "1. Si los containers no están corriendo: docker-compose up -d"
echo "2. Si hay errores 404 en thumbnails: verificar configuración de static files"
echo "3. Si el código no está actualizado: verificar hot reload de Vite"
echo "4. Si hay errores en logs: revisar errores específicos"
echo "5. Si faltan skeleton loaders: añadir componente LoadingSkeleton"
