# 🤖 AgentVerse Calendar Agent

Un agente inteligente para gestionar tu calendario de Google a través de AgentVerse.

**Agent ID:** `agent1qgalpghkvfs6fpm262y8j6vpluvzhhhdl9xx24x5wdz4lcz90ffg5z47jac`

## 🚀 Características

- ✅ **Lectura de eventos** - Ve tus citas de cualquier período
- ➕ **Creación de eventos** - Agenda nuevas reuniones con lenguaje natural
- ✏️ **Actualización de eventos** - Modifica citas existentes
- 🗑️ **Eliminación de eventos** - Cancela citas fácilmente  
- 🕐 **Búsqueda de tiempo libre** - Encuentra espacios disponibles
- 🌐 **Procesamiento de lenguaje natural** - Entiende comandos en español
- 📱 **Integración completa con AgentVerse**

## 📋 Requisitos Previos

1. **Python 3.8+**
2. **Cuenta de Google** con Calendar habilitado
3. **Proyecto en Google Cloud Console** 
4. **Credenciales OAuth 2.0** configuradas

## 🛠️ Instalación

### 1. Clonar e instalar dependencias

```bash
# Clonar el proyecto
git clone <tu-repositorio>
cd calendar_agent

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la **Google Calendar API**
4. Crea credenciales **OAuth 2.0** para aplicación de escritorio
5. Agrega estas URIs de redirección:
   ```
   http://localhost:8080
   http://localhost:8000
   http://localhost
   ```
6. Descarga el archivo `credentials.json`

### 3. Configurar el proyecto

```bash
# Colocar el archivo de credenciales
mv ~/Downloads/client_secret_*.json ./credentials.json

# Verificar instalación
python main.py --status
```

## 🎯 Uso

### Línea de comandos

```bash
# Ver estado del agente
python main.py --status

# Procesar un mensaje específico
python main.py --message "Mostrar mis eventos de esta semana"

# Modo interactivo
python main.py --interactive

# Ejecutar tests
python main.py --test

# Salida en JSON
python main.py --message "¿Tengo tiempo libre mañana?" --json
```

### Desde código Python

```python
from main import process_user_message, get_agent_status

# Procesar mensaje del usuario
response = process_user_message("Crear reunión mañana a las 2pm")
print(response['message'])

# Obtener estado
status = get_agent_status()
print(f"Status: {status['status']}")
```

### Integración con AgentVerse

```python
from main import AgentVerseInterface

# Inicializar agente
AgentVerseInterface.on_startup()

# Procesar mensaje desde AgentVerse
response = AgentVerseInterface.on_message(
    sender="user123",
    message="¿Qué tengo programado para hoy?"
)
```

## 💬 Comandos Soportados

### 📅 Mostrar Eventos
- *"Mostrar mis eventos de esta semana"*
- *"¿Qué tengo programado para hoy?"*
- *"Ver mi agenda del próximo mes"*

### ➕ Crear Eventos
- *"Crear una reunión mañana a las 2pm"*
- *"Agendar cita con el doctor el viernes a las 10am"*
- *"Nueva reunión de equipo el lunes de 9am a 10am"*

### 🗑️ Eliminar Eventos
- *"Cancelar mi cita de las 3pm"*
- *"Eliminar la reunión de mañana"*

### ✏️ Actualizar Eventos  
- *"Mover mi reunión de las 2pm a las 3pm"*
- *"Cambiar el título de mi cita de las 10am"*

### 🕐 Tiempo Libre
- *"¿Tengo tiempo libre el viernes por la tarde?"*
- *"Buscar 2 horas libres mañana"*

## 🏗️ Estructura del Proyecto

```
calendar_agent/
├── 📁 config/           # Configuraciones
├── 📁 auth/            # Autenticación Google  
├── 📁 calendar/        # Cliente Google Calendar
├── 📁 nlp/             # Procesamiento de lenguaje
├── 📁 agentverse/      # Integración AgentVerse
├── 📁 utils/           # Utilidades generales
├── 📁 tests/           # Tests automatizados
├── 📁 logs/            # Archivos de log
├── 📄 main.py          # Punto de entrada
├── 📄 requirements.txt # Dependencias
└── 📄 credentials.json # Credenciales Google (no subir a git)
```

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env`:

```bash
# Configuración del agente
AGENT_ID=agent1qgalpghkvfs6fpm262y8j6vpluvzhhhdl9xx24x5wdz4lcz90ffg5z47jac
DEBUG=False
ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO

# Google Calendar
DEFAULT_TIMEZONE=America/Mexico_City
BUSINESS_HOURS_START=9
BUSINESS_HOURS_END=17
```

### Personalizar Configuración

Edita `config/settings.py` para:
- Cambiar zona horaria
- Modificar horas laborales  
- Ajustar palabras clave de NLP
- Configurar cache y rate limiting

