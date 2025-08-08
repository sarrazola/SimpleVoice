#!/bin/bash

# SimpleVoice - Automatic Installation Script
# Sets up everything needed to run SimpleVoice easily

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Function to display styled messages
print_header() {
    echo -e "\n${BOLD}${BLUE}========================================${NC}"
    echo -e "${BOLD}${BLUE}  SimpleVoice - Automatic Installer   ${NC}"
    echo -e "${BOLD}${BLUE}========================================${NC}\n"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Show header
print_header

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="SimpleVoice"

print_step "Checking operating system..."
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This installer is designed for macOS only."
    exit 1
fi
print_success "macOS detected"

print_step "Checking system dependencies..."

# Check Python 3
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed."
    print_info "Download from: https://python.org/downloads/"
    print_info "Or install using Homebrew: brew install python3"
    exit 1
fi
print_success "Python 3 found: $(python3 --version)"

# Check pip
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed."
    print_info "Install with: python3 -m ensurepip --upgrade"
    exit 1
fi
print_success "pip3 found"

# Check and install PortAudio (required for PyAudio)
print_step "Checking PortAudio dependencies..."
if ! pkg-config --exists portaudio-2.0 2>/dev/null && ! brew list portaudio &>/dev/null; then
    print_warning "PortAudio not found. This is required for PyAudio to work."
    
    if command -v brew &> /dev/null; then
        print_step "Installing PortAudio via Homebrew..."
        brew install portaudio
        print_success "PortAudio installed successfully"
    else
        print_error "Homebrew not found. PortAudio installation required."
        print_info "Please install Homebrew first: https://brew.sh"
        print_info "Then run: brew install portaudio"
        print_info "After that, re-run this installer."
        exit 1
    fi
else
    print_success "PortAudio is available"
fi

print_step "Checking FFmpeg dependency..."
if ! command -v ffmpeg &> /dev/null; then
    print_warning "FFmpeg not found. This is required by Whisper to process audio."
    if command -v brew &> /dev/null; then
        print_step "Installing FFmpeg via Homebrew..."
        brew install ffmpeg || {
            print_error "Failed to install FFmpeg automatically."
            print_info "You can try manually: brew install ffmpeg"
            exit 1
        }
        print_success "FFmpeg installed successfully"
    else
        print_error "Homebrew not found. FFmpeg installation required."
        print_info "Please install Homebrew first: https://brew.sh"
        print_info "Then run: brew install ffmpeg"
        print_info "After that, re-run this installer."
        exit 1
    fi
else
    print_success "FFmpeg is available: $(ffmpeg -version | head -n 1)"
fi

print_step "Setting up SimpleVoice..."

# Create symbolic link in /Applications if it doesn't exist
APP_LINK="/Applications/SimpleVoice.app"
if [ ! -L "$APP_LINK" ] && [ ! -d "$APP_LINK" ]; then
    print_step "Creating link in /Applications..."
    if ln -s "$SCRIPT_DIR/SimpleVoice.app" "$APP_LINK" 2>/dev/null; then
        print_success "SimpleVoice.app available in /Applications"
    else
        print_warning "Could not create link in /Applications (insufficient permissions)"
        print_info "You can use the app from: $SCRIPT_DIR/SimpleVoice.app"
    fi
else
    print_success "SimpleVoice.app already available in /Applications"
fi

# Create quick access script in PATH
LAUNCHER_PATH="/usr/local/bin/simplevoice"
print_step "Setting up 'simplevoice' terminal command..."

# Create launcher script
LAUNCHER_CONTENT="#!/bin/bash
# SimpleVoice - Terminal launcher
cd \"$SCRIPT_DIR\"
./launch_simplevoice.sh
"

if echo "$LAUNCHER_CONTENT" > "$LAUNCHER_PATH" 2>/dev/null && chmod +x "$LAUNCHER_PATH" 2>/dev/null; then
    print_success "'simplevoice' command available in terminal"
else
    print_warning "Could not create 'simplevoice' command (insufficient permissions)"
    print_info "To use from terminal, run: $SCRIPT_DIR/launch_simplevoice.sh"
fi

print_step "Installing Python dependencies..."

# Create virtual environment
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created"
fi

# Activate virtual environment and install dependencies
source "$VENV_DIR/bin/activate"

# Install GUI dependencies
if [ -f "$SCRIPT_DIR/requirements-gui.txt" ]; then
    pip3 install -r "$SCRIPT_DIR/requirements-gui.txt"
    print_success "Dependencies installed from requirements-gui.txt"
elif [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip3 install -r "$SCRIPT_DIR/requirements.txt"
    print_success "Dependencies installed from requirements.txt"
else
    print_warning "No requirements files found"
fi

print_step "Configuring macOS permissions..."
print_info "SimpleVoice needs the following permissions:"
print_info "  • Microphone access (for speech recognition)"
print_info "  • Accessibility (to type text in other apps)"
print_info "  • Application control (for automation)"
print_warning "macOS will ask for these permissions the first time you run the app."

# Check project structure
print_step "Creating SimpleVoice.app..."

# Remove existing app if it exists
if [ -d "$SCRIPT_DIR/SimpleVoice.app" ]; then
    rm -rf "$SCRIPT_DIR/SimpleVoice.app"
fi

# Create .app structure
mkdir -p "$SCRIPT_DIR/SimpleVoice.app/Contents/MacOS"
mkdir -p "$SCRIPT_DIR/SimpleVoice.app/Contents/Resources"

# Crear Info.plist
cat > "$SCRIPT_DIR/SimpleVoice.app/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>es</string>
    
    <key>CFBundleDisplayName</key>
    <string>SimpleVoice</string>
    
    <key>CFBundleExecutable</key>
    <string>SimpleVoice</string>
    
    <key>CFBundleIconFile</key>
    <string>SimpleVoice.icns</string>
    
    <key>CFBundleIdentifier</key>
    <string>com.simplevoice.app</string>
    
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    
    <key>CFBundleName</key>
    <string>SimpleVoice</string>
    
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.productivity</string>
    
    <key>NSHighResolutionCapable</key>
    <true/>
    
    <key>NSMicrophoneUsageDescription</key>
    <string>SimpleVoice needs microphone access to convert your voice to text.</string>
    
    <key>NSAppleEventsUsageDescription</key>
    <string>SimpleVoice needs to control applications to automate text writing.</string>
    
    <key>NSAccessibilityUsageDescription</key>
    <string>SimpleVoice needs accessibility permissions to write text in other applications.</string>
    
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2024 SimpleVoice. All rights reserved.</string>
    
    <key>LSBackgroundOnly</key>
    <false/>
    
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
EOF

# Create main executable
cat > "$SCRIPT_DIR/SimpleVoice.app/Contents/MacOS/SimpleVoice" << 'EOF'
#!/bin/bash

# SimpleVoice.app - Main executable
# This script runs when you double-click the .app

# Obtener el directorio donde está instalada la aplicación
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../" && pwd)"

# Buscar el directorio del proyecto SimpleVoice
# Primero verificar si estamos en el directorio del proyecto
if [ -f "$APP_DIR/launch_simplevoice.sh" ] && [ -d "$APP_DIR/src" ]; then
    PROJECT_DIR="$APP_DIR"
else
    # Buscar en ubicaciones comunes
    SEARCH_DIRS=(
        "$HOME/Documents/GitHub/SimpleVoice"
        "$HOME/Documents/SimpleVoice"
        "$HOME/Desktop/SimpleVoice"
        "$HOME/Downloads/SimpleVoice"
        "/Applications/SimpleVoice"
    )
    
    PROJECT_DIR=""
    for dir in "${SEARCH_DIRS[@]}"; do
        if [ -f "$dir/launch_simplevoice.sh" ] && [ -d "$dir/src" ]; then
            PROJECT_DIR="$dir"
            break
        fi
    done
    
    # Si no se encuentra, mostrar diálogo de error
    if [ -z "$PROJECT_DIR" ]; then
        osascript -e 'display dialog "Could not find SimpleVoice. Please make sure the project is in ~/Documents/GitHub/SimpleVoice or another standard location." buttons {"OK"} default button "OK" with icon stop'
        exit 1
    fi
fi

# Cambiar al directorio del proyecto
cd "$PROJECT_DIR"

# Verificar que el launcher existe
if [ ! -f "launch_simplevoice.sh" ]; then
    osascript -e 'display dialog "Error: launch_simplevoice.sh not found in project directory." buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi

# Mostrar una notificación de que se está iniciando
osascript -e 'display notification "Starting SimpleVoice..." with title "SimpleVoice"'

# Ejecutar el launcher en una nueva ventana de Terminal
osascript <<APPLESCRIPT
tell application "Terminal"
    activate
    do script "cd '$PROJECT_DIR' && ./launch_simplevoice.sh"
end tell
APPLESCRIPT
EOF

# Give execution permissions
chmod +x "$SCRIPT_DIR/SimpleVoice.app/Contents/MacOS/SimpleVoice"

print_step "Creating app icon..."

# Create a basic icon using macOS tools
create_icon() {
    ICON_DIR="$SCRIPT_DIR/SimpleVoice.app/Contents/Resources"
    ICONSET_DIR="$SCRIPT_DIR/SimpleVoice.iconset"
    
    # Create iconset directory
    mkdir -p "$ICONSET_DIR"
    
    # Use SimpleVoice custom logo
    CUSTOM_LOGO="$SCRIPT_DIR/src/logo/simple_voice.png"
    
    # Check if we have the necessary tools and custom logo
    if command -v sips &> /dev/null && [ -f "$CUSTOM_LOGO" ]; then        
        print_success "Using custom logo: $CUSTOM_LOGO"
        
        # Resize logo to 1024x1024 if necessary
        sips -z 1024 1024 "$CUSTOM_LOGO" --out "$SCRIPT_DIR/temp_1024.png" &> /dev/null
        
        if [ -f "$SCRIPT_DIR/temp_1024.png" ]; then
            
            # Create all necessary sizes using sips
            sips -z 16 16 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_16x16.png" &> /dev/null
            sips -z 32 32 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_16x16@2x.png" &> /dev/null
            sips -z 32 32 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_32x32.png" &> /dev/null
            sips -z 64 64 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_32x32@2x.png" &> /dev/null
            sips -z 128 128 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_128x128.png" &> /dev/null
            sips -z 256 256 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_128x128@2x.png" &> /dev/null
            sips -z 256 256 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_256x256.png" &> /dev/null
            sips -z 512 512 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_256x256@2x.png" &> /dev/null
            sips -z 512 512 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_512x512.png" &> /dev/null
            sips -z 1024 1024 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_512x512@2x.png" &> /dev/null
            
            # Create .icns file
            iconutil -c icns "$ICONSET_DIR" -o "$ICON_DIR/SimpleVoice.icns" 2>/dev/null
            
            if [ $? -eq 0 ]; then
                print_success "Icon created successfully"
            else
                print_warning "Could not create .icns file"
            fi
            
            # Clean temporary files
            rm -f "$SCRIPT_DIR/temp_1024.png"
        else
            print_warning "Could not process custom logo"
        fi
    else
        if [ ! -f "$CUSTOM_LOGO" ]; then
            print_warning "Custom logo not found: $CUSTOM_LOGO"
            print_info "Will create a basic icon instead"
        fi
        
        if ! command -v sips &> /dev/null; then
            print_warning "sips not available. Could not create icon."
        fi
        
        # Fallback: create basic icon if no custom logo
        create_fallback_icon
    fi
    
    # Clean temporary files
    rm -rf "$ICONSET_DIR"
}

# Function to create basic fallback icon
create_fallback_icon() {
    print_info "Creating basic icon..."
    
    # Create simple SVG icon as fallback
    cat > "$SCRIPT_DIR/temp_icon.svg" << 'SVGEOF'
<svg width="1024" height="1024" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4A90E2;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#2E5BBA;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Fondo circular -->
  <circle cx="512" cy="512" r="450" fill="url(#grad1)" stroke="#1B4F8C" stroke-width="20"/>
  
  <!-- Micrófono -->
  <rect x="456" y="300" width="112" height="200" rx="56" ry="56" fill="white" opacity="0.9"/>
  
  <!-- Base del micrófono -->
  <rect x="486" y="500" width="52" height="80" fill="white" opacity="0.9"/>
  
  <!-- Stand del micrófono -->
  <rect x="400" y="580" width="224" height="20" rx="10" ry="10" fill="white" opacity="0.9"/>
  
  <!-- Ondas de sonido -->
  <path d="M 620 420 Q 660 420 660 460 Q 660 500 620 500" stroke="white" stroke-width="8" fill="none" opacity="0.7"/>
  <path d="M 640 400 Q 700 400 700 460 Q 700 520 640 520" stroke="white" stroke-width="8" fill="none" opacity="0.5"/>
  <path d="M 660 380 Q 740 380 740 460 Q 740 540 660 540" stroke="white" stroke-width="8" fill="none" opacity="0.3"/>
</svg>
SVGEOF
    
    if command -v sips &> /dev/null; then        
        # Convert SVG to 1024x1024 PNG
        qlmanage -t -s 1024 -o "$SCRIPT_DIR" "$SCRIPT_DIR/temp_icon.svg" 2>/dev/null
        
        if [ -f "$SCRIPT_DIR/temp_icon.svg.png" ]; then
            mv "$SCRIPT_DIR/temp_icon.svg.png" "$SCRIPT_DIR/temp_1024.png"
            
            # Create all necessary sizes using sips
            sips -z 16 16 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_16x16.png" &> /dev/null
            sips -z 32 32 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_16x16@2x.png" &> /dev/null
            sips -z 32 32 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_32x32.png" &> /dev/null
            sips -z 64 64 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_32x32@2x.png" &> /dev/null
            sips -z 128 128 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_128x128.png" &> /dev/null
            sips -z 256 256 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_128x128@2x.png" &> /dev/null
            sips -z 256 256 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_256x256.png" &> /dev/null
            sips -z 512 512 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_256x256@2x.png" &> /dev/null
            sips -z 512 512 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_512x512.png" &> /dev/null
            sips -z 1024 1024 "$SCRIPT_DIR/temp_1024.png" --out "$ICONSET_DIR/icon_512x512@2x.png" &> /dev/null
            
            # Create .icns file
            iconutil -c icns "$ICONSET_DIR" -o "$ICON_DIR/SimpleVoice.icns" 2>/dev/null
            
            # Clean temporary files
            rm -f "$SCRIPT_DIR/temp_1024.png"
        fi
    fi
    
    # Clean temporary files
    rm -f "$SCRIPT_DIR/temp_icon.svg"
}

# Run icon creation
create_icon

print_success "SimpleVoice.app created successfully"

print_step "Checking project structure..."
REQUIRED_FILES=("src/main_gui.py" "launch_simplevoice.sh")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        print_success "Found: $file"
    else
        print_error "Missing required file: $file"
        exit 1
    fi
done

# Show installation summary
echo -e "\n${BOLD}${GREEN}Installation completed successfully!${NC}\n"

echo -e "${BOLD}Ways to run SimpleVoice:${NC}"
echo -e "  1. ${GREEN}From Finder:${NC} Open /Applications/SimpleVoice.app"
echo -e "  2. ${GREEN}From Launchpad:${NC} Search 'SimpleVoice'"
echo -e "  3. ${GREEN}From Terminal:${NC} Run 'simplevoice'"
echo -e "  4. ${GREEN}Directly:${NC} Run '$SCRIPT_DIR/launch_simplevoice.sh'"

echo -e "\n${BOLD}Important notes:${NC}"
echo -e "  • First run may take longer while installing dependencies"
echo -e "  • macOS will ask for microphone and accessibility permissions"
echo -e "  • If you have PyAudio issues, install: ${YELLOW}brew install portaudio${NC}"

echo -e "\n${BOLD}Support:${NC}"
echo -e "  • Repository: https://github.com/sarrazola/SimpleVoice"
echo -e "  • For issues: Check logs in terminal"

echo -e "\n${GREEN}Enjoy using SimpleVoice! 🎤✨${NC}\n"