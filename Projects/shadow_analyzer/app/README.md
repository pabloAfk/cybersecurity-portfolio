## 🖥️ ShadowAnalyzer Desktop (v2.0)

A versão Desktop transforma o ShadowAnalyzer em um aplicativo nativo para Linux, eliminando a necessidade de abrir o navegador manualmente. Ele utiliza **PyWebView** com backend **GTK3** para renderizar a interface e **Flask** como motor interno.

### 🗂️ Estrutura de Arquivos (Desktop)
* `main.py`: O ponto de entrada. Gerencia threads do Flask, busca portas livres e cria a janela nativa.
* `install.sh`: Script de automação para instalação, configuração de dependências e integração com o sistema.

---

### 🛠️ O que o Instalador faz?
O `install.sh` foi projetado para ser agnóstico à distribuição (Fedora, Ubuntu, Debian, Arch, etc). O fluxo de instalação segue estes passos:

1.  **Detecção de Pacotes:** Identifica o gerenciador (`dnf`, `apt`, `pacman` ou `zypper`) e instala as dependências de sistema necessárias (Python3, GTK3, WebKit2GTK).
2.  **Isolamento em `/opt`:** Move o código para `/opt/shadowanalyzer/` para manter o sistema organizado.
3.  **Ambiente Híbrido (Venv):** Cria um Virtualenv com a flag `--system-site-packages`.
    > **Nota Técnica:** Isso permite que o ambiente isolado acesse o módulo `gi` (GObject Introspection) do sistema, que é uma biblioteca em C e não pode ser instalada via pip.
4.  **Gerenciamento de Dependências:** Instala via `pip` as bibliotecas `flask`, `pywebview`, `pefile` e `docker` dentro do ambiente isolado.
5.  **Integração com o Shell:** Cria um link simbólico em `/usr/local/bin/shadowanalyzer`, permitindo chamar o app de qualquer lugar do terminal.
6.  **Integração com Desktop (XDG):** Gera um arquivo `.desktop` e instala o ícone, fazendo com que o ShadowAnalyzer apareça no seu menu de aplicativos (GNOME, KDE, XFCE, etc).

---

### 🚀 Instalação e Uso

Para instalar a versão desktop no seu sistema:

```bash
# Dê permissão de execução
chmod +x install.sh

# Execute como root
sudo ./install.sh
```

**Para iniciar o app:**
* Procure por **ShadowAnalyzer** no menu do seu sistema.
* Ou digite no terminal: `shadowanalyzer`

**Para desinstalar:**
```bash
sudo ./install.sh --uninstall
```

---

### ⚙️ Detalhes do `main.py`
O script principal resolve problemas comuns de concorrência e rede:
* **Porta Dinâmica:** Utiliza a função `find_free_port()` para evitar conflitos caso a porta padrão esteja ocupada.
* **Ciclo de Vida:** Vincula o fechamento da janela ao encerramento do processo Flask (`signal.SIGTERM`), garantindo que não fiquem processos "zumbis" rodando em background.
* **Modo Desktop:** Configura a janela com tamanho mínimo e cores personalizadas para combinar com a identidade visual do projeto.

---

### 🐳 Suporte a Docker (Sandbox)
O instalador verifica automaticamente se o Docker está presente. Se detectado, a **Sandbox Dinâmica** é habilitada para execução segura de amostras. Caso contrário, o sistema operará apenas em modo de **Análise Estática**.

---
