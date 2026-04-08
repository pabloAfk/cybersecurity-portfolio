// api.js - Configuração do Axios
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true,  // ESSENCIAL para enviar cookies!
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token (redundante com cookie, mas mantido)
api.interceptors.request.use(
  (config) => {
    // O cookie é enviado automaticamente com withCredentials: true
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para tratar erros de autenticação
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      // Redireciona para index.html (não /login)
      if (!window.location.pathname.includes('index.html') && 
          !window.location.pathname.includes('/')) {
        window.location.href = '/index.html';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
