# Flujo de Trabajo del Sistema ClasificadorV2

## Visión General del Proceso

El sistema ClasificadorV2 implementa un flujo de trabajo completo para el procesamiento, clasificación y organización de archivos multimedia. A continuación se detalla cada paso del proceso desde la subida del archivo hasta su clasificación final.

```
[Frontend] → [API] → [MediaProcessor] → [Base de datos] → [Archivos organizados]
```

## 1. Recepción de Archivos

### Desde la interfaz web:
1. El usuario arrastra archivos o selecciona desde el explorador
2. Se validan los tipos MIME permitidos antes del envío
3. Se muestra un indicador de progreso durante la subida

### Desde la API directa:
1. Se envían archivos mediante solicitud POST a `/api/v1/media/upload/`
2. Se valida la autenticidad del archivo y su formato

## 2. Procesamiento Inicial

### Sanitización y validación:
1. Limpieza del nombre del archivo para compatibilidad con el sistema de archivos
2. Verificación de tamaño máximo y tipo de archivo permitido
3. Generación de nombres únicos para evitar conflictos

### Almacenamiento primario:
1. Guardado del archivo original en `/storage/uploads/`
2. Registro inicial en la base de datos con información básica

## 3. Extracción de Metadatos

### Análisis del archivo:
1. Extracción de datos EXIF para imágenes (fecha, dimensiones, GPS)
2. Extracción de metadata para vídeos (duración, dimensiones, codec)
3. Conversión de formatos especiales (ej: HEIC → JPG para procesamiento)

### Enriquecimiento de información:
1. Determinación precisa del tipo de archivo
2. Extracción de coordenadas geográficas cuando están disponibles
3. Normalización de fechas de creación

## 4. Generación de Miniaturas

### Proceso de creación:
1. Redimensionamiento proporcional manteniendo el aspecto original
2. Optimización para carga rápida en la interfaz
3. Almacenamiento en `/storage/thumbnails/`

### Casos especiales:
1. Para vídeos: extracción de un fotograma representativo
2. Para formatos RAW o HEIC: conversión previa a formato procesable

## 5. Clasificación mediante IA (CLIP)

### Análisis de contenido:
1. Procesamiento de la imagen mediante el modelo CLIP preentrenado
2. Comparación con un conjunto de categorías predefinidas
3. Determinación del tipo de evento representado en la imagen/vídeo

### Evaluación de confianza:
1. Cálculo del nivel de certeza en la clasificación
2. Selección de la categoría con mayor puntuación
3. Registro del nivel de confianza para referencia futura

## 6. Generación de Archivos Procesados

### Creación de nombre estandarizado:
1. Construcción del nombre siguiendo el formato `YYYY-MM-DD-tipo-evento.ext`
2. Verificación de colisiones y adición de índice numérico si es necesario
3. Preparación de la ruta de destino en `/storage/processed/`

### Procesamiento del archivo:
1. Creación de una copia del archivo original con el nuevo nombre
2. Verificación de integridad de la copia creada
3. Actualización del registro en la base de datos con la nueva ruta

## 7. Actualización de la Base de Datos

### Campos actualizados:
1. Metadatos extraídos (dimensiones, duración, fecha de creación)
2. Información geográfica (latitud, longitud)
3. Resultado de clasificación (tipo de evento, nivel de confianza)
4. Rutas de acceso (archivo original, miniatura, archivo procesado)

## 8. Presentación al Usuario

### Visualización en interfaz:
1. Actualización automática de la lista/cuadrícula de contenido
2. Visualización de miniaturas y metadatos relevantes
3. Opciones para gestión y edición de la información

## Diagrama Simplificado del Flujo

```
Usuario → Subida de archivo → Validación → Almacenamiento original
↓
Procesamiento de metadata → Extracción de información EXIF/media
↓
Generación de miniatura → Optimización para visualización
↓
Clasificación IA (CLIP) → Determinación del tipo de evento
↓
Creación archivo procesado → Nombre estandarizado por fecha y evento
↓
Actualización BD → Registro completo con todas las rutas
↓
Interfaz de usuario → Visualización y gestión
```

## Consideraciones de Rendimiento

El sistema está diseñado para procesar los archivos de manera eficiente, con las siguientes optimizaciones:

1. **Procesamiento asíncrono** para archivos grandes
2. **Caché de modelos de IA** para acelerar la clasificación
3. **Optimización de miniaturas** para carga rápida en la interfaz
4. **Procesamiento paralelo** cuando es posible para múltiples archivos

## Errores y Recuperación

El sistema implementa estrategias robustas para manejar errores en cada fase:

1. **Validación temprana** para evitar procesamiento innecesario
2. **Registro detallado** de errores para facilitar diagnóstico
3. **Mecanismos de reintentos** para operaciones críticas
4. **Estado parcial** para conservar información incluso si alguna fase falla
