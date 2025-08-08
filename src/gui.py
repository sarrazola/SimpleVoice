#!/usr/bin/env python3
"""
SimpleVoice - Interfaz Gráfica
GUI moderna con CustomTkinter
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
import threading
import sys
import os
import logging
from pathlib import Path
from typing import Optional
import multiprocessing
import queue
import time
import pystray
from PIL import Image, ImageDraw
import webbrowser

# Importar módulos locales
from recorder import VoiceRecorder

# Configurar CustomTkinter para apariencia nativa
ctk.set_appearance_mode("system")  # Seguir el tema del sistema
ctk.set_default_color_theme("blue")

class SimpleVoiceGUI:
    def __init__(self):
        """Inicializar la GUI"""
        self.recorder: Optional[VoiceRecorder] = None
        self.tray_icon = None
        self.window_visible = True
        self.is_recording = False
        self.tray_queue = multiprocessing.Queue()
        self.tray_status_queue = multiprocessing.Queue()
        self.tray_process = None
        
        # Configurar opciones de teclas disponibles (macOS-friendly)
        self.hotkey_options = {
            "F12": "f12",
            "F11": "f11",
            "F10": "f10",
            "F9": "f9",
            "F8": "f8",
            "F7": "f7",
            "F6": "f6",
            "F5": "f5",
            "F4": "f4",
            "F3": "f3",
            "F2": "f2",
            "F1": "f1",
            "Option+S": "alt+s",  # 'alt' es la tecla Option en pynput
            "Option+R": "alt+r",
            "Cmd+Shift+S": "cmd+shift+s",
            "Cmd+Shift+R": "cmd+shift+r",
            "Ctrl+Shift+S": "ctrl+shift+s",
            "Ctrl+Option+S": "ctrl+alt+s",
        }
        
        # Tecla seleccionada por defecto
        self.selected_hotkey = "F12"
        
        self._setup_logging()
        self.setup_window()
        self.setup_widgets()
        self.setup_hotkeys()
        self.init_recorder()
        
        # Configurar system tray con manejo específico para macOS (se puede desactivar con SIMPLEVOICE_NO_TRAY=1)
        if os.environ.get("SIMPLEVOICE_NO_TRAY", "0") != "1":
            self.setup_system_tray()
        else:
            print("ℹ️ System tray desactivado por variable de entorno SIMPLEVOICE_NO_TRAY=1")
        
        # Workaround para bug de macOS - forzar actualización después de mostrar la ventana
        self._apply_macos_window_fix()

        # Asegurar repintado inicial en macOS/VMs donde la ventana aparece gris
        self._schedule_force_redraw()
        # Atajo para refrescar manualmente (Cmd+R)
        if sys.platform == "darwin":
            try:
                self.root.bind_all('<Command-r>', lambda e: self._force_full_redraw())
            except Exception:
                pass
        
    def setup_window(self):
        """Configurar ventana principal"""
        self.root = ctk.CTk()
        self.root.title("SimpleVoice")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # Configurar protocolo de cierre (ocultar en lugar de cerrar)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        # Configurar grid para sidebar y contenido
        self.root.grid_columnconfigure(0, weight=0)  # Sidebar (no se expande)
        self.root.grid_columnconfigure(1, weight=1)  # Contenido (se expande)
        self.root.grid_rowconfigure(0, weight=1)
        
    def setup_widgets(self):
        """Configurar widgets de la interfaz"""
        # Sidebar
        self.setup_sidebar()

        # Frame principal para el contenido
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Header con título y configuraciones
        self.setup_header(self.main_frame)
        
        # Contenido principal con configuraciones y controles
        self.setup_main_content(self.main_frame)

        # Mostrar la vista "Home" por defecto
        self.show_view("home")
        
    def setup_sidebar(self):
        """Configurar el menú lateral"""
        sidebar_frame = ctk.CTkFrame(self.root, width=120, corner_radius=0)
        sidebar_frame.grid(row=0, column=0, sticky="nsw")
        sidebar_frame.grid_rowconfigure(5, weight=1)

        logo_label = ctk.CTkLabel(sidebar_frame, text="SimpleVoice", font=ctk.CTkFont(size=20, weight="bold"))
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Crear botones con workaround para macOS
        home_button = ctk.CTkButton(sidebar_frame, text="🏠 Home", command=lambda: self.show_view("home"))
        home_button.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self._add_macos_button_fix(home_button)

        settings_button = ctk.CTkButton(sidebar_frame, text="⚙️ Settings", command=lambda: self.show_view("settings"))
        settings_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self._add_macos_button_fix(settings_button)

        help_button = ctk.CTkButton(sidebar_frame, text="❓ Help", command=lambda: self.show_view("help"))
        help_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self._add_macos_button_fix(help_button)

        logs_button = ctk.CTkButton(sidebar_frame, text="📝 Logs", command=lambda: self.show_view("logs"))
        logs_button.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self._add_macos_button_fix(logs_button)

    def _add_macos_button_fix(self, button):
        """
        Workaround para el bug de Tkinter en macOS donde los botones no responden
        al primer clic sin movimiento del mouse. Este es un problema conocido en
        macOS Sonoma y versiones recientes.
        
        Referencia: https://github.com/python/cpython/issues/110218
        """
        if sys.platform == "darwin":  # Solo en macOS
            def on_enter(event):
                # Forzar actualización de estado cuando el mouse entra
                button.focus_set()
                button.update_idletasks()
                
            def on_leave(event):
                # Limpiar focus cuando el mouse sale
                self.root.focus_set()
                
            # Bind a eventos de mouse
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)

    def _apply_macos_window_fix(self):
        """
        Aplicar workaround adicional para el bug de macOS con eventos de mouse.
        Fuerza una actualización después de que la ventana esté completamente cargada.
        """
        if sys.platform == "darwin":  # Solo en macOS
            def force_window_update():
                try:
                    # Forzar que la ventana procese todos los eventos pendientes
                    self.root.update_idletasks()
                    self.root.update()
                    
                    # Simular un pequeño movimiento interno para activar los eventos
                    x = self.root.winfo_x()
                    y = self.root.winfo_y()
                    self.root.geometry(f"+{x}+{y}")
                    
                except Exception as e:
                    # Fallar silenciosamente si hay algún problema
                    pass
                    
            # Ejecutar el fix después de que la ventana esté completamente renderizada
            self.root.after(100, force_window_update)

    def _force_full_redraw(self):
        """Forzar un repintado completo de la ventana."""
        try:
            # Toggle de tamaño 1px para forzar recomposición de todos los widgets
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            self.root.geometry(f"{w+1}x{h+1}+{x}+{y}")
            self.root.update_idletasks()
            self.root.update()
            self.root.geometry(f"{w}x{h}+{x}+{y}")
            self.root.update_idletasks()
            self.root.update()
        except Exception:
            pass

    def _schedule_force_redraw(self):
        """Programar varios repintados al inicio para evitar ventana en gris."""
        try:
            # Ejecutar varios repintados en los primeros 2 segundos
            for i, delay in enumerate([50, 150, 300, 600, 1000, 1500]):
                self.root.after(delay, self._force_full_redraw)
        except Exception:
            pass

    def show_view(self, view_name):
        """Mostrar la vista seleccionada (home o help)"""
        # Ocultar todos los frames de contenido
        self.home_frame.grid_remove()
        self.help_frame.grid_remove()
        self.settings_frame.grid_remove()
        self.logs_frame.grid_remove()

        # Mostrar el frame seleccionado
        if view_name == "home":
            self.home_frame.grid()
        elif view_name == "help":
            self.help_frame.grid()
        elif view_name == "settings":
            self.settings_frame.grid()
        elif view_name == "logs":
            self.logs_frame.grid()
        
    def setup_header(self, parent):
        """Configurar header con título y estado"""
        header_frame = ctk.CTkFrame(parent, height=80, corner_radius=0, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_propagate(False)
        
        # Título principal y botones
        title_row = ctk.CTkFrame(header_frame, corner_radius=0, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="ew", pady=(10, 0))
        title_row.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            title_row,
            text="SimpleVoice",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Estado
        self.status_label = ctk.CTkLabel(
            header_frame,
            text="Status: Initializing...",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray50")
        )
        self.status_label.grid(row=1, column=0, pady=(5, 10), sticky="w")
        
    def setup_main_content(self, parent):
        """Configurar contenido principal"""
        # Frame para la vista "Home"
        self.home_frame = ctk.CTkFrame(parent, corner_radius=0, fg_color="transparent")
        self.home_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=0)
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame.grid_rowconfigure(1, weight=1)

        # Frame para la vista "Help"
        self.help_frame = ctk.CTkFrame(parent, corner_radius=0, fg_color="transparent")
        self.help_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=0)
        self.help_frame.grid_columnconfigure(0, weight=1)
        self.help_frame.grid_rowconfigure(0, weight=1)

        # Frame para la vista "Settings"
        self.settings_frame = ctk.CTkFrame(parent, corner_radius=0, fg_color="transparent")
        self.settings_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=0)
        self.settings_frame.grid_columnconfigure(0, weight=1)
        self.settings_frame.grid_rowconfigure(0, weight=0)

        # Frame para la vista "Logs"
        self.logs_frame = ctk.CTkFrame(parent, corner_radius=0, fg_color="transparent")
        self.logs_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=0)
        self.logs_frame.grid_columnconfigure(0, weight=1)
        self.logs_frame.grid_rowconfigure(0, weight=1)

        # Contenido de las vistas
        self.setup_settings_section(self.settings_frame)
        self.setup_recording_controls(self.home_frame)
        self.setup_transcription_section(self.home_frame)
        self.setup_logs_section(self.logs_frame)
        self.setup_help_content(self.help_frame)
        
    def setup_help_content(self, parent):
        """Configurar el contenido de la sección de ayuda"""
        # Crear un frame scrollable para el contenido de ayuda
        help_scrollable = ctk.CTkScrollableFrame(parent)
        help_scrollable.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Configurar el texto principal
        self.help_text_template = """🎙️ SimpleVoice - Voice Transcriptor

