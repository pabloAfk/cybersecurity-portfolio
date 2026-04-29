"""
ShadowAnalyzer - Motor de análise estática de malware
Versão 1.0 — análise real com heurísticas, strings, entropia e headers PE/ELF
"""

import math
import hashlib
import struct
import re
import os
import string
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────
#  Assinaturas de strings suspeitas por família
# ─────────────────────────────────────────────
SUSPICIOUS_STRINGS = {
    "Ransomware": [
        b"your files have been encrypted", b"bitcoin", b"decrypt",
        b"ransom", b"pay", b"wallet", b"recovery key", b"CryptEncrypt",
        b"AES", b"RSA", b"CryptoAPI",
    ],
    "Keylogger": [
        b"GetAsyncKeyState", b"SetWindowsHookEx", b"keylog",
        b"keystroke", b"keyboard hook", b"WH_KEYBOARD",
    ],
    "RAT/Backdoor": [
        b"cmd.exe", b"powershell", b"reverse shell", b"bind shell",
        b"socket", b"connect", b"recv", b"send", b"backdoor",
        b"RemoteThread", b"ShellExecute",
    ],
    "Injector": [
        b"VirtualAllocEx", b"WriteProcessMemory", b"CreateRemoteThread",
        b"NtCreateThreadEx", b"ZwCreateThreadEx", b"OpenProcess",
        b"inject", b"hollowing", b"RunPE",
    ],
    "Stealer": [
        b"password", b"credentials", b"cookie", b"chrome", b"firefox",
        b"login data", b"wallet.dat", b"credential",
    ],
    "Dropper": [
        b"URLDownloadToFile", b"WinExec", b"CreateProcess",
        b"DropPath", b"TempPath", b"GetTempPath", b"dropper",
    ],
    "Evasion": [
        b"IsDebuggerPresent", b"CheckRemoteDebuggerPresent",
        b"NtQueryInformationProcess", b"OutputDebugString",
        b"GetTickCount", b"sleep", b"obfuscat", b"base64",
        b"VirtualProtect", b"anti-analysis",
    ],
}

# APIs do Windows consideradas de alto risco
HIGH_RISK_APIS = [
    "VirtualAllocEx", "WriteProcessMemory", "CreateRemoteThread",
    "NtCreateThreadEx", "ZwCreateThreadEx", "OpenProcess",
    "SetWindowsHookEx", "GetAsyncKeyState", "URLDownloadToFile",
    "WinExec", "ShellExecuteA", "ShellExecuteW",
    "CryptEncrypt", "CryptDecrypt", "CryptGenKey",
    "RegSetValueEx", "RegCreateKeyEx",  # persistência no registro
    "CreateService", "StartService",    # instalação de serviço
    "FindFirstFile", "CopyFile",        # worm/propagação
    "IsDebuggerPresent", "CheckRemoteDebuggerPresent",  # anti-debug
    "NtQueryInformationProcess",        # anti-análise
]

# Packers / compressores conhecidos (magic bytes na seção)
KNOWN_PACKERS = {
    b"UPX!": "UPX Packer",
    b"UPX0": "UPX Packer (seg. 0)",
    b"MPRESS": "MPRESS Packer",
    b"PECompact": "PECompact",
    b"Themida": "Themida Protector",
    b"VMProtect": "VMProtect",
    b"ASPack": "ASPack Packer",
    b".NPACK": "nPack",
    b"ExeStealth": "ExeStealth",
}


@dataclass
class AnalysisResult:
    file_name: str
    file_size: int
    md5: str
    sha256: str
    file_type: str
    entropy: float
    entropy_flag: str                       # "normal" / "high" / "packed"
    yara_score: int                         # 0–100
    risk_level: str                         # CLEAN / LOW / MEDIUM / HIGH / CRITICAL
    risk_color: str
    suspicious_strings: dict = field(default_factory=dict)   # família → lista de hits
    high_risk_apis: list = field(default_factory=list)
    packer_detected: Optional[str] = None
    pe_info: dict = field(default_factory=dict)              # seções, imports, etc.
    elf_info: dict = field(default_factory=dict)
    strings_printable: list = field(default_factory=list)    # strings legíveis ≥8 chars
    recommendations: list = field(default_factory=list)
    errors: list = field(default_factory=list)


# ─────────────────────────────────────────────
#  Cálculo de entropia de Shannon
# ─────────────────────────────────────────────
def calculate_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    freq = {}
    for byte in data:
        freq[byte] = freq.get(byte, 0) + 1
    length = len(data)
    entropy = -sum((c / length) * math.log2(c / length) for c in freq.values())
    return round(entropy, 4)


def classify_entropy(entropy: float) -> str:
    if entropy < 5.0:
        return "normal"
    elif entropy < 7.0:
        return "high"
    else:
        return "packed"  # muito provável ofuscação / compressão


