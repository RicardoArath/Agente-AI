"""
Punto de entrada principal del agente con funcionalidad de gestión de normas
"""

import sys
import argparse
from datetime import datetime, timedelta
import json
import pytz

# Importaciones existentes (mantén tus imports actuales)
from config.settings import settings
from calendar_service.calendar_client import GoogleCalendarClient
from nlp.message_processor import MessageProcessor
from utils.logger import setup_logging, get_logger
from normas.normas_processor import NormasProcessor  # NUEVO

logger = get_logger(__name__)

class AgentVerseInterface:
    """Interfaz para AgentVerse"""
    
    @staticmethod
    def on_startup():
        """Se ejecuta cuando el agente inicia"""
        logger.info(f"Agente {settings.AGENT_ID} iniciado correctamente")
        logger.info("Funcionalidad de gestión de normas activa")
        return {"status": "ready", "agent_id": settings.AGENT_ID}
    
    @staticmethod
    def on_message(sender: str, message: str) -> dict:
        """
        Procesa mensajes entrantes
        
        Args:
            sender: ID del usuario que envía el mensaje
            message: Contenido del mensaje
            
        Returns:
            dict: Respuesta del agente
        """
        logger.info(f"Mensaje recibido de {sender}: {message}")
        
        # Procesar el mensaje
        response = process_user_message(message, sender)
        
        return {
            "sender": settings.AGENT_ID,
            "message": response.get('message', ''),
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "tipo_respuesta": response.get('tipo', 'general')
            }
        }


def process_user_message(message: str, user_id: str = "usuario") -> dict:
    """
    Procesa mensajes del usuario con detección de faltas académicas
    
    Args:
        message: Mensaje del usuario
        user_id: ID del usuario
        
    Returns:
        dict: Respuesta procesada
    """
    try:
        # Inicializar procesadores
        normas_processor = NormasProcessor()
        
        # Primero verificar si es una consulta sobre normas/faltas
        palabras_clave_normas = [
            'falta', 'norma', 'problema', 'hice', 'cometí', 'error',
            'me pasó', 'sucedió', 'confesión', 'admitir'
        ]
        
        mensaje_lower = message.lower()
        es_consulta_normas = any(palabra in mensaje_lower for palabra in palabras_clave_normas)
        
        if es_consulta_normas:
            # Procesar como consulta de normas
            logger.info(f"Procesando mensaje como consulta de normas: {message}")
            resultado = normas_processor.procesar_mensaje(message, user_id)
            
            if not resultado.get('success'):
                return resultado
            
            if resultado.get('requiere_cita'):
                # Falta grave - agendar cita
                return manejar_falta_grave(resultado, user_id)
            else:
                # Falta menor - enviar mensaje
                return manejar_falta_menor(resultado, user_id)
        
        else:
            # Procesamiento normal de calendario (tu código existente)
            message_processor = MessageProcessor()
            calendar_client = GoogleCalendarClient()
            
            # Aquí va tu lógica existente de procesamiento de mensajes de calendario
            parsed = message_processor.parse_message(message)
            
            # Tu código existente para manejar eventos de calendario...
            # (mantén tu lógica actual aquí)
            
            return {
                'success': True,
                'message': 'Procesando tu solicitud de calendario...',
                'tipo': 'calendario'
            }
    
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}", exc_info=True)
        return {
            'success': False,
            'message': f'Lo siento, ocurrió un error: {str(e)}',
            'tipo': 'error'
        }


