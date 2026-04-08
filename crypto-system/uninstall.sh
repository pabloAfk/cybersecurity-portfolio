#!/bin/bash
# ============================================
# Educational Crypto System - Uninstaller
# ============================================

echo "🗑️  Parando containers..."
docker-compose down -v

echo "🧹 Limpando arquivos..."
rm -rf database/
rm -f .env

echo "✅ Sistema removido!"