🌟 Open Source Alternative to Commercial Voice-to-Text Software
This project is completely FREE and open source!

📖 How to use:
1. Press {hotkey} or the "Start Recording" button to start
2. Speak clearly into the microphone
3. Press {hotkey} again or "Stop" to finish
4. The text is automatically transcribed
5. It's automatically copied to clipboard

🔧 Features:
• Global {hotkey} hotkey (configurable)
• AI transcription with OpenAI Whisper
• Auto-copy to clipboard
• Multi-language support with auto-detection
• Multiple AI models (Turbo, Base, Small, etc.)
• Detailed system logs
• Modern and friendly interface
• 100% private - works offline

📝 Notes:
• Requires functional microphone
• Optimized for multiple languages
• Logs are saved in ~/SimpleVoice/logs/
• Give microphone permissions to Terminal/Python

🌐 Open Source Project:"""
        
        # Label principal con el texto
        self.help_label = ctk.CTkLabel(
            help_scrollable,
            text=self.help_text_template.format(hotkey=self.selected_hotkey),
            font=ctk.CTkFont(size=14),
            justify="left",
            anchor="nw"
        )
        self.help_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")
        
        # Botón clickeable para GitHub
        self.github_button = ctk.CTkButton(
            help_scrollable,
            text="🔗 GitHub: https://github.com/sarrazola/SimpleVoice/",
            command=self.open_github,
            font=ctk.CTkFont(size=14, underline=True),
            fg_color="transparent",
            text_color=("blue", "lightblue"),
            hover_color=("lightgray", "darkgray"),
            cursor="hand2"
        )
        self.github_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self._add_macos_button_fix(self.github_button)
        
        # Resto del texto
        additional_text = """• License: MIT (most permissive open source license)
