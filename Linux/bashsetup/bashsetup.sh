#!/usr/bin/env bash

# ==============================================================================
# bashsetup - Modular Bash Configuration Manager
# ==============================================================================
#
# Usage:
#   bashsetup --gen-config
#   bashsetup --select-editor
#   bashsetup --enable-aliases
#   bashsetup --disable-aliases
#   bashsetup --enable-history
#   bashsetup --disable-history
#   bashsetup --install-completion
#   bashsetup --uninstall
#   bashsetup --status
#   bashsetup --help
#   bashsetup --version
#
# ==============================================================================

set -Eeuo pipefail

# ==============================================================================
# CONSTANTS
# ==============================================================================

readonly VERSION="3.3.0"

readonly BASHRC="$HOME/.bashrc"
readonly BASHRC_DIR="$HOME/.bashrc.d"

readonly ENV_FILE="$BASHRC_DIR/00-env.sh"
readonly ALIASES_FILE="$BASHRC_DIR/10-aliases.sh"
readonly FUNCTIONS_FILE="$BASHRC_DIR/20-functions.sh"
readonly PROMPT_FILE="$BASHRC_DIR/30-prompt.sh"
readonly COMPLETION_FILE="$BASHRC_DIR/40-completion.sh"

readonly LOADER_START="# >>> bashsetup loader >>>"
readonly LOADER_END="# <<< bashsetup loader <<<"

# ==============================================================================
# COLORS
# ==============================================================================

if [[ -t 1 ]]; then
    readonly GREEN='\033[0;32m'
    readonly YELLOW='\033[1;33m'
    readonly RED='\033[0;31m'
    readonly BLUE='\033[0;34m'
    readonly CYAN='\033[0;36m'
    readonly BOLD='\033[1m'
    readonly RESET='\033[0m'
else
    readonly GREEN=''
    readonly YELLOW=''
    readonly RED=''
    readonly BLUE=''
    readonly CYAN=''
    readonly BOLD=''
    readonly RESET=''
fi

# ==============================================================================
# OUTPUT
# ==============================================================================

info() {
    printf "${BLUE}ℹ${RESET} %s\n" "$1"
}

success() {
    printf "${GREEN}✓${RESET} %s\n" "$1"
}

warning() {
    printf "${YELLOW}⚠${RESET} %s\n" "$1"
}

error() {
    printf "${RED}✗${RESET} %s\n" "$1" >&2
}

die() {
    error "$1"
    exit 1
}

# ==============================================================================
# ERROR HANDLING
# ==============================================================================

on_error() {
    error "bashsetup encontrou um erro."

    if [[ -n "${BACKUP_FILE:-}" && -f "${BACKUP_FILE:-}" ]]; then
        info "Backup disponível em:"
        printf "  %s\n" "$BACKUP_FILE"
    fi
}

trap on_error ERR

# ==============================================================================
# HELP
# ==============================================================================

show_help() {
    cat << EOF
${BOLD}bashsetup${RESET} - Modular Bash Configuration Manager

${BOLD}Usage:${RESET}
  bashsetup [OPTION]

${BOLD}Options:${RESET}

  --gen-config
      Generate the default ~/.bashrc.d configuration.

  --select-editor
      Select the default shell editor.

  --enable-aliases
      Enable all default aliases. Regenerates 10-aliases.sh from scratch.

  --disable-aliases
      Disable all default aliases. Regenerates 10-aliases.sh from scratch.

  --enable-history
      Enable Bash history configuration.

  --disable-history
      Disable Bash history configuration.

  --install-completion
      Install Tab autocompletion for bashsetup in ~/.bashrc.d.

  --uninstall
      Remove the bashsetup loader from ~/.bashrc (backs it up first).
      Optionally offers to remove ~/.bashrc.d as well.

  --status
      Show current bashsetup configuration.

  --version
      Show bashsetup version.

  --help
      Show this help message.

${BOLD}Examples:${RESET}

  bashsetup --gen-config
  bashsetup --select-editor
  bashsetup --enable-aliases
  bashsetup --install-completion
  bashsetup --status
  bashsetup --uninstall

EOF
}

