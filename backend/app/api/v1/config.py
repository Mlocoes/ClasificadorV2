from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Literal, Dict
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

router = APIRouter()

class AIModelConfig(BaseModel):
    model: Literal["clip", "opencv_dnn", "opencv_yolo"]

class ConfigResponse(BaseModel):
    message: str
    current_settings: Dict

@router.get("/", response_model=ConfigResponse)
def get_config():
    """Obtiene la configuración actual del sistema."""
    current_settings = {
        "ai_model": settings.AI_MODEL
    }
    return {
        "message": "Configuración actual del sistema",
        "current_settings": current_settings
    }

@router.post("/ai-model", response_model=ConfigResponse)
def set_ai_model(config: AIModelConfig):
    """Establece el modelo de IA a utilizar para la clasificación de imágenes."""
    try:
        # Validar el modelo seleccionado
        if config.model not in ["clip", "opencv_dnn", "opencv_yolo"]:
            raise ValueError(f"Modelo de IA no válido: {config.model}")
            
        # Actualizar la configuración en memoria
        settings.AI_MODEL = config.model
        
        # Guardar la configuración en archivo para persistencia
        save_result = settings.save_config_to_file()
        
        if save_result:
            message = f"Modelo de IA cambiado a {config.model} y configuración guardada"
        else:
            message = f"Modelo de IA cambiado a {config.model} pero no se pudo guardar la configuración"
        
        return {
            "message": message,
            "current_settings": {"ai_model": settings.AI_MODEL}
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cambiar el modelo de IA: {str(e)}")
