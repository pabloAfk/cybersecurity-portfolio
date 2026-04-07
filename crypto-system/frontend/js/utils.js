// utils.js — Helpers compartilhados

// ── Toast notifications ───────────────────────────────────────────────
function showToast(msg, type = 'success', duration = 3000) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = msg;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity 0.3s';
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ── Clipboard ─────────────────────────────────────────────────────────
async function copyToClipboard(text, feedbackEl = null) {
  try {
    await navigator.clipboard.writeText(text);
    if (feedbackEl) {
      const original = feedbackEl.textContent;
      feedbackEl.textContent = 'copiado!';
      feedbackEl.style.color = 'var(--green)';
      setTimeout(() => {
        feedbackEl.textContent = original;
        feedbackEl.style.color = '';
      }, 1500);
    }
    showToast('Copiado para a área de transferência', 'success');
    return true;
  } catch {
    showToast('Não foi possível copiar automaticamente', 'error');
    return false;
  }
}

// ── Validação de chave ────────────────────────────────────────────────
function validKey(val) {
  const n = Number(val);
  return Number.isInteger(n) && n >= 0 && n <= 999;
}

// ── Formatar data ─────────────────────────────────────────────────────
function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString('pt-BR') + ' ' +
         d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

// ── Truncar texto ─────────────────────────────────────────────────────
function truncate(str, max = 80) {
  return str.length > max ? str.slice(0, max) + '…' : str;
}

// ── Mostra/esconde spinner de processamento ───────────────────────────
function setProcessing(elId, visible) {
  const el = document.getElementById(elId);
  if (el) el.classList.toggle('visible', visible);
}
