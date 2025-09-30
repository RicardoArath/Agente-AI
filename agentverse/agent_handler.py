"""
Correcciones para agent_handler.py - Manejo correcto de fechas
"""

# Agregar estas importaciones al inicio del archivo
from datetime import datetime, timedelta
import pytz
from calendar_service.calendar_client import get_calendar_client

# Agregar estas funciones auxiliares
def get_week_range(tz_str: str = 'America/Mexico_City') -> tuple:
    """Obtiene el rango de la semana actual"""
    tz = pytz.timezone(tz_str)
    now = datetime.now(tz)
    
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=7)
    
    return start_of_week.isoformat(), end_of_week.isoformat()


def get_today_range(tz_str: str = 'America/Mexico_City') -> tuple:
    """Obtiene el rango del día actual"""
    tz = pytz.timezone(tz_str)
    now = datetime.now(tz)
    
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return start_of_day.isoformat(), end_of_day.isoformat()


def get_tomorrow_range(tz_str: str = 'America/Mexico_City') -> tuple:
    """Obtiene el rango de mañana"""
    tz = pytz.timezone(tz_str)
    now = datetime.now(tz)
    tomorrow = now + timedelta(days=1)
    
    start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    end = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return start.isoformat(), end.isoformat()


# MODIFICAR la función _handle_show_events así:
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
            tz = pytz.timezone('America/Mexico_City')
            now = datetime.now(tz)
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Último día del mes
            if now.month == 12:
                end = start.replace(year=now.year + 1, month=1)
            else:
                end = start.replace(month=now.month + 1)
            
            time_min = start.isoformat()
            time_max = end.isoformat()
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