## 🧪 Testing

```bash
# Ejecutar todos los tests
python main.py --test

# Tests específicos con pytest
pytest tests/ -v

# Test de integración
python -c "
from main import process_user_message
response = process_user_message('Mostrar eventos de hoy')
print('✅ Test pasó' if response['success'] else '❌ Test falló')
"
```

## 📊 Monitoring y Logs

Los logs se guardan en `logs/calendar_agent.log` con información detallada:

```bash
# Ver logs en tiempo real
tail -f logs/calendar_agent.log

# Buscar errores
grep "ERROR" logs/calendar_agent.log
```

## 🚨 Troubleshooting

### Error de Autenticación
```bash
# Eliminar token y re-autenticar
rm token.json
python main.py --status
```

### Error de Permisos
- Verificar que Google Calendar API esté habilitada
- Confirmar que las URIs de redirección sean correctas
- Revisar que los scopes incluyan permisos de escritura

### Error de Dependencias
```bash
# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

## 🔒 Seguridad

- ✅ **Credenciales encriptadas** - OAuth 2.0 con refresh tokens
- ✅ **Rate limiting** - Previene abuso de la API
- ✅ **Logging seguro** - No se registran datos sensibles
- ✅ **Validación de entrada** - Sanitización de inputs del usuario

## 🤝 Contribuir

1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📜 Licencia

MIT License - ver archivo `LICENSE` para detalles.

## 📞 Soporte

- **Issues:** [GitHub Issues](https://github.com/tu-usuario/calendar-agent/issues)
- **Documentación:** [Wiki del proyecto](https://github.com/tu-usuario/calendar-agent/wiki)
- **AgentVerse:** [Documentación oficial](https://docs.agentverse.ai/)

---

# 📚 Sistema de Gestión de Normas Académicas

## Nueva Funcionalidad Agregada

Este sistema ahora incluye un módulo inteligente para gestionar situaciones académicas y disciplinarias de forma empática y automatizada.

## 🎯 Características Principales

### 1. **Análisis Inteligente de Mensajes**
- Procesa mensajes de estudiantes usando NLP
- Identifica automáticamente el tipo y gravedad de la falta
- Clasifica en normas menores y graves

### 2. **Respuestas Personalizadas**
- Mensajes empáticos, comprensivos y amorosos
- Tono humano, no robotizado
- Adaptados a la gravedad de cada situación

### 3. **Gestión Automática**

#### Para Faltas Menores:
- ✉️ Envío de notificación (impresa en consola)
- 📋 Explicación clara de consecuencias
- ✅ Indicaciones sobre qué debe hacer el estudiante

#### Para Faltas Graves:
- 📅 Agendamiento automático de cita
- 🔍 Búsqueda de espacios libres en Google Calendar
- 🗓️ Creación de evento en el calendario
- 📧 Notificación con detalles de la cita

## 📁 Estructura de Archivos

```
calendar_agent/
├── normas/
│   ├── __init__.py                    # Módulo de normas
│   └── normas_processor.py            # Procesador principal
├── config/
│   └── normas_config.py               # Configuración de normas
├── tests/
│   └── test_normas.py                 # Tests unitarios
├── normas.json                        # Base de datos de normas
├── main.py                            # Punto de entrada modificado
└── README_NORMAS.md                   # Esta documentación
```

## 🚀 Instalación y Configuración

### 1. Asegúrate de tener las dependencias instaladas

```bash
pip install -r requirements.txt
```

### 2. Coloca el archivo `normas.json` en la raíz del proyecto

El archivo ya está configurado con ejemplos de normas menores y graves.

### 3. Configura variables de entorno (opcional)

Crea o actualiza tu archivo `.env`:

```bash
# Configuración de normas
NORMAS_FILE=normas.json
DIAS_BUSQUEDA_CITA=7
DURACION_CITA_MINUTOS=30
HORARIO_INICIO=08:00
HORARIO_FIN=16:00

# Información de contacto
NOMBRE_DIRECTORA=Dirección Académica
EMAIL_DIRECTORA=direccion@escuela.edu.mx

# Logging
LOG_NORMAS_PROCESADAS=True
```

## 💻 Uso del Sistema

### Modo Interactivo

```bash
python main.py --interactive
```

Ejemplo de interacción:
```
Estudiante: Hola, llegué tarde a clase hoy
🤖 Directora: [Mensaje empático con consecuencias y acciones a seguir]
```

### Procesar Mensaje Único

```bash
python main.py --message "Copié en el examen" --user "Juan Pérez"
```

### Ver Estado del Sistema

```bash
python main.py --status
```

Muestra:
- Estado del agente
- Conexión con Google Calendar
- Cantidad de normas cargadas

### Ejecutar Tests

```bash
python main.py --test
```

O con pytest:
```bash
pytest tests/test_normas.py -v
```

## 📋 Ejemplos de Uso

### Ejemplo 1: Falta Menor (Retardo)

**Entrada:**
```
"Llegué tarde a clase, fueron como 10 minutos"
```

**Salida:**
```
📧 NOTIFICACIÓN POR CORREO ELECTRÓNICO
===============================================
Para: estudiante
Asunto: Sobre tu situación - Puntualidad

