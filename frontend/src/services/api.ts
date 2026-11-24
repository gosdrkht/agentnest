import axios from 'axios';

const API_URL =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? 'http://localhost:8000' : 'https://agentnest-production.up.railway.app');

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      const isAuthRoute =
        window.location.pathname === '/login' || window.location.pathname === '/signup';
      if (!isAuthRoute) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;