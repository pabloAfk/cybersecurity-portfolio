# 🧪 Meu Homelab de Segurança Cibernética

## 📋 Sobre o Projeto

Este homelab foi criado com o objetivo de estudar e praticar conceitos de segurança cibernética, combinando técnicas de ataque (red team) com monitoramento e detecção (blue team). A ideia é simular ataques a partir do host contra uma máquina alvo, enquanto toda a atividade é monitorada por um servidor Wazuh.

## 💻 Hardware
---
| Componente | Especificação |
|------------|---------------|
| Notebook | Acer |
| Processador | Intel Core i5 10ª Geração |
| Placa de Vídeo | NVIDIA MX250 (integrada) |
| Armazenamento | 256GB SSD |
| Memória RAM | 8GB |
---


## 🖥️ Máquinas Virtuais
---
| VM | Sistema Operacional | Função | Recursos Alocados |
|----|---------------------|--------|-------------------|
| VM1 | Ubuntu Server | Wazuh Server (SIEM) | 2GB RAM / 20GB Disk |
| VM2 | Ubuntu Server | Target (Máquina Alvo) | 1GB RAM / 10GB Disk |
---
## 🛠️ Tecnologias Utilizadas

- **Parrot OS Security Edition** - Distribuição Linux 
- **KVM/QEMU** - Hypervisor nativo do Linux (maior integração com o kernel do que o padrão VMware)
- **Wazuh** - Plataforma SIEM (Security Information and Event Management)
- **Ubuntu Server** - Sistema base das duas VMs por simular um servidor e consumir pouca RAM

## 🔄 Fluxo de Trabalho

1. **Host (Parrot OS)** → Executa ataques e scans contra a VM2
2. **VM2 (Target)** → Máquina alvo, recebe os ataques simulados
3. **VM1 (Wazuh)** → Monitora toda a atividade do host através do agente
4. **Dashboard Wazuh** → Visualização dos alertas e eventos em tempo real

## 🎯 Objetivos de Aprendizado

- Configurar e gerenciar um ambiente virtualizado com KVM
- Instalar e configurar o Wazuh (manager + agentes)
- Realizar ataques controlados em ambiente isolado
- Analisar logs e alertas gerados pelo Wazuh
- Entender a correlação entre ações ofensivas e defensivas

*Documentação atualizada em: Abril/2026*
