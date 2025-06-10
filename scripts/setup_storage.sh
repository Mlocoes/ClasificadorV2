#!/bin/bash

# Script para asegurar que los directorios de almacenamiento tengan los permisos correctos
# Este script debe ejecutarse antes de iniciar los contenedores

echo "Configurando directorios de almacenamiento..."

# Crear directorios si no existen
mkdir -p ./storage/uploads
mkdir -p ./storage/thumbnails
mkdir -p ./storage/processed
mkdir -p ./storage/data

# Establecer permisos
chmod -R 777 ./storage

echo "Directorios configurados correctamente"