# ─────────────────────────────────────────────
#  Detecção de tipo de arquivo (magic bytes)
# ─────────────────────────────────────────────
def detect_file_type(data: bytes, filename: str) -> str:
    if data[:2] == b"MZ":
        return "PE (Windows Executable)"
    if data[:4] == b"\x7fELF":
        return "ELF (Linux Executable)"
    if data[:4] in (b"PK\x03\x04", b"PK\x05\x06"):
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext in ("docx", "xlsx", "pptx"):
            return f"Office OpenXML (.{ext})"
        return "ZIP Archive"
    if data[:4] == b"%PDF":
        return "PDF Document"
    if data[:2] in (b"\xff\xfe", b"\xfe\xff") or data[:3] == b"\xef\xbb\xbf":
        return "Text / Script (BOM detected)"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    ext_map = {
        "js": "JavaScript", "vbs": "VBScript", "ps1": "PowerShell",
        "bat": "Batch Script", "py": "Python Script", "sh": "Shell Script",
        "jar": "Java Archive", "apk": "Android Package",
        "docm": "Word Macro-enabled", "xlsm": "Excel Macro-enabled",
    }
    return ext_map.get(ext, f"Unknown (.{ext})" if ext else "Unknown")


# ─────────────────────────────────────────────
#  Extração de strings legíveis (≥8 chars)
# ─────────────────────────────────────────────
def extract_strings(data: bytes, min_len: int = 8) -> list:
    printable = set(string.printable.encode())
    strings_found = []
    current = []
    for byte in data:
        if byte in printable:
            current.append(chr(byte))
        else:
            if len(current) >= min_len:
                strings_found.append("".join(current))
            current = []
    if len(current) >= min_len:
        strings_found.append("".join(current))
    return strings_found[:200]  # limita para performance


# ─────────────────────────────────────────────
#  Busca de strings / APIs suspeitas
# ─────────────────────────────────────────────
def find_suspicious_strings(data: bytes) -> dict:
    hits = {}
    data_lower = data.lower()
    for family, patterns in SUSPICIOUS_STRINGS.items():
        found = []
        for p in patterns:
            if p.lower() in data_lower:
                found.append(p.decode("utf-8", errors="replace"))
        if found:
            hits[family] = found
    return hits


def find_high_risk_apis(data: bytes) -> list:
    found = []
    for api in HIGH_RISK_APIS:
        if api.encode() in data or api.lower().encode() in data.lower():
            found.append(api)
    return found


def find_packer(data: bytes) -> Optional[str]:
    for sig, name in KNOWN_PACKERS.items():
        if sig in data:
            return name
    return None


# ─────────────────────────────────────────────
#  Parser PE (Windows EXE/DLL)
# ─────────────────────────────────────────────
def parse_pe(data: bytes) -> dict:
    info = {}
    try:
        import pefile
        pe = pefile.PE(data=data)

        # seções
        sections = []
        for section in pe.sections:
            name = section.Name.rstrip(b"\x00").decode("utf-8", errors="replace")
            entropy = section.get_entropy()
            sections.append({
                "name": name,
                "virtual_size": section.Misc_VirtualSize,
                "raw_size": section.SizeOfRawData,
                "entropy": round(entropy, 3),
                "entropy_flag": classify_entropy(entropy),
            })
        info["sections"] = sections

        # imports
        imports = []
        if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                dll = entry.dll.decode("utf-8", errors="replace") if entry.dll else "?"
                funcs = []
                for imp in entry.imports:
                    if imp.name:
                        funcs.append(imp.name.decode("utf-8", errors="replace"))
                imports.append({"dll": dll, "functions": funcs[:20]})
        info["imports"] = imports[:15]

        # exports (DLLs)
        exports = []
        if hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
            for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                if exp.name:
                    exports.append(exp.name.decode("utf-8", errors="replace"))
        info["exports"] = exports[:30]

        # características gerais
        info["is_dll"] = pe.is_dll()
        info["is_exe"] = pe.is_exe()
        info["machine"] = hex(pe.FILE_HEADER.Machine)
        info["timestamp"] = pe.FILE_HEADER.TimeDateStamp

    except Exception as e:
        info["error"] = str(e)
    return info


# ─────────────────────────────────────────────
#  Parser ELF básico
# ─────────────────────────────────────────────
def parse_elf(data: bytes) -> dict:
    info = {}
    try:
        # ELF header básico
        ei_class = data[4]  # 1=32bit, 2=64bit
        ei_data = data[5]   # 1=little, 2=big endian
        e_type = struct.unpack_from("<H" if ei_data == 1 else ">H", data, 16)[0]
        e_machine = struct.unpack_from("<H" if ei_data == 1 else ">H", data, 18)[0]

        types = {1: "Relocatable", 2: "Executable", 3: "Shared object", 4: "Core"}
        machines = {3: "x86", 62: "x86-64", 40: "ARM", 183: "AArch64"}

        info["class"] = "64-bit" if ei_class == 2 else "32-bit"
        info["type"] = types.get(e_type, f"Unknown ({e_type})")
        info["machine"] = machines.get(e_machine, f"Unknown ({e_machine})")
    except Exception as e:
        info["error"] = str(e)
    return info


