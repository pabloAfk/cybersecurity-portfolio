from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import sys
import os

# Adiciona o diretório backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cipher_engine import encrypt, decrypt
from database import init_db, create_user, get_user_by_username, save_to_vault, get_user_vault, delete_from_vault
from auth import hash_password, verify_password, create_access_token, decode_token
from models import (
    UserRegister, UserLogin, EncryptRequest, DecryptRequest,
    VaultAddRequest, VaultDeleteRequest, Token
)

app = FastAPI(
    title="Educational Crypto System API",
    description="Sistema de Criptografia Homofônica - Educacional",
    version="1.0.0"
)

# CORS para o frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique o domínio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Inicializa o banco de dados na startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("🚀 API started!")

# ========== UTILS ==========
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obtém o usuário atual a partir do token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload["sub"]
    user = get_user_by_username(username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user

# ========== ENDPOINTS PÚBLICOS ==========
@app.post("/register", response_model=Token)
async def register(user_data: UserRegister):
    """Registra um novo usuário"""
    # Verifica se usuário já existe
    existing_user = get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Cria o usuário
    password_hash = hash_password(user_data.password)
    create_user(user_data.username, password_hash)
    
    # Cria token
    access_token = create_access_token(data={"sub": user_data.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user_data.username
    }

@app.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login do usuário"""
    user = get_user_by_username(user_data.username)
    
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    access_token = create_access_token(data={"sub": user["username"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user["username"]
    }

# ========== ENDPOINTS PROTEGIDOS ==========
@app.post("/encrypt")
async def encrypt_message(request: EncryptRequest, current_user = Depends(get_current_user)):
    """Criptografa uma mensagem"""
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
    """Descriptografa uma mensagem"""
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
    """Lista todas as mensagens do cofre do usuário"""
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
    """Salva uma mensagem criptografada no cofre"""
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

@app.delete("/vault/delete")
async def delete_from_vault_endpoint(request: VaultDeleteRequest, current_user = Depends(get_current_user)):
    """Remove uma mensagem do cofre"""
    deleted = delete_from_vault(request.message_id, current_user["id"])
    
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
    """Verifica se a API está funcionando"""
    return {"status": "healthy", "system": "Educational Crypto System"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
