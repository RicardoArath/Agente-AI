"""
Configuración de logging para el AgentVerse Calendar Agent
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> None:
    """
    Configura el sistema de logging
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Archivo opcional para guardar logs
        format_string: Formato personalizado para los logs
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configurar el nivel
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configurar handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        # Crear directorio de logs si no existe
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    # Configurar logging básico
    logging.basicConfig(
        level=log_level,
        format=format_string,
        handlers=handlers,
        force=True
    )

def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado
    
    Args:
        name: Nombre del logger (normalmente __name__)
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)