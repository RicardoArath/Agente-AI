"""
Tests para los módulos NLP
"""
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nlp.intent_parser import IntentParser
from nlp.date_parser import DateParser
from agentverse.response_formatter import ResponseFormatter

def test_intent_parser():
    """Prueba el parser de intenciones"""
    print("\n" + "="*60)
    print("PRUEBA: Intent Parser")
    print("="*60)
    
    parser = IntentParser()
    
    test_messages = [
        "Mostrar mis eventos de esta semana",
        "Crear una reunión mañana a las 2pm",
        "¿Tengo tiempo libre el viernes?",
        "Cancelar mi cita de las 3pm",
        "Ayuda con el calendario"
    ]
    
    for message in test_messages:
        result = parser.parse(message)
        print(f"\nMensaje: '{message}'")
        print(f"  → Intent: {result['intent']}")
        print(f"  → Confidence: {result['confidence']:.2f}")
        
        # Prueba de extracción de detalles
        if result['intent'] == 'create_event':
            details = parser.extract_event_details(message)
            if details:
                print(f"  → Detalles: {details['title']} - {details['start']}")

def test_date_parser():
    """Prueba el parser de fechas"""
    print("\n" + "="*60)
    print("PRUEBA: Date Parser")
    print("="*60)
    
    parser = DateParser()
    
    test_messages = [
        "eventos de hoy",
        "citas de mañana",
        "reuniones de esta semana",
        "eventos del viernes",
        "agenda del próximo mes"
    ]
    
    for message in test_messages:
        result = parser.extract_date_range(message)
        print(f"\nMensaje: '{message}'")
        print(f"  → Inicio: {result['start_display']}")
        print(f"  → Fin: {result['end_display']}")

def test_response_formatter():
    """Prueba el formateador de respuestas"""
    print("\n" + "="*60)
    print("PRUEBA: Response Formatter")
    print("="*60)
    
    formatter = ResponseFormatter()
    
    # Simular respuesta de eventos
    sample_response = {
        'type': 'events_list',
        'events': [
            {
                'title': 'Reunión de equipo',
                'formatted_date': '2025-09-25 09:00',
                'location': 'Oficina',
                'id': 'test123'
            }
        ],
        'date_range': {
            'start': '2025-09-25',
            'end': '2025-09-27'
        }
    }
    
    formatted = formatter.format_response(sample_response, 'show_events')
    print(f"\nRespuesta formateada:")
    print(f"  → Tipo: {formatted['type']}")
    print(f"  → Mensaje: {formatted['message']}")
    print(f"  → Eventos: {formatted['data']['count']}")

def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "🧪 " + "="*58)
    print("EJECUTANDO TESTS DE MÓDULOS NLP")
    print("="*60)
    
    try:
        test_intent_parser()
        print("\n✅ Intent Parser: PASS")
    except Exception as e:
        print(f"\n❌ Intent Parser: FAIL - {e}")
    
    try:
        test_date_parser()
        print("\n✅ Date Parser: PASS")
    except Exception as e:
        print(f"\n❌ Date Parser: FAIL - {e}")
    
    try:
        test_response_formatter()
        print("\n✅ Response Formatter: PASS")
    except Exception as e:
        print(f"\n❌ Response Formatter: FAIL - {e}")
    
    print("\n" + "="*60)
    print("TESTS COMPLETADOS")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_all_tests()