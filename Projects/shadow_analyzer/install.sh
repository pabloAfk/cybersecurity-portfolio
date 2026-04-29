#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
#  ShadowAnalyzer v2.0 — Instalador
#  Uso:     sudo ./install.sh
#  Remover: sudo ./install.sh --uninstall
# ═══════════════════════════════════════════════════════════════════════

# SEM set -e — cada passo trata o próprio erro explicitamente

APP_VERSION="2.0"
INSTALL_DIR="/opt/shadowanalyzer"
VENV_DIR="$INSTALL_DIR/venv"
BIN_LINK="/usr/local/bin/shadowanalyzer"
DESKTOP_DIR="/usr/share/applications"
ICON_DIR="/usr/share/icons/hicolor/scalable/apps"

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
RED='\033[0;31m'; BOLD='\033[1m'; NC='\033[0m'

banner() {
  echo ""
  echo -e "${CYAN}${BOLD}  ╔═══════════════════════════════════════════╗${NC}"
  echo -e "${CYAN}${BOLD}  ║  🛡️  ShadowAnalyzer v${APP_VERSION} — Instalador   ║${NC}"
  echo -e "${CYAN}${BOLD}  ╚═══════════════════════════════════════════╝${NC}"
  echo ""
}

ok()   { echo -e "  ${GREEN}✔${NC} $*"; }
info() { echo -e "  ${CYAN}→${NC} $*"; }
warn() { echo -e "  ${YELLOW}⚠${NC}  $*"; }
die()  { echo -e "  ${RED}✘${NC} $*"; echo ""; exit 1; }
step() { echo ""; echo -e "${BOLD}  ── $* ${NC}"; }

need_root() {
  if [ "$EUID" -ne 0 ]; then
    die "Execute com sudo:  sudo ./install.sh"
  fi
}

detect_pm() {
  if   command -v dnf     &>/dev/null; then echo "dnf"
  elif command -v apt-get &>/dev/null; then echo "apt"
  elif command -v pacman  &>/dev/null; then echo "pacman"
  elif command -v zypper  &>/dev/null; then echo "zypper"
  else echo "unknown"
  fi
}

# ── instala pacotes de sistema ─────────────────────────────────────────
install_system_deps() {
  local pm="$1"
  local rc=0

  case "$pm" in
    dnf)
      info "Tentando webkit2gtk4.1..."
      dnf install -y \
        python3 python3-pip python3-venv \
        python3-gobject gobject-introspection \
        webkit2gtk4.1 cairo-gobject gtk3
      rc=$?
      if [ $rc -ne 0 ]; then
        info "Tentando webkit2gtk3 como fallback..."
        dnf install -y \
          python3 python3-pip python3-venv \
          python3-gobject gobject-introspection \
          webkit2gtk3 cairo-gobject gtk3
        rc=$?
      fi
      ;;
    apt)
      apt-get update -qq
      info "Tentando libwebkit2gtk-4.1-0..."
      apt-get install -y \
        python3 python3-pip python3-venv \
        python3-gi python3-gi-cairo \
        gir1.2-gtk-3.0 \
        libwebkit2gtk-4.1-0 gir1.2-webkit2-4.1
      rc=$?
      if [ $rc -ne 0 ]; then
        info "Tentando libwebkit2gtk-4.0-37 como fallback..."
        apt-get install -y \
          python3 python3-pip python3-venv \
          python3-gi python3-gi-cairo \
          gir1.2-gtk-3.0 \
          libwebkit2gtk-4.0-37 gir1.2-webkit2-4.0
        rc=$?
      fi
      ;;
    pacman)
      pacman -Sy --noconfirm python python-pip python-gobject webkit2gtk
      rc=$?
      ;;
    zypper)
      zypper install -y python3 python3-pip python3-venv python3-gobject webkit2gtk3
      rc=$?
      ;;
    *)
      warn "Gerenciador de pacotes não reconhecido."
      warn "Instale manualmente: python3, python3-venv, python3-gi, webkit2gtk"
      rc=0  # continua — talvez já esteja instalado
      ;;
  esac

  return $rc
}

