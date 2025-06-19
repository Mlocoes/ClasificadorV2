from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
import os
import time
from pathlib import Path

from app.core.config import settings
from app.core.database import engine, Base, get_db, SessionLocal
from app.core.logger import logger
from app.core.errors import register_exception_handlers
from app.core.middlewares import RequestLoggingMiddleware
from app.api.v1 import router as api_router

# Configurar directorio de logs si está habilitado
if settings.LOG_TO_FILE:
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)

# Cargar configuración desde archivo si existe
try:
    settings.load_config_from_file()
    logger.info(f"Configuración cargada. Modelo de IA activo: {settings.AI_MODEL}")
except Exception as e:
    logger.error(f"Error al cargar la configuración: {e}")

# Crear tablas de la base de datos
start_time = time.time()
Base.metadata.create_all(bind=engine)
logger.info(f"Tablas de base de datos creadas en {time.time() - start_time:.2f}s")

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para gestión de archivos multimedia con clasificación automática",
    version="2.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# Registrar manejadores de excepciones
register_exception_handlers(app)

# Añadir middleware para logging de peticiones
app.add_middleware(RequestLoggingMiddleware)

# Añadir compresión gzip
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configurar CORS para permitir acceso desde cualquier origen en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=False,  # No usar credenciales para permitir "*"
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600  # Cache preflight por 1 hora
)

# Crear y asegurar directorios de almacenamiento
directories = [
    settings.STORAGE_DIR, 
    settings.UPLOADS_DIR, 
    settings.THUMBNAILS_DIR, 
    settings.PROCESSED_DIR,
    settings.CONFIG_DIR,
    settings.LOG_DIR
]
for directory in directories:
    try:
        directory.mkdir(parents=True, exist_ok=True)
        os.chmod(str(directory), 0o775)  # Permisos más seguros
        logger.info(f"Directorio {directory} creado y permisos establecidos")
    except Exception as e:
        logger.critical(f"Error al crear o establecer permisos en el directorio {directory}: {e}")
        raise

# Montar directorios estáticos
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")
app.mount("/thumbnails", StaticFiles(directory=str(settings.THUMBNAILS_DIR)), name="thumbnails")
app.mount("/processed", StaticFiles(directory=str(settings.PROCESSED_DIR)), name="processed")

# Registrar rutas
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    """
    Endpoint para verificar que la API está en funcionamiento.
    
    Comprueba:
    - Estado del servidor
    - Acceso a directorios de almacenamiento
    """
    try:
        # Verificar directorios
        directories = [settings.STORAGE_DIR, settings.UPLOADS_DIR, settings.THUMBNAILS_DIR]
        for directory in directories:
            if not directory.exists():
                return {"status": "error", "detail": f"Directorio {directory} no existe"}
        
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