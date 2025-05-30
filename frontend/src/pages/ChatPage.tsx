// 💬 CHATPAGE ENTERPRISE - LAYOUT FIXED COMPLETE
import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

// Icons
import { 
  PaperAirplaneIcon,
  ChartBarIcon,
  SparklesIcon,
  ExclamationTriangleIcon,
  WifiIcon,
  NoSymbolIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'

// Types
interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  sources?: Array<{
    source: string
    content?: string
  }>
  error?: string
}

interface ChatRequest {
  message: string
  user_id: string
  conversation_id?: string | null
}

interface ChatResponse {
  message: string
  suggested_actions: string[]
  conversation_id: string
  sources: Array<{
    source: string
    content?: string
  }>
}

// 🔗 INLINE API CLIENT (using our tested functions)
const apiCall = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    console.log('💬 Sending message:', request.message.substring(0, 50) + '...')
    
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`HTTP ${response.status}: ${errorText}`)
    }

    const data = await response.json()
    console.log('✅ Response received:', data.message.substring(0, 50) + '...')
    
    return data
  },

  async getHealth(): Promise<any> {
    const response = await fetch('/api/health', {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    return response.json()
  }
}

export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'online' | 'offline' | 'error' | 'checking'>('checking')
  const [lastError, setLastError] = useState<string | null>(null)
  const [backendInfo, setBackendInfo] = useState<any>(null)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // Quick Actions - ENHANCED CON RAILWAY
  const quickActions = [
    {
      id: 'rca',
      icon: '🚗',
      title: 'Polizza RCA',
      description: 'Coperture obbligatorie',
      message: 'Cosa copre esattamente la polizza RCA? Quali sono i massimali?',
      color: 'from-blue-500 to-blue-600',
      shadowColor: 'shadow-blue-500/25'
    },
    {
      id: 'sinistro',
      icon: '⚠️',
      title: 'Gestione Sinistro',
      description: 'Procedure emergenze',
      message: 'Come devo comportarmi in caso di sinistro stradale? Cosa devo fare?',
      color: 'from-amber-500 to-orange-500',
      shadowColor: 'shadow-orange-500/25'
    },
    {
      id: 'casa',
      icon: '🏠',
      title: 'Polizza Casa',
      description: 'Protezione abitazione',
      message: 'Come funziona la polizza casa? Cosa copre per incendio e furto?',
      color: 'from-emerald-500 to-teal-600',
      shadowColor: 'shadow-emerald-500/25'
    },
    {
      id: 'preventivo',
      icon: '💰',
      title: 'Preventivo',
      description: 'Calcolo premio',
      message: 'Come viene calcolato il prezzo di una polizza auto? Quali fattori influenzano il costo?',
      color: 'from-purple-500 to-violet-600',
      shadowColor: 'shadow-purple-500/25'
    }
  ]

  // Quick Suggestions - ENHANCED
  const quickSuggestions = [
    { text: 'Differenza tra RCA e Kasko', icon: '🚗' },
    { text: 'Procedura CID constatazione amichevole', icon: '📋' },
    { text: 'Assistenza stradale 24/7', icon: '🛠️' },
    { text: 'Copertura eventi naturali', icon: '🌪️' }
  ]

  // System Features - REAL-TIME STATUS
  const systemFeatures = [
    { icon: '🧠', text: 'RAG System (Custom)', active: connectionStatus === 'online' },
    { icon: '🔍', text: 'Document Retrieval', active: connectionStatus === 'online' },
    { icon: '💬', text: 'Conversation Management', active: connectionStatus === 'online' },
    { icon: '📚', text: 'Knowledge Base (19 chunks)', active: connectionStatus === 'online' }
  ]

  // Check connection status on mount
  useEffect(() => {
    checkConnectionStatus()
    // Check periodically
    const interval = setInterval(checkConnectionStatus, 30000) // every 30s
    return () => clearInterval(interval)
  }, [])

  // Force scroll reset on mount
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = 0
      window.scrollTo(0, 0)
    }
  }, [])

  const checkConnectionStatus = async () => {
    setConnectionStatus('checking')
    try {
      const health = await apiCall.getHealth()
      setConnectionStatus('online')
      setBackendInfo(health)
      setLastError(null)
      console.log('✅ Backend health:', health)
    } catch (error) {
      setConnectionStatus('error')
      setLastError(error instanceof Error ? error.message : 'Connection failed')
      console.error('❌ Backend health check failed:', error)
    }
  }

  // Auto scroll
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  // Handle input change con auto-resize
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value)
    
    const textarea = e.target
    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
  }

  // Send message - ENHANCED RAILWAY INTEGRATION
  const sendMessage = async (messageText?: string) => {
    const message = messageText || inputValue.trim()
    if (!message || isLoading || connectionStatus !== 'online') return

    setInputValue('')
    setIsLoading(true)
    setLastError(null)
    
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setIsTyping(true)

    try {
      console.log('🚀 Sending to Railway:', { message, conversationId })
      
      const chatRequest: ChatRequest = {
        message,
        user_id: 'chat_user',
        conversation_id: conversationId
      }

      const response = await apiCall.sendMessage(chatRequest)

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        sources: response.sources || []
      }

      setMessages(prev => [...prev, botMessage])
      
      if (response.conversation_id) {
        setConversationId(response.conversation_id)
        console.log('💬 Conversation ID:', response.conversation_id)
      }

      console.log('📚 Sources:', response.sources)

    } catch (error) {
      console.error('❌ Error sending message:', error)
      
      const errorMessage = error instanceof Error ? error.message : 'Errore di connessione'
      setLastError(errorMessage)
      
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Mi dispiace, si è verificato un errore: ${errorMessage}. Riprova più tardi.`,
        timestamp: new Date(),
        error: errorMessage
      }
      setMessages(prev => [...prev, errorResponse])
      
      // Check connection after error
      setTimeout(checkConnectionStatus, 1000)
    } finally {
      setIsTyping(false)
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // Connection status indicator
  const getConnectionIndicator = () => {
    switch (connectionStatus) {
      case 'online':
        return { icon: CheckCircleIcon, color: 'text-green-400', text: 'Online', bgColor: 'bg-green-500/20' }
      case 'offline':
        return { icon: NoSymbolIcon, color: 'text-red-400', text: 'Offline', bgColor: 'bg-red-500/20' }
      case 'error':
        return { icon: ExclamationTriangleIcon, color: 'text-orange-400', text: 'Errore', bgColor: 'bg-orange-500/20' }
      case 'checking':
        return { icon: WifiIcon, color: 'text-yellow-400', text: 'Verifica...', bgColor: 'bg-yellow-500/20' }
      default:
        return { icon: WifiIcon, color: 'text-gray-400', text: 'Sconosciuto', bgColor: 'bg-gray-500/20' }
    }
  }

  const connectionIndicator = getConnectionIndicator()

  // Format timestamp
  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('it-IT', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 relative" ref={containerRef}>
      
      {/* ANIMATED BACKGROUND */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900/50 via-blue-900/30 to-slate-800/50" />
        {/* Floating bubbles */}
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full bg-white/5 backdrop-blur-sm"
            style={{
              width: Math.random() * 100 + 50,
              height: Math.random() * 100 + 50,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -30, 0],
              x: [0, Math.random() * 20 - 10, 0],
              opacity: [0.3, 0.6, 0.3],
            }}
            transition={{
              duration: 8 + Math.random() * 4,
              repeat: Infinity,
              ease: "easeInOut",
              delay: Math.random() * 2
            }}
          />
        ))}
      </div>

      {/* MAIN CONTAINER - FIXED */}
      <div className="relative z-10 flex min-h-screen w-full px-4 py-4">
        
        {/* ============= LEFT PANEL - INFO & CONTROLS ============= */}
        <motion.div 
          className="w-1/2 flex flex-col min-h-screen pr-2"
          initial={{ x: -50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          
          {/* HEADER CON CONNECTION STATUS */}
          <motion.div 
            className="flex items-center justify-between p-4 bg-slate-900/20 backdrop-blur-sm border-b border-white/10 rounded-t-lg"
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            <div className="flex items-center gap-3">
              <motion.div 
                className="w-12 h-12 bg-gradient-to-br from-green-400 to-green-500 rounded-lg flex items-center justify-center text-white text-lg shadow-lg"
                whileHover={{ scale: 1.05 }}
                animate={connectionStatus === 'online' ? {
                  boxShadow: ['0 0 0 0 rgba(34, 197, 94, 0.7)', '0 0 0 10px rgba(34, 197, 94, 0)']
                } : {}}
                transition={{ duration: 2, repeat: Infinity }}
              >
                🛡️
              </motion.div>
              <div>
                <h1 className="text-xl font-bold text-white flex items-center gap-2">
                  AssistentIA Pro
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                  >
                    <SparklesIcon className="w-4 h-4 text-yellow-400" />
                  </motion.div>
                </h1>
                <p className="text-white/60 text-xs">RAG System • Railway Backend</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* Connection Status */}
              <motion.div 
                className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${connectionIndicator.bgColor} border border-white/20`}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.3 }}
              >
                <connectionIndicator.icon className={`w-3 h-3 ${connectionIndicator.color}`} />
                <span className={`text-xs font-medium ${connectionIndicator.color}`}>
                  {connectionIndicator.text}
                </span>
              </motion.div>

              <motion.button
                className="px-3 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg flex items-center gap-2 shadow-lg hover:shadow-xl transition-all text-xs font-medium"
                whileHover={{ scale: 1.02, y: -1 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => window.open('/dashboard', '_blank')}
              >
                <ChartBarIcon className="w-4 h-4" />
                Dashboard
              </motion.button>
            </div>
          </motion.div>

          {/* CONTENUTO SCROLLABILE - FIXED */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
            
            {/* CONNECTION INFO */}
            <motion.div 
              className={`bg-white/5 backdrop-blur-sm border rounded-lg p-3 ${
                connectionStatus === 'online' ? 'border-green-500/30' : 'border-orange-400/30'
              }`}
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.1 }}
            >
              <div className="flex items-center gap-2 mb-2">
                <connectionIndicator.icon className={`w-4 h-4 ${connectionIndicator.color}`} />
                <span className="text-white font-medium text-sm">
                  Railway Backend: {connectionIndicator.text}
                </span>
                {connectionStatus !== 'online' && (
                  <motion.button
                    onClick={checkConnectionStatus}
                    className="ml-auto text-xs bg-blue-500/20 hover:bg-blue-500/30 px-2 py-1 rounded text-blue-300 transition-colors"
                    whileTap={{ scale: 0.95 }}
                  >
                    Riconnetti
                  </motion.button>
                )}
              </div>
              
              {lastError && (
                <div className="text-red-300 text-xs mb-2">
                  ⚠️ {lastError}
                </div>
              )}
              
              {connectionStatus === 'online' && backendInfo && (
                <div className="text-white/50 text-xs space-y-1">
                  <div>✅ Status: {backendInfo.status}</div>
                  <div>🚄 Version: {backendInfo.version}</div>
                  <div>🏭 Deploy: {backendInfo.deployment}</div>
                  {conversationId && (
                    <div>💬 Conv ID: {conversationId.substring(0, 8)}...</div>
                  )}
                </div>
              )}
            </motion.div>
            
            {/* HEADER SECTION */}
            <motion.div 
              className="text-center"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <h2 className="text-lg font-bold text-white mb-1">
                Come posso aiutarti oggi?
              </h2>
              <p className="text-white/60 text-xs">
                {connectionStatus === 'online' 
                  ? 'Clicca su un\'opzione per domande immediate'
                  : 'Connessione al backend in corso...'}
              </p>
            </motion.div>
            
            {/* QUICK ACTIONS - ENHANCED */}
            <motion.div 
              className="grid gap-3"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              {quickActions.map((action, index) => (
                <motion.button
                  key={action.id}
                  className={`
                    relative p-3 rounded-lg bg-gradient-to-r ${action.color} 
                    text-white shadow-lg ${action.shadowColor} 
                    hover:shadow-xl transition-all text-left overflow-hidden group
                    border border-white/10
                    ${connectionStatus !== 'online' ? 'opacity-50 cursor-not-allowed' : ''}
                  `}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 + index * 0.05 }}
                  whileHover={connectionStatus === 'online' ? { y: -2, scale: 1.01 } : {}}
                  whileTap={connectionStatus === 'online' ? { scale: 0.98 } : {}}
                  onClick={() => connectionStatus === 'online' && sendMessage(action.message)}
                  disabled={connectionStatus !== 'online'}
                >
                  {/* Shine effect */}
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 -translate-x-full group-hover:translate-x-full"
                    transition={{ duration: 0.6 }}
                  />
                  
                  <div className="relative z-10 flex items-center gap-3">
                    <div className="text-xl group-hover:scale-105 transition-transform duration-300">
                      {action.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold text-sm mb-0.5 truncate">{action.title}</div>
                      <div className="text-white/90 text-xs truncate">{action.description}</div>
                    </div>
                    <div className="text-white/60 group-hover:text-white transition-colors text-sm">
                      →
                    </div>
                  </div>
                </motion.button>
              ))}
            </motion.div>

            {/* QUICK SUGGESTIONS */}
            <motion.div 
              className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.6 }}
            >
              <h3 className="text-white font-medium mb-2 text-sm text-center">
                💬 Oppure chiedimi direttamente:
              </h3>
              <div className="space-y-1">
                {quickSuggestions.map((suggestion, index) => (
                  <motion.button
                    key={index}
                    className={`w-full flex items-center gap-2 p-2 rounded-md bg-white/5 hover:bg-white/10 transition-colors text-left text-white/80 hover:text-white text-xs ${
                      connectionStatus !== 'online' ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                    whileHover={connectionStatus === 'online' ? { x: 2 } : {}}
                    onClick={() => connectionStatus === 'online' && sendMessage(suggestion.text)}
                    disabled={connectionStatus !== 'online'}
                  >
                    <span className="text-sm">{suggestion.icon}</span>
                    <span className="truncate">{suggestion.text}</span>
                  </motion.button>
                ))}
              </div>
            </motion.div>

            {/* SYSTEM FEATURES - REAL TIME STATUS */}
            <motion.div 
              className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.7 }}
            >
              <h3 className="text-blue-300 font-medium mb-2 text-sm">
                🛠️ Sistema Features:
              </h3>
              <div className="space-y-1">
                {systemFeatures.map((feature, index) => (
                  <motion.div
                    key={index}
                    className="flex items-center gap-2 text-white/80"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.8 + index * 0.05 }}
                  >
                    <span className="text-sm">{feature.icon}</span>
                    <span className="text-xs flex-1 truncate">{feature.text}</span>
                    <motion.div
                      className={`w-1.5 h-1.5 rounded-full ${
                        feature.active ? 'bg-green-400' : 'bg-gray-400'
                      }`}
                      animate={feature.active ? {
                        scale: [1, 1.2, 1], 
                        opacity: [1, 0.7, 1]
                      } : {}}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* FOOTER */}
            <motion.div 
              className="text-center text-white/40 text-xs py-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
            >
              © 2025 AssistentIA Pro • Connected to Railway Backend
            </motion.div>
          </div>
        </motion.div>

        {/* ============= RIGHT PANEL - CHAT INTERFACE ============= */}
        <motion.div 
          className="w-1/2 flex flex-col min-h-screen pl-2"
          initial={{ x: 50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          
          {/* CHAT HEADER */}
          <motion.div 
            className="bg-white/10 backdrop-blur-xl border border-white/20 border-b-0 rounded-t-lg p-3 shadow-lg"
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <div className="flex items-center gap-3">
              <motion.div 
                className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center text-white shadow-lg"
                animate={connectionStatus === 'online' ? { 
                  boxShadow: ['0 0 0 0 rgba(59, 130, 246, 0.5)', '0 0 0 6px rgba(59, 130, 246, 0)']
                } : {}}
                transition={{ duration: 3, repeat: Infinity }}
              >
                🤖
              </motion.div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="text-white font-semibold text-sm">AssistentIA Pro</h3>
                  <motion.div
                    className={`w-1.5 h-1.5 rounded-full ${
                      connectionStatus === 'online' ? 'bg-green-400' : 'bg-red-400'
                    }`}
                    animate={{ opacity: [1, 0.4, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                  <span className={`text-xs font-medium ${
                    connectionStatus === 'online' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {connectionIndicator.text}
                  </span>
                </div>
                <p className="text-white/60 text-xs">
                  {connectionStatus === 'online' 
                    ? 'Custom RAG System • 19 documenti assicurativi'
                    : 'Connessione al backend in corso...'}
                </p>
              </div>
            </div>
          </motion.div>

          {/* MESSAGES AREA - FIXED */}
          <div className="flex-1 bg-white/5 backdrop-blur-xl border border-white/10 border-t-0 border-b-0 overflow-hidden flex flex-col shadow-lg">
            <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
              
              {messages.length === 0 ? (
                <motion.div
                  className="text-center py-12"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.4 }}
                >
                  <motion.div
                    className="text-4xl mb-3"
                    animate={{
                      y: [0, -6, 0],
                      rotate: [0, 3, 0]
                    }}
                    transition={{
                      duration: 4,
                      repeat: Infinity,
                      ease: "easeInOut"
                    }}
                  >
                    💬
                  </motion.div>
                  
                  <h3 className="text-white text-lg font-bold mb-2">
                    {connectionStatus === 'online' 
                      ? 'Inizia una conversazione'
                      : 'Connessione in corso...'}
                  </h3>
                  <p className="text-white/60 text-sm max-w-sm mx-auto leading-relaxed">
                    {connectionStatus === 'online'
                      ? 'Usa le azioni rapide o scrivi la tua domanda per ricevere assistenza assicurativa personalizzata'
                      : 'Attendi la connessione al sistema RAG...'}
                  </p>
                </motion.div>
              ) : (
                <AnimatePresence>
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      initial={{ opacity: 0, y: 15, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -15, scale: 0.95 }}
                      transition={{ type: "spring", stiffness: 400, damping: 25 }}
                    >
                      <div
                        className={`
                          max-w-[85%] p-3 rounded-lg relative overflow-hidden shadow-lg
                          ${message.role === 'user' 
                            ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-br-sm' 
                            : 'bg-white/10 backdrop-blur-xl border border-white/20 text-white rounded-bl-sm'
                          }
                          ${message.error ? 'border-red-400/50 bg-red-500/20' : ''}
                        `}
                      >
                        <div className="relative z-10">
                          <p className="whitespace-pre-wrap leading-relaxed text-sm">
                            {message.content}
                          </p>
                          
                          <div className={`text-xs mt-2 opacity-60 ${
                            message.role === 'user' ? 'text-right' : 'text-left'
                          }`}>
                            {formatTime(message.timestamp)}
                          </div>

                          {/* SOURCES ATTRIBUTION - REAL FROM RAILWAY */}
                          {message.sources && message.sources.length > 0 && (
                            <motion.div 
                              className="mt-3 pt-2 border-t border-white/20"
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ delay: 0.3 }}
                            >
                              <div className="text-xs font-medium mb-1 opacity-80 flex items-center gap-1">
                                📚 Fonti dai documenti:
                              </div>
                              <div className="flex flex-wrap gap-1">
                                {message.sources.map((source, index) => (
                                  <motion.span
                                    key={index}
                                    className="text-xs bg-white/20 rounded-full px-2 py-0.5 hover:bg-white/30 transition-colors cursor-pointer"
                                    whileHover={{ scale: 1.05 }}
                                    title={source.content || source.source}
                                  >
                                    {typeof source === 'string' ? source : source.source}
                                  </motion.span>
                                ))}
                              </div>
                            </motion.div>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              )}

              {/* TYPING INDICATOR */}
              <AnimatePresence>
                {isTyping && (
                  <motion.div
                    className="flex justify-start"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                  >
                    <div className="bg-white/10 backdrop-blur-xl border border-white/20 px-3 py-2 rounded-lg rounded-bl-sm shadow-lg">
                      <div className="flex space-x-1 items-center">
                        <span className="text-xs text-white/60 mr-2">AssistentIA sta pensando</span>
                        {[0, 1, 2].map((i) => (
                          <motion.div
                            key={i}
                            className="w-1.5 h-1.5 bg-white/60 rounded-full"
                            animate={{
                              scale: [1, 1.3, 1],
                              opacity: [0.6, 1, 0.6],
                            }}
                            transition={{
                              duration: 1.2,
                              repeat: Infinity,
                              ease: "easeInOut",
                              delay: i * 0.2
                            }}
                          />
                        ))}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* INPUT AREA - ENHANCED */}
          <motion.div 
            className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-b-lg p-3 shadow-lg"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <div className="flex items-end gap-2">
              <div className="flex-1">
                <textarea
                  ref={textareaRef}
                  value={inputValue}
                  onChange={handleInputChange}
                  onKeyPress={handleKeyPress}
                  placeholder={
                    connectionStatus === 'online' 
                      ? "Scrivi qui la tua domanda sulle assicurazioni..."
                      : "Connessione in corso..."
                  }
                  className="w-full bg-transparent text-white placeholder-white/50 border-none outline-none resize-none min-h-[40px] max-h-[100px] leading-relaxed text-sm py-2"
                  rows={1}
                  disabled={isLoading || connectionStatus !== 'online'}
                />
                <div className="flex justify-between text-white/40 text-xs mt-1">
                  <span>{inputValue.length}/500</span>
                  <span>{connectionStatus === 'online' ? 'Premi Enter per inviare' : 'Offline'}</span>
                </div>
              </div>

              <motion.button
                className={`w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center text-white shadow-lg relative overflow-hidden transition-all ${
                  (!inputValue.trim() || isLoading || connectionStatus !== 'online') 
                    ? 'opacity-50 cursor-not-allowed' 
                    : 'opacity-100 hover:shadow-xl'
                }`}
                whileHover={!isLoading && inputValue.trim() && connectionStatus === 'online' ? { scale: 1.05 } : {}}
                whileTap={!isLoading && inputValue.trim() && connectionStatus === 'online' ? { scale: 0.95 } : {}}
                onClick={() => sendMessage()}
                disabled={!inputValue.trim() || isLoading || connectionStatus !== 'online'}
              >
                {isLoading ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  >
                    ⚙️
                  </motion.div>
                ) : (
                  <PaperAirplaneIcon className="w-4 h-4" />
                )}
              </motion.button>
            </div>

            {/* QUICK SUGGESTIONS PILLS */}
            <div className="flex flex-wrap gap-1 mt-2 pt-2 border-t border-white/10">
              <span className="text-white/50 text-xs">Prova:</span>
              {['🔍 RCA vs Kasko', '📋 Procedura CID', '🛠️ Assistenza stradale', '💰 Calcolo premio'].map((pill, index) => (
                <motion.button
                  key={index}
                  className={`px-2 py-1 bg-white/10 rounded-full text-white/70 text-xs hover:bg-white/20 hover:text-white transition-all ${
                    connectionStatus !== 'online' ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                  whileHover={connectionStatus === 'online' ? { scale: 1.05 } : {}}
                  whileTap={connectionStatus === 'online' ? { scale: 0.95 } : {}}
                  onClick={() => connectionStatus === 'online' && sendMessage(pill.substring(2))}
                  disabled={connectionStatus !== 'online'}
                >
                  {pill}
                </motion.button>
              ))}
            </div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}