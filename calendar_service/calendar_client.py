"""
Cliente principal para interactuar con Google Calendar API
"""
import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from functools import lru_cache

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Importar pytz para manejo correcto de timezones
try:
    import pytz
except ImportError:
    raise ImportError("pytz no está instalado. Ejecuta: pip install pytz")

from config.settings import settings
from utils.exceptions import CalendarError, AuthenticationError
from utils.logger import get_logger

logger = get_logger(__name__)

# ==========================================
# FUNCIONES AUXILIARES PARA FECHAS
# ==========================================

def format_datetime_for_api(dt: datetime, tz_str: str = None) -> str:
    """
    Formatea un datetime para la API de Google Calendar (RFC3339)
    
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


def get_month_range(tz_str: str = None) -> tuple:
    """
    Obtiene el rango del mes actual
    
    Returns:
        Tuple (start_of_month, end_of_month) en formato ISO
    """
    if tz_str is None:
        tz_str = settings.DEFAULT_TIMEZONE
    
    tz = pytz.timezone(tz_str)
    now = datetime.now(tz)
    
    # Inicio del mes
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Último día del mes
    if now.month == 12:
        end = start.replace(year=now.year + 1, month=1)
    else:
        end = start.replace(month=now.month + 1)
    
    return format_datetime_for_api(start, tz_str), format_datetime_for_api(end, tz_str)


# ==========================================
# CLASE PRINCIPAL
# ==========================================

class GoogleCalendarClient:
    """Cliente principal para Google Calendar API"""
    
    def __init__(self):
        """Inicializa el cliente de Calendar"""
        self.service = None
        self.credentials = None
        self._initialize()
    
    def _initialize(self):
        """Inicializa la conexión con Google Calendar"""
        try:
            logger.info("Inicializando cliente de Google Calendar...")
            self.credentials = self._get_credentials()
            self.service = build('calendar', 'v3', credentials=self.credentials)
            logger.info("✅ Cliente de Google Calendar inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando cliente: {e}")
            raise CalendarError(f"No se pudo inicializar el cliente de Calendar: {e}")
    
    def _get_credentials(self) -> Credentials:
        """Obtiene y valida las credenciales de Google"""
        creds = None
        token_path = settings.get_token_path()
        
        # Cargar credenciales existentes
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, settings.GOOGLE_SCOPES)
                logger.info("📄 Credenciales cargadas desde archivo")
            except Exception as e:
                logger.warning(f"⚠️ Error cargando credenciales: {e}")
        
        # Validar y renovar credenciales
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.info("🔄 Renovando credenciales...")
                    creds.refresh(Request())
                    logger.info("✅ Credenciales renovadas")
                except Exception as e:
                    logger.error(f"❌ Error renovando credenciales: {e}")
                    creds = None
            
            # Si no se pueden renovar, hacer auth completo
            if not creds:
                creds = self._perform_auth_flow()
            
            # Guardar credenciales
            self._save_credentials(creds)
        
        return creds
    
    def _perform_auth_flow(self) -> Credentials:
        """Realiza el flujo completo de autenticación"""
        credentials_path = settings.get_credentials_path()
        
        if not os.path.exists(credentials_path):
            raise AuthenticationError(f"Archivo de credenciales no encontrado: {credentials_path}")
        
        try:
            logger.info("🔐 Iniciando flujo de autenticación...")
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, 
                settings.GOOGLE_SCOPES
            )
            
            # Ejecutar servidor local para auth
            creds = flow.run_local_server(port=settings.AUTH_SERVER_PORT, open_browser=True)
            logger.info("✅ Autenticación completada exitosamente")
            
            return creds
            
        except Exception as e:
            logger.error(f"❌ Error en flujo de autenticación: {e}")
            raise AuthenticationError(f"Fallo en autenticación: {e}")
    
    def _save_credentials(self, creds: Credentials):
        """Guarda las credenciales en archivo"""
        try:
            token_path = settings.get_token_path()
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
            logger.info(f"💾 Credenciales guardadas en {token_path}")
        except Exception as e:
            logger.error(f"❌ Error guardando credenciales: {e}")
    
    # ==========================================
    # MÉTODOS PRINCIPALES DE LA API
    # ==========================================
    
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
                if not ('+' in time_min or 'Z' in time_min or '-' in time_min.split('T')[-1] if 'T' in time_min else False):
                    logger.warning("⚠️ time_min sin timezone, agregando...")
                    try:
                        dt = datetime.fromisoformat(time_min)
                        time_min = format_datetime_for_api(dt)
                    except Exception as e:
                        logger.error(f"Error formateando time_min: {e}")
            
            if time_max:
                # Validar que tiene timezone
                if not ('+' in time_max or 'Z' in time_max or '-' in time_max.split('T')[-1] if 'T' in time_max else False):
                    logger.warning("⚠️ time_max sin timezone, agregando...")
                    try:
                        dt = datetime.fromisoformat(time_max)
                        time_max = format_datetime_for_api(dt)
                    except Exception as e:
                        logger.error(f"Error formateando time_max: {e}")
            
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
            logger.error(f"   timeMin: {time_min}")
            logger.error(f"   timeMax: {time_max}")
            raise CalendarError(f"Error de API: {e}")
        except Exception as e:
            logger.error(f"❌ Error inesperado obteniendo eventos: {e}")
            raise CalendarError(f"Error obteniendo eventos: {e}")
    
    def create_event(self, 
                    title: str,
                    start_datetime: str,
                    end_datetime: str,
                    description: str = "",
                    location: str = "",
                    calendar_id: Optional[str] = None) -> Dict:
        """
        Crea un nuevo evento en el calendario
        
        Args:
            title: Título del evento
            start_datetime: Fecha/hora de inicio en formato ISO
            end_datetime: Fecha/hora de fin en formato ISO
            description: Descripción opcional
            location: Ubicación opcional
            calendar_id: ID del calendario donde crear el evento
            
        Returns:
            Evento creado formateado
        """
        if calendar_id is None:
            calendar_id = settings.CALENDAR_ID
            
        if self.service is None:
            raise CalendarError("Cliente de Calendar no está inicializado")
            
        try:
            logger.info(f"➕ Creando evento: {title}")
            
            # Construir body del evento
            event_body = {
                'summary': title,
                'description': description,
                'location': location,
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': settings.DEFAULT_TIMEZONE,
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': settings.DEFAULT_TIMEZONE,
                }
            }
            
            # Crear evento
            event = self.service.events().insert(
                calendarId=calendar_id, 
                body=event_body
            ).execute()
            
            logger.info(f"✅ Evento creado con ID: {event['id']}")
            
            return self._format_event(event)
            
        except HttpError as e:
            logger.error(f"❌ Error HTTP creando evento: {e}")
            raise CalendarError(f"Error de API creando evento: {e}")
        except Exception as e:
            logger.error(f"❌ Error inesperado creando evento: {e}")
            raise CalendarError(f"Error creando evento: {e}")
    
    def update_event(self, 
                    event_id: str,
                    title: Optional[str] = None,
                    start_datetime: Optional[str] = None,
                    end_datetime: Optional[str] = None,
                    description: Optional[str] = None,
                    location: Optional[str] = None,
                    calendar_id: Optional[str] = None) -> Dict:
        """
        Actualiza un evento existente
        
        Args:
            event_id: ID del evento a actualizar
            title: Nuevo título (opcional)
            start_datetime: Nueva fecha/hora de inicio (opcional)
            end_datetime: Nueva fecha/hora de fin (opcional)
            description: Nueva descripción (opcional)
            location: Nueva ubicación (opcional)
            calendar_id: ID del calendario
            
        Returns:
            Evento actualizado formateado
        """
        if calendar_id is None:
            calendar_id = settings.CALENDAR_ID
            
        if self.service is None:
            raise CalendarError("Cliente de Calendar no está inicializado")
            
        try:
            logger.info(f"✏️ Actualizando evento: {event_id}")
            
            # Obtener evento actual
            event = self.service.events().get(
                calendarId=calendar_id, 
                eventId=event_id
            ).execute()
            
            # Actualizar campos especificados
            if title is not None:
                event['summary'] = title
            if description is not None:
                event['description'] = description
            if location is not None:
                event['location'] = location
            if start_datetime is not None:
                event['start']['dateTime'] = start_datetime
            if end_datetime is not None:
                event['end']['dateTime'] = end_datetime
            
            # Aplicar actualización
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"✅ Evento actualizado: {updated_event.get('summary')}")
            
            return self._format_event(updated_event)
            
        except HttpError as e:
            logger.error(f"❌ Error HTTP actualizando evento: {e}")
            raise CalendarError(f"Error de API actualizando evento: {e}")
        except Exception as e:
            logger.error(f"❌ Error inesperado actualizando evento: {e}")
            raise CalendarError(f"Error actualizando evento: {e}")
    
    def delete_event(self, 
                    event_id: str,
                    calendar_id: Optional[str] = None) -> bool:
        """
        Elimina un evento del calendario
        
        Args:
            event_id: ID del evento a eliminar
            calendar_id: ID del calendario
            
        Returns:
            True si se eliminó exitosamente
        """
        if calendar_id is None:
            calendar_id = settings.CALENDAR_ID
            
        if self.service is None:
            raise CalendarError("Cliente de Calendar no está inicializado")
            
        try:
            logger.info(f"🗑️ Eliminando evento: {event_id}")
            
            # Obtener info del evento antes de eliminarlo
            try:
                event = self.service.events().get(
                    calendarId=calendar_id, 
                    eventId=event_id
                ).execute()
                title = event.get('summary', 'Sin título')
            except:
                title = 'Evento desconocido'
            
            # Eliminar evento
            self.service.events().delete(
                calendarId=calendar_id, 
                eventId=event_id
            ).execute()
            
            logger.info(f"✅ Evento eliminado: {title}")
            return True
            
        except HttpError as e:
            logger.error(f"❌ Error HTTP eliminando evento: {e}")
            raise CalendarError(f"Error de API eliminando evento: {e}")
        except Exception as e:
            logger.error(f"❌ Error inesperado eliminando evento: {e}")
            raise CalendarError(f"Error eliminando evento: {e}")
    
    def find_free_time(self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 30,
        calendar_id: Optional[str] = None) -> List[Dict]:
        """
        Encuentra espacios libres en el calendario usando un algoritmo optimizado
        
        Args:
            start_date: Fecha/hora de inicio de búsqueda
            end_date: Fecha/hora de fin de búsqueda
            duration_minutes: Duración del espacio buscado en minutos
            calendar_id: ID del calendario
            
        Returns:
            Lista de espacios libres con 'start' y 'end'
        """
        if calendar_id is None:
            calendar_id = settings.CALENDAR_ID
            
        if self.service is None:
            raise CalendarError("Cliente de Calendar no está inicializado")
        
        try:
            logger.info(f"🔍 Buscando espacios libres de {duration_minutes} minutos")
            
            # Normalizar fechas con timezone
            tz = pytz.timezone(settings.DEFAULT_TIMEZONE)
            
            if start_date.tzinfo is None:
                start_date = tz.localize(start_date)
            else:
                start_date = start_date.astimezone(tz)
            
            if end_date.tzinfo is None:
                end_date = tz.localize(end_date)
            else:
                end_date = end_date.astimezone(tz)
            
            # Formatear fechas para la API
            time_min = format_datetime_for_api(start_date)
            time_max = format_datetime_for_api(end_date)
            
            logger.info(f"📅 Rango de búsqueda: {time_min} a {time_max}")
            
            # Obtener eventos existentes
            eventos = self.get_events(
                time_min=time_min,
                time_max=time_max,
                calendar_id=calendar_id
            )
            
            logger.info(f"📊 {len(eventos)} eventos encontrados en el rango")
            
            # Si no hay eventos, el primer slot disponible es el inicio
            if not eventos:
                logger.info("✅ No hay eventos, retornando primer espacio desde inicio")
                return [{
                    'start': start_date,
                    'end': start_date + timedelta(minutes=duration_minutes),
                    'duration_minutes': duration_minutes
                }]
            
            # Parsear y ordenar eventos por fecha de inicio
            eventos_parseados = []
            for evento in eventos:
                try:
                    start_str = evento['start_datetime']
                    end_str = evento['end_datetime']
                    
                    # Parsear fechas
                    event_start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    event_end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                    
                    # Convertir a timezone local
                    if event_start.tzinfo is None:
                        event_start = tz.localize(event_start)
                    else:
                        event_start = event_start.astimezone(tz)
                    
                    if event_end.tzinfo is None:
                        event_end = tz.localize(event_end)
                    else:
                        event_end = event_end.astimezone(tz)
                    
                    eventos_parseados.append({
                        'start': event_start,
                        'end': event_end,
                        'title': evento.get('title', 'Sin título')
                    })
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error parseando evento: {e}")
                    continue
            
            # Ordenar por fecha de inicio
            eventos_parseados.sort(key=lambda x: x['start'])
            
            logger.info(f"✅ {len(eventos_parseados)} eventos parseados y ordenados")
            
            # Buscar espacios libres
            espacios_libres = []
            duracion = timedelta(minutes=duration_minutes)
            
            # Configuración de horario laboral
            hora_inicio = settings.BUSINESS_HOURS_START
            hora_fin = settings.BUSINESS_HOURS_END
            
            # Verificar si hay espacio antes del primer evento
            primer_evento_start = eventos_parseados[0]['start']
            
            # Ajustar start_date al horario laboral del primer día
            dia_actual = start_date.replace(hour=hora_inicio, minute=0, second=0, microsecond=0)
            
            # Si start_date es después del inicio del horario laboral, usar start_date
            if start_date > dia_actual:
                dia_actual = start_date
            
            # Verificar espacio antes del primer evento
            if dia_actual + duracion <= primer_evento_start:
                # Hay espacio antes del primer evento
                # Buscar slots en ese gap
                tiempo_actual = dia_actual
                while tiempo_actual + duracion <= primer_evento_start:
                    # Verificar que esté en horario laboral
                    if (tiempo_actual.hour >= hora_inicio and 
                        (tiempo_actual + duracion).hour <= hora_fin and
                        tiempo_actual.weekday() < 5):  # Lunes a Viernes
                        
                        espacios_libres.append({
                            'start': tiempo_actual,
                            'end': tiempo_actual + duracion,
                            'duration_minutes': duration_minutes
                        })
                        
                        if len(espacios_libres) >= 10:
                            logger.info(f"✅ Encontrados {len(espacios_libres)} espacios libres")
                            return espacios_libres
                    
                    tiempo_actual += timedelta(minutes=30)
                    
                    # Si salimos del horario laboral, saltar al siguiente día
                    if tiempo_actual.hour >= hora_fin:
                        tiempo_actual = (tiempo_actual + timedelta(days=1)).replace(
                            hour=hora_inicio, minute=0, second=0, microsecond=0
                        )
            
            # Buscar gaps entre eventos consecutivos
            for i in range(len(eventos_parseados) - 1):
                evento_actual_end = eventos_parseados[i]['end']
                evento_siguiente_start = eventos_parseados[i + 1]['start']
                
                gap = evento_siguiente_start - evento_actual_end
                
                logger.debug(f"🕐 Gap entre eventos: {gap}")
                
                if gap >= duracion:
                    # Hay un gap suficientemente grande
                    # Buscar slots en ese gap
                    tiempo_actual = evento_actual_end
                    
                    while tiempo_actual + duracion <= evento_siguiente_start:
                        # Verificar que esté en horario laboral y día hábil
                        if (tiempo_actual.hour >= hora_inicio and 
                            (tiempo_actual + duracion).hour <= hora_fin and
                            tiempo_actual.weekday() < 5):
                            
                            espacios_libres.append({
                                'start': tiempo_actual,
                                'end': tiempo_actual + duracion,
                                'duration_minutes': duration_minutes
                            })
                            
                            if len(espacios_libres) >= 10:
                                logger.info(f"✅ Encontrados {len(espacios_libres)} espacios libres")
                                return espacios_libres
                        
                        tiempo_actual += timedelta(minutes=30)
                        
                        # Si salimos del horario laboral, saltar al siguiente día
                        if tiempo_actual.hour >= hora_fin:
                            tiempo_actual = (tiempo_actual + timedelta(days=1)).replace(
                                hour=hora_inicio, minute=0, second=0, microsecond=0
                            )
                            
                            # Si el siguiente día está fuera del gap, salir del while
                            if tiempo_actual >= evento_siguiente_start:
                                break
            
            # Verificar si hay espacio después del último evento
            ultimo_evento_end = eventos_parseados[-1]['end']
            
            tiempo_actual = ultimo_evento_end
            
            while tiempo_actual + duracion <= end_date:
                # Verificar que esté en horario laboral y día hábil
                if (tiempo_actual.hour >= hora_inicio and 
                    (tiempo_actual + duracion).hour <= hora_fin and
                    tiempo_actual.weekday() < 5):
                    
                    espacios_libres.append({
                        'start': tiempo_actual,
                        'end': tiempo_actual + duracion,
                        'duration_minutes': duration_minutes
                    })
                    
                    if len(espacios_libres) >= 10:
                        logger.info(f"✅ Encontrados {len(espacios_libres)} espacios libres")
                        return espacios_libres
                
                tiempo_actual += timedelta(minutes=30)
                
                # Si salimos del horario laboral, saltar al siguiente día
                if tiempo_actual.hour >= hora_fin:
                    tiempo_actual = (tiempo_actual + timedelta(days=1)).replace(
                        hour=hora_inicio, minute=0, second=0, microsecond=0
                    )
            
            logger.info(f"✅ Encontrados {len(espacios_libres)} espacios libres")
            return espacios_libres
            
        except Exception as e:
            logger.error(f"❌ Error buscando espacios libres: {e}", exc_info=True)
            raise CalendarError(f"Error buscando espacios libres: {e}")
        
    @lru_cache(maxsize=128)
    def get_calendar_info(self, calendar_id: Optional[str] = None) -> Dict:
        """
        Obtiene información del calendario (cached)
        
        Args:
            calendar_id: ID del calendario
            
        Returns:
            Información del calendario
        """
        if calendar_id is None:
            calendar_id = settings.CALENDAR_ID
            
        if self.service is None:
            raise CalendarError("Cliente de Calendar no está inicializado")
            
        try:
            logger.info(f"ℹ️ Obteniendo información del calendario: {calendar_id}")
            
            calendar = self.service.calendars().get(calendarId=calendar_id).execute()
            
            return {
                'id': calendar['id'],
                'name': calendar.get('summary', 'Sin nombre'),
                'timezone': calendar.get('timeZone', settings.DEFAULT_TIMEZONE),
                'description': calendar.get('description', '')
            }
            
        except HttpError as e:
            logger.error(f"❌ Error obteniendo info del calendario: {e}")
            raise CalendarError(f"Error obteniendo información del calendario: {e}")
    
    # ==========================================
    # MÉTODOS AUXILIARES
    # ==========================================
    
    def _format_event(self, event: Dict) -> Dict:
        """
        Formatea un evento de la API para uso interno
        
        Args:
            event: Evento crudo de la API
            
        Returns:
            Evento formateado
        """
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        
        # Formatear fecha para mostrar
        if start and 'T' in start:
            try:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                formatted_date = start_dt.strftime('%Y-%m-%d %H:%M')
            except:
                formatted_date = start
        else:
            formatted_date = start or 'Fecha no disponible'
        
        return {
            'id': event.get('id', ''),
            'title': event.get('summary', 'Sin título'),
            'description': event.get('description', ''),
            'location': event.get('location', ''),
            'start_datetime': start,
            'end_datetime': end,
            'formatted_date': formatted_date,
            'html_link': event.get('htmlLink', ''),
            'created': event.get('created', ''),
            'updated': event.get('updated', ''),
            'status': event.get('status', 'confirmed')
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verifica el estado de la conexión con Google Calendar
        
        Returns:
            Estado de la conexión
        """
        try:
            # Intentar obtener info del calendario principal
            calendar_info = self.get_calendar_info()
            
            return {
                'status': 'healthy',
                'calendar_connected': True,
                'calendar_name': calendar_info['name'],
                'timezone': calendar_info['timezone'],
                'agent_id': settings.AGENT_ID,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Health check falló: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'calendar_connected': False,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

# Instancia singleton del cliente
_calendar_client = None

def get_calendar_client() -> GoogleCalendarClient:
    """
    Obtiene la instancia singleton del cliente de Calendar
    
    Returns:
        Instancia del cliente de Google Calendar
    """
    global _calendar_client
    
    if _calendar_client is None:
        _calendar_client = GoogleCalendarClient()
    
    return _calendar_client