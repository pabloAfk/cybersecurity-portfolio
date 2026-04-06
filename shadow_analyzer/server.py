"""
ShadowAnalyzer — servidor web Flask
"""

import os
import json
import tempfile
from dataclasses import asdict
from flask import Flask, request, jsonify, send_from_directory

from analyzer import analyze_file

app = Flask(__name__, static_folder="static")

UPLOAD_FOLDER = tempfile.mkdtemp(prefix="shadowanalyzer_")
MAX_FILE_MB = 64
MAX_FILE_BYTES = MAX_FILE_MB * 1024 * 1024


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "Nome de arquivo vazio."}), 400

    # lê o arquivo em memória para verificar tamanho
    data = f.read()
    if len(data) > MAX_FILE_BYTES:
        return jsonify({"error": f"Arquivo muito grande. Máximo: {MAX_FILE_MB} MB."}), 413

    # salva temporariamente para análise
    tmp_path = os.path.join(UPLOAD_FOLDER, f.filename)
    with open(tmp_path, "wb") as tmp:
        tmp.write(data)

    try:
        result = analyze_file(tmp_path, f.filename)
        return jsonify(asdict(result))
    except Exception as e:
        return jsonify({"error": f"Falha na análise: {str(e)}"}), 500
    finally:
        # limpa o arquivo temporário após análise
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    print("=" * 55)
    print("  🛡️  ShadowAnalyzer v1.0 — Static Malware Engine")
    print("=" * 55)
    print(f"  Servidor:   http://127.0.0.1:5000")
    print(f"  Limite:     {MAX_FILE_MB} MB por arquivo")
    print(f"  Temp dir:   {UPLOAD_FOLDER}")
    print("=" * 55)
    app.run(debug=False, host="127.0.0.1", port=5000)