# ==============================================================================
# VERSION
# ==============================================================================

show_version() {
    printf "bashsetup %s\n" "$VERSION"
}

# ==============================================================================
# BACKUP
# ==============================================================================

create_backup() {

    [[ -f "$BASHRC" ]] || return 0

    local timestamp
    timestamp="$(date '+%Y%m%d_%H%M%S')"

    BACKUP_FILE="$BASHRC.bak.$timestamp"

    cp -- "$BASHRC" "$BACKUP_FILE"
    chmod 600 "$BACKUP_FILE"

    success "Backup criado: $BACKUP_FILE"
}

# ==============================================================================
# DIRECTORY
# ==============================================================================

ensure_config_dir() {

    if [[ ! -d "$BASHRC_DIR" ]]; then
        mkdir -p "$BASHRC_DIR"
        chmod 700 "$BASHRC_DIR"

        success "Diretório criado: $BASHRC_DIR"
    fi
}

# ==============================================================================
# BASHRC LOADER
# ==============================================================================

install_loader() {

    [[ -f "$BASHRC" ]] || touch "$BASHRC"

    if grep -Fq "$LOADER_START" "$BASHRC"; then
        return 0
    fi

    create_backup

    cat >> "$BASHRC" << EOF

$LOADER_START
# Carregamento automático dos módulos ~/.bashrc.d

if [[ -d "\$HOME/.bashrc.d" ]]; then
    for file in "\$HOME/.bashrc.d"/*.sh; do
        [[ -f "\$file" && -r "\$file" ]] && source "\$file"
    done
    unset file
fi
$LOADER_END
EOF

    chmod 600 "$BASHRC"

    success "Loader instalado no .bashrc."
}

# ==============================================================================
# ENVIRONMENT MODULE
# ==============================================================================

create_env() {

    [[ -f "$ENV_FILE" ]] && return 0

    cat > "$ENV_FILE" << 'EOF'
# ==============================================================================
# 00-env.sh - Environment, PATH and History
# ==============================================================================

# EDITOR
# export EDITOR="vim"
# export VISUAL="vim"

# PAGER
# export PAGER="less"

# PATH
# export PATH="$HOME/.local/bin:$PATH"
# export PATH="$HOME/bin:$PATH"

# HISTORY
# export HISTSIZE=10000
# export HISTFILESIZE=20000
# export HISTCONTROL=ignoreboth:erasedups
# export HISTTIMEFORMAT="%F %T "

EOF

    chmod 600 "$ENV_FILE"

    success "00-env.sh criado."
}

# ==============================================================================
# ALIASES MODULE (Geração determinística)
# ==============================================================================

write_aliases_file() {
    local enabled="$1"
    local c=""

    [[ "$enabled" == false ]] && c="#"

    cat > "$ALIASES_FILE" << EOF
# ==============================================================================
# 10-aliases.sh - Command Aliases
# ==============================================================================

# NAVEGAÇÃO
${c}alias ll='ls -lh --color=auto'
${c}alias la='ls -la --color=auto'
${c}alias ls='ls --color=auto'
${c}alias ..='cd ..'
${c}alias ...='cd ../..'
${c}alias ....='cd ../../..'
${c}alias .....='cd ../../../..'

# SEGURANÇA
${c}alias rm='rm -i'
${c}alias cp='cp -i'
${c}alias mv='mv -i'

# SISTEMA
${c}alias c='clear'
${c}alias e='exit'
${c}alias h='history'
${c}alias reload='source ~/.bashrc && echo "✓ Bashrc recarregado!"'
${c}alias cf='clear && fastfetch'

# MONITORAMENTO
${c}alias df='df -h'
${c}alias du='du -h'
${c}alias free='free -m'

# GIT
${c}if command -v git &> /dev/null; then
${c}    alias gs='git status'
${c}    alias ga='git add .'
${c}    alias gc='git commit -m'
${c}    alias gp='git push'
${c}    alias gpl='git pull'
${c}    alias gl='git log --oneline --graph --decorate --all'
${c}fi
EOF

    chmod 600 "$ALIASES_FILE"
}

create_aliases() {
    [[ -f "$ALIASES_FILE" ]] && return 0
    write_aliases_file false
    success "10-aliases.sh criado."
}

# ==============================================================================
# FUNCTIONS MODULE
# ==============================================================================

create_functions() {

    [[ -f "$FUNCTIONS_FILE" ]] && return 0

    cat > "$FUNCTIONS_FILE" << 'EOF'
# ==============================================================================
# 20-functions.sh - Custom Functions
# ==============================================================================

# CRIA E ENTRA NO DIRETÓRIO
# mkcd() {
#     mkdir -p "$1" && cd "$1" || return 1
# }

# BACKUP RÁPIDO
# bak() {
#     local timestamp
#     timestamp=$(date +%Y%m%d_%H%M%S)
# 
#     [ $# -eq 0 ] && {
#         echo "Uso: bak <arquivo>"
#         return 1
#     }
# 
#     for item in "$@"; do
#         if [ -e "$item" ]; then
#             cp -r "$item" "${item}.bak.${timestamp}"
#             echo "✓ Backup: ${item}.bak.${timestamp}"
#         fi
#     done
# }

# EXTRAÇÃO UNIVERSAL
# extract() {
#     if [ ! -f "$1" ]; then
#         echo "✗ Arquivo '$1' não encontrado"
#         return 1
#     fi
# 
#     case "$1" in
#         *.tar.bz2) tar xjf "$1" ;;
#         *.tar.gz)  tar xzf "$1" ;;
#         *.tar.xz)  tar xJf "$1" ;;
#         *.zip)     unzip "$1" ;;
#         *.7z)      7z x "$1" ;;
#         *.gz)      gunzip "$1" ;;
#         *)          echo "✗ Formato não suportado: $1"; return 1 ;;
#     esac
# }

# IP PÚBLICO
# myip() {
#     curl -s ifconfig.me | xargs echo "IP Público:"
# }

# PORTAS
# ports() {
#     sudo ss -tulanp 2>/dev/null | grep LISTEN | sort -n
# }

# LISTA ARQUIVOS POR TAMANHO
# ls-size() {
#     du -sh * | sort -hr
# }

# PROCURA EM ARQUIVOS
# grep-files() {
#     if [ $# -lt 2 ]; then
#         echo "Uso: grep-files <padrão> <diretório>"
#         return 1
#     fi
#     grep -r --color=auto "$1" "$2"
# }

# MONTA E DESMONTA
# mount-iso() {
#     if [ $# -lt 2 ]; then
#         echo "Uso: mount-iso <arquivo.iso> <ponto_montagem>"
#         return 1
#     fi
#     sudo mount -o loop "$1" "$2"
# }

# TEMPO DE EXECUÇÃO
# time-cmd() {
#     time "$@"
# }

# CRIA BACKUP COMPLETO DO DIRETÓRIO
# backup-dir() {
#     local dir="${1:-.}"
#     local timestamp=$(date +%Y%m%d_%H%M%S)
#     local backup_name="backup_${dir}_${timestamp}.tar.gz"
#     tar -czf "$backup_name" "$dir"
#     echo "✓ Backup criado: $backup_name"
# }

# MOSTRA INFORMAÇÕES DO SISTEMA
# sysinfo() {
#     echo "=== INFORMAÇÕES DO SISTEMA ==="
#     echo "Kernel: $(uname -r)"
#     echo "Distro: $(lsb_release -ds 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2)"
#     echo "Uptime: $(uptime -p)"
#     echo "Memória: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
#     echo "Disco: $(df -h / | grep / | awk '{print $3 "/" $2}')"
# }

EOF

    chmod 600 "$FUNCTIONS_FILE"

    success "20-functions.sh criado."
}

# ==============================================================================
# PROMPT MODULE
# ==============================================================================

create_prompt() {

    [[ -f "$PROMPT_FILE" ]] && return 0

    cat > "$PROMPT_FILE" << 'EOF'
# ==============================================================================
# 30-prompt.sh - Terminal Prompt
# ==============================================================================

# PROMPT COLORIDO
# export PS1="\[\e[32m\]\u@\h\[\e[m\]:\[\e[34m\]\w\[\e[m\]\$ "

# CORES DO LS
# eval "$(dircolors -b 2>/dev/null)"

EOF

    chmod 600 "$PROMPT_FILE"

    success "30-prompt.sh criado."
}

# ==============================================================================
# COMPLETION MODULE
# ==============================================================================

cmd_install_completion() {
    ensure_config_dir

    cat > "$COMPLETION_FILE" << 'EOF'
# ==============================================================================
# 40-completion.sh - Autocompletar do bashsetup
# ==============================================================================

_bashsetup_completions() {
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"

    local opts="--gen-config --select-editor --enable-aliases --disable-aliases --enable-history --disable-history --install-completion --uninstall --status --version --help -v -h"

    if [[ "${cur}" == -* ]]; then
        COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
        return 0
    fi
}

complete -F _bashsetup_completions bashsetup
EOF

    chmod 600 "$COMPLETION_FILE"

    success "Autocompletar instalado em 40-completion.sh."
    info "Execute 'source ~/.bashrc' para ativar o autocompletar na sessão atual."
}

# ==============================================================================
# GENERATE CONFIG
# ==============================================================================

cmd_gen_config() {

    echo ""
    printf "${BOLD}Generating Bash configuration${RESET}\n"
    echo ""

    ensure_config_dir
    install_loader

    create_env
    create_aliases
    create_functions
    create_prompt

    echo ""
    success "Configuração gerada com sucesso."
    echo ""
    info "Arquivos:"
    printf "  %s\n" "$ENV_FILE"
    printf "  %s\n" "$ALIASES_FILE"
    printf "  %s\n" "$FUNCTIONS_FILE"
    printf "  %s\n" "$PROMPT_FILE"
    echo ""
}

# ==============================================================================
# SELECT EDITOR
# ==============================================================================

cmd_select_editor() {

    ensure_config_dir
    create_env

    echo ""
    printf "${BOLD}bashsetup - Editor${RESET}\n"
    echo ""
    echo "Selecione seu editor padrão:"
    echo ""

    local editors=(
        "vim"
        "nvim"
        "nano"
        "emacs"
        "micro"
        "ne"
        "gedit"
        "code"
        "subl"
        "atom"
        "kate"
        "leafpad"
        "geany"
        "mousepad"
        "vi"
    )

    local editor

    select editor in "${editors[@]}"; do

        if [[ -z "${editor:-}" ]]; then
            warning "Opção inválida. Escolha um número da lista."
            continue
        fi

        create_backup

        if grep -qE '^[[:space:]]*#?[[:space:]]*export EDITOR=' "$ENV_FILE"; then
            sed -i -E "s/^[[:space:]]*#?[[:space:]]*export EDITOR=.*/export EDITOR=\"$editor\"/" "$ENV_FILE"
            sed -i -E "s/^[[:space:]]*#?[[:space:]]*export VISUAL=.*/export VISUAL=\"$editor\"/" "$ENV_FILE"
        else
            cat >> "$ENV_FILE" << EOF

# EDITOR
export EDITOR="$editor"
export VISUAL="$editor"
EOF
        fi

        chmod 600 "$ENV_FILE"

        success "Editor configurado como: $editor"
        break
    done
}

