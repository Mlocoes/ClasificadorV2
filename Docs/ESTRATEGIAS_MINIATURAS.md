# Opciones de Estrategias para Miniaturas

Este documento describe las diferentes estrategias disponibles para el almacenamiento de miniaturas en el sistema ClasificadorV2.

## Estrategias Disponibles

### 1. Directorio Dedicado (`dedicated_dir`)

**Descripción:** Todas las miniaturas se guardan en un directorio específico dedicado.

**Ubicación:** `/app/storage/thumbnails/`

**Ventajas:**
- Organización centralizada de todas las miniaturas.
- Facilita la gestión (respaldo, eliminación, etc.) de todas las miniaturas a la vez.
- Simplifica la configuración de permisos y seguridad.

**Desventajas:**
- Con grandes volúmenes de archivos, el directorio puede crecer demasiado.
- Puede ser menos claro qué miniatura corresponde a qué archivo original.

### 2. Subdirectorio (`subdir`)

**Descripción:** Se crea un subdirectorio `thumbnails` dentro de cada directorio que contiene archivos originales.

**Ubicación:** `/ruta/al/archivo/original/../thumbnails/`

**Ventajas:**
- Las miniaturas se mantienen junto a los archivos originales.
- Mejor organización cuando los archivos se distribuyen en varios directorios.
- Si se elimina un directorio con archivos originales, también se eliminan sus miniaturas.

**Desventajas:**
- Requiere mayor mantenimiento de directorios.
- Permisos deben establecerse en múltiples ubicaciones.
- Más complejo para listar todas las miniaturas del sistema.

### 3. Directorio Base (`base_dir`)

**Descripción:** Similar a `dedicated_dir`, usa un directorio en la raíz del proyecto.

**Ubicación:** `/app/storage/thumbnails/` (configuración anterior)

**Ventajas y desventajas:** Similares a la estrategia `dedicated_dir`.

## Cómo cambiar la estrategia

Para cambiar la estrategia de almacenamiento de miniaturas, utilice el script proporcionado:

```bash
./update_thumbnail_strategy.sh <estrategia>
```

Donde `<estrategia>` puede ser:
- `dedicated_dir`
- `subdir`
- `base_dir`

Ejemplo:
```bash
./update_thumbnail_strategy.sh dedicated_dir
```

## Regeneración de miniaturas

Si cambia la estrategia y desea que todas las miniaturas existentes sigan la nueva estrategia, se recomienda regenerarlas:

```bash
./regenerate_thumbnails.sh
```

Este proceso puede ser lento para grandes volúmenes de archivos.

## Estrategia Recomendada

Para la mayoría de los casos, se recomienda usar la estrategia `dedicated_dir` ya que es la más simple de gestionar y configurar.
