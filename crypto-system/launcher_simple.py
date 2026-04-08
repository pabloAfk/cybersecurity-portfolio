#!/usr/bin/env python3
"""
CryptoSystem - Launcher (apenas conecta ao backend existente)
"""

import sys
import socket

try:
    import gi
    gi.require_version('Gtk', '3.0')
    
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
        raise ValueError("WebKit2 não encontrado")
    
    from gi.repository import Gtk, GLib, WebKit2
    print(f"✅ Usando WebKit2 versão {webkit_version}")
    
except ImportError as e:
    print("❌ Dependências GTK não encontradas!")
    sys.exit(1)

class CryptoApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="CryptoSystem - Cofre Homofônico")
        self.set_default_size(1280, 800)
        self.set_position(Gtk.WindowPosition.CENTER)
        
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
        
        # Verifica e conecta ao backend
        self.check_backend()
        
        self.show_all()
    
    def check_backend(self):
        """Verifica se o backend está rodando e conecta"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        
        if result == 0:
            self.statusbar.push(self.status_context, "🟢 Conectado ao backend!")
            self.webview.load_uri("http://127.0.0.1:8000")
        else:
            self.statusbar.push(self.status_context, "🔴 Backend não encontrado! Inicie manualmente: cd backend && python main.py")
    
    def on_destroy(self, widget):
        Gtk.main_quit()

def main():
    app = CryptoApp()
    Gtk.main()

if __name__ == "__main__":
    main()
