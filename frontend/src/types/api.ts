// 📝 API TYPES - Complete Type Definitions per Railway Backend

// ===== CHAT TYPES =====
export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  sources?: Source[]
  error?: string
}

export interface Source {
  source: string
  content?: string
}

export interface ChatRequest {
  message: string
  user_id: string
  conversation_id?: string | null
}

export interface ChatResponse {
  message: string
  suggested_actions: string[]
  conversation_id: string
  sources: Source[]
}

// ===== INTENT TYPES =====
export interface Intent {
  type: string
  confidence: number
  entities: Record<string, any>
}

// ===== HEALTH CHECK TYPES =====
export interface HealthComponent {
  status: 'ok' | 'error' | 'ready' | 'not_ready'
  details: string
}

export interface HealthResponse {
  status: 'online' | 'degraded' | 'offline'
  timestamp: string
  deployment: string
  components: {
    database_connection: HealthComponent
    rag_system: HealthComponent
  }
  version: string
}

// ===== DASHBOARD TYPES =====
export interface SystemStatus {
  status: string
  uptime: string
  version: string
  deployment: string
}

export interface ConversationStats {
  total_conversations: number
  today_conversations: number
  total_messages: number
  avg_messages_per_conversation: number
}

export interface PerformanceStats {
  cache_items: number
  cache_hit_rate: number
  avg_response_time_ms: number
  total_queries_processed: number
}

export interface ActivityChartData {
  hour: string
  count: number
}

export interface SystemHealthComponents {
  database_status: string
  rag_status: string
  cache_status: string
  memory_usage_mb: number
  documents_indexed: number
  files_indexed: number
}

export interface DashboardData {
  timestamp: string
  system_status: SystemStatus
  conversation_stats: ConversationStats
  performance_stats: PerformanceStats
  activity_chart: ActivityChartData[]
  system_health_components: SystemHealthComponents
}

export interface DashboardResponse {
  status: 'success' | 'error'
  data: DashboardData
  error?: string
}

// ===== CACHE TYPES =====
export interface CacheResponse {
  status: 'success' | 'error'
  timestamp: string
  message: string
  deployment: string
}

// ===== ERROR TYPES =====
export interface ApiError {
  detail: string
  status_code?: number
}

// ===== UTILITY TYPES =====
export type ApiResponse<T> = {
  success: true
  data: T
} | {
  success: false
  error: string
}

// ===== RAILWAY API ENDPOINTS =====
export const API_ENDPOINTS = {
  CHAT: '/api/chat',
  HEALTH: '/api/health',
  DASHBOARD_DATA: '/api/dashboard/data',
  CACHE_CLEAR: '/api/cache/clear',
  DASHBOARD: '/dashboard'
} as const

// ===== API CLIENT HELPER =====
export class ApiClient {
  private baseUrl: string

  constructor(baseUrl = '') {
    this.baseUrl = baseUrl
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}${API_ENDPOINTS.CHAT}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  async getHealth(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}${API_ENDPOINTS.HEALTH}`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  async getDashboardData(): Promise<DashboardResponse> {
    const response = await fetch(`${this.baseUrl}${API_ENDPOINTS.DASHBOARD_DATA}`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  async clearCache(): Promise<CacheResponse> {
    const response = await fetch(`${this.baseUrl}${API_ENDPOINTS.CACHE_CLEAR}`, {
      method: 'POST'
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }
}

// ===== DEFAULT API CLIENT =====
export const apiClient = new ApiClient()

// ===== TYPE GUARDS =====
export const isApiError = (response: any): response is ApiError => {
  return response && typeof response.detail === 'string'
}

export const isValidMessage = (message: any): message is Message => {
  return message && 
         typeof message.id === 'string' &&
         typeof message.content === 'string' &&
         ['user', 'assistant'].includes(message.role) &&
         message.timestamp instanceof Date
}

// ===== MOCK DATA per Development =====
export const MOCK_MESSAGES: Message[] = [
  {
    id: '1',
    role: 'user',
    content: 'Cosa copre esattamente la polizza RCA?',
    timestamp: new Date()
  },
  {
    id: '2',
    role: 'assistant',
    content: 'La RCA (Responsabilità Civile Auto) è obbligatoria per tutti i veicoli. Copre i danni causati a terzi con massimale di €6.000.000. Include copertura per danni a persone e cose, assistenza stradale 24/7...',
    timestamp: new Date(),
    sources: [
      { source: 'polizza_auto.txt', content: 'Informazioni RCA...' },
      { source: 'faq_polizze_auto_casa.md', content: 'FAQ RCA...' }
    ]
  }
]

export const MOCK_DASHBOARD_DATA: DashboardData = {
  timestamp: new Date().toISOString(),
  system_status: {
    status: 'online',
    uptime: '2g 14:30:45',
    version: '2.0.0-custom-rag',
    deployment: 'Railway - Custom RAG'
  },
  conversation_stats: {
    total_conversations: 156,
    today_conversations: 23,
    total_messages: 892,
    avg_messages_per_conversation: 5.7
  },
  performance_stats: {
    cache_items: 45,
    cache_hit_rate: 85.5,
    avg_response_time_ms: 2150,
    total_queries_processed: 892
  },
  activity_chart: [
    { hour: '2025-05-29T10:00:00Z', count: 12 },
    { hour: '2025-05-29T11:00:00Z', count: 18 },
    { hour: '2025-05-29T12:00:00Z', count: 25 }
  ],
  system_health_components: {
    database_status: 'ok',
    rag_status: 'initialized',
    cache_status: 'ok',
    memory_usage_mb: 245.7,
    documents_indexed: 19,
    files_indexed: 4
  }
}