# ==============================================================================
# ALIASES CONTROL
# ==============================================================================
#
# NOTA: write_aliases_file() sempre regenera 10-aliases.sh do zero.
# Se você editou esse arquivo manualmente (adicionou aliases próprios),
# --enable-aliases / --disable-aliases vão sobrescrever essas edições.
# Um backup do .bashrc é criado antes, mas o 10-aliases.sh em si não é
# versionado — por isso o aviso explícito abaixo.
# ==============================================================================

cmd_enable_aliases() {
    ensure_config_dir
    create_backup

    if [[ -f "$ALIASES_FILE" ]]; then
        warning "Isso vai regenerar $ALIASES_FILE do zero."
        warning "Edições manuais feitas nesse arquivo serão perdidas."
    fi

    write_aliases_file true
    success "Aliases ativados com sucesso."
}

cmd_disable_aliases() {
    ensure_config_dir
    create_backup

    if [[ -f "$ALIASES_FILE" ]]; then
        warning "Isso vai regenerar $ALIASES_FILE do zero."
        warning "Edições manuais feitas nesse arquivo serão perdidas."
    fi

    write_aliases_file false
    success "Aliases desativados com sucesso."
}

# ==============================================================================
# HISTORY CONTROL
# ==============================================================================

cmd_enable_history() {

    ensure_config_dir
    create_env

    create_backup

    if grep -qE '^[[:space:]]*#?[[:space:]]*export HISTSIZE=' "$ENV_FILE"; then
        sed -i -E 's/^[[:space:]]*#?[[:space:]]*export HISTSIZE=.*/export HISTSIZE=10000/' "$ENV_FILE"
        sed -i -E 's/^[[:space:]]*#?[[:space:]]*export HISTFILESIZE=.*/export HISTFILESIZE=20000/' "$ENV_FILE"
        sed -i -E 's/^[[:space:]]*#?[[:space:]]*export HISTCONTROL=.*/export HISTCONTROL=ignoreboth:erasedups/' "$ENV_FILE"
        sed -i -E 's/^[[:space:]]*#?[[:space:]]*export HISTTIMEFORMAT=.*/export HISTTIMEFORMAT="%F %T "/' "$ENV_FILE"
    else
        cat >> "$ENV_FILE" << 'EOF'

# HISTORY
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTCONTROL=ignoreboth:erasedups
export HISTTIMEFORMAT="%F %T "
EOF
    fi

    chmod 600 "$ENV_FILE"

    success "Histórico configurado."
}

