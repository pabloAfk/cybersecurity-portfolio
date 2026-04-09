#!/bin/bash
# ============================================
# CryptoSystem - Instalador para Parrot OS
# Versão específica para Parrot (sem WebKit problemático)
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     CryptoSystem - Instalador para Parrot OS                   ║"
echo "║     Criptografia Homofônica + Interface Web                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd "$PROJECT_ROOT"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir com cor
print_msg() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Verifica se está no Parrot
if ! grep -qi "parrot" /etc/os-release 2>/dev/null; then
    print_warning "Este instalador é otimizado para Parrot OS"
    print_info "Detectado: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
    echo ""
    read -p "Continuar mesmo assim? (s/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# 1. Atualizar repositórios
print_info "Atualizando repositórios..."
sudo apt update

# 2. Instalar dependências principais do sistema
print_info "Instalando dependências do sistema..."
sudo apt install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    python3-full \
    build-essential \
    pkg-config \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev

# 3. Instalar dependências GTK (para interface gráfica)
print_info "Instalando GTK e dependências..."
sudo apt install -y \
    libgtk-3-dev \
    gir1.2-gtk-3.0 \
    python3-gi \
    python3-gi-cairo \
    libgirepository1.0-dev \
    gobject-introspection \
    libcairo2-dev \
    libcairo2

# 4. Instalar WebKit (para navegador embutido - opcional)
print_info "Instalando WebKit2GTK (para app nativo)..."
sudo apt install -y \
    libwebkit2gtk-4.1-dev \
    gir1.2-webkit2-4.1 \
    2>/dev/null || {
        print_warning "WebKit2GTK 4.1 não encontrado, tentando 4.0..."
        sudo apt install -y \
            libwebkit2gtk-4.0-dev \
            gir1.2-webkit2-4.0 2>/dev/null || {
            print_warning "WebKit2GTK não instalado (apenas modo navegador)"
        }
    }

# 5. Criar ambiente virtual
print_info "Criando ambiente virtual Python..."
cd "$PROJECT_ROOT"
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# 6. Instalar dependências Python
print_info "Instalando dependências Python..."
pip install --upgrade pip

# Instalar pacotes principais
pip install fastapi uvicorn[standard] sqlmodel bcrypt python-jose[cryptography] passlib[bcrypt] python-multipart python-dotenv

# Instalar PyGObject (com bindings GTK)
print_info "Instalando PyGObject (GTK bindings)..."
pip install PyGObject 2>/dev/null || {
    print_warning "PyGObject não instalado via pip, usando versão do sistema"
    sudo apt install -y python3-gi python3-gi-cairo
}

# 7. Criar diretórios necessários
print_info "Criando diretórios do projeto..."
mkdir -p src/backend
mkdir -p src/frontend/js

# 8. Criar arquivo de configuração do Parrot
print_info "Configurando ambiente Parrot..."

cat > "$PROJECT_ROOT/.parrot_env" << 'ENV_EOF'
# CryptoSystem - Ambiente Parrot OS
# Este arquivo indica que o sistema está otimizado para Parrot

PARROT_OPTIMIZED=true
GTK_VERSION=3.0
WEBKIT_VERSION=4.1
ENVIRONMENT=parrot
ENV_EOF

# 9. Criar script de inicialização específico para Parrot
cat > "$PROJECT_ROOT/start-parrot.sh" << 'START_EOF'
#!/bin/bash
# CryptoSystem - Inicialização para Parrot OS

cd "$(dirname "$0")"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔐 CryptoSystem - Modo Parrot OS${NC}"
echo ""

# Verifica se venv existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente não instalado. Execute: ./parrot-install.sh"
    exit 1
fi

# Ativa ambiente virtual
source venv/bin/activate

# Verifica se backend já está rodando
if pgrep -f "python.*main.py" > /dev/null; then
    echo "✅ Backend já está rodando"
else
    echo "🚀 Iniciando backend..."
    cd src/backend
    python main.py &
    BACKEND_PID=$!
    cd ../..
    sleep 3
fi

# Abre navegador
echo "🌐 Abrindo navegador..."
xdg-open http://localhost:8000

echo ""
echo -e "${GREEN}✅ Sistema rodando!${NC}"
echo "   Pressione Ctrl+C para encerrar"
echo ""

# Aguarda
wait $BACKEND_PID 2>/dev/null
START_EOF

chmod +x "$PROJECT_ROOT/start-parrot.sh"

# 10. Criar atalho no menu
print_info "Criando atalho no menu de aplicações..."

mkdir -p ~/.local/share/applications

cat > ~/.local/share/applications/cryptosystem-parrot.desktop << DESKTOP_EOF
[Desktop Entry]
Name=CryptoSystem (Parrot)
Comment=Sistema de Criptografia Homofônica
Exec=$PROJECT_ROOT/start-parrot.sh
Icon=security-high
Terminal=true
Type=Application
Categories=Utility;Security;
StartupNotify=true
Keywords=crypto;encryption;security;
DESKTOP_EOF

# 11. Testar instalação
print_info "Testando instalação..."

# Testar GTK
python3 -c "from gi.repository import Gtk; print('✅ GTK disponível')" 2>/dev/null || {
    print_warning "GTK não disponível (apenas modo navegador)"
}

# Testar WebKit
python3 -c "from gi.repository import WebKit2; print('✅ WebKit2 disponível')" 2>/dev/null || {
    print_info "WebKit2 não disponível (apenas modo navegador)"
}

# Testar FastAPI
python3 -c "import fastapi; print('✅ FastAPI OK')" 2>/dev/null || {
    print_error "FastAPI não instalado corretamente"
    exit 1
}

# 12. Criar arquivo de teste do vault
if [ ! -f "src/backend/vault.json" ]; then
    echo '{"messages": [], "next_id": 1}' > src/backend/vault.json
    print_info "Arquivo vault.json criado"
fi

# 13. Resumo final
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ INSTALAÇÃO CONCLUÍDA!                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📦 Pacotes instalados:"
echo "   • Python 3 + venv"
echo "   • GTK 3.0 + bindings Python"
echo "   • WebKit2GTK (opcional)"
echo "   • FastAPI + dependências"
echo ""
echo "🚀 Para iniciar o CryptoSystem:"
echo ""
echo "   1. Modo navegador (recomendado):"
echo "      ./start-parrot.sh"
echo ""
echo "   2. Modo manual:"
echo "      cd src/backend && python main.py"
echo "      Abra: http://localhost:8000"
echo ""
echo "   3. Pelo menu de aplicações:"
echo "      Procure por 'CryptoSystem (Parrot)'"
echo ""
echo "📁 Local do cofre (vault.json):"
echo "   src/backend/vault.json"
echo ""
echo "⚠️  Lembre-se: Este sistema é EDUCACIONAL"
echo "   Não usar para proteger dados reais!"
echo ""

# Pergunta se quer iniciar agora
read -p "Deseja iniciar o CryptoSystem agora? (s/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    ./start-parrot.sh
fi
