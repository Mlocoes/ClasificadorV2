#!/bin/bash

# Colores para los mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}===== CONFIGURACIÓN PARA ACCESO DESDE RED =====${NC}"
echo ""
echo "Chrome está bloqueando las peticiones de red privada por seguridad."
echo "Aquí tienes varias opciones para solucionarlo:"
echo ""

echo -e "${GREEN}OPCIÓN 1: Usar localhost (RECOMENDADO)${NC}"
echo "- Accede desde: http://localhost:3000"
echo "- Funciona sin problemas de seguridad"
echo "- Para acceso desde otros dispositivos, usar SSH tunneling"
echo ""

echo -e "${GREEN}OPCIÓN 2: Chrome con flags de desarrollo${NC}"
echo "Ejecuta Chrome con estos flags para desarrollo:"
echo ""
echo "google-chrome --disable-web-security --disable-features=VizDisplayCompositor --user-data-dir=/tmp/chrome_dev_session --allow-running-insecure-content --disable-features=BlockInsecurePrivateNetworkRequests"
echo ""
echo "O en Ubuntu/Debian:"
echo "chromium-browser --disable-web-security --disable-features=VizDisplayCompositor --user-data-dir=/tmp/chrome_dev_session --allow-running-insecure-content --disable-features=BlockInsecurePrivateNetworkRequests"
echo ""

echo -e "${GREEN}OPCIÓN 3: SSH Tunneling para acceso remoto${NC}"
echo "Desde otro dispositivo en la red:"
echo "ssh -L 3000:localhost:3000 -L 8000:localhost:8000 usuario@192.168.0.7"
echo "Luego accede a: http://localhost:3000"
echo ""

echo -e "${GREEN}OPCIÓN 4: Configurar HTTPS local${NC}"
echo "Más complejo pero más seguro para desarrollo:"
echo "- Generar certificados SSL locales"
echo "- Configurar nginx con HTTPS"
echo "- Actualizar docker-compose para HTTPS"
echo ""

echo -e "${YELLOW}RECOMENDACIÓN:${NC}"
echo "Para desarrollo local: Usar OPCIÓN 1 (localhost)"
echo "Para acceso desde otros dispositivos: Usar OPCIÓN 3 (SSH tunneling)"
echo ""

# Verificar si podemos cambiar automáticamente a localhost
read -p "¿Deseas configurar automáticamente para localhost? (y/n): " confirm
if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    echo ""
    echo "Reiniciando servicios con configuración localhost..."
    cd /home/mloco/Escritorio/ClasificadorV2
    docker-compose down
    docker-compose up -d
    
    echo ""
    echo -e "${GREEN}✅ Servicios reiniciados${NC}"
    echo "Accede a: http://localhost:3000"
    echo "API disponible en: http://localhost:8000/api/v1"
    
    # Abrir navegador automáticamente
    if command -v xdg-open > /dev/null; then
        echo "Abriendo navegador..."
        xdg-open http://localhost:3000 &
    fi
fi
