#!/usr/bin/env python3
"""
CryptoSystem - Launcher GTK
"""

import subprocess
import sys
import os
import signal
import time
import socket

# Adiciona src ao path para importar módulos
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

try:
    import gi
    gi.require_version('Gtk', '3.0')
    
    for version in ['4.1', '4.0']:
        try:
            gi.require_version('WebKit2', version)
            break
        except ValueError:
            continue
    
    from gi.repository import Gtk, GLib, WebKit2
    
except ImportError as e:
    print("❌ Dependências GTK não encontradas!")
    print("   Rode: ./scripts/install.sh")
    sys.exit(1)

class CryptoApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="CryptoSystem")
        self.set_default_size(1280, 800)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        self.backend_process = None
        
        # WebView
        self.webview = WebKit2.WebView()
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.add(self.webview)
        
        # Barra de status
        self.statusbar = Gtk.Statusbar()
        self.status_context = self.statusbar.get_context_id("status")
        
        # Layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.pack_start(self.scroll, True, True, 0)
        vbox.pack_start(self.statusbar, False, False, 0)
        self.add(vbox)
        
        self.connect("destroy", self.on_destroy)
        
        self.start_backend()
        self.show_all()
    
    def start_backend(self):
        """Inicia o backend"""
        backend_dir = os.path.join(PROJECT_ROOT, "src", "backend")
        venv_python = os.path.join(PROJECT_ROOT, "venv", "bin", "python")
        
        # Verifica se já está rodando
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        
        if result == 0:
            self.statusbar.push(self.status_context, "🟢 Conectado ao backend")
            self.webview.load_uri("http://127.0.0.1:8000")
            return
        
        if not os.path.exists(venv_python):
            self.statusbar.push(self.status_context, "❌ Sistema não instalado. Rode: ./start.sh")
            return
        
        try:
            self.backend_process = subprocess.Popen(
                [venv_python, "main.py"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            GLib.timeout_add_seconds(1, self.check_backend, 0)
            
        except Exception as e:
            self.statusbar.push(self.status_context, f"❌ Erro: {str(e)[:50]}")
    
    def check_backend(self, attempts):
        if attempts > 15:
            self.statusbar.push(self.status_context, "❌ Falha ao iniciar backend")
            return False
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        
        if result == 0:
            self.statusbar.push(self.status_context, "🟢 Backend pronto!")
            self.webview.load_uri("http://127.0.0.1:8000")
            return False
        else:
            self.statusbar.push(self.status_context, f"🟡 Aguardando... ({attempts+1}/15)")
            GLib.timeout_add_seconds(1, self.check_backend, attempts + 1)
            return False
    
    def on_destroy(self, widget):
        if self.backend_process:
            self.backend_process.terminate()
            time.sleep(0.5)
            if self.backend_process.poll() is None:
                self.backend_process.kill()
        Gtk.main_quit()

def main():
    app = CryptoApp()
    Gtk.main()

if __name__ == "__main__":
    main()