• Free to use, modify and distribute
• Report bugs or contribute features on GitHub

💡 Alternative to paid solutions"""
        
        self.additional_label = ctk.CTkLabel(
            help_scrollable,
            text=additional_text,
            font=ctk.CTkFont(size=14),
            justify="left",
            anchor="nw"
        )
        self.additional_label.grid(row=2, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="ew")
        
        # Configurar el grid del frame scrollable
        help_scrollable.grid_columnconfigure(0, weight=1)
    
    def open_github(self):
        """Abrir el enlace de GitHub en el navegador"""
        try:
            webbrowser.open("https://github.com/sarrazola/SimpleVoice/")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el enlace:\n{e}")

    def update_help_text(self):
        """Actualizar el texto de ayuda con la tecla seleccionada"""
        if hasattr(self, 'help_label'):
            self.help_label.configure(
                text=self.help_text_template.format(hotkey=self.selected_hotkey)
            )

    def setup_settings_section(self, parent):
        """Configurar sección de configuraciones"""
        settings_frame = ctk.CTkFrame(parent, corner_radius=10)
        settings_frame.grid(row=0, column=0, sticky="new", pady=(0, 20))
        settings_frame.grid_columnconfigure(0, weight=1)

        # Título de configuraciones
        settings_title = ctk.CTkLabel(
            settings_frame,
            text="Configuration",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        settings_title.grid(row=0, column=0, pady=(15, 20), sticky="w", padx=20)

        # Hotkey
        hotkey_label = ctk.CTkLabel(
            settings_frame,
            text="Hotkey:",
            font=ctk.CTkFont(size=12)
        )
        hotkey_label.grid(row=1, column=0, pady=(5, 0), sticky="w", padx=20)

        # Dropdown para seleccionar tecla
        self.hotkey_dropdown = ctk.CTkComboBox(
            settings_frame,
            values=list(self.hotkey_options.keys()),
            state="readonly",
            width=200,
            font=ctk.CTkFont(size=12),
            command=self.on_hotkey_change
        )
        self.hotkey_dropdown.set(self.selected_hotkey)
        self.hotkey_dropdown.grid(row=2, column=0, pady=(0, 20), sticky="w", padx=20)

        # Modelo
        model_label = ctk.CTkLabel(
            settings_frame,
            text="Transcription Model:",
            font=ctk.CTkFont(size=12)
        )
        model_label.grid(row=3, column=0, pady=(5, 0), sticky="w", padx=20)

        # Dropdown de modelos con información rica
        self.model_options = {
            "⚡ Tiny - Very Fast (39MB)": {
                "model": "tiny",
                "size": "39MB",
                "speed": "⚡⚡⚡⚡⚡",
                "accuracy": "⭐⭐",
                "description": "Ultra-fast basic transcription"
            },
            "🏃 Base - Fast (74MB)": {
                "model": "base",
                "size": "74MB",
                "speed": "⚡⚡⚡⚡",
                "accuracy": "⭐⭐⭐",
                "description": "Lightweight general use"
            },
            "⚖️ Small - Balanced (244MB)": {
                "model": "small",
                "size": "244MB",
                "speed": "⚡⚡⚡",
                "accuracy": "⭐⭐⭐⭐",
                "description": "Ideal speed/quality balance"
            },
            "🎯 Medium - Accurate (769MB)": {
                "model": "medium",
                "size": "769MB",
                "speed": "⚡⚡",
                "accuracy": "⭐⭐⭐⭐⭐",
                "description": "High accuracy for complex audio"
            },
            "👑 Large - Maximum (1.5GB)": {
                "model": "large",
                "size": "1.5GB",
                "speed": "⚡",
                "accuracy": "⭐⭐⭐⭐⭐",
                "description": "Maximum accuracy for critical cases"
            },
            "🚀 Turbo - Optimized (805MB)": {
                "model": "turbo",
                "size": "805MB",
                "speed": "⚡⚡⚡",
                "accuracy": "⭐⭐⭐⭐⭐",
                "description": "Fast and accurate (recommended)"
            }
        }

        self.model_dropdown = ctk.CTkComboBox(
            settings_frame,
            values=list(self.model_options.keys()),
            state="readonly",
            width=400,
            font=ctk.CTkFont(size=12),
            command=self.on_model_change
        )
        self.model_dropdown.set("🚀 Turbo - Optimized (805MB)")
        self.model_dropdown.grid(row=4, column=0, pady=(0, 5), sticky="w", padx=20)

        # Información del modelo seleccionado
        self.model_info_label = ctk.CTkLabel(
            settings_frame,
            text="Fast and accurate (recommended)\nSpeed: ⚡⚡⚡ | Accuracy: ⭐⭐⭐⭐⭐",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray50"),
            justify="left"
        )
        self.model_info_label.grid(row=5, column=0, pady=(0, 20), sticky="w", padx=20)

        # Idioma
        language_label = ctk.CTkLabel(
            settings_frame,
            text="Language:",
            font=ctk.CTkFont(size=12)
        )
        language_label.grid(row=6, column=0, pady=(5, 0), sticky="w", padx=20)

        # Dropdown de idiomas
        self.language_options = {
            "🌐 Auto-detect": None,
            "🇪🇸 Spanish": "es",
            "🇺🇸 English": "en",
            "🇫🇷 French": "fr",
            "🇩🇪 German": "de",
            "🇮🇹 Italian": "it",
            "🇵🇹 Portuguese": "pt",
            "🇯🇵 Japanese": "ja",
            "🇰🇷 Korean": "ko",
            "🇨🇳 Chinese": "zh",
            "🇷🇺 Russian": "ru",
            "🇳🇱 Dutch": "nl",
            "🇸🇪 Swedish": "sv",
            "🇳🇴 Norwegian": "no",
            "🇩🇰 Danish": "da"
        }

        self.language_dropdown = ctk.CTkComboBox(
            settings_frame,
            values=list(self.language_options.keys()),
            state="readonly",
            width=200,
            font=ctk.CTkFont(size=12),
            command=self.on_language_change
        )
        self.language_dropdown.set("🌐 Auto-detect")
        self.language_dropdown.grid(row=7, column=0, pady=(0, 20), sticky="w", padx=20)

    def on_hotkey_change(self, selection):
        """Callback cuando se cambia la tecla seleccionada"""
        self.selected_hotkey = selection
        self.add_log(f"🎹 Hotkey changed to: {selection}")
        
        # Ya no se necesita reiniciar el listener. El listener existente
        # leerá el nuevo valor de `self.selected_hotkey` dinámicamente.
        
        # Actualizar instrucciones en la interfaz
        self.update_recording_instructions()
        
        # Actualizar texto de ayuda
        self.update_help_text()

    def _setup_logging(self):
        """Configura el logging para la GUI para que también imprima en la consola."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def on_language_change(self, selection):
        """Callback cuando cambia el idioma seleccionado"""
        language_code = self.language_options.get(selection)
        if hasattr(self, 'recorder') and self.recorder:
            self.recorder.set_language(language_code)
            lang_text = "🌐 Auto-detect" if language_code is None else f"🌍 {language_code.upper()}"
            self.add_log(f"🗣️  Language changed to: {lang_text}")
        else:
            self.add_log("⚠️  Recorder not initialized yet")

    def on_model_change(self, selection):
        """Callback cuando cambia el modelo seleccionado"""
        self._update_model_info(selection)
        
        model_info = self.model_options[selection]
        model_name = model_info["model"]
        
        self.add_log(f"🤖 Model changed to: {selection}")
        
        # Verificar si el modelo está descargado
        if self.is_model_downloaded(model_name):
            self.add_log(f"✅ Model '{model_name}' is already downloaded")
            self.load_new_model(model_name)
        else:
            self.add_log(f"⬇️ Downloading model '{model_name}' ({model_info['size']})...")
            self.download_and_load_model(model_name, model_info)

    def _update_model_info(self, selection):
        """Actualizar el label con la info del modelo seleccionado"""
        model_info = self.model_options[selection]
        info_text = (
            f"{model_info['description']}\n"
            f"Speed: {model_info['speed']} | Accuracy: {model_info['accuracy']}"
        )
        self.model_info_label.configure(text=info_text)
    
    def is_model_downloaded(self, model_name):
        """Verificar si un modelo está descargado"""
        try:
            # Verificar en el directorio de cache de whisper
            cache_dir = os.path.expanduser("~/.cache/whisper")
            if not os.path.exists(cache_dir):
                return False
                
            # Buscar archivos del modelo en cache
            for file in os.listdir(cache_dir):
                if model_name in file and file.endswith('.pt'):
                    return True
            return False
        except:
            return False
    
    def download_and_load_model(self, model_name, model_info):
        """Descargar y cargar modelo en hilo separado"""
        def download_thread():
            try:
                self.root.after(0, lambda: self.update_status(f"⬇️ Downloading {model_name}..."))
                
                # Descargar modelo (Whisper lo hace automáticamente)
                import whisper
                new_model = whisper.load_model(model_name, device="cpu")
                
                # Actualizar recorder con nuevo modelo
                if self.recorder:
                    self.recorder.whisper_model = new_model
                    self.recorder.set_model(model_name)
                    self.root.after(0, lambda: self.add_log(f"🚀 Model '{model_name}' loaded successfully"))
                
                self.root.after(0, lambda: self.update_status("🟢 Ready"))
                
            except Exception as e:
                self.root.after(0, lambda: self.add_log(f"❌ Error downloading model '{model_name}': {e}", "ERROR"))
                self.root.after(0, lambda: self.update_status("❌ Error"))
                
                # Revertir selección al modelo anterior
                self.root.after(0, lambda: self.model_dropdown.set("🚀 Turbo - Optimized (805MB)"))
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def load_new_model(self, model_name):
        """Cargar modelo ya descargado"""
        def load_thread():
            try:
                self.root.after(0, lambda: self.update_status(f"🔄 Loading {model_name}..."))
                
                import whisper
                new_model = whisper.load_model(model_name, device="cpu")
                
                if self.recorder:
                    self.recorder.whisper_model = new_model
                    self.recorder.set_model(model_name)
                    self.root.after(0, lambda: self.add_log(f"🚀 Model '{model_name}' loaded successfully"))
                
                self.root.after(0, lambda: self.update_status("🟢 Ready"))
                
            except Exception as e:
                self.root.after(0, lambda: self.add_log(f"❌ Error loading model '{model_name}': {e}", "ERROR"))
                self.root.after(0, lambda: self.update_status("❌ Error"))
    
        threading.Thread(target=load_thread, daemon=True).start()
    
    def get_selected_model(self):
        """Obtener el modelo seleccionado"""
        current_selection = self.model_dropdown.get()
        return self.model_options[current_selection]["model"]
    
    def get_selected_language(self):
        """Obtener el código del idioma seleccionado"""
        current_selection = self.language_dropdown.get()
        return self.language_options.get(current_selection, None)
        
    def setup_recording_controls(self, parent):
        """Configurar controles de grabación"""
        controls_frame = ctk.CTkFrame(parent, corner_radius=10)
        controls_frame.grid(row=0, column=0, sticky="new", pady=(0, 20))
        controls_frame.grid_columnconfigure(0, weight=1)

        # Botón principal de grabación
        self.record_button = ctk.CTkButton(
            controls_frame,
            text="🎙️ Start Recording",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=60,
            command=self.toggle_recording
        )
        self.record_button.grid(row=0, column=0, pady=20, padx=20, sticky="ew")
        self._add_macos_button_fix(self.record_button)
        
        # Instrucción
        self.instruction_label = ctk.CTkLabel(
            controls_frame,
            text=f"Press {self.selected_hotkey} or the button to record. Speak clearly and press again to transcribe.",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray50"),
            wraplength=600
        )
        self.instruction_label.grid(row=1, column=0, pady=(0, 20), padx=20)

    def update_recording_instructions(self):
        """Actualizar las instrucciones de grabación con la tecla seleccionada"""
        if hasattr(self, 'instruction_label'):
            self.instruction_label.configure(
                text=f"Press {self.selected_hotkey} or the button to record. Speak clearly and press again to transcribe."
            )

    def setup_transcription_section(self, parent):
        """Configurar sección de transcripción"""
        trans_frame = ctk.CTkFrame(parent, corner_radius=10)
        trans_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        trans_frame.grid_columnconfigure(0, weight=1)
        trans_frame.grid_rowconfigure(1, weight=1)
        
        # Header de transcripción
        trans_header = ctk.CTkFrame(trans_frame, corner_radius=0, fg_color="transparent")
        trans_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        trans_header.grid_columnconfigure(0, weight=1)
        
        trans_title = ctk.CTkLabel(
            trans_header,
            text="Last transcription",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        trans_title.grid(row=0, column=0, sticky="w")
        
        # Botón copiar
        self.copy_button = ctk.CTkButton(
            trans_header,
            text="📋 Copy",
            width=80,
            height=28,
            command=self.copy_transcription
        )
        self.copy_button.grid(row=0, column=1, sticky="e")
        
        # Área de texto
        self.transcription_text = ctk.CTkTextbox(
            trans_frame,
            font=ctk.CTkFont(size=14),
            corner_radius=8
        )
        self.transcription_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 15))
        
        # Placeholder text
        self.transcription_text.insert("1.0", "Transcriptions will appear here...")
        
    def setup_logs_section(self, parent):
        """Configurar sección de logs"""
        logs_frame = ctk.CTkFrame(parent, corner_radius=10)
        logs_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        logs_frame.grid_columnconfigure(0, weight=1)
        logs_frame.grid_rowconfigure(1, weight=1)
        
        # Header de logs
        logs_header = ctk.CTkFrame(logs_frame, corner_radius=0, fg_color="transparent")
        logs_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        logs_header.grid_columnconfigure(0, weight=1)
        
        logs_title = ctk.CTkLabel(
            logs_header,
            text="System Logs",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        logs_title.grid(row=0, column=0, sticky="w")
        
        # Área de logs (siempre visible)
        self.logs_container = ctk.CTkFrame(logs_frame, corner_radius=8)
        self.logs_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(15, 15))
        self.logs_visible = True
        
        self.logs_text = ctk.CTkTextbox(
            self.logs_container,
            height=120,
            font=ctk.CTkFont(size=10, family="Monaco")
        )
        self.logs_text.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.logs_container.grid_columnconfigure(0, weight=1)
        self.logs_container.grid_rowconfigure(0, weight=1)
        
    def setup_system_tray(self):
        """Configurar icono del system tray usando multiprocessing para macOS"""
        try:
            # Iniciar proceso separado para el system tray
            self.tray_process = multiprocessing.Process(
                target=self.run_tray_process,
                args=(self.tray_queue, self.tray_status_queue),
                daemon=True
            )
            self.tray_process.start()
            
            # Iniciar monitor de eventos del tray
            self.root.after(100, self.check_tray_events)
            
            print("✅ System tray inicializado en proceso separado")
            
        except Exception as e:
            print(f"⚠️ No se pudo inicializar system tray: {e}")
            print("📱 La aplicación funcionará sin icono en la barra de menú")
            self.tray_process = None
            
    @staticmethod
    def run_tray_process(event_queue, status_queue):
        """Ejecutar system tray en proceso separado"""
        import threading
        try:
            # Crear icono para el tray
            def create_tray_icon_static(state='idle'):
                size = 64
                image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                draw = ImageDraw.Draw(image)
                
                if state == 'recording':
                    color = (220, 50, 50, 255)  # Rojo
                elif state == 'processing':
                    color = (138, 43, 226, 255) # Morado
                else:  # 'idle'
                    color = (50, 150, 220, 255)  # Azul
                    
                margin = 8
                draw.ellipse([margin, margin, size-margin, size-margin], fill=color)
                
                inner_margin = 16
                inner_color = tuple(min(255, c + 40) for c in color[:3]) + (255,)
                draw.ellipse([inner_margin, inner_margin, size-inner_margin, size-inner_margin], fill=inner_color)
                
                center_margin = 24
                center_color = (255, 255, 255, 255)
                draw.ellipse([center_margin, center_margin, size-center_margin, size-center_margin], fill=center_color)
                
                return image
            
            # Estado del tray
            current_state = 'idle'
            icon = None
            
            def on_record_click(icon_obj, item):
                event_queue.put(('toggle_recording',))
                
            def on_options_click(icon_obj, item):
                event_queue.put(('show_window',))
                
            def on_quit_click(icon_obj, item):
                event_queue.put(('quit',))
                icon_obj.stop()
            
            def create_menu():
                is_recording = current_state == 'recording'
                is_processing = current_state == 'processing'
                
                if is_recording:
                    record_text = "⏹️ Stop Recording"
                elif is_processing:
                    record_text = "⏳ Processing..."
                else:
                    record_text = "🎙️ Start Recording"

                return pystray.Menu(
                    pystray.MenuItem(record_text, on_record_click, enabled=not is_processing),
                    pystray.MenuItem("⚙️ Options", on_options_click),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem("❌ Quit", on_quit_click)
                )
            
            def update_tray_state():
                """Actualizar estado del tray basado en mensajes del proceso principal"""
                nonlocal current_state, icon
                try:
                    while not status_queue.empty():
                        status_update = status_queue.get_nowait()
                        if status_update[0] == 'state':
                            new_state = status_update[1]
                            if new_state != current_state:
                                current_state = new_state
                                # Actualizar icono y menú
                                icon.icon = create_tray_icon_static(current_state)
                                icon.menu = create_menu()
                except:
                    pass
            
            # Crear y ejecutar icono
            icon_image = create_tray_icon_static('idle')
            icon = pystray.Icon(
                "SimpleVoice",
                icon_image,
                "SimpleVoice - Voice Transcriptor",
                create_menu()
            )
            
            # Configurar verificación periódica de actualizaciones
            def check_updates():
                update_tray_state()
                # Programar siguiente verificación
                threading.Timer(0.1, check_updates).start()
            
            # Iniciar verificación de actualizaciones
            check_updates()
            
            icon.run()
            
        except Exception as e:
            print(f"⚠️ Error en proceso tray: {e}")
            
    def check_tray_events(self):
        """Verificar eventos del system tray"""
        try:
            while not self.tray_queue.empty():
                event = self.tray_queue.get_nowait()
                
                if event[0] == 'toggle_recording':
                    self.toggle_recording()
                elif event[0] == 'show_window':
                    self.show_window()
                elif event[0] == 'quit':
                    self.quit_application()
                    
        except queue.Empty:
            pass
        except Exception as e:
            print(f"⚠️ Error procesando eventos tray: {e}")
        
        # Programar próxima verificación
        if self.tray_process and self.tray_process.is_alive():
            self.root.after(100, self.check_tray_events)
        
    def hide_window(self):
        """Ocultar ventana (cerrar a system tray)"""
        self.root.withdraw()
        self.window_visible = False
        
    def show_window(self):
        """Mostrar ventana"""
        try:
            # Ejecutar en el hilo principal si es llamado desde otro hilo
            if threading.current_thread() != threading.main_thread():
                self.root.after_idle(self._show_window_safe)
            else:
                self._show_window_safe()
        except Exception as e:
            print(f"⚠️ Error mostrando ventana: {e}")
            
    def _show_window_safe(self):
        """Mostrar ventana de forma segura"""
        try:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            self.window_visible = True
        except Exception as e:
            print(f"⚠️ Error en _show_window_safe: {e}")
        

            
    def quit_application(self):
        """Salir completamente de la aplicación"""
        try:
            # Detener listener de teclado de forma segura
            if hasattr(self, 'listener') and self.listener is not None:
                try:
                    self.listener.stop()
                except:
                    pass
            
            # Terminar proceso del system tray
            if self.tray_process and self.tray_process.is_alive():
                self.tray_process.terminate()
                self.tray_process.join(timeout=1)
                
            # Limpiar colas de comunicación
            try:
                while not self.tray_queue.empty():
                    self.tray_queue.get_nowait()
                while not self.tray_status_queue.empty():
                    self.tray_status_queue.get_nowait()
            except:
                pass
                
            # Limpiar recursos
            if self.recorder:
                self.recorder.cleanup()
                
        except:
            pass
        
        self.root.quit()
        sys.exit(0)
        
    def setup_hotkeys(self):
        """Configurar hotkeys globales. Solo se debe llamar una vez."""
        # Prevenir la creación de múltiples listeners
        if hasattr(self, 'listener') and self.listener and self.listener.is_alive():
            return

        try:
            from pynput import keyboard
            
            # Inicializar estado de las teclas modificadoras
            self.pressed_keys = set()
            
            def on_key_press(key):
                try:
                    # Agregar la tecla al set de teclas presionadas
                    self.pressed_keys.add(key)
                    
                    # Obtener la tecla configurada
                    hotkey_code = self.hotkey_options.get(self.selected_hotkey, "f12")
                    
                    # Manejar teclas individuales (F1-F12)
                    if hotkey_code.startswith('f') and hotkey_code[1:].isdigit():
                        expected_key = getattr(keyboard.Key, hotkey_code, None)
                        if expected_key and key == expected_key:
                            self.root.after(0, self.toggle_recording)
                    
                    # Manejar combinaciones de teclas
                    elif '+' in hotkey_code:
                        self.check_combination(hotkey_code)
                        
                except (AttributeError, Exception) as e:
                    # Manejo silencioso de errores para no interrumpir el flujo
                    pass
            
            def on_key_release(key):
                try:
                    # Remover la tecla del set de teclas presionadas
                    self.pressed_keys.discard(key)
                except:
                    pass
            
            # Iniciar listener en hilo separado
            self.listener = keyboard.Listener(
                on_press=on_key_press,
                on_release=on_key_release,
                suppress=False
            )
            self.listener.start()
            
            self.add_log(f"🎹 Hotkeys configured: {self.selected_hotkey}")
            
        except ImportError:
            self.add_log("⚠️ No se pudieron configurar hotkeys globales")
        except Exception as e:
            self.add_log(f"⚠️ Error setting up hotkeys: {e}")
    
    def check_combination(self, hotkey_code):
        """Verificar si se presionó la combinación de teclas correcta"""
        try:
            from pynput import keyboard
            
            # Mapear combinaciones a teclas
            parts = hotkey_code.split('+')
            required_modifiers = []
            required_key = None
            
            for part in parts:
                part = part.strip().lower()
                if part == 'ctrl':
                    required_modifiers.append('ctrl')
                elif part == 'cmd':
                    required_modifiers.append('cmd')
                elif part == 'alt':
                    required_modifiers.append('alt')
                elif part == 'shift':
                    required_modifiers.append('shift')
                elif len(part) == 1:
                    required_key = part
            
            # Si no hay tecla requerida, no procesar
            if not required_key:
                return
            
            # Verificar que tenemos todos los modificadores necesarios
            current_modifiers = []
            has_required_key = False
            
            for pressed_key in self.pressed_keys:
                if pressed_key in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
                    current_modifiers.append('ctrl')
                elif pressed_key in [keyboard.Key.cmd_l, keyboard.Key.cmd_r]:
                    current_modifiers.append('cmd')
                elif pressed_key in [keyboard.Key.alt_l, keyboard.Key.alt_r]:
                    current_modifiers.append('alt')
                elif pressed_key in [keyboard.Key.shift_l, keyboard.Key.shift_r]:
                    current_modifiers.append('shift')
                elif hasattr(pressed_key, 'char') and pressed_key.char and pressed_key.char.lower() == required_key:
                    has_required_key = True
            
            # Verificar que tenemos exactamente los modificadores requeridos
            current_modifiers = list(set(current_modifiers))  # Remove duplicates
            required_modifiers = list(set(required_modifiers))  # Remove duplicates
            
            if set(current_modifiers) == set(required_modifiers) and has_required_key:
                # Pequeña pausa para evitar activaciones múltiples
                if not hasattr(self, 'last_combination_time') or time.time() - self.last_combination_time > 0.5:
                    self.last_combination_time = time.time()
                    self.root.after(0, self.toggle_recording)
                
        except Exception as e:
            # Manejo silencioso para evitar interrupciones
            pass

    def init_recorder(self):
        """Inicializar grabador en hilo separado"""
        def init_thread():
            try:
                # Obtener configuración seleccionada
                selected_language = self.get_selected_language()
                selected_model = self.get_selected_model()
                
                # Pasar una versión adaptada de `add_log` como callback
                def recorder_log_callback(message):
                    self.root.after(0, self.add_log, message, True)

                self.recorder = VoiceRecorder(
                    log_callback=recorder_log_callback, 
                    language=selected_language,
                    model=selected_model
                )
                self.root.after(0, lambda: self.update_status("🟢 Ready"))
            except Exception as e:
                self.root.after(0, lambda: self.add_log(f"❌ Initialization error: {e}"))
                self.root.after(0, lambda: self.update_status("❌ Error"))
        
        threading.Thread(target=init_thread, daemon=True).start()
        
    def toggle_recording(self):
        """Alternar grabación"""
        if not self.recorder:
            self.add_log("❌ Recorder not initialized")
            return
            
        if self.recorder.is_recording:
            # Parar grabación
            self.is_recording = False
            self.record_button.configure(text="⏳ Processing...", state="disabled")
            self.update_status("⏳ Processing...")
            self.update_tray_state('processing')
            
            def stop_thread():
                transcript = self.recorder.stop_recording()
                if transcript:
                    self.root.after(0, lambda: self.show_transcription(transcript))
                self.root.after(0, lambda: self.record_button.configure(text="🎙️ Start Recording", state="normal"))
                self.root.after(0, lambda: self.update_status("🟢 Ready"))
                self.root.after(0, self.update_tray_state, 'idle')
                
            threading.Thread(target=stop_thread, daemon=True).start()
        else:
            # Iniciar grabación
            if self.recorder.start_recording(hotkey=self.selected_hotkey):
                self.is_recording = True
                self.record_button.configure(text="⏹️ Stop Recording")
                self.update_status("🔴 Recording...")
                self.update_tray_state('recording')
                
    def update_tray_state(self, state: str):
        """Enviar actualización de estado al process del tray"""
        try:
            if self.tray_process and self.tray_process.is_alive():
                self.tray_status_queue.put(('state', state))
        except Exception as e:
            print(f"⚠️ Error actualizando estado tray: {e}")
                
    def show_transcription(self, text):
        """Mostrar transcripción en el área de texto"""
        self.transcription_text.delete("1.0", tk.END)
        self.transcription_text.insert("1.0", text)
        
        # Auto scroll al final
        self.transcription_text.see(tk.END)
        
    def copy_transcription(self):
        """Copiar transcripción al portapapeles"""
        text = self.transcription_text.get("1.0", tk.END).strip()
        if text:
            try:
                import pyperclip
                pyperclip.copy(text)
                self.add_log("📋 Text copied to clipboard")
            except:
                self.add_log("❌ Error copying to clipboard")
        else:
            self.add_log("⚠️ No text to copy")
            
    def add_log(self, message: str, from_recorder: bool = False):
        """Añadir mensaje a los logs de la GUI. La consola ya es manejada por el logger."""
        # Evitar que los mensajes del recorder se logueen dos veces en la consola
        if not from_recorder:
            self.logger.info(message)

        try:
            # Añadir al área de logs de la GUI
            if hasattr(self, 'logs_text') and self.logs_text:
                from datetime import datetime
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_entry = f"[{timestamp}] {message}\n"

                self.logs_text.insert(tk.END, log_entry)
                self.logs_text.see(tk.END)
                
                # Mantener solo últimas 100 líneas
                lines = self.logs_text.get("1.0", tk.END).split("\n")
                if len(lines) > 101:
                    self.logs_text.delete("1.0", f"{len(lines) - 100}.0")
                    
        except Exception as e:
            # Loguear este error específico a la consola
            self.logger.error(f"Error añadiendo log a la GUI: {e}")

    def update_status(self, status: str):
        """Actualizar estado"""
        self.status_label.configure(text=f"Status: {status}")
        
    def run(self):
        """Ejecutar la aplicación"""
        # Mostrar ventana al inicio
        self.root.deiconify()
        self.root.mainloop()

def main():
    """Función principal para GUI"""
    try:
        app = SimpleVoiceGUI()
        app.run()
    except Exception as e:
        print(f"❌ Error running GUI: {e}")
        messagebox.showerror("Error", f"Error running SimpleVoice:\n{e}")

if __name__ == "__main__":
    # Protección necesaria para multiprocessing en macOS
    multiprocessing.set_start_method('spawn', force=True)
    main() 