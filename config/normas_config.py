"""
Configuración específica para el módulo de normas
"""

import os
from pathlib import Path

# Ruta al archivo de normas
NORMAS_FILE = os.getenv('NORMAS_FILE', 'normas.json')

# Configuración de búsqueda de citas
DIAS_BUSQUEDA_CITA = int(os.getenv('DIAS_BUSQUEDA_CITA', 7))  # Buscar citas en los próximos 7 días
DURACION_CITA_DEFAULT = int(os.getenv('DURACION_CITA_MINUTOS', 30))  # 30 minutos por defecto

# Horario de atención (si no está en normas.json)
HORARIO_INICIO = os.getenv('HORARIO_INICIO', '08:00')
HORARIO_FIN = os.getenv('HORARIO_FIN', '16:00')
DIAS_ATENCION = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes']

# Configuración de mensajes
NOMBRE_DIRECTORA = os.getenv('NOMBRE_DIRECTORA', 'Dirección Académica')
EMAIL_DIRECTORA = os.getenv('EMAIL_DIRECTORA', 'direccion@escuela.edu.mx')

# Umbral de coincidencia para identificación de normas
UMBRAL_MATCH_MINIMO = float(os.getenv('UMBRAL_MATCH_NORMAS', 0.3))

# Logging
LOG_NORMAS_PROCESADAS = os.getenv('LOG_NORMAS_PROCESADAS', 'True').lower() == 'true'