#!/usr/bin/env python3
"""
SimpleVoice - Módulo de Grabación y Transcripción
Lógica separada para facilitar integración con GUI
"""

import os
import sys
import time
import threading
import logging
import tempfile
import warnings
from pathlib import Path
from typing import Callable, Optional
from datetime import datetime

# Silenciar warnings de Whisper
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
warnings.filterwarnings("ignore", category=UserWarning)

try:
    import pyaudio
    import wave
    import whisper
    import pyperclip
    import subprocess
except ImportError as e:
    logging.error(f"❌ Error importando dependencias: {e}")
    raise

class VoiceRecorder:
    def __init__(self, log_callback: Optional[Callable] = None, language: str = "es"):
        """
        Inicializar el grabador de voz
        
        Args:
            log_callback: Función para enviar logs a la GUI
            language: Código de idioma para transcripción (ej: "es", "en", None para auto-detectar)
        """
        self.is_recording = False
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.channels = 1
        self.temp_dir = tempfile.mkdtemp()
        self.whisper_model = None
        self.recording_thread = None
        self.audio_data = []
        self.start_time = None
        self.log_callback = log_callback
        self.language = language  # Idioma para transcripción
        
        # Configurar logging
        self.setup_logging()
        
        self.log("🎙️  Inicializando SimpleVoice...")
        self.log(f"📁 Directorio temporal: {self.temp_dir}")
        
        # Inicializar PyAudio
        self.audio = pyaudio.PyAudio()
        self.log("🎤 PyAudio inicializado")
        
        # Cargar modelo Whisper
        self.load_whisper_model()
        
        # Registrar idioma configurado
        lang_text = "🌐 Auto-detectar" if language is None else f"🌍 {language.upper()}"
        self.log(f"🗣️  Idioma configurado: {lang_text}")
        
        self.log("🚀 SimpleVoice listo para usar!")
        
    def setup_logging(self):
        """Configurar logging a archivo y callback"""
        logs_dir = Path.home() / "SimpleVoice" / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = logs_dir / f"simplevoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Configurar logging a archivo
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.log_file_path = log_file
        
    def log(self, message: str, level: str = "INFO"):
        """Enviar log tanto a archivo como a callback GUI"""
        # Log a archivo
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
        
        # Enviar a GUI si hay callback
        if self.log_callback:
            self.log_callback(message)
            
    def load_whisper_model(self):
        """Cargar modelo Whisper"""
        try:
            self.log("🤖 Cargando modelo Whisper 'turbo'...")
            self.whisper_model = whisper.load_model("turbo", device="cpu")
            self.log("✅ Modelo Whisper cargado exitosamente")
        except Exception as e:
            self.log(f"❌ Error cargando modelo Whisper: {e}", "ERROR")
            raise
    
    def set_language(self, language_code: Optional[str]):
        """
        Cambiar el idioma de transcripción
        
        Args:
            language_code: Código de idioma ("es", "en", etc.) o None para auto-detectar
        """
        self.language = language_code
        lang_text = "🌐 Auto-detectar" if language_code is None else f"🌍 {language_code.upper()}"
        self.log(f"🗣️  Idioma actualizado: {lang_text}")
    
    def start_recording(self):
        """Iniciar grabación de audio"""
        if self.is_recording:
            self.log("⚠️  Ya se está grabando", "WARNING")
            return False
            
        self.log("🎵 INICIANDO GRABACIÓN...")
        
        # Notificación de inicio
        self.send_notification("🎤 Grabando", "¡Habla ahora! Presiona F12 para parar", 2)
        
        self.is_recording = True
        self.audio_data = []
        self.start_time = time.time()
        
        # Iniciar grabación en hilo separado
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.start()
        
        return True
        
    def stop_recording(self):
        """Parar grabación y procesar audio"""
        if not self.is_recording:
            self.log("⚠️  No se está grabando", "WARNING")
            return None
            
        self.log("🛑 PARANDO GRABACIÓN...")
        self.is_recording = False
        
        # Calcular tiempo de grabación
        if self.start_time:
            duration = time.time() - self.start_time
            self.log(f"⏹️  Grabación terminada ({duration:.1f}s)")
        
        # Notificación de procesamiento
        self.send_notification("🤖 Procesando", "Transcribiendo audio...", 3)
        
        # Esperar a que termine el hilo de grabación
        if self.recording_thread:
            self.recording_thread.join()
            
        # Procesar audio grabado
        if len(self.audio_data) > 0:
            return self._process_audio()
        else:
            self.log("⚠️  No hay audio para procesar", "WARNING")
            return None
    
    def _record_audio(self):
        """Grabar audio continuamente"""
        try:
            # Configurar stream de audio
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            while self.is_recording:
                try:
                    # Leer chunk de audio
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    self.audio_data.append(data)
                except Exception as e:
                    self.log(f"⚠️  Error leyendo audio: {e}", "WARNING")
                    break
            
            # Cerrar stream
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            self.log(f"❌ Error durante grabación: {e}", "ERROR")
            self.is_recording = False
    
    def _process_audio(self):
        """Procesar audio grabado con Whisper"""
        try:
            if not self.audio_data:
                self.log("⚠️  No hay datos de audio para procesar", "WARNING")
                return None
            
            # Combinar todos los chunks de audio
            audio_bytes = b''.join(self.audio_data)
            
            # Guardar audio temporal como WAV
            temp_file = os.path.join(self.temp_dir, "temp_audio.wav")
            
            with wave.open(temp_file, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_bytes)
            
            # Transcribir con Whisper
            self.log("🤖 Transcribiendo con Whisper...")
            
            result = self.whisper_model.transcribe(
                temp_file,
                language=self.language,
                fp16=False,
                verbose=False,
                temperature=0.0,
                best_of=1,
                beam_size=1,
                patience=1.0,
                length_penalty=1.0,
                suppress_tokens="",
                initial_prompt=None,
                condition_on_previous_text=False,
                compression_ratio_threshold=2.4,
                logprob_threshold=-1.0,
                no_speech_threshold=0.6
            )
            
            transcript = result["text"].strip()
            
            if transcript:
                self.log(f"📝 Transcripción: {transcript}")
                
                # Copiar al portapapeles
                pyperclip.copy(transcript)
                self.log("📋 Texto copiado al portapapeles")
                
                # Notificación de éxito
                preview = transcript[:50] + ('...' if len(transcript) > 50 else '')
                self.send_notification("📋 ¡Listo!", f"Transcripción copiada: {preview}", 4)
                
                # Limpiar archivo temporal
                try:
                    os.remove(temp_file)
                except:
                    pass
                
                return transcript
            else:
                self.log("⚠️  No se detectó habla en el audio", "WARNING")
                return None
            
        except Exception as e:
            self.log(f"❌ Error procesando audio: {e}", "ERROR")
            return None
    
    def send_notification(self, title, message, timeout=3):
        """Enviar notificación del sistema usando osascript nativo de macOS"""
        try:
            # Usar osascript para notificaciones nativas de macOS
            script = f'''
            display notification "{message}" with title "SimpleVoice" subtitle "{title}"
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            self.log(f"📱 Notificación: {title} - {message}")
        except Exception as e:
            self.log(f"⚠️ Error enviando notificación: {e}", "WARNING")
    
    def cleanup(self):
        """Limpiar recursos"""
        try:
            if self.audio:
                self.audio.terminate()
            
            # Limpiar directorio temporal
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                
            self.log("🧹 Recursos limpiados")
        except Exception as e:
            self.log(f"❌ Error limpiando recursos: {e}", "ERROR")
    
    def get_log_file_path(self):
        """Obtener ruta del archivo de logs"""
        return self.log_file_path 