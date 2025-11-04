import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8888',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token se necessário
api.interceptors.request.use((config) => {
  // Adicionar token aqui quando implementar autenticação
  // const token = localStorage.getItem('token');
  // if (token) {
  //   config.headers.Authorization = `Bearer ${token}`;
  // }
  return config;
});

export default api;
