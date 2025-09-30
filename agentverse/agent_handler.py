"""
Manejador principal de mensajes para AgentVerse
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Importar configuración
from config.settings import settings

# Importar cliente de calendario y funciones auxiliares
from calendar_service.calendar_client import (
    get_calendar_client,
    get_week_range,
    get_today_range,
    get_tomorrow_range,
    get_month_range
)

# Importar utilidades
from utils.logger import get_logger
from utils.exceptions import CalendarError

logger = get_logger(__name__)

# Inicializar
logger.info(f"🤖 AgentVerse Handler iniciado para agente: {settings.AGENT_ID}")


def process_user_message(message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Procesa un mensaje del usuario y retorna una respuesta estructurada
    
    Args:
        message: Mensaje del usuario
        context: Contexto adicional opcional
        
    Returns:
        Diccionario con la respuesta estructurada
    """
    try:
        logger.info(f"📨 Procesando mensaje: '{message[:50]}...'")
        
        if context is None:
            context = {}
        
        # Detectar intención del usuario
        intent = _detect_intent(message)
        logger.info(f"🎯 Intención detectada: {intent}")
        
        # Procesar según la intención
        if intent == 'show_events':
            response = _handle_show_events(message, context)
        elif intent == 'create_event':
            response = _handle_create_event(message, context)
        elif intent == 'update_event':
            response = _handle_update_event(message, context)
        elif intent == 'delete_event':
            response = _handle_delete_event(message, context)
        elif intent == 'find_free_time':
            response = _handle_find_free_time(message, context)
        elif intent == 'help':
            response = _handle_help(message, context)
        else:
            response = _handle_unknown_intent(message, context)
        
        logger.info("✅ Mensaje procesado exitosamente")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error procesando mensaje: {e}")
        return {
            'type': 'error',
            'success': False,
            'message': f'Lo siento, hubo un error procesando tu solicitud: {str(e)}',
            'error': str(e)
        }


