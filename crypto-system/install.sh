#!/bin/bash
# ============================================
# CryptoSystem - Instalador para Linux
# Detecta automaticamente apt/dnf/pacman/zypper
# ============================================

set -e

echo "╔════════════════════════════════════════════════╗"
echo "║   CryptoSystem - Instalador                   ║"
echo "║   Criptografia Homofônica com Interface GTK   ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# Obtém diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Detecta o gerenciador de pacotes
detect_package_manager() {
    if command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v apt &> /dev/null; then
        echo "apt"
    elif command -v pacman &> /dev/null; then
        echo "pacman"
    elif command -v zypper &> /dev/null; then
        echo "zypper"
    else
        echo "unknown"
    fi
}

PKG_MANAGER=$(detect_package_manager)
echo "📦 Gerenciador de pacotes detectado: $PKG_MANAGER"
echo ""

# Instala dependências do sistema baseado no gerenciador
install_system_deps() {
    echo "🔧 Instalando dependências do sistema..."
    
    case $PKG_MANAGER in
        dnf)
            # Fedora / Nobara / RHEL
            echo "   Usando dnf (Fedora/Nobara)..."
            
            # Nomes corretos dos pacotes no Fedora
            sudo dnf install -y \
                python3-pip \
                python3-devel \
                python3-gobject \
                python3-gobject-devel \
                webkit2gtk4.1 \
                webkit2gtk4.1-devel \
                gtk3 \
                gtk3-devel \
                cairo \
                cairo-devel \
                cairo-gobject-devel \
                gobject-introspection \
                gobject-introspection-devel \
                pkg-config \
                gcc \
                redhat-rpm-config \
                libffi-devel \
                meson \
                ninja-build
            ;;
        apt)
            # Debian / Ubuntu / Mint
            echo "   Usando apt (Debian/Ubuntu)..."
            sudo apt update
            sudo apt install -y \
                python3-pip \
                python3-dev \
                python3-gi \
                python3-gi-cairo \
                gir1.2-gtk-3.0 \
                gir1.2-webkit2-4.0 \
                libcairo2-dev \
                libgirepository1.0-dev \
                libffi-dev \
                pkg-config \
                gcc \
                build-essential \
                meson \
                ninja-build
            ;;
        pacman)
            # Arch Linux / Manjaro
            echo "   Usando pacman (Arch/Manjaro)..."
            sudo pacman -S --noconfirm \
                python-pip \
                python-gobject \
                webkit2gtk \
                gtk3 \
                cairo \
                gobject-introspection \
                pkg-config \
                gcc \
                meson \
                ninja
            ;;
        zypper)
            # openSUSE
            echo "   Usando zypper (openSUSE)..."
            sudo zypper install -y \
                python3-pip \
                python3-devel \
                python3-gobject \
                webkit2gtk3 \
                gtk3 \
                cairo-devel \
                gobject-introspection-devel \
                pkg-config \
                gcc \
                meson \
                ninja
            ;;
        *)
            echo "❌ Gerenciador de pacotes não reconhecido!"
            echo ""
            echo "Por favor, instale manualmente:"
            echo "  - Python 3.9+"
            echo "  - GTK3 e desenvolvimento"
            echo "  - WebKit2GTK"
            echo "  - Cairo"
            echo "  - GObject Introspection"
            exit 1
            ;;
    esac
}

# Verifica se já tem as dependências
check_system_deps() {
    echo ""
    echo "🔍 Verificando dependências do sistema..."
    
    MISSING=0
    
    # Verifica Cairo
    if ! pkg-config --exists cairo 2>/dev/null; then
        echo "   ❌ Cairo não encontrado"
        MISSING=1
    else
        echo "   ✅ Cairo encontrado"
    fi
    
    # Verifica GTK
    if ! pkg-config --exists gtk+-3.0 2>/dev/null; then
        echo "   ❌ GTK+3 não encontrado"
        MISSING=1
    else
        echo "   ✅ GTK+3 encontrado"
    fi
    
    # Verifica WebKit (versões diferentes em cada distro)
    if pkg-config --exists webkit2gtk-4.1 2>/dev/null; then
        echo "   ✅ WebKit2GTK-4.1 encontrado"
    elif pkg-config --exists webkit2gtk-4.0 2>/dev/null; then
        echo "   ✅ WebKit2GTK-4.0 encontrado"
    else
        echo "   ❌ WebKit2GTK não encontrado"
        MISSING=1
    fi
    
    # Verifica GObject Introspection
    if ! pkg-config --exists gobject-introspection-1.0 2>/dev/null; then
        echo "   ❌ GObject Introspection não encontrado"
        MISSING=1
    else
        echo "   ✅ GObject Introspection encontrado"
    fi
    
    if [ $MISSING -eq 1 ]; then
        echo ""
        echo "⚠️  Dependências faltando. Instalando..."
        install_system_deps
        
        # Após instalar, verifica novamente
        echo ""
        echo "🔍 Verificando novamente..."
        if pkg-config --exists cairo && pkg-config --exists gtk+-3.0; then
            echo "   ✅ Todas as dependências instaladas com sucesso!"
        else
            echo "   ⚠️  Algumas dependências ainda podem estar faltando."
            echo "   Tentando continuar mesmo assim..."
        fi
    else
        echo "   ✅ Todas as dependências estão ok!"
    fi
}

# Executa verificação de dependências do sistema
check_system_deps

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado!"
    exit 1
fi
echo ""
echo "✅ Python3 encontrado: $(python3 --version)"

# Cria ambiente virtual
echo ""
echo "🐍 Criando ambiente virtual..."
if [ -d "venv" ]; then
    echo "   Removendo ambiente virtual antigo..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

# Atualiza pip
pip install --upgrade pip

# Instala dependências Python do requirements.txt
echo ""
echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

# Instala PyGObject (agora com as dependências do sistema já instaladas)
echo ""
echo "📦 Instalando PyGObject (binding GTK para Python)..."
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
