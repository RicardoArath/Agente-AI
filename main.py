#!/usr/bin/env python3
"""
Punto de entrada principal para el AgentVerse Calendar
Agente ID: agent1qgalpghkvfs6fpm262y8j6vpluvzhhhdl9xx24x5wdz4lcz90ffg5z47jac
"""

import sys
import json
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

# Configurar el path para importaciones
sys.path.insert(0, '.')

from config.settings import settings
from agentverse.agent_handler import process_user_message, get_agent_status
from utils.logger import get_logger, setup_logging

# Configurar logging
setup_logging()
logger = get_logger(__name__)

def main():
    """Función principal del agente"""
    
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description=f"AgentVerse Calendar Agent - {settings.AGENT_ID}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py --message "Mostrar mis eventos de esta semana"
  python main.py --status
  python main.py --interactive
  python main.py --test
        """
    )
    
    parser.add_argument(
        '--message', '-m',
        type=str,
        help='Procesar un mensaje específico'
    )
    
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='Mostrar estado del agente'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Modo interactivo'
    )
    
    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='Ejecutar tests básicos'
    )
    
    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='Salida en formato JSON'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Activar modo debug'
    )
    
    args = parser.parse_args()
    
    try:
        # Banner de inicio
        if not args.json:
            print_banner()
        
        # Procesar argumentos
        if args.debug:
            import logging
            logging.getLogger().setLevel(logging.DEBUG)
            logger.info("🐛 Modo debug activado")
        
        if args.status:
            handle_status_request(args.json)
        
        elif args.message:
            handle_single_message(args.message, args.json)
        
        elif args.interactive:
            handle_interactive_mode()
        
        elif args.test:
            handle_test_mode(args.json)
        
        else:
            # Modo por defecto: mostrar ayuda y estado
            if not args.json:
                parser.print_help()
                print(f"\n{'='*60}")
            handle_status_request(args.json)
            
    except KeyboardInterrupt:
        if not args.json:
            print("\n👋 ¡Hasta luego!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error en main: {e}")
        if args.json:
            print(json.dumps({
                "error": True,
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }))
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)

def print_banner():
    """Imprime el banner de inicio"""
    print(f"""
{'='*80}
🤖 AGENTVERSE CALENDAR AGENT
{'='*80}
Agent ID: {settings.AGENT_ID}
Version:  {settings.VERSION}
Time:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}
    """)

def handle_status_request(json_output: bool = False):
    """Maneja solicitudes de estado"""
    try:
        logger.info("📊 Obteniendo estado del agente...")
        status = get_agent_status()
        
        if json_output:
            print(json.dumps(status, indent=2))
        else:
            print_status(status)
            
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        if json_output:
            print(json.dumps({"error": True, "message": str(e)}))
        else:
            print(f"❌ Error obteniendo estado: {e}")

def print_status(status: Dict[str, Any]):
    """Imprime el estado de manera legible"""
    print(f"🚀 Estado del Agente:")
    print(f"   Status: {'🟢' if status['status'] == 'operational' else '🟡'} {status['status']}")
    print(f"   Calendar: {'✅' if status.get('calendar_connected') else '❌'} {'Conectado' if status.get('calendar_connected') else 'Desconectado'}")
    print(f"   Capacidades: {len(status.get('capabilities', []))}")
    
    if status.get('capabilities'):
        print(f"   📋 Funciones disponibles:")
        for capability in status['capabilities']:
            print(f"      • {capability}")

def handle_single_message(message: str, json_output: bool = False):
    """Maneja un mensaje único"""
    try:
        logger.info(f"📨 Procesando mensaje: {message}")
        response = process_user_message(message)
        
        if json_output:
            print(json.dumps(response, indent=2))
        else:
            print_response(response)
            
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        if json_output:
            print(json.dumps({"error": True, "message": str(e)}))
        else:
            print(f"❌ Error: {e}")

def print_response(response: Dict[str, Any]):
    """Imprime una respuesta de manera legible"""
    print(f"\n🤖 Respuesta:")
    print(f"   {response.get('message', 'Sin mensaje')}")
    
    if response.get('type') == 'events_list' and response.get('events'):
        print(f"\n📅 Eventos encontrados ({response.get('count', 0)}):")
        for i, event in enumerate(response['events'][:5], 1):
            print(f"   {i}. {event['formatted_date']} - {event['title']}")
        
        if len(response['events']) > 5:
            print(f"   ... y {len(response['events']) - 5} eventos más")
    
    elif response.get('type') == 'free_time' and response.get('free_slots'):
        print(f"\n🕐 Tiempo libre encontrado:")
        for slot in response['free_slots']:
            print(f"   • {slot['start']} - {slot['end']} ({slot['duration_minutes']} min)")

def handle_interactive_mode():
    """Maneja el modo interactivo"""
    print(f"""
