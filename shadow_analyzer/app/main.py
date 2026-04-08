"""
ShadowAnalyzer — Ponto de entrada do app desktop (PyWebView + Flask)
Abre uma janela nativa com a interface embutida, sem precisar de navegador.
"""

import sys
import os
import threading
import socket
import time
import signal

# ── ajuste de paths para o bundle PyInstaller ─────────────────────────────
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
    APP_DIR  = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR  = BASE_DIR

sys.path.insert(0, BASE_DIR)

import webview
from server import app as flask_app


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start_flask(port: int):
    flask_app.run(
        host="127.0.0.1",
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True,
    )


def wait_for_flask(port: int, timeout: float = 10.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def main():
    port = find_free_port()

    flask_thread = threading.Thread(target=start_flask, args=(port,), daemon=True)
    flask_thread.start()

    if not wait_for_flask(port):
        print("ERRO: servidor interno não iniciou.", file=sys.stderr)
        sys.exit(1)

    window = webview.create_window(
        title="ShadowAnalyzer v2.0",
        url=f"http://127.0.0.1:{port}",
        width=1260,
        height=800,
        min_size=(900, 620),
        resizable=True,
        text_select=False,
        background_color="#050a12",
    )

    def on_closed():
        os.kill(os.getpid(), signal.SIGTERM)

    window.events.closed += on_closed
    webview.start(debug=False, private_mode=False)


if __name__ == "__main__":
    main()
