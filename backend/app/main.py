from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import media

# Crear tablas de la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear y asegurar directorios de almacenamiento
directories = [settings.STORAGE_DIR, settings.UPLOADS_DIR, settings.THUMBNAILS_DIR]
for directory in directories:
    try:
        directory.mkdir(parents=True, exist_ok=True)
        os.chmod(str(directory), 0o777)
        print(f"Directorio {directory} creado y permisos establecidos")
    except Exception as e:
        print(f"Error al crear o establecer permisos en el directorio {directory}: {e}")
        raise
    except Exception as e:
        print(f"Error al crear o establecer permisos en el directorio {directory}: {e}")
        raise

# Montar directorios estáticos
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")
app.mount("/thumbnails", StaticFiles(directory=str(settings.THUMBNAILS_DIR)), name="thumbnails")

# Registrar rutas
app.include_router(media.router, prefix=f"{settings.API_V1_STR}/media", tags=["media"])

@app.get("/")
async def root():
    return {"message": f"Bienvenido a {settings.PROJECT_NAME}"}