🗣️  MODO INTERACTIVO ACTIVADO
Escribe tus solicitudes o 'quit' para salir.

Ejemplos:
• Mostrar mis eventos de esta semana
• Crear una reunión mañana a las 2pm
• ¿Tengo tiempo libre el viernes?
• Cancelar mi cita de las 3pm
""")
    
    while True:
        try:
            user_input = input("\n👤 Tú: ").strip()
            
            if user_input.lower() in ['quit', 'salir', 'exit']:
                print("👋 ¡Hasta luego!")
                break
            
            if not user_input:
                continue
            
            response = process_user_message(user_input)
            print(f"🤖 Agente: {response.get('message', 'Sin respuesta')}")
            
            # Mostrar información adicional si la hay
            if response.get('type') == 'events_list' and response.get('count', 0) > 0:
                events = response.get('events', [])
                print(f"   📊 {len(events)} eventos encontrados")
            
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            logger.error(f"Error en modo interactivo: {e}")
            print(f"❌ Error: {e}")

def handle_test_mode(json_output: bool = False):
    """Ejecuta tests básicos del sistema"""
    tests = [
        {
            'name': 'Status Check',
            'message': None,  # Test especial para status
            'expected_keys': ['status', 'agent_id', 'calendar_connected']
        },
        {
            'name': 'Show Events Intent',
            'message': 'Mostrar mis eventos de esta semana',
            'expected_keys': ['type', 'success', 'message']
        },
        {
            'name': 'Free Time Intent',
            'message': '¿Tengo tiempo libre mañana?',
            'expected_keys': ['type', 'success', 'message']
        },
        {
            'name': 'Help Intent',
            'message': 'Ayuda',
            'expected_keys': ['type', 'success', 'capabilities']
        },
        {
            'name': 'Unknown Intent',
            'message': 'xyz123 comando inexistente',
            'expected_keys': ['type', 'success', 'suggestions']
        }
    ]
    
    results = []
    
    if not json_output:
        print(f"\n🧪 EJECUTANDO TESTS BÁSICOS")
        print(f"{'='*50}")
    
    for i, test in enumerate(tests, 1):
        try:
            if not json_output:
                print(f"\n{i}. {test['name']}...")
            
            # Test especial para status
            if test['message'] is None:
                response = get_agent_status()
            else:
                response = process_user_message(test['message'])
            
            # Verificar que las claves esperadas estén presentes
            missing_keys = []
            for key in test['expected_keys']:
                if key not in response:
                    missing_keys.append(key)
            
            success = len(missing_keys) == 0
            
            result = {
                'test_name': test['name'],
                'success': success,
                'response_type': response.get('type', 'status'),
                'missing_keys': missing_keys,
                'message': response.get('message', ''),
                'error': None
            }
            
            if not json_output:
                status_icon = "✅" if success else "❌"
                print(f"   {status_icon} {'PASS' if success else 'FAIL'}")
                if missing_keys:
                    print(f"      Claves faltantes: {missing_keys}")
                if response.get('message'):
                    print(f"      Respuesta: {response['message'][:100]}...")
            
        except Exception as e:
            result = {
                'test_name': test['name'],
                'success': False,
                'error': str(e)
            }
            
            if not json_output:
                print(f"   ❌ ERROR: {e}")
        
        results.append(result)
    
    # Resumen
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    if json_output:
        print(json.dumps({
            'test_results': results,
            'summary': {
                'total': total,
                'passed': passed,
                'failed': total - passed,
                'success_rate': passed / total if total > 0 else 0
            },
            'timestamp': datetime.now().isoformat()
        }, indent=2))
    else:
        print(f"\n{'='*50}")
        print(f"📊 RESUMEN: {passed}/{total} tests pasaron ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 ¡Todos los tests pasaron!")
        else:
            print("⚠️ Algunos tests fallaron. Revisar logs para más detalles.")

def handle_agentverse_webhook(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Maneja webhooks desde AgentVerse
    Esta función sería llamada por el framework de AgentVerse
    
    Args:
        request_data: Datos de la solicitud desde AgentVerse
        
    Returns:
        Respuesta estructurada para AgentVerse
    """
    try:
        logger.info(f"📡 Webhook recibido de AgentVerse")
        
        # Extraer mensaje del usuario
        user_message = request_data.get('message', '')
        context = request_data.get('context', {})
        
        # Validar entrada
        if not user_message:
            return {
                'success': False,
                'error': 'No message provided',
                'timestamp': datetime.now().isoformat()
            }
        
        # Procesar mensaje
        response = process_user_message(user_message, context)
        
        # Agregar metadatos para AgentVerse
        response.update({
            'agent_id': settings.AGENT_ID,
            'timestamp': datetime.now().isoformat(),
            'version': settings.VERSION
        })
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error en webhook: {e}")
        return {
            'success': False,
            'error': str(e),
            'agent_id': settings.AGENT_ID,
            'timestamp': datetime.now().isoformat()
        }

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def validate_environment():
    """Valida que el entorno esté configurado correctamente"""
    try:
        settings.validate_settings()
        logger.info("✅ Entorno validado correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error de configuración: {e}")
        return False

