"""
Sistema de logging centralizado para la aplicación.
Permite un control consistente de los logs en toda la aplicación.
"""
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from app.core.config import settings

# Configuración de formatos
DEFAULT_FORMAT = "[%(levelname)s] [%(asctime)s] %(message)s"
JSON_FORMAT = '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'

class Logger:
    """
    Clase para manejar el logging centralizado de la aplicación.
    Proporciona métodos para diferentes niveles de log y configuración.
    """
    
    def __init__(self, name: str = "app"):
        """Inicializa el logger con un nombre específico."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.setup_handlers()
        
    def setup_handlers(self):
        """Configura los handlers para el logger."""
        # Comprobar si ya hay handlers para evitar duplicados
        if self.logger.handlers:
            return
            
        # Handler para la consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))
        self.logger.addHandler(console_handler)
        
        # Handler para archivo si está configurado
        if settings.LOG_TO_FILE:
            file_path = Path(settings.LOG_DIR) / "app.log"
            file_handler = logging.FileHandler(file_path)
            file_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))
            self.logger.addHandler(file_handler)
    
    def debug(self, msg: str, *args, **kwargs):
        """Registra un mensaje con nivel DEBUG."""
        self.logger.debug(msg, *args, **kwargs)
        
    def info(self, msg: str, *args, **kwargs):
        """Registra un mensaje con nivel INFO."""
        self.logger.info(msg, *args, **kwargs)
        
    def warning(self, msg: str, *args, **kwargs):
        """Registra un mensaje con nivel WARNING."""
        self.logger.warning(msg, *args, **kwargs)
        
    def error(self, msg: str, *args, **kwargs):
        """Registra un mensaje con nivel ERROR."""
        self.logger.error(msg, *args, **kwargs)
        
    def critical(self, msg: str, *args, **kwargs):
        """Registra un mensaje con nivel CRITICAL."""
        self.logger.critical(msg, *args, **kwargs)
        
    def exception(self, msg: str, *args, exc_info=True, **kwargs):
        """Registra un mensaje con nivel ERROR incluyendo información de la excepción."""
        self.logger.exception(msg, *args, exc_info=exc_info, **kwargs)
        
    def log_request(self, request: Any, response_status: int = None):
        """Registra información de una petición HTTP."""
        client = getattr(request, "client", None)
        client_host = getattr(client, "host", "unknown")
        client_port = getattr(client, "port", 0)
        
        method = request.method
        url = str(request.url)
        
        status_text = f" [Status: {response_status}]" if response_status else ""
        self.info(f"Request: {method} {url} from {client_host}:{client_port}{status_text}")
        
# Instancia global del logger
logger = Logger()
