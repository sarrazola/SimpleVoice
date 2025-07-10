#!/usr/bin/env python3
"""
SimpleVoice - Script de Construcción
Automatiza el proceso de empaquetado con PyInstaller
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Imprimir banner de inicio"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                  🎙️  SimpleVoice Builder                      ║
    ║                Construcción de App de Escritorio             ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Verificar versión de Python"""
    print("🐍 Verificando versión de Python...")
    
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_dependencies():
    """Verificar dependencias necesarias"""
    print("📦 Verificando dependencias...")
    
    missing_packages = []
    
    # Verificar PyInstaller (se ejecuta como módulo)
    try:
        result = subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ pyinstaller")
        else:
            missing_packages.append('pyinstaller')
            print("   ❌ pyinstaller")
    except:
        missing_packages.append('pyinstaller')
        print("   ❌ pyinstaller")
    
    # Verificar otros paquetes
    regular_packages = [
        ('customtkinter', 'customtkinter'),
        ('pyaudio', 'pyaudio'),
        ('whisper', 'whisper'),
        ('pynput', 'pynput'),
        ('pyperclip', 'pyperclip')
    ]
    
    for pip_name, import_name in regular_packages:
        try:
            __import__(import_name)
            print(f"   ✅ {pip_name}")
        except ImportError:
            missing_packages.append(pip_name)
            print(f"   ❌ {pip_name}")
    
    if missing_packages:
        print(f"\n❌ Faltan las siguientes dependencias:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print(f"\n💡 Instala con: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def clean_build_directories():
    """Limpiar directorios de construcción anteriores"""
    print("🧹 Limpiando directorios de construcción...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__', 'src/__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   🗑️  Eliminado: {dir_name}")
    
    print("✅ Limpieza completada")

def install_dependencies():
    """Instalar dependencias desde requirements-gui.txt"""
    print("📦 Instalando dependencias...")
    
    if not os.path.exists('requirements-gui.txt'):
        print("❌ No se encontró requirements-gui.txt")
        return False
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements-gui.txt'
        ], check=True)
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def build_application():
    """Construir aplicación con PyInstaller"""
    print("🔨 Construyendo aplicación...")
    
    if not os.path.exists('SimpleVoice.spec'):
        print("❌ No se encontró SimpleVoice.spec")
        return False
    
    try:
        # Ejecutar PyInstaller
        cmd = [sys.executable, '-m', 'PyInstaller', 'SimpleVoice.spec', '--noconfirm']
        
        print(f"📝 Ejecutando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Construcción completada exitosamente")
            print(f"📄 Logs de construcción guardados")
            
            # Mostrar archivos creados
            list_output_files()
            return True
        else:
            print("❌ Error en la construcción")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando PyInstaller: {e}")
        return False

def list_output_files():
    """Listar archivos de salida generados"""
    print("📁 Archivos generados:")
    
    dist_dir = Path('dist')
    if dist_dir.exists():
        for item in dist_dir.iterdir():
            if item.is_file():
                size = item.stat().st_size / (1024 * 1024)  # MB
                print(f"   📄 {item.name} ({size:.1f} MB)")
            elif item.is_dir():
                print(f"   📁 {item.name}/")
                # Mostrar contenido del directorio
                for sub_item in item.iterdir():
                    if sub_item.is_file():
                        size = sub_item.stat().st_size / (1024 * 1024)  # MB
                        print(f"      📄 {sub_item.name} ({size:.1f} MB)")

def create_distribution_package():
    """Crear paquete de distribución"""
    print("📦 Creando paquete de distribución...")
    
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("❌ No se encontró el directorio dist")
        return False
    
    # Determinar nombre del paquete según la plataforma
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system == 'darwin':
        # macOS
        app_bundle = dist_dir / 'SimpleVoice.app'
        if app_bundle.exists():
            package_name = f"SimpleVoice-macOS-{arch}"
            zip_name = f"{package_name}.zip"
            
            try:
                # Crear ZIP del bundle .app
                shutil.make_archive(package_name, 'zip', dist_dir, 'SimpleVoice.app')
                print(f"✅ Paquete creado: {zip_name}")
                return True
            except Exception as e:
                print(f"❌ Error creando paquete: {e}")
                return False
    else:
        # Linux/Windows
        executable = dist_dir / 'SimpleVoice'
        if not executable.exists():
            executable = dist_dir / 'SimpleVoice.exe'
        
        if executable.exists():
            package_name = f"SimpleVoice-{system}-{arch}"
            zip_name = f"{package_name}.zip"
            
            try:
                # Crear ZIP del ejecutable
                shutil.make_archive(package_name, 'zip', dist_dir)
                print(f"✅ Paquete creado: {zip_name}")
                return True
            except Exception as e:
                print(f"❌ Error creando paquete: {e}")
                return False
    
    print("❌ No se encontró el ejecutable construido")
    return False

