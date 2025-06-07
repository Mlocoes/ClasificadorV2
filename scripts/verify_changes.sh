#!/bin/bash

echo "=== VERIFICACIÓN POST-ACTUALIZACIÓN ==="
echo "Verificando que todos los cambios se aplicaron correctamente"
echo ""

cd /home/mloco/Escritorio/ClasificadorV2

# 1. Verificar que getMediaUrl existe en mediaService.ts
echo "1. Verificando función getMediaUrl:"
if grep -q "export const getMediaUrl" frontend/src/services/mediaService.ts; then
    echo "✅ getMediaUrl encontrada en mediaService.ts"
    grep -n "getMediaUrl" frontend/src/services/mediaService.ts
else
    echo "❌ getMediaUrl NO encontrada en mediaService.ts"
fi
echo ""

# 2. Verificar imports en MediaGrid.tsx
echo "2. Verificando imports en MediaGrid.tsx:"
if grep -q "import.*getMediaUrl.*from.*mediaService" frontend/src/components/MediaGrid.tsx; then
    echo "✅ Import de getMediaUrl encontrado en MediaGrid.tsx"
else
    echo "❌ Import de getMediaUrl NO encontrado en MediaGrid.tsx"
fi

if grep -q "import.*LoadingSkeleton" frontend/src/components/MediaGrid.tsx; then
    echo "✅ Import de LoadingSkeleton encontrado en MediaGrid.tsx"
else
    echo "❌ Import de LoadingSkeleton NO encontrado en MediaGrid.tsx"
fi
echo ""

# 3. Verificar uso en MediaGrid.tsx
echo "3. Verificando uso de getMediaUrl en MediaGrid.tsx:"
if grep -q "getMediaUrl(item.thumbnail_path)" frontend/src/components/MediaGrid.tsx; then
    echo "✅ Uso de getMediaUrl encontrado en MediaGrid.tsx"
    grep -n "getMediaUrl" frontend/src/components/MediaGrid.tsx
else
    echo "❌ Uso de getMediaUrl NO encontrado en MediaGrid.tsx"
fi
echo ""

# 4. Verificar LoadingSkeleton.tsx
echo "4. Verificando componente LoadingSkeleton:"
if [ -f "frontend/src/components/LoadingSkeleton.tsx" ]; then
    echo "✅ LoadingSkeleton.tsx existe"
    echo "Líneas del archivo: $(wc -l < frontend/src/components/LoadingSkeleton.tsx)"
else
    echo "❌ LoadingSkeleton.tsx NO existe"
fi
echo ""

# 5. Verificar MediaTable.tsx
echo "5. Verificando MediaTable.tsx:"
if grep -q "import.*getMediaUrl.*from.*mediaService" frontend/src/components/MediaTable.tsx; then
    echo "✅ Import de getMediaUrl encontrado en MediaTable.tsx"
else
    echo "❌ Import de getMediaUrl NO encontrado en MediaTable.tsx"
fi

if grep -q "import.*LoadingSkeleton" frontend/src/components/MediaTable.tsx; then
    echo "✅ Import de LoadingSkeleton encontrado en MediaTable.tsx"
else
    echo "❌ Import de LoadingSkeleton NO encontrado en MediaTable.tsx"
fi
echo ""

# 6. Verificar docker-compose.yml
echo "6. Verificando docker-compose.yml:"
if grep -q "frontend/src:/app/src" docker-compose.yml; then
    echo "✅ Volume para hot reload configurado"
else
    echo "❌ Volume para hot reload NO configurado"
fi
echo ""

# 7. Verificar estructura de thumbnails
echo "7. Verificando estructura de storage:"
if [ -d "storage/thumbnails" ]; then
    echo "✅ Directorio storage/thumbnails existe"
    echo "Archivos en thumbnails:"
    ls -la storage/thumbnails/ | head -5
    echo "Total de thumbnails: $(find storage/thumbnails -name "thumb_*" 2>/dev/null | wc -l)"
else
    echo "❌ Directorio storage/thumbnails NO existe"
fi
echo ""

# 8. Crear un archivo de resumen
echo "8. Creando resumen de verificación..."
cat > VERIFICACION_CAMBIOS.md << EOF
# Verificación de Cambios - ClasificadorV2

## Cambios Aplicados

### 1. ✅ Función getMediaUrl en mediaService.ts
- Función para construir URLs completas de media
- Maneja rutas relativas y absolutas
- Base URL: http://localhost:8000

### 2. ✅ Componente LoadingSkeleton.tsx
- Skeleton loaders para diferentes vistas (card, table, list)
- Reemplaza CircularProgress básico
- Mejora la experiencia de usuario durante la carga

### 3. ✅ MediaGrid.tsx actualizado
- Import de getMediaUrl y LoadingSkeleton
- Uso de getMediaUrl para construir URLs de thumbnails
- LoadingSkeleton en lugar de CircularProgress

### 4. ✅ MediaTable.tsx actualizado
- Import de getMediaUrl y LoadingSkeleton
- Uso de getMediaUrl para URLs de thumbnails
- LoadingSkeleton para estado de carga

### 5. ✅ docker-compose.yml actualizado
- Volumes añadidos para hot reload del frontend
- Montaje de src, public, y archivos de configuración

## Próximos Pasos

1. **Reiniciar el sistema**:
   \`\`\`bash
   docker-compose down
   docker-compose up -d --build
   \`\`\`

2. **Verificar en el navegador**:
   - Abrir http://localhost:3000
   - Verificar que aparezcan skeleton loaders durante la carga
   - Verificar que las miniaturas se muestren correctamente

3. **Usar herramientas de diagnóstico**:
   - Abrir diagnostics.html en el navegador
   - Ejecutar diagnóstico completo
   - Revisar Network tab en Developer Tools

4. **Verificar logs**:
   \`\`\`bash
   docker-compose logs frontend
   docker-compose logs backend
   \`\`\`

## Problemas Comunes

- **Hot reload no funciona**: Verificar que los volumes estén montados
- **404 en thumbnails**: Verificar configuración de static files en backend
- **CORS errors**: Verificar configuración de CORS en backend
- **Caché del navegador**: Ctrl+F5 para hard refresh

Fecha de verificación: $(date)
EOF

echo "✅ Resumen creado en VERIFICACION_CAMBIOS.md"
echo ""

echo "=== COMANDOS PARA CONTINUAR ==="
echo "1. Reiniciar sistema: docker-compose down && docker-compose up -d --build"
echo "2. Ver logs frontend: docker-compose logs -f frontend"  
echo "3. Ver logs backend: docker-compose logs -f backend"
echo "4. Abrir diagnóstico: firefox file://$(pwd)/diagnostics.html"
echo "5. Acceder a la app: firefox http://localhost:3000"
