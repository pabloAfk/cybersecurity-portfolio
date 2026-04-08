# 🔐 CryptoSystem - Criptografia Homofônica
> **Sistema educacional de criptografia homofônica com interface gráfica nativa (GTK) e cofre de mensagens.**

## ⚠️ Aviso Importante
╔════════════════════════════════════════════════════════════════╗
║ ESTE SISTEMA É PURAMENTE EDUCACIONAL                           ║
║ Não utilize para proteger dados reais ou sensíveis!            ║
║ A criptografia implementada é frágil e vulnerável a ataques.   ║
╚════════════════════════════════════════════════════════════════╝


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

### 4️⃣ Ferramentas
Ferramenta	                      Função
Verificador de Colisões	          Testa se uma KEY1 gera representações únicas
Gerador de Chaves	                Cria pares de chaves aleatórias

### 📦 O Cofre (Vault)
Como Funciona
O cofre armazena suas mensagens criptografadas em um arquivo JSON local:
{
  "messages": [
    {
      "id": 1,
      "encrypted_message": "S:8fK9mXpQ2...",
      "key1": 123,
      "key2": 456,
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "next_id": 2
}

# O arquivo fica em:
~/githubmeu/cybersecurity-portfolio-main/crypto-system/src/backend/vault.json

## Capacidade
Característica	     Valor
Limite teórico	     Milhares de cifras
Limite prático	     Centenas (arquivo leve)
Tamanho por cifra	   ~200-300 bytes
1.000 cifras	       ~300 KB
Persistência	       ✅ Sim (reinicializações)

comandos úteis:
# Ver quantidade de mensagens
cat src/backend/vault.json | grep -c '"id"'

# Limpar cofre
rm src/backend/vault.json

# Backup do cofre
cp src/backend/vault.json vault-backup.json


