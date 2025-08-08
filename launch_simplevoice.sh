#!/bin/bash

# SimpleVoice Launcher Script
# Automates dependency installation and SimpleVoice execution

set -e  # Exit if any command fails

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display colored messages
print_status() {
    echo -e "${BLUE}[SimpleVoice]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SimpleVoice]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[SimpleVoice]${NC} $1"
}

print_error() {
    echo -e "${RED}[SimpleVoice]${NC} $1"
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

print_status "Starting SimpleVoice..."
print_status "Project directory: $PROJECT_ROOT"

# Change to project directory
cd "$PROJECT_ROOT"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3 from https://python.org"
    exit 1
fi

print_success "Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3"
    exit 1
fi

# Create virtual environment if it doesn't exist
VENV_DIR="$PROJECT_ROOT/.venv"
if [ ! -d "$VENV_DIR" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Function to check if a package is installed
is_package_installed() {
    python3 -c "import $1" 2>/dev/null
}

# Check and install dependencies
print_status "Checking dependencies..."

REQUIREMENTS_FILE="$PROJECT_ROOT/requirements-gui.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    # Check if we need to install dependencies
    NEED_INSTALL=false
    
    # List of critical packages to check
    CRITICAL_PACKAGES=("customtkinter" "whisper" "pyaudio" "pynput" "pyperclip")
    
    for package in "${CRITICAL_PACKAGES[@]}"; do
        if ! is_package_installed "$package"; then
            NEED_INSTALL=true
            break
        fi
    done
    
    if [ "$NEED_INSTALL" = true ]; then
        print_status "Installing dependencies..."
        pip3 install -r "$REQUIREMENTS_FILE"
        print_success "Dependencies installed"
    else
        print_success "All dependencies are installed"
    fi
else
    print_warning "requirements-gui.txt file not found, trying requirements.txt"
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        pip3 install -r "$PROJECT_ROOT/requirements.txt"
    else
        print_error "No requirements files found"
        exit 1
    fi
fi

# Check FFmpeg availability (required by Whisper)
if ! command -v ffmpeg &> /dev/null; then
    print_error "FFmpeg is not installed. It is required to process audio."
    if command -v brew &> /dev/null; then
        print_status "You can install it with: brew install ffmpeg"
    else
        print_status "Please install FFmpeg and try again."
    fi
    exit 1
fi

# Check microphone permissions on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_status "Checking microphone permissions on macOS..."
    print_warning "IMPORTANT: If this is the first time running the app,"
    print_warning "macOS will ask for microphone permissions."
    print_warning "Please accept these permissions for SimpleVoice to work correctly."
fi

# Run the application
print_status "Running SimpleVoice..."
cd "$PROJECT_ROOT/src"

# Check that the main file exists
if [ ! -f "main_gui.py" ]; then
    print_error "main_gui.py file not found in src/"
    exit 1
fi

# Run the application with error handling
if python3 main_gui.py; then
    print_success "SimpleVoice ran successfully"
else
    print_error "Error running SimpleVoice"
    print_status "Check that all dependencies are correctly installed"
    exit 1
fi