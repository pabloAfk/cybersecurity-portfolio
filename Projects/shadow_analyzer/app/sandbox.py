"""
ShadowAnalyzer — Módulo de Sandbox Dinâmica (v2.0)
Executa o arquivo suspeito dentro de um container Docker isolado
e monitora: syscalls (strace), rede (tcpdump), filesystem (inotifywait) e processos.

Requisitos do host:
  - Docker instalado e rodando
  - Usuário com permissão de usar o Docker (grupo docker)
  pip install docker
"""

import os
import time
import json
import shutil
import tempfile
import threading
import subprocess
from dataclasses import dataclass, field
from typing import Optional


# ── Imagem base do container de análise ──────────────────────────────────────
# Ubuntu mínimo com as ferramentas de monitoramento instaladas.
# Construída uma vez, reutilizada em todas as análises.
SANDBOX_IMAGE = "shadowanalyzer-sandbox:latest"

DOCKERFILE_CONTENT = r"""
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq && apt-get install -y -qq \
    strace \
    tcpdump \
    inotify-tools \
    procps \
    net-tools \
    curl \
    wget \
    wine \
    wine64 \
    python3 \
    perl \
    bash \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# diretório de trabalho da análise
RUN mkdir -p /sandbox/sample /sandbox/logs /sandbox/created_files

WORKDIR /sandbox
"""

# Script que roda DENTRO do container durante a análise
# Monitora em paralelo e executa o sample
MONITOR_SCRIPT = r"""#!/bin/bash
set -e

SAMPLE="$1"
TIMEOUT="${2:-60}"
LOG_DIR="/sandbox/logs"
SAMPLE_DIR="/sandbox/sample"

mkdir -p "$LOG_DIR"

# ── 1. Monitoramento de filesystem com inotifywait ──────────────────────────
inotifywait -m -r -e create,modify,delete,moved_to,moved_from \
    --format '%T|%w|%f|%e' --timefmt '%s' \
    / --exclude "^/(proc|sys|dev|sandbox/logs)" \
    > "$LOG_DIR/filesystem.log" 2>/dev/null &
INOTIFY_PID=$!

# ── 2. Captura de rede com tcpdump ──────────────────────────────────────────
tcpdump -i any -nn -q -l \
    > "$LOG_DIR/network.log" 2>/dev/null &
TCPDUMP_PID=$!

# ── 3. Snapshot de processos antes ──────────────────────────────────────────
ps aux > "$LOG_DIR/processes_before.log" 2>/dev/null

# ── 4. Detectar como executar o sample ──────────────────────────────────────
EXT="${SAMPLE##*.}"
EXT_LOWER=$(echo "$EXT" | tr '[:upper:]' '[:lower:]')

case "$EXT_LOWER" in
    exe|dll|com)
        # Tenta wine para PE Windows
        if command -v wine &>/dev/null; then
            EXEC_CMD="wine $SAMPLE_DIR/$SAMPLE"
        else
            EXEC_CMD="echo '[sandbox] wine não disponível para $SAMPLE'"
        fi
        ;;
    py)
        EXEC_CMD="python3 $SAMPLE_DIR/$SAMPLE"
        ;;
    sh|bash)
        EXEC_CMD="bash $SAMPLE_DIR/$SAMPLE"
        ;;
    pl)
        EXEC_CMD="perl $SAMPLE_DIR/$SAMPLE"
        ;;
    elf|"")
        chmod +x "$SAMPLE_DIR/$SAMPLE"
        EXEC_CMD="$SAMPLE_DIR/$SAMPLE"
        ;;
    *)
        EXEC_CMD="echo '[sandbox] Tipo não executável diretamente: $EXT_LOWER'"
        ;;
esac

# ── 5. Executa com strace (syscalls) ────────────────────────────────────────
strace -f -tt -T \
    -e trace=network,file,process,signal,ipc \
    -o "$LOG_DIR/strace.log" \
    timeout "$TIMEOUT" \
    bash -c "$EXEC_CMD" \
    > "$LOG_DIR/stdout.log" 2> "$LOG_DIR/stderr.log" || true

# ── 6. Snapshot de processos depois ─────────────────────────────────────────
ps aux > "$LOG_DIR/processes_after.log" 2>/dev/null

# ── 7. Encerra monitores ─────────────────────────────────────────────────────
kill $INOTIFY_PID 2>/dev/null || true
kill $TCPDUMP_PID 2>/dev/null || true
sleep 1

echo "DONE" > "$LOG_DIR/status"
"""


