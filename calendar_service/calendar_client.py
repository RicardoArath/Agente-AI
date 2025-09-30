"""
Correcciones para calendar_client.py - Arreglar formato de fechas
"""

# 1. IMPORTAR pytz para manejo correcto de timezones
from datetime import datetime, timezone, timedelta
import pytz

# 2. AGREGAR función auxiliar para formatear fechas correctamente
def format_datetime_for_api(dt: datetime, tz_str: str = None) -> str:
    """
    Formatea un datetime para la API de Google Calendar
    
    Args:
        dt: Objeto datetime
        tz_str: String de timezone (ej: 'America/Mexico_City')
        
    Returns:
        String en formato RFC3339
    """
    if tz_str is None:
        tz_str = settings.DEFAULT_TIMEZONE
    
    # Si el datetime no tiene timezone, agregar el correcto
    if dt.tzinfo is None:
        tz = pytz.timezone(tz_str)
        dt = tz.localize(dt)
    
    # Retornar en formato ISO con timezone
    return dt.isoformat()

# 3. MODIFICAR el método get_events en GoogleCalendarClient
def get_events(self, 
               time_min: Optional[str] = None,
               time_max: Optional[str] = None,
               max_results: Optional[int] = None,
               calendar_id: Optional[str] = None) -> List[Dict]:
    """
    Obtiene eventos del calendario
    
    Args:
        time_min: Fecha/hora mínima en formato ISO (RFC3339)
        time_max: Fecha/hora máxima en formato ISO (RFC3339)
        max_results: Número máximo de eventos a retornar
        calendar_id: ID del calendario a consultar
        
    Returns:
        Lista de eventos formateados
    """
    if max_results is None:
        max_results = settings.MAX_EVENTS_DEFAULT
    if calendar_id is None:
        calendar_id = settings.CALENDAR_ID
        
    if self.service is None:
        raise CalendarError("Cliente de Calendar no está inicializado")
        
    try:
        logger.info(f"📅 Obteniendo eventos: {time_min} - {time_max}")
        
        # Validar y formatear fechas si son necesarias
        if time_min:
            # Validar que tiene timezone
            if not ('+' in time_min or 'Z' in time_min or time_min.endswith('+00:00')):
                logger.warning("⚠️ time_min sin timezone, agregando...")
                try:
                    dt = datetime.fromisoformat(time_min)
                    time_min = format_datetime_for_api(dt)
                except:
                    pass
        
        if time_max:
            # Validar que tiene timezone
            if not ('+' in time_max or 'Z' in time_max or time_max.endswith('+00:00')):
                logger.warning("⚠️ time_max sin timezone, agregando...")
                try:
                    dt = datetime.fromisoformat(time_max)
                    time_max = format_datetime_for_api(dt)
                except:
                    pass
        
        # Construir parámetros
        params = {
            'calendarId': calendar_id,
            'maxResults': max_results,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        
        if time_min:
            params['timeMin'] = time_min
        if time_max:
            params['timeMax'] = time_max
        
        # Log de parámetros para debug
        logger.debug(f"📋 Parámetros de consulta: {params}")
        
        # Llamada a la API
        events_result = self.service.events().list(**params).execute()
        events = events_result.get('items', [])
        
        logger.info(f"✅ {len(events)} eventos obtenidos")
        
        # Formatear eventos
        formatted_events = [self._format_event(event) for event in events]
        
        return formatted_events
        
    except HttpError as e:
        logger.error(f"❌ Error HTTP obteniendo eventos: {e}")
        # Log adicional para debugging
        logger.error(f"   timeMin: {time_min}")
        logger.error(f"   timeMax: {time_max}")
        raise CalendarError(f"Error de API: {e}")
    except Exception as e:
        logger.error(f"❌ Error inesperado obteniendo eventos: {e}")
        raise CalendarError(f"Error obteniendo eventos: {e}")


# 4. AGREGAR funciones auxiliares de utilidad para fechas
def get_week_range(tz_str: str = None) -> tuple:
    """
    Obtiene el rango de la semana actual
    
    Returns:
        Tuple (start_of_week, end_of_week) en formato ISO
    """
    if tz_str is None:
        tz_str = settings.DEFAULT_TIMEZONE
    
    tz = pytz.timezone(tz_str)
    now = datetime.now(tz)
    
    # Inicio de la semana (lunes)
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Fin de la semana (domingo)
    end_of_week = start_of_week + timedelta(days=7)
    
    return format_datetime_for_api(start_of_week, tz_str), format_datetime_for_api(end_of_week, tz_str)


def get_today_range(tz_str: str = None) -> tuple:
    """
    Obtiene el rango del día actual
    
    Returns:
        Tuple (start_of_day, end_of_day) en formato ISO
    """
    if tz_str is None:
        tz_str = settings.DEFAULT_TIMEZONE
    
    tz = pytz.timezone(tz_str)
    now = datetime.now(tz)
    
    # Inicio del día
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Fin del día
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return format_datetime_for_api(start_of_day, tz_str), format_datetime_for_api(end_of_day, tz_str)


def get_tomorrow_range(tz_str: str = None) -> tuple:
    """
    Obtiene el rango de mañana
    
    Returns:
        Tuple (start_of_tomorrow, end_of_tomorrow) en formato ISO
    """
    if tz_str is None:
        tz_str = settings.DEFAULT_TIMEZONE
    
    tz = pytz.timezone(tz_str)
    now = datetime.now(tz)
    tomorrow = now + timedelta(days=1)
    
    # Inicio de mañana
    start_of_tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Fin de mañana
    end_of_tomorrow = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return format_datetime_for_api(start_of_tomorrow, tz_str), format_datetime_for_api(end_of_tomorrow, tz_str)


# 5. EJEMPLO DE USO en agent_handler.py
"""
# En lugar de:
from datetime import datetime
time_min = datetime.now().isoformat()  # ❌ INCORRECTO

# Hacer:
from calendar_service.calendar_client import get_week_range, get_today_range

# Para esta semana:
time_min, time_max = get_week_range()
events = calendar_client.get_events(time_min=time_min, time_max=time_max)

# Para hoy:
time_min, time_max = get_today_range()
events = calendar_client.get_events(time_min=time_min, time_max=time_max)

# Para mañana:
time_min, time_max = get_tomorrow_range()
events = calendar_client.get_events(time_min=time_min, time_max=time_max)
"""


# 6. INSTALACIÓN DE DEPENDENCIA
"""
Agregar a requirements.txt:
pytz>=2023.3
"""