"""
Utilidades para validación y manejo de archivos multimedia.
"""
import os
import magic
import tempfile
import shutil
from pathlib import Path
from typing import Set, List, Tuple, Optional
from fastapi import UploadFile, HTTPException, status

from app.core.config import settings
from app.core.logger import logger

# Configuración de tipos MIME permitidos
ALLOWED_IMAGE_MIMES: Set[str] = {
    "image/jpeg", 
    "image/png", 
    "image/heic", 
    "image/heif"
}

ALLOWED_VIDEO_MIMES: Set[str] = {
    "video/mp4", 
    "video/quicktime", 
    "video/x-msvideo"
}

ALLOWED_MIMES: Set[str] = ALLOWED_IMAGE_MIMES.union(ALLOWED_VIDEO_MIMES)

# Tamaño máximo de archivo (en bytes)
MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB

class FileValidator:
    """
    Clase para validar y procesar archivos multimedia.
    """
    
    @staticmethod
    async def validate_file(file: UploadFile) -> Tuple[str, str]:
        """
        Valida un archivo subido y devuelve su tipo MIME real.
        
        Parámetros:
        - file: El archivo a validar
        
        Returns:
        - Tuple[str, str]: El tipo MIME real y el tipo de archivo (image/video)
        
        Raises:
        - HTTPException: Si el archivo no pasa las validaciones
        """
        # Comprobar tamaño (primeros 100 bytes para determinar tipo)
        first_bytes = await file.read(100)
        await file.seek(0)  # Regresar al inicio del archivo
        
        # Verificar que no esté vacío
        if not first_bytes:
            logger.warning(f"Archivo vacío: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo está vacío"
            )
            
        # Usar python-magic para determinar el tipo MIME real
        mime_type = magic.from_buffer(first_bytes, mime=True)
        
        # Validar tipo de archivo
        if mime_type not in ALLOWED_MIMES:
            logger.warning(f"Tipo de archivo no permitido: {mime_type}, archivo: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de archivo {mime_type} no permitido. Tipos permitidos: {', '.join(ALLOWED_MIMES)}"
            )
            
        # Determinar categoría del archivo
        file_type = "image" if mime_type in ALLOWED_IMAGE_MIMES else "video"
        
        return mime_type, file_type
        
    @staticmethod
    async def save_upload_file(file: UploadFile, destination: Path) -> Path:
        """
        Guarda un archivo subido en el destino especificado.
        
        Parámetros:
        - file: El archivo a guardar
        - destination: El directorio de destino
        
        Returns:
        - Path: La ruta al archivo guardado
        
        Raises:
        - HTTPException: Si hay un error al guardar el archivo
        """
        try:
            # Crear el directorio destino si no existe
            destination.mkdir(parents=True, exist_ok=True)
            
            # Generar ruta final
            file_path = destination / file.filename
            
            # Asegurarse de no sobrescribir un archivo existente
            if file_path.exists():
                base_name = file_path.stem
                extension = file_path.suffix
                counter = 1
                
                while file_path.exists():
                    new_name = f"{base_name}_{counter}{extension}"
                    file_path = destination / new_name
                    counter += 1
            
            # Escribir el archivo
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            logger.info(f"Archivo guardado en {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error al guardar el archivo {file.filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al guardar el archivo: {str(e)}"
            )