cmd_disable_history() {

    ensure_config_dir
    create_env

    create_backup

    # Normaliza (não empilha "#" se já estiver comentado, e comenta se
    # estiver ativo) usando o mesmo padrão "#? opcional" das outras funções.
    sed -i -E 's/^[[:space:]]*#*[[:space:]]*export (HISTSIZE|HISTFILESIZE|HISTCONTROL|HISTTIMEFORMAT)=(.*)/# export \1=\2/' "$ENV_FILE"

    chmod 600 "$ENV_FILE"

    success "Configuração de histórico desativada."
}

# ==============================================================================
# STATUS
# ==============================================================================

get_editor() {

    if [[ ! -f "$ENV_FILE" ]]; then
        echo "not configured"
        return
    fi

    local line
    line="$(grep -m1 -E '^[[:space:]]*export EDITOR=' "$ENV_FILE" || true)"

    if [[ -z "$line" ]]; then
        echo "not configured"
        return
    fi

    # Extrai o valor após o "=" e remove as aspas nas pontas
    # (mais robusto que awk -F'"', não depende da posição das aspas).
    line="${line#*=}"
    line="${line%\"}"
    line="${line#\"}"

    printf '%s\n' "$line"
}

get_alias_status() {

    if [[ ! -f "$ALIASES_FILE" ]]; then
        echo "not configured"
        return
    fi

    if grep -q '^alias ll=' "$ALIASES_FILE"; then
        echo "enabled"
    else
        echo "disabled"
    fi
}

