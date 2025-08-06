# SimpleVoice.app - Guía de Usuario

## 🚀 Instalación Rápida

### Opción 1: Instalación Automática (Recomendada)
```bash
./install.sh
```

Este script configura todo automáticamente:
- ✅ Verifica dependencias del sistema
- ✅ Instala dependencias de Python
- ✅ Crea la aplicación .app en /Applications
- ✅ Configura comando de terminal
- ✅ Configura permisos necesarios

### Opción 2: Solo ejecutar (sin instalación)
```bash
./launch_simplevoice.sh
```

## 🎯 Formas de Ejecutar SimpleVoice

### 1. Desde Finder (más fácil)
- Abre **Finder** → **Aplicaciones**
- Busca **SimpleVoice.app**
- Haz doble clic para ejecutar

### 2. Desde Launchpad
- Abre **Launchpad** (F4 o gesture)
- Busca **SimpleVoice**
- Haz clic para ejecutar

### 3. Desde Terminal
```bash
simplevoice
```

### 4. Ejecución Directa
```bash
cd /ruta/a/SimpleVoice
./launch_simplevoice.sh
```

## 🔧 Qué Hace la Aplicación .app

### Proceso Automático:
1. **Detecta** la ubicación del proyecto SimpleVoice
2. **Verifica** que Python 3 esté instalado
3. **Crea** un entorno virtual si no existe
4. **Instala** dependencias automáticamente
5. **Verifica** permisos de micrófono
6. **Ejecuta** la aplicación GUI

### Ubicaciones de Búsqueda:
La aplicación busca SimpleVoice en estas ubicaciones:
- `~/Documents/GitHub/SimpleVoice`
- `~/Documents/SimpleVoice`
- `~/Desktop/SimpleVoice`
- `~/Downloads/SimpleVoice`
- `/Applications/SimpleVoice`

## 🛠 Solución de Problemas

### Error: "No se pudo encontrar SimpleVoice"
- Asegúrate de que el proyecto esté en una de las ubicaciones listadas arriba
- O ejecuta `./launch_simplevoice.sh` directamente desde el directorio del proyecto

### Error: "Python 3 no está instalado"
```bash
# Instalar con Homebrew
brew install python3

# O descargar desde python.org
open https://python.org/downloads/
```

### Error: "PyAudio no se puede instalar"
```bash
# Instalar dependencias de audio
brew install portaudio

# Luego reinstalar PyAudio
pip3 install pyaudio
```

### Problemas con Permisos
1. **Micrófono**: Ve a **Configuración del Sistema** → **Privacidad y Seguridad** → **Micrófono**
2. **Accesibilidad**: Ve a **Configuración del Sistema** → **Privacidad y Seguridad** → **Accesibilidad**
3. Agrega **Terminal** y **SimpleVoice** a las aplicaciones permitidas

### La aplicación no aparece en /Applications
```bash
# Crear enlace manualmente
ln -s /ruta/completa/a/SimpleVoice/SimpleVoice.app /Applications/
```

## 📁 Estructura de Archivos

```
SimpleVoice/
├── SimpleVoice.app/              # Aplicación macOS
│   └── Contents/
│       ├── Info.plist            # Configuración de la app
│       ├── MacOS/
│       │   └── SimpleVoice       # Ejecutable principal
│       └── Resources/
│           └── SimpleVoice.icns  # Icono de la aplicación
├── launch_simplevoice.sh         # Launcher principal
├── install.sh                    # Instalador automático
├── create_icon.sh                # Generador de iconos
├── src/                          # Código fuente
│   ├── main_gui.py              # GUI principal
│   ├── gui.py                   # Interfaz gráfica
│   └── recorder.py              # Grabación de audio
├── requirements-gui.txt          # Dependencias GUI
└── requirements.txt             # Dependencias básicas
```

## 🔄 Actualizaciones

Para actualizar SimpleVoice:
1. Haz `git pull` en el directorio del proyecto
2. Ejecuta `./install.sh` nuevamente
3. O simplemente ejecuta la aplicación (actualizará dependencias automáticamente)

## 🚀 Para Desarrolladores

### Compilar a Ejecutable Standalone
```bash
# Instalar PyInstaller
pip3 install pyinstaller

# Crear ejecutable
pyinstaller --onefile --windowed src/main_gui.py
```

### Personalizar la Aplicación .app
- **Icono**: Reemplaza `SimpleVoice.app/Contents/Resources/SimpleVoice.icns`
- **Configuración**: Edita `SimpleVoice.app/Contents/Info.plist`
- **Comportamiento**: Modifica `SimpleVoice.app/Contents/MacOS/SimpleVoice`

## 📞 Soporte

- **Repositorio**: [GitHub - SimpleVoice](https://github.com/tu-usuario/SimpleVoice)
- **Issues**: Reporta problemas en GitHub Issues
- **Documentación**: Revisa el README.md principal del proyecto

---

> **Nota**: Esta aplicación .app está diseñada específicamente para macOS y automatiza completamente el proceso de instalación y ejecución de SimpleVoice.