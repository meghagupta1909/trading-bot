import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// Request logger
api.interceptors.request.use(
  (config) => {
    console.debug(`[API] → ${config.method?.toUpperCase()} ${config.url}`, config.data)
    return config
  },
  (error) => Promise.reject(error),
)

// Response logger + error normaliser
api.interceptors.response.use(
  (response) => {
    console.debug(`[API] ← ${response.status} ${response.config.url}`, response.data)
    return response
  },
  (error) => {
    const message =
      error.response?.data?.message ||
      error.response?.data?.detail ||
      error.message ||
      'Unknown error'
    console.error(`[API] Error: ${message}`, error.response?.data)
    return Promise.reject({ ...error, userMessage: message })
  },
)

// ── Orders ─────────────────────────────────────────────────────────────────────

export const placeOrder = async (orderData) => {
  const { data } = await api.post('/api/orders/place', orderData)
  return data
}

// ── Health ─────────────────────────────────────────────────────────────────────

export const getHealth = async () => {
  const { data } = await api.get('/api/health')
  return data
}

// ── Logs ───────────────────────────────────────────────────────────────────────

export const getRecentLogs = async (logFile = 'trading_bot.log', lines = 100) => {
  const { data } = await api.get('/api/logs/recent', {
    params: { log_file: logFile, lines },
  })
  return data
}

export const getLogFiles = async () => {
  const { data } = await api.get('/api/logs/files')
  return data
}

export default api