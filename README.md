# SimpleVoice 🎙️

Herramienta simple de transcripción de voz en la terminal usando OpenAI Whisper.

## Instalación

1. **Instalar ffmpeg** (requerido por Whisper):
   ```bash
   brew install ffmpeg
   ```

2. **Instalar dependencias de Python**:
   ```bash
   pip install -r requirements.txt
   ```
   
   **Nota**: En macOS, si tienes problemas con pyaudio, puedes instalarlo con:
   ```bash
   brew install portaudio
   pip install pyaudio
   ```

## Uso

1. **Ejecutar el programa**:
   ```bash
   python main.py
   ```

2. **Controles**:
   - 🔥 **F12**: Iniciar/parar grabación
   - **Ctrl+C**: Salir del programa

3. **Flujo de trabajo**:
   1. Presiona F12 para empezar a grabar
   2. Habla lo que quieras transcribir
   3. Presiona F12 de nuevo para parar
   4. El texto se transcribe automáticamente
   5. Se copia al portapapeles
   6. Se muestra en la terminal

## Características

- ✅ Grabación con tecla F12
- ✅ Transcripción con Whisper (modelo turbo)
- ✅ Copia automática al portapapeles
- ✅ Soporte para español
- ✅ Logs detallados con emojis
- ✅ Interfaz simple de terminal
- ✅ Compatible con macOS (PyAudio en lugar de SoundDevice)

## Requisitos

- Python 3.8+
- ffmpeg
- Micrófono funcionando
- macOS (para teclas globales)

¡Listo para transcribir! 🚀 