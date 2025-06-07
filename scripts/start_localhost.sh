#!/bin/bash

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🚀 INICIANDO ClasificadorV2 en localhost${NC}"
echo ""

# Verificar que Docker esté funcionando
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker no está funcionando. Por favor, inicia Docker primero."
    exit 1
fi

# Cambiar al directorio del proyecto
cd /home/mloco/Escritorio/ClasificadorV2

# Asegurar que los servicios estén actualizados
echo "🔄 Iniciando servicios..."
docker-compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 15

# Verificar que los servicios respondan
echo "🔍 Verificando servicios..."

# Verificar backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "✅ Backend funcionando en ${GREEN}http://localhost:8000${NC}"
else
    echo "❌ Backend no responde"
    exit 1
fi

# Verificar frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "✅ Frontend funcionando en ${GREEN}http://localhost:3000${NC}"
else
    echo "❌ Frontend no responde"
    exit 1
fi

# Verificar API
if curl -s http://localhost:8000/api/v1/media/ > /dev/null; then
    echo -e "✅ API funcionando en ${GREEN}http://localhost:8000/api/v1${NC}"
else
    echo "❌ API no responde"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 ¡Sistema listo!${NC}"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 API: http://localhost:8000/api/v1"
echo "🖼️  Thumbnails: http://localhost:8000/thumbnails/"
echo ""

# Abrir navegador automáticamente
if command -v xdg-open > /dev/null 2>&1; then
    echo "🌐 Abriendo navegador automáticamente..."
    xdg-open http://localhost:3000 &
elif command -v open > /dev/null 2>&1; then
    echo "🌐 Abriendo navegador automáticamente..."
    open http://localhost:3000 &
else
    echo "🌐 Abre manualmente tu navegador en: http://localhost:3000"
fi

echo ""
echo -e "${YELLOW}💡 Nota: Si necesitas acceso desde otros dispositivos, usa SSH tunneling:${NC}"
echo "ssh -L 3000:localhost:3000 -L 8000:localhost:8000 usuario@$(hostname -I | awk '{print $1}')"
