import json
import os
from datetime import datetime, timezone
from typing import List, Optional, Dict

# Arquivo para armazenar os dados
DATA_FILE = "data.json"

def load_data() -> Dict:
    """Carrega dados do arquivo JSON"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"users": [], "vault": [], "next_user_id": 1, "next_vault_id": 1}

def save_data(data: Dict):
    """Salva dados no arquivo JSON"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

# ========== USER FUNCTIONS ==========
def create_user(username: str, password_hash: str) -> Optional[Dict]:
    data = load_data()
    
    # Verifica se usuário existe
    for user in data["users"]:
        if user["username"] == username:
            return None
    
    user = {
        "id": data["next_user_id"],
        "username": username,
        "password_hash": password_hash,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    data["users"].append(user)
    data["next_user_id"] += 1
    save_data(data)
    return user

def get_user_by_username(username: str) -> Optional[Dict]:
    data = load_data()
    for user in data["users"]:
        if user["username"] == username:
            return user
    return None

def get_user_by_id(user_id: int) -> Optional[Dict]:
    data = load_data()
    for user in data["users"]:
        if user["id"] == user_id:
            return user
    return None

# ========== VAULT FUNCTIONS ==========
def save_to_vault(user_id: int, encrypted_message: str, key1: int, key2: int) -> int:
    data = load_data()
    
    vault_item = {
        "id": data["next_vault_id"],
        "user_id": user_id,
        "encrypted_message": encrypted_message,
        "key1": key1,
        "key2": key2,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    data["vault"].append(vault_item)
    data["next_vault_id"] += 1
    save_data(data)
    return vault_item["id"]

def get_user_vault(user_id: int) -> List[Dict]:
    data = load_data()
    user_vault = [item for item in data["vault"] if item["user_id"] == user_id]
    # Ordena por data decrescente
    user_vault.sort(key=lambda x: x["created_at"], reverse=True)
    return user_vault

def delete_from_vault(message_id: int, user_id: int) -> bool:
    data = load_data()
    for i, item in enumerate(data["vault"]):
        if item["id"] == message_id and item["user_id"] == user_id:
            data["vault"].pop(i)
            save_data(data)
            return True
    return False

def init_db():
    """Inicializa o arquivo de dados"""
    if not os.path.exists(DATA_FILE):
        save_data({"users": [], "vault": [], "next_user_id": 1, "next_vault_id": 1})
    print("✅ Database initialized! (JSON file mode)")

def get_session():
    """Mock session para compatibilidade (não usado)"""
    class MockSession:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    return MockSession()
