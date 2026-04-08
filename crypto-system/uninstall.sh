#!/bin/bash
# ============================================
# CryptoSystem - Desinstalador
# ============================================

echo "🗑️  Removendo CryptoSystem..."

# Mata processos
pkill -f "uvicorn main:app" 2>/dev/null || true

# Remove ambiente virtual
rm -rf venv

# Remove atalho desktop
rm -f "$HOME/.local/share/applications/crypto.desktop"
rm -f crypto.desktop

# Remove banco de dados (opcional)
read -p "Remover também o banco de dados? (s/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    rm -rf database/
    rm -f backend/data.json
    echo "✅ Banco de dados removido."
fi

echo ""
echo "✅ CryptoSystem desinstalado!"