def manejar_falta_grave(resultado: dict, user_id: str) -> dict:
    """
    Maneja faltas graves agendando una cita en Google Calendar
    
    Args:
        resultado: Resultado del procesamiento de normas
        user_id: ID del usuario
        
    Returns:
        dict: Respuesta con detalles de la cita
    """
    try:
        logger.info(f"Manejando falta grave para usuario {user_id}")
        
        norma = resultado.get('norma', {})
        mensaje_estudiante = resultado.get('mensaje_estudiante', '')
        duracion = resultado.get('duracion_cita', 30)
        
        # Inicializar cliente de calendario
        calendar_client = GoogleCalendarClient()
        
        # Buscar primer espacio disponible con timezone
        tz = pytz.timezone(settings.DEFAULT_TIMEZONE)
        inicio_busqueda = datetime.now(tz)
        fin_busqueda = inicio_busqueda + timedelta(days=7)

        logger.info(f"🔍 Buscando espacios libres entre {inicio_busqueda.isoformat()} y {fin_busqueda.isoformat()}")
        
        espacios_libres = calendar_client.find_free_time(
            start_date=inicio_busqueda,
            end_date=fin_busqueda,
            duration_minutes=duracion
        )
        
        if not espacios_libres:
            logger.warning("No se encontraron espacios disponibles")
            return {
                'success': False,
                'message': (
                    f"{mensaje_estudiante}\n\n"
                    "En este momento no tengo espacios disponibles en mi agenda "
                    "para la próxima semana. Por favor, escríbeme directamente para "
                    "que podamos encontrar un horario que funcione para ambos."
                ),
                'tipo': 'grave_sin_espacio'
            }
        
        # Tomar el primer espacio disponible
        primer_espacio = espacios_libres[0]
        
        # Crear evento en el calendario (convertir datetime a string ISO)
        evento_creado = calendar_client.create_event(
            title=f"Reunión - {norma.get('categoria', 'Situación académica')}",
            start_datetime=primer_espacio['start'].isoformat(),
            end_datetime=primer_espacio['end'].isoformat(),
            description=f"Reunión sobre: {norma.get('descripcion', 'situación académica')}\n\nEstudiante: {user_id}",
            location="Oficina de Dirección"
        )
        
        # Formatear fecha para mensaje
        fecha_cita = primer_espacio['start'].strftime("%A %d de %B a las %I:%M %p")
        
        mensaje_final = f"""{mensaje_estudiante}

📅 Tu cita ha sido agendada para:
{fecha_cita}

📍 Ubicación: Oficina de Dirección
⏱️ Duración: {duracion} minutos

Por favor, sé puntual. Si por alguna razón no puedes asistir, avísame con anticipación para reprogramar.

Te espero con la mejor disposición para escucharte y apoyarte.

Con afecto,
Dirección Académica"""
        
        # IMPRIMIR EN CONSOLA (como solicitaste para los correos)
        print("\n" + "="*80)
        print("📧 NOTIFICACIÓN DE CITA AGENDADA")
        print("="*80)
        print(f"Para: {user_id}")
        print(f"Asunto: Cita agendada - {norma.get('categoria', 'Situación académica')}")
        print(f"Fecha de cita: {fecha_cita}")
        print("-"*80)
        print(mensaje_final)
        print("="*80 + "\n")
        
        logger.info(f"Cita agendada exitosamente: {evento_creado.get('id')}")
        
        return {
            'success': True,
            'message': mensaje_final,
            'tipo': 'grave_cita_agendada',
            'evento_id': evento_creado.get('id'),
            'fecha_cita': primer_espacio['start'].isoformat(),
            'norma': norma
        }
    
    except Exception as e:
        logger.error(f"Error agendando cita para falta grave: {e}", exc_info=True)
        return {
            'success': False,
            'message': (
                f"Entiendo la seriedad de la situación y quiero ayudarte. "
                f"Desafortunadamente tuve un problema técnico al agendar la cita. "
                f"Por favor, acércate directamente a mi oficina o escríbeme para "
                f"coordinar una reunión lo antes posible."
            ),
            'tipo': 'error_cita'
        }


def manejar_falta_menor(resultado: dict, user_id: str) -> dict:
    """
    Maneja faltas menores mostrando mensaje en consola
    
    Args:
        resultado: Resultado del procesamiento de normas
        user_id: ID del usuario
        
    Returns:
        dict: Respuesta con el mensaje
    """
    try:
        logger.info(f"Manejando falta menor para usuario {user_id}")
        
        norma = resultado.get('norma', {})
        mensaje = resultado.get('mensaje_estudiante', '')
        
        # IMPRIMIR EN CONSOLA (simulando envío de correo)
        print("\n" + "="*80)
        print("📧 NOTIFICACIÓN POR CORREO ELECTRÓNICO")
        print("="*80)
        print(f"Para: {user_id}")
        print(f"Asunto: Sobre tu situación - {norma.get('categoria', 'Situación académica')}")
        print(f"Gravedad: {norma.get('gravedad', 'N/A')} (Falta menor)")
        print("-"*80)
        print(mensaje)
        print("="*80 + "\n")
        
        logger.info(f"Notificación de falta menor enviada a {user_id}")
        
        return {
            'success': True,
            'message': mensaje,
            'tipo': 'menor_notificacion_enviada',
            'norma': norma
        }
    
    except Exception as e:
        logger.error(f"Error manejando falta menor: {e}", exc_info=True)
        return {
            'success': False,
            'message': (
                f"Gracias por comunicarte. Tomé nota de la situación "
                f"y me pondré en contacto contigo pronto."
            ),
            'tipo': 'error_notificacion'
        }


