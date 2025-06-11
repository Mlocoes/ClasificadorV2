# Pruebas de Modelos de IA para ClasificadorV2

Este directorio contiene scripts para probar los diferentes modelos de IA implementados en ClasificadorV2.

## Scripts disponibles

### 1. `test_ai_models.py`

Prueba directa de los modelos de IA accediendo al código del backend.

**Requisitos:**
- Acceso directo al código del backend
- Dependencias del backend instaladas
- Debe ejecutarse desde el directorio raíz del proyecto

**Uso:**
```bash
cd /home/mloco/Escritorio/ClasificadorV2
python scripts/test_ai_models.py --image Contexto/test_real.jpg
```

**Características:**
- Prueba ambos modelos (CLIP y OpenCV+DNN) directamente
- Mide tiempo de ejecución y confianza para cada modelo
- Muestra comparativa de resultados
- Prueba también la API de configuración

### 2. `test_ai_models_api.py`

Prueba los modelos de IA a través de la API REST, sin depender de importaciones directas del backend.

**Requisitos:**
- API del backend en ejecución (por defecto en http://localhost:8000/api/v1)
- Módulo requests de Python

**Uso:**
```bash
./scripts/test_ai_models_api.py --api-url http://localhost:8000/api/v1
```

**Características:**
- No requiere acceso directo al código del backend
- Prueba la API de cambio de modelo
- Compara tiempos de respuesta
- Más adecuado para entornos donde el backend corre en un contenedor o servidor separado

## Ejemplos de salida

### Ejemplo de salida de `test_ai_models.py`:
```
================================================================================
                 PRUEBA DE MODELOS DE IA PARA CLASIFICADORV2                  
================================================================================
Imagen a clasificar: /home/mloco/Escritorio/ClasificadorV2/Contexto/test_real.jpg
Visualizando imagen...
  - Dimensiones: 1200x800
  - Formato: JPEG
  - Modo: RGB

================================================================================
                          PRUEBA DIRECTA DE MODELOS                           
================================================================================

Clasificando imagen con modelo CLIP...
  - Evento detectado: concierto
  - Confianza: 0.8654
  - Tiempo de procesamiento: 2.35 segundos

Clasificando imagen con modelo OPENCV_DNN...
  - Evento detectado: evento musical
  - Confianza: 0.7123
  - Tiempo de procesamiento: 0.48 segundos

================================================================================
                     RESULTADOS COMPARATIVOS                      
================================================================================
Modelo          Evento                          Confianza   Tiempo
----------------------------------------------------------------------
clip            concierto                       0.8654    2.35s
opencv_dnn      evento musical                  0.7123    0.48s
```

### Ejemplo de salida de `test_ai_models_api.py`:
```
================================================================================
               PRUEBA DE MODELOS DE IA PARA CLASIFICADORV2 (VIA API)                
================================================================================
Imagen a clasificar: /home/mloco/Escritorio/ClasificadorV2/Contexto/test_real.jpg
Visualizando imagen...
  - Dimensiones: 1200x800
  - Formato: JPEG
  - Modo: RGB

================================================================================
                     PRUEBA DE LA API DE CONFIGURACIÓN                      
================================================================================
Modelo actual: clip

Cambiando el modelo de IA a través de la API (clip)...
  - Respuesta API: Modelo de IA cambiado a clip y configuración guardada

Cambiando el modelo de IA a través de la API (opencv_dnn)...
  - Respuesta API: Modelo de IA cambiado a opencv_dnn y configuración guardada
Modelo restaurado al original: clip

================================================================================
                           RESULTADOS DE LAS PRUEBAS                            
================================================================================
Modelo          Tiempo respuesta API
----------------------------------------
clip            0.12s
opencv_dnn      0.11s
```
