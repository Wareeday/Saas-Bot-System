import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authApi = {
  login: (credentials) => api.post('/api/auth/token', credentials),
  register: (data) => api.post('/api/auth/register', data),
  me: () => api.get('/api/auth/me'),
}

export const tasksApi = {
  list: (params) => api.get('/api/tasks', { params }),
  get: (id) => api.get(`/api/tasks/${id}`),
  create: (data) => api.post('/api/tasks', data),
  update: (id, data) => api.patch(`/api/tasks/${id}`, data),
  delete: (id) => api.delete(`/api/tasks/${id}`),
  run: (id) => api.post(`/api/tasks/${id}/run`),
  cancel: (id) => api.post(`/api/tasks/${id}/cancel`),
  stats: () => api.get('/api/tasks/stats'),
}

export const accountsApi = {
  list: (params) => api.get('/api/accounts', { params }),
  get: (id) => api.get(`/api/accounts/${id}`),
  create: (data) => api.post('/api/accounts', data),
  update: (id, data) => api.patch(`/api/accounts/${id}`, data),
  delete: (id) => api.delete(`/api/accounts/${id}`),
}
