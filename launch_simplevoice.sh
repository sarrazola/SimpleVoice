#!/bin/bash

# SimpleVoice Launcher Script
# Automatiza la instalación de dependencias y ejecución de SimpleVoice

set -e  # Salir si algún comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes con color
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

# Obtener el directorio donde está este script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

print_status "Iniciando SimpleVoice..."
print_status "Directorio del proyecto: $PROJECT_ROOT"

# Cambiar al directorio del proyecto
cd "$PROJECT_ROOT"

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado. Por favor instala Python 3 desde https://python.org"
    exit 1
fi

print_success "Python 3 encontrado: $(python3 --version)"

# Verificar si pip está instalado
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 no está instalado. Por favor instala pip3"
    exit 1
fi

# Crear entorno virtual si no existe
VENV_DIR="$PROJECT_ROOT/.venv"
if [ ! -d "$VENV_DIR" ]; then
    print_status "Creando entorno virtual..."
    python3 -m venv "$VENV_DIR"
    print_success "Entorno virtual creado"
fi

# Activar entorno virtual
print_status "Activando entorno virtual..."
source "$VENV_DIR/bin/activate"

# Función para verificar si un paquete está instalado
is_package_installed() {
    python3 -c "import $1" 2>/dev/null
}

# Verificar e instalar dependencias
print_status "Verificando dependencias..."

REQUIREMENTS_FILE="$PROJECT_ROOT/requirements-gui.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    # Verificar si necesitamos instalar dependencias
    NEED_INSTALL=false
    
    # Lista de paquetes críticos para verificar
    CRITICAL_PACKAGES=("customtkinter" "whisper" "pyaudio" "pynput" "pyperclip")
    
    for package in "${CRITICAL_PACKAGES[@]}"; do
        if ! is_package_installed "$package"; then
            NEED_INSTALL=true
            break
        fi
    done
    
    if [ "$NEED_INSTALL" = true ]; then
        print_status "Instalando dependencias..."
        pip3 install -r "$REQUIREMENTS_FILE"
        print_success "Dependencias instaladas"
    else
        print_success "Todas las dependencias están instaladas"
    fi
else
    print_warning "Archivo requirements-gui.txt no encontrado, intentando con requirements.txt"
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        pip3 install -r "$PROJECT_ROOT/requirements.txt"
    else
        print_error "No se encontraron archivos de requirements"
        exit 1
    fi
fi

# Verificar permisos de micrófono en macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_status "Verificando permisos de micrófono en macOS..."
    print_warning "IMPORTANTE: Si es la primera vez que ejecutas la aplicación,"
    print_warning "macOS te pedirá permisos para acceder al micrófono."
    print_warning "Por favor, acepta estos permisos para que SimpleVoice funcione correctamente."
fi

# Ejecutar la aplicación
print_status "Ejecutando SimpleVoice..."
cd "$PROJECT_ROOT/src"

# Verificar que el archivo principal existe
if [ ! -f "main_gui.py" ]; then
    print_error "Archivo main_gui.py no encontrado en src/"
    exit 1
fi

# Ejecutar la aplicación con manejo de errores
if python3 main_gui.py; then
    print_success "SimpleVoice se ejecutó correctamente"
else
    print_error "Error al ejecutar SimpleVoice"
    print_status "Verifica que todas las dependencias estén correctamente instaladas"
    exit 1
fi