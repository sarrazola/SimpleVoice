# 🎙️ SimpleVoice - Desktop App Construction

## 📋 Project Summary

Your SimpleVoice application has been converted into a modern desktop app with:

- ✅ **Modern graphical interface** with CustomTkinter
- ✅ **Visible logs** both in GUI and files
- ✅ **Global hotkeys** (F12 works from any app)
- ✅ **Independent executable** (user doesn't need Python)
- ✅ **Automatic logs** saved in ~/SimpleVoice/logs/
- ✅ **Automated packaging** with PyInstaller

## 🗂️ Created File Structure

```
SimpleVoice/
├── src/
│   ├── __init__.py           # Python package
│   ├── recorder.py           # Recording logic (refactored)
│   ├── gui.py               # Modern graphical interface
│   └── main_gui.py          # Main entry point
├── requirements-gui.txt      # GUI dependencies
├── SimpleVoice.spec         # PyInstaller configuration
├── build.py                 # Automated build script
└── INSTRUCTIONS.md          # This file
```

## 🚀 Steps to Build the App

### 1. Install Dependencies
```bash
pip install -r requirements-gui.txt
```

### 2. Build Application (Automatic)
```bash
python build.py
```

### 3. Build Application (Manual)
```bash
pyinstaller SimpleVoice.spec --noconfirm
```

## 📁 Generated Files

After building you'll find:

- `dist/SimpleVoice.app` (macOS) or `dist/SimpleVoice` (Linux/Windows)
- `SimpleVoice-[platform].zip` - Distribution package
- `README-Distribution.md` - Instructions for end users

## 🎯 How to Use the Application

### For Developers (Development Mode)
```bash
cd src
python main_gui.py
```

### For End Users
1. Extract the ZIP file
2. Open SimpleVoice.app (macOS) or SimpleVoice.exe (Windows)
3. **Use from menu bar** (recommended):
   - Look for the blue circular icon in the top menu bar
   - Right click → "🎙️ Start Recording"
   - Speak clearly
   - Right click → "⏹️ Stop Recording"
   - Text is automatically copied to clipboard
4. **Use from graphical interface**:
   - Press F12 to record
   - Speak clearly
   - Press F12 to stop and transcribe
5. **Closing the window** doesn't close the app (stays in system tray)
6. To **exit completely**: System Tray → "❌ Quit"

## 📊 Logging System

### Visible Logs in GUI
- Collapsible logs area in the interface
- "View Logs" button to open complete file
- Real-time logs during recording

### Logs in Files
- Location: `~/SimpleVoice/logs/`
- Format: `simplevoice_YYYYMMDD_HHMMSS.log`
- Detailed logs for debugging

## 🔧 Advanced Features

### Graphical Interface
- **System theme** by default
- **Large buttons** and easy to use
- **Visual states** (recording, processing, ready)
- **Editable transcription area**
- **Collapsible logs** for monitoring

### Functionalities
- **Global F12 hotkey** (works from any app)
- **Automatic copy** to clipboard
- **Multi-language transcription** with Whisper Turbo
- **Automatic resource management**
- **Visual status notifications**
- **🆕 System Tray**: Permanent icon in macOS menu bar
  - **Visual state**: Blue (ready) / Red (recording)
  - **🎙️ Record**: Start/stop recording from menu
  - **⚙️ Options**: Show/hide main window
  - **❌ Quit**: Completely close the application
  - **Synchronization**: State updates automatically with F12
- **🌍 Language Selection**: Dropdown with 15+ supported languages
  - **Auto-detection** (default): Whisper automatically detects language
  - **Immediate change**: No need to restart application
  - **Languages included**: Spanish, English, French, German, Italian, Portuguese, Japanese, Korean, Chinese, Russian, Dutch, Swedish, Norwegian, Danish
- **🤖 Model Selection**: Dropdown with rich performance information
  - **6 available models**: Tiny, Base, Small, Medium, Large, Turbo
  - **Visual information**: Speed (⚡) and accuracy (⭐) for each model
  - **Automatic download**: Models download when selected
  - **Sizes**: From 39MB (Tiny) to 1.5GB (Large)
  - **Recommended**: Turbo (805MB) - Optimal speed/accuracy balance

## 🛠️ Customization

### Change Language
**🎯 From Graphical Interface (Recommended):**
- Use the "Language" dropdown in the configuration section
- Select from 15+ available languages
- Includes auto-detection of language
- Immediate change, no restart needed

**🔧 Programmatically:**
```python
# In code, if you need to change default
self.recorder.set_language("en")  # Change to English
self.recorder.set_language(None)  # Auto-detect
```

### Change Model
**🎯 From Graphical Interface (Recommended):**
- Use the "Transcription Model" dropdown
- View speed and accuracy information for each model
- Automatic download if model isn't available
- Immediate change with visual feedback

**📊 Model Guide:**
- **⚡ Tiny (39MB)**: For very fast basic transcription
- **🏃 Base (74MB)**: Lightweight general use
- **⚖️ Small (244MB)**: Ideal speed/quality balance
- **🎯 Medium (769MB)**: High accuracy for complex audio
- **👑 Large (1.5GB)**: Maximum accuracy for critical cases
- **🚀 Turbo (805MB)**: Recommended - Optimized and accurate

**🔧 Programmatically:**
```python
# Change model in code
self.recorder.set_model("small")  # Change to small model
```

### Change Hotkey
In `src/gui.py`, line ~220:
```python
if key == keyboard.Key.f12:  # Change to another key
```

### Change Theme
In `src/gui.py`, line ~19:
```python
ctk.set_appearance_mode("system")  # "light", "dark", or "system"
```

## 📦 Distribution

### Create Distribution Package
```bash
python build.py
```

### Share with Users
1. Send `SimpleVoice-[platform].zip` file
2. Include `README-Distribution.md`
3. Mention they need microphone permissions

## 🔧 Troubleshooting

### Error: "CustomTkinter not found"
```bash
pip install customtkinter
```

### Error: "PyAudio not found"
```bash
# macOS
brew install portaudio
pip install pyaudio

# Linux
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### Error: "Permission denied for microphone"
1. Go to System Preferences → Security & Privacy → Privacy
2. Click "Microphone"
3. Check the box next to SimpleVoice
4. Restart the application

### Error: "F12 hotkey not working"
1. Go to System Preferences → Security & Privacy → Privacy
2. Click "Accessibility"
3. Add SimpleVoice to the list and check the box
4. Restart the application

## 🎉 Ready to Use!

SimpleVoice is optimized to provide you with the best voice transcription experience. With its intuitive interface and powerful AI technology, converting your voice to text has never been easier.

**Press F12 and start transcribing! 🎙️** 