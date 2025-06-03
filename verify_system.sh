#!/bin/bash

# Colores para los mensajes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Verificando el sistema...${NC}"

# Verificar Python y versión
echo -n "Python: "
if command -v python3 &> /dev/null; then
    python3 --version
    echo -e "${GREEN}✓ Python instalado${NC}"
else
    echo -e "${RED}✗ Python no encontrado${NC}"
    exit 1
fi

# Verificar Node.js y versión
echo -n "Node.js: "
if command -v node &> /dev/null; then
    node --version
    echo -e "${GREEN}✓ Node.js instalado${NC}"
else
    echo -e "${RED}✗ Node.js no encontrado${NC}"
    exit 1
fi

# Verificar npm y versión
echo -n "npm: "
if command -v npm &> /dev/null; then
    npm --version
    echo -e "${GREEN}✓ npm instalado${NC}"
else
    echo -e "${RED}✗ npm no encontrado${NC}"
    exit 1
fi

# Verificar Docker y versión
echo -n "Docker: "
if command -v docker &> /dev/null; then
    docker --version
    echo -e "${GREEN}✓ Docker instalado${NC}"
else
    echo -e "${RED}✗ Docker no encontrado${NC}"
    exit 1
fi

# Verificar Docker Compose y versión
echo -n "Docker Compose: "
if command -v docker-compose &> /dev/null; then
    docker-compose --version
    echo -e "${GREEN}✓ Docker Compose instalado${NC}"
else
    echo -e "${RED}✗ Docker Compose no encontrado${NC}"
    exit 1
fi

# Verificar estructura de directorios
echo -e "\nVerificando estructura de directorios:"
directories=(
    "backend/app"
    "frontend/src"
    "storage/uploads"
    "storage/thumbnails"
)

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓ $dir existe${NC}"
    else
        echo -e "${RED}✗ $dir no existe${NC}"
        mkdir -p "$dir"
        echo -e "${YELLOW}  Directorio creado${NC}"
    fi
done

# Verificar archivos de configuración
echo -e "\nVerificando archivos de configuración:"
files=(
    "backend/requirements.txt"
    "frontend/package.json"
    "docker-compose.yml"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file existe${NC}"
    else
        echo -e "${RED}✗ $file no existe${NC}"
    fi
done

echo -e "\n${GREEN}Verificación completada${NC}"
