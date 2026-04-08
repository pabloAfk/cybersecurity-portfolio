#!/usr/bin/env python3
"""
CryptoSystem - Launcher GTK
Abre o backend e frontend em um único aplicativo nativo
Coloque este arquivo na RAIZ do projeto crypto-system/
"""

import subprocess
import sys
import os
import signal
import time
import atexit

# Tenta importar GTK com detecção automática da versão do WebKit
try:
    import gi
    gi.require_version('Gtk', '3.0')
    
    # Tenta diferentes versões do WebKit (Fedora usa 4.1, Ubuntu 4.0)
    webkit_versions = ['4.1', '4.0']
    webkit_version = None
    
    for version in webkit_versions:
        try:
            gi.require_version('WebKit2', version)
            webkit_version = version
            break
        except ValueError:
            continue
    
    if not webkit_version:
        raise ValueError("WebKit2 não encontrado (tentado 4.1 e 4.0)")
    
    from gi.repository import Gtk, GLib, WebKit2
    print(f"✅ Usando WebKit2 versão {webkit_version}")
    
except ImportError as e:
    print("❌ Dependências GTK não encontradas!")
    print()
    print("Para instalar no Ubuntu/Debian:")
    print("  sudo apt install python3-gi gir1.2-webkit2-4.0")
    print()
    print("Para instalar no Fedora/Nobara:")
    print("  sudo dnf install python3-gobject webkit2gtk4.1")
    print()
    print("Depois rode: pip install PyGObject")
    sys.exit(1)

class CryptoApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="CryptoSystem - Cofre Homofônico")
        self.set_default_size(1280, 800)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(0)
        
        # Processos
        self.backend_process = None
        self.backend_ready = False
        
        # Configurar ícone (opcional - tenta vários nomes)
        for icon in ["security-high", "dialog-password", "application-x-executable"]:
            try:
                self.set_icon_name(icon)
                break
            except:
                pass
        
        # Criar WebView
        self.webview = WebKit2.WebView()
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scroll.add(self.webview)
        
        # Barra de status
        self.statusbar = Gtk.Statusbar()
        self.status_context = self.statusbar.get_context_id("status")
        self.statusbar.push(self.status_context, "🔴 Iniciando serviços...")
        
        # Barra de progresso
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("Carregando...")
        
        # Layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.pack_start(self.scroll, True, True, 0)
        
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        status_box.pack_start(self.statusbar, True, True, 0)
        status_box.pack_start(self.progress_bar, False, False, 0)
        vbox.pack_start(status_box, False, False, 0)
        
        self.add(vbox)
        
        # Conectar eventos
        self.connect("destroy", self.on_destroy)
        self.webview.connect("load-changed", self.on_load_changed)
        
        # Iniciar serviços
        GLib.timeout_add_seconds(1, self.start_services)
        
        self.show_all()
        self.progress_bar.hide()
    
    def on_load_changed(self, webview, load_event):
        """Atualiza barra de progresso durante carregamento"""
        if load_event == WebKit2.LoadEvent.STARTED:
            self.progress_bar.show()
            self.progress_bar.set_fraction(0.3)
            self.progress_bar.set_text("Conectando ao servidor...")
        elif load_event == WebKit2.LoadEvent.COMMITTED:
            self.progress_bar.set_fraction(0.6)
            self.progress_bar.set_text("Carregando interface...")
        elif load_event == WebKit2.LoadEvent.FINISHED:
            self.progress_bar.set_fraction(1.0)
            self.progress_bar.set_text("Pronto!")
            GLib.timeout_add(500, lambda: self.progress_bar.hide())
    
    def start_services(self):
        """Inicia backend e frontend"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.join(base_dir, "backend")
        
        # Verifica se backend existe
        if not os.path.exists(os.path.join(backend_dir, "main.py")):
            self.statusbar.push(self.status_context, "❌ Erro: backend/main.py não encontrado!")
            return False
        
        # Verifica se o backend já está rodando
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        
        if result == 0:
            # Backend já está rodando
            self.statusbar.push(self.status_context, "🟢 Conectado ao backend existente")
            self.webview.load_uri("http://127.0.0.1:8000")
            return False
        
        # Inicia backend com uvicorn
        self.statusbar.push(self.status_context, "🟡 Iniciando backend...")
        
        # Detecta Python correto
        python_cmd = sys.executable
        
        self.backend_process = subprocess.Popen(
            [python_cmd, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if hasattr(os, 'setsid') else None,
            text=True
        )
        
        # Aguarda backend ficar pronto
        GLib.timeout_add_seconds(1, self.check_backend_ready, 0)
        
        return False  # Para não repetir
    
    def check_backend_ready(self, attempts):
        """Verifica se backend está pronto para receber conexões"""
        import socket
        
        if attempts > 30:  # 30 segundos timeout
            self.statusbar.push(self.status_context, "❌ Falha ao iniciar backend!")
            return False
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        
        if result == 0:
            self.statusbar.push(self.status_context, "🟢 Backend pronto! Carregando interface...")
            self.webview.load_uri("http://127.0.0.1:8000")
            return False
        else:
            self.statusbar.push(self.status_context, f"🟡 Aguardando backend... ({attempts + 1}/30)")
            GLib.timeout_add_seconds(1, self.check_backend_ready, attempts + 1)
            return False
    
    def on_destroy(self, widget):
        """Finaliza processos ao fechar"""
        if self.backend_process:
            try:
                if hasattr(os, 'killpg') and self.backend_process.pid:
                    os.killpg(os.getpgid(self.backend_process.pid), signal.SIGTERM)
                else:
                    self.backend_process.terminate()
            except:
                pass
            GLib.timeout_add(500, self.force_kill)
        
        Gtk.main_quit()
    
    def force_kill(self):
        """Força matar processo se necessário"""
        if self.backend_process and self.backend_process.poll() is None:
            try:
                self.backend_process.kill()
            except:
                pass
        return False

def main():
    app = CryptoApp()
    Gtk.main()

if __name__ == "__main__":
    main()
