"""
SimpleVoice - Transcriptor de Voz
Paquete para aplicación de escritorio
"""

__version__ = "1.0.0"
__author__ = "SimpleVoice Team"
__description__ = "Transcriptor de voz con IA usando Whisper"

from .recorder import VoiceRecorder
from .gui import SimpleVoiceGUI

__all__ = ['VoiceRecorder', 'SimpleVoiceGUI'] 