# Protocolos de Rede e Portas
### aqui eu vou detalhar mais sobre meus conhecimentos em alguns Protocolos de Rede e Portas que adquiri com os estudos de Nmap e Wireshark

## 1. HTTP
o HyperTextTransfer Protocol, por padrão na porta 80, que permite a visualização de sites porém envia tudo em texto puro
normalmente usado em host local

Superfície de Ataque: Sniffing (interceptação de mensagem)

## 2. HTTPS
o HTTP porém seguro, por padrão na porta 443, permite visualização de sites porém criptografado, mesmo que alguém intercepte os códigos
ainda vê tudo criptografado (TLS/SSL)

## 3. SSH
o Secure Shell, porta padrão 22, cria um canal criptografado pra acessar outra máquina da sua, como um cabo invisível de teclado e monitor até outro computador

Superfície de Ataque: Brute Force & Credential Stuffing

## 4. SCP
o Secure Copy usa a estrada do SSH (porta 22) pra envio de arquivos 

## 5. FTP 
o File Transfer Protocol, geralmente porta 20 ou 21, é um serviço que permite a transferência de arquivos entre computadores, porém inseguro

## 6. SMTP
o Simple Mail Transfer Protocol, geralmente porta 25, permite a troca de E-Mails, é um protocolo usado no envio e recepcão de emails

## 7. DNS
o Domain Name System, porta 53 por padrão, é o protocolo que realiza a tradução entre IP e nome que aparece na URL, por exemplo google.com se torna 8.8.8.8

Superfície de Ataque: DNS Cache Poisoning (Envenenar cache pro DNS direcionar pra outro Site)

## 8. RDP
o Remote Desktop Protocol, padrão porta 3389, permite você acessar máquinas Windows remotamente com interface gráfica

Superfície de Ataque: BlueKeep (executar código no servidor sem precisar de senha)

## 9. ICMP
o Internet Control Message Protocol traça rotas de um ponto a outro, o "ping", traceroute e aviso de destino inalcançável

Superfície de Ataque: ICMP Exfiltration (Exfiltração de dados por meio do ICMP)

## 10. DHCP
o Dynamic Host Configuration Protocol, porta padrão 67 (server) e 68 (cliente) gerencia endereços IP na mesma rede, é ele quem atribui automáticamente o endereço de cada dispositivo

Superfície de Ataque: DHCP Starvation (Requerimento de todos os IPs possíveis pra impedir máquinas de se conectarem)

## 11. TCP
o Transmission Control Protocol, protocolo de transferência que prioriza a integridade dos dados e informação

Superfície de Ataque: TCP SYN Flood (O atacante envia milhares de pedidos de conexão mas nunca responde, o servidor fica guardando memória para essas conexões que nunca se completam até travar)

# Portas
### algumas portas TCP

## 1. 3306
a porta padrão MySQL

## 2. 5432
a porta padrão PostgreSQL
