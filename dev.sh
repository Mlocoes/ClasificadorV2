#!/bin/bash

# Colores para los mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Iniciando entorno de desarrollo para ClasificadorV2...${NC}"

# Crear directorios necesarios si no existen
mkdir -p storage/{uploads,thumbnails}

# Iniciar backend
echo -e "${GREEN}Iniciando backend...${NC}"
cd backend
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload &
BACKEND_PID=$!

# Iniciar frontend
echo -e "${GREEN}Iniciando frontend...${NC}"
cd ../frontend
npm install
npm run dev &
FRONTEND_PID=$!

# Función para manejar el cierre
cleanup() {
    echo -e "${YELLOW}Deteniendo servicios...${NC}"
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit 0
}

# Capturar señal de interrupción
trap cleanup SIGINT

# Mantener el script corriendo
echo -e "${GREEN}Servicios iniciados. Presiona Ctrl+C para detener.${NC}"
wait