Hola estudiante,

Gracias por ser honesto y comunicarte conmigo sobre
la situación de puntualidad.

Entiendo que todos cometemos errores y lo importante
es aprender de ellos...

[Consecuencias y acciones a seguir]
```

### Ejemplo 2: Falta Grave (Falta de Respeto)

**Entrada:**
```
"Le grité a mi compañero y le dije cosas ofensivas"
```

**Salida:**
```
📧 NOTIFICACIÓN DE CITA AGENDADA
===============================================
Entiendo que a veces las emociones pueden llevarnos
a actuar de formas que no representan quién realmente
somos...

📅 Tu cita ha sido agendada para:
Lunes 07 de octubre a las 10:00 AM

📍 Ubicación: Oficina de Dirección
⏱️ Duración: 30 minutos
```

## 🔧 Personalización

### Agregar Nuevas Normas

Edita `normas.json` y agrega nuevas normas en las secciones correspondientes:

```json
{
  "normas_menores": [
    {
      "id": "NM006",
      "categoria": "Nueva Categoría",
      "descripcion": "Descripción de la falta",
      "gravedad": 1,
      "keywords": ["palabra1", "palabra2"],
      "consecuencia": "Lo que sucederá...",
      "accion_alumno": "Lo que debe hacer..."
    }
  ]
}
```

### Modificar Umbrales

En `config/normas_config.py`:

```python
# Cambiar qué gravedad requiere cita
UMBRAL_GRAVEDAD_CITA = 3

# Cambiar días de búsqueda de citas
DIAS_BUSQUEDA_CITA = 14

# Cambiar duración de citas
DURACION_CITA_DEFAULT = 45
```

### Personalizar Mensajes

Los mensajes se generan en:
- `normas_processor.py` → método `_generar_mensaje_menor()`
- `main.py` → función `manejar_falta_grave()`

## 🧪 Testing

El sistema incluye tests completos:

```bash
# Tests unitarios
pytest tests/test_normas.py::TestNormasProcessor -v

# Tests de integración
pytest tests/test_normas.py::TestIntegracionNormas -v

# Tests con cobertura
pytest tests/test_normas.py --cov=normas --cov-report=html
```

## 📊 Flujo del Sistema

```
Mensaje del Estudiante
         ↓
    Análisis NLP
         ↓
  ¿Contiene keywords de normas?
         ↓
    Sí         No
    ↓          ↓
Identificar   Procesamiento
Norma       normal (calendario)
    ↓
¿Es grave?
    ↓
Sí          No
↓           ↓
Buscar      Generar
Espacio     Mensaje
Libre       Simple
↓           ↓
Agendar     Mostrar en
Cita        Consola
↓           ↓
Notificar   Notificar
```

## 🛠️ Troubleshooting

### Error: "No se encontró el archivo de normas"
**Solución:** Asegúrate de que `normas.json` esté en la raíz del proyecto.

### Error: "No se encontraron espacios disponibles"
**Solución:** 
1. Verifica que Google Calendar esté conectado
2. Aumenta `DIAS_BUSQUEDA_CITA` en la configuración
3. Revisa que el horario de atención sea correcto

### Las normas no se identifican correctamente
**Solución:**
1. Revisa las keywords en `normas.json`
2. Ajusta `UMBRAL_MATCH_MINIMO` en la configuración
3. Agrega más keywords variadas

## 📝 Notas Importantes

1. **Correos:** Actualmente se muestran en consola. Para enviarlos realmente, integra un servicio como SendGrid o Gmail API.

2. **Privacidad:** Los datos de estudiantes se manejan con confidencialidad. Asegúrate de cumplir con regulaciones de protección de datos.

3. **Backup:** Realiza backups regulares de `normas.json` y los logs.

## 🔜 Futuras Mejoras

- [ ] Envío real de correos electrónicos
- [ ] Dashboard web para ver estadísticas
- [ ] Notificaciones a padres/tutores
- [ ] Historial de incidencias por estudiante
- [ ] Reportes automáticos mensuales
- [ ] Integración con sistema escolar existente

## 📞 Soporte

Para dudas o problemas:
1. Revisa los logs en `logs/calendar_agent.log`
2. Ejecuta `python main.py --status` para diagnosticar
3. Consulta la documentación de AgentVerse

---

**Desarrollado con ❤️ para crear un entorno escolar más comprensivo y eficiente**