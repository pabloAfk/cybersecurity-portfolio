#!/bin/bash
# ============================================
# CryptoSystem - Instalador para Linux
# Cria ambiente virtual e atalho desktop
# ============================================

set -e  # Para o script se algum comando falhar

echo "╔════════════════════════════════════════════════╗"
echo "║   CryptoSystem - Instalador                   ║"
echo "║   Criptografia Homofônica com Interface GTK   ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# Obtém diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado!"
    echo "   Instale: sudo apt install python3 (Ubuntu/Debian)"
    echo "   ou: sudo dnf install python3 (Fedora/Nobara)"
    exit 1
fi

echo "✅ Python3 encontrado: $(python3 --version)"

# Verifica dependências GTK
echo ""
echo "📦 Verificando dependências GTK..."

MISSING_DEPS=""

if ! python3 -c "import gi" 2>/dev/null; then
    MISSING_DEPS="$MISSING_DEPS python3-gi"
fi

if ! python3 -c "from gi.repository import WebKit2" 2>/dev/null; then
    MISSING_DEPS="$MISSING_DEPS gir1.2-webkit2-4.0"
fi

if [ -n "$MISSING_DEPS" ]; then
    echo "⚠️  Dependências GTK faltando: $MISSING_DEPS"
    echo ""
    echo "Para instalar no Ubuntu/Debian:"
    echo "  sudo apt install python3-gi gir1.2-webkit2-4.0"
    echo ""
    echo "Para instalar no Fedora/Nobara:"
    echo "  sudo dnf install python3-gobject webkit2gtk4.0"
    echo ""
    read -p "Deseja instalar automaticamente? (s/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y python3-gi gir1.2-webkit2-4.0
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3-gobject webkit2gtk4.0
        else
            echo "❌ Não foi possível instalar automaticamente. Instale manualmente."
            exit 1
        fi
    else
        echo "❌ Instalação cancelada. Instale as dependências manualmente."
        exit 1
    fi
fi

# Cria ambiente virtual
echo ""
echo "🐍 Criando ambiente virtual..."
if [ -d "venv" ]; then
    echo "   Ambiente virtual já existe. Removendo..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

# Instala dependências Python
echo ""
echo "📦 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Instala PyGObject no venv
pip install PyGObject

# Verifica se backend/main.py existe
if [ ! -f "backend/main.py" ]; then
    echo "❌ Erro: backend/main.py não encontrado!"
    exit 1
fi

# Cria diretório database se não existir
mkdir -p database

# Cria atalho desktop
echo ""
echo "🔗 Criando atalho desktop..."

cat > crypto.desktop << EOF
[Desktop Entry]
Name=CryptoSystem
Comment=Sistema de Criptografia Homofônica
Exec=$SCRIPT_DIR/launcher.py
Icon=security-high
Terminal=false
Type=Application
Categories=Utility;Security;
StartupNotify=true
StartupWMClass=CryptoSystem
EOF

chmod +x launcher.py
chmod +x crypto.desktop

# Copia para aplicações do usuário
DESKTOP_FILE="$HOME/.local/share/applications/crypto.desktop"
mkdir -p "$HOME/.local/share/applications"
cp crypto.desktop "$DESKTOP_FILE"

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Para iniciar:"
echo ""
echo "   1. Pelo menu de aplicações: 'CryptoSystem'"
echo "   2. Pelo terminal: ./launcher.py"
echo "   3. Pelo atalho na área de trabalho (se copiado)"
echo ""
echo "📂 Diretório de instalação: $SCRIPT_DIR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  Lembre-se: Este sistema é EDUCACIONAL"
echo "   Não usar para proteger dados reais!"
echo ""

# Pergunta se quer executar agora
read -p "Deseja iniciar o CryptoSystem agora? (s/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    ./launcher.py
fi
