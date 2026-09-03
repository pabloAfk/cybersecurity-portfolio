# bashsetup

Gerenciador modular de configuração do Bash. Organiza seu `.bashrc` em módulos separados dentro de `~/.bashrc.d/`, com backup automático, validação de sintaxe e controle de aliases/histórico via linha de comando.

**Versão:** 3.3.0

---

## Por que usar

Em vez de um `.bashrc` gigante e bagunçado, o `bashsetup` divide sua configuração em arquivos numerados:

```
~/.bashrc.d/
├── 00-env.sh          # variáveis de ambiente, PATH, editor, histórico
├── 10-aliases.sh       # aliases (ativáveis/desativáveis)
├── 20-functions.sh     # funções úteis (mkcd, extract, myip, etc.)
├── 30-prompt.sh         # customização do prompt
└── 40-completion.sh    # autocompletar do próprio bashsetup
```

Um pequeno "loader" é injetado no seu `.bashrc` para carregar todos esses arquivos automaticamente, na ordem numérica.

---

## Instalação

1. Salve o script como `bashsetup` em algum lugar do seu `PATH`, por exemplo:

   ```bash
   mkdir -p ~/.local/bin
   cp bashsetup.sh ~/.local/bin/bashsetup
   chmod +x ~/.local/bin/bashsetup
   ```

2. Confirme que `~/.local/bin` está no seu `PATH` (adicione ao `.bashrc` se necessário):

   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

3. Rode a geração inicial da configuração:

   ```bash
   bashsetup --gen-config
   ```

4. Recarregue o shell:

   ```bash
   source ~/.bashrc
   ```

---

## Uso

```bash
bashsetup [OPÇÃO]
```

| Opção | O que faz |
|---|---|
| `--gen-config` | Gera a estrutura padrão em `~/.bashrc.d/` e instala o loader no `.bashrc` |
| `--select-editor` | Menu interativo para escolher o editor padrão (`EDITOR`/`VISUAL`) |
| `--enable-aliases` | Ativa (descomenta) todos os aliases padrão |
| `--disable-aliases` | Desativa (comenta) todos os aliases padrão |
| `--enable-history` | Configura histórico do Bash (tamanho, formato, deduplicação) |
| `--disable-history` | Desativa a configuração customizada de histórico |
| `--install-completion` | Instala autocompletar (Tab) das opções do `bashsetup` |
| `--uninstall` | Remove o loader do `.bashrc` (com backup) e opcionalmente apaga `~/.bashrc.d` |
| `--status` | Mostra o estado atual da configuração |
| `--version`, `-v` | Mostra a versão instalada |
| `--help`, `-h` | Mostra a ajuda |

### Exemplos

```bash
bashsetup --gen-config
bashsetup --select-editor
bashsetup --enable-aliases
bashsetup --install-completion
bashsetup --status
```

### Exemplo de saída do `--status`

```
bashsetup status
────────────────────────────────────

Version          : 3.2.0
Config directory : /home/user/.bashrc.d
Loader           : enabled
Editor           : vim
Aliases          : enabled
History          : enabled

Modules:
  ✓ 00-env.sh
  ✓ 10-aliases.sh
  ✓ 20-functions.sh
  ✓ 30-prompt.sh
  ✓ 40-completion.sh
```

---

## Avisos importantes

- `--enable-aliases` e `--disable-aliases` **regeneram `10-aliases.sh` do zero**. Se você editou esse arquivo manualmente (adicionou aliases próprios), essas edições são perdidas — o script agora avisa isso explicitamente antes de sobrescrever. O `.bashrc` continua sendo salvo em backup, mas o `10-aliases.sh` em si não é versionado.
- `20-functions.sh`, `30-prompt.sh` e boa parte de `00-env.sh` são gerados **totalmente comentados**, de propósito — o objetivo é servir de referência (no estilo `visudo` ou dos arquivos de configuração comentados do Gentoo), para você descomentar manualmente o que quiser usar.
- `--uninstall` remove o bloco do loader do `.bashrc` (fazendo backup antes) e pergunta se você quer apagar `~/.bashrc.d` também. Se disser não, o diretório fica no disco, só não é mais carregado.

## Segurança e backups

- Sempre que um arquivo existente é modificado (`.bashrc` ou `00-env.sh`), o script cria antes um backup com timestamp: `~/.bashrc.bak.AAAAMMDD_HHMMSS`.
- Todos os arquivos gerados recebem permissão `600` (leitura/escrita só para o dono); o diretório `~/.bashrc.d` recebe `700`.
- Após qualquer comando que altere arquivos, o script roda `bash -n` em todos os módulos para checar erros de sintaxe antes de considerar a operação concluída.
- Se algo der errado no meio da execução, um `trap` de erro avisa qual foi o problema e, se existir, aponta o caminho do backup mais recente.

---

## Resumo técnico do código

O script segue `set -Eeuo pipefail` (interrompe em qualquer erro, variável não definida ou falha em pipe) e está organizado nas seguintes seções:

- **Constantes e cores**: caminhos dos arquivos e códigos ANSI (desativados automaticamente se a saída não for um terminal).
- **Funções de output** (`info`, `success`, `warning`, `error`, `die`): mensagens padronizadas e coloridas.
- **Tratamento de erro** (`trap ... ERR`): captura falhas e informa sobre backups disponíveis.
- **Backup e diretório** (`create_backup`, `ensure_config_dir`): preparam o ambiente com segurança.
- **Loader** (`install_loader`): injeta no `.bashrc` o trecho que carrega os módulos de `~/.bashrc.d/`.
- **Geração de módulos** (`create_env`, `create_aliases`, `create_functions`, `create_prompt`): criam os arquivos padrão (a maior parte do conteúdo vem comentada, como sugestão).
- **Controle de aliases** (`write_aliases_file`, `cmd_enable_aliases`, `cmd_disable_aliases`): regeneram o arquivo de aliases comentando ou descomentando tudo de uma vez.
- **Controle de histórico** (`cmd_enable_history`, `cmd_disable_history`): usam `sed` para ativar/desativar as variáveis `HISTSIZE`, `HISTFILESIZE`, `HISTCONTROL`, `HISTTIMEFORMAT`.
- **Editor** (`cmd_select_editor`): menu interativo (`select`) para definir `EDITOR`/`VISUAL`.
- **Completion** (`cmd_install_completion`): gera função de autocompletar via `compgen`.
- **Status** (`get_editor`, `get_alias_status`, `get_history_status`, `cmd_status`): inspeciona os arquivos sem alterá-los e reporta o estado atual.
- **Validação** (`validate_config`): roda `bash -n` em todos os módulos para garantir sintaxe válida.
- **Parser de argumentos** (`main`): interpreta a flag recebida e chama a função `cmd_*` correspondente.

---

## Requisitos

- Bash 4+ (usa recursos como `select`, arrays e expansão de parâmetros)
- Utilitários padrão: `sed`, `awk`, `grep`, `date`, `cp`, `chmod`
