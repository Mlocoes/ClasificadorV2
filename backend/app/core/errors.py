"""
Manejador centralizado de errores para la aplicación.
Define excepciones personalizadas y manejadores para errores HTTP.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.logger import logger

class AppException(Exception):
    """
    Excepción base para todas las excepciones de la aplicación.
    Permite un manejo consistente de errores.
    """
    def __init__(
        self, 
        message: str = "Se produjo un error interno", 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: dict = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)
        
class NotFoundException(AppException):
    """Excepción para recursos no encontrados."""
    def __init__(self, message: str = "Recurso no encontrado", detail: dict = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, detail)
        
class ValidationException(AppException):
    """Excepción para errores de validación."""
    def __init__(self, message: str = "Error de validación de datos", detail: dict = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, detail)
        
class DatabaseException(AppException):
    """Excepción para errores de base de datos."""
    def __init__(self, message: str = "Error en la base de datos", detail: dict = None):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, detail)
        
class UnauthorizedException(AppException):
    """Excepción para errores de autenticación."""
    def __init__(self, message: str = "No autorizado", detail: dict = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, detail)
        
class ForbiddenException(AppException):
    """Excepción para errores de permisos."""
    def __init__(self, message: str = "Acceso prohibido", detail: dict = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, detail)

async def app_exception_handler(request: Request, exc: AppException):
    """Manejador para excepciones personalizadas de la aplicación."""
    logger.error(f"AppException: {exc.message} - Status {exc.status_code}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "detail": exc.detail or {}
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejador para errores de validación de FastAPI."""
    errors = exc.errors()
    logger.warning(f"Validation Error: {errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Error de validación en los datos de entrada",
            "detail": {"errors": errors}
        }
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Manejador para errores de SQLAlchemy."""
    logger.error(f"Database Error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Error en la base de datos",
            "detail": {"error": str(exc)}
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Manejador para excepciones no manejadas."""
    logger.exception(f"Unhandled Exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Se produjo un error interno",
            "detail": {"error": str(exc)}
        }
    )

def register_exception_handlers(app):
    """Registra todos los manejadores de excepciones en la aplicación."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
