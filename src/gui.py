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
from pathlib import Path
from typing import Optional
import multiprocessing
import queue
import time
import pystray
from PIL import Image, ImageDraw

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
        
        self.setup_window()
        self.setup_widgets()
        self.setup_hotkeys()
        self.init_recorder()
        
        # Configurar system tray con manejo específico para macOS
        self.setup_system_tray()
        
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
        sidebar_frame.grid_rowconfigure(4, weight=1)

        logo_label = ctk.CTkLabel(sidebar_frame, text="SimpleVoice", font=ctk.CTkFont(size=20, weight="bold"))
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        home_button = ctk.CTkButton(sidebar_frame, text="🏠 Home", command=lambda: self.show_view("home"))
        home_button.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        settings_button = ctk.CTkButton(sidebar_frame, text="⚙️ Settings", command=lambda: self.show_view("settings"))
        settings_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        help_button = ctk.CTkButton(sidebar_frame, text="❓ Help", command=lambda: self.show_view("help"))
        help_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

    def show_view(self, view_name):
        """Mostrar la vista seleccionada (home o help)"""
        # Ocultar todos los frames de contenido
        self.home_frame.grid_remove()
        self.help_frame.grid_remove()
        self.settings_frame.grid_remove()

        # Mostrar el frame seleccionado
        if view_name == "home":
            self.home_frame.grid()
        elif view_name == "help":
            self.help_frame.grid()
        elif view_name == "settings":
            self.settings_frame.grid()
        
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

        # Contenido de las vistas
        self.setup_settings_section(self.settings_frame)
        self.setup_recording_controls(self.home_frame)
        self.setup_transcription_section(self.home_frame)
        self.setup_logs_section(self.home_frame)
        self.setup_help_content(self.help_frame)
        
    def setup_help_content(self, parent):
        """Configurar el contenido de la sección de ayuda"""
        help_text = """
        🎙️ SimpleVoice - Voice Transcriptor
        
        📖 How to use:
        1. Press F12 or the "RECORD" button to start
        2. Speak clearly into the microphone
        3. Press F12 again or "STOP" to finish
        4. The text is automatically transcribed
        5. It's automatically copied to clipboard
        
        🔧 Features:
        • Global F12 hotkey
        • AI transcription (Whisper)
        • Auto-copy to clipboard
        • Detailed system logs
        • Modern and friendly interface
        
        📝 Notes:
        • Requires functional microphone
        • Optimized for multiple languages
        • Logs are saved in ~/SimpleVoice/logs/
        """
        
        help_label = ctk.CTkLabel(
            parent,
            text=help_text,
            font=ctk.CTkFont(size=14),
            justify="left",
            anchor="nw"
        )
        help_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

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

        self.hotkey_value = ctk.CTkLabel(
            settings_frame,
            text="F12",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("blue", "lightblue")
        )
        self.hotkey_value.grid(row=2, column=0, pady=(0, 20), sticky="w", padx=20)

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
                "description": "Basic transcription, very fast"
            },
            "🏃 Base - Fast (74MB)": {
                "model": "base", 
                "size": "74MB",
                "speed": "⚡⚡⚡⚡",
                "accuracy": "⭐⭐⭐",
                "description": "General lightweight usage"
            },
            "⚖️ Small - Balanced (244MB)": {
                "model": "small",
                "size": "244MB", 
                "speed": "⚡⚡⚡",
                "accuracy": "⭐⭐⭐⭐",
                "description": "Speed/quality balance"
            },
            "🎯 Medium - Accurate (769MB)": {
                "model": "medium",
                "size": "769MB",
                "speed": "⚡⚡", 
                "accuracy": "⭐⭐⭐⭐⭐",
                "description": "High accuracy"
            },
            "👑 Large - Maximum (1.5GB)": {
                "model": "large",
                "size": "1.5GB",
                "speed": "⚡",
                "accuracy": "⭐⭐⭐⭐⭐", 
                "description": "Maximum accuracy"
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
            font=ctk.CTkFont(size=11),
            width=220,
            height=28,
            command=self.on_model_change,
            state="readonly"
        )
        self.model_dropdown.set("🚀 Turbo - Optimized (805MB)")  # Valor por defecto
        self.model_dropdown.grid(row=4, column=0, pady=(0, 20), sticky="w", padx=20)
        
        # Idioma
        language_label = ctk.CTkLabel(
            settings_frame,
            text="Language:",
            font=ctk.CTkFont(size=12)
        )
        language_label.grid(row=5, column=0, pady=(5, 0), sticky="w", padx=20)
        
        # Dropdown de idiomas
        self.language_options = {
            "🌐 Auto-detect": None,
            "🇺🇸 English": "en",
            "🇪🇸 Spanish": "es",
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
            font=ctk.CTkFont(size=12),
            width=160,
            height=28,
            command=self.on_language_change,
            state="readonly"
        )
        self.language_dropdown.set("🌐 Auto-detect")  # Valor por defecto
        self.language_dropdown.grid(row=6, column=0, pady=(0, 20), sticky="w", padx=20)
        
    def on_language_change(self, selection):
        """Callback cuando cambia el idioma seleccionado"""
        language_code = self.language_options[selection]
        self.add_log(f"🌍 Language changed to: {selection}")
        
        # Actualizar el recorder con el nuevo idioma
        if self.recorder:
            self.recorder.set_language(language_code)
            
    def on_model_change(self, selection):
        """Callback cuando cambia el modelo seleccionado"""
        model_info = self.model_options[selection]
        model_name = model_info["model"]
        
        self.add_log(f"🤖 Model changed to: {selection}")
        self.add_log(f"📊 Speed: {model_info['speed']} | Accuracy: {model_info['accuracy']}")
        
        # Verificar si el modelo está descargado
        if self.is_model_downloaded(model_name):
            self.add_log(f"✅ Model '{model_name}' is already downloaded")
            self.load_new_model(model_name)
        else:
            self.add_log(f"⬇️ Downloading model '{model_name}' ({model_info['size']})...")
            self.download_and_load_model(model_name, model_info)
    
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
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
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
        
        # Instrucción
        instruction_label = ctk.CTkLabel(
            controls_frame,
            text="Press F12 or the button to record. Speak clearly and press again to transcribe.",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray50"),
            wraplength=600
        )
        instruction_label.grid(row=1, column=0, pady=(0, 20), padx=20)
        
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
            text="Transcription",
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
        logs_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        logs_frame.grid_columnconfigure(0, weight=1)
        
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
        
        # Botones de logs
        logs_buttons = ctk.CTkFrame(logs_header, corner_radius=0, fg_color="transparent")
        logs_buttons.grid(row=0, column=1, sticky="e")
        
        self.logs_toggle = ctk.CTkButton(
            logs_buttons,
            text="👁️ Show",
            width=80,
            height=28,
            command=self.toggle_logs
        )
        self.logs_toggle.grid(row=0, column=0, padx=(0, 5))
        
        self.view_logs_button = ctk.CTkButton(
            logs_buttons,
            text="📄 File",
            width=80,
            height=28,
            command=self.open_log_file
        )
        self.view_logs_button.grid(row=0, column=1)
        
        # Área de logs (inicialmente oculta)
        self.logs_container = ctk.CTkFrame(logs_frame, corner_radius=8)
        self.logs_visible = False
        
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
            if hasattr(self, 'listener'):
                self.listener.stop()
        except:
            pass
        self.root.quit()
        sys.exit(0)
        
    def setup_hotkeys(self):
        """Configurar hotkeys globales"""
        try:
            from pynput import keyboard
            
            def on_key_press(key):
                try:
                    if key == keyboard.Key.f12:
                        # Ejecutar en hilo principal de GUI
                        self.root.after(0, self.toggle_recording)
                except AttributeError:
                    pass
            
            # Iniciar listener en hilo separado
            self.listener = keyboard.Listener(on_press=on_key_press)
            self.listener.start()
            
        except ImportError:
            self.add_log("⚠️ No se pudieron configurar hotkeys globales")
            
    def init_recorder(self):
        """Inicializar grabador en hilo separado"""
        def init_thread():
            try:
                # Obtener configuración seleccionada
                selected_language = self.get_selected_language()
                selected_model = self.get_selected_model()
                
                self.recorder = VoiceRecorder(
                    log_callback=self.add_log, 
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
            if self.recorder.start_recording():
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
            
    def toggle_logs(self):
        """Mostrar/ocultar logs"""
        if self.logs_visible:
            self.logs_container.grid_remove()
            self.logs_toggle.configure(text="👁️ Show")
            self.logs_visible = False
        else:
            self.logs_container.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
            self.logs_toggle.configure(text="👁️ Hide")
            self.logs_visible = True
            
    def add_log(self, message: str):
        """Añadir mensaje a los logs"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            
            # Añadir al área de logs
            self.logs_text.insert(tk.END, log_entry)
            self.logs_text.see(tk.END)
            
            # Mantener solo últimas 100 líneas
            lines = self.logs_text.get("1.0", tk.END).split("\n")
            if len(lines) > 100:
                self.logs_text.delete("1.0", f"{len(lines) - 100}.0")
                
        except Exception as e:
            print(f"Error añadiendo log: {e}")
            
    def update_status(self, status: str):
        """Actualizar estado"""
        self.status_label.configure(text=f"Status: {status}")
        
    def open_log_file(self):
        """Abrir archivo de logs"""
        if self.recorder:
            log_file = self.recorder.get_log_file_path()
            if log_file and os.path.exists(log_file):
                try:
                    if sys.platform == "darwin":  # macOS
                        os.system(f"open '{log_file}'")
                    elif sys.platform == "linux":  # Linux
                        os.system(f"xdg-open '{log_file}'")
                    else:  # Windows
                        os.system(f"start '{log_file}'")
                except:
                    messagebox.showinfo("Log File", f"File: {log_file}")
            else:
                messagebox.showwarning("Logs", "Log file not found")
                
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