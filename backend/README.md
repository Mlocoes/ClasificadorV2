# Documentación del Backend - ClasificadorV2

## Introducción

El backend de ClasificadorV2 es un servicio API RESTful construido con FastAPI que proporciona todas las funcionalidades de procesamiento de medios, incluyendo:
- Gestión de archivos (subida, descarga, actualización, eliminación)
- Procesamiento inteligente de imágenes y videos
- Extracción automática de metadatos (EXIF, GPS, dimensiones)
- Clasificación de eventos mediante IA (utilizando CLIP)
- Generación de miniaturas optimizadas
- Base de datos SQLite para almacenamiento persistente

## Arquitectura del Backend

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── media.py       # Endpoints relacionados con medios
│   ├── core/
│   │   ├── config.py          # Configuración centralizada
│   │   └── database.py        # Configuración de la base de datos
│   ├── crud/
│   │   └── media.py           # Operaciones CRUD para medios
│   ├── models/
│   │   └── media.py           # Modelos ORM SQLAlchemy
│   ├── schemas/
│   │   └── media.py           # Esquemas Pydantic para validación
│   ├── services/
│   │   └── media_processor.py # Servicio de procesamiento de medios
│   └── main.py                # Punto de entrada FastAPI
├── Dockerfile                 # Configuración para Docker
├── healthcheck.py             # Script de comprobación de salud
└── requirements.txt           # Dependencias del proyecto
```

## Componentes Principales

### 1. API (app/api/v1/media.py)

**Endpoints principales:**

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/upload/` | POST | Subida de archivos multimedia con procesado automático |
| `/` | GET | Listado de todos los medios disponibles |
| `/{id}` | GET | Obtener datos de un medio específico |
| `/{id}` | DELETE | Eliminar un medio específico |
| `/{id}` | PATCH | Actualizar datos de un medio específico |

**Funcionalidades destacadas:**

- **Subida inteligente**: Validación de archivos, detección de formato y sanitización de nombres
- **Procesamiento automático**: Uso asíncrono del MediaProcessor para no bloquear la respuesta
- **Paginación**: Soporte para paginación en listados con parámetros limit/skip
- **Filtrado**: Búsqueda por tipo de evento, rango de fechas y otros criterios

### 2. Modelos y Esquemas (app/models/, app/schemas/)

**Media**: Representa un archivo multimedia en el sistema con propiedades como:

- Datos básicos: id, filename, file_path, file_type, file_size
- Metadatos: width, height, creation_date, uploaded_at
- Datos geográficos: latitude, longitude
- Clasificación: event_type, event_confidence
- Referencias: thumbnail_path, processed_file_path

**Esquemas Pydantic**:
- `MediaCreate`: Validación para creación
- `MediaUpdate`: Validación para actualización parcial
- `Media`: Representación completa para respuestas API

### 3. Servicios (app/services/)

**MediaProcessor**: Componente principal que implementa:

- **Procesamiento de imágenes**:
  - Extracción de metadatos EXIF
  - Soporte para formato HEIC/HEIF
  - Corrección automática de orientación
  - Extracción de coordenadas GPS

- **Procesamiento de vídeos**:
  - Extracción de datos como dimensiones y duración
  - Captura de fotogramas para miniaturas
  - Procesamiento optimizado con OpenCV

- **Generación de miniaturas**:
  - Estrategias configurables (dedicated_dir, subdir, base_dir)
  - Preservación de proporción y calidad
  - Gestión eficiente de caché

- **Procesamiento de archivos estandarizados**:
  - Generación automática de copias con nombres estandarizados
  - Formato basado en fecha y evento detectado (YYYY-MM-DD-evento.ext)
  - Manejo inteligente de nombres duplicados con índices automáticos
  - Almacenamiento en directorio específico (/storage/processed/)

- **Clasificación de eventos (IA)**:
  - Modelo CLIP para clasificación de contenido visual
  - Categorización multilingüe (español e inglés)
  - Medición de confianza para cada predicción
  - Lista predefinida de eventos detectables:
    - Eventos deportivos
    - Conciertos y espectáculos
    - Bodas y ceremonias
    - Reuniones familiares
    - Conferencias y eventos educativos
    - Y muchos más...

### 4. Configuración (app/core/)

**Settings (config.py)**:
- Rutas de almacenamiento configurables
- Parámetros del sistema y entorno
- Configuraciones de acceso y seguridad

**Database (database.py)**:
- Conexión SQLite optimizada
- Sesiones y motores SQLAlchemy
- Migración automática de esquemas

### 5. Aspectos de Seguridad

- **CORS**: Configurado para permitir acceso seguro desde el frontend
- **Validación**: Comprobación estricta de tipos y formatos con Pydantic
- **Sanitización**: Limpieza de nombres de archivo y contenido para prevenir vulnerabilidades
- **Manejo de errores**: Gestión robusta de excepciones y respuestas de error informativas

## Instalación y Despliegue

### Requisitos

- Python 3.10+
- Dependencias en `requirements.txt`
- Espacio de almacenamiento para medios

### Instalación Local (Desarrollo)

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Despliegue con Docker

```bash
# Construir imagen
docker build -t clasificadorv2-backend .

# Ejecutar contenedor
docker run -p 8000:8000 -v ./storage:/app/storage clasificadorv2-backend
```

## Consideraciones Técnicas

- **Rendimiento**: Optimizado para gestionar operaciones asíncronas
- **Escalabilidad**: Diseñado para manejar grandes volúmenes de archivos
- **Extensibilidad**: Arquitectura modular para facilitar nuevas características
