#!/bin/bash

echo "=== DEPURACIÓN AVANZADA DEL PROBLEMA DE MINIATURAS ==="
echo ""

# Reiniciar contenedores para asegurar que los cambios se carguen
echo "1. Reiniciando contenedores para aplicar cambios..."
docker-compose restart
echo "Esperando 15 segundos para que los servicios se reinicien completamente..."
sleep 15

# Verificar que los contenedores están funcionando
echo "2. Verificando estado de contenedores:"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(frontend|backend)"
echo ""

# Verificar que el backend responde
echo "3. Verificando backend:"
curl -s -I "http://localhost:8000/health" | head -1

# Verificar que la API de medios funciona
echo "4. Verificando API de medios:"
API_RESPONSE=$(curl -s "http://localhost:8000/api/v1/media/")
if echo "$API_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'API OK: {len(data)} elementos')" 2>/dev/null; then
    echo "✅ API de medios funcionando"
else
    echo "❌ Error en API de medios:"
    echo "$API_RESPONSE" | head -3
fi
echo ""

# Verificar acceso directo a miniaturas
echo "5. Verificando acceso directo a miniaturas:"
THUMBNAILS=$(docker exec backend ls /app/storage/thumbnails/ | grep -v test_thumb.jpg | head -3)
for thumb in $THUMBNAILS; do
    echo "Probando: http://localhost:8000/thumbnails/$thumb"
    curl -s -I "http://localhost:8000/thumbnails/$thumb" | head -1
done
echo ""

# Verificar logs del frontend para errores
echo "6. Verificando logs recientes del frontend:"
docker logs frontend --tail 10 2>&1 | grep -i error || echo "No se encontraron errores recientes"
echo ""

# Verificar logs del backend para errores
echo "7. Verificando logs recientes del backend:"
docker logs backend --tail 10 2>&1 | grep -i error || echo "No se encontraron errores recientes"
echo ""

# Verificar si el problema está en el código compilado del frontend
echo "8. Verificando si los cambios están en el frontend compilado:"
docker exec frontend grep -r "getMediaUrl" /app/dist/ 2>/dev/null && echo "✅ Función getMediaUrl encontrada en el build" || echo "❌ Función getMediaUrl NO encontrada en el build"
echo ""

# Crear un archivo de prueba HTML para verificar manualmente
echo "9. Creando archivo de prueba HTML..."
cat > /tmp/test_thumbnails.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Test Miniaturas ClasificadorV2</title>
    <style>
        .thumbnail { margin: 10px; border: 1px solid #ccc; padding: 10px; }
        .thumbnail img { max-width: 200px; max-height: 200px; }
        .error { color: red; }
        .success { color: green; }
    </style>
</head>
<body>
    <h1>Test de Miniaturas ClasificadorV2</h1>
    <div id="results"></div>
    
    <script>
        fetch('http://localhost:8000/api/v1/media/')
        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById('results');
            
            if (data.length === 0) {
                resultsDiv.innerHTML = '<p class="error">No se encontraron medios en la API</p>';
                return;
            }
            
            data.forEach(item => {
                const div = document.createElement('div');
                div.className = 'thumbnail';
                
                const thumbnailUrl = `http://localhost:8000${item.thumbnail_path}`;
                
                div.innerHTML = `
                    <h3>${item.filename}</h3>
                    <p>Thumbnail path: ${item.thumbnail_path}</p>
                    <p>URL completa: ${thumbnailUrl}</p>
                    <img src="${thumbnailUrl}" onerror="this.style.border='2px solid red'; this.alt='ERROR CARGANDO IMAGEN';" onload="this.style.border='2px solid green';">
                `;
                
                resultsDiv.appendChild(div);
            });
        })
        .catch(error => {
            document.getElementById('results').innerHTML = `<p class="error">Error cargando datos: ${error}</p>`;
        });
    </script>
</body>
</html>
EOF

echo "✅ Archivo de prueba creado en /tmp/test_thumbnails.html"
echo ""

echo "10. Para prueba manual:"
echo "   - Abre http://localhost:3000 para ver el sistema real"
echo "   - Abre file:///tmp/test_thumbnails.html para ver la prueba directa"
echo ""

echo "=== FIN DE LA DEPURACIÓN AVANZADA ==="
