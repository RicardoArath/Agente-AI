"""
Interfaz principal para integración con AgentVerse
Este es el punto de entrada que usará tu agente
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from config.settings import settings
from calendar_service.calendar_client import get_calendar_client
from nlp.intent_parser import IntentParser
from nlp.date_parser import DateParser
from agentverse.response_formatter import ResponseFormatter
from utils.logger import get_logger
from utils.exceptions import CalendarError, AgentError

logger = get_logger(__name__)

class AgentVerseHandler:
    """
    Manejador principal para integración con AgentVerse
    """
    
    def __init__(self):
        """Inicializa el manejador del agente"""
        self.calendar_client = get_calendar_client()
        self.intent_parser = IntentParser()
        self.date_parser = DateParser()
        self.response_formatter = ResponseFormatter()
        
        logger.info(f"🤖 AgentVerse Handler iniciado para agente: {settings.AGENT_ID}")
    
    def process_message(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Procesa un mensaje del usuario y devuelve una respuesta estructurada
        
        Args:
            message (str): Mensaje del usuario
            context (Dict, optional): Contexto adicional de la conversación
            
        Returns:
            Dict con la respuesta estructurada para AgentVerse
        """
        try:
            logger.info(f"📨 Procesando mensaje: '{message[:100]}...'")
            
            # 1. Analizar intención del usuario
            intent_result = self.intent_parser.parse(message)
            logger.info(f"🎯 Intención detectada: {intent_result['intent']}")
            
            # 2. Procesar según la intención
            response = self._dispatch_intent(intent_result, message, context)
            
            # 3. Formatear respuesta para AgentVerse
            formatted_response = self.response_formatter.format_response(
                response, 
                intent_result['intent']
            )
            
            logger.info(f"✅ Mensaje procesado exitosamente")
            return formatted_response
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
            return self._handle_error(e, message)
    
    def _dispatch_intent(self, intent_result: Dict, message: str, context: Optional[Dict] = None) -> Dict:
        """
        Despacha el procesamiento según la intención detectada
        
        Args:
            intent_result: Resultado del análisis de intención
            message: Mensaje original del usuario
            context: Contexto de la conversación
            
        Returns:
            Respuesta específica de la intención
        """
        intent = intent_result['intent']
        confidence = intent_result.get('confidence', 0.0)
        
        # Si la confianza es muy baja, pedir aclaración
        if confidence < 0.3:
            return {
                'type': 'clarification',
                'message': "No estoy seguro de entender tu solicitud. ¿Podrías ser más específico?",
                'suggestions': [
                    "Mostrar mis eventos de esta semana",
                    "Crear una reunión mañana a las 2pm",
                    "¿Tengo tiempo libre el viernes?"
                ]
            }
        
        # Despachar a la función apropiada
        intent_handlers = {
            'show_events': self._handle_show_events,
            'create_event': self._handle_create_event,
            'delete_event': self._handle_delete_event,
            'update_event': self._handle_update_event,
            'find_free_time': self._handle_find_free_time,
            'get_help': self._handle_help,
            'unknown': self._handle_unknown
        }
        
        handler = intent_handlers.get(intent, self._handle_unknown)
        return handler(intent_result, message, context)
    
    def _handle_show_events(self, intent_result: Dict, message: str, context: Optional[Dict]) -> Dict:
        """Maneja solicitudes para mostrar eventos"""
        try:
            # Extraer rango de fechas del mensaje
            date_info = self.date_parser.extract_date_range(message)
            
            # Obtener eventos
            events = self.calendar_client.get_events(
                time_min=date_info['start_iso'],
                time_max=date_info['end_iso']
            )
            
            return {
                'type': 'events_list',
                'success': True,
                'date_range': {
                    'start': date_info['start_display'],
                    'end': date_info['end_display']
                },
                'events': events,
                'count': len(events),
                'message': self._generate_events_message(events, date_info)
            }
            
        except Exception as e:
            logger.error(f"Error mostrando eventos: {e}")
            return {
                'type': 'error',
                'success': False,
                'message': f"No pude obtener tus eventos: {str(e)}"
            }
    
    def _handle_create_event(self, intent_result: Dict, message: str, context: Optional[Dict]) -> Dict:
        """Maneja solicitudes para crear eventos"""
        try:
            # Extraer detalles del evento del mensaje
            event_details = self.intent_parser.extract_event_details(message)
            
            if not event_details or not all(k in event_details for k in ['title', 'start', 'end']):
                return {
                    'type': 'missing_info',
                    'success': False,
                    'message': "Necesito más información para crear el evento.",
                    'missing_fields': self._get_missing_event_fields(event_details),
                    'example': "Ejemplo: 'Crear reunión de equipo mañana de 2pm a 3pm'"
                }
            
            # Crear el evento
            created_event = self.calendar_client.create_event(
                title=event_details['title'],
                start_datetime=event_details['start'],
                end_datetime=event_details['end'],
                description=event_details.get('description', ''),
                location=event_details.get('location', '')
            )
            
            return {
                'type': 'event_created',
                'success': True,
                'event': created_event,
                'message': f"✅ Evento creado: '{created_event['title']}' para {created_event['formatted_date']}"
            }
            
        except Exception as e:
            logger.error(f"Error creando evento: {e}")
            return {
                'type': 'error',
                'success': False,
                'message': f"No pude crear el evento: {str(e)}"
            }
    
    def _handle_delete_event(self, intent_result: Dict, message: str, context: Optional[Dict]) -> Dict:
        """Maneja solicitudes para eliminar eventos"""
        try:
            # Extraer identificación del evento a eliminar
            event_info = self.intent_parser.extract_event_identifier(message)
            
            if not event_info:
                return {
                    'type': 'missing_info',
                    'success': False,
                    'message': "No pude identificar qué evento quieres cancelar.",
                    'suggestion': "Especifica la hora o título del evento, ejemplo: 'Cancelar mi reunión de las 3pm'"
                }
            
            # Buscar el evento específico
            event_to_delete = self._find_event_by_criteria(event_info)
            
            if not event_to_delete:
                return {
                    'type': 'event_not_found',
                    'success': False,
                    'message': "No encontré un evento que coincida con tu descripción.",
                    'suggestion': "Verifica la hora o título del evento"
                }
            
            # Eliminar el evento
            success = self.calendar_client.delete_event(event_to_delete['id'])
            
            if success:
                return {
                    'type': 'event_deleted',
                    'success': True,
                    'event': event_to_delete,
                    'message': f"🗑️ Evento cancelado: '{event_to_delete['title']}'"
                }
            else:
                return {
                    'type': 'error',
                    'success': False,
                    'message': "No pude cancelar el evento"
                }
                
        except Exception as e:
            logger.error(f"Error eliminando evento: {e}")
            return {
                'type': 'error',
                'success': False,
                'message': f"No pude cancelar el evento: {str(e)}"
            }
    
    def _handle_update_event(self, intent_result: Dict, message: str, context: Optional[Dict]) -> Dict:
        """Maneja solicitudes para actualizar eventos"""
        try:
            # Extraer información del evento a actualizar y nuevos datos
            update_info = self.intent_parser.extract_update_info(message)
            
            if not update_info or not update_info.get('event_identifier'):
                return {
                    'type': 'missing_info',
                    'success': False,
                    'message': "No pude identificar qué evento quieres actualizar.",
                    'suggestion': "Especifica el evento y qué cambiar, ejemplo: 'Mover mi reunión de las 2pm a las 3pm'"
                }
            
            # Buscar el evento a actualizar
            event_to_update = self._find_event_by_criteria(update_info['event_identifier'])
            
            if not event_to_update:
                return {
                    'type': 'event_not_found',
                    'success': False,
                    'message': "No encontré el evento que quieres actualizar."
                }
            
            # Actualizar el evento
            updated_event = self.calendar_client.update_event(
                event_id=event_to_update['id'],
                **update_info.get('updates', {})
            )
            
            return {
                'type': 'event_updated',
                'success': True,
                'old_event': event_to_update,
                'new_event': updated_event,
                'message': f"✏️ Evento actualizado: '{updated_event['title']}'"
            }
            
        except Exception as e:
            logger.error(f"Error actualizando evento: {e}")
            return {
                'type': 'error',
                'success': False,
                'message': f"No pude actualizar el evento: {str(e)}"
            }
    
    def _handle_find_free_time(self, intent_result: Dict, message: str, context: Optional[Dict]) -> Dict:
        """Maneja solicitudes para encontrar tiempo libre"""
        try:
            # Extraer información de fecha y duración
            date_info = self.date_parser.extract_date_range(message, single_day=True)
            duration = self.intent_parser.extract_duration(message) or settings.DEFAULT_EVENT_DURATION
            
            # Obtener eventos del día
            events = self.calendar_client.get_events(
                time_min=date_info['start_iso'],
                time_max=date_info['end_iso']
            )
            
            # Calcular espacios libres
            free_slots = self._calculate_free_slots(events, date_info, duration)
            
            return {
                'type': 'free_time',
                'success': True,
                'date': date_info['start_display'],
                'requested_duration': duration,
                'free_slots': free_slots,
                'count': len(free_slots),
                'message': self._generate_free_time_message(free_slots, date_info, duration)
            }
            
        except Exception as e:
            logger.error(f"Error buscando tiempo libre: {e}")
            return {
                'type': 'error',
                'success': False,
                'message': f"No pude buscar tiempo libre: {str(e)}"
            }
    
    def _handle_help(self, intent_result: Dict, message: str, context: Optional[Dict]) -> Dict:
        """Maneja solicitudes de ayuda"""
        return {
            'type': 'help',
            'success': True,
            'message': settings.DEFAULT_MESSAGES['help'],
            'capabilities': [
                "📅 Ver eventos de cualquier período",
                "➕ Crear nuevos eventos y reuniones",
                "✏️ Actualizar eventos existentes",
                "🗑️ Cancelar citas",
                "🕐 Encontrar tiempo libre"
            ],
            'examples': [
                "Mostrar mis citas de esta semana",
                "Agendar reunión mañana a las 2pm",
                "¿Tengo tiempo libre el viernes por la tarde?",
                "Cancelar mi cita de las 3pm",
                "Mover mi reunión de las 10am a las 11am"
            ]
        }
    
    def _handle_unknown(self, intent_result: Dict, message: str, context: Optional[Dict]) -> Dict:
        """Maneja intenciones no reconocidas"""
        return {
            'type': 'unknown',
            'success': False,
            'message': "No entendí tu solicitud. ¿Podrías reformularla?",
            'suggestions': [
                "Mostrar eventos",
                "Crear una cita",
                "Buscar tiempo libre",
                "Ayuda"
            ],
            'help_message': "Escribe 'ayuda' para ver qué puedo hacer por ti."
        }
    
    # ==========================================
    # MÉTODOS AUXILIARES
    # ==========================================
    
    def _find_event_by_criteria(self, criteria: Dict) -> Optional[Dict]:
        """
        Busca un evento específico basado en criterios
        
        Args:
            criteria: Criterios de búsqueda (tiempo, título, etc.)
            
        Returns:
            Evento encontrado o None
        """
        try:
            # Buscar en un rango amplio (próximos 30 días)
            from datetime import datetime, timedelta
            
            now = datetime.now()
            future = now + timedelta(days=30)
            
            events = self.calendar_client.get_events(
                time_min=now.isoformat(),
                time_max=future.isoformat()
            )
            
            # Filtrar por criterios
            for event in events:
                if self._event_matches_criteria(event, criteria):
                    return event
            
            return None
            
        except Exception as e:
            logger.error(f"Error buscando evento por criterios: {e}")
            return None
    
    def _event_matches_criteria(self, event: Dict, criteria: Dict) -> bool:
        """Verifica si un evento coincide con los criterios dados"""
        # Verificar por título
        if 'title_keywords' in criteria:
            for keyword in criteria['title_keywords']:
                if keyword.lower() in event['title'].lower():
                    return True
        
        # Verificar por hora
        if 'time' in criteria:
            event_time = event['start_datetime']
            if criteria['time'] in event_time:
                return True
        
        return False
    
    def _calculate_free_slots(self, events: List[Dict], date_info: Dict, duration: int) -> List[Dict]:
        """
        Calcula los espacios libres en un día
        
        Args:
            events: Lista de eventos del día
            date_info: Información del día
            duration: Duración mínima del espacio libre (minutos)
            
        Returns:
            Lista de espacios libres
        """
        try:
            from datetime import datetime, timedelta
            
            # Definir horas laborales
            day_start = datetime.fromisoformat(date_info['start_iso'].replace('Z', '+00:00'))
            day_start = day_start.replace(hour=settings.BUSINESS_HOURS_START, minute=0)
            day_end = day_start.replace(hour=settings.BUSINESS_HOURS_END, minute=0)
            
            # Ordenar eventos por hora de inicio
            sorted_events = sorted(events, key=lambda e: e['start_datetime'])
            
            free_slots = []
            current_time = day_start
            
            for event in sorted_events:
                event_start = datetime.fromisoformat(event['start_datetime'].replace('Z', '+00:00'))
                
                # Si hay espacio antes del evento
                if (event_start - current_time).total_seconds() >= duration * 60:
                    free_slots.append({
                        'start': current_time.strftime('%H:%M'),
                        'end': event_start.strftime('%H:%M'),
                        'duration_minutes': int((event_start - current_time).total_seconds() / 60)
                    })
                
                # Mover tiempo actual al final del evento
                event_end = datetime.fromisoformat(event['end_datetime'].replace('Z', '+00:00'))
                current_time = max(current_time, event_end)
            
            # Verificar espacio después del último evento
            if (day_end - current_time).total_seconds() >= duration * 60:
                free_slots.append({
                    'start': current_time.strftime('%H:%M'),
                    'end': day_end.strftime('%H:%M'),
                    'duration_minutes': int((day_end - current_time).total_seconds() / 60)
                })
            
            return free_slots
            
        except Exception as e:
            logger.error(f"Error calculando espacios libres: {e}")
            return []
    
    def _generate_events_message(self, events: List[Dict], date_info: Dict) -> str:
        """Genera mensaje legible sobre los eventos"""
        if not events:
            return f"No tienes eventos programados del {date_info['start_display']} al {date_info['end_display']}"
        
        if len(events) == 1:
            event = events[0]
            return f"Tienes 1 evento: '{event['title']}' el {event['formatted_date']}"
        
        message = f"Tienes {len(events)} eventos del {date_info['start_display']} al {date_info['end_display']}:\n"
        for i, event in enumerate(events[:5], 1):  # Mostrar max 5
            message += f"{i}. {event['formatted_date']} - {event['title']}\n"
        
        if len(events) > 5:
            message += f"... y {len(events) - 5} eventos más"
        
        return message.strip()
    
    def _generate_free_time_message(self, free_slots: List[Dict], date_info: Dict, duration: int) -> str:
        """Genera mensaje sobre tiempo libre"""
        if not free_slots:
            return f"No encontré espacios libres de {duration} minutos el {date_info['start_display']}"
        
        message = f"Encontré {len(free_slots)} espacios libres el {date_info['start_display']}:\n"
        for slot in free_slots:
            message += f"• {slot['start']} - {slot['end']} ({slot['duration_minutes']} min)\n"
        
        return message.strip()
    
    def _get_missing_event_fields(self, event_details: Optional[Dict]) -> List[str]:
        """Identifica qué campos faltan para crear un evento"""
        if not event_details:
            return ['título', 'fecha', 'hora']
        
        missing = []
        if not event_details.get('title'):
            missing.append('título')
        if not event_details.get('start'):
            missing.append('fecha y hora de inicio')
        if not event_details.get('end'):
            missing.append('hora de fin')
        
        return missing
    
    def _handle_error(self, error: Exception, original_message: str) -> Dict[str, Any]:
        """
        Maneja errores y devuelve respuesta formateada
        
        Args:
            error: Excepción ocurrida
            original_message: Mensaje original que causó el error
            
        Returns:
            Respuesta de error formateada
        """
        error_type = type(error).__name__
        
        # Mapear tipos de error a mensajes amigables
        user_messages = {
            'CalendarError': 'Hubo un problema accediendo a tu calendario',
            'AuthenticationError': 'Necesito reautenticarme con Google',
            'AgentError': 'Error interno del agente',
            'ValueError': 'Los datos proporcionados no son válidos',
            'ConnectionError': 'Problema de conexión con Google'
        }
        
        user_message = user_messages.get(error_type, 'Ocurrió un error inesperado')
        
        return self.response_formatter.format_error_response(
            error_message=user_message,
            technical_error=str(error),
            original_message=original_message
        )
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del agente
        
        Returns:
            Estado del sistema
        """
        try:
            calendar_status = self.calendar_client.health_check()
            
            return {
                'agent_id': settings.AGENT_ID,
                'status': 'operational' if calendar_status['status'] == 'healthy' else 'degraded',
                'calendar_connected': calendar_status.get('calendar_connected', False),
                'capabilities': [
                    'show_events',
                    'create_event', 
                    'update_event',
                    'delete_event',
                    'find_free_time'
                ],
                'version': settings.VERSION,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo status: {e}")
            return {
                'agent_id': settings.AGENT_ID,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

# ==========================================
# FUNCIONES DE CONVENIENCIA PARA AGENTVERSE
# ==========================================

# Instancia singleton del handler
_agent_handler = None

def get_agent_handler() -> AgentVerseHandler:
    """Obtiene la instancia singleton del handler"""
    global _agent_handler
    
    if _agent_handler is None:
        _agent_handler = AgentVerseHandler()
    
    return _agent_handler

def process_user_message(message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Función principal para procesar mensajes desde AgentVerse
    
    Args:
        message: Mensaje del usuario
        context: Contexto opcional
        
    Returns:
        Respuesta estructurada
    """
    handler = get_agent_handler()
    return handler.process_message(message, context)

def get_agent_status() -> Dict[str, Any]:
    """
    Obtiene el estado del agente
    
    Returns:
        Estado actual del sistema
    """
    handler = get_agent_handler()
    return handler.get_status()