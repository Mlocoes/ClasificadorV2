#!/bin/bash

# Crear directorios si no existen
mkdir -p storage/uploads storage/thumbnails storage/processed cache

# Establecer permisos
chmod 755 storage storage/uploads storage/thumbnails storage/processed cache
chown -R $USER:$USER storage storage/uploads storage/thumbnails storage/processed cache

echo "Permisos establecidos correctamente"
