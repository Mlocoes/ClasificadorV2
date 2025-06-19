# Documentación del Selector de Modelos de IA

## Descripción

ClasificadorV2 ahora incorpora un sistema de selección de modelos de IA que permite alternar entre:

1. **CLIP** (Contrastive Language-Image Pre-Training): Un modelo multimodal desarrollado por OpenAI que ofrece alta precisión en la clasificación de eventos.
2. **OpenCV+DNN**: Utiliza una red neuronal convolucional pre-entrenada (ResNet-50) a través del módulo DNN de OpenCV, enfocado en eficiencia y rendimiento.
3. **OpenCV+YOLO**: Implementa el modelo YOLOv4 (You Only Look Once) para detección de objetos, que proporciona una identificación más precisa de elementos en la imagen para clasificar eventos.

## Características Principales

- **Interfaz web**: Selector intuitivo en la interfaz principal para cambiar de modelo
- **Persistencia**: La configuración se guarda entre reinicios del sistema
- **API REST**: Endpoints dedicados para consultar y modificar el modelo activo
- **Optimización**: OpenCV+DNN ofrece menor consumo de recursos con clasificación aceptable
- **Adaptabilidad**: Opciones para diferentes casos de uso según necesidades

## Diferencias entre modelos

| Característica | CLIP | OpenCV+DNN (ResNet-50) | OpenCV+YOLO |
|---------------|------|------------|------------|
| Precisión     | Alta | Media      | Alta       |
| Velocidad     | Moderada | Alta   | Media-Alta |
| Uso de memoria | Alto | Bajo      | Medio      |
| Categorías     | 15 específicas | Mapeo desde 1000 clases ImageNet | 80 clases COCO |
| Tamaño del modelo | ~1GB | ~100MB | ~245MB |
| Especialización | Eventos sociales | Objetos generales | Detección de objetos |
| Tipo de análisis | Semántico | Clasificación | Detección |

## Cómo usar

### Desde la Interfaz Web

1. Acceder a la aplicación web de ClasificadorV2
2. Buscar el panel "Configuración del Modelo de IA" en la interfaz
3. Seleccionar el modelo deseado (CLIP u OpenCV+DNN)
4. Hacer clic en "Guardar cambios"
5. El nuevo modelo será usado para todas las clasificaciones posteriores

### Desde la API REST

**Consultar modelo actual**:
```http
GET /api/v1/config/
```

**Cambiar modelo**:
```http
POST /api/v1/config/ai-model
Content-Type: application/json

{
    "model": "opencv_dnn"
}
```

o

```http
POST /api/v1/config/ai-model
Content-Type: application/json

{
    "model": "opencv_yolo"
}
```

## Consideraciones Técnicas

### Modelo CLIP

- Implementa "cero-shot learning" para clasificar sin entrenamiento específico
- Permite entender conceptos más abstractos como "concierto" o "graduación"
- Mayor precisión para categorías de eventos sociales y culturales
- Requiere más recursos (memoria y CPU/GPU)

### Modelo OpenCV+DNN (ResNet-50)

- Clasificación basada en las 1000 categorías de ImageNet
- Implementa un sistema de puntuación para mapear objetos a categorías de eventos
- Menor precisión pero significativamente más rápido
- Descarga automática del modelo (~25MB) en la primera ejecución
- Ideal para dispositivos con recursos limitados

### Modelo OpenCV+YOLO

- Basado en YOLOv4 para detección de objetos en tiempo real
- Utiliza el conjunto de datos COCO con 80 clases de objetos comunes
- Mejor precisión que ResNet-50 para detectar múltiples objetos en la imagen
- Balance entre precisión y velocidad
- Implementa una lógica avanzada para relacionar objetos detectados con tipos de eventos
- Descarga automática de los archivos del modelo (~245MB) en la primera ejecución
- Recomendado para clasificaciones que requieran detección de objetos específicos

## Ejemplos de respuestas

### CLIP
- "boda" (para imágenes de ceremonias matrimoniales)
- "concierto" (para imágenes de presentaciones musicales)
- "evento deportivo" (para imágenes de competiciones)

### OpenCV+DNN
- "evento deportivo" (detecta elementos como pelotas, uniformes)
- "evento gastronómico" (detecta comida, restaurantes)
- "actividad al aire libre" (detecta montañas, playas, bosques)

### OpenCV+YOLO
- "evento deportivo" (detecta jugadores, pelotas deportivas, raquetas)
- "fiesta" (detecta vasos, botellas, personas reunidas)
- "boda" (detecta vestidos, pasteles, velas, arreglos florales)
- "conferencia" (detecta ordenadores portátiles, personas, presentaciones)

## Solución de problemas

Si experimenta problemas con alguno de los modelos:

1. **Problema**: El modelo CLIP muestra "unknown" con confianza 0.0
   **Solución**: Verificar que los archivos del modelo están correctamente descargados en `/app/cache/models`

2. **Problema**: El modelo OpenCV+DNN no se descarga correctamente
   **Solución**: Ejecutar manualmente el script `test_ai_models.py` para forzar la descarga

3. **Problema**: El modelo OpenCV+YOLO muestra un error al cargar los pesos
   **Solución**: Verificar que el archivo de pesos se descargó completamente (~245MB). Eliminar archivos en `/app/cache/models--opencv--dnn` y reintentar la descarga.

4. **Problema**: La descarga del modelo YOLO es muy lenta
   **Solución**: El archivo de pesos es grande (~245MB). Espere a que se complete la descarga o descargue manualmente en `/app/cache/models--opencv--dnn/yolov4.weights`.

5. **Problema**: La selección del modelo no persiste tras reiniciar
   **Solución**: Verificar permisos de escritura en `/app/config`
