# Funcionalidad de Archivos Procesados

## Descripción General

La funcionalidad de archivos procesados permite generar automáticamente copias estandarizadas de los archivos multimedia subidos al sistema. Estas copias siguen una convención de nombres basada en la fecha de creación del archivo y el tipo de evento detectado por la IA, facilitando la organización y búsqueda posterior.

## Características Clave

- **Generación automática**: Se crea una copia procesada para cada archivo subido
- **Convención de nombres**: Formato `YYYY-MM-DD-tipo-evento[-n].extensión`
- **Almacenamiento dedicado**: Los archivos procesados se guardan en `/storage/processed/`
- **Preservación del formato**: Se mantiene la extensión y calidad original del archivo
- **Numeración automática**: Añade un sufijo numérico cuando hay múltiples archivos del mismo evento y fecha

## Flujo de Procesamiento

1. El usuario sube un archivo multimedia al sistema
2. El sistema extrae metadatos, incluyendo la fecha de creación
3. El modelo CLIP analiza el contenido visual y clasifica el tipo de evento
4. Se genera un nombre estandarizado siguiendo el formato especificado
5. Se crea una copia del archivo con el nuevo nombre en el directorio `processed`
6. La ruta de la copia procesada se almacena en la base de datos

## Implementación Técnica

### Estructura de la Base de Datos

La tabla `media` incluye el campo `processed_file_path` que almacena la ruta relativa del archivo procesado:

```sql
CREATE TABLE media (
    ...
    processed_file_path VARCHAR,
    ...
);
```

### Componentes Involucrados

- **MediaProcessor (backend)**: Servicio que implementa la lógica de procesamiento
- **API (backend)**: Endpoints que gestionan los archivos y actualizan la base de datos
- **Modelo (backend)**: Estructura que define el campo `processed_file_path`

### Consideraciones

- Si no se puede determinar la fecha de creación, se usa la fecha actual
- Si la clasificación del evento tiene baja confianza, se utiliza igualmente
- El sistema maneja automáticamente colisiones de nombres añadiendo sufijos numéricos

## Beneficios

- **Organización mejorada**: Nombres de archivos consistentes y descriptivos
- **Búsqueda facilitada**: Permite buscar por fecha y tipo de evento en el sistema de archivos
- **Preservación de originales**: Los archivos originales se mantienen intactos
- **Consistencia**: Todos los archivos siguen la misma convención de nombres

## Ejemplos

Archivo original: `IMG_20240605_123456.jpg`
Archivo procesado: `2024-06-05-conferencia.jpg`

Archivo original: `MOV_0123.mp4` (de una boda grabada el 15/08/2023)
Archivo procesado: `2023-08-15-boda.mp4`
