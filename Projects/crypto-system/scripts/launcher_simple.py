#!/usr/bin/env python3
"""
CryptoSystem - Launcher Simples (fallback)
Abre no navegador padrão
"""

import subprocess
import sys
import os
import webbrowser
import time
import socket

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def start_backend():
    backend_dir = os.path.join(PROJECT_ROOT, "src", "backend")
    venv_python = os.path.join(PROJECT_ROOT, "venv", "bin", "python")
    
    if not os.path.exists(venv_python):
        print("❌ Sistema não instalado. Rode: ./start.sh")
        return None
    
    return subprocess.Popen(
        [venv_python, "main.py"],
        cwd=backend_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def main():
    print("🚀 Iniciando CryptoSystem...")
    
    # Verifica se backend já está rodando
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8000))
    sock.close()
    
    if result != 0:
        process = start_backend()
        if not process:
            return
        time.sleep(3)
    else:
        process = None
    
    print("🌐 Abrindo navegador...")
    webbrowser.open("http://127.0.0.1:8000")
    
    print("✅ Sistema rodando!")
    print("   Pressione Ctrl+C para encerrar...")
    
    try:
        if process:
            process.wait()
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        if process:
            process.terminate()
        print("\n👋 Sistema encerrado.")

if __name__ == "__main__":
    main()