# ── encontra python3 com gi acessível ──────────────────────────────────
find_system_python() {
  for py in python3 python3.12 python3.11 python3.10 python3.9; do
    if command -v "$py" &>/dev/null; then
      if "$py" -c "import gi" 2>/dev/null; then
        echo "$py"
        return 0
      fi
    fi
  done
  return 1
}

# ── checa webkit2 via python ────────────────────────────────────────────
check_webkit() {
  local py="$1"
  "$py" -c "
import gi
for v in ('4.1', '4.0'):
    try:
        gi.require_version('WebKit2', v)
        from gi.repository import WebKit2
        print(v)
        exit(0)
    except Exception:
        pass
exit(1)
" 2>/dev/null
}

# ══════════════════════════════════════════════════════════════════════
#  DESINSTALAR
# ══════════════════════════════════════════════════════════════════════
do_uninstall() {
  banner
  echo -e "  ${RED}${BOLD}Desinstalando ShadowAnalyzer...${NC}"
  echo ""
  need_root

  if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR" && ok "Removido: $INSTALL_DIR"
  fi
  if [ -f "$BIN_LINK" ]; then
    rm -f "$BIN_LINK" && ok "Removido: $BIN_LINK"
  fi
  if [ -f "$DESKTOP_DIR/shadowanalyzer.desktop" ]; then
    rm -f "$DESKTOP_DIR/shadowanalyzer.desktop" && ok "Removido: entrada do menu"
  fi
  if [ -f "$ICON_DIR/shadowanalyzer.svg" ]; then
    rm -f "$ICON_DIR/shadowanalyzer.svg" && ok "Removido: ícone"
  fi

  command -v update-desktop-database &>/dev/null && \
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

  echo ""
  echo -e "  ${GREEN}${BOLD}ShadowAnalyzer removido com sucesso.${NC}"
  echo ""
  exit 0
}

# ══════════════════════════════════════════════════════════════════════
#  INSTALAR
# ══════════════════════════════════════════════════════════════════════
do_install() {
  banner
  need_root

  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  SRC="$SCRIPT_DIR/app"

  if [ ! -f "$SRC/main.py" ]; then
    die "Pasta 'app/' não encontrada ao lado do install.sh"
  fi

  PM=$(detect_pm)
  ok "Gerenciador de pacotes: $PM"

  # ── 1. Deps de sistema ────────────────────────────────────────────
  step "1/6  Instalando dependências do sistema..."
  install_system_deps "$PM"
  # não abortamos aqui — pode já estar tudo instalado mesmo com rc != 0

  # ── 2. Valida python + gi + webkit ───────────────────────────────
  step "2/6  Verificando Python e WebKit2GTK..."

  SYS_PY=$(find_system_python)
  if [ -z "$SYS_PY" ]; then
    echo ""
    die "python3-gi (gobject) não encontrado. Instale manualmente:
       dnf:    sudo dnf install python3-gobject
       apt:    sudo apt install python3-gi
       pacman: sudo pacman -S python-gobject"
  fi
  ok "Python com gi: $SYS_PY  ($(${SYS_PY} --version))"

  WK_VER=$(check_webkit "$SYS_PY")
  if [ -z "$WK_VER" ]; then
    echo ""
    die "WebKit2GTK não encontrado. Instale manualmente:
       dnf:    sudo dnf install webkit2gtk4.1   (ou webkit2gtk3)
       apt:    sudo apt install libwebkit2gtk-4.1-0
       pacman: sudo pacman -S webkit2gtk"
  fi
  ok "WebKit2GTK $WK_VER OK"

  # ── 3. Copia arquivos ─────────────────────────────────────────────
  step "3/6  Copiando arquivos para $INSTALL_DIR ..."

  rm -rf "$INSTALL_DIR"
  mkdir -p "$INSTALL_DIR"

  if ! cp -r "$SRC/." "$INSTALL_DIR/app"; then
    die "Falha ao copiar arquivos para $INSTALL_DIR"
  fi
  ok "Arquivos copiados"

  # ── 4. Virtualenv com --system-site-packages ──────────────────────
  step "4/6  Criando ambiente Python isolado..."

  if ! "$SYS_PY" -m venv --system-site-packages "$VENV_DIR"; then
    die "Falha ao criar virtualenv. Instale: sudo $PM install python3-venv"
  fi
  ok "Virtualenv criado"

  info "Instalando Flask, pywebview, pefile, docker..."
  if ! "$VENV_DIR/bin/pip" install --quiet --upgrade pip; then
    warn "Falha ao atualizar pip — continuando com versão atual"
  fi

  if ! "$VENV_DIR/bin/pip" install \
      "flask>=3.0.0" \
      "pywebview>=5.0" \
      "pefile>=2023.2.7" \
      "docker>=7.0.0"; then
    die "Falha ao instalar dependências Python via pip"
  fi
  ok "Dependências Python instaladas"

  # ── 5. Launcher ───────────────────────────────────────────────────
  step "5/6  Criando comando 'shadowanalyzer'..."

  cat > "$BIN_LINK" << LAUNCHER
#!/usr/bin/env bash
export PYWEBVIEW_GUILIB=gtk
export GDK_BACKEND=\${GDK_BACKEND:-x11}
cd "$INSTALL_DIR/app"
exec "$VENV_DIR/bin/python" "$INSTALL_DIR/app/main.py" "\$@"
LAUNCHER

  chmod +x "$BIN_LINK"
  ok "Comando disponível: shadowanalyzer"

  # ── 6. Ícone + menu ───────────────────────────────────────────────
  step "6/6  Registrando no menu do sistema..."

  mkdir -p "$ICON_DIR"
  if [ -f "$SCRIPT_DIR/shadowanalyzer.svg" ]; then
    cp "$SCRIPT_DIR/shadowanalyzer.svg" "$ICON_DIR/shadowanalyzer.svg"
    ok "Ícone instalado"
  fi

  mkdir -p "$DESKTOP_DIR"
  cat > "$DESKTOP_DIR/shadowanalyzer.desktop" << DESKTOP
[Desktop Entry]
Name=ShadowAnalyzer
GenericName=Malware Analyzer
Comment=Análise estática e dinâmica de malware
Exec=$BIN_LINK %U
Icon=shadowanalyzer
Terminal=false
Type=Application
Categories=Security;System;
Keywords=malware;security;análise;sandbox;vírus;
StartupWMClass=shadowanalyzer
StartupNotify=true
DESKTOP

  command -v update-desktop-database &>/dev/null && \
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
  ok "Entrada no menu criada (categoria: Security)"

  # ── Docker (aviso) ────────────────────────────────────────────────
  echo ""
  if command -v docker &>/dev/null; then
    ok "Docker detectado — Sandbox Dinâmica disponível"
  else
    warn "Docker não instalado — apenas análise estática disponível"
    case "$PM" in
      dnf)    warn "Instalar: sudo dnf install docker && sudo systemctl enable --now docker" ;;
      apt)    warn "Instalar: sudo apt install docker.io" ;;
      pacman) warn "Instalar: sudo pacman -S docker && sudo systemctl enable --now docker" ;;
    esac
    warn "Depois: sudo usermod -aG docker \$USER  (e reinicie a sessão)"
  fi

  # ── Resumo ────────────────────────────────────────────────────────
  echo ""
  echo -e "${GREEN}${BOLD}  ══════════════════════════════════════════════${NC}"
  echo -e "${GREEN}${BOLD}  ✔  ShadowAnalyzer v${APP_VERSION} instalado!${NC}"
  echo -e "${GREEN}${BOLD}  ══════════════════════════════════════════════${NC}"
  echo ""
  echo -e "  Abrir pelo menu:  ${CYAN}ShadowAnalyzer${NC}  (categoria Security)"
  echo -e "  Abrir no terminal: ${CYAN}shadowanalyzer${NC}"
  echo -e "  Desinstalar:       ${CYAN}sudo ./install.sh --uninstall${NC}"
  echo ""
}

# ── entry point ────────────────────────────────────────────────────────
case "${1:-}" in
  --uninstall|-u|--remove) do_uninstall ;;
  --help|-h)
    echo "Uso: sudo ./install.sh             # instalar"
    echo "     sudo ./install.sh --uninstall # desinstalar"
    ;;
  *) do_install ;;
esac
