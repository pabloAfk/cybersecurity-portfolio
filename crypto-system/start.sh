#!/bin/bash
# start.sh - Inicia backend e app em um único comando

cd ~/githubmeu/cybersecurity-portfolio-main/crypto-system

# Ativa venv
source venv/bin/activate

# Inicia backend em background
cd backend
python main.py &
BACKEND_PID=$!

# Aguarda backend iniciar
sleep 3

# Volta e inicia o launcher
cd ..
python launcher_simple.py

# Quando fechar o launcher, mata o backend
kill $BACKEND_PID 2>/dev/null
