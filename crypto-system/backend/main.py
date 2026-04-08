from fastapi import FastAPI, HTTPException, status, Depends, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional
from contextlib import asynccontextmanager
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cipher_engine import encrypt, decrypt
from database import init_db, create_user, get_user_by_username, save_to_vault, get_user_vault, delete_from_vault
from auth import hash_password, verify_password, create_access_token, decode_token
from models import (
    UserRegister, UserLogin, EncryptRequest, DecryptRequest,
    VaultAddRequest, VaultDeleteRequest
)

# Caminho para o frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("🚀 API started with JSON storage!")
    print(f"📁 Frontend directory: {FRONTEND_DIR}")
    yield
    print("👋 Shutting down...")

app = FastAPI(
    title="Educational Crypto System API",
    description="Sistema de Criptografia Homofônica - Educacional",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos do frontend
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
    print(f"✅ Servindo arquivos estáticos de: {FRONTEND_DIR}")
else:
    print(f"⚠️ Pasta frontend não encontrada: {FRONTEND_DIR}")

# ========== ROTAS DO FRONTEND ==========
@app.get("/")
async def serve_index():
    """Serve a página inicial"""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "index.html not found"}

@app.get("/dashboard")
async def serve_dashboard():
    """Serve o dashboard"""
    dashboard_path = os.path.join(FRONTEND_DIR, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"error": "dashboard.html not found"}

@app.get("/styles.css")
async def serve_css():
    """Serve o CSS"""
    css_path = os.path.join(FRONTEND_DIR, "styles.css")
    if os.path.exists(css_path):
        return FileResponse(css_path, media_type="text/css")
    return {"error": "styles.css not found"}

@app.get("/js/{filename}")
async def serve_js(filename: str):
    """Serve arquivos JavaScript"""
    js_path = os.path.join(FRONTEND_DIR, "js", filename)
    if os.path.exists(js_path):
        return FileResponse(js_path, media_type="application/javascript")
    return {"error": f"{filename} not found"}

# ========== ENDPOINTS DA API ==========
def get_current_user(
    response: Response,
    access_token: Optional[str] = Cookie(None)
):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    payload = decode_token(access_token)
    
    if not payload or "sub" not in payload:
        response.delete_cookie("access_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    username = payload["sub"]
    user = get_user_by_username(username)
    
    if not user:
        response.delete_cookie("access_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@app.post("/register")
async def register(user_data: UserRegister, response: Response):
    existing_user = get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    password_hash = hash_password(user_data.password)
    user = create_user(user_data.username, password_hash)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )
    
    access_token = create_access_token(data={"sub": user["username"]})
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24,
        path="/"
    )
    
    return {
        "success": True,
        "username": user["username"],
        "message": "User registered successfully"
    }

@app.post("/login")
async def login(user_data: UserLogin, response: Response):
    user = get_user_by_username(user_data.username)
    
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    access_token = create_access_token(data={"sub": user["username"]})
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24,
        path="/"
    )
    
    return {
        "success": True,
        "username": user["username"],
        "message": "Login successful"
    }

@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"success": True, "message": "Logged out"}

@app.get("/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "created_at": current_user["created_at"]
    }

@app.post("/encrypt")
async def encrypt_message(request: EncryptRequest, current_user = Depends(get_current_user)):
    try:
        if not (0 <= request.key1 <= 999) or not (0 <= request.key2 <= 999):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Keys must be between 0 and 999"
            )
        
        result = encrypt(request.text, request.key1, request.key2)
        return {
            "success": True,
            "ciphertext": result,
            "key1": request.key1,
            "key2": request.key2
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Encryption error: {str(e)}"
        )

@app.post("/decrypt")
async def decrypt_message(request: DecryptRequest, current_user = Depends(get_current_user)):
    try:
        if not (0 <= request.key1 <= 999) or not (0 <= request.key2 <= 999):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Keys must be between 0 and 999"
            )
        
        result = decrypt(request.ciphertext, request.key1, request.key2)
        return {
            "success": True,
            "plaintext": result,
            "key1": request.key1,
            "key2": request.key2
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decryption error: {str(e)}"
        )

@app.get("/vault")
async def get_vault(current_user = Depends(get_current_user)):
    messages = get_user_vault(current_user["id"])
    
    return {
        "messages": [
            {
                "id": msg["id"],
                "encrypted_message": msg["encrypted_message"],
                "key1": msg["key1"],
                "key2": msg["key2"],
                "created_at": msg["created_at"]
            }
            for msg in messages
        ]
    }

@app.post("/vault/add")
async def add_to_vault(request: VaultAddRequest, current_user = Depends(get_current_user)):
    try:
        message_id = save_to_vault(
            current_user["id"],
            request.encrypted_message,
            request.key1,
            request.key2
        )
        
        return {
            "success": True,
            "message_id": message_id,
            "message": "Message saved to vault"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving to vault: {str(e)}"
        )

@app.delete("/vault/{message_id}")
async def delete_from_vault_endpoint(
    message_id: int,
    current_user = Depends(get_current_user)
):
    deleted = delete_from_vault(message_id, current_user["id"])
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found or not owned by user"
        )
    
    return {
        "success": True,
        "message": "Message deleted from vault"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "system": "Educational Crypto System v2 (JSON storage)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
