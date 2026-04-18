import axios from 'axios';

const API_URL = 'http://localhost:8000';

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

export const auth = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  signup: (username, email, password) => api.post('/auth/signup', { username, email, password }),
  changePassword: (old_password, new_password) => api.post('/auth/change-password', { old_password, new_password }),
};

export const profile = {
  get: () => api.get('/profile'),
  update: (new_username, new_email) => api.put('/profile', { new_username, new_email }),
};

export const documents = {
  list: () => api.get('/documents'),
  delete: (doc) => api.delete(`/documents/${doc}`),
};

export const rag = {
  upload: (formData) => api.post('/rag/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  query: (question, top_k, selected_documents) => api.post('/rag/query', { question, top_k, selected_documents }),
};

export const history = {
  get: () => api.get('/history'),
};

export default api;
