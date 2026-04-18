# Aqui eu falo sobre Operadores (Dorks) do Google
### Dorks são Operadores que funcionam pra busca avançada no Google
### dork:xyz (exemplo - site:xyz.com | intext:palavra)

## 1. site:
o site: é um dork usado pra descobrir endpoints e subdomínios em um site 

## 2. intext:
o intext: é usado pra descobrir palavras ou arquivos em determinado site, exemlo "intext:passwords.txt"

## 3. filetype:
dork que filtra por extensão de arquivo (ex: pdf, log, sql, env)

## 4. index of	
encontra diretórios expostos que não possuem uma index.php/html

## 5. cache:
mostra a versão de uma página que o Google salvou (útil se o site saiu do ar)

## 6. link:
lista páginas que apontam para um domínio específico

# exemplos

## Busca por Bancos de Dados expostos:
filetype:sql "password" "INSERT INTO"

procura arquivos de dump de SQL que podem conter dumps de usuários e senhas

## Painéis de Administração e Senhas de Configuração:
intitle:"index of" "wp-config.php" ou inurl:admin/login

pode revelar arquivos de configuração do WordPress que expõem as credenciais do banco de dados em texto claro

## Câmeras e Dispositivos IoT:
inurl:"view/view.shtml"

muitas câmeras de segurança antigas ou mal configuradas usam URLs padrão que o Google indexa, permitindo acesso direto ao streaming

## Arquivos de Ambiente:
filetype:env DB_PASSWORD

arquivos .env são usados por frameworks modernos (como Node.js e Laravel) pra armazenar segredos de API e senhas, se o servidor estiver mal configurado, o Google indexa
