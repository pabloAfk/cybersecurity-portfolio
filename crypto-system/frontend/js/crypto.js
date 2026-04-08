// crypto.js — Funções auxiliares de criptografia
// Este arquivo pode ser importado por outros módulos se necessário

// Validação de chaves
export function validKey(key) {
  return !isNaN(key) && key >= 0 && key <= 999;
}

// Normalização de texto para exibição
export function truncateText(text, maxLength = 100) {
  if (!text) return '';
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

// Geração de chaves aleatórias
export function generateRandomKeys() {
  return {
    key1: Math.floor(Math.random() * 1000),
    key2: Math.floor(Math.random() * 1000)
  };
}
