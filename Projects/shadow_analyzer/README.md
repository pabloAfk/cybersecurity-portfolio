# 🛡️ ShadowAnalyzer v2.0

Motor de análise de malware com **análise estática** + **sandbox dinâmica** via Docker.

---

## Instalação

```bash
pip install flask pefile docker
```

Docker também precisa estar instalado:
- **Linux**: https://docs.docker.com/engine/install/
- **Windows/Mac**: https://www.docker.com/products/docker-desktop/

## Uso

```bash
cd shadow_analyzer
python server.py
```

Abra: **http://127.0.0.1:5000**

---

## Análise Estática (sem Docker)

| Técnica | O que detecta |
|---|---|
| Entropia de Shannon | Ofuscação, compressão, criptografia |
| Strings suspeitas | 7 famílias: ransomware, keylogger, RAT, injector, stealer, dropper, evasão |
| High-Risk APIs | 20+ funções do Windows associadas a malware |
| Detecção de packer | UPX, MPRESS, Themida, VMProtect, ASPack e outros |
| Parser PE | Seções, imports, exports, arquitetura |
| Parser ELF | Binários Linux: tipo, arquitetura, classe |
| Hashes | MD5 + SHA-256 para busca no VirusTotal |
| Score heurístico | 0–100 combinando todas as métricas |

## Sandbox Dinâmica (requer Docker)

Arquivo executado dentro de um container Ubuntu isolado com:

| Monitor | Ferramenta | Captura |
|---|---|---|
| Syscalls | strace | Chamadas ao kernel em tempo real |
| Rede | tcpdump | IPs contatados, DNS queries, pacotes |
| Filesystem | inotifywait | Arquivos criados, modificados, deletados |
| Processos | /proc | Processos filhos criados |

### Segurança do sandbox
- Container destruído automaticamente após cada análise
- Limite de memória: 256 MB / CPU: 50%
- Sem acesso a devices do host
- Sem novos privilégios

### Primeira execução
Na aba Sandbox da interface, clique em "Construir Imagem Sandbox".
Só precisa fazer uma vez — faz download do Ubuntu 22.04 e instala as ferramentas.

---

## Estrutura

```
shadow_analyzer/
├── analyzer.py     ← análise estática
├── sandbox.py      ← sandbox dinâmica (Docker)
├── server.py       ← servidor Flask + SSE
├── requirements.txt
└── static/
    └── index.html  ← interface web
```

## ⚠️ Aviso

Software para fins educacionais e pesquisa em segurança.
Nunca analise malware real fora de um ambiente isolado e controlado.