def get_agent_status() -> Dict[str, Any]:
    """
    Obtiene el estado actual del agente
    
    Returns:
        Diccionario con el estado del agente
    """
    try:
        client = get_calendar_client()
        health = client.health_check()
        
        return {
            'status': 'operational' if health['status'] == 'healthy' else 'degraded',
            'agent_id': settings.AGENT_ID,
            'agent_name': settings.AGENT_NAME,
            'version': settings.VERSION,
            'calendar_connected': health.get('calendar_connected', False),
            'calendar_name': health.get('calendar_name', ''),
            'timezone': health.get('timezone', settings.DEFAULT_TIMEZONE),
            'capabilities': [
                'Ver eventos del calendario',
                'Crear nuevos eventos',
                'Actualizar eventos existentes',
                'Eliminar eventos',
                'Buscar tiempo libre'
            ],
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        return {
            'status': 'error',
            'agent_id': settings.AGENT_ID,
            'calendar_connected': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


# ==========================================
# DETECCIÓN DE INTENCIÓN
# ==========================================

def _detect_intent(message: str) -> str:
    """
    Detecta la intención del usuario basándose en el mensaje
    
    Args:
        message: Mensaje del usuario
        
    Returns:
        Nombre de la intención detectada
    """
    message_lower = message.lower()
    
    # Mostrar eventos
    if any(word in message_lower for word in settings.INTENT_KEYWORDS.get('show_events', [])):
        return 'show_events'
    
    # Crear evento
    if any(word in message_lower for word in settings.INTENT_KEYWORDS.get('create_event', [])):
        return 'create_event'
    
    # Actualizar evento
    if any(word in message_lower for word in settings.INTENT_KEYWORDS.get('update_event', [])):
        return 'update_event'
    
    # Eliminar evento
    if any(word in message_lower for word in settings.INTENT_KEYWORDS.get('delete_event', [])):
        return 'delete_event'
    
    # Buscar tiempo libre
    if any(word in message_lower for word in settings.INTENT_KEYWORDS.get('find_free_time', [])):
        return 'find_free_time'
    
    # Ayuda
    if any(word in message_lower for word in settings.INTENT_KEYWORDS.get('help', [])):
        return 'help'
    
    # Intención desconocida
    return 'unknown'


# ==========================================
# MANEJADORES DE INTENCIONES
# ==========================================

def _handle_show_events(message: str, context: Dict = None) -> Dict:
    """
    Maneja solicitudes para mostrar eventos del calendario
    """
    try:
        logger.info("📅 Procesando solicitud de mostrar eventos...")
        
        client = get_calendar_client()
        
        # Determinar el rango de tiempo basado en el mensaje
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hoy', 'today']):
            time_min, time_max = get_today_range()
            period_text = "hoy"
            
        elif any(word in message_lower for word in ['mañana', 'tomorrow']):
            time_min, time_max = get_tomorrow_range()
            period_text = "mañana"
            
        elif any(word in message_lower for word in ['semana', 'week']):
            time_min, time_max = get_week_range()
            period_text = "esta semana"
            
        elif any(word in message_lower for word in ['mes', 'month']):
            time_min, time_max = get_month_range()
            period_text = "este mes"
            
        else:
            # Por defecto: próximos 7 días
            time_min, time_max = get_week_range()
            period_text = "los próximos 7 días"
        
        logger.info(f"🔍 Buscando eventos para: {period_text}")
        logger.info(f"   Rango: {time_min} a {time_max}")
        
        # Obtener eventos
        events = client.get_events(
            time_min=time_min,
            time_max=time_max,
            max_results=50
        )
        
        if not events:
            return {
                'type': 'events_list',
                'success': True,
                'message': f'No tienes eventos programados para {period_text}.',
                'events': [],
                'count': 0,
                'period': period_text
            }
        
        # Formatear respuesta
        event_summary = []
        for event in events[:5]:
            event_summary.append(
                f"• {event['formatted_date']} - {event['title']}"
            )
        
        message_text = f"Tienes {len(events)} evento(s) {period_text}:\n\n"
        message_text += "\n".join(event_summary)
        
        if len(events) > 5:
            message_text += f"\n\n... y {len(events) - 5} evento(s) más."
        
        return {
            'type': 'events_list',
            'success': True,
            'message': message_text,
            'events': events,
            'count': len(events),
            'period': period_text,
            'time_range': {
                'start': time_min,
                'end': time_max
            }
        }
        
    except Exception as e:
        logger.error(f"Error mostrando eventos: {e}")
        return {
            'type': 'events_list',
            'success': False,
            'message': f'No pude obtener tus eventos: {str(e)}',
            'events': [],
            'count': 0,
            'error': str(e)
        }


def _handle_create_event(message: str, context: Dict = None) -> Dict:
    """
    Maneja solicitudes para crear eventos
    """
    try:
        logger.info("➕ Procesando solicitud de crear evento...")
        
        # TODO: Implementar lógica de creación de eventos
        # Por ahora, retornar mensaje indicando que está en desarrollo
        
        return {
            'type': 'create_event',
            'success': False,
            'message': 'La funcionalidad de crear eventos está en desarrollo. Por favor, intenta más tarde.',
            'event': None
        }
        
    except Exception as e:
        logger.error(f"Error creando evento: {e}")
        return {
            'type': 'create_event',
            'success': False,
            'message': f'No pude crear el evento: {str(e)}',
            'error': str(e)
        }


def _handle_update_event(message: str, context: Dict = None) -> Dict:
    """
    Maneja solicitudes para actualizar eventos
    """
    try:
        logger.info("✏️ Procesando solicitud de actualizar evento...")
        
        # TODO: Implementar lógica de actualización
        
        return {
            'type': 'update_event',
            'success': False,
            'message': 'La funcionalidad de actualizar eventos está en desarrollo.',
            'event': None
        }
        
    except Exception as e:
        logger.error(f"Error actualizando evento: {e}")
        return {
            'type': 'update_event',
            'success': False,
            'message': f'No pude actualizar el evento: {str(e)}',
            'error': str(e)
        }


def _handle_delete_event(message: str, context: Dict = None) -> Dict:
    """
    Maneja solicitudes para eliminar eventos
    """
    try:
        logger.info("🗑️ Procesando solicitud de eliminar evento...")
        
        # TODO: Implementar lógica de eliminación
        
        return {
            'type': 'delete_event',
            'success': False,
            'message': 'La funcionalidad de eliminar eventos está en desarrollo.',
            'deleted': False
        }
        
    except Exception as e:
        logger.error(f"Error eliminando evento: {e}")
        return {
            'type': 'delete_event',
            'success': False,
            'message': f'No pude eliminar el evento: {str(e)}',
            'error': str(e)
        }


def _handle_find_free_time(message: str, context: Dict = None) -> Dict:
    """
    Maneja solicitudes para buscar tiempo libre
    """
    try:
        logger.info("🕐 Procesando solicitud de tiempo libre...")
        
        # TODO: Implementar lógica de búsqueda de tiempo libre
        
        return {
            'type': 'free_time',
            'success': False,
            'message': 'La funcionalidad de buscar tiempo libre está en desarrollo.',
            'free_slots': []
        }
        
    except Exception as e:
        logger.error(f"Error buscando tiempo libre: {e}")
        return {
            'type': 'free_time',
            'success': False,
            'message': f'No pude buscar tiempo libre: {str(e)}',
            'error': str(e)
        }


def _handle_help(message: str, context: Dict = None) -> Dict:
    """
    Maneja solicitudes de ayuda
    """
    help_text = f"""
¡Hola! Soy tu asistente de calendario. Puedo ayudarte con:

📅 Ver eventos:
   • "Mostrar mis eventos de esta semana"
   • "¿Qué tengo programado para hoy?"
   • "Ver mi agenda del mes"

➕ Crear eventos:
   • "Crear una reunión mañana a las 2pm"
   • "Agendar cita con el doctor el viernes"

✏️ Actualizar eventos:
   • "Mover mi reunión de las 2pm a las 3pm"
   • "Cambiar el título de mi cita"

🗑️ Eliminar eventos:
   • "Cancelar mi cita de las 3pm"
   • "Eliminar la reunión de mañana"

🕐 Buscar tiempo libre:
   • "¿Tengo tiempo libre mañana?"
   • "Buscar 2 horas libres esta semana"

¿En qué puedo ayudarte?
    """
    
    return {
        'type': 'help',
        'success': True,
        'message': help_text.strip(),
        'capabilities': [
            'show_events',
            'create_event',
            'update_event',
            'delete_event',
            'find_free_time'
        ]
    }


def _handle_unknown_intent(message: str, context: Dict = None) -> Dict:
    """
    Maneja mensajes con intención desconocida
    """
    return {
        'type': 'unknown',
        'success': False,
        'message': 'No entendí tu solicitud. Escribe "ayuda" para ver qué puedo hacer.',
        'suggestions': [
            'Mostrar mis eventos de esta semana',
            '¿Qué tengo programado para hoy?',
            'Ayuda'
        ]
    }