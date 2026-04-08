#!/bin/bash
# ============================================
# CryptoSystem - Desinstalador
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "🗑️  Removendo CryptoSystem..."

# Remove ambiente virtual
rm -rf venv

# Remove dados do cofre (opcional)
read -p "Remover dados do cofre? (s/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    rm -f src/backend/vault.json
    echo "✅ Dados removidos."
fi

echo "✅ CryptoSystem desinstalado!"