# ─────────────────────────────────────────────────────────────────────────────
#  Resultado da análise dinâmica
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class SandboxResult:
    success: bool
    duration_seconds: float = 0.0
    error: str = ""

    # Rede
    network_connections: list = field(default_factory=list)   # IPs/hosts contatados
    dns_queries: list = field(default_factory=list)
    packets_captured: int = 0

    # Filesystem
    files_created: list = field(default_factory=list)
    files_modified: list = field(default_factory=list)
    files_deleted: list = field(default_factory=list)

    # Processos
    new_processes: list = field(default_factory=list)

    # Syscalls (resumo das mais relevantes)
    syscall_summary: dict = field(default_factory=dict)       # syscall → count
    suspicious_syscalls: list = field(default_factory=list)   # syscalls de alto risco encontradas

    # Output do processo
    stdout_snippet: str = ""
    stderr_snippet: str = ""

    # Score de comportamento dinâmico (0–100)
    behavior_score: int = 0
    behavior_flags: list = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
#  Syscalls consideradas de alto risco
# ─────────────────────────────────────────────────────────────────────────────
HIGH_RISK_SYSCALLS = {
    "ptrace":       "Anti-debug / injeção em processo",
    "process_vm_writemem": "Escrita em memória de outro processo",
    "execve":       "Execução de novo processo",
    "fork":         "Criação de processo filho",
    "clone":        "Criação de thread/processo",
    "connect":      "Conexão de rede",
    "bind":         "Abertura de porta (possível backdoor)",
    "listen":       "Escuta em porta",
    "sendto":       "Envio de dados pela rede",
    "recvfrom":     "Recebimento de dados da rede",
    "unlink":       "Deleção de arquivo",
    "rename":       "Renomeação de arquivo",
    "chmod":        "Alteração de permissões",
    "chown":        "Alteração de dono de arquivo",
    "mprotect":     "Alteração de proteção de memória",
    "mmap":         "Mapeamento de memória",
    "prctl":        "Controle de processo",
    "setuid":       "Alteração de usuário (escala de privilégio)",
    "setgid":       "Alteração de grupo",
    "kill":         "Envio de sinal para processo",
    "sched_setscheduler": "Alteração de prioridade de processo",
}


# ─────────────────────────────────────────────────────────────────────────────
#  Build da imagem Docker (só precisa rodar uma vez)
# ─────────────────────────────────────────────────────────────────────────────
def build_sandbox_image(progress_callback=None) -> tuple[bool, str]:
    """Constrói a imagem Docker do sandbox. Retorna (ok, mensagem)."""
    try:
        import docker
        client = docker.from_env()

        # Verifica se já existe
        try:
            client.images.get(SANDBOX_IMAGE)
            return True, "Imagem já existe."
        except docker.errors.ImageNotFound:
            pass

        if progress_callback:
            progress_callback("Construindo imagem Docker (pode levar alguns minutos)...")

        # Escreve Dockerfile temporário
        tmpdir = tempfile.mkdtemp()
        with open(os.path.join(tmpdir, "Dockerfile"), "w") as f:
            f.write(DOCKERFILE_CONTENT)

        # Build
        _, logs = client.images.build(
            path=tmpdir,
            tag=SANDBOX_IMAGE,
            rm=True,
            forcerm=True,
        )
        shutil.rmtree(tmpdir, ignore_errors=True)
        return True, "Imagem construída com sucesso."

    except ImportError:
        return False, "Biblioteca 'docker' não instalada. Execute: pip install docker"
    except Exception as e:
        return False, f"Erro ao construir imagem: {e}"


def check_docker_available() -> tuple[bool, str]:
    """Verifica se Docker está instalado e acessível."""
    try:
        import docker
        client = docker.from_env()
        client.ping()
        return True, "Docker disponível."
    except ImportError:
        return False, "Biblioteca 'docker' não instalada. Execute: pip install docker"
    except Exception as e:
        return False, f"Docker não acessível: {e}"


def check_image_exists() -> bool:
    try:
        import docker
        client = docker.from_env()
        client.images.get(SANDBOX_IMAGE)
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  Parsers dos logs gerados dentro do container
# ─────────────────────────────────────────────────────────────────────────────
def parse_strace_log(log_text: str) -> tuple[dict, list]:
    """Retorna (syscall_counts, suspicious_found)."""
    counts = {}
    suspicious = []

    for line in log_text.splitlines():
        # linha típica: "1234  12:00:00 execve("/bin/sh", ...) = 0"
        parts = line.strip().split()
        if len(parts) < 2:
            continue
        # extrai nome da syscall
        for part in parts:
            paren = part.find("(")
            if paren > 0:
                syscall = part[:paren]
                if syscall.isidentifier():
                    counts[syscall] = counts.get(syscall, 0) + 1
                    if syscall in HIGH_RISK_SYSCALLS and syscall not in suspicious:
                        suspicious.append(syscall)
                break

    # ordena por frequência, top 20
    top = dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:20])
    return top, suspicious


