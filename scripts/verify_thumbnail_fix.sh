#!/bin/bash

echo "=== VERIFICACIÓN DE SOLUCIÓN DE MINIATURAS ==="
echo ""

# Esperar a que el frontend esté completamente iniciado
echo "Esperando a que el frontend esté completamente cargado..."
sleep 5

echo "1. Verificando que el backend puede servir miniaturas:"
THUMBNAIL_PATH=$(docker exec backend python3 -c "
import sqlite3
conn = sqlite3.connect('/app/storage/db.sqlite3')
cursor = conn.cursor()
cursor.execute('SELECT thumbnail_path FROM media WHERE thumbnail_path IS NOT NULL LIMIT 1')
row = cursor.fetchone()
if row:
    print(row[0])
conn.close()
" 2>/dev/null)

if [ ! -z "$THUMBNAIL_PATH" ]; then
    echo "Probando acceso directo a: $THUMBNAIL_PATH"
    curl -s -I "http://localhost:8000$THUMBNAIL_PATH" | grep "HTTP"
else
    echo "No se encontraron miniaturas en la base de datos"
fi
echo ""

echo "2. Verificando que el frontend puede obtener la lista de medios:"
curl -s "http://localhost:8000/api/v1/media/" | python3 -c "
import sys
import json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list) and len(data) > 0:
        print(f'✅ API devuelve {len(data)} elementos')
        first_item = data[0]
        print(f'Primer elemento:')
        print(f'  - ID: {first_item.get(\"id\")}')
        print(f'  - Filename: {first_item.get(\"filename\")}')
        print(f'  - Thumbnail path: {first_item.get(\"thumbnail_path\")}')
        print(f'  - File path: {first_item.get(\"file_path\")}')
    else:
        print('❌ API no devuelve datos válidos')
except Exception as e:
    print(f'❌ Error procesando respuesta de API: {e}')
"
echo ""

echo "3. Verificando acceso al frontend:"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000")
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Frontend accesible en http://localhost:3000 (HTTP $FRONTEND_STATUS)"
else
    echo "❌ Frontend no accesible (HTTP $FRONTEND_STATUS)"
fi
echo ""

echo "4. Sugerencia de prueba manual:"
echo "Ahora puedes abrir http://localhost:3000 en tu navegador y verificar si las miniaturas se muestran correctamente."
echo ""

echo "5. URLs que deberían funcionar para las miniaturas:"
docker exec backend python3 -c "
import sqlite3
conn = sqlite3.connect('/app/storage/db.sqlite3')
cursor = conn.cursor()
cursor.execute('SELECT id, filename, thumbnail_path FROM media WHERE thumbnail_path IS NOT NULL LIMIT 3')
rows = cursor.fetchall()
for row in rows:
    print(f'  Archivo: {row[1]}')
    print(f'  URL: http://localhost:8000{row[2]}')
    print('')
conn.close()
" 2>/dev/null

echo "=== FIN DE LA VERIFICACIÓN ==="
