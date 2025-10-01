"""
Tests para el módulo de normas académicas
"""

import pytest
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from normas.normas_processor import NormasProcessor


class TestNormasProcessor:
    """Tests para el procesador de normas"""
    
    @pytest.fixture
    def processor(self):
        """Fixture para crear una instancia del procesador"""
        return NormasProcessor()
    
    def test_carga_normas(self, processor):
        """Test que verifica la carga correcta del archivo de normas"""
        assert processor.normas_data is not None
        assert 'normas_menores' in processor.normas_data
        assert 'normas_graves' in processor.normas_data
        assert 'configuracion' in processor.normas_data
    
    def test_identificar_retardo(self, processor):
        """Test para identificar falta de retardo"""
        mensaje = "Llegué tarde a clase hoy"
        norma = processor.identificar_norma(mensaje)
        
        assert norma is not None
        assert norma['tipo'] == 'menor'
        assert 'Puntualidad' in norma['categoria']
    
    def test_identificar_falta_respeto(self, processor):
        """Test para identificar falta de respeto (grave)"""
        mensaje = "Le grité a mi compañero y le dije cosas ofensivas"
        norma = processor.identificar_norma(mensaje)
        
        assert norma is not None
        assert norma['tipo'] == 'grave'
        assert norma['gravedad'] >= 3
    
    def test_identificar_copia(self, processor):
        """Test para identificar copia en examen"""
        mensaje = "Copié en el examen de matemáticas"
        norma = processor.identificar_norma(mensaje)
        
        assert norma is not None
        assert norma['tipo'] == 'grave'
        assert 'Integridad' in norma['categoria']
    
    def test_identificar_uniforme(self, processor):
        """Test para identificar problema con uniforme"""
        mensaje = "No traigo el uniforme completo"
        norma = processor.identificar_norma(mensaje)
        
        assert norma is not None
        assert norma['tipo'] == 'menor'
        assert 'Uniforme' in norma['categoria']
    
    def test_mensaje_sin_norma(self, processor):
        """Test para mensaje que no identifica ninguna norma"""
        mensaje = "Buenos días, ¿cómo está?"
        norma = processor.identificar_norma(mensaje)
        
        assert norma is None
    
    def test_procesar_falta_menor(self, processor):
        """Test para procesar una falta menor completa"""
        mensaje = "Olvidé mi tarea de español"
        resultado = processor.procesar_mensaje(mensaje, "Juan Pérez")
        
        assert resultado['success'] is True
        assert resultado['tipo'] == 'menor'
        assert resultado['requiere_cita'] is False
        assert resultado['accion'] == 'enviar_correo'
        assert 'Juan Pérez' in resultado['mensaje_estudiante']
    
    def test_procesar_falta_grave(self, processor):
        """Test para procesar una falta grave completa"""
        mensaje = "Tuve una pelea con otro estudiante"
        resultado = processor.procesar_mensaje(mensaje, "María López")
        
        assert resultado['success'] is True
        assert resultado['tipo'] == 'grave'
        assert resultado['requiere_cita'] is True
        assert resultado['accion'] == 'agendar_cita'
        assert resultado['duracion_cita'] > 0
    
    def test_normalizacion_texto(self, processor):
        """Test para la normalización de texto"""
        texto_con_acentos = "Está María José ñoño"
        texto_normalizado = processor._normalize_text(texto_con_acentos)
        
        assert 'á' not in texto_normalizado
        assert 'é' not in texto_normalizado
        assert 'ñ' not in texto_normalizado
        assert texto_normalizado == "esta maria jose nono"
    
    def test_match_keywords(self, processor):
        """Test para el sistema de matching de keywords"""
        mensaje = "Llegué tarde a mi clase de matemáticas"
        keywords = ["tarde", "retardo", "llegué tarde"]
        
        score = processor._match_keywords(mensaje, keywords)
        
        assert score > 0
        assert score <= 1.0
    
    def test_horario_atencion(self, processor):
        """Test para obtener horario de atención"""
        horario = processor.get_horario_atencion()
        
        assert 'dias' in horario
        assert 'hora_inicio' in horario
        assert 'hora_fin' in horario
        assert len(horario['dias']) > 0


# Tests de integración
class TestIntegracionNormas:
    """Tests de integración del sistema completo"""
    
    def test_flujo_completo_menor(self):
        """Test del flujo completo para una falta menor"""
        from main import process_user_message
        
        mensaje = "Olvidé mi libro de historia"
        resultado = process_user_message(mensaje, "Pedro Hernández")
        
        assert resultado is not None
        assert 'message' in resultado
        assert resultado.get('success') is not None
    
    def test_flujo_completo_grave(self):
        """Test del flujo completo para una falta grave"""
        from main import process_user_message
        
        mensaje = "Tuve un problema serio, le falté el respeto al profesor"
        resultado = process_user_message(mensaje, "Ana Torres")
        
        assert resultado is not None
        assert 'message' in resultado


if __name__ == '__main__':
    pytest.main([__file__, '-v'])