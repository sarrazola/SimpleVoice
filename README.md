# SimpleVoice 🎙️

**A free and open source voice-to-text transcription alternative**

SimpleVoice is a modern voice transcription tool that uses OpenAI Whisper to convert your voice to text quickly and accurately. Unlike commercial solutions, SimpleVoice is completely free, open source, and runs locally on your computer, ensuring your data privacy.

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-sarrazola/SimpleVoice-black)](https://github.com/sarrazola/SimpleVoice/)

## 🌟 Features

- 🎤 **Modern and user-friendly GUI**
- 🚀 **Fast and accurate transcription** with optimized Whisper models
- 🌍 **Multi-language support** with automatic detection
- ⌨️ **Configurable global F12 hotkey** for quick recording
- 📋 **Auto-copy to clipboard** for efficient workflow
- 🔒 **100% private** - everything runs locally
- 📝 **Detailed logging** for debugging and tracking
- 🎯 **Multiple Whisper models** (Turbo, Base, Small, etc.)
- 🔧 **Customizable configuration** for language and model settings

## 🚀 Installation

### 🍎 macOS - Instalación Súper Fácil (Recomendada)

**¿Quieres que SimpleVoice funcione como cualquier aplicación de macOS? ¡Solo 3 comandos!**

```bash
git clone https://github.com/sarrazola/SimpleVoice.git
cd SimpleVoice
./install.sh
```

**🎉 ¡YA ESTÁ LISTO!** El instalador automáticamente:
- ✅ Crea **SimpleVoice.app** en /Applications
- ✅ Instala **todas las dependencias** de Python
- ✅ Configura **permisos** de micrófono
- ✅ Crea comando **`simplevoice`** para terminal

**Ahora puedes usar SimpleVoice como cualquier app de macOS:**
- 🖱️ **Desde Finder**: /Applications/SimpleVoice.app 
- 🚀 **Desde Launchpad**: Busca "SimpleVoice"
- 💻 **Desde Terminal**: Escribe `simplevoice`

> **💡 Nota**: No necesitas hacer `cd` a ningún directorio ni recordar rutas. ¡Funciona desde cualquier lugar!

### 📖 Instalación Manual (Todas las Plataformas)

#### 1. Clone the project
```bash
git clone https://github.com/sarrazola/SimpleVoice.git
cd SimpleVoice
```

#### 2. Install ffmpeg (required by Whisper)
```bash
# On macOS with Homebrew
brew install ffmpeg

# On Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# On Windows (with Chocolatey)
choco install ffmpeg
```

#### 3. Install Python dependencies
```bash
# For GUI interface (recommended)
pip install -r requirements-gui.txt

# Or for terminal only
pip install -r requirements.txt
```

**Note for macOS**: If you have issues with pyaudio:
```bash
brew install portaudio 
pip install pyaudio
```

#### 4. Configure permissions (macOS)
On macOS, you need to grant microphone permissions:
1. Go to **System Settings** > **Privacy & Security** > **Microphone**
2. Add **Terminal** or your preferred terminal application
3. Add **Python** if it appears in the list

## 🎯 Usage

### 🍎 macOS - Después de Instalación Automática

**Opción 1 - Desde Aplicaciones (más fácil):**
- Abre **Finder** → **Aplicaciones**
- Busca **SimpleVoice.app** y haz doble clic

**Opción 2 - Desde Launchpad:**
- Presiona **F4** o haz gesture de Launchpad
- Busca **SimpleVoice** y haz clic

**Opción 3 - Desde Terminal:**
```bash
simplevoice
```

**Opción 4 - Launcher directo:**
```bash
cd SimpleVoice
./launch_simplevoice.sh
```

### 📖 Manual - GUI Interface (All Platforms)
```bash
cd src
python main_gui.py
```

The GUI includes:

#### 🏠 **Home Screen**
- **"Start Recording" button**: Starts voice recording
- **Status indicator**: Shows if ready (🟢 Ready)
- **Transcription area**: Displays the latest transcribed text
- **"Copy" button**: Copies transcription to clipboard

#### ⚙️ **Settings**
- **Hotkey**: Configure global key (default F12)
- **Transcription Model**: 
  - 🚀 **Turbo - Optimized (805MB)**: Fast and accurate (recommended)
  - 📱 **Base (290MB)**: Balance between speed and accuracy
  - 🔬 **Small (488MB)**: More accurate, slightly slower
- **Language**: Auto-detect or specific languages

#### ❓ **Help**
- Detailed usage instructions
- Feature information
- GitHub repository links
- Important notes about permissions

#### 📋 **Logs**
- Detailed system logging
- Useful for debugging and activity tracking

### Terminal Interface
```bash
python main.py
```

## 🔧 Workflow

1. **Start SimpleVoice**: `cd src && python main_gui.py`
2. **Configure your preferences** in the Settings section
3. **Press F12** or the "Start Recording" button
4. **Speak clearly** into the microphone
5. **Press F12 again** or "Stop" to finish
6. **Text is automatically transcribed** and copied to clipboard
7. **Paste wherever you need** with Cmd+V (macOS) or Ctrl+V (Windows/Linux)

## 🛠️ System Requirements

- **Python 3.8+**
- **ffmpeg** installed and accessible from PATH
- **Working microphone**
- **macOS/Windows/Linux** (global hotkeys optimized for macOS)
- **At least 1GB free space** for Whisper models

## 📁 Project Structure

```
SimpleVoice/
├── SimpleVoice.app/              # 🍎 macOS Application Bundle
│   └── Contents/
│       ├── Info.plist            # App configuration
│       ├── MacOS/SimpleVoice     # Main executable
│       └── Resources/            # App resources and icons
├── src/
│   ├── main_gui.py      # Main GUI interface
│   ├── main.py          # Terminal interface
│   ├── gui.py           # GUI components
│   └── recorder.py      # Recording and transcription logic
├── launch_simplevoice.sh         # 🚀 Smart launcher script
├── install.sh                    # 🔧 Automatic installer (macOS)
├── create_icon.sh                # 🎨 Icon generator
├── requirements-gui.txt          # GUI dependencies
├── requirements.txt              # Basic dependencies
├── APP_README.md                 # .app specific documentation
└── README.md                     # This file
```

## 🤝 Contributing

SimpleVoice is an open source project and contributions are welcome:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌐 Links

- **GitHub**: [https://github.com/sarrazola/SimpleVoice/](https://github.com/sarrazola/SimpleVoice/)
- **Issues**: [Report bugs or request features](https://github.com/sarrazola/SimpleVoice/issues)
- **Releases**: [Download versions](https://github.com/sarrazola/SimpleVoice/releases)

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for the transcription engine
- The open source community for making this project possible

---

**SimpleVoice** - Made with ❤️ for the open source community 