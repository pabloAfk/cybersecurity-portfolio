#!/bin/bash
# ============================================
# CryptoSystem - Instalador
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "╔════════════════════════════════════════════════╗"
echo "║   CryptoSystem - Instalador                   ║"
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

# Instala dependências do sistema
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
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Instala dependências Python
echo "📦 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt
pip install PyGObject

# Cria diretório para o vault
mkdir -p src/backend

# Cria atalho desktop
echo ""
echo "🔗 Criando atalho no menu de aplicações..."

# Garante que o diretório existe
mkdir -p ~/.local/share/applications

# Cria o arquivo .desktop
cat > ~/.local/share/applications/crypto.desktop << DESKTOP_EOF
[Desktop Entry]
Name=CryptoSystem
Comment=Sistema de Criptografia Homofônica
Exec=$PROJECT_ROOT/start.sh
Icon=security-high
Terminal=false
Type=Application
Categories=Utility;Security;
StartupNotify=true
StartupWMClass=CryptoSystem
DESKTOP_EOF

# Verifica se o atalho foi criado
if [ -f ~/.local/share/applications/crypto.desktop ]; then
    echo "✅ Atalho criado em ~/.local/share/applications/crypto.desktop"
else
    echo "⚠️ Falha ao criar atalho"
fi

# Tenta atualizar o cache do menu (para GNOME/KDE)
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database ~/.local/share/applications/
    echo "✅ Cache de aplicações atualizado"
fi

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Para iniciar:"
echo ""
echo "   1. Menu de aplicações: 'CryptoSystem'"
echo "   2. Terminal: ./start.sh"
echo ""
echo "📂 Local do atalho: ~/.local/share/applications/crypto.desktop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  Lembre-se: Este sistema é EDUCACIONAL"
echo "   Não usar para proteger dados reais!"
echo ""
