"""
ShadowAnalyzer v2.0 — servidor web Flask
Endpoints:
  GET  /                   → interface web
  POST /analyze            → análise estática
  POST /sandbox            → análise dinâmica (Docker)
  GET  /sandbox/stream/<id>→ Server-Sent Events com progresso em tempo real
  GET  /docker/check       → verifica Docker + imagem
  POST /docker/build       → constrói imagem sandbox
"""

import os
import json
import queue
import tempfile
import threading
from dataclasses import asdict
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context

from analyzer import analyze_file
from sandbox import (
    run_sandbox, check_docker_available, check_image_exists, build_sandbox_image
)

app = Flask(__name__, static_folder="static")

UPLOAD_FOLDER  = tempfile.mkdtemp(prefix="shadowanalyzer_")
MAX_FILE_BYTES = 64 * 1024 * 1024   # 64 MB

# fila de progresso por análise (session_id → queue)
_progress_queues: dict = {}
_progress_lock = threading.Lock()


def get_progress_queue(sid: str) -> queue.Queue:
    with _progress_lock:
        if sid not in _progress_queues:
            _progress_queues[sid] = queue.Queue()
        return _progress_queues[sid]


def cleanup_queue(sid: str):
    with _progress_lock:
        _progress_queues.pop(sid, None)


# ─────────────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ─────────────────────────────────────────────────────────────────────────────
#  Análise estática
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Nome de arquivo vazio."}), 400

    data = f.read()
    if len(data) > MAX_FILE_BYTES:
        return jsonify({"error": "Arquivo muito grande (máx 64 MB)."}), 413

    tmp_path = os.path.join(UPLOAD_FOLDER, f.filename)
    with open(tmp_path, "wb") as tmp:
        tmp.write(data)
    try:
        result = analyze_file(tmp_path, f.filename)
        return jsonify(asdict(result))
    except Exception as e:
        return jsonify({"error": f"Falha na análise estática: {e}"}), 500
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ─────────────────────────────────────────────────────────────────────────────
#  Análise dinâmica (sandbox Docker)
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/sandbox", methods=["POST"])
def sandbox_analyze():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Nome de arquivo vazio."}), 400

    session_id = request.form.get("session_id", "default")
    timeout    = int(request.form.get("timeout", 60))
    timeout    = max(10, min(timeout, 180))

    data = f.read()
    if len(data) > MAX_FILE_BYTES:
        return jsonify({"error": "Arquivo muito grande (máx 64 MB)."}), 413

    tmp_path = os.path.join(UPLOAD_FOLDER, f.filename)
    with open(tmp_path, "wb") as tmp:
        tmp.write(data)

    q = get_progress_queue(session_id)

    def progress(msg):
        q.put({"type": "progress", "message": msg})

    def run():
        try:
            result = run_sandbox(
                file_path=tmp_path,
                file_name=f.filename,
                timeout_seconds=timeout,
                progress_callback=progress,
            )
            q.put({"type": "result", "data": asdict(result)})
        except Exception as e:
            q.put({"type": "result", "data": {"success": False, "error": str(e)}})
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"status": "started", "session_id": session_id})


@app.route("/sandbox/stream/<session_id>")
def sandbox_stream(session_id):
    """Server-Sent Events: envia progresso e resultado para o frontend."""
    q = get_progress_queue(session_id)

    def generate():
        while True:
            try:
                msg = q.get(timeout=120)
            except queue.Empty:
                yield 'data: {"type":"timeout"}\n\n'
                break
            yield f"data: {json.dumps(msg)}\n\n"
            if msg.get("type") in ("result", "timeout", "error"):
                break
        cleanup_queue(session_id)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Docker helpers
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/docker/check")
def docker_check():
    ok, msg = check_docker_available()
    image_ok = check_image_exists() if ok else False
    return jsonify({
        "docker_available": ok,
        "docker_message": msg,
        "image_ready": image_ok,
        "image_name": "shadowanalyzer-sandbox:latest",
    })


@app.route("/docker/build", methods=["POST"])
def docker_build():
    ok, msg = build_sandbox_image()
    return jsonify({"success": ok, "message": msg})


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    print("=" * 60)
    print("  🛡️  ShadowAnalyzer v2.0 — Static + Dynamic Engine")
    print("=" * 60)
    print("  URL:      http://127.0.0.1:5000")
    print("  Static:   entropia · strings · PE/ELF · hashes")
    print("  Sandbox:  Docker isolado · strace · tcpdump · inotify")
    print("=" * 60)
    app.run(debug=False, host="127.0.0.1", port=5000, threaded=True)
