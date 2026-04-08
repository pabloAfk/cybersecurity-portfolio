# 🔐 Educational Crypto System

Sistema educacional de criptografia homofônica para demonstração de conceitos de segurança cibernética.

## ⚠️ Aviso Importante

> **Este sistema é puramente EDUCACIONAL** e não deve ser usado para proteger dados reais. A criptografia implementada é frágil e vulnerável a ataques.

## 🎯 Objetivo

Demonstrar conhecimentos em:
- Criptografia (algoritmo homofônico)
- Desenvolvimento Backend (FastAPI)
- Banco de Dados (SQLModel)
- Autenticação Segura (JWT em HttpOnly cookies)
- Docker e Containerização
- Boas práticas de segurança

## 🚀 Como Executar

### Opção 1: Docker (Recomendado)

```bash
# 1. Extraia o pacote
tar -xzf crypto-system.tar.gz
cd crypto-system

# 2. Execute o instalador
./install.sh

# 3. Acesse http://localhost:8000
```
### Opção 3: Sem Docker
```bash
# 1. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Instale dependências
pip install -r requirements.txt

# 3. Rode o backend
cd backend
python main.py
```
🔐 Como funciona a criptografia
Homofônica: Cada caractere vira 5 caracteres aleatórios

Duas chaves: key1 (mapa) + key2 (rotação)

Salt: Prefixo S: para identificar cifras

⚠️ Limitações de Segurança
Não é seguro para produção - apenas educacional

Vulnerável a análise de frequência

Chaves curtas (0-999) - brute force possível

Sem autenticação da mensagem

🛠️ Tecnologias
FastAPI + Uvicorn

SQLModel + SQLite

JWT + Bcrypt

Docker

HTML/CSS/JavaScript
