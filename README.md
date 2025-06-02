# ClasificadorV2

Organizador inteligente de fotos y videos con reconocimiento de eventos mediante IA (CLIP), extracción de metadatos y gestión web.

## Estructura del proyecto

- `backend/` — API en Python (FastAPI), extracción de metadatos, IA CLIP, miniaturas, base de datos SQLite.
- `frontend/` — Interfaz web (React), subida, edición y eliminación de archivos, visualización en tiempo real.
- `docker-compose.yml` — Orquestación de servicios.
- `storage/` — Almacenamiento de archivos subidos y miniaturas.

## Instalación rápida

1. Instala Docker y Docker Compose en Ubuntu 24.04 Desktop.
2. Clona este repositorio.
3. Ejecuta:

```bash
docker-compose up --build
```

4. Accede a la interfaz web en http://localhost:3000

## Funcionalidades
- Subida de fotos/videos (múltiples formatos)
- Extracción automática de metadatos y sidecar
- Clasificación de evento con IA (CLIP)
- Miniaturas automáticas
- Edición y eliminación de archivos
- Actualización en tiempo real

## Dependencias principales
- Python 3.10+
- FastAPI
- SQLite
- React
- Docker & Docker Compose
- OpenAI CLIP (vía HuggingFace)

---

Para detalles técnicos, revisa los README en `backend/` y `frontend/`.
