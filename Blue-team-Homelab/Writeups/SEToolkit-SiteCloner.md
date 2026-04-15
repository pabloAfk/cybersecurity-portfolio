# SEToolkit (Clonagem de Site / Credential Harvester)
Visão geral

O SEToolkit (Social-Engineer Toolkit) é uma ferramenta focada em ataques de engenharia social.
Nesse caso, o que foi feito foi um ataque de clonagem de site com captura de credenciais (Credential Harvester).

ideia geral:

clonar um site

enganar o usuário pra ele inserir login/senha

capturar esses dados


(obviamente só em ambiente de teste, VM, lab, etc)

## Fluxo completo usado

### 1)Menu Principal 1.Social-Engineering Attacks

   
### O que é:

área principal de ataques de engenharia social
tudo que envolve manipular usuário ao invés de explorar sistema direto

### 2) Tipo de ataque 2. Website Attack Vectors

 O que é:

ataques baseados em páginas web
foco em enganar o usuário via navegador

### 3) Método de ataque web 3. Credential Harvester Attack Method

📌 O que é:

método que não invade nada diretamente

apenas captura dados que o usuário digitar

funciona assim:

vítima acessa página falsa

digita login/senha

dados são enviados pro atacante

### 4) Forma de criação do site falso 2. Site Cloner

📌 O que é:

clona um site real automaticamente

copia HTML/CSS da página

deixa visualmente igual ao original

👉 diferença pras outras opções:

Web Templates → usa modelos prontos (tipo login fake genérico)

Site Cloner → copia um site real (mais convincente)

Custom Import → você mesmo fornece os arquivos

### 5. IP para receber os dados
IP address for the POST back: 127.0.0.1

📌 O que é:

endereço onde os dados capturados vão ser enviados

basicamente o “servidor do atacante”

👉 no meu caso:

127.0.0.1 → loopback (localhost)
ou seja, tudo ficou dentro da própria VM (perfeito pra lab 👍)

### 6. URL do site a ser clonado
Enter the url to clone:

📌 O que é:

site que será copiado

👉 no meu teste:

usei localhost
ou seja, clonando algo local → ambiente controlado
##  O que acontece por trás

Depois disso, o SEToolkit:

baixa o conteúdo do site
cria uma página fake local
injeta código pra capturar dados
sobe um servidor web
espera alguém acessar
📥 Resultado esperado

Quando alguém acessa o link:

vê um site igual ao original
digita login/senha
SET salva algo tipo:
username: teste
password: 123456
