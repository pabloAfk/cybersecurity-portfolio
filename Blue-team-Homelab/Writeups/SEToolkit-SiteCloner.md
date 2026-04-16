# SEToolkit (Clonagem de Site / Credential Harvester)

O SEToolkit (Social-Engineer Toolkit) é uma ferramenta focada em ataques de engenharia social, nesse caso, o que foi feito foi um ataque de clonagem de site com captura de credenciais (Credential Harvester)

ideia geral: clonar um site, enganar o usuário pra ele inserir login/senha e capturar esses dados

(obviamente só em ambiente de teste, VM, lab, etc)

sempre verifique suas URLs


### 1)Menu Principal 
1.Social-Engineering Attacks

área principal de ataques de engenharia social, tudo que envolve manipular usuário ao invés de explorar sistema direto

### 2) Tipo de ataque 
2. Website Attack Vectors

ataques baseados em páginas web, foco em enganar o usuário via navegador

### 3) Método de ataque web 
3. Credential Harvester Attack Method

método que não invade nada diretamente, apenas captura dados que o usuário digitar

vítima acessa página falsa - digita login/senha - dados são enviados pro atacante

### 4) Forma de criação do site falso 
2. Site Cloner

clona um site real automaticamente, copia HTML/CSS da página e deixa visualmente igual ao original

diferença pras outras opções: Web Templates usa modelos prontos (tipo login fake genérico), Site Cloner copia um site real (mais convincente) e Custom Import você mesmo fornece os arquivos

### 5. IP para receber os dados
IP address for the POST back: 127.0.0.1

endereço onde os dados capturados vão ser enviados, basicamente o “servidor do atacante”

no meu caso usei 127.0.0.1 (localhost), ou seja, tudo ficou dentro da própria VM

### 6. URL do site a ser clonado
Enter the url to clone: (site que será copiado)

##  o que acontece por trás

depois disso, o SEToolkit baixa o conteúdo do site, cria uma página fake local, injeta código pra capturar dados, sobe um servidor web e espera alguém acessar

quando alguém acessa o link vê um site igual ao original, digita login/senha, SET salva algo tipo: username: teste | password: 123456

