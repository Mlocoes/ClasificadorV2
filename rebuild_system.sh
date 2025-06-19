#!/bin/bash

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Script de Reconstrucción Unificado - ClasificadorV2 ===${NC}"
echo

# Opciones de reconstrucción
echo -e "Por favor, seleccione una opción de reconstrucción:"
echo -e "  ${GREEN}1${NC}. Reconstrucción estándar (mantiene los datos)"
echo -e "  ${YELLOW}2${NC}. Reconstrucción completa (elimina todos los datos)"
echo -e "  ${RED}3${NC}. Cancelar"

read -p "Seleccione una opción [1-3]: " OPTION

case $OPTION in
    1)
        echo -e "${GREEN}Iniciando reconstrucción estándar...${NC}"
        echo

        # Detener y eliminar contenedores existentes
        echo "1. Deteniendo contenedores existentes..."
        docker-compose down
        echo "✅ Contenedores detenidos"

        # Eliminar imágenes
        echo "2. Eliminando imágenes existentes..."
        docker rmi clasificadorv2-backend clasificadorv2-frontend 2>/dev/null || true
        echo "✅ Imágenes eliminadas"

        # Eliminar carpetas de storage (opcional, preguntar al usuario)
        echo "3. ¿Desea eliminar también los archivos almacenados (uploads, thumbnails, processed)?"
        echo "   Esto eliminará todas las imágenes subidas y procesadas."
        read -p "   Eliminar archivos almacenados? (s/N): " REMOVE_STORAGE
        if [[ "$REMOVE_STORAGE" =~ ^[sS]$ ]]; then
            echo "   Eliminando archivos almacenados..."
            rm -rf storage/uploads/* storage/thumbnails/* storage/processed/*
            echo "   ✅ Archivos almacenados eliminados"
        else
            echo "   ✅ Archivos almacenados conservados"
        fi

        # Eliminar node_modules (opcional)
        echo "4. ¿Desea eliminar node_modules para una instalación limpia del frontend?"
        read -p "   Eliminar node_modules? (s/N): " REMOVE_MODULES
        if [[ "$REMOVE_MODULES" =~ ^[sS]$ ]]; then
            echo "   Eliminando node_modules..."
            rm -rf frontend/node_modules
            echo "   ✅ node_modules eliminados"
        else
            echo "   ✅ node_modules conservados"
        fi

        # Reconstruir y levantar los contenedores
        echo "5. Reconstruyendo y levantando contenedores..."
        docker-compose up --build -d
        echo "✅ Contenedores reconstruidos y levantados"
        ;;

    2)
        echo -e "${YELLOW}Iniciando reconstrucción completa...${NC}"
        echo -e "${RED}¡ADVERTENCIA! Esta opción eliminará TODOS los datos, incluyendo la base de datos.${NC}"
        read -p "¿Está seguro de que desea continuar? (s/N): " CONFIRM
        if [[ ! "$CONFIRM" =~ ^[sS]$ ]]; then
            echo "Operación cancelada."
            exit 1
        fi

        # Directorio actual
        CURRENT_DIR=$(pwd)
        echo "Directorio de trabajo: $CURRENT_DIR"

        # Detener y eliminar contenedores con volúmenes
        echo "1. Deteniendo y eliminando contenedores con volúmenes..."
        docker-compose down --volumes
        echo "✅ Contenedores y volúmenes eliminados"

        # Eliminar imágenes
        echo "2. Eliminando imágenes Docker..."
        docker rmi clasificadorv2-backend clasificadorv2-frontend 2>/dev/null || true
        echo "✅ Imágenes eliminadas"

        # Eliminar datos almacenados
        echo "3. Eliminando todos los datos almacenados..."
        rm -rf storage/uploads/* storage/thumbnails/* storage/processed/*
        rm -f storage/db.sqlite3
        echo "✅ Datos almacenados eliminados"

        # Eliminar cache de modelos
        echo "4. ¿Desea eliminar la cache de modelos AI? (Esto requerirá volver a descargarlos)"
        read -p "   Eliminar cache de modelos? (s/N): " REMOVE_CACHE
        if [[ "$REMOVE_CACHE" =~ ^[sS]$ ]]; then
            echo "   Eliminando cache de modelos..."
            rm -rf cache/models--*
            echo "   ✅ Cache de modelos eliminada"
        else
            echo "   ✅ Cache de modelos conservada"
        fi

        # Eliminar node_modules
        echo "5. Eliminando node_modules para instalación limpia del frontend..."
        rm -rf frontend/node_modules
        echo "✅ node_modules eliminado"

        # Reconstruir y levantar los contenedores
        echo "6. Reconstruyendo y levantando contenedores..."
        docker-compose up --build -d
        echo "✅ Contenedores reconstruidos y levantados"
        ;;

    3|*)
        echo "Operación cancelada."
        exit 0
        ;;
esac

echo
echo -e "${GREEN}¡Reconstrucción completada!${NC}"
echo "El sistema debería estar disponible en unos momentos en http://localhost:3000"
echo

# Verificar estado de los contenedores
echo "Verificando estado de los contenedores:"
docker-compose ps