def get_agent_status() -> dict:
    """
    Obtiene el estado actual del agente
    
    Returns:
        dict: Estado del agente
    """
    try:
        calendar_client = GoogleCalendarClient()
        normas_processor = NormasProcessor()
        
        # Verificar conexión con calendario
        calendar_status = "conectado" if calendar_client.service else "desconectado"
        
        # Cargar estadísticas de normas
        normas_data = normas_processor.normas_data
        total_normas_menores = len(normas_data.get('normas_menores', []))
        total_normas_graves = len(normas_data.get('normas_graves', []))
        
        return {
            'status': 'active',
            'agent_id': settings.AGENT_ID,
            'calendar': calendar_status,
            'normas': {
                'menores': total_normas_menores,
                'graves': total_normas_graves,
                'total': total_normas_menores + total_normas_graves
            },
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        return {
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Agente de Calendario con Gestión de Normas Académicas'
    )
    parser.add_argument(
        '--message', '-m',
        help='Mensaje a procesar'
    )
    parser.add_argument(
        '--user', '-u',
        default='estudiante',
        help='Nombre del usuario/estudiante'
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
        help='Ejecutar tests de normas'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Salida en formato JSON'
    )
    
    args = parser.parse_args()
    
    # Inicializar agente
    AgentVerseInterface.on_startup()
    
    if args.status:
        # Mostrar estado
        status = get_agent_status()
        if args.json:
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            print("\n" + "="*60)
            print("📊 ESTADO DEL AGENTE")
            print("="*60)
            print(f"Estado: {status['status']}")
            print(f"Agent ID: {status['agent_id']}")
            print(f"Calendario: {status['calendar']}")
            if 'normas' in status:
                print(f"\nNormas cargadas:")
                print(f"  - Menores: {status['normas']['menores']}")
                print(f"  - Graves: {status['normas']['graves']}")
                print(f"  - Total: {status['normas']['total']}")
            print("="*60 + "\n")
    
    elif args.test:
        # Ejecutar tests
        ejecutar_tests()
    
    elif args.interactive:
        # Modo interactivo
        print("\n" + "="*60)
        print("🤖 AGENTE DE NORMAS ACADÉMICAS - MODO INTERACTIVO")
        print("="*60)
        print("Escribe 'salir' o 'exit' para terminar\n")
        
        while True:
            try:
                mensaje = input("Estudiante: ").strip()
                if mensaje.lower() in ['salir', 'exit', 'quit']:
                    print("\n¡Hasta luego! 👋\n")
                    break
                
                if not mensaje:
                    continue
                
                response = process_user_message(mensaje, args.user)
                print(f"\n🤖 Directora: {response['message']}\n")
                print("-"*60 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n¡Hasta luego! 👋\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
    
    elif args.message:
        # Procesar mensaje único
        response = process_user_message(args.message, args.user)
        
        if args.json:
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            print(f"\n{response['message']}\n")
    
    else:
        parser.print_help()


def ejecutar_tests():
    """Ejecuta tests de ejemplo del sistema de normas"""
    print("\n" + "="*60)
    print("🧪 EJECUTANDO TESTS DEL SISTEMA DE NORMAS")
    print("="*60 + "\n")
    
    tests = [
        {
            'nombre': 'Falta menor - Retardo',
            'mensaje': 'Hola, llegué tarde a clase hoy, fueron como 5 minutos',
            'usuario': 'Juan Pérez'
        },
        {
            'nombre': 'Falta grave - Falta de respeto',
            'mensaje': 'Maestra, necesito hablar con usted. Ayer le grité a mi compañero y le dije cosas feas',
            'usuario': 'María García'
        },
        {
            'nombre': 'Falta menor - Uniforme',
            'mensaje': 'No traigo el uniforme completo, se me olvidó la chamarra',
            'usuario': 'Pedro López'
        },
        {
            'nombre': 'Falta grave - Copia',
            'mensaje': 'Confieso que copié en el examen de matemáticas',
            'usuario': 'Ana Martínez'
        },
        {
            'nombre': 'Mensaje sin falta clara',
            'mensaje': 'Buenos días, ¿cómo está?',
            'usuario': 'Luis Torres'
        }
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n📝 Test {i}/{len(tests)}: {test['nombre']}")
        print(f"Usuario: {test['usuario']}")
        print(f"Mensaje: \"{test['mensaje']}\"")
        print("-"*60)
        
        try:
            response = process_user_message(test['mensaje'], test['usuario'])
            print(f"✅ Tipo de respuesta: {response.get('tipo', 'N/A')}")
            print(f"✅ Éxito: {response.get('success', False)}")
            if response.get('norma'):
                print(f"✅ Norma identificada: {response['norma'].get('id', 'N/A')} - {response['norma'].get('categoria', 'N/A')}")
            print()
        except Exception as e:
            print(f"❌ Error en test: {e}\n")
    
    print("="*60)
    print("✅ Tests completados")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()