from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
import json
from datetime import datetime, timezone

from cipher_engine import encrypt, decrypt

# Caminho para o frontend e arquivo de dados
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
DATA_FILE = os.path.join(os.path.dirname(__file__), "vault.json")

# ========== VAULT SIMPLES (sem usuário) ==========
def load_vault():
    """Carrega mensagens do arquivo JSON"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"messages": [], "next_id": 1}

def save_vault(data):
    """Salva mensagens no arquivo JSON"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 CryptoSystem iniciado!")
    print(f"📁 Frontend: {FRONTEND_DIR}")
    yield
    print("👋 Sistema encerrado")

app = FastAPI(
    title="CryptoSystem",
    description="Sistema de Criptografia Homofônica",
    version="3.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# ========== ROTAS DO FRONTEND ==========
@app.get("/")
@app.get("/dashboard")
async def serve_dashboard():
    """Serve o dashboard"""
    dashboard_path = os.path.join(FRONTEND_DIR, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"error": "dashboard.html not found"}

@app.get("/styles.css")
async def serve_css():
    css_path = os.path.join(FRONTEND_DIR, "styles.css")
    if os.path.exists(css_path):
        return FileResponse(css_path, media_type="text/css")
    return {"error": "styles.css not found"}

@app.get("/js/{filename}")
async def serve_js(filename: str):
    js_path = os.path.join(FRONTEND_DIR, "js", filename)
    if os.path.exists(js_path):
        return FileResponse(js_path, media_type="application/javascript")
    return {"error": f"{filename} not found"}

# ========== ENDPOINTS DA API ==========
@app.post("/encrypt")
async def encrypt_message(request: dict):
    text = request.get("text", "")
    key1 = request.get("key1", 0)
    key2 = request.get("key2", 0)
    
    if not text:
        raise HTTPException(status_code=400, detail="Texto vazio")
    if not (0 <= key1 <= 999) or not (0 <= key2 <= 999):
        raise HTTPException(status_code=400, detail="Chaves devem ser entre 0 e 999")
    
    try:
        result = encrypt(text, key1, key2)
        return {"success": True, "ciphertext": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/decrypt")
async def decrypt_message(request: dict):
    ciphertext = request.get("ciphertext", "")
    key1 = request.get("key1", 0)
    key2 = request.get("key2", 0)
    
    if not ciphertext:
        raise HTTPException(status_code=400, detail="Cifra vazia")
    if not ciphertext.startswith("S:"):
        raise HTTPException(status_code=400, detail="Cifra deve começar com 'S:'")
    if not (0 <= key1 <= 999) or not (0 <= key2 <= 999):
        raise HTTPException(status_code=400, detail="Chaves devem ser entre 0 e 999")
    
    try:
        result = decrypt(ciphertext, key1, key2)
        return {"success": True, "plaintext": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vault")
async def get_vault():
    """Lista mensagens salvas"""
    data = load_vault()
    return {"messages": data["messages"]}

@app.post("/vault")
async def add_to_vault(request: dict):
    """Salva uma mensagem"""
    data = load_vault()
    
    message = {
        "id": data["next_id"],
        "encrypted_message": request.get("encrypted_message", ""),
        "key1": request.get("key1", 0),
        "key2": request.get("key2", 0),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    data["messages"].append(message)
    data["next_id"] += 1
    save_vault(data)
    
    return {"success": True, "id": message["id"]}

@app.delete("/vault/{message_id}")
async def delete_from_vault(message_id: int):
    """Remove uma mensagem"""
    data = load_vault()
    
    for i, msg in enumerate(data["messages"]):
        if msg["id"] == message_id:
            data["messages"].pop(i)
            save_vault(data)
            return {"success": True}
    
    raise HTTPException(status_code=404, detail="Mensagem não encontrada")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "system": "CryptoSystem v3"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
