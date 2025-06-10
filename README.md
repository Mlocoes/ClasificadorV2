# ClasificadorV2

Sistema inteligente para organización y clasificación de medios (imágenes y vídeos) con reconocimiento automático de eventos mediante IA, extracción de metadatos y gestión web.

## 🚀 Características Principales

- **Clasificación automática**: Utiliza inteligencia artificial (CLIP) para clasificar eventos
- **Procesamiento completo**: Extracción de metadatos, generación de miniaturas, detección de ubicación
- **Archivos procesados**: Crea copias con nombre estandarizado basado en fecha y evento
- **Soporte amplio**: Formatos JPEG, PNG, HEIC, MP4, MOV y más
- **Interfaz moderna**: Diseño responsivo, vista grid/lista, actualización en tiempo real
- **Organización inteligente**: Búsqueda y filtrado por evento, nombre o ubicación

## 📋 Requisitos del Sistema

- Docker y Docker Compose
- 4GB RAM mínimo (8GB recomendados)
- 2GB espacio para instalación (más espacio para archivos de medios)
- Navegador web moderno (Chrome, Firefox, Safari, Edge)
- Conexión a internet para descarga inicial del modelo CLIP

## 🛠️ Instalación

### Mediante Docker (Recomendado)

1. **Clonar el repositorio**
```bash
git clone https://github.com/Mlocoes/ClasificadorV2.git
cd ClasificadorV2
```

2. **Iniciar los contenedores**
```bash
docker-compose up --build
```

3. **Acceder a la aplicación**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - API Backend: [http://localhost:8000/api/v1](http://localhost:8000/api/v1)

### Instalación Manual (Desarrollo)

1. **Backend (Python/FastAPI)**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows usar: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Frontend (React/TypeScript)**
```bash
cd frontend
npm install
npm run dev
```

## 📁 Estructura del Proyecto

```
ClasificadorV2/
├── backend/             # API en Python (FastAPI)
├── frontend/            # Interfaz web (React + TypeScript)
├── storage/             # Almacenamiento de archivos y base de datos
│   ├── uploads/         # Archivos originales
│   ├── thumbnails/      # Miniaturas generadas
│   ├── processed/       # Archivos con formato fecha-evento
│   └── db.sqlite3       # Base de datos SQLite
├── cache/               # Caché para modelos de IA
├── docker-compose.yml   # Configuración Docker
└── Docs/                # Documentación adicional
```

## 🔧 Uso Básico

1. **Subir archivos**: Arrastre imágenes o videos a la zona de carga o use el selector de archivos
2. **Visualizar contenido**: Alterne entre vista de tabla o cuadrícula
3. **Gestionar archivos**: Edite metadatos o elimine archivos usando los botones correspondientes
4. **Buscar contenido**: Utilice el buscador para filtrar por nombre o tipo de evento
5. **Acceder a archivos procesados**: Utilice los enlaces en la interfaz para acceder a las versiones procesadas con nombres estandarizados

## ⚙️ Configuración Avanzada

El sistema puede configurarse modificando las variables de entorno en `docker-compose.yml`:

- `VITE_API_URL`: URL de la API backend
- `VITE_MEDIA_URL`: URL base para acceso a medios
- `DB_PATH`: Ruta de la base de datos SQLite
- `TRANSFORMERS_CACHE`: Directorio de caché para modelos

## 🔄 Actualización Automática

La interfaz se actualiza automáticamente cuando:
- Se cargan nuevos archivos
- Se edita información de un archivo
- Se elimina un archivo

## 📝 Documentación Adicional

Para información más detallada, consulte:
- [Índice de Documentación](Docs/INDICE_DOCUMENTACION.md) - Catálogo completo de toda la documentación disponible
- [Documentación del Backend](backend/README.md)
- [Documentación del Frontend](frontend/README.md)
- [Flujo de Trabajo del Sistema](Docs/FLUJO_TRABAJO_SISTEMA.md)
- [Funcionalidad de Archivos Procesados](Docs/FUNCIONALIDAD_ARCHIVOS_PROCESADOS.md)

## 📄 Formato de Archivos Procesados

El sistema genera automáticamente copias de los archivos con nombres estandarizados siguiendo el formato:

```
YYYY-MM-DD-tipo-de-evento.extensión
```

Donde:
- `YYYY-MM-DD`: Fecha de creación de la imagen/video
- `tipo-de-evento`: Categoría del evento detectado (ej: boda, conferencia, fiesta)
- `extensión`: Extensión original del archivo (.jpg, .mp4, etc.)

Cuando existen varios archivos del mismo evento y fecha, el sistema añade automáticamente un índice numérico:

```
YYYY-MM-DD-tipo-de-evento-1.extensión
YYYY-MM-DD-tipo-de-evento-2.extensión
```

Los archivos procesados se almacenan en el directorio `/storage/processed/` y facilitan la organización y búsqueda posterior.

Para más información, consulte la [Documentación de Archivos Procesados](Docs/FUNCIONALIDAD_ARCHIVOS_PROCESADOS.md).
