// frontend/src/config/api.ts
// 🔧 CONFIGURAZIONE API - Development e Production

// Determina automaticamente l'ambiente
const isDevelopment = import.meta.env.DEV
const isProduction = import.meta.env.PROD

// URLs per diversi ambienti
const API_URLS = {
  development: 'http://localhost:8000', // Backend locale per testing
  production: 'https://loving-comfort-production.up.railway.app', // Railway backend
  local_backend: 'http://localhost:8000', // Per testing locale completo
  railway_backend: 'https://loving-comfort-production.up.railway.app' // Per testing con Railway
}

// Configurazione attiva (modificabile per testing)
export const API_CONFIG = {
  // 🎯 CAMBIA QUESTO PER TESTARE DIVERSI BACKEND
  baseURL: isDevelopment 
    ? API_URLS.railway_backend  // Punta subito a Railway per testing
    : API_URLS.production,
  
  timeout: 30000, // 30 secondi timeout
  retryAttempts: 3,
  retryDelay: 1000, // 1 secondo tra retry
  
  // Headers di default
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  
  // Endpoints
  endpoints: {
    chat: '/api/chat',
    health: '/api/health',
    dashboard: '/api/dashboard/data',
    clearCache: '/api/cache/clear'
  }
}

// 🔍 HELPER FUNCTIONS per debugging e testing

export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.baseURL}${endpoint}`
}

export const logApiCall = (method: string, url: string, data?: any) => {
  if (isDevelopment) {
    console.group(`🔗 API Call: ${method} ${url}`)
    console.log('⚙️ Config:', { baseURL: API_CONFIG.baseURL })
    if (data) console.log('📤 Request Data:', data)
    console.groupEnd()
  }
}

export const logApiResponse = (url: string, response: any, error?: any) => {
  if (isDevelopment) {
    console.group(`📥 API Response: ${url}`)
    if (error) {
      console.error('❌ Error:', error)
    } else {
      console.log('✅ Success:', response)
    }
    console.groupEnd()
  }
}

// 🎛️ SWITCH BACKEND per testing rapido
export const switchToLocalBackend = () => {
  API_CONFIG.baseURL = API_URLS.local_backend
  console.log('🔄 Switched to LOCAL backend:', API_CONFIG.baseURL)
}

export const switchToRailwayBackend = () => {
  API_CONFIG.baseURL = API_URLS.railway_backend
  console.log('🔄 Switched to RAILWAY backend:', API_CONFIG.baseURL)
}

// 🏥 HEALTH CHECK per testare connessione
export const testConnection = async (): Promise<boolean> => {
  try {
    logApiCall('GET', getApiUrl(API_CONFIG.endpoints.health))
    
    const response = await fetch(getApiUrl(API_CONFIG.endpoints.health), {
      method: 'GET',
      headers: API_CONFIG.headers,
      signal: AbortSignal.timeout(5000) // 5s timeout per health check
    })
    
    const data = await response.json()
    logApiResponse(API_CONFIG.endpoints.health, data)
    
    return response.ok && data.status === 'online'
  } catch (error) {
    logApiResponse(API_CONFIG.endpoints.health, null, error)
    return false
  }
}

// 🔧 ENVIRONMENT INFO per debugging
export const getEnvironmentInfo = () => {
  return {
    isDevelopment,
    isProduction,
    currentBackend: API_CONFIG.baseURL,
    availableBackends: API_URLS,
    endpoints: Object.entries(API_CONFIG.endpoints).map(([name, path]) => ({
      name,
      path,
      fullUrl: getApiUrl(path)
    }))
  }
}

// Auto-log configurazione in development
if (isDevelopment) {
  console.group('🔧 API Configuration Initialized')
  console.table(getEnvironmentInfo())
  console.groupEnd()
}