// dashboard.js — Versão simplificada e funcional
import api from './api.js';

// Função para mostrar toast
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// Verifica autenticação
async function checkAuth() {
  try {
    const response = await api.get('/me');
    return response.data;
  } catch {
    window.location.href = '/';
    return null;
  }
}

// Logout
async function logout() {
  try {
    await api.post('/logout');
  } finally {
    window.location.href = '/';
  }
}

// Inicialização do dashboard
async function initDashboard() {
  const user = await checkAuth();
  if (!user) return;

  // Mostra nome do usuário
  const usernameEl = document.getElementById('topbar-username');
  if (usernameEl) usernameEl.textContent = user.username;

  // Botão logout
  const logoutBtn = document.getElementById('btn-logout');
  if (logoutBtn) logoutBtn.addEventListener('click', logout);

  // Criptografar
  const encryptBtn = document.getElementById('btn-encrypt');
  if (encryptBtn) {
    encryptBtn.addEventListener('click', async () => {
      const text = document.getElementById('encrypt-text')?.value;
      const key1 = parseInt(document.getElementById('encrypt-key1')?.value);
      const key2 = parseInt(document.getElementById('encrypt-key2')?.value);
      const saveToVault = document.getElementById('save-to-vault')?.checked;

      if (!text) {
        showToast('Digite um texto para criptografar', 'error');
        return;
      }

      try {
        const response = await api.post('/encrypt', { text, key1, key2 });
        const output = document.getElementById('encrypt-output');
        if (output) {
          output.innerHTML = `<div class="output-text">${response.data.ciphertext}</div>`;
        }
        showToast('Mensagem criptografada!', 'success');

        if (saveToVault) {
          await api.post('/vault/add', {
            encrypted_message: response.data.ciphertext,
            key1, key2
          });
          showToast('Salvo no cofre!', 'success');
        }
      } catch (err) {
        showToast(err.response?.data?.detail || 'Erro ao criptografar', 'error');
      }
    });
  }

  // Descriptografar
  const decryptBtn = document.getElementById('btn-decrypt');
  if (decryptBtn) {
    decryptBtn.addEventListener('click', async () => {
      const ciphertext = document.getElementById('decrypt-text')?.value;
      const key1 = parseInt(document.getElementById('decrypt-key1')?.value);
      const key2 = parseInt(document.getElementById('decrypt-key2')?.value);

      if (!ciphertext) {
        showToast('Digite uma cifra para descriptografar', 'error');
        return;
      }

      try {
        const response = await api.post('/decrypt', { ciphertext, key1, key2 });
        const output = document.getElementById('decrypt-output');
        if (output) {
          output.innerHTML = `<div class="output-text">${response.data.plaintext}</div>`;
        }
        showToast('Mensagem descriptografada!', 'success');
      } catch (err) {
        showToast(err.response?.data?.detail || 'Erro ao descriptografar', 'error');
      }
    });
  }

  // Carregar cofre
  async function loadVault() {
    const vaultList = document.getElementById('vault-list');
    if (!vaultList) return;

    try {
      const response = await api.get('/vault');
      const messages = response.data.messages || [];

      if (messages.length === 0) {
        vaultList.innerHTML = '<div class="vault-empty">📭 Nenhuma mensagem salva</div>';
        return;
      }

      vaultList.innerHTML = messages.map(msg => `
        <div class="vault-card">
          <div>
            <div class="vault-cipher">${msg.encrypted_message.substring(0, 100)}...</div>
            <div class="vault-meta">
              <span>🔑 ${msg.key1} | ${msg.key2}</span>
              <span>📅 ${new Date(msg.created_at).toLocaleString()}</span>
            </div>
          </div>
          <div class="vault-actions">
            <button class="btn-vault-action" onclick="window.quickDecrypt('${msg.encrypted_message}', ${msg.key1}, ${msg.key2})">🔓 Usar</button>
            <button class="btn-vault-action danger" onclick="window.deleteMessage(${msg.id})">🗑️</button>
          </div>
        </div>
      `).join('');
    } catch (err) {
      vaultList.innerHTML = '<div class="vault-empty">Erro ao carregar mensagens</div>';
    }
  }

  // Quick Decrypt global
  window.quickDecrypt = (ciphertext, key1, key2) => {
    const decryptText = document.getElementById('decrypt-text');
    const decryptKey1 = document.getElementById('decrypt-key1');
    const decryptKey2 = document.getElementById('decrypt-key2');
    if (decryptText) decryptText.value = ciphertext;
    if (decryptKey1) decryptKey1.value = key1;
    if (decryptKey2) decryptKey2.value = key2;
    showToast('Campos preenchidos! Clique em DESCRIPTOGRAFAR', 'success');
  };

  // Delete Message global
  window.deleteMessage = async (id) => {
    if (!confirm('Excluir esta mensagem?')) return;
    try {
      await api.delete(`/vault/${id}`);
      showToast('Mensagem removida', 'success');
      await loadVault();
    } catch (err) {
      showToast('Erro ao excluir', 'error');
    }
  };

  // Navegação
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
      const panel = item.dataset.panel;
      document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
      item.classList.add('active');
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      const target = document.getElementById(`panel-${panel}`);
      if (target) target.classList.add('active');
      if (panel === 'vault') loadVault();
    });
  });

  // Carrega vault se for o painel ativo
  const activePanel = document.querySelector('.panel.active');
  if (activePanel?.id === 'panel-vault') loadVault();
}

// Inicia
document.addEventListener('DOMContentLoaded', initDashboard);
