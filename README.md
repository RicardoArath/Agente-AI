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

**Desarrollado con ❤️ para AgentVerse**