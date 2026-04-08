cat > Dockerfile << 'EOF'
FROM python:3.12-slim

WORKDIR /app

# Instala dependências de sistema (necessárias para bcrypt)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código
COPY . .

# Cria diretório para o banco SQLite
RUN mkdir -p /app/database

# Expõe a porta
EXPOSE 8000

# Comando para rodar
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
