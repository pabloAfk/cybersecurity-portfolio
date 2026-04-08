// auth.js — Autenticação: login, registro, logout, verificação de sessão
import api from './api.js';

// ── Verifica se está autenticado (para redirecionar) ──────────────────
async function checkAuth() {
  try {
    const response = await api.get('/me');
    return response.data;
  } catch {
    return null;
  }
}

// ── Redireciona se não autenticado ───────────────────────────────────
async function requireAuth() {
  const user = await checkAuth();
  if (!user) {
    window.location.href = '/index.html';
    return null;
  }
  return user;
}

// ── Redireciona se já autenticado (página de login) ───────────────────
async function redirectIfAuth() {
  const user = await checkAuth();
  if (user) window.location.href = '/dashboard.html';
}

// ══════════════════════════════════════════════════════════════════════
//  Página de login/registro (index.html)
// ══════════════════════════════════════════════════════════════════════
function initAuthPage() {
  // Só roda se as tabs existirem
  const tabs = document.querySelectorAll('.auth-tab');
  if (!tabs.length) return;

  // Redireciona se já logado
  redirectIfAuth();

  // ── Tabs ──────────────────────────────────────────────────────────
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById(`form-${tab.dataset.tab}`).classList.add('active');
      clearMessages();
    });
  });

  function clearMessages() {
    ['login-msg', 'reg-msg'].forEach(id => {
      const el = document.getElementById(id);
      if (el) { el.className = 'auth-msg'; el.textContent = ''; }
    });
  }

  function showMsg(elId, text, type) {
    const el = document.getElementById(elId);
    if (!el) return;
    el.textContent = text;
    el.className = `auth-msg ${type}`;
  }

  function setLoading(btnId, loading) {
    const btn = document.getElementById(btnId);
    if (!btn) return;
    btn.disabled = loading;
    btn.textContent = loading ? 'AGUARDE...' : (btnId === 'btn-login' ? 'AUTENTICAR →' : 'CRIAR CONTA →');
  }

  // ── Login ─────────────────────────────────────────────────────────
  const formLogin = document.getElementById('form-login');
  if (formLogin) {
    formLogin.addEventListener('submit', async e => {
      e.preventDefault();
      clearMessages();

      const username = document.getElementById('login-user').value.trim();
      const password = document.getElementById('login-pass').value;

      if (!username || !password) {
        showMsg('login-msg', 'Preencha todos os campos.', 'error');
        return;
      }

      setLoading('btn-login', true);
      try {
        const response = await api.post('/login', { username, password });
        if (response.data.success) {
          showMsg('login-msg', 'Autenticado! Redirecionando...', 'success');
          setTimeout(() => { window.location.href = '/dashboard.html'; }, 600);
        }
      } catch (err) {
        const msg = err.response?.data?.detail || 'Erro ao fazer login';
        showMsg('login-msg', msg, 'error');
        setLoading('btn-login', false);
      }
    });
  }

  // ── Registro ──────────────────────────────────────────────────────
  const formRegister = document.getElementById('form-register');
  if (formRegister) {
    formRegister.addEventListener('submit', async e => {
      e.preventDefault();
      clearMessages();

      const username = document.getElementById('reg-user').value.trim();
      const password = document.getElementById('reg-pass').value;
      const password2 = document.getElementById('reg-pass2').value;

      if (!username || !password || !password2) {
        showMsg('reg-msg', 'Preencha todos os campos.', 'error');
        return;
      }
      if (username.length < 3) {
        showMsg('reg-msg', 'Usuário deve ter pelo menos 3 caracteres.', 'error');
        return;
      }
      if (password.length < 6) {
        showMsg('reg-msg', 'Senha deve ter pelo menos 6 caracteres.', 'error');
        return;
      }
      if (password !== password2) {
        showMsg('reg-msg', 'As senhas não coincidem.', 'error');
        return;
      }

      setLoading('btn-register', true);
      try {
        const response = await api.post('/register', { username, password });
        if (response.data.success) {
          showMsg('reg-msg', 'Conta criada! Redirecionando...', 'success');
          setTimeout(() => { window.location.href = '/dashboard.html'; }, 600);
        }
      } catch (err) {
        const msg = err.response?.data?.detail || 'Erro ao registrar';
        showMsg('reg-msg', msg, 'error');
        setLoading('btn-register', false);
      }
    });
  }
}

// ── Logout (chamado pelo dashboard) ───────────────────────────────────
async function logout() {
  try {
    await api.post('/logout');
  } finally {
    window.location.href = '/index.html';
  }
}

// Exporta funções para uso em outros módulos
export { checkAuth, requireAuth, redirectIfAuth, logout };

// ── Init ──────────────────────────────────────────────────────────────
initAuthPage();
