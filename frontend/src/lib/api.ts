import axios from 'axios';

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8888',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token automaticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para detectar token expirado (401) e fazer logout automático
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Se receber 401 (Unauthorized), significa que o token expirou
    if (error.response?.status === 401) {
      // Verificar se não está na página de login para evitar loop
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        // Limpar dados locais
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        
        // Mostrar mensagem
        alert('Sessão expirada! Faça login novamente.');
        
        // Redirecionar para login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
