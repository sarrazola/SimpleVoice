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
        
        # Configurar grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
    def setup_widgets(self):
        """Configurar widgets de la interfaz"""
        # Frame principal sin border para look más nativo
        main_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Header con título y configuraciones
        self.setup_header(main_frame)
        
        # Contenido principal con configuraciones y controles
        self.setup_main_content(main_frame)
        
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
        
        # Botones de menú
        menu_buttons = ctk.CTkFrame(title_row, corner_radius=0, fg_color="transparent")
        menu_buttons.grid(row=0, column=1, sticky="e")
        
        # Botón configuraciones
        settings_btn = ctk.CTkButton(
            menu_buttons,
            text="⚙️",
            width=30,
            height=30,
            font=ctk.CTkFont(size=14),
            command=self.show_settings
        )
        settings_btn.grid(row=0, column=0, padx=(0, 5))
        
        # Botón ayuda
        help_btn = ctk.CTkButton(
            menu_buttons,
            text="?",
            width=30,
            height=30,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.show_help
        )
        help_btn.grid(row=0, column=1)
        
        # Estado
        self.status_label = ctk.CTkLabel(
            header_frame,
            text="Estado: Inicializando...",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray50")
        )
        self.status_label.grid(row=1, column=0, pady=(5, 10), sticky="w")
        
    def setup_main_content(self, parent):
        """Configurar contenido principal"""
        content_frame = ctk.CTkFrame(parent, corner_radius=0, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=0)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(2, weight=1)
        
        # Configuraciones visibles
        self.setup_settings_section(content_frame)
        
        # Controles de grabación
        self.setup_recording_controls(content_frame)
        
        # Área de transcripción
        self.setup_transcription_section(content_frame)
        
        # Área de logs (inicialmente oculta)
        self.setup_logs_section(content_frame)
        
    def setup_settings_section(self, parent):
        """Configurar sección de configuraciones"""
        settings_frame = ctk.CTkFrame(parent, corner_radius=10)
        settings_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        settings_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Título de configuraciones
        settings_title = ctk.CTkLabel(
            settings_frame,
            text="Configuración",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        settings_title.grid(row=0, column=0, columnspan=3, pady=(15, 10), sticky="w", padx=20)
        
        # Hotkey
        hotkey_label = ctk.CTkLabel(
            settings_frame,
            text="Tecla de acceso rápido:",
            font=ctk.CTkFont(size=12)
        )
        hotkey_label.grid(row=1, column=0, pady=5, sticky="w", padx=20)
        
        self.hotkey_value = ctk.CTkLabel(
            settings_frame,
            text="F12",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("blue", "lightblue")
        )
        self.hotkey_value.grid(row=2, column=0, pady=(0, 15), sticky="w", padx=20)
        
        # Modelo
        model_label = ctk.CTkLabel(
            settings_frame,
            text="Modelo de transcripción:",
            font=ctk.CTkFont(size=12)
        )
        model_label.grid(row=1, column=1, pady=5, sticky="w", padx=20)
        
        self.model_value = ctk.CTkLabel(
            settings_frame,
            text="Whisper Turbo",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("blue", "lightblue")
        )
        self.model_value.grid(row=2, column=1, pady=(0, 15), sticky="w", padx=20)
        
        # Idioma
        language_label = ctk.CTkLabel(
            settings_frame,
            text="Idioma:",
            font=ctk.CTkFont(size=12)
        )
        language_label.grid(row=1, column=2, pady=5, sticky="w", padx=20)
        
        # Dropdown de idiomas
        self.language_options = {
            "🌐 Auto-detectar": None,
            "🇪🇸 Español": "es",
            "🇺🇸 Inglés": "en",
            "🇫🇷 Francés": "fr",
            "🇩🇪 Alemán": "de",
            "🇮🇹 Italiano": "it",
            "🇵🇹 Portugués": "pt",
            "🇯🇵 Japonés": "ja",
            "🇰🇷 Coreano": "ko",
            "🇨🇳 Chino": "zh",
            "🇷🇺 Ruso": "ru",
            "🇳🇱 Holandés": "nl",
            "🇸🇪 Sueco": "sv",
            "🇳🇴 Noruego": "no",
            "🇩🇰 Danés": "da"
        }
        
        self.language_dropdown = ctk.CTkComboBox(
            settings_frame,
            values=list(self.language_options.keys()),
            font=ctk.CTkFont(size=12),
            width=160,
            height=28,
            command=self.on_language_change
        )
        self.language_dropdown.set("🌐 Auto-detectar")  # Valor por defecto
        self.language_dropdown.grid(row=2, column=2, pady=(0, 15), sticky="w", padx=20)
        
    def on_language_change(self, selection):
        """Callback cuando cambia el idioma seleccionado"""
        language_code = self.language_options[selection]
        self.add_log(f"🌍 Idioma cambiado a: {selection}")
        
        # Actualizar el recorder con el nuevo idioma
        if self.recorder:
            self.recorder.set_language(language_code)
            
    def get_selected_language(self):
        """Obtener el código del idioma seleccionado"""
        current_selection = self.language_dropdown.get()
        return self.language_options.get(current_selection, None)
        
    def setup_recording_controls(self, parent):
        """Configurar controles de grabación"""
        controls_frame = ctk.CTkFrame(parent, corner_radius=10)
        controls_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        controls_frame.grid_columnconfigure(0, weight=1)
        
        # Botón principal de grabación
        self.record_button = ctk.CTkButton(
            controls_frame,
            text="🎙️ Iniciar Grabación",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=60,
            command=self.toggle_recording
        )
        self.record_button.grid(row=0, column=0, pady=20, padx=20, sticky="ew")
        
        # Instrucción
        instruction_label = ctk.CTkLabel(
            controls_frame,
            text="Presiona F12 o el botón para grabar. Habla claramente y presiona nuevamente para transcribir.",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray50"),
            wraplength=600
        )
        instruction_label.grid(row=1, column=0, pady=(0, 20), padx=20)
        
    def setup_transcription_section(self, parent):
        """Configurar sección de transcripción"""
        trans_frame = ctk.CTkFrame(parent, corner_radius=10)
        trans_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        trans_frame.grid_columnconfigure(0, weight=1)
        trans_frame.grid_rowconfigure(1, weight=1)
        
        # Header de transcripción
        trans_header = ctk.CTkFrame(trans_frame, corner_radius=0, fg_color="transparent")
        trans_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        trans_header.grid_columnconfigure(0, weight=1)
        
        trans_title = ctk.CTkLabel(
            trans_header,
            text="Transcripción",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        trans_title.grid(row=0, column=0, sticky="w")
        
        # Botón copiar
        self.copy_button = ctk.CTkButton(
            trans_header,
            text="📋 Copiar",
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
        self.transcription_text.insert("1.0", "Las transcripciones aparecerán aquí...")
        
    def setup_logs_section(self, parent):
        """Configurar sección de logs"""
        logs_frame = ctk.CTkFrame(parent, corner_radius=10)
        logs_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        logs_frame.grid_columnconfigure(0, weight=1)
        
        # Header de logs
        logs_header = ctk.CTkFrame(logs_frame, corner_radius=0, fg_color="transparent")
        logs_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        logs_header.grid_columnconfigure(0, weight=1)
        
        logs_title = ctk.CTkLabel(
            logs_header,
            text="Logs del Sistema",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        logs_title.grid(row=0, column=0, sticky="w")
        
        # Botones de logs
        logs_buttons = ctk.CTkFrame(logs_header, corner_radius=0, fg_color="transparent")
        logs_buttons.grid(row=0, column=1, sticky="e")
        
        self.logs_toggle = ctk.CTkButton(
            logs_buttons,
            text="👁️ Mostrar",
            width=80,
            height=28,
            command=self.toggle_logs
        )
        self.logs_toggle.grid(row=0, column=0, padx=(0, 5))
        
        self.view_logs_button = ctk.CTkButton(
            logs_buttons,
            text="📄 Archivo",
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
            def create_tray_icon_static(is_recording=False):
                size = 64
                image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                draw = ImageDraw.Draw(image)
                
                if is_recording:
                    color = (220, 50, 50, 255)
                else:
                    color = (50, 150, 220, 255)
                    
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
            is_recording = False
            icon = None
            
            def on_record_click(icon_obj, item):
                event_queue.put(('toggle_recording',))
                
            def on_options_click(icon_obj, item):
                event_queue.put(('show_window',))
                
            def on_quit_click(icon_obj, item):
                event_queue.put(('quit',))
                icon_obj.stop()
            
            def create_menu():
                record_text = "⏹️ Detener Grabación" if is_recording else "🎙️ Iniciar Grabación"
                return pystray.Menu(
                    pystray.MenuItem(record_text, on_record_click),
                    pystray.MenuItem("⚙️ Opciones", on_options_click),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem("❌ Salir", on_quit_click)
                )
            
            def update_tray_state():
                """Actualizar estado del tray basado en mensajes del proceso principal"""
                nonlocal is_recording, icon
                try:
                    while not status_queue.empty():
                        status_update = status_queue.get_nowait()
                        if status_update[0] == 'recording_state':
                            new_recording_state = status_update[1]
                            if new_recording_state != is_recording:
                                is_recording = new_recording_state
                                # Actualizar icono
                                icon.icon = create_tray_icon_static(is_recording)
                                # Actualizar menú
                                icon.menu = create_menu()
                except:
                    pass
            
            # Crear y ejecutar icono
            icon_image = create_tray_icon_static(False)
            icon = pystray.Icon(
                "SimpleVoice",
                icon_image,
                "SimpleVoice - Transcriptor de Voz",
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
                # Obtener idioma seleccionado
                selected_language = self.get_selected_language()
                self.recorder = VoiceRecorder(log_callback=self.add_log, language=selected_language)
                self.root.after(0, lambda: self.update_status("🟢 Listo"))
            except Exception as e:
                self.root.after(0, lambda: self.add_log(f"❌ Error inicializando: {e}"))
                self.root.after(0, lambda: self.update_status("❌ Error"))
        
        threading.Thread(target=init_thread, daemon=True).start()
        
    def toggle_recording(self):
        """Alternar grabación"""
        if not self.recorder:
            self.add_log("❌ Grabador no inicializado")
            return
            
        if self.recorder.is_recording:
            # Parar grabación
            self.is_recording = False
            self.record_button.configure(text="⏳ Procesando...", state="disabled")
            self.update_status("⏳ Procesando...")
            self.update_tray_state()
            
            def stop_thread():
                transcript = self.recorder.stop_recording()
                if transcript:
                    self.root.after(0, lambda: self.show_transcription(transcript))
                self.root.after(0, lambda: self.record_button.configure(text="🎙️ Iniciar Grabación", state="normal"))
                self.root.after(0, lambda: self.update_status("🟢 Listo"))
                
            threading.Thread(target=stop_thread, daemon=True).start()
        else:
            # Iniciar grabación
            if self.recorder.start_recording():
                self.is_recording = True
                self.record_button.configure(text="⏹️ Detener Grabación")
                self.update_status("🔴 Grabando...")
                self.update_tray_state()
                
    def update_tray_state(self):
        """Enviar actualización de estado al process del tray"""
        try:
            if self.tray_process and self.tray_process.is_alive():
                self.tray_status_queue.put(('recording_state', self.is_recording))
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
                self.add_log("📋 Texto copiado al portapapeles")
            except:
                self.add_log("❌ Error copiando al portapapeles")
        else:
            self.add_log("⚠️ No hay texto para copiar")
            
    def toggle_logs(self):
        """Mostrar/ocultar logs"""
        if self.logs_visible:
            self.logs_container.grid_remove()
            self.logs_toggle.configure(text="👁️ Mostrar")
            self.logs_visible = False
        else:
            self.logs_container.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
            self.logs_toggle.configure(text="👁️ Ocultar")
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
        self.status_label.configure(text=f"Estado: {status}")
        
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
                    messagebox.showinfo("Archivo de Logs", f"Archivo: {log_file}")
            else:
                messagebox.showwarning("Logs", "No se encontró el archivo de logs")
                
    def show_settings(self):
        """Mostrar configuraciones avanzadas"""
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("Configuraciones Avanzadas")
        settings_window.geometry("500x400")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Título
        title = ctk.CTkLabel(
            settings_window,
            text="Configuraciones Avanzadas",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=20)
        
        # Frame principal
        content_frame = ctk.CTkFrame(settings_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Información de archivos
        files_label = ctk.CTkLabel(
            content_frame,
            text="📁 Ubicaciones de Archivos",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        files_label.pack(pady=(20, 10), anchor="w", padx=20)
        
        # Logs
        logs_info = ctk.CTkLabel(
            content_frame,
            text=f"Logs: ~/SimpleVoice/logs/",
            font=ctk.CTkFont(size=12)
        )
        logs_info.pack(anchor="w", padx=20)
        
        # Información técnica
        tech_label = ctk.CTkLabel(
            content_frame,
            text="🔧 Información Técnica",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        tech_label.pack(pady=(20, 10), anchor="w", padx=20)
        
        tech_info = ctk.CTkLabel(
            content_frame,
            text="""• Motor: OpenAI Whisper
• Versión del modelo: Turbo (1.6GB)
• Formato de audio: WAV 16kHz mono
• Hotkeys: Globales (funcionan desde cualquier app)
• Logs automáticos: Activados""",
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        tech_info.pack(anchor="w", padx=20, pady=(0, 20))
        
        # Botón cerrar
        close_button = ctk.CTkButton(
            content_frame,
            text="Cerrar",
            command=settings_window.destroy
        )
        close_button.pack(pady=20)
        
    def show_help(self):
        """Mostrar ayuda"""
        help_text = """
        🎙️ SimpleVoice - Transcriptor de Voz
        
        📖 Cómo usar:
        1. Presiona F12 o el botón "GRABAR" para iniciar
        2. Habla claramente al micrófono
        3. Presiona F12 nuevamente o "PARAR" para terminar
        4. El texto se transcribe automáticamente
        5. Se copia al portapapeles automáticamente
        
        🔧 Características:
        • Hotkey global F12
        • Transcripción con IA (Whisper)
        • Copia automática al portapapeles
        • Logs detallados del sistema
        • Interfaz moderna y amigable
        
        📝 Notas:
        • Requiere micrófono funcional
        • Optimizado para español
        • Los logs se guardan en ~/SimpleVoice/logs/
        """
        
        messagebox.showinfo("❓ Ayuda", help_text)
        

        
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
        print(f"❌ Error ejecutando GUI: {e}")
        messagebox.showerror("Error", f"Error ejecutando SimpleVoice:\n{e}")

if __name__ == "__main__":
    # Protección necesaria para multiprocessing en macOS
    multiprocessing.set_start_method('spawn', force=True)
    main() 