#!/bin/bash

# SimpleVoice - Script de Instalación Automática
# Configura todo lo necesario para ejecutar SimpleVoice fácilmente

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Función para mostrar mensajes con estilo
print_header() {
    echo -e "\n${BOLD}${BLUE}========================================${NC}"
    echo -e "${BOLD}${BLUE}  SimpleVoice - Instalador Automático  ${NC}"
    echo -e "${BOLD}${BLUE}========================================${NC}\n"
}

print_step() {
    echo -e "${BLUE}[PASO]${NC} $1"
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

# Mostrar header
print_header

# Obtener el directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="SimpleVoice"

print_step "Verificando sistema operativo..."
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "Este instalador está diseñado para macOS únicamente."
    exit 1
fi
print_success "macOS detectado"

print_step "Verificando dependencias del sistema..."

# Verificar Python 3
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado."
    print_info "Descárgalo desde: https://python.org/downloads/"
    print_info "O instálalo usando Homebrew: brew install python3"
    exit 1
fi
print_success "Python 3 encontrado: $(python3 --version)"

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 no está instalado."
    print_info "Instálalo con: python3 -m ensurepip --upgrade"
    exit 1
fi
print_success "pip3 encontrado"

# Verificar herramientas de audio (opcional)
if ! python3 -c "import pyaudio" 2>/dev/null; then
    print_warning "PyAudio podría requerir dependencias adicionales."
    print_info "Si tienes problemas, instala portaudio: brew install portaudio"
fi

print_step "Configurando SimpleVoice..."

# Crear enlace simbólico en /Applications si no existe
APP_LINK="/Applications/SimpleVoice.app"
if [ ! -L "$APP_LINK" ] && [ ! -d "$APP_LINK" ]; then
    print_step "Creando enlace en /Applications..."
    if ln -s "$SCRIPT_DIR/SimpleVoice.app" "$APP_LINK" 2>/dev/null; then
        print_success "SimpleVoice.app disponible en /Applications"
    else
        print_warning "No se pudo crear enlace en /Applications (permisos insuficientes)"
        print_info "Puedes usar la aplicación desde: $SCRIPT_DIR/SimpleVoice.app"
    fi
else
    print_success "SimpleVoice.app ya está disponible en /Applications"
fi

# Crear script de acceso rápido en PATH
LAUNCHER_PATH="/usr/local/bin/simplevoice"
print_step "Configurando comando 'simplevoice' en terminal..."

# Crear el script launcher
LAUNCHER_CONTENT="#!/bin/bash
# SimpleVoice - Launcher de terminal
cd \"$SCRIPT_DIR\"
./launch_simplevoice.sh
"

if echo "$LAUNCHER_CONTENT" > "$LAUNCHER_PATH" 2>/dev/null && chmod +x "$LAUNCHER_PATH" 2>/dev/null; then
    print_success "Comando 'simplevoice' disponible en terminal"
else
    print_warning "No se pudo crear el comando 'simplevoice' (permisos insuficientes)"
    print_info "Para usarlo desde terminal, ejecuta: $SCRIPT_DIR/launch_simplevoice.sh"
fi

print_step "Instalando dependencias de Python..."

# Crear entorno virtual
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    print_success "Entorno virtual creado"
fi

# Activar entorno virtual e instalar dependencias
source "$VENV_DIR/bin/activate"

# Instalar dependencias GUI
if [ -f "$SCRIPT_DIR/requirements-gui.txt" ]; then
    pip3 install -r "$SCRIPT_DIR/requirements-gui.txt"
    print_success "Dependencias instaladas desde requirements-gui.txt"
elif [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip3 install -r "$SCRIPT_DIR/requirements.txt"
    print_success "Dependencias instaladas desde requirements.txt"
else
    print_warning "No se encontraron archivos de requirements"
fi

print_step "Configurando permisos de macOS..."
print_info "SimpleVoice necesita los siguientes permisos:"
print_info "  • Acceso al micrófono (para reconocimiento de voz)"
print_info "  • Accesibilidad (para escribir texto en otras apps)"
print_info "  • Control de aplicaciones (para automatización)"
print_warning "macOS te pedirá estos permisos la primera vez que ejecutes la aplicación."

# Verificar estructura del proyecto
print_step "Verificando estructura del proyecto..."
REQUIRED_FILES=("src/main_gui.py" "launch_simplevoice.sh" "SimpleVoice.app/Contents/Info.plist")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        print_success "Encontrado: $file"
    else
        print_error "Falta archivo requerido: $file"
        exit 1
    fi
done

# Mostrar resumen de instalación
echo -e "\n${BOLD}${GREEN}¡Instalación completada exitosamente!${NC}\n"

echo -e "${BOLD}Formas de ejecutar SimpleVoice:${NC}"
echo -e "  1. ${GREEN}Desde Finder:${NC} Abre /Applications/SimpleVoice.app"
echo -e "  2. ${GREEN}Desde Launchpad:${NC} Busca 'SimpleVoice'"
echo -e "  3. ${GREEN}Desde Terminal:${NC} Ejecuta 'simplevoice'"
echo -e "  4. ${GREEN}Directamente:${NC} Ejecuta '$SCRIPT_DIR/launch_simplevoice.sh'"

echo -e "\n${BOLD}Notas importantes:${NC}"
echo -e "  • La primera ejecución puede tardar más mientras se instalan dependencias"
echo -e "  • macOS pedirá permisos para micrófono y accesibilidad"
echo -e "  • Si hay problemas con PyAudio, instala: ${YELLOW}brew install portaudio${NC}"

echo -e "\n${BOLD}Soporte:${NC}"
echo -e "  • Repositorio: https://github.com/tu-usuario/SimpleVoice"
echo -e "  • Para problemas: Revisa los logs en la terminal"

echo -e "\n${GREEN}¡Disfruta usando SimpleVoice! 🎤✨${NC}\n"