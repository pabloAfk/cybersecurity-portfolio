#!/bin/bash
# ============================================
# CryptoSystem - Instalador
# Uso interno: chamado pelo start.sh
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "╔════════════════════════════════════════════════╗"
echo "║   CryptoSystem - Instalador                   ║"
echo "║   Criptografia Homofônica                     ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

cd "$PROJECT_ROOT"

# Detecta gerenciador de pacotes
detect_package_manager() {
    if command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v apt &> /dev/null; then
        echo "apt"
    elif command -v pacman &> /dev/null; then
        echo "pacman"
    else
        echo "unknown"
    fi
}

PKG_MANAGER=$(detect_package_manager)
echo "📦 Gerenciador detectado: $PKG_MANAGER"

# Instala dependências do sistema (se necessário)
if [ "$PKG_MANAGER" = "dnf" ]; then
    echo "🔧 Instalando dependências (Fedora/Nobara)..."
    sudo dnf install -y python3-pip python3-devel python3-gobject webkit2gtk4.1 webkit2gtk4.1-devel gtk3 cairo-devel gobject-introspection-devel pkg-config gcc
elif [ "$PKG_MANAGER" = "apt" ]; then
    echo "🔧 Instalando dependências (Ubuntu/Debian)..."
    sudo apt update
    sudo apt install -y python3-pip python3-dev python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.0 libcairo2-dev libgirepository1.0-dev pkg-config gcc
fi

# Cria ambiente virtual
echo ""
echo "🐍 Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instala dependências Python
pip install --upgrade pip
pip install -r requirements.txt
pip install PyGObject

# Cria diretórios necessários
mkdir -p src/backend
mkdir -p src/frontend/js

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "🚀 Para iniciar: ./start.sh"
