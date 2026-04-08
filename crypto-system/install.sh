cat > install.sh << 'EOF'
#!/bin/bash
# ============================================
# Educational Crypto System - Installer
# ============================================

set -e  # Para o script se algum comando falhar

echo "╔════════════════════════════════════════════════╗"
echo "║   Educational Crypto System - Installer       ║"
echo "║         Criptografia Homofônica               ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# Verifica se tem Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado!"
    echo ""
    echo "📦 Instale o Docker:"
    echo "   https://docs.docker.com/engine/install/"
    echo ""
    echo "Ou rode sem Docker:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    echo "   cd backend && python main.py"
    echo ""
    exit 1
fi

# Verifica Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose não encontrado!"
    echo "   Instale: https://docs.docker.com/compose/install/"
    exit 1
fi

# Cria .env se não existir
if [ ! -f .env ]; then
    echo "📝 Criando .env com configurações padrão..."
    cp .env.example .env
    
    # Gera chave secreta aleatória
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || echo "fallback-key-change-me")
    sed -i "s/your-secret-key-here-change-this-in-production/$SECRET_KEY/" .env
    echo "✅ .env criado"
fi

# Cria diretório do banco
mkdir -p database

echo ""
echo "🚀 Iniciando containers..."
echo ""

# Sobe os containers
docker-compose up -d --build

echo ""
echo "✅ Sistema rodando!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 Acesse:"
echo "   API: http://localhost:8000"
echo "   Documentação: http://localhost:8000/docs"
echo "   Health: http://localhost:8000/health"
echo ""
echo "📋 Comandos úteis:"
echo "   docker-compose logs -f    # Ver logs"
echo "   docker-compose down       # Parar"
echo "   docker-compose restart    # Reiniciar"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  Lembre-se: Este é um sistema EDUCACIONAL"
echo "   Não usar para dados reais!"
echo ""
EOF

# Dá permissão de execução
chmod +x install.sh
