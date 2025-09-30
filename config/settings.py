"""
Configuración de la aplicación Calendar Agent
"""
import os
from pathlib import Path
from typing import List, Dict, Any

class Settings:
    """Configuración centralizada de la aplicación"""
    
    # ==========================================
    # INFORMACIÓN DEL AGENTE
    # ==========================================
    
    # ID único del agente en AgentVerse
    AGENT_ID = "agent1qgalpghkvfs6fpm262y8j6vpluvzhhhdl9xx24x5wdz4lcz90ffg5z47jac"
    
    # Nombre del agente
    AGENT_NAME = "CalendarAgent"
    
    # Versión de la aplicación
    VERSION = "1.0.0"
    
    # ==========================================
    # CONFIGURACIÓN DE ARCHIVOS Y DIRECTORIOS
    # ==========================================
    
    # Directorio base del proyecto
    BASE_DIR = Path(__file__).parent.parent
    
    # Directorio de credenciales
    CREDENTIALS_DIR = BASE_DIR / "credentials"
    CREDENTIALS_DIR.mkdir(exist_ok=True)
    
    # Archivos de credenciales y token
    CREDENTIALS_FILE = str(CREDENTIALS_DIR / "credentials.json")
    TOKEN_FILE = str(CREDENTIALS_DIR / "token.json")
    
    # Directorio de logs
    LOGS_DIR = BASE_DIR / "logs"
    LOGS_DIR.mkdir(exist_ok=True)
    
    # Archivo de log principal
    LOG_FILE = str(LOGS_DIR / "calendar_agent.log")
    
    # ==========================================
    # CONFIGURACIÓN DE GOOGLE CALENDAR
    # ==========================================
    
    # Scopes necesarios para Google Calendar (lectura y escritura)
    GOOGLE_SCOPES: List[str] = [
        'https://www.googleapis.com/auth/calendar',  # Acceso completo
        'https://www.googleapis.com/auth/calendar.events'  # Gestión de eventos
    ]
    
    # ID del calendario principal
    CALENDAR_ID = os.getenv('CALENDAR_ID', 'primary')
    
    # Timezone por defecto (Nuevo León, México)
    DEFAULT_TIMEZONE = os.getenv('TIMEZONE', 'America/Mexico_City')
    
    # Número máximo de eventos a obtener por defecto
    MAX_EVENTS_DEFAULT = int(os.getenv('MAX_EVENTS_DEFAULT', '50'))
    
    # Duración por defecto de eventos (en minutos)
    DEFAULT_EVENT_DURATION = 60
    
    # Horario laboral
    BUSINESS_HOURS_START = 9   # 9 AM
    BUSINESS_HOURS_END = 17    # 5 PM
    
    # ==========================================
    # CONFIGURACIÓN DE LOGGING
    # ==========================================
    
    # Nivel de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Tamaño máximo del archivo de log (en bytes)
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    
    # Número de archivos de backup
    LOG_BACKUP_COUNT = 5
    
    # ==========================================
    # CONFIGURACIÓN DE CACHE
    # ==========================================
    
    # Habilitar cache
    ENABLE_CACHE = True
    
    # Tamaño máximo del cache
    CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', '100'))
    
    # Duración del cache en segundos
    CACHE_DURATION_SECONDS = 300  # 5 minutos
    
    # ==========================================
    # CONFIGURACIÓN DE RATE LIMITING
    # ==========================================
    
    # Límite de requests por minuto
    API_RATE_LIMIT = 100
    
    # Límite de burst requests
    API_BURST_LIMIT = 10
    
    # ==========================================
    # CONFIGURACIÓN DE DESARROLLO
    # ==========================================
    
    # Modo debug
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes', 'on')
    
    # Entorno (development, production)
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    # Puerto para el servidor de autenticación local
    AUTH_SERVER_PORT = int(os.getenv('AUTH_SERVER_PORT', '8080'))
    
    # ==========================================
    # MENSAJES PREDEFINIDOS
    # ==========================================
    
    DEFAULT_MESSAGES: Dict[str, str] = {
        "welcome": "¡Hola! Soy tu asistente de calendario. Puedo ayudarte a gestionar tus citas y eventos.",
        "no_events": "No tienes eventos programados en el rango solicitado.",
        "event_created": "✅ Evento creado exitosamente: '{title}'",
        "event_updated": "✅ Evento actualizado: '{title}'",
        "event_deleted": "🗑️ Evento eliminado: '{title}'",
        "error_generic": "❌ Ocurrió un error inesperado. Por favor intenta de nuevo.",
        "help": """
Comandos disponibles:
• "Mostrar mis eventos de esta semana"
• "Crear una reunión mañana a las 2pm"
• "¿Tengo tiempo libre el viernes?"
• "Cancelar mi cita de las 3pm"
• "Actualizar mi reunión de las 10am"
        """
    }
    
    # ==========================================
    # CONFIGURACIÓN DE NLP
    # ==========================================
    
    # Palabras clave para identificar intenciones
    INTENT_KEYWORDS: Dict[str, List[str]] = {
        "show_events": [
            "mostrar", "ver", "eventos", "citas", "agenda", 
            "qué tengo", "programado", "calendario", "mis eventos"
        ],
        "create_event": [
            "crear", "agendar", "nueva cita", "reunión", 
            "programar", "agregar evento", "nueva reunión"
        ],
        "delete_event": [
            "cancelar", "eliminar", "borrar", "quitar evento"
        ],
        "update_event": [
            "actualizar", "modificar", "cambiar", "mover", "reprogramar"
        ],
        "find_free_time": [
            "tiempo libre", "disponible", "cuándo puedo", 
            "espacio libre", "horario disponible"
        ]
    }
    
    # Palabras clave para fechas relativas
    DATE_KEYWORDS: Dict[str, int] = {
        "hoy": 0,
        "mañana": 1,
        "pasado mañana": 2,
        "esta semana": 7,
        "próxima semana": 14,
        "este mes": 30
    }
    
    # Días de la semana
    WEEKDAYS: Dict[str, int] = {
        "lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2,
        "jueves": 3, "viernes": 4, "sábado": 5, "sabado": 5, "domingo": 6
    }
    
    # ==========================================
    # ENDPOINTS DE AGENTVERSE
    # ==========================================
    
    AGENTVERSE_ENDPOINTS: Dict[str, str] = {
        "development": "https://agentverse-dev.fetchai.com",
        "production": "https://agentverse.ai"
    }
    
    # ==========================================
    # MÉTODOS AUXILIARES
    # ==========================================
    
    @classmethod
    def get_agentverse_endpoint(cls) -> str:
        """Obtiene el endpoint correcto según el ambiente"""
        return cls.AGENTVERSE_ENDPOINTS.get(cls.ENVIRONMENT, cls.AGENTVERSE_ENDPOINTS["development"])
    
    @classmethod
    def validate_settings(cls) -> bool:
        """Valida que todas las configuraciones necesarias estén presentes"""
        import os
        
        # Crear directorios si no existen
        cls.CREDENTIALS_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
        
        # Verificar que exista el archivo de credenciales
        if not os.path.exists(cls.CREDENTIALS_FILE):
            raise FileNotFoundError(
                f"Archivo de credenciales no encontrado: {cls.CREDENTIALS_FILE}\n"
                f"Por favor descarga tu archivo credentials.json desde Google Cloud Console\n"
                f"y colócalo en: {cls.CREDENTIALS_FILE}"
            )
        
        return True
    
    @classmethod
    def get_summary(cls) -> Dict[str, Any]:
        """Obtiene resumen de la configuración actual"""
        return {
            "agent_id": cls.AGENT_ID,
            "agent_name": cls.AGENT_NAME,
            "version": cls.VERSION,
            "environment": cls.ENVIRONMENT,
            "debug": cls.DEBUG,
            "timezone": cls.DEFAULT_TIMEZONE,
            "scopes": len(cls.GOOGLE_SCOPES),
            "cache_enabled": cls.ENABLE_CACHE,
            "credentials_file": cls.CREDENTIALS_FILE,
            "token_file": cls.TOKEN_FILE
        }
    
    def __str__(self):
        """Representación string de la configuración"""
        return f"Settings(agent_id={self.AGENT_ID}, version={self.VERSION}, environment={self.ENVIRONMENT})"
    
    def get_credentials_path(self) -> str:
        """Retorna la ruta del archivo de credenciales como string"""
        return self.CREDENTIALS_FILE
    
    def get_token_path(self) -> str:
        """Retorna la ruta del archivo de token como string"""
        return self.TOKEN_FILE

# Instancia singleton de configuración
settings = Settings()

# Validar configuración al importar (excepto cuando se está importando el módulo para inspección)
if __name__ != "__main__":
    try:
        # Solo verificar directorios, no el archivo de credenciales
        settings.CREDENTIALS_DIR.mkdir(exist_ok=True)
        settings.LOGS_DIR.mkdir(exist_ok=True)
    except Exception as e:
        import warnings
        warnings.warn(f"Advertencia en configuración: {e}")