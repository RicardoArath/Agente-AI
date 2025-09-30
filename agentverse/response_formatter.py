"""
Formateador de respuestas para AgentVerse
"""
from typing import Dict, Any, List
from datetime import datetime

from utils.logger import get_logger

logger = get_logger(__name__)


class ResponseFormatter:
    """Formatea respuestas para enviar al usuario a través de AgentVerse"""
    
    def format_response(self, response: Dict, intent: str) -> Dict[str, Any]:
        """Formatea una respuesta según la intención"""
        formatter_map = {
            'show_events': self._format_events_response,
            'create_event': self._format_create_response,
            'delete_event': self._format_delete_response,
            'update_event': self._format_update_response,
            'find_free_time': self._format_free_time_response,
            'get_help': self._format_help_response,
            'unknown': self._format_unknown_response
        }
        
        formatter = formatter_map.get(intent, self._format_generic_response)
        return formatter(response)
    
    def format_error_response(self, error_message: str, technical_error: str, original_message: str) -> Dict:
        """Formatea una respuesta de error"""
        return {
            'type': 'error',
            'success': False,
            'message': error_message,
            'technical_details': technical_error if logger.level <= 10 else None,
            'original_message': original_message,
            'suggestions': [
                "Intenta reformular tu solicitud",
                "Verifica que tu calendario esté conectado",
                "Escribe 'ayuda' para ver comandos disponibles"
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def _format_events_response(self, response: Dict) -> Dict[str, Any]:
        """Formatea respuesta de mostrar eventos"""
        events = response.get('events', [])
        
        if not events:
            return {
                'type': 'events_list',
                'success': True,
                'message': response.get('message', 'No se encontraron eventos'),
                'data': {
                    'events': [],
                    'count': 0,
                    'date_range': response.get('date_range', {})
                },
                'timestamp': datetime.now().isoformat()
            }
        
        return {
            'type': 'events_list',
            'success': True,
            'message': self._generate_events_summary_message(events, response.get('date_range', {})),
            'data': {
                'events': events,
                'count': len(events),
                'date_range': response.get('date_range', {})
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _format_create_response(self, response: Dict) -> Dict[str, Any]:
        """Formatea respuesta de crear evento"""
        event = response.get('event', {})
        
        return {
            'type': 'event_created',
            'success': True,
            'message': f"Evento creado: '{event.get('title', 'Sin título')}'",
            'data': {'event': event},
            'timestamp': datetime.now().isoformat()
        }
    
    def _format_delete_response(self, response: Dict) -> Dict[str, Any]:
        """Formatea respuesta de eliminar evento"""
        event = response.get('event', {})
        
        return {
            'type': 'event_deleted',
            'success': True,
            'message': f"Evento cancelado: '{event.get('title', 'Sin título')}'",
            'data': {'deleted_event': event},
            'timestamp': datetime.now().isoformat()
        }
    
    def _format_update_response(self, response: Dict) -> Dict[str, Any]:
        """Formatea respuesta de actualizar evento"""
        new_event = response.get('new_event', {})
        
        return {
            'type': 'event_updated',
            'success': True,
            'message': f"Evento actualizado: '{new_event.get('title', 'Sin título')}'",
            'data': {
                'old_event': response.get('old_event', {}),
                'new_event': new_event
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _format_free_time_response(self, response: Dict) -> Dict[str, Any]:
        """Formatea respuesta de tiempo libre"""
        free_slots = response.get('free_slots', [])
        
        return {
            'type': 'free_time',
            'success': True,
            'message': self._generate_free_time_message(free_slots, response),
            'data': {
                'free_slots': free_slots,
                'count': len(free_slots),
                'date': response.get('date', ''),
                'requested_duration': response.get('requested_duration', 60)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _format_help_response(self, response: Dict) -> Dict[str, Any]:
        """Formatea respuesta de ayuda"""
        return {
            'type': 'help',
            'success': True,
            'message': response.get('message', ''),
            'data': {
                'capabilities': response.get('capabilities', []),
                'examples': response.get('examples', [])
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _format_unknown_response(self, response: Dict) -> Dict[str, Any]:
        """Formatea respuesta de intención desconocida"""
        return {
            'type': 'unknown',
            'success': False,
            'message': response.get('message', 'No entendí tu solicitud'),
            'data': {'suggestions': response.get('suggestions', [])},
            'help_available': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def _format_generic_response(self, response: Dict) -> Dict[str, Any]:
        """Formatea respuesta genérica"""
        return {
            **response,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_events_summary_message(self, events: List[Dict], date_range: Dict) -> str:
        """Genera mensaje resumen de eventos"""
        count = len(events)
        start = date_range.get('start', '')
        end = date_range.get('end', '')
        
        if count == 0:
            return f"No tienes eventos programados del {start} al {end}"
        elif count == 1:
            event = events[0]
            return f"Tienes 1 evento: '{event['title']}' el {event['formatted_date']}"
        else:
            return f"Tienes {count} eventos del {start} al {end}"
    
    def _generate_free_time_message(self, free_slots: List[Dict], response: Dict) -> str:
        """Genera mensaje sobre tiempo libre"""
        count = len(free_slots)
        date = response.get('date', '')
        duration = response.get('requested_duration', 60)
        
        if count == 0:
            return f"No encontré espacios libres de {duration} minutos el {date}"
        else:
            return f"Encontré {count} espacios libres el {date}"