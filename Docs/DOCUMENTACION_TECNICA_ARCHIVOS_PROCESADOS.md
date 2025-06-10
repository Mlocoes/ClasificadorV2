# Documentación Técnica: Modelo de Datos y Archivos Procesados

## Introducción

Esta documentación describe la implementación técnica del procesamiento de archivos en ClasificadorV2, centrándose en la estructura del modelo de datos, la columna `processed_file_path` y el flujo de trabajo para generar y gestionar archivos con nombres estandarizados.

## Modelo de Datos

### Tabla `media`

La tabla `media` almacena toda la información relacionada con los archivos multimedia procesados por el sistema. El esquema incluye la columna `processed_file_path` que guarda la ruta relativa del archivo procesado.

```python
class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    thumbnail_path = Column(String, nullable=True)
    mime_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Metadatos
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration = Column(Float, nullable=True)  # Para videos
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    creation_date = Column(DateTime, nullable=True)
    
    # Archivo procesado con formato fecha-evento
    processed_file_path = Column(String, nullable=True)
    
    # Datos CLIP
    event_type = Column(String, nullable=True)
    event_confidence = Column(Float, nullable=True)
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

## Flujo de Procesamiento de Archivos

### 1. Carga del Archivo

Cuando un usuario sube un archivo multimedia, el sistema realiza los siguientes pasos:

```
Frontend → API (/api/v1/media/upload/) → MediaProcessor
```

### 2. Extracción de Metadatos

El servicio `MediaProcessor` extrae metadatos relevantes del archivo:

```python
# Extracción de fecha de creación
creation_date = extract_creation_date(file_path)

# Clasificación del evento mediante CLIP
event_type, confidence = classify_event(file_path)
```

### 3. Generación del Nombre Estandarizado

Se crea un nombre basado en la fecha de creación y el tipo de evento:

```python
# Formato: YYYY-MM-DD-evento.extension
date_str = creation_date.strftime("%Y-%m-%d")
base_name = f"{date_str}-{event_type}"
extension = os.path.splitext(original_filename)[1]
processed_name = f"{base_name}{extension}"
```

### 4. Manejo de Duplicados

El sistema verifica si ya existe un archivo con el mismo nombre y, en caso afirmativo, añade un índice numérico:

```python
# Si ya existe file.jpg, crear file-1.jpg, file-2.jpg, etc.
index = 1
while os.path.exists(os.path.join(processed_dir, processed_name)):
    processed_name = f"{base_name}-{index}{extension}"
    index += 1
```

### 5. Creación del Archivo Procesado

Se crea una copia del archivo original con el nuevo nombre:

```python
# Copiar el archivo con el nuevo nombre
shutil.copy2(
    original_file_path, 
    os.path.join(processed_dir, processed_name)
)
```

### 6. Actualización de la Base de Datos

Se guarda la ruta relativa del archivo procesado en la columna `processed_file_path`:

```python
# Actualizar el registro en la base de datos
media_item.processed_file_path = f"/processed/{processed_name}"
db.commit()
```

## Consideraciones Importantes

### Almacenamiento

- Los archivos procesados se almacenan en `/app/storage/processed/`
- Las rutas en la base de datos son relativas, comenzando con `/processed/`

### Acceso a los Archivos

- Los archivos son accesibles mediante la API en la ruta `/processed/{nombre_archivo}`
- El frontend puede construir URLs completas usando la base URL configurada

### Restricciones y Validaciones

- La columna `processed_file_path` es nullable, ya que podría haber casos donde el procesamiento falle
- El modelo de datos permite almacenar la ruta incluso si la clasificación del evento tiene baja confianza

## Ejemplos

### Ejemplo 1: Archivo con fecha y clasificación exitosa

- Archivo original: `IMG_20240605_123456.jpg` (creado el 5 de junio de 2024)
- Evento detectado: "conferencia" (confianza: 0.75)
- Archivo procesado: `2024-06-05-conferencia.jpg`
- Valor en BD: `/processed/2024-06-05-conferencia.jpg`

### Ejemplo 2: Múltiples archivos del mismo evento y fecha

- Archivos originales: `IMG_001.jpg`, `IMG_002.jpg` (ambos de una boda el 15/08/2023)
- Evento detectado: "boda"
- Archivos procesados: 
  - `2023-08-15-boda.jpg`
  - `2023-08-15-boda-1.jpg`
- Valores en BD:
  - `/processed/2023-08-15-boda.jpg`
  - `/processed/2023-08-15-boda-1.jpg`
