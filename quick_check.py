#!/usr/bin/env python3
"""
Script de verificación rápida del sistema
Verifica que todos los módulos estén disponibles y configurados
"""
import sys
from pathlib import Path

def check_python_version():
    """Verifica la versión de Python"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (se requiere 3.8+)")
        return False

def check_module(module_name, display_name=None):
    """Verifica que un módulo se pueda importar"""
    display = display_name or module_name
    try:
        __import__(module_name)
        print(f"✅ {display}")
        return True
    except ImportError as e:
        print(f"❌ {display} - {e}")
        return False

def check_project_structure():
    """Verifica la estructura de carpetas del proyecto"""
    required_dirs = [
        'config',
        'utils',
        'calendar_service',
        'nlp',
        'agentverse',
        'logs'
    ]
    
    missing = []
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing.append(dir_name)
    
    if not missing:
        print(f"✅ Estructura de carpetas completa")
        return True
    else:
        print(f"❌ Faltan carpetas: {', '.join(missing)}")
        return False

def check_credentials():
    """Verifica que existan archivos de credenciales"""
    creds_file = Path('credentials') / 'credentials.json'
    
    if creds_file.exists():
        print(f"✅ Archivo de credenciales encontrado")
        return True
    else:
        print(f"⚠️  Archivo de credenciales no encontrado")
        print(f"    Coloca tu credentials.json en: {creds_file}")
        return False

def main():
    print("\n" + "="*60)
    print("VERIFICACIÓN RÁPIDA DEL SISTEMA")
    print("="*60 + "\n")
    
    checks = []
    
    # Python
    print("🐍 Python:")
    checks.append(check_python_version())
    
    # Dependencias core
    print("\n📦 Dependencias Core:")
    checks.append(check_module('google.auth', 'google-auth'))
    checks.append(check_module('googleapiclient', 'google-api-python-client'))
    checks.append(check_module('dateutil', 'python-dateutil'))
    
    # Módulos del proyecto
    print("\n🔧 Módulos del Proyecto:")
    checks.append(check_module('config.settings', 'config.settings'))
    checks.append(check_module('utils.logger', 'utils.logger'))
    checks.append(check_module('utils.exceptions', 'utils.exceptions'))
    checks.append(check_module('nlp.intent_parser', 'nlp.intent_parser'))
    checks.append(check_module('nlp.date_parser', 'nlp.date_parser'))
    checks.append(check_module('agentverse.response_formatter', 'response_formatter'))
    
    # Estructura
    print("\n📁 Estructura:")
    checks.append(check_project_structure())
    
    # Credenciales
    print("\n🔑 Credenciales:")
    creds_ok = check_credentials()
    
    # Resumen
    print("\n" + "="*60)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total and creds_ok:
        print(f"🎉 TODO LISTO ({passed}/{total} checks pasaron)")
        print("\n Siguiente paso: python main.py --status")
    elif passed == total:
        print(f"⚠️  CASI LISTO ({passed}/{total} checks pasaron)")
        print("\n🔸 Falta: Configurar credenciales de Google")
        print("   1. Ve a https://console.cloud.google.com")
        print("   2. Descarga tu credentials.json")
        print("   3. Colócalo en: credentials/credentials.json")
    else:
        print(f"❌ FALTAN COMPONENTES ({passed}/{total} checks pasaron)")
        print("\n🔸 Ejecuta: pip install -r requirements.txt")
    
    print("="*60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)