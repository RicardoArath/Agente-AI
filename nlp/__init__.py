"""
Módulo de procesamiento de lenguaje natural (NLP)
Contiene parsers de intenciones, fechas y formateadores de respuestas
"""

from .intent_parser import IntentParser
from .date_parser import DateParser

__all__ = [
    'IntentParser',
    'DateParser'
]

__version__ = '1.0.0'