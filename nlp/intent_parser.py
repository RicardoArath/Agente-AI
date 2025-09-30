"""Parser de intenciones - versión simplificada"""
from typing import Dict
from config.settings import settings

class IntentParser:
    def parse(self, message: str) -> Dict:
        message_lower = message.lower()
        
        for intent, keywords in settings.INTENT_KEYWORDS.items():
            if any(keyword in message_lower for keyword in keywords):
                return {
                    'intent': intent,
                    'confidence': 0.8,
                    'original_message': message
                }
        
        return {
            'intent': 'unknown',
            'confidence': 0.0,
            'original_message': message
        }
    
    def extract_event_details(self, message: str) -> Dict:
        # Implementación básica - retorna diccionario vacío por ahora
        return {}
    
    def extract_event_identifier(self, message: str) -> Dict:
        return {}
    
    def extract_update_info(self, message: str) -> Dict:
        return {}
    
    def extract_duration(self, message: str) -> int:
        if "30 minutos" in message.lower():
            return 30
        return 60