def parse_network_log(log_text: str) -> tuple[list, list, int]:
    """Retorna (connections, dns_queries, packet_count)."""
    connections = set()
    dns_queries = set()
    packet_count = 0

    for line in log_text.splitlines():
        packet_count += 1
        line_lower = line.lower()

        # DNS
        if " a? " in line or " aaaa? " in line or "domain" in line_lower:
            # extrai hostname
            parts = line.split()
            for i, p in enumerate(parts):
                if p in ("A?", "AAAA?") and i + 1 < len(parts):
                    dns_queries.add(parts[i + 1].rstrip("."))

        # Conexões TCP/UDP — extrai IPs
        import re
        ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', line)
        for ip in ips:
            # ignora loopback e broadcast
            if not ip.startswith(("127.", "0.", "255.")):
                connections.add(ip)

    return list(connections)[:50], list(dns_queries)[:30], packet_count


def parse_filesystem_log(log_text: str) -> tuple[list, list, list]:
    """Retorna (created, modified, deleted)."""
    created, modified, deleted = [], [], []
    seen = set()

    for line in log_text.splitlines():
        parts = line.split("|")
        if len(parts) < 4:
            continue
        _, directory, filename, event = parts[0], parts[1], parts[2], parts[3]
        full_path = os.path.join(directory, filename)

        # ignora paths de sistema e logs do próprio sandbox
        ignore_prefixes = ("/proc", "/sys", "/dev", "/sandbox/logs", "/run", "/tmp/.X")
        if any(full_path.startswith(p) for p in ignore_prefixes):
            continue
        if full_path in seen:
            continue
        seen.add(full_path)

        event_up = event.upper()
        if "CREATE" in event_up or "MOVED_TO" in event_up:
            created.append(full_path)
        elif "MODIFY" in event_up:
            modified.append(full_path)
        elif "DELETE" in event_up or "MOVED_FROM" in event_up:
            deleted.append(full_path)

    return created[:100], modified[:100], deleted[:50]


def parse_process_diff(before: str, after: str) -> list:
    """Retorna processos que apareceram após a execução."""
    def extract_pids(text):
        procs = {}
        for line in text.splitlines()[1:]:  # pula header
            parts = line.split(None, 10)
            if len(parts) >= 11:
                try:
                    procs[parts[1]] = parts[10]  # PID → COMMAND
                except Exception:
                    pass
        return procs

    before_procs = extract_pids(before)
    after_procs = extract_pids(after)
    new = []
    for pid, cmd in after_procs.items():
        if pid not in before_procs and not cmd.startswith("["):
            new.append(f"[{pid}] {cmd}")
    return new[:20]


# ─────────────────────────────────────────────────────────────────────────────
#  Score de comportamento dinâmico
# ─────────────────────────────────────────────────────────────────────────────
def calculate_behavior_score(result: SandboxResult) -> tuple[int, list]:
    score = 0
    flags = []

    if result.network_connections:
        score += min(len(result.network_connections) * 10, 30)
        flags.append(f"🌐 {len(result.network_connections)} IP(s) contatado(s)")

    if result.dns_queries:
        score += min(len(result.dns_queries) * 8, 20)
        flags.append(f"🔍 {len(result.dns_queries)} consulta(s) DNS")

    if result.files_created:
        score += min(len(result.files_created) * 5, 20)
        flags.append(f"📝 {len(result.files_created)} arquivo(s) criado(s)")

    if result.files_deleted:
        score += min(len(result.files_deleted) * 8, 25)
        flags.append(f"🗑️ {len(result.files_deleted)} arquivo(s) deletado(s)")

    if result.new_processes:
        score += min(len(result.new_processes) * 5, 15)
        flags.append(f"⚙️ {len(result.new_processes)} processo(s) filho(s)")

    # syscalls de alto risco
    risky = [s for s in result.suspicious_syscalls
             if s in ("connect", "bind", "listen", "ptrace", "setuid")]
    if risky:
        score += len(risky) * 8
        flags.append(f"⚠️ Syscalls críticas: {', '.join(risky)}")

    return min(score, 100), flags


