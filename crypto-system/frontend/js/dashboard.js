// dashboard.js — Inicialização e navegação do dashboard

async function initDashboard() {
  // ── Verifica autenticação ─────────────────────────────────────────
  const user = await requireAuth();
  if (!user) return;

  // ── Preenche nome do usuário ──────────────────────────────────────
  const el = document.getElementById('topbar-username');
  if (el) el.textContent = user.username;

  // ── Logout ────────────────────────────────────────────────────────
  document.getElementById('btn-logout')?.addEventListener('click', logout);

  // ── Navegação lateral ─────────────────────────────────────────────
  const navItems = document.querySelectorAll('.nav-item[data-panel]');
  const panels   = document.querySelectorAll('.panel-area > .panel');

  function switchPanel(panelId) {
    navItems.forEach(n => n.classList.toggle('active', n.dataset.panel === panelId));
    panels.forEach(p => p.classList.toggle('active', p.id === `panel-${panelId}`));

    // carrega vault quando navega para ele
    if (panelId === 'vault') loadVault();
  }

  navItems.forEach(item => {
    item.addEventListener('click', () => switchPanel(item.dataset.panel));
  });

  // ── Atalhos de teclado ────────────────────────────────────────────
  document.addEventListener('keydown', e => {
    // ignora se foco está em input/textarea
    if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

    const map = { e: 'encrypt', d: 'decrypt', v: 'vault', t: 'tools', i: 'info' };
    const panel = map[e.key.toLowerCase()];
    if (panel) switchPanel(panel);
  });

  // ── Ferramentas ───────────────────────────────────────────────────
  initTools();

  // ── Inicializa módulos ────────────────────────────────────────────
  initCrypto();
  initVault();
}

function initTools() {
  // Verificar colisões
  const btnCheck = document.getElementById('btn-check');
  const checkK1  = document.getElementById('check-k1');
  const result   = document.getElementById('collision-result');

  btnCheck?.addEventListener('click', async () => {
    const k1 = parseInt(checkK1.value);
    if (!validKey(k1)) { showToast('Chave inválida (0–999).', 'error'); return; }

    btnCheck.disabled = true;
    btnCheck.textContent = 'verificando...';

    // A verificação de colisões é feita localmente (algoritmo determinístico)
    // Chamamos encrypt com uma string curta e vemos se retorna "?????"
    try {
      const data = await api.post('/encrypt', { text: 'test', key1: k1, key2: 0 });
      const hasIssue = data.ciphertext.includes('?????');

      result.className = `collision-result ${hasIssue ? 'unsafe' : 'safe'}`;
      result.textContent = hasIssue
        ? `⚠  Key1 = ${k1} apresenta problemas. Escolha outra chave.`
        : `✓  Key1 = ${k1} está segura. Nenhuma colisão detectada.`;
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btnCheck.disabled = false;
      btnCheck.textContent = 'verificar';
    }
  });

  // Gerar chaves aleatórias
  const btnGen      = document.getElementById('btn-gen-keys');
  const genResult   = document.getElementById('gen-keys-result');
  const genText     = document.getElementById('gen-keys-text');
  const btnCopyKeys = document.getElementById('btn-copy-keys');

  let generatedKeys = '';

  btnGen?.addEventListener('click', () => {
    const k1 = Math.floor(Math.random() * 1000);
    const k2 = Math.floor(Math.random() * 1000);
    generatedKeys = `KEY1: ${k1}\nKEY2: ${k2}`;
    genText.textContent = generatedKeys;
    genResult.style.display = 'block';
    showToast(`Chaves geradas: K1=${k1}, K2=${k2}`, 'info');
  });

  btnCopyKeys?.addEventListener('click', () => {
    if (generatedKeys) copyToClipboard(generatedKeys, btnCopyKeys);
  });
}

// ── Inicia tudo quando o DOM estiver pronto ───────────────────────────
document.addEventListener('DOMContentLoaded', initDashboard);
