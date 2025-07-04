#!/usr/bin/env python3
"""
SimpleVoice - Terminal Voice Transcription Tool
Presiona F12 para iniciar/parar grabación, transcribe con Whisper y copia al portapapeles
"""

import os
import sys
import time
import threading
import logging
import tempfile
import warnings
from pathlib import Path

# Silenciar warnings de Whisper para mejor UX
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
warnings.filterwarnings("ignore", category=UserWarning)

# Configurar logging con muchos detalles
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

try:
    import pyaudio
    import wave
    import whisper
    import pyperclip
    from pynput import keyboard
    import subprocess
    logger.info("✅ Todas las dependencias importadas correctamente")
except ImportError as e:
    logger.error(f"❌ Error importando dependencias: {e}")
    logger.error("Instala las dependencias con: pip install -r requirements.txt")
    sys.exit(1)

class SimpleVoiceRecorder:
    def __init__(self):
        self.is_recording = False
        self.sample_rate = 16000  # Whisper prefiere 16kHz
        self.chunk_size = 1024
        self.channels = 1
        self.temp_dir = tempfile.mkdtemp()
        self.whisper_model = None
        self.recording_thread = None
        self.audio_data = []
        self.start_time = None
        
        logger.info("🎙️  Inicializando SimpleVoice...")
        logger.info(f"📁 Directorio temporal: {self.temp_dir}")
        
        # Inicializar PyAudio
        self.audio = pyaudio.PyAudio()
        logger.info("🎤 PyAudio inicializado")
        
        # Cargar modelo Whisper
        self.load_whisper_model()
        
        logger.info("🚀 SimpleVoice listo para usar!")
        logger.info("🔥 Presiona F12 para iniciar/parar grabación")
        logger.info("📋 La transcripción se copiará automáticamente al portapapeles")
        
    def load_whisper_model(self):
        """Cargar modelo Whisper"""
        try:
            logger.info("🤖 Cargando modelo Whisper 'turbo'...")
            # Cargar modelo con configuración optimizada
            self.whisper_model = whisper.load_model("turbo", device="cpu")
            logger.info("✅ Modelo Whisper cargado exitosamente")
        except Exception as e:
            logger.error(f"❌ Error cargando modelo Whisper: {e}")
            sys.exit(1)
    
    def start_recording(self):
        """Iniciar grabación de audio"""
        if self.is_recording:
            logger.warning("⚠️  Ya se está grabando")
            return
            
        logger.info("🎵 INICIANDO GRABACIÓN...")
        print("🎤 Grabando... (presiona F12 para parar)")
        
        # Notificación para empezar a hablar
        self.send_notification("🎤 Grabando", "¡Habla ahora! Presiona F12 para parar", 2)
        
        self.is_recording = True
        self.audio_data = []
        self.start_time = time.time()
        
        # Iniciar grabación en hilo separado
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.start()
        
    def stop_recording(self):
        """Parar grabación y procesar audio"""
        if not self.is_recording:
            logger.warning("⚠️  No se está grabando")
            return
            
        logger.info("🛑 PARANDO GRABACIÓN...")
        self.is_recording = False
        
        # Calcular tiempo de grabación
        if self.start_time:
            duration = time.time() - self.start_time
            print(f"⏹️  Grabación terminada ({duration:.1f}s)")
        
        # Notificación de procesamiento
        self.send_notification("🤖 Procesando", "Transcribiendo audio...", 3)
        
        # Esperar a que termine el hilo de grabación
        if self.recording_thread:
            self.recording_thread.join()
            
        # Procesar audio grabado
        if len(self.audio_data) > 0:
            self._process_audio()
        else:
            logger.warning("⚠️  No hay audio para procesar")
    
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
                    logger.warning(f"⚠️  Error leyendo audio: {e}")
                    break
            
            # Cerrar stream
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            logger.error(f"❌ Error durante grabación: {e}")
            self.is_recording = False
    
    def _process_audio(self):
        """Procesar audio grabado con Whisper"""
        try:
            if not self.audio_data:
                logger.warning("⚠️  No hay datos de audio para procesar")
                return
            
            # Combinar todos los chunks de audio
            audio_bytes = b''.join(self.audio_data)
            duration = len(audio_bytes) / (self.sample_rate * self.channels * 2)  # 2 bytes per sample (paInt16)
            
            # Guardar audio temporal como WAV
            temp_file = os.path.join(self.temp_dir, "temp_audio.wav")
            
            with wave.open(temp_file, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_bytes)
            
            # Transcribir con Whisper
            logger.info("🤖 Transcribiendo con Whisper...")
            print("⏳ Procesando audio...", end="", flush=True)
            
            # Configuración optimizada para mejor rendimiento
            result = self.whisper_model.transcribe(
                temp_file,
                language="es",
                fp16=False,  # Forzar FP32 para evitar warnings
                verbose=False,  # Reducir output verboso
                temperature=0.0,  # Más determinístico
                best_of=1,  # Reducir complejidad
                beam_size=1,  # Más rápido
                patience=1.0,
                length_penalty=1.0,
                suppress_tokens="",
                initial_prompt=None,
                condition_on_previous_text=False,
                compression_ratio_threshold=2.4,
                logprob_threshold=-1.0,
                no_speech_threshold=0.6
            )
            
            print("\r✅ Transcripción completada!    ")
            transcription = result["text"].strip()
            logger.info(f"📝 Transcripción: '{transcription}'")
            
            if transcription:
                # Copiar al portapapeles
                pyperclip.copy(transcription)
                logger.info("📋 ✅ Transcripción copiada al portapapeles")
                
                # Notificación de copiado
                self.send_notification("📋 ¡Listo!", f"Transcripción copiada: {transcription[:50]}{'...' if len(transcription) > 50 else ''}", 4)
                
                # Mostrar resultado
                print("\n" + "="*50)
                print("🎯 TRANSCRIPCIÓN COMPLETA:")
                print(f"📝 {transcription}")
                print("📋 Copiado al portapapeles")
                print("="*50 + "\n")
            else:
                logger.warning("⚠️  No se detectó texto en el audio")
            
            # Limpiar archivo temporal
            os.remove(temp_file)
            logger.info("🧹 Archivo temporal eliminado")
            
        except Exception as e:
            logger.error(f"❌ Error procesando audio: {e}")
    
    def toggle_recording(self):
        """Alternar entre iniciar y parar grabación"""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def send_notification(self, title, message, timeout=3):
        """Enviar notificación del sistema usando osascript nativo de macOS"""
        try:
            # Usar osascript para notificaciones nativas de macOS
            script = f'''
            display notification "{message}" with title "SimpleVoice" subtitle "{title}"
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        except Exception as e:
            logger.warning(f"⚠️ Error enviando notificación: {e}")
    
    def cleanup(self):
        """Limpiar recursos"""
        try:
            if self.audio:
                self.audio.terminate()
                logger.info("🧹 PyAudio terminado")
        except Exception as e:
            logger.error(f"❌ Error limpiando recursos: {e}")

def main():
    """Función principal"""
    logger.info("🎬 Iniciando SimpleVoice...")
    
    # Verificar que ffmpeg esté instalado
    if os.system("ffmpeg -version > /dev/null 2>&1") != 0:
        logger.error("❌ ffmpeg no está instalado")
        logger.error("Instala ffmpeg: brew install ffmpeg (macOS)")
        sys.exit(1)
    
    # Crear recorder
    recorder = SimpleVoiceRecorder()
    
    # Configurar captura de teclas
    def on_key_press(key):
        try:
            if key == keyboard.Key.f12:
                logger.info("🔥 F12 presionado!")
                recorder.toggle_recording()
        except AttributeError:
            # Ignorar teclas especiales que no podemos procesar
            pass
        except Exception as e:
            logger.error(f"❌ Error en captura de tecla: {e}")
    
    def on_key_release(key):
        # Manejar liberación de teclas para evitar escape sequences
        pass
    
    # Iniciar listener de teclas
    logger.info("⌨️  Iniciando captura de teclas...")
    with keyboard.Listener(on_press=on_key_press, on_release=on_key_release, suppress=False) as listener:
        try:
            print("\n" + "="*60)
            print("🎙️  SIMPLE VOICE - TRANSCRIPCIÓN DE VOZ")
            print("="*60)
            print("🔥 Presiona F12 para INICIAR/PARAR grabación")
            print("📋 La transcripción se copiará automáticamente al portapapeles")
            print("❌ Presiona Ctrl+C para salir")
            print("="*60 + "\n")
            
            listener.join()
            
        except KeyboardInterrupt:
            logger.info("👋 Cerrando SimpleVoice...")
            recorder.cleanup()
            print("\n¡Hasta la vista! 👋")
            sys.exit(0)

if __name__ == "__main__":
    main() 