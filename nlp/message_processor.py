"""
Procesador principal de mensajes que combina intent y date parsing
"""
from typing import Dict
from .intent_parser import IntentParser
from .date_parser import DateParser

class MessageProcessor:
    """Procesa mensajes combinando análisis de intención y fechas"""
    
    def __init__(self):
        self.intent_parser = IntentParser()
        self.date_parser = DateParser()
    
    def parse_message(self, message: str) -> Dict:
        """
        Analiza un mensaje completo
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            Dict con intent, fechas y otros datos extraídos
        """
        # Parsear intención
        intent_result = self.intent_parser.parse(message)
        
        # Parsear fechas si es relevante
        date_range = None
        if intent_result['intent'] in ['show_events', 'find_free_time']:
            date_range = self.date_parser.extract_date_range(message)
        
        # Extraer detalles según la intención
        details = {}
        if intent_result['intent'] == 'create_event':
            details = self.intent_parser.extract_event_details(message)
        elif intent_result['intent'] == 'update_event':
            details = self.intent_parser.extract_update_info(message)
        elif intent_result['intent'] == 'delete_event':
            details = self.intent_parser.extract_event_identifier(message)
        
        return {
            'intent': intent_result['intent'],
            'confidence': intent_result['confidence'],
            'date_range': date_range,
            'details': details,
            'original_message': message
        }