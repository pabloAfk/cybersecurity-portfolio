#!/bin/bash
# ============================================
# CryptoSystem - Ponto de Entrada Único
# Detecta se está instalado e inicia
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔐 CryptoSystem - Criptografia Homofônica"
echo ""

# Verifica se já está instalado
if [ ! -d "$SCRIPT_DIR/venv" ] || [ ! -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    echo "🔧 Sistema não encontrado. Executando instalador..."
    bash "$SCRIPT_DIR/scripts/install.sh"
    echo ""
fi

# Verifica se o instalador foi bem-sucedido
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "❌ Falha na instalação. Execute manualmente: ./scripts/install.sh"
    exit 1
fi

# Ativa o ambiente virtual
source "$SCRIPT_DIR/venv/bin/activate"

# Inicia o launcher (tenta GTK, fallback para navegador)
if command -v python3 &> /dev/null; then
    python3 "$SCRIPT_DIR/scripts/launcher.py" 2>/dev/null || python3 "$SCRIPT_DIR/scripts/launcher_simple.py"
else
    echo "❌ Python3 não encontrado!"
    exit 1
fi
