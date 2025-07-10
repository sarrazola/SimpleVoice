# 🎙️ SimpleVoice - Construcción de App de Escritorio

## 📋 Resumen del Proyecto

Tu aplicación SimpleVoice ha sido convertida en una app de escritorio moderna con:

- ✅ **Interfaz gráfica moderna** con CustomTkinter
- ✅ **Logs visibles** tanto en GUI como en archivos
- ✅ **Hotkeys globales** (F12 funciona desde cualquier app)
- ✅ **Ejecutable independiente** (usuario no necesita Python)
- ✅ **Logs automáticos** guardados en ~/SimpleVoice/logs/
- ✅ **Empaquetado automatizado** con PyInstaller

## 🗂️ Estructura de Archivos Creada

```
SimpleVoice/
├── src/
│   ├── __init__.py           # Paquete Python
│   ├── recorder.py           # Lógica de grabación (refactorizada)
│   ├── gui.py               # Interfaz gráfica moderna
│   └── main_gui.py          # Punto de entrada principal
├── requirements-gui.txt      # Dependencias para GUI
├── SimpleVoice.spec         # Configuración PyInstaller
├── build.py                 # Script de construcción automatizado
└── INSTRUCCIONES.md         # Este archivo
```

## 🚀 Pasos para Construir la App

### 1. Instalar Dependencias
```bash
pip install -r requirements-gui.txt
```

### 2. Construir Aplicación (Automático)
```bash
python build.py
```

### 3. Construir Aplicación (Manual)
```bash
pyinstaller SimpleVoice.spec --noconfirm
```

## 📁 Archivos Generados

Después de la construcción encontrarás:

- `dist/SimpleVoice.app` (macOS) o `dist/SimpleVoice` (Linux/Windows)
- `SimpleVoice-[platform].zip` - Paquete de distribución
- `README-Distribution.md` - Instrucciones para usuarios finales

## 🎯 Cómo Usar la Aplicación

### Para Desarrolladores (Modo Desarrollo)
```bash
cd src
python main_gui.py
```

### Para Usuarios Finales
1. Descomprimir el archivo ZIP
2. Abrir SimpleVoice.app (macOS) o SimpleVoice.exe (Windows)
3. **Usar desde la barra de menú** (recomendado):
   - Buscar el icono azul circular en la barra de menú superior
   - Clic derecho → "🎙️ Iniciar Grabación"
   - Hablar claramente
   - Clic derecho → "⏹️ Detener Grabación"
   - El texto se copia automáticamente al portapapeles
4. **Usar desde la interfaz gráfica**:
   - Presionar F12 para grabar
   - Hablar claramente
   - Presionar F12 para parar y transcribir
5. **Cerrar la ventana** no cierra la app (queda en system tray)
6. Para **salir completamente**: System Tray → "❌ Salir"

## 📊 Sistema de Logs

### Logs Visibles en GUI
- Área de logs desplegable en la interfaz
- Botón "Ver Logs" para abrir archivo completo
- Logs en tiempo real durante grabación

### Logs en Archivos
- Ubicación: `~/SimpleVoice/logs/`
- Formato: `simplevoice_YYYYMMDD_HHMMSS.log`
- Logs detallados para depuración

## 🔧 Características Avanzadas

### Interfaz Gráfica
- **Tema oscuro** por defecto
- **Botones grandes** y fáciles de usar
- **Estados visuales** (grabando, procesando, listo)
- **Área de transcripción** editable
- **Logs desplegables** para monitoreo

### Funcionalidades
- **Hotkey global F12** (funciona desde cualquier app)
- **Copia automática** al portapapeles
- **Transcripción en español** con Whisper Turbo
- **Gestión de recursos** automática
- **Notificaciones visuales** de estado
- **🆕 System Tray**: Icono permanente en la barra de menú de macOS
  - **🎙️ Grabar**: Iniciar/detener grabación desde el menú
  - **⚙️ Opciones**: Mostrar/ocultar la ventana principal
  - **❌ Salir**: Cerrar completamente la aplicación

## 🛠️ Personalización

### Cambiar Idioma
En `src/recorder.py`, línea ~190:
```python
result = self.whisper_model.transcribe(
    temp_file,
    language="es",  # Cambiar a "en" para inglés
    ...
)
```

### Cambiar Hotkey
En `src/gui.py`, línea ~220:
```python
if key == keyboard.Key.f12:  # Cambiar por otra tecla
```

### Cambiar Tema
En `src/gui.py`, línea ~19:
```python
ctk.set_appearance_mode("dark")  # "light" o "system"
```

## 📦 Distribución

### Crear Paquete de Distribución
```bash
python build.py
```

### Compartir con Usuarios
1. Enviar archivo `SimpleVoice-[platform].zip`
2. Incluir `README-Distribution.md`
3. Mencionar que necesitan permisos de micrófono

## 🔧 Solución de Problemas

### Error: "No se encontró CustomTkinter"
```bash
pip install customtkinter
```

### Error: "No se encontró PyAudio"
```bash
# macOS
brew install portaudio
pip install pyaudio

# Linux
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### Error: "No se encontró Whisper"
```bash
pip install openai-whisper
```

### Logs para Depuración
- Revisa `~/SimpleVoice/logs/` para errores detallados
- Ejecuta en modo desarrollo: `cd src && python main_gui.py`

## 📈 Próximos Pasos Sugeridos

1. **Probar** la aplicación en modo desarrollo
2. **Construir** el ejecutable
3. **Probar** el ejecutable en sistema limpio
4. **Distribuir** el archivo ZIP
5. **Recopilar feedback** de usuarios

## 💡 Notas Importantes

- Los logs se guardan automáticamente para feedback
- La aplicación necesita permisos de micrófono
- F12 es la tecla global (funciona desde cualquier app)
- La primera carga del modelo Whisper puede tomar tiempo
- En macOS, puede requerir permisos de seguridad

## 🎉 ¡Listo!

Tu aplicación SimpleVoice está lista para ser una app de escritorio profesional. El sistema de logs te permitirá recibir feedback detallado y mejorar la experiencia de usuario.

¿Necesitas alguna personalización adicional o tienes preguntas sobre el proceso? 