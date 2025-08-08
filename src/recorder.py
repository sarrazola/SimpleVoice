#!/usr/bin/env python3
"""
SimpleVoice - Recording and Transcription Module
Separate logic to facilitate GUI integration
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
import shutil

# Silenciar warnings de Whisper
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
warnings.filterwarnings("ignore", category=UserWarning)

try:
    import pyaudio
    import wave
    import whisper
    import pyperclip
    import subprocess
    import pyautogui
except ImportError as e:
    logging.error(f"❌ Error importing dependencies: {e}")
    raise

class VoiceRecorder:
    def __init__(self, log_callback: Optional[Callable] = None, language: Optional[str] = None, model: str = "turbo"):
        """
        Initialize the voice recorder
        
        Args:
            log_callback: Function to send logs to the GUI
            language: Language code for transcription (e.g., "es", "en") or None for auto-detect (default)
            model: Whisper model to use (tiny, base, small, medium, large, turbo)
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
        self.language = language  # Language for transcription
        self.model_name = model  # Whisper model
        
        # Obtener el logger ya configurado por la GUI
        self.logger = logging.getLogger(__name__)
        
        self.log("🎙️  Initializing SimpleVoice...")
        self.log(f"📁 Temporary directory: {self.temp_dir}")
        
        # Verificar ffmpeg (requerido por whisper para carga/decodificación)
        if shutil.which("ffmpeg") is None:
            error_msg = "FFmpeg is not installed or not found in PATH. Install with 'brew install ffmpeg' on macOS."
            self.log(f"❌ {error_msg}", "ERROR")
            raise RuntimeError(error_msg)

        # Inicializar PyAudio
        self.audio = pyaudio.PyAudio()
        self.log("🎤 PyAudio initialized")
        
        # Cargar modelo Whisper
        self.load_whisper_model()
        
        # Registrar configuración
        lang_text = "🌐 Auto-detect" if language is None else f"🌍 {language.upper()}"
        self.log(f"🗣️  Language configured: {lang_text}")
        self.log(f"🤖 Model configured: {model.upper()}")
        
        self.log("🚀 SimpleVoice ready to use!")
        
    def log(self, message: str, level: str = "INFO"):
        """Send log both to stdout and GUI callback"""
        # Log to stdout using the configured logger
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
        
        # Send to GUI if callback exists
        if self.log_callback:
            # We only send the message, as the GUI logger will handle formatting
            self.log_callback(message)
            
    def load_whisper_model(self):
        """Load Whisper model"""
        try:
            self.log(f"🤖 Loading Whisper model '{self.model_name}'...")
            self.send_notification("Initializing...", f"Initializing model, please wait a few seconds...")
            self.whisper_model = whisper.load_model(self.model_name, device="cpu")
            self.log(f"✅ Whisper model '{self.model_name}' loaded successfully")
            self.send_notification("Ready to Record", "SimpleVoice is now ready to use.")
        except Exception as e:
            self.log(f"❌ Error loading Whisper model '{self.model_name}': {e}", "ERROR")
            self.send_notification("Initialization Error", f"Could not load model: {e}")
            raise
    
    def set_language(self, language_code: Optional[str]):
        """
        Change the transcription language
        
        Args:
            language_code: Language code ("es", "en", etc.) or None for auto-detect
        """
        self.language = language_code
        lang_text = "🌐 Auto-detect" if language_code is None else f"🌍 {language_code.upper()}"
        self.log(f"🗣️  Language updated: {lang_text}")
        
    def set_model(self, model_name: str):
        """
        Change the Whisper model
        
        Args:
            model_name: Model name (tiny, base, small, medium, large, turbo)
        """
        self.model_name = model_name
        self.log(f"🤖 Model updated: {model_name.upper()}")
        # Note: The model is loaded externally from the GUI to show progress
    
    def start_recording(self, hotkey: str = "F12"):
        """Start audio recording"""
        if self.is_recording:
            self.log("⚠️  Already recording", "WARNING")
            return False
            
        self.log("🎵 STARTING RECORDING...")
        
        # Start notification
        self.send_notification("🎤 Recording", f"Speak now! Press {hotkey} to stop", 2)
        
        self.is_recording = True
        self.audio_data = []
        self.start_time = time.time()
        
        # Start recording in separate thread
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.start()
        
        return True
        
    def stop_recording(self):
        """Stop recording and process audio"""
        if not self.is_recording:
            self.log("⚠️  Not recording", "WARNING")
            return None
            
        self.log("🛑 STOPPING RECORDING...")
        self.is_recording = False
        
        # Calculate recording duration
        if self.start_time:
            duration = time.time() - self.start_time
            self.log(f"⏹️  Recording finished ({duration:.1f}s)")
        
        # Processing notification
        self.send_notification("🤖 Processing", "Transcribing audio...", 3)
        
        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join()
            
        # Process recorded audio
        if len(self.audio_data) > 0:
            return self._process_audio()
        else:
            self.log("⚠️  No audio to process", "WARNING")
            return None
    
    def _record_audio(self):
        """Record audio continuously"""
        try:
            # Configure audio stream
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            while self.is_recording:
                try:
                    # Read audio chunk
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    self.audio_data.append(data)
                except Exception as e:
                    self.log(f"⚠️  Error reading audio: {e}", "WARNING")
                    break
            
            # Close stream
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            self.log(f"❌ Error during recording: {e}", "ERROR")
            self.is_recording = False
    
    def _process_audio(self):
        """Process recorded audio with Whisper"""
        try:
            if not self.audio_data:
                self.log("⚠️  No audio data to process", "WARNING")
                return None
            
            # Combine all audio chunks
            audio_bytes = b''.join(self.audio_data)
            
            # Save temporary audio as WAV
            temp_file = os.path.join(self.temp_dir, "temp_audio.wav")
            
            with wave.open(temp_file, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_bytes)
            
            # Transcribe with Whisper
            self.log("🤖 Transcribing with Whisper...")
            
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
                suppress_tokens=-1,  # keep default suppression (e.g., [Music], [Laughter])
                initial_prompt=None,
                condition_on_previous_text=False,
                compression_ratio_threshold=2.4,
                logprob_threshold=-1.0,
                no_speech_threshold=0.7
            )
            
            transcript = result["text"].strip()
            
            self.log(f"📝 Transcription: {transcript}")
            
            # Copy to clipboard and auto-paste
            try:
                pyperclip.copy(transcript)
                self.log("📋 Text copied to clipboard")

                # Auto-paste from clipboard
                self._paste_from_clipboard()
                
            except Exception as e:
                self.log(f"❌ Error copying to clipboard or pasting: {e}", "ERROR")

            # Send notification
            self.send_notification("📋 Ready!", f"Transcription copied: {transcript[:50]}...")
            
            return transcript
        except Exception as e:
            self.log(f"❌ Error processing audio: {e}", "ERROR")
            return None

    def _paste_from_clipboard(self):
        """Simulate pasting from clipboard using pyautogui with a more robust method."""
        try:
            self.log("📋 Pasting text automatically...")
            
            # Allow a very short moment for the user to switch focus if needed
            time.sleep(0.2)

            os_platform = sys.platform
            self.log(f"💻 Detected OS: {os_platform}")

            if os_platform == "darwin":  # macOS
                self.log("macOS detected, using low-level key events for reliability.")
                pyautogui.keyDown('command')
                time.sleep(0.1)  # Ensure modifier key is registered
                pyautogui.press('v')
                pyautogui.keyUp('command')
            else:  # Windows or Linux
                self.log("Windows/Linux detected, using 'ctrl' + 'v'")
                pyautogui.hotkey('ctrl', 'v')
            
            self.log("✅ Paste command sent successfully.")

        except Exception as e:
            self.log(f"❌ Error during automatic paste: {e}", "ERROR")
            self.log("ℹ️  Please ensure accessibility permissions are granted for your terminal/IDE if on macOS.", "WARNING")

    def send_notification(self, title, message, timeout=3):
        """Send desktop notification (macOS only)"""
        if sys.platform == "darwin":
            try:
                # Use osascript for native macOS notifications
                script = f'''
                display notification "{message}" with title "SimpleVoice" subtitle "{title}"
                '''
                subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
                self.log(f"📱 Notification: {title} - {message}")
            except Exception as e:
                self.log(f"⚠️ Error sending notification: {e}", "WARNING")

    def cleanup(self):
        """Clean up resources"""
        try:
            if self.audio:
                self.audio.terminate()
            
            # Clean temporary directory
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                
            self.log("🧹 Resources cleaned")
        except Exception as e:
            self.log(f"❌ Error cleaning resources: {e}", "ERROR") 