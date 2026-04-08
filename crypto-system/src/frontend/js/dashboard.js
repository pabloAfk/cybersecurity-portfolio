// dashboard.js - Versão sem autenticação
const API_URL = window.location.origin;

// Funções auxiliares
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

async function apiRequest(endpoint, method = 'GET', data = null) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (data) options.body = JSON.stringify(data);
  
  const response = await fetch(`${API_URL}${endpoint}`, options);
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.detail || 'Erro na requisição');
  }
  return result;
}

// Criptografar
async function encrypt() {
  const text = document.getElementById('encrypt-text')?.value;
  const key1 = parseInt(document.getElementById('encrypt-key1')?.value);
  const key2 = parseInt(document.getElementById('encrypt-key2')?.value);
  const saveToVault = document.getElementById('save-to-vault')?.checked;
  
  if (!text) {
    showToast('Digite um texto para criptografar', 'error');
    return;
  }
  
  try {
    const result = await apiRequest('/encrypt', 'POST', { text, key1, key2 });
    const output = document.getElementById('encrypt-output');
    if (output) {
      output.innerHTML = `<div class="output-text" id="encrypt-output-text">${result.ciphertext}</div>`;
    }
    showToast('✅ Mensagem criptografada!', 'success');
    
    if (saveToVault) {
      await apiRequest('/vault', 'POST', {
        encrypted_message: result.ciphertext,
        key1, key2
      });
      showToast('📦 Salvo no cofre!', 'success');
      loadVault();
    }
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Descriptografar
async function decrypt() {
  const ciphertext = document.getElementById('decrypt-text')?.value;
  const key1 = parseInt(document.getElementById('decrypt-key1')?.value);
  const key2 = parseInt(document.getElementById('decrypt-key2')?.value);
  
  if (!ciphertext) {
    showToast('Digite uma cifra para descriptografar', 'error');
    return;
  }
  
  try {
    const result = await apiRequest('/decrypt', 'POST', { ciphertext, key1, key2 });
    const output = document.getElementById('decrypt-output');
    if (output) {
      output.innerHTML = `<div class="output-text" id="decrypt-output-text">${result.plaintext}</div>`;
    }
    showToast('✅ Mensagem descriptografada!', 'success');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Carregar cofre
async function loadVault() {
  const vaultList = document.getElementById('vault-list');
  if (!vaultList) return;
  
  try {
    const data = await apiRequest('/vault');
    const messages = data.messages || [];
    
    if (messages.length === 0) {
      vaultList.innerHTML = '<div class="vault-empty">📭 Nenhuma mensagem salva</div>';
      return;
    }
    
    vaultList.innerHTML = messages.map(msg => `
      <div class="vault-card" data-id="${msg.id}">
        <div>
          <div class="vault-cipher">${msg.encrypted_message.substring(0, 100)}...</div>
          <div class="vault-meta">
            <span>🔑 ${msg.key1} | ${msg.key2}</span>
            <span>📅 ${new Date(msg.created_at).toLocaleString()}</span>
          </div>
        </div>
        <div class="vault-actions">
          <button class="btn-vault-action" onclick="quickDecrypt('${msg.encrypted_message}', ${msg.key1}, ${msg.key2})">🔓 Usar</button>
          <button class="btn-vault-action danger" onclick="deleteMessage(${msg.id})">🗑️</button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    vaultList.innerHTML = '<div class="vault-empty">Erro ao carregar mensagens</div>';
  }
}

// Quick Decrypt
window.quickDecrypt = (ciphertext, key1, key2) => {
  const decryptText = document.getElementById('decrypt-text');
  const decryptKey1 = document.getElementById('decrypt-key1');
  const decryptKey2 = document.getElementById('decrypt-key2');
  if (decryptText) decryptText.value = ciphertext;
  if (decryptKey1) decryptKey1.value = key1;
  if (decryptKey2) decryptKey2.value = key2;
  showToast('🔓 Campos preenchidos!', 'success');
};

// Delete Message
window.deleteMessage = async (id) => {
  if (!confirm('Excluir esta mensagem?')) return;
  try {
    await apiRequest(`/vault/${id}`, 'DELETE');
    showToast('Mensagem removida', 'success');
    loadVault();
  } catch (err) {
    showToast('Erro ao excluir', 'error');
  }
};

// Copiar para clipboard
window.copyToClipboard = async (text, btn) => {
  try {
    await navigator.clipboard.writeText(text);
    const original = btn.textContent;
    btn.textContent = '✓ copiado!';
    setTimeout(() => btn.textContent = original, 1500);
    showToast('Copiado!', 'success');
  } catch {
    showToast('Erro ao copiar', 'error');
  }
};

// Navegação
function setupNavigation() {
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
}

// Inicialização
function init() {
  setupNavigation();
  
  // Botões
  document.getElementById('btn-encrypt')?.addEventListener('click', encrypt);
  document.getElementById('btn-decrypt')?.addEventListener('click', decrypt);
  
  // Copiar
  document.getElementById('btn-copy-encrypt')?.addEventListener('click', () => {
    const text = document.getElementById('encrypt-output-text')?.innerText;
    if (text) copyToClipboard(text, event.target);
  });
  document.getElementById('btn-copy-decrypt')?.addEventListener('click', () => {
    const text = document.getElementById('decrypt-output-text')?.innerText;
    if (text) copyToClipboard(text, event.target);
  });
  
  // Ferramentas
  document.getElementById('btn-check')?.addEventListener('click', async () => {
    const k1 = parseInt(document.getElementById('check-k1')?.value);
    if (isNaN(k1) || k1 < 0 || k1 > 999) {
      showToast('Chave inválida (0-999)', 'error');
      return;
    }
    try {
      const result = await apiRequest('/encrypt', 'POST', { text: 'test', key1: k1, key2: 0 });
      const hasIssue = result.ciphertext.includes('?????');
      const resultDiv = document.getElementById('collision-result');
      if (resultDiv) {
        resultDiv.className = `collision-result ${hasIssue ? 'unsafe' : 'safe'}`;
        resultDiv.textContent = hasIssue 
          ? `⚠ Key1 = ${k1} tem colisões!` 
          : `✓ Key1 = ${k1} está segura!`;
        resultDiv.style.display = 'block';
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  });
  
  // Gerar chaves
  document.getElementById('btn-gen-keys')?.addEventListener('click', () => {
    const k1 = Math.floor(Math.random() * 1000);
    const k2 = Math.floor(Math.random() * 1000);
    const text = `KEY1: ${k1}\nKEY2: ${k2}`;
    const genText = document.getElementById('gen-keys-text');
    const genResult = document.getElementById('gen-keys-result');
    if (genText) genText.textContent = text;
    if (genResult) genResult.style.display = 'block';
    showToast(`Chaves geradas: ${k1} | ${k2}`, 'success');
  });
  
  document.getElementById('btn-copy-keys')?.addEventListener('click', () => {
    const text = document.getElementById('gen-keys-text')?.innerText;
    if (text) copyToClipboard(text, event.target);
  });
}

document.addEventListener('DOMContentLoaded', init);
