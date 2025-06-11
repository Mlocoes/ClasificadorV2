# Scripts de diagnóstico para ClasificadorV2

Este directorio contiene scripts para probar, depurar y verificar el funcionamiento del sistema ClasificadorV2, especialmente la implementación del modelo YOLO.

## Scripts principales

### 1. Prueba de modelo YOLO

```bash
# Verificación mejorada del modelo YOLO
python test_yolo_standalone_v2.py [--image RUTA_IMAGEN] [--debug]
```

Este script prueba la integración del modelo YOLO de forma aislada. Incluye mejoras para la detección de errores y más información de depuración.

Opciones:
- `--image`: Ruta a una imagen específica para clasificar
- `--debug`: Activa información de depuración adicional

### 2. Verificación de recursos YOLO

```bash
# Comprobar si los archivos del modelo YOLO están disponibles para descargar
python check_yolo_resources.py [--test-download]
```

Comprueba si los recursos del modelo YOLO (configuración, pesos y clases) están disponibles en sus URLs originales y muestra información sobre su estado local.

Opciones:
- `--test-download`: Prueba la descarga de fragmentos pequeños para verificar el acceso completo

### 3. Verificación del entorno

```bash
# Verificar la configuración del entorno de desarrollo
python verify_environment.py
```

Comprueba la configuración del entorno de desarrollo, buscando problemas comunes que pueden afectar al funcionamiento del sistema.

### 4. Prueba de todos los modelos de IA

```bash
# Probar todos los modelos de IA disponibles
python test_ai_models_standalone.py [--image RUTA_IMAGEN] [--api-url URL_API] [--test-yolo] [--skip-api]
```

Prueba todos los modelos de IA disponibles (CLIP, OpenCV DNN, OpenCV YOLO) con la misma imagen para comparar resultados.

Opciones:
- `--image`: Ruta a una imagen específica para clasificar
- `--api-url`: URL base de la API (por defecto: http://localhost:8000/api/v1)
- `--test-yolo`: Incluir el modelo YOLO en las pruebas
- `--skip-api`: Omitir las pruebas de API

## Resolución de problemas comunes

### Errores de importación

Si experimentas errores de importación como `ModuleNotFoundError: No module named 'app'`:

1. Asegúrate de que el directorio `backend` está en el PYTHONPATH
2. Ejecuta el script `module_loader_v2.py` para diagnosticar problemas de importación:
   ```
   python module_loader_v2.py
   ```

### Problemas de permisos

Si hay errores de permisos al acceder a directorios como `/app`:

1. Ejecuta los scripts con permisos adecuados o como administrador si es necesario
2. Verifica que el usuario tiene permisos de lectura/escritura en los directorios relevantes

### Modelo YOLO no disponible

Si el modelo YOLO no puede descargarse:

1. Verifica tu conexión a internet
2. Ejecuta `check_yolo_resources.py` para comprobar si las URLs de los recursos están disponibles
3. Si las URLs han cambiado, actualiza el archivo `media_processor.py` con las nuevas URLs

## Contribuciones

Para contribuir a estos scripts de diagnóstico, por favor asegúrate de:

1. Mantener la compatibilidad con el sistema existente
2. Añadir manejo de errores adecuado
3. Proporcionar información de diagnóstico útil
4. Documentar cualquier cambio en este README