def create_readme():
    """Crear README para distribución"""
    print("📝 Creando README de distribución...")
    
    system = platform.system().lower()
    
    if system == 'darwin':
        readme_content = """
# SimpleVoice - Transcriptor de Voz

## 🎙️ Instalación en macOS

1. Descarga el archivo SimpleVoice-macOS-[arch].zip
2. Descomprime el archivo
3. Mueve SimpleVoice.app a tu carpeta Aplicaciones
4. Haz doble clic en SimpleVoice.app para abrir

## ⚠️ Permisos

La primera vez que ejecutes la aplicación, macOS te pedirá permisos para:
- Acceder al micrófono
- Ejecutar la aplicación (puede requerir ir a Preferencias > Seguridad)

## 🎯 Uso

1. Presiona F12 o el botón "GRABAR" para iniciar la grabación
2. Habla claramente al micrófono
3. Presiona F12 nuevamente para parar y transcribir
4. El texto se copia automáticamente al portapapeles

## 📊 Logs

Los logs se guardan en: ~/SimpleVoice/logs/
Usa el botón "Ver Logs" en la aplicación para acceder a ellos.

## 🔧 Soporte

Si tienes problemas, revisa los logs o contacta al desarrollador.
        """
    else:
        readme_content = """
# SimpleVoice - Transcriptor de Voz

## 🎙️ Instalación

1. Descarga el archivo SimpleVoice-[system]-[arch].zip
2. Descomprime el archivo
3. Ejecuta SimpleVoice (o SimpleVoice.exe en Windows)

## 🎯 Uso

1. Presiona F12 o el botón "GRABAR" para iniciar la grabación
2. Habla claramente al micrófono
3. Presiona F12 nuevamente para parar y transcribir
4. El texto se copia automáticamente al portapapeles

## 📊 Logs

Los logs se guardan en: ~/SimpleVoice/logs/
Usa el botón "Ver Logs" en la aplicación para acceder a ellos.

## 🔧 Soporte

Si tienes problemas, revisa los logs o contacta al desarrollador.
        """
    
    with open('README-Distribution.md', 'w', encoding='utf-8') as f:
        f.write(readme_content.strip())
    
    print("✅ README creado: README-Distribution.md")

def show_final_instructions():
    """Mostrar instrucciones finales"""
    print("\n" + "="*60)
    print("🎉 ¡CONSTRUCCIÓN COMPLETADA!")
    print("="*60)
    
    print("\n📁 Archivos generados:")
    print("   • dist/ - Contiene el ejecutable/app")
    print("   • SimpleVoice-[platform].zip - Paquete de distribución")
    print("   • README-Distribution.md - Instrucciones para usuarios")
    
    print("\n🚀 Próximos pasos:")
    print("   1. Prueba el ejecutable en dist/")
    print("   2. Comparte el archivo ZIP con usuarios")
    print("   3. Incluye el README con instrucciones")
    
    print("\n💡 Notas importantes:")
    print("   • Los logs se guardan en ~/SimpleVoice/logs/")
    print("   • La aplicación necesita permisos de micrófono")
    print("   • F12 es la tecla de acceso rápido global")
    
    print("\n📊 Ubicación de logs durante desarrollo:")
    print("   • Revisa ~/SimpleVoice/logs/ para depuración")
    
    print("\n✅ ¡Listo para distribuir!")

def main():
    """Función principal del script de construcción"""
    print_banner()
    
    # Verificar entorno
    if not check_python_version():
        return 1
    
    # Limpiar directorios anteriores
    clean_build_directories()
    
    # Instalar dependencias
    if not install_dependencies():
        return 1
    
    # Verificar dependencias
    if not check_dependencies():
        return 1
    
    # Construir aplicación
    if not build_application():
        return 1
    
    # Crear paquete de distribución
    if not create_distribution_package():
        print("⚠️  No se pudo crear el paquete de distribución")
    
    # Crear README
    create_readme()
    
    # Mostrar instrucciones finales
    show_final_instructions()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 