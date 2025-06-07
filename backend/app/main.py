from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
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

# Añadir compresión gzip
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configurar CORS para permitir acceso desde cualquier origen en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=False,  # No usar credenciales para permitir "*"
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    max_age=3600  # Cache preflight por 1 hora
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

# Montar directorios estáticos
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")
app.mount("/thumbnails", StaticFiles(directory=str(settings.THUMBNAILS_DIR)), name="thumbnails")

# Registrar rutas
app.include_router(media.router, prefix=f"{settings.API_V1_STR}/media", tags=["media"])

@app.get("/health")
async def health_check():
    """
    Endpoint para verificar la salud del servicio.
    Verifica:
    - Acceso a directorios
    - Conexión a la base de datos
    - Estado general del servicio
    """
    try:
        # Verificar directorios
        directories = [settings.STORAGE_DIR, settings.UPLOADS_DIR, settings.THUMBNAILS_DIR]
        for directory in directories:
            if not directory.exists():
                return {"status": "error", "detail": f"Directorio {directory} no existe"}
            
        # Verificar base de datos
        try:
            # Intentar una consulta simple
            with engine.connect() as conn:
                conn.execute("SELECT 1")
        except Exception as e:
            return {"status": "error", "detail": f"Error de base de datos: {str(e)}"}
        
        return {
            "status": "healthy",
            "version": "2.0.0",
            "storage": {
                "uploads": str(settings.UPLOADS_DIR),
                "thumbnails": str(settings.THUMBNAILS_DIR)
            }
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/")
async def root():
    return {"message": f"Bienvenido a {settings.PROJECT_NAME}"}