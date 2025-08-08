#!/usr/bin/env python3
"""
SimpleVoice - Aplicación de Escritorio
Punto de entrada principal para la GUI 
"""

import sys
import os
from pathlib import Path
import multiprocessing

# Añadir directorio src al path para imports
if getattr(sys, 'frozen', False):
    # Ejecutándose como ejecutable empaquetado
    application_path = sys._MEIPASS
else:
    # Ejecutándose como script normal
    application_path = Path(__file__).parent

sys.path.insert(0, str(application_path))

LAST_DEP_ERROR = ""

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas"""
    missing_deps = []
    missing_tools = []
    
    try:
        import customtkinter
    except ImportError:
        missing_deps.append("customtkinter")
    
    try:
        import pyaudio
    except ImportError:
        missing_deps.append("pyaudio")
    
    try:
        import whisper
    except ImportError:
        missing_deps.append("openai-whisper")
    
    try:
        import pynput
    except ImportError:
        missing_deps.append("pynput")
    
    try:
        import pyperclip
    except ImportError:
        missing_deps.append("pyperclip")
    
    try:
        import pystray
    except ImportError:
        missing_deps.append("pystray")
    
    global LAST_DEP_ERROR
    if missing_deps:
        print("❌ Faltan las siguientes dependencias:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n💡 Instala con: pip install " + " ".join(missing_deps))
        LAST_DEP_ERROR = "Faltan dependencias de Python: " + ", ".join(missing_deps)
        return False

    # Verificar herramientas del sistema requeridas
    try:
        import shutil
        if shutil.which("ffmpeg") is None:
            missing_tools.append("ffmpeg")
    except Exception:
        missing_tools.append("ffmpeg")

    if missing_tools:
        print("❌ Faltan herramientas del sistema:")
        for tool in missing_tools:
            print(f"   - {tool}")
        print("\n💡 En macOS instala con: brew install ffmpeg")
        LAST_DEP_ERROR = "Faltan herramientas del sistema: " + ", ".join(missing_tools) + "\nInstala en macOS con: brew install ffmpeg"
        return False
    
    return True

def main():
    """Función principal"""
    print("🎙️ SimpleVoice - Iniciando aplicación de escritorio...")
    
    # Verificar dependencias
    if not check_dependencies():
        if hasattr(sys, 'frozen'):
            # En ejecutable empaquetado, mostrar error con messagebox
            try:
                import tkinter.messagebox as messagebox
                messagebox.showerror(
                    "Error de Dependencias",
                    (LAST_DEP_ERROR or "Faltan dependencias críticas. Por favor contacta al desarrollador.")
                )
            except:
                pass
        return 1
    
    # Importar e iniciar GUI
    try:
        from gui import SimpleVoiceGUI
        
        print("✅ Dependencias verificadas")
        print("🚀 Iniciando interfaz gráfica...")
        
        app = SimpleVoiceGUI()
        app.run()
        
    except Exception as e:
        print(f"❌ Error iniciando aplicación: {e}")
        # Mensaje específico si falta ffmpeg
        if "ffmpeg" in str(e).lower():
            print("💡 Parece que falta FFmpeg. En macOS instala con: brew install ffmpeg")
        
        # Mostrar error en GUI si es posible
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror(
                "Error de Aplicación",
                f"Error iniciando SimpleVoice:\n\n{e}\n\nRevisa los logs para más detalles."
            )
        except:
            pass
        
        return 1
    
    return 0

if __name__ == "__main__":
    # Protección necesaria para multiprocessing en macOS
    multiprocessing.set_start_method('spawn', force=True)
    sys.exit(main()) 