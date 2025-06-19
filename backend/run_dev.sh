#!/bin/bash

# Colores para los mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Script de desarrollo para ClasificadorV2 Backend ===${NC}\n"

# Verificar entorno virtual
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creando entorno virtual...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}Entorno virtual creado.${NC}"
fi

# Activar entorno virtual
echo -e "${YELLOW}Activando entorno virtual...${NC}"
source venv/bin/activate
echo -e "${GREEN}Entorno virtual activado.${NC}"

# Instalar/actualizar dependencias
echo -e "${YELLOW}Instalando/actualizando dependencias...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}Dependencias instaladas.${NC}\n"

# Crear directorios necesarios
echo -e "${YELLOW}Verificando directorios necesarios...${NC}"
for dir in "../storage/uploads" "../storage/thumbnails" "../storage/processed" "../config" "../logs"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo -e "Directorio $dir creado."
    else
        echo -e "Directorio $dir ya existe."
    fi
done
echo -e "${GREEN}Directorios verificados.${NC}\n"

# Opciones de ejecución
echo -e "Seleccione modo de ejecución:"
echo -e "  ${GREEN}1${NC}. Normal (producción)"
echo -e "  ${YELLOW}2${NC}. Desarrollo (con recarga automática)"
echo -e "  ${BLUE}3${NC}. Depuración (con recarga y logs detallados)"
echo -e "  ${RED}4${NC}. Cancelar"

read -p "Seleccione una opción [1-4]: " OPTION

UVICORN_CMD="uvicorn app.main:app"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

case $OPTION in
    1)
        echo -e "${GREEN}Iniciando en modo normal...${NC}"
        $UVICORN_CMD --host 0.0.0.0 --port 8000
        ;;
    2)
        echo -e "${YELLOW}Iniciando en modo desarrollo...${NC}"
        $UVICORN_CMD --reload --host 0.0.0.0 --port 8000
        ;;
    3)
        echo -e "${BLUE}Iniciando en modo depuración...${NC}"
        export LOG_LEVEL="DEBUG"
        export LOG_TO_FILE="True"
        $UVICORN_CMD --reload --host 0.0.0.0 --port 8000 --log-level debug
        ;;
    4|*)
        echo -e "${RED}Operación cancelada.${NC}"
        exit 0
        ;;
esac
