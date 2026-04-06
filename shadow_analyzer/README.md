# 🛡️ ShadowAnalyzer v1.0

Motor de análise **estática** de malware com interface web local.

---

## O que ele analisa (de verdade)

| Técnica | Descrição |
|---|---|
| **Entropia de Shannon** | Detecta ofuscação, compressão e criptografia |
| **Strings suspeitas** | Busca por padrões de 7 famílias (ransomware, keylogger, RAT, injector, stealer, dropper, evasão) |
| **APIs de alto risco** | 20+ funções do Windows associadas a comportamento malicioso |
| **Detecção de packer** | UPX, MPRESS, Themida, VMProtect, ASPack e outros |
| **Parser PE** | Seções, imports, exports, arquitetura (requer pefile) |
| **Parser ELF** | Tipo, arquitetura, classe (32/64-bit) |
| **Hashes** | MD5 + SHA-256 para busca em VirusTotal |
| **Strings legíveis** | Extração de strings ≥8 chars do binário |
| **Score heurístico** | 0–100 combinando todas as métricas acima |

---

## Instalação

```bash
pip install flask pefile
```

## Uso

```bash
cd shadow_analyzer
python server.py
```

Abra no navegador: **http://127.0.0.1:5000**

---

## Estrutura

```
shadow_analyzer/
├── analyzer.py      ← motor de análise (Python puro)
├── server.py        ← servidor web Flask
├── requirements.txt
└── static/
    └── index.html   ← interface web
```

---

## Roadmap (v2.0 — Sandbox)

A próxima versão vai adicionar análise **dinâmica**:

- [ ] Virtualização com **QEMU** ou **Docker** isolado
- [ ] Monitoramento de syscalls com **strace** (Linux) / **Frida**
- [ ] Captura de tráfego de rede (**tcpdump**)
- [ ] Log de arquivos criados/modificados (**inotify**)
- [ ] Screenshot do comportamento visual
- [ ] Relatório comparativo: estático vs. dinâmico

---

## ⚠️ Aviso

Este software é para fins educacionais e de pesquisa em segurança.
Nunca execute arquivos suspeitos fora de um ambiente isolado.