def setup_signal_handlers():
    """Configura manejadores de señales para cierre limpio"""
    import signal
    
    def signal_handler(signum, frame):
        logger.info(f"📨 Señal {signum} recibida, cerrando limpiamente...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

# ==========================================
# INTEGRACIÓN CON AGENTVERSE
# ==========================================

class AgentVerseInterface:
    """
    Interfaz específica para AgentVerse
    Esta clase proporciona métodos que AgentVerse puede llamar directamente
    """
    
    @staticmethod
    def on_message(sender: str, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Método llamado cuando AgentVerse recibe un mensaje
        
        Args:
            sender: ID del remitente
            message: Mensaje recibido
            context: Contexto adicional
            
        Returns:
            Respuesta para enviar de vuelta
        """
        logger.info(f"📨 Mensaje de {sender}: {message}")
        
        response = process_user_message(message, context or {})
        
        # Formatear para AgentVerse
        return {
            'to': sender,
            'message': response.get('message', ''),
            'data': response,
            'agent_id': settings.AGENT_ID
        }
    
    @staticmethod
    def on_startup():
        """Método llamado cuando el agente se inicia en AgentVerse"""
        logger.info("🚀 Agente iniciado en AgentVerse")
        
        # Validar configuración
        if not validate_environment():
            raise RuntimeError("Fallo en validación del entorno")
        
        # Verificar conexión con Google Calendar
        status = get_agent_status()
        if not status.get('calendar_connected'):
            logger.warning("⚠️ Calendario no conectado - se necesita autenticación")
        
        logger.info("✅ Agente listo para recibir mensajes")
    
    @staticmethod
    def on_shutdown():
        """Método llamado cuando el agente se cierra en AgentVerse"""
        logger.info("🔄 Cerrando agente...")
        # Aquí podrías agregar limpieza específica si es necesario
        logger.info("👋 Agente cerrado limpiamente")
    
    @staticmethod
    def get_capabilities() -> Dict[str, Any]:
        """Devuelve las capacidades del agente para AgentVerse"""
        return {
            'agent_id': settings.AGENT_ID,
            'name': settings.AGENT_NAME,
            'version': settings.VERSION,
            'capabilities': [
                {
                    'name': 'calendar_management',
                    'description': 'Gestión completa del calendario de Google',
                    'actions': [
                        'show_events',
                        'create_event',
                        'update_event',
                        'delete_event',
                        'find_free_time'
                    ]
                }
            ],
            'intents': list(settings.INTENT_KEYWORDS.keys()),
            'supported_languages': ['es', 'en'],
            'timezone': settings.DEFAULT_TIMEZONE
        }

# ==========================================
# PUNTO DE ENTRADA
# ==========================================

if __name__ == "__main__":
    # Configurar manejadores de señales
    setup_signal_handlers()
    
    # Validar entorno
    if not validate_environment():
        sys.exit(1)
    
    # Ejecutar función principal
    main()

# ==========================================
# EXPORTACIONES PARA AGENTVERSE
# ==========================================

# Estas son las funciones que AgentVerse puede importar y usar
__all__ = [
    'process_user_message',
    'get_agent_status', 
    'handle_agentverse_webhook',
    'AgentVerseInterface'
]

# Ejemplo de cómo AgentVerse podría usar este módulo:
"""
from main import process_user_message, AgentVerseInterface

# Inicializar agente
AgentVerseInterface.on_startup()

# Procesar mensaje de usuario
response = process_user_message("Mostrar mis eventos de hoy")

# En un webhook
webhook_response = handle_agentverse_webhook({
    'message': 'Crear reunión mañana a las 2pm',
    'context': {'user_id': 'user123'}
})
"""