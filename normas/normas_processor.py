"""
Procesador de normas académicas
Analiza mensajes de estudiantes y determina la gravedad de las faltas
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re


class NormasProcessor:
    """
    Procesa mensajes de estudiantes sobre faltas académicas y determina
    la acción apropiada según la gravedad
    """
    
    def __init__(self, normas_file_path: str = "normas.json"):
        """
        Inicializa el procesador de normas
        
        Args:
            normas_file_path: Ruta al archivo JSON con las normas
        """
        self.normas_file_path = normas_file_path
        self.normas_data = self._load_normas()
        
    def _load_normas(self) -> Dict:
        """Carga las normas desde el archivo JSON"""
        try:
            with open(self.normas_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"No se encontró el archivo de normas en {self.normas_file_path}"
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Error al leer el archivo de normas: {e}")
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza el texto para mejor matching"""
        text = text.lower()
        # Eliminar acentos
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ñ': 'n'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    def _match_keywords(self, mensaje: str, keywords: List[str]) -> float:
        """
        Calcula el score de coincidencia entre el mensaje y las keywords
        
        Returns:
            float: Score de coincidencia (0.0 a 1.0)
        """
        mensaje_norm = self._normalize_text(mensaje)
        matches = 0
        
        for keyword in keywords:
            keyword_norm = self._normalize_text(keyword)
            # Buscar coincidencia exacta o parcial
            if keyword_norm in mensaje_norm:
                matches += 1
            # Bonus por coincidencia de palabra completa
            elif re.search(r'\b' + re.escape(keyword_norm) + r'\b', mensaje_norm):
                matches += 1.5
        
        # Calcular score normalizado
        if len(keywords) > 0:
            return min(matches / len(keywords), 1.0)
        return 0.0
    
    def identificar_norma(self, mensaje: str) -> Optional[Dict]:
        """
        Identifica qué norma se está violando según el mensaje
        
        Args:
            mensaje: Mensaje del estudiante describiendo la falta
            
        Returns:
            Dict con la información de la norma identificada, o None si no se encuentra
        """
        mejor_match = None
        mejor_score = 0.0
        umbral_minimo = 0.3  # Score mínimo para considerar un match
        
        # Buscar en normas graves primero
        for norma in self.normas_data.get('normas_graves', []):
            score = self._match_keywords(mensaje, norma.get('keywords', []))
            if score > mejor_score and score >= umbral_minimo:
                mejor_score = score
                mejor_match = {
                    **norma,
                    'tipo': 'grave',
                    'match_score': score
                }
        
        # Si no hay match grave suficientemente fuerte, buscar en menores
        if mejor_score < 0.6:  # Si el match grave no es muy fuerte, considerar menores
            for norma in self.normas_data.get('normas_menores', []):
                score = self._match_keywords(mensaje, norma.get('keywords', []))
                if score > mejor_score and score >= umbral_minimo:
                    mejor_score = score
                    mejor_match = {
                        **norma,
                        'tipo': 'menor',
                        'match_score': score
                    }
        
        return mejor_match
    
    def procesar_mensaje(self, mensaje: str, nombre_estudiante: str = "estudiante") -> Dict:
        """
        Procesa el mensaje del estudiante y determina la acción a tomar
        
        Args:
            mensaje: Mensaje del estudiante
            nombre_estudiante: Nombre del estudiante (opcional)
            
        Returns:
            Dict con la respuesta y acción a realizar
        """
        norma = self.identificar_norma(mensaje)
        
        if not norma:
            return {
                'success': False,
                'tipo': 'desconocido',
                'mensaje': (
                    f"Hola {nombre_estudiante}, gracias por comunicarte. "
                    "No logré identificar exactamente la situación que describes. "
                    "¿Podrías darme más detalles sobre lo que sucedió? "
                    "Estoy aquí para ayudarte."
                ),
                'accion': None
            }
        
        # Determinar si requiere cita
        config = self.normas_data.get('configuracion', {})
        umbral_cita = config.get('umbral_gravedad_cita', 3)
        requiere_cita = (
            norma.get('gravedad', 0) >= umbral_cita or 
            norma.get('requiere_cita', False)
        )
        
        if requiere_cita:
            # Falta grave - requiere cita
            return {
                'success': True,
                'tipo': 'grave',
                'norma': norma,
                'requiere_cita': True,
                'mensaje_estudiante': norma.get('mensaje_estudiante', ''),
                'accion': 'agendar_cita',
                'duracion_cita': config.get('duracion_cita_minutos', 30)
            }
        else:
            # Falta menor - solo correo/mensaje
            return {
                'success': True,
                'tipo': 'menor',
                'norma': norma,
                'requiere_cita': False,
                'mensaje_estudiante': self._generar_mensaje_menor(norma, nombre_estudiante),
                'accion': 'enviar_correo'
            }
    
    def _generar_mensaje_menor(self, norma: Dict, nombre_estudiante: str) -> str:
        """
        Genera un mensaje empático para faltas menores
        
        Args:
            norma: Diccionario con información de la norma
            nombre_estudiante: Nombre del estudiante
            
        Returns:
            str: Mensaje personalizado
        """
        categoria = norma.get('categoria', 'situación')
        consecuencia = norma.get('consecuencia', '')
        accion_alumno = norma.get('accion_alumno', '')
        
        mensaje = f"""Hola {nombre_estudiante},

Gracias por ser honesto y comunicarte conmigo sobre la situación de {categoria.lower()}.

Entiendo que todos cometemos errores y lo importante es aprender de ellos. Aquí te cuento qué sigue:

📋 Consecuencia:
{consecuencia}

✅ Lo que necesitas hacer:
{accion_alumno}

Recuerda que estoy aquí para apoyarte en tu proceso de aprendizaje. Si tienes alguna pregunta o necesitas ayuda, no dudes en acercarte.

Confío en que esto no volverá a suceder y que seguirás creciendo como estudiante.

Con cariño y apoyo,
Dirección Académica"""
        
        return mensaje
    
    def get_horario_atencion(self) -> Dict:
        """
        Obtiene el horario de atención configurado
        
        Returns:
            Dict con horario de atención
        """
        config = self.normas_data.get('configuracion', {})
        return config.get('horario_atencion', {
            'dias': ['lunes', 'martes', 'miércoles', 'jueves', 'viernes'],
            'hora_inicio': '08:00',
            'hora_fin': '16:00'
        })