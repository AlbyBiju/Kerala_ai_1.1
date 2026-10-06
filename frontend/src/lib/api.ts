import axios from 'axios'

const getBaseUrl = () => {
  if (import.meta.env.VITE_API_BASE_URL) return import.meta.env.VITE_API_BASE_URL
  if (typeof window !== 'undefined' && window.location.hostname === '127.0.0.1') {
    return 'http://127.0.0.1:8000'
  }
  return 'http://localhost:8000'
}

const api = axios.create({
  baseURL: getBaseUrl(),
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('eg_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !window.location.pathname.startsWith('/login')) {
      localStorage.removeItem('eg_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default api
