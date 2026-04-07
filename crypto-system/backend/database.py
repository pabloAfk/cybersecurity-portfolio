from sqlmodel import SQLModel, Field, Session, create_engine, Relationship, select
from typing import Optional, List
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração do banco
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://crypto_user:crypto_pass_2024@localhost:5432/crypto_db")

engine = create_engine(DATABASE_URL, echo=True)

# ========== MODELS ==========
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relacionamento com vault
    vault_items: List["Vault"] = Relationship(back_populates="user")

class Vault(SQLModel, table=True):
    __tablename__ = "vault"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    encrypted_message: str
    key1: int
    key2: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relacionamento com user
    user: User = Relationship(back_populates="vault_items")

def init_db():
    """Cria as tabelas no banco"""
    SQLModel.metadata.create_all(engine)
    print("✅ Database initialized!")

def get_session():
    """Retorna uma sessão do banco"""
    with Session(engine) as session:
        yield session

# ========== CRUD OPERATIONS ==========
def create_user(session: Session, username: str, password_hash: str) -> User:
    user = User(username=username, password_hash=password_hash)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()

def save_to_vault(session: Session, user_id: int, encrypted_message: str, key1: int, key2: int) -> Vault:
    vault_item = Vault(
        user_id=user_id,
        encrypted_message=encrypted_message,
        key1=key1,
        key2=key2
    )
    session.add(vault_item)
    session.commit()
    session.refresh(vault_item)
    return vault_item

def get_user_vault(session: Session, user_id: int) -> List[Vault]:
    statement = select(Vault).where(Vault.user_id == user_id).order_by(Vault.created_at.desc())
    return session.exec(statement).all()

def delete_from_vault(session: Session, message_id: int, user_id: int) -> bool:
    statement = select(Vault).where(Vault.id == message_id, Vault.user_id == user_id)
    vault_item = session.exec(statement).first()
    
    if vault_item:
        session.delete(vault_item)
        session.commit()
        return True
    return False