get_history_status() {

    if [[ ! -f "$ENV_FILE" ]]; then
        echo "not configured"
        return
    fi

    if grep -q '^export HISTSIZE=' "$ENV_FILE"; then
        echo "enabled"
    else
        echo "disabled"
    fi
}

cmd_status() {

    echo ""
    printf "${BOLD}bashsetup status${RESET}\n"
    echo "────────────────────────────────────"
    echo ""

    printf "Version          : %s\n" "$VERSION"
    printf "Config directory : %s\n" "$BASHRC_DIR"

    if [[ -f "$BASHRC" ]] &&
       grep -Fq "$LOADER_START" "$BASHRC"; then
        printf "Loader           : ${GREEN}enabled${RESET}\n"
    else
        printf "Loader           : ${YELLOW}disabled${RESET}\n"
    fi

    printf "Editor           : %s\n" "$(get_editor)"
    printf "Aliases          : %s\n" "$(get_alias_status)"
    printf "History          : %s\n" "$(get_history_status)"

    echo ""
    echo "Modules:"

    for file in \
        "$ENV_FILE" \
        "$ALIASES_FILE" \
        "$FUNCTIONS_FILE" \
        "$PROMPT_FILE" \
        "$COMPLETION_FILE"; do

        if [[ -f "$file" ]]; then
            printf "  ${GREEN}✓${RESET} %s\n" "$(basename "$file")"
        else
            printf "  ${YELLOW}○${RESET} %s\n" "$(basename "$file")"
        fi
    done

    echo ""
}

