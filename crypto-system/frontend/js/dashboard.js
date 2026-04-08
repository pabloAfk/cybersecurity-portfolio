// dashboard.js — Inicialização e navegação do dashboard
import api from './api.js';
import { requireAuth, logout } from './auth.js';

// Função auxiliar para mostrar toast
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// Função auxiliar para validar chaves
function validKey(key) {
  return !isNaN(key) && key >= 0 && key <= 999;
}

// Função para copiar para clipboard
async function copyToClipboard(text, btnElement) {
  try {
    await navigator.clipboard.writeText(text);
    const originalText = btnElement?.textContent;
    if (btnElement) {
      btnElement.textContent = '✓ copiado!';
      setTimeout(() => { btnElement.textContent = originalText; }, 1500);
    }
    showToast('Copiado para área de transferência!', 'success');
  } catch (err) {
    showToast('Erro ao copiar', 'error');
  }
}

// ── Módulo de Criptografia ───────────────────────────────────────────
function initCrypto() {
  const encryptBtn = document.getElementById('btn-encrypt');
  const decryptBtn = document.getElementById('btn-decrypt');
  const encryptText = document.getElementById('encrypt-text');
  const decryptText = document.getElementById('decrypt-text');
  const encryptKey1 = document.getElementById('encrypt-key1');
  const encryptKey2 = document.getElementById('encrypt-key2');
  const decryptKey1 = document.getElementById('decrypt-key1');
  const decryptKey2 = document.getElementById('decrypt-key2');
  const encryptOutput = document.getElementById('encrypt-output');
  const decryptOutput = document.getElementById('decrypt-output');
  const saveToVault = document.getElementById('save-to-vault');
  const copyEncryptBtn = document.getElementById('btn-copy-encrypt');
  const copyDecryptBtn = document.getElementById('btn-copy-decrypt');

  // Criptografar
  encryptBtn?.addEventListener('click', async () => {
    const text = encryptText?.value;
    const key1 = parseInt(encryptKey1?.value);
    const key2 = parseInt(encryptKey2?.value);

    if (!text) {
      showToast('Digite um texto para criptografar', 'error');
      return;
    }
    if (!validKey(key1) || !validKey(key2)) {
      showToast('Chaves devem ser números entre 0 e 999', 'error');
      return;
    }

    encryptBtn.disabled = true;
    encryptBtn.textContent = 'processando...';

    try {
      const response = await api.post('/encrypt', { text, key1, key2 });
      const ciphertext = response.data.ciphertext;
      
      if (encryptOutput) {
        encryptOutput.innerHTML = `<div class="output-text" id="encrypt-output-text">${ciphertext}</div>`;
      }
      showToast('✅ Mensagem criptografada!', 'success');

      if (saveToVault?.checked) {
        await api.post('/vault/add', { encrypted_message: ciphertext, key1, key2 });
        showToast('📦 Salvo no cofre!', 'success');
        if (typeof loadVault === 'function') loadVault();
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao criptografar';
      showToast(msg, 'error');
    } finally {
      encryptBtn.disabled = false;
      encryptBtn.textContent = 'CRIPTOGRAFAR →';
    }
  });

  // Descriptografar
  decryptBtn?.addEventListener('click', async () => {
    const ciphertext = decryptText?.value;
    const key1 = parseInt(decryptKey1?.value);
    const key2 = parseInt(decryptKey2?.value);

    if (!ciphertext) {
      showToast('Digite uma cifra para descriptografar', 'error');
      return;
    }
    if (!ciphertext.startsWith('S:')) {
      showToast('Cifra inválida - deve começar com "S:"', 'error');
      return;
    }
    if (!validKey(key1) || !validKey(key2)) {
      showToast('Chaves devem ser números entre 0 e 999', 'error');
      return;
    }

    decryptBtn.disabled = true;
    decryptBtn.textContent = 'processando...';

    try {
      const response = await api.post('/decrypt', { ciphertext, key1, key2 });
      const plaintext = response.data.plaintext;
      
      if (decryptOutput) {
        decryptOutput.innerHTML = `<div class="output-text" id="decrypt-output-text">${plaintext}</div>`;
      }
      showToast('✅ Mensagem descriptografada!', 'success');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao descriptografar';
      showToast(msg, 'error');
    } finally {
      decryptBtn.disabled = false;
      decryptBtn.textContent = 'DESCRIPTOGRAFAR →';
    }
  });

  // Copiar resultados
  copyEncryptBtn?.addEventListener('click', () => {
    const text = document.getElementById('encrypt-output-text')?.innerText;
    if (text) copyToClipboard(text, copyEncryptBtn);
  });
  
  copyDecryptBtn?.addEventListener('click', () => {
    const text = document.getElementById('decrypt-output-text')?.innerText;
    if (text) copyToClipboard(text, copyDecryptBtn);
  });
}

// ── Módulo do Cofre (Vault) ──────────────────────────────────────────
async function loadVault() {
  const vaultList = document.getElementById('vault-list');
  if (!vaultList) return;

  try {
    const response = await api.get('/vault');
    const messages = response.data.messages || [];

    if (messages.length === 0) {
      vaultList.innerHTML = '<div class="vault-empty">📭 Nenhuma mensagem salva ainda</div>';
      return;
    }

    vaultList.innerHTML = messages.map(msg => `
      <div class="vault-card" data-id="${msg.id}">
        <div>
          <div class="vault-cipher">${msg.encrypted_message.substring(0, 100)}...</div>
          <div class="vault-meta">
            <span>📅 ${new Date(msg.created_at).toLocaleString()}</span>
            <span class="vault-key">🔑 ${msg.key1} | ${msg.key2}</span>
          </div>
        </div>
        <div class="vault-actions">
          <button class="btn-vault-action" onclick="window.quickDecrypt(${msg.id}, '${msg.encrypted_message}', ${msg.key1}, ${msg.key2})">🔓 Decrypt</button>
          <button class="btn-vault-action danger" onclick="window.deleteMessage(${msg.id})">🗑️ Delete</button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('Erro ao carregar cofre:', err);
    showToast('Erro ao carregar mensagens', 'error');
  }
}

function initVault() {
  // Função global para quick decrypt
  window.quickDecrypt = async (id, ciphertext, key1, key2) => {
    const decryptText = document.getElementById('decrypt-text');
    const decryptKey1 = document.getElementById('decrypt-key1');
    const decryptKey2 = document.getElementById('decrypt-key2');
    
    if (decryptText) decryptText.value = ciphertext;
    if (decryptKey1) decryptKey1.value = key1;
    if (decryptKey2) decryptKey2.value = key2;
    
    // Muda para o painel de decrypt
    const decryptNav = document.querySelector('.nav-item[data-panel="decrypt"]');
    if (decryptNav) decryptNav.click();
    
    showToast('🔓 Campos preenchidos para descriptografia', 'success');
  };

  // Função global para deletar mensagem
  window.deleteMessage = async (id) => {
    if (!confirm('Tem certeza que deseja excluir esta mensagem?')) return;
    
    try {
      await api.delete(`/vault/${id}`);
      showToast('✅ Mensagem removida do cofre', 'success');
      await loadVault();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao excluir';
      showToast(msg, 'error');
    }
  };
}

// ── Ferramentas ───────────────────────────────────────────────────────
function initTools() {
  const btnCheck = document.getElementById('btn-check');
  const checkK1 = document.getElementById('check-k1');
  const result = document.getElementById('collision-result');

  btnCheck?.addEventListener('click', async () => {
    const k1 = parseInt(checkK1?.value);
    if (!validKey(k1)) {
      showToast('Chave inválida (0–999).', 'error');
      return;
    }

    btnCheck.disabled = true;
    btnCheck.textContent = 'verificando...';

    try {
      const response = await api.post('/encrypt', { text: 'test', key1: k1, key2: 0 });
      const hasIssue = response.data.ciphertext.includes('?????');

      if (result) {
        result.className = `collision-result ${hasIssue ? 'unsafe' : 'safe'}`;
        result.textContent = hasIssue
          ? `⚠ Key1 = ${k1} apresenta problemas. Escolha outra chave.`
          : `✓ Key1 = ${k1} está segura. Nenhuma colisão detectada.`;
        result.style.display = 'block';
      }
    } catch (err) {
      showToast(err.response?.data?.detail || 'Erro ao verificar', 'error');
    } finally {
      btnCheck.disabled = false;
      btnCheck.textContent = 'verificar colisões';
    }
  });

  // Gerar chaves aleatórias
  const btnGen = document.getElementById('btn-gen-keys');
  const genText = document.getElementById('gen-keys-text');
  const genResult = document.getElementById('gen-keys-result');
  const btnCopyKeys = document.getElementById('btn-copy-keys');
  let generatedKeys = '';

  btnGen?.addEventListener('click', () => {
    const k1 = Math.floor(Math.random() * 1000);
    const k2 = Math.floor(Math.random() * 1000);
    generatedKeys = `KEY1: ${k1}\nKEY2: ${k2}`;
    if (genText) genText.textContent = generatedKeys;
    if (genResult) genResult.style.display = 'block';
    showToast(`Chaves geradas: K1=${k1}, K2=${k2}`, 'info');
  });

  btnCopyKeys?.addEventListener('click', () => {
    if (generatedKeys) copyToClipboard(generatedKeys, btnCopyKeys);
  });
}

// ── Inicialização do Dashboard ────────────────────────────────────────
async function initDashboard() {
  // Verifica autenticação
  const user = await requireAuth();
  if (!user) return;

  // Preenche nome do usuário
  const usernameEl = document.getElementById('topbar-username');
  if (usernameEl) usernameEl.textContent = user.username;

  // Logout
  const logoutBtn = document.getElementById('btn-logout');
  if (logoutBtn) logoutBtn.addEventListener('click', logout);

  // Navegação lateral
  const navItems = document.querySelectorAll('.nav-item[data-panel]');
  const panels = document.querySelectorAll('.panel-area > .panel');

  function switchPanel(panelId) {
    navItems.forEach(n => n.classList.toggle('active', n.dataset.panel === panelId));
    panels.forEach(p => p.classList.toggle('active', p.id === `panel-${panelId}`));
    if (panelId === 'vault') loadVault();
  }

  navItems.forEach(item => {
    item.addEventListener('click', () => switchPanel(item.dataset.panel));
  });

  // Atalhos de teclado
  document.addEventListener('keydown', e => {
    if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;
    const map = { e: 'encrypt', d: 'decrypt', v: 'vault', t: 'tools', i: 'info' };
    const panel = map[e.key.toLowerCase()];
    if (panel) switchPanel(panel);
  });

  // Inicializa módulos
  initCrypto();
  initVault();
  initTools();
  
  // Carrega vault inicial se o painel estiver visível
  const activePanel = document.querySelector('.panel.active');
  if (activePanel?.id === 'panel-vault') {
    await loadVault();
  }
}

// Inicia quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', initDashboard);
