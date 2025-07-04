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
   
   **Nota**:  En macOS, si tienes problemas con pyaudio, puedes instalarlo con:
   ```bash
   brew install portaudio 
   pip install pyaudio
   ```
   
   **Notificaciones**: Las notificaciones usan `osascript` nativo de macOS, sin dependencias adicionales.

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
   2. Aparece notificación: "🎤 Grabando - ¡Habla ahora!"
   3. Habla lo que quieras transcribir
   4. Presiona F12 de nuevo para parar
   5. Aparece notificación: "🤖 Procesando - Transcribiendo audio..."
   6. El texto se transcribe automáticamente
   7. Aparece notificación: "📋 ¡Listo! - Transcripción copiada"
   8. Se muestra en la terminal

## Características

- ✅ Grabación con tecla F12
- ✅ Transcripción con Whisper (modelo turbo)
- ✅ Copia automática al portapapeles
- ✅ Soporte para español
- ✅ Logs detallados con emojis
- ✅ Interfaz simple de terminal
- ✅ Compatible con macOS (PyAudio en lugar de SoundDevice)
- ✅ Notificaciones nativas de macOS para estados de grabación

## Requisitos

- Python 3.8+
- ffmpeg
- Micrófono funcionando
- macOS (para teclas globales)

¡Listo para transcribir! 🚀 