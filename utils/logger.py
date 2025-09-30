"""
Sistema de logging configurado para el Calendar Agent
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

try:
    import colorlog
    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False

from config.settings import settings

# Logger global configurado
_loggers = {}

def setup_logging(log_level: Optional[str] = None):
    """
    Configura el sistema de logging global
    
    Args:
        log_level: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    level = log_level or settings.LOG_LEVEL
    
    # Configurar nivel de logging
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configurar el root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Formato de log
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Handler para consola con colores (si está disponible)
    if HAS_COLORLOG:
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        
        color_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s',
            datefmt=date_format,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(color_formatter)
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_formatter = logging.Formatter(log_format, datefmt=date_format)
        console_handler.setFormatter(console_formatter)
    
    root_logger.addHandler(console_handler)
    
    # Handler para archivo (con rotación)
    try:
        file_handler = RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        root_logger.warning(f"No se pudo crear archivo de log: {e}")
    
    # Reducir verbosidad de librerías externas
    logging.getLogger('googleapiclient').setLevel(logging.WARNING)
    logging.getLogger('google.auth').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    root_logger.info(f"Sistema de logging inicializado - Nivel: {level}")

def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado para un módulo específico
    
    Args:
        name: Nombre del módulo (usualmente __name__)
        
    Returns:
        Logger configurado
    """
    if name not in _loggers:
        logger = logging.getLogger(name)
        _loggers[name] = logger
    
    return _loggers[name]

# Clase auxiliar para contexto de logging
class LogContext:
    """Contexto para logging temporal"""
    
    def __init__(self, logger: logging.Logger, level: int, message: str):
        self.logger = logger
        self.level = level
        self.message = message
    
    def __enter__(self):
        self.logger.log(self.level, f"Iniciando: {self.message}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.logger.log(self.level, f"Completado: {self.message}")
        else:
            self.logger.error(f"Error en: {self.message} - {exc_val}")
        return False

# Configurar logging al importar el módulo
if __name__ != "__main__":
    setup_logging()