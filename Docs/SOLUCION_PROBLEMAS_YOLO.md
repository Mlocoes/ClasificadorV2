# SOLUCIÓN DE PROBLEMAS DEL MODELO YOLO

Este documento describe los problemas más comunes encontrados al implementar y probar el modelo YOLO en ClasificadorV2 y sus soluciones.

## 1. Problema de rutas hardcoded en la configuración

### Síntoma
Error de permisos al intentar acceder al directorio `/app`:

```
PermissionError: [Errno 13] Permission denied: '/app'
```

### Causa
La configuración en `backend/app/core/config.py` utiliza rutas absolutas hardcoded como `/app/storage` que asumen un entorno de Docker, pero que no son válidas en un entorno de desarrollo local.

### Solución
Hay dos enfoques para solucionar este problema:

#### Solución temporal (scripts)
Utilizar el script `fix_config_paths.py` que modifica dinámicamente las configuraciones en tiempo de ejecución:

```bash
python scripts/fix_config_paths.py
```

#### Solución permanente (modificación del código)
Modificar el archivo `backend/app/core/config.py` para utilizar rutas relativas o configurables:

```python
# Cambiar esto:
STORAGE_DIR: Path = Path("/app/storage")

# Por esto:
base_dir = os.getenv("CLASIFICADOR_BASE_DIR", str(Path(__file__).parent.parent.parent.parent))
STORAGE_DIR: Path = Path(base_dir) / "storage"
```

## 2. Errores al cargar el modelo YOLO

### Síntoma
Mensajes de error como:
- "No se pudo cargar el modelo YOLO"
- "Error durante la detección"

### Causas posibles
1. Archivos del modelo no descargados correctamente
2. Ruta a los archivos del modelo incorrecta
3. Incompatibilidad de versiones de OpenCV

### Solución
Utilizar el script `check_yolo_resources.py` para verificar la disponibilidad y descarga de los archivos:

```bash
python scripts/check_yolo_resources.py --test-download
```

Luego utilizar el script `test_yolo_minimal.py` para probar específicamente la carga del modelo:

```bash
python scripts/test_yolo_minimal.py
```

## 3. Problemas de importación de módulos

### Síntoma
Errores como:
- `ModuleNotFoundError: No module named 'app'`
- `ImportError: cannot import name 'X' from 'app.Y'`

### Causas
1. PYTHONPATH no configurado correctamente
2. Archivos `__init__.py` faltantes
3. Estructura de directorios incorrecta

### Solución
Utilizar el script mejorado de carga de módulos:

```bash
python scripts/module_loader_v2.py
```

También puedes configurar el PYTHONPATH manualmente antes de ejecutar los scripts:

```bash
PYTHONPATH=/home/mloco/Escritorio/ClasificadorV2/backend python scripts/test_yolo_unified.py
```

## 4. Pruebas unificadas

Para una prueba completa que incluya corrección de rutas y manejo de errores mejorado, utiliza:

```bash
python scripts/test_yolo_unified.py [--image RUTA_IMAGEN] [--conf UMBRAL]
```

Este script:
1. Corrige las rutas en la configuración
2. Carga el modelo YOLO
3. Realiza detección de objetos
4. Clasifica el tipo de evento
5. Muestra un resumen de resultados

## 5. Verificación del entorno

Para una verificación completa del entorno y los permisos, utiliza:

```bash
python scripts/check_permissions.py
```

Este script comprobará los permisos y la existencia de todos los directorios y archivos necesarios.

## 6. Soluciones adicionales

### Errores de permisos
Si continúas experimentando errores de permisos:

```bash
sudo mkdir -p /app/storage/models/opencv_dnn
sudo chown -R $USER:$USER /app
```

### Problemas con las descargas
Si los archivos del modelo no se pueden descargar automáticamente, puedes hacerlo manualmente:

1. Descarga el archivo de configuración: https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg
2. Descarga el archivo de pesos: https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights
3. Descarga el archivo de clases: https://raw.githubusercontent.com/AlexeyAB/darknet/master/data/coco.names

Luego coloca estos archivos en la carpeta `/home/mloco/Escritorio/ClasificadorV2/storage/models/opencv_dnn/`
