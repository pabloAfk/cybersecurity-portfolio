// vault.js — Gerenciamento do cofre de mensagens

async function loadVault() {
  const grid = document.getElementById('vault-grid');
  const loading = document.getElementById('vault-loading');
  if (!grid) return;

  setProcessing('vault-loading', true);
  grid.innerHTML = '';

  try {
    const data = await api.get('/vault');
    const messages = data.messages || [];

    if (messages.length === 0) {
      grid.innerHTML = `
        <div class="vault-empty">
          Nenhuma mensagem no cofre.<br>
          <span style="font-size:0.65rem;margin-top:0.3rem;display:block;opacity:0.6">
            Cifre uma mensagem e ative "salvar no cofre".
          </span>
        </div>`;
      return;
    }

    messages.forEach(msg => {
      grid.appendChild(buildVaultCard(msg));
    });
  } catch (err) {
    grid.innerHTML = `<div class="vault-empty" style="color:var(--red)">
      Falha ao carregar cofre: ${err.message}
    </div>`;
  } finally {
    setProcessing('vault-loading', false);
  }
}

function buildVaultCard(msg) {
  const card = document.createElement('div');
  card.className = 'vault-card';
  card.dataset.id = msg.id;

  card.innerHTML = `
    <div>
      <div class="vault-cipher">${truncate(msg.encrypted_message, 100)}</div>
      <div class="vault-meta">
        <span>KEY1: <span class="vault-key">${msg.key1}</span></span>
        <span>KEY2: <span class="vault-key">${msg.key2}</span></span>
        <span>${formatDate(msg.created_at)}</span>
      </div>
    </div>
    <div class="vault-actions">
      <button class="btn-vault-action btn-use" title="Usar no decifrador">↳ usar</button>
      <button class="btn-vault-action btn-copy-vault" title="Copiar cifra">copiar</button>
      <button class="btn-vault-action danger btn-delete" title="Deletar">✕</button>
    </div>
  `;

  // copiar cifra
  card.querySelector('.btn-copy-vault').addEventListener('click', () => {
    copyToClipboard(msg.encrypted_message);
  });

  // usar no decifrador
  card.querySelector('.btn-use').addEventListener('click', () => {
    if (window.fillDecrypt) window.fillDecrypt(msg.encrypted_message, msg.key1, msg.key2);
  });

  // deletar
  card.querySelector('.btn-delete').addEventListener('click', async () => {
    if (!confirm('Remover esta mensagem do cofre?')) return;
    try {
      await api.delete(`/vault/${msg.id}`);
      card.style.transition = 'opacity 0.2s';
      card.style.opacity = '0';
      setTimeout(() => card.remove(), 200);
      showToast('Mensagem removida do cofre.', 'success');

      // se ficou vazio, mostra placeholder
      const grid = document.getElementById('vault-grid');
      if (grid && !grid.querySelector('.vault-card')) {
        grid.innerHTML = `<div class="vault-empty">Cofre vazio.</div>`;
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  return card;
}

function initVault() {
  const btnRefresh = document.getElementById('btn-vault-refresh');
  if (btnRefresh) {
    btnRefresh.addEventListener('click', loadVault);
  }
}
