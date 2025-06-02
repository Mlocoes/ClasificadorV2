# Backend ClasificadorV2

API en Python (FastAPI) para procesamiento de fotos/videos, extracción de metadatos, clasificación de eventos con IA (CLIP), generación de miniaturas y gestión de base de datos.

## Estructura sugerida
- app/
  - main.py (punto de entrada FastAPI)
  - api/ (rutas)
  - core/ (configuración)
  - crud/ (operaciones DB)
  - models/ (modelos ORM)
  - schemas/ (pydantic)
  - services/ (procesamiento, IA, miniaturas)
- requirements.txt
- Dockerfile

## Instalación local

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Notas
- La base de datos por defecto es SQLite, ubicada en `../storage/db.sqlite3`.
- Los archivos subidos y miniaturas se almacenan en `../storage/`.
- El modelo CLIP se descarga automáticamente la primera vez.
