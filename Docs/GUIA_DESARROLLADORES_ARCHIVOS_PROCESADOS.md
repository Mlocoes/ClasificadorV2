# Guía para Desarrolladores: Archivos Procesados

Esta guía proporciona información detallada para desarrolladores que necesiten trabajar con la funcionalidad de archivos procesados en ClasificadorV2.

## Estructura de Datos

### Modelo de Base de Datos

La columna `processed_file_path` en la tabla `media` almacena la ruta relativa del archivo procesado:

```python
class Media(Base):
    # ... otras columnas ...
    
    # Archivo procesado con formato fecha-evento
    processed_file_path = Column(String, nullable=True)
    
    # ... otras columnas ...
```

### Formato de Ruta

Las rutas almacenadas siguen este patrón:
- Siempre comienzan con `/processed/`
- Siguen con el nombre del archivo en formato `YYYY-MM-DD-tipo-evento[-n].extensión`
- Ejemplo: `/processed/2025-06-10-boda-1.jpg`

## Acceso a los Archivos Procesados

### Desde el Backend

Para acceder a los archivos procesados desde el código del backend:

```python
from app.core.config import settings

def get_absolute_processed_path(media_item):
    """Convierte la ruta relativa en absoluta para acceso al archivo"""
    if not media_item.processed_file_path:
        return None
        
    # La ruta relativa comienza con /processed/ pero sin el slash inicial
    relative_path = media_item.processed_file_path.lstrip('/')
    return settings.STORAGE_DIR / relative_path
```

### Desde la API

Los archivos procesados están disponibles a través de la API mediante la ruta base del servidor:

```
GET http://servidor:puerto/{processed_file_path}
```

Por ejemplo:
```
GET http://localhost:8000/processed/2025-06-10-boda-1.jpg
```

## Modificación del Comportamiento

### Cambiar el Formato del Nombre

Si necesitas modificar el formato del nombre de los archivos procesados, debes actualizar la función correspondiente en el servicio `MediaProcessor`:

```python
# En app/services/media_processor.py

def _generate_processed_filename(self, media_item, event_type):
    # Obtener fecha
    date_str = media_item.creation_date.strftime("%Y-%m-%d") if media_item.creation_date else datetime.now().strftime("%Y-%m-%d")
    
    # Obtener extensión
    _, extension = os.path.splitext(media_item.filename)
    
    # Crear nombre base
    base_name = f"{date_str}-{event_type}"
    
    # Si deseas cambiar el formato, modifica la línea anterior
    # Por ejemplo, para incluir la hora:
    # date_time_str = media_item.creation_date.strftime("%Y-%m-%d-%H%M") if media_item.creation_date else datetime.now().strftime("%Y-%m-%d-%H%M")
    # base_name = f"{date_time_str}-{event_type}"
    
    return base_name, extension
```

### Personalizar el Directorio de Almacenamiento

Para cambiar dónde se guardan los archivos procesados:

1. Modifica la configuración en `app/core/config.py`:

```python
class Settings(BaseSettings):
    # ... otras configuraciones ...
    
    # Directorio para archivos procesados
    PROCESSED_DIR: Path = STORAGE_DIR / "processed"
    
    # Para cambiar a otro directorio, modifica la línea anterior
    # Por ejemplo:
    # PROCESSED_DIR: Path = STORAGE_DIR / "standardized"
```

2. Actualiza también las referencias en el código que utiliza esta configuración.

## Procesamiento Manual

Si necesitas procesar manualmente un archivo existente:

```python
from app.services.media_processor import MediaProcessor
from app.crud.media import get_media

# Inicializar el procesador
processor = MediaProcessor()

# Obtener el elemento de media
with SessionLocal() as db:
    media_item = get_media(db, media_id=123)
    
    # Procesar y crear archivo estandarizado
    success = processor.create_processed_file(db, media_item)
    
    if success:
        print(f"Archivo procesado creado en: {media_item.processed_file_path}")
    else:
        print("Error al crear archivo procesado")
```

## Depuración y Solución de Problemas

### Logs de Procesamiento

El servicio `MediaProcessor` registra información detallada durante el procesamiento:

```
DEBUG: Evento predicho - boda (0.75)
DEBUG: Creando copia procesada del archivo con formato fecha-evento
DEBUG: Copiando archivo a: /app/storage/processed/2025-06-10-boda.jpg
DEBUG: Copia procesada creada exitosamente en: /processed/2025-06-10-boda.jpg
DEBUG: Guardando cambios en BD
```

### Problemas Comunes

1. **Archivo procesado no se crea**:
   - Verificar permisos en el directorio `/storage/processed/`
   - Comprobar si hay suficiente espacio en disco
   - Revisar logs para errores específicos

2. **Nombre incorrecto o fecha incorrecta**:
   - Verificar que los metadatos de fecha se extrajeron correctamente
   - Comprobar si hay errores en la lógica de formateo de fechas

3. **Conflicto con archivos existentes**:
   - El sistema debería manejar automáticamente las colisiones añadiendo sufijos numéricos
   - Si hay problemas, verificar la lógica de incremento de índices

4. **Ruta no se guarda en la base de datos**:
   - Confirmar que la transacción de base de datos se completa correctamente
   - Verificar si hay errores en la actualización del registro

## Pruebas Unitarias

Ejemplo de prueba para la funcionalidad de archivos procesados:

```python
def test_processed_file_creation():
    # Configurar
    processor = MediaProcessor()
    db = MagicMock()
    media_item = Media(
        id=1,
        filename="test.jpg",
        file_path="/uploads/test.jpg",
        mime_type="image/jpeg",
        file_size=1024,
        creation_date=datetime(2025, 6, 10, 12, 0, 0),
        event_type="boda",
        event_confidence=0.75
    )
    
    # Ejecutar
    result = processor.create_processed_file(db, media_item)
    
    # Verificar
    assert result is True
    assert media_item.processed_file_path is not None
    assert "2025-06-10-boda" in media_item.processed_file_path
    db.commit.assert_called_once()
```

## Integraciones y Extensiones

### Exportación de Archivos Procesados

Si deseas implementar una funcionalidad para exportar archivos procesados:

```python
def export_processed_files(media_items, target_dir):
    """Exporta una colección de archivos procesados a un directorio externo"""
    os.makedirs(target_dir, exist_ok=True)
    
    exported_files = []
    for item in media_items:
        if item.processed_file_path:
            source_path = settings.STORAGE_DIR / item.processed_file_path.lstrip('/')
            target_path = os.path.join(target_dir, os.path.basename(item.processed_file_path))
            
            if os.path.exists(source_path):
                shutil.copy2(source_path, target_path)
                exported_files.append(target_path)
    
    return exported_files
```

### Procesamiento por Lotes

Para procesar múltiples archivos existentes:

```python
def batch_process_files(db, media_ids):
    """Procesa un lote de archivos existentes"""
    processor = MediaProcessor()
    results = {"success": [], "failed": []}
    
    for media_id in media_ids:
        media_item = get_media(db, media_id)
        if media_item:
            success = processor.create_processed_file(db, media_item)
            if success:
                results["success"].append(media_id)
            else:
                results["failed"].append(media_id)
    
    return results
```
