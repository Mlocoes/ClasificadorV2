"""
Middleware para el logging de peticiones HTTP.
Registra información de las peticiones entrantes y salientes.
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.logger import logger

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware que registra información sobre cada solicitud HTTP.
    Incluye tiempo de procesamiento, método, ruta, estado de respuesta.
    """
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Procesa la solicitud HTTP y registra información de logging."""
        start_time = time.time()
        
        # Extraer información básica de la solicitud
        method = request.method
        path = request.url.path
        
        # Ejecutar el siguiente middleware/endpoint
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log de información de la respuesta
            status_code = response.status_code
            logger.info(
                f"{method} {path} → {status_code} [Tiempo: {process_time:.3f}s]"
            )
            
            # Añadir header con el tiempo de procesamiento
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
        except Exception as exc:
            # En caso de error, registrar la excepción
            process_time = time.time() - start_time
            logger.exception(
                f"Error en {method} {path} [Tiempo: {process_time:.3f}s]: {str(exc)}"
            )
            raise
