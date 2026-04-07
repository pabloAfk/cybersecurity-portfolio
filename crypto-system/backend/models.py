from pydantic import BaseModel
from typing import Optional

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class EncryptRequest(BaseModel):
    text: str
    key1: int
    key2: int

class DecryptRequest(BaseModel):
    ciphertext: str
    key1: int
    key2: int

class VaultAddRequest(BaseModel):
    encrypted_message: str
    key1: int
    key2: int

class VaultDeleteRequest(BaseModel):
    message_id: int

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
