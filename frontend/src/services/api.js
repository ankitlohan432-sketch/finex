import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const api = axios.create({ baseURL: BASE_URL })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(res => res, err => Promise.reject(err))

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  verifyOtp: (data) => api.post('/auth/verify-otp', data),
  resendOtp: (data) => api.post('/auth/resend-otp', data),
  login: (data) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
}
export const userAPI = {
  getMe: () => api.get('/users/me'),
  updateMe: (data) => api.put('/users/me', data),
  getStats: () => api.get('/users/stats'),
}
export const portfolioAPI = {
  get: () => api.get('/portfolio/'),
  getSummary: () => api.get('/portfolio/summary'),
  getOverview: () => api.get('/portfolio/overview'),
}
export const transactionAPI = {
  getAll: () => api.get('/transactions/'),
  getOne: (id) => api.get(`/transactions/${id}`),
  create: (data) => api.post('/transactions/', data),
  getStats: () => api.get('/transactions/summary/stats'),
}
export const stockAPI = {
  getPrice: (symbol) => api.get(`/stocks/price/${symbol}`),
  getHistory: (symbol) => api.get(`/stocks/history/${symbol}`),
  getTopMovers: () => api.get('/stocks/top-movers'),
  getIndices: () => api.get('/stocks/indices'),
}
export const analyticsAPI = {
  getDashboard: () => api.get('/analytics/dashboard'),
  getUsersGrowth: () => api.get('/analytics/users-growth'),
  getTrafficOverview: () => api.get('/analytics/traffic-overview'),
  log: (data) => api.post('/analytics/log', data),
}
export const adminAPI = {
  getUsers: () => api.get('/admin/users'),
  getPlatformStats: () => api.get('/admin/stats/platform'),
  suspendUser: (id) => api.post(`/admin/users/${id}/suspend`),
  activateUser: (id) => api.post(`/admin/users/${id}/activate`),
}
export const cardsAPI = {
  getAll: () => api.get('/cards/'),
  add: (data) => api.post('/cards/', data),
  remove: (id) => api.delete(`/cards/${id}`),
}
export const chatAPI = {
  ask: (data) => api.post('/chat/ask', data),
  getSuggestions: () => api.get('/chat/suggestions'),
}

// Live Market APIs (Binance, NSE, BSE)
export const cryptoAPI = {
  list:    ()                                       => api.get('/live/crypto/list'),
  tickers: (page=0, size=10)                        => api.get(`/live/crypto/tickers?page=${page}&page_size=${size}`),
  ticker:  (binanceSymbol)                          => api.get(`/live/crypto/ticker/${binanceSymbol}`),
  klines:  (binanceSymbol, interval='1d', limit=60) => api.get(`/live/crypto/klines/${binanceSymbol}?interval=${interval}&limit=${limit}`),
}

export const nseAPI = {
  list:    ()                      => api.get('/live/nse/list'),
  tickers: (page=0, size=10)       => api.get(`/live/nse/tickers?page=${page}&page_size=${size}`),
  ticker:  (symbol)                => api.get(`/live/nse/ticker/${symbol}`),
  klines:  (symbol, interval='1d') => api.get(`/live/nse/klines/${symbol}?interval=${interval}`),
  indices: ()                      => api.get('/live/nse/indices'),
}

export const bseAPI = {
  list:    ()                      => api.get('/live/bse/list'),
  tickers: (page=0, size=10)       => api.get(`/live/bse/tickers?page=${page}&page_size=${size}`),
  ticker:  (symbol)                => api.get(`/live/bse/ticker/${symbol}`),
  klines:  (symbol, interval='1d') => api.get(`/live/bse/klines/${symbol}?interval=${interval}`),
}

export default api