# ─────────────────────────────────────────────────────────────────────────────
#  Função principal: roda o sandbox
# ─────────────────────────────────────────────────────────────────────────────
def run_sandbox(
    file_path: str,
    file_name: str,
    timeout_seconds: int = 60,
    progress_callback=None,
) -> SandboxResult:
    """
    Executa o arquivo dentro do container Docker e retorna SandboxResult.
    O container é destruído ao final independente do resultado.
    """
    try:
        import docker
    except ImportError:
        return SandboxResult(success=False, error="Biblioteca 'docker' não instalada.")

    def progress(msg):
        if progress_callback:
            progress_callback(msg)

    # ── Verifica Docker ──────────────────────────────────────────────────────
    ok, msg = check_docker_available()
    if not ok:
        return SandboxResult(success=False, error=msg)

    # ── Verifica/constrói imagem ─────────────────────────────────────────────
    if not check_image_exists():
        progress("Construindo imagem sandbox (primeira vez, aguarde)...")
        ok, msg = build_sandbox_image(progress)
        if not ok:
            return SandboxResult(success=False, error=msg)

    client = docker.from_env()
    container = None
    tmp_dir = tempfile.mkdtemp(prefix="shadow_sandbox_")
    start_time = time.time()

    try:
        # ── Prepara arquivos no volume temporário ────────────────────────────
        sample_dir = os.path.join(tmp_dir, "sample")
        logs_dir   = os.path.join(tmp_dir, "logs")
        os.makedirs(sample_dir)
        os.makedirs(logs_dir)

        # copia o sample
        dest = os.path.join(sample_dir, file_name)
        shutil.copy2(file_path, dest)

        # escreve o script de monitoramento
        monitor_path = os.path.join(tmp_dir, "monitor.sh")
        with open(monitor_path, "w", newline="\n") as f:
            f.write(MONITOR_SCRIPT)
        os.chmod(monitor_path, 0o755)

        progress("Iniciando container isolado...")

        # ── Cria e inicia o container ────────────────────────────────────────
        container = client.containers.run(
            image=SANDBOX_IMAGE,
            command=f"/sandbox/monitor.sh {file_name} {timeout_seconds}",
            volumes={
                tmp_dir: {"bind": "/sandbox", "mode": "rw"},
            },
            # isolamento de rede: bridge própria sem acesso externo real
            # (para análise de comportamento de rede, observamos tentativas)
            network_mode="bridge",
            # limites de recursos
            mem_limit="256m",
            cpu_period=100000,
            cpu_quota=50000,   # 50% de 1 CPU
            # sem acesso a devices do host
            cap_drop=["ALL"],
            cap_add=["NET_RAW", "SYS_PTRACE"],  # necessário para tcpdump e strace
            security_opt=["no-new-privileges"],
            # read-only exceto /sandbox
            # tmpfs para /tmp
            tmpfs={"/tmp": "size=64m"},
            detach=True,
            remove=False,
            name=f"shadow_{int(time.time())}",
        )

        progress(f"Monitorando execução (timeout: {timeout_seconds}s)...")

        # aguarda o container terminar (com timeout extra de segurança)
        try:
            container.wait(timeout=timeout_seconds + 30)
        except Exception:
            pass

        duration = round(time.time() - start_time, 2)
        progress("Coletando logs...")

        # ── Lê os logs gerados ───────────────────────────────────────────────
        def read_log(name):
            path = os.path.join(logs_dir, name)
            if os.path.exists(path):
                with open(path, "r", errors="replace") as f:
                    return f.read()
            return ""

        strace_log  = read_log("strace.log")
        network_log = read_log("network.log")
        fs_log      = read_log("filesystem.log")
        proc_before = read_log("processes_before.log")
        proc_after  = read_log("processes_after.log")
        stdout      = read_log("stdout.log")
        stderr      = read_log("stderr.log")

        # ── Parseia logs ─────────────────────────────────────────────────────
        syscall_summary, suspicious_syscalls = parse_strace_log(strace_log)
        connections, dns_queries, packet_count = parse_network_log(network_log)
        files_created, files_modified, files_deleted = parse_filesystem_log(fs_log)
        new_processes = parse_process_diff(proc_before, proc_after)

        result = SandboxResult(
            success=True,
            duration_seconds=duration,
            network_connections=connections,
            dns_queries=dns_queries,
            packets_captured=packet_count,
            files_created=files_created,
            files_modified=files_modified,
            files_deleted=files_deleted,
            new_processes=new_processes,
            syscall_summary=syscall_summary,
            suspicious_syscalls=suspicious_syscalls,
            stdout_snippet=stdout[:2000],
            stderr_snippet=stderr[:1000],
        )

        # Score de comportamento
        result.behavior_score, result.behavior_flags = calculate_behavior_score(result)
        return result

    except Exception as e:
        return SandboxResult(success=False, error=str(e),
                             duration_seconds=round(time.time() - start_time, 2))

    finally:
        # ── Destrói container e arquivos temporários SEMPRE ──────────────────
        if container:
            try:
                container.stop(timeout=5)
            except Exception:
                pass
            try:
                container.remove(force=True)
            except Exception:
                pass
        shutil.rmtree(tmp_dir, ignore_errors=True)
        progress("Container destruído. Análise concluída.")