# ==============================================================================
# UNINSTALL
# ==============================================================================

cmd_uninstall() {

    echo ""
    printf "${BOLD}bashsetup - Uninstall${RESET}\n"
    echo ""

    if [[ ! -f "$BASHRC" ]] || ! grep -Fq "$LOADER_START" "$BASHRC"; then
        info "Loader do bashsetup não encontrado em $BASHRC. Nada a remover."
        return 0
    fi

    create_backup

    sed -i "/$LOADER_START/,/$LOADER_END/d" "$BASHRC"

    success "Loader removido do .bashrc."

    if [[ -d "$BASHRC_DIR" ]]; then
        local reply
        read -r -p "Remover também o diretório $BASHRC_DIR e seus módulos? [y/N] " reply
        if [[ "$reply" =~ ^[Yy]$ ]]; then
            rm -rf -- "$BASHRC_DIR"
            success "Diretório $BASHRC_DIR removido."
        else
            info "Diretório $BASHRC_DIR mantido (não referenciado mais pelo .bashrc)."
        fi
    fi

    echo ""
}

# ==============================================================================
# SYNTAX CHECK
# ==============================================================================

validate_config() {

    local failed=false

    if [[ -f "$BASHRC" ]]; then
        if bash -n "$BASHRC"; then
            success ".bashrc: syntax OK"
        else
            error ".bashrc: syntax error"
            failed=true
        fi
    fi

    if [[ -d "$BASHRC_DIR" ]]; then

        for file in "$BASHRC_DIR"/*.sh; do

            [[ -f "$file" ]] || continue

            if bash -n "$file"; then
                success "$(basename "$file"): syntax OK"
            else
                error "$(basename "$file"): syntax error"
                failed=true
            fi

        done

    fi

    if [[ "$failed" == true ]]; then
        die "A configuração contém erros de sintaxe."
    fi
}

# ==============================================================================
# ARGUMENT PARSER
# ==============================================================================

main() {

    if [[ $# -eq 0 ]]; then
        show_help
        exit 0
    fi

    case "$1" in

        --gen-config)
            cmd_gen_config
            ;;

        --select-editor)
            cmd_select_editor
            ;;

        --enable-aliases)
            cmd_enable_aliases
            ;;

        --disable-aliases)
            cmd_disable_aliases
            ;;

        --enable-history)
            cmd_enable_history
            ;;

        --disable-history)
            cmd_disable_history
            ;;

        --install-completion)
            cmd_install_completion
            ;;

        --uninstall)
            cmd_uninstall
            ;;

        --status)
            cmd_status
            ;;

        --version|-v)
            show_version
            ;;

        --help|-h)
            show_help
            ;;

        *)
            error "Opção desconhecida: $1"
            echo ""
            echo "Use 'bashsetup --help' para ver as opções disponíveis."
            exit 1
            ;;

    esac

    case "$1" in
        --gen-config|--select-editor|--enable-aliases|--disable-aliases|--enable-history|--disable-history|--install-completion|--uninstall)
            echo ""
            validate_config
            ;;
    esac
}

# ==============================================================================
# ENTRY POINT
# ==============================================================================

main "$@"