# ─────────────────────────────────────────────
#  Score heurístico (0–100)
# ─────────────────────────────────────────────
def calculate_score(
    entropy: float,
    suspicious: dict,
    apis: list,
    packer: Optional[str],
    file_type: str,
    file_size: int,
) -> int:
    score = 0

    # Entropia
    if entropy >= 7.5:
        score += 30
    elif entropy >= 6.5:
        score += 20
    elif entropy >= 5.5:
        score += 10

    # Strings suspeitas por família (cada família vale pontos diferentes)
    family_weights = {
        "Injector": 25, "Ransomware": 25, "RAT/Backdoor": 20,
        "Keylogger": 20, "Stealer": 15, "Dropper": 15, "Evasion": 10,
    }
    for family, hits in suspicious.items():
        score += min(family_weights.get(family, 10), len(hits) * 5)

    # APIs de alto risco
    score += min(len(apis) * 4, 30)

    # Packer detectado
    if packer:
        score += 15

    # Tipos inerentemente arriscados
    risky_types = ["PE (Windows Executable)", "ELF (Linux Executable)",
                   "JavaScript", "VBScript", "PowerShell", "Batch Script",
                   "Word Macro-enabled", "Excel Macro-enabled"]
    if any(t in file_type for t in risky_types):
        score += 10

    return min(score, 100)


def classify_risk(score: int) -> tuple[str, str]:
    if score < 15:
        return "CLEAN", "#22c55e"
    elif score < 35:
        return "LOW", "#84cc16"
    elif score < 60:
        return "MEDIUM", "#eab308"
    elif score < 80:
        return "HIGH", "#f97316"
    else:
        return "CRITICAL", "#ef4444"


def build_recommendations(score: int, suspicious: dict, apis: list, packer: Optional[str]) -> list:
    recs = []
    if score >= 80:
        recs.append("🚨 Arquivo com alto risco de ser malware. NÃO execute.")
        recs.append("🔒 Isole o arquivo imediatamente de qualquer rede.")
    elif score >= 60:
        recs.append("⚠️  Execute apenas em ambiente isolado (sandbox/VM).")
    elif score >= 35:
        recs.append("📌 Analise em sandbox antes de qualquer execução.")
    else:
        recs.append("✅ Nenhum padrão crítico detectado. Monitoramento recomendado.")

    if packer:
        recs.append(f"📦 Packer detectado ({packer}): conteúdo real só visível em tempo de execução.")
    if "Ransomware" in suspicious:
        recs.append("💀 Padrões de ransomware: faça backup dos dados AGORA.")
    if "Injector" in suspicious:
        recs.append("💉 Possível injector de processo: risco de escalada de privilégios.")
    if "RAT/Backdoor" in suspicious:
        recs.append("📡 Possível RAT/Backdoor: monitore conexões de rede.")
    if "Keylogger" in suspicious:
        recs.append("⌨️  Possível keylogger: altere senhas em dispositivo limpo.")
    if "Evasion" in suspicious:
        recs.append("🕵️  Técnicas anti-análise detectadas: análise dinâmica necessária.")
    return recs


# ─────────────────────────────────────────────
#  Função principal de análise
# ─────────────────────────────────────────────
def analyze_file(file_path: str, file_name: str) -> AnalysisResult:
    with open(file_path, "rb") as f:
        data = f.read()

    file_size = len(data)
    md5 = hashlib.md5(data).hexdigest()
    sha256 = hashlib.sha256(data).hexdigest()
    file_type = detect_file_type(data, file_name)
    entropy = calculate_entropy(data)
    entropy_flag = classify_entropy(entropy)
    suspicious = find_suspicious_strings(data)
    apis = find_high_risk_apis(data)
    packer = find_packer(data)
    strings = extract_strings(data)

    pe_info = {}
    elf_info = {}
    if data[:2] == b"MZ":
        pe_info = parse_pe(data)
    elif data[:4] == b"\x7fELF":
        elf_info = parse_elf(data)

    score = calculate_score(entropy, suspicious, apis, packer, file_type, file_size)
    risk_level, risk_color = classify_risk(score)
    recommendations = build_recommendations(score, suspicious, apis, packer)

    return AnalysisResult(
        file_name=file_name,
        file_size=file_size,
        md5=md5,
        sha256=sha256,
        file_type=file_type,
        entropy=entropy,
        entropy_flag=entropy_flag,
        yara_score=score,
        risk_level=risk_level,
        risk_color=risk_color,
        suspicious_strings=suspicious,
        high_risk_apis=apis,
        packer_detected=packer,
        pe_info=pe_info,
        elf_info=elf_info,
        strings_printable=strings,
        recommendations=recommendations,
    )
