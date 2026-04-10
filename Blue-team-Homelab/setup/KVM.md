# instalação da KVM no Host (ParrotOS Security Edition)

## sudo apt update
## sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager -y

KVM (virtualização via hardware)
QEMU (emulador)
libvirt (gerenciador)
virt-manager (interface gráfica bonitinha)

# ver se o PC suporta virtualização

## egrep -c '(vmx|svm)' /proc/cpuinfo

precisa devolver >=1

# ativar e iniciar o serviço

## sudo systemctl enable --now libvirtd

# adicionar o usuário no grupo libvirtd

## sudo usermod -aG libvirt $USER

após isso reiniciar o PC
