"""
Módulo de procesamiento de lenguaje natural (NLP)
"""

from .intent_parser import IntentParser
from .date_parser import DateParser
from .message_processor import MessageProcessor

__all__ = [
    'IntentParser',
    'DateParser',
    'MessageProcessor'  
]

__version__ = '1.0.0'