# 🔐 CryptoSystem - Criptografia Homofônica
> **Sistema educacional de criptografia homofônica com interface gráfica nativa (GTK) e cofre de mensagens.**

## ⚠️ Aviso Importante

ESTE SISTEMA É PURAMENTE EDUCACIONAL                           
Não utilize para proteger dados reais ou sensíveis!            
A criptografia implementada é frágil e vulnerável a ataques.   



## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Como Funciona a Criptografia](#-como-funciona-a-criptografia)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [O Cofre (Vault)](#-o-cofre-vault)
- [Ferramentas](#-ferramentas)
- [Análise de Segurança](#-análise-de-segurança)
- [Scripts e Componentes](#-scripts-e-componentes)
- [Limitações](#-limitações)
- [Desenvolvimento](#-desenvolvimento)
- [Licença](#-licença)

---

## 🎯 Sobre o Projeto

O **CryptoSystem** é uma aplicação completa de criptografia que demonstra conceitos de:

- **Criptografia homofônica** (substituição com múltiplas representações)
- **Desenvolvimento Full-Stack** (FastAPI + HTML/CSS/JS)
- **Aplicações Desktop** (GTK/WebKit)
- **Persistência de dados** (JSON)
- **Boas práticas de organização de projetos**

### 🎨 Demonstrações de Conhecimento

| Área | Tecnologias/Skills |
|------|-------------------|
| **Backend** | Python, FastAPI, Uvicorn |
| **Frontend** | HTML5, CSS3, JavaScript, Axios |
| **Desktop** | GTK, WebKit2, PyGObject |
| **Criptografia** | Algoritmo homofônico personalizado |
| **Armazenamento** | JSON, SQLModel (SQLite) |
| **DevOps** | Shell Script, Instalador automático |

---

## 🔐 Como Funciona a Criptografia

### O Algoritmo Homofônico

O sistema converte cada caractere em **5 caracteres aleatórios** do pool:
Pool de caracteres: A-Z, a-z, 0-9 (62 caracteres)
Entrada: "Hello"
Saída: "S:aB3xYkL9mPq2R..."
↑
Prefixo identificador


### Processo de Criptografia
1. Caractere 'H' → Mapeado para representação de 5 letras

2. Aplica rotação baseada na posição (key2)

3. Prefixo "S:" adicionado

4. Caracteres especiais são normalizados (á → a, ç → c)


### As Duas Chaves

| Chave | Função | Intervalo |
|-------|--------|-----------|
| **KEY1** | Gera o mapa de substituição | 0 - 999 |
| **KEY2** | Controla a rotação por posição | 0 - 999 |

### Exemplo Prático

```bash
Entrada:  "Olá mundo!"
KEY1:     123
KEY2:     456

Cifra:    "S:8fK9mXpQ2rL7nVtY3w..."
```
### ESTRUTURA DO PROJETO
crypto-system/
│
├── start.sh                    # 🚀 PONTO DE ENTRADA ÚNICO
│
├── scripts/                    # 📜 SCRIPTS DE SUPORTE
│   ├── install.sh              # Instalador automático
│   ├── uninstall.sh            # Remove o sistema
│   ├── launcher.py             # App GTK (interface nativa)
│   └── launcher_simple.py      # Fallback (navegador)
│
├── src/                        # 💻 CÓDIGO FONTE
│   ├── backend/
│   │   ├── main.py             # Servidor FastAPI
│   │   ├── cipher_engine.py    # Motor de criptografia
│   │   ├── database.py         # Gerenciador do vault
│   │   └── vault.json          # Dados do cofre (criado automático)
│   │
│   └── frontend/
│       ├── dashboard.html      # Interface principal
│       ├── styles.css          # Estilos (tema terminal)
│       └── js/
│           └── dashboard.js    # Lógica do frontend
│
├── requirements.txt            # Dependências Python
└── README.md                   # Esta documentação

### O QUE O START.SH FAZ?

se estiver instalado -> inicia o app

se não -> scripts/install.sh - > detecta apt, pacman ou dnf -> instala dependências -> cria venv -> instala python libs -> cria atalho desktop -> inicia o app

### 1️⃣ Criptografar
Digite seu texto no campo superior

Escolha KEY1 e KEY2 (0-999)

Clique CRIPTOGRAFAR

Copie a cifra gerada

Opção: marque "salvar no cofre" para guardar automaticamente

### 2️⃣ Descriptografar
Cole a cifra (começa com S:)

Digite as mesmas chaves usadas na criptografia

Clique DESCRIPTOGRAFAR

Texto original é revelado

### 3️⃣ Cofre (Vault)
Salvar: Automático com checkbox ou manual via API

Listar: Todos os itens salvos

Usar: Clique "🔓 Usar" para preencher automaticamente os campos

Deletar: Remove permanentemente do vault


### 📦 O Cofre (Vault)
Como Funciona

O cofre armazena suas mensagens criptografadas em um arquivo JSON local

# O arquivo fica em:
~/githubmeu/cybersecurity-portfolio-main/crypto-system/src/backend/vault.json

## Capacidade

Limite teórico: Milhares de cifras

Limite prático: centenas (arquivo leve)

Tamanho por cifra: ~200-300 bytes

1.000 cifras: ~300 KB

Persistência: ✅ Sim (reinicializações)

# comandos úteis:
# Ver quantidade de mensagens
cat src/backend/vault.json | grep -c '"id"'

### Limpar cofre
rm src/backend/vault.json ou o botão de delete na interface

### Backup do cofre
cp src/backend/vault.json vault-backup.json


# 🛠️ Scripts e Componentes
### 📄 start.sh - Ponto de Entrada
O que faz:

Verifica se o sistema está instalado

Se não, executa install.sh

Ativa ambiente virtual

Tenta launcher.py (GTK), fallback para launcher_simple.py

### 📄 scripts/install.sh - Instalador
Etapas:

Detecta gerenciador de pacotes (dnf/apt/pacman)

Instala dependências do sistema

Cria ambiente virtual Python

Instala dependências Python (FastAPI, PyGObject, etc)

Cria atalho no menu de aplicações

### 📄 scripts/launcher.py - App GTK
Características:

Janela nativa com GTK/WebKit

Barra de status com feedback

Inicia backend automaticamente

Detecta versão do WebKit (4.0/4.1)

### 📄 src/backend/main.py - Servidor FastAPI
Endpoints:


POST - /encrypt	- Criptografa texto

POST - /decrypt	- Descriptografa

GET	- /vault - Lista mensagens

POST - /vault - Salva mensagem

DELETE - /vault/{id} - Remove mensagem

GET	- /health	- Status do sistema

### 📄 src/backend/cipher_engine.py - Motor de Criptografia
Funções principais:
def encrypt(texto: str, key1: int, key2: int) -> str
def decrypt(cifra: str, key1: int, key2: int) -> str
Características:

Mapeamento homofônico sem colisões

Rotação dependente da posição

Normalização de acentos e pontuação

Suporte a 69 caracteres

### 📄 src/backend/database.py - Gerenciador do Vault
Funções:

load_vault() / save_vault() - Persistência JSON

CRUD completo para mensagens

Auto-incremento de IDs

### 🔒 Análise de Segurança
Como um Analista Poderia Quebrar Este Sistema?
Este sistema é educacional e propositalmente frágil para demonstração de conceitos.

## 1. Ataque de Força Bruta

## 2. Análise de Frequência

## 3. Padrões Detectáveis

### ⚠️ Conclusão
Este sistema é excelente para aprendizado, mas NUNCA use em produção!

Para uso real, utilize:

AES-256-GCM para cifragem simétrica

RSA-2048+ para cifragem assimétrica

Argon2 para hash de senhas

### Adicionar Novas Funcionalidades
Backend: Adicione rotas no main.py

Frontend: Adicione elementos no dashboard.html

Lógica: Implemente no dashboard.js

Criptografia: Modifique cipher_engine.py

### 🗑️ Desinstalação
cd crypto-system

./scripts/uninstall.sh

remove tudo:

Ambiente virtual
Atalho do menu
Dados do cofre (opcional)

### 📝 Licença
MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

### Por fim
Projeto desenvolvido para portfólio de Cibersegurança

Inspirado em sistemas de criptografia clássica

Interface com estética "terminal classified"

(agradecimento especial a minha namorada que me inspirou a fazer uma interface frontend pra mostrar esse software pra ela e também me inspirou a transformar em um app gtk mais uma vez pra mostrar a ela sem que ela se confundisse no terminal)
