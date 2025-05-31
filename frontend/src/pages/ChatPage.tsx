// 💬 CHATPAGE ENHANCED - Con Sidebar Navigation e Scroll Control
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
  CheckCircleIcon,
  ChatBubbleLeftIcon,
  HomeIcon,
  ArrowUpIcon,
  CogIcon,
  InformationCircleIcon,
  BoltIcon,
  DocumentTextIcon,
  ChevronLeftIcon,
  ChevronRightIcon
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

// 🔗 API CLIENT
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
  // ===== STATE =====
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'online' | 'offline' | 'error' | 'checking'>('checking')
  const [lastError, setLastError] = useState<string | null>(null)
  const [backendInfo, setBackendInfo] = useState<any>(null)
  
  // 📱 MOBILE STATE
  const [isMobile, setIsMobile] = useState(false)
  const [activeMobileTab, setActiveMobileTab] = useState<'home' | 'chat'>('home')
  
  // 🧭 SIDEBAR STATE - NUOVO
  const [activeLeftSection, setActiveLeftSection] = useState<'home' | 'actions' | 'system' | 'docs'>('home')
  const [leftSidebarCollapsed, setLeftSidebarCollapsed] = useState(false)
  
  // 📜 SCROLL CONTROL - NUOVO
  const [isNearBottom, setIsNearBottom] = useState(true)
  const [showScrollToTop, setShowScrollToTop] = useState(false)
  const [autoScroll, setAutoScroll] = useState(true)
  const [userHasScrolled, setUserHasScrolled] = useState(false)
  const [isScrolling, setIsScrolling] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)

  // Left Sidebar Sections
  const leftSidebarSections = [
    {
      id: 'home',
      icon: HomeIcon,
      label: 'Home',
      description: 'Panoramica sistema'
    },
    {
      id: 'actions',
      icon: BoltIcon,
      label: 'Azioni',
      description: 'Quick actions'
    },
    {
      id: 'system',
      icon: CogIcon,
      label: 'Sistema',
      description: 'Status e features'
    },
    {
      id: 'docs',
      icon: DocumentTextIcon,
      label: 'Documenti',
      description: 'Knowledge base'
    }
  ]

  // Quick Actions
  const quickActions = [
    {
      id: 'rca',
      icon: '🚗',
      title: 'Polizza RCA',
      description: 'Coperture obbligatorie auto',
      message: 'Cosa copre esattamente la polizza RCA? Quali sono i massimali e cosa include?',
      color: 'from-blue-500 to-blue-600',
      shadowColor: 'shadow-blue-500/25'
    },
    {
      id: 'sinistro',
      icon: '⚠️',
      title: 'Gestione Sinistro',
      description: 'Procedure emergenze',
      message: 'Come devo comportarmi in caso di sinistro stradale? Quali documenti servono?',
      color: 'from-amber-500 to-orange-500',
      shadowColor: 'shadow-orange-500/25'
    },
    {
      id: 'casa',
      icon: '🏠',
      title: 'Polizza Casa',
      description: 'Protezione abitazione',
      message: 'Come funziona la polizza casa? Cosa copre per incendio, furto e responsabilità civile?',
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

  // System features
  const systemFeatures = [
    { icon: '🧠', text: 'Custom RAG System', active: connectionStatus === 'online' },
    { icon: '🔍', text: 'Document Retrieval', active: connectionStatus === 'online' },
    { icon: '💬', text: 'Conversation Mgmt', active: connectionStatus === 'online' },
    { icon: '📚', text: 'Knowledge Base (19)', active: connectionStatus === 'online' }
  ]

  // Documents info
  const documentsInfo = [
    { name: 'faq_polizze_auto_casa.md', chunks: 13, type: 'FAQ' },
    { name: 'polizza_auto.txt', chunks: 2, type: 'Polizze' },
    { name: 'polizza_casa.txt', chunks: 2, type: 'Polizze' },
    { name: 'sinistri.txt', chunks: 2, type: 'Procedure' }
  ]

  // 📱 MOBILE DETECTION
  useEffect(() => {
    const checkMobile = () => {
      const width = window.innerWidth
      const isMobileDevice = width < 768
      setIsMobile(isMobileDevice)
      
      document.body.className = document.body.className
        .replace(/force-(mobile|desktop)-layout/g, '')
      
      if (isMobileDevice) {
        document.body.classList.add('force-mobile-layout')
      } else {
        document.body.classList.add('force-desktop-layout')
      }
    }
    
    checkMobile()
    window.addEventListener('resize', checkMobile)
    
    return () => {
      window.removeEventListener('resize', checkMobile)
      document.body.classList.remove('force-mobile-layout', 'force-desktop-layout')
    }
  }, [])

  // 🔧 FORCE FULL WIDTH
  useEffect(() => {
    const style = document.createElement('style')
    style.id = 'force-fullwidth-fix'
    style.textContent = `
      body, html {
        margin: 0 !important;
        padding: 0 !important;
        width: 100vw !important;
        overflow-x: hidden !important;
      }
      
      #root, .App {
        width: 100vw !important;
        min-width: 100vw !important;
        max-width: none !important;
        margin: 0 !important;
        padding: 0 !important;
      }
      
      .desktop-container {
        display: flex !important;
        height: 100vh !important;
        width: 100vw !important;
        gap: 24px !important;
        padding: 16px 20px !important;
        box-sizing: border-box !important;
      }
      
      .desktop-left-panel,
      .desktop-right-panel {
        flex: 1 !important;
        min-height: 100% !important;
        width: calc(50% - 12px) !important;
      }
    `
    
    document.head.appendChild(style)
    
    return () => {
      const existingStyle = document.getElementById('force-fullwidth-fix')
      if (existingStyle) {
        document.head.removeChild(existingStyle)
      }
    }
  }, [])

  // 📜 SCROLL MONITORING - MIGLIORATO
  useEffect(() => {
    const chatContainer = chatContainerRef.current
    if (!chatContainer) return

    let scrollTimeout: NodeJS.Timeout

    const handleScroll = () => {
      // Previeni loop di scroll events
      if (isScrolling) return
      
      const { scrollTop, scrollHeight, clientHeight } = chatContainer
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 10
      const isAtTop = scrollTop < 50
      
      // Clear timeout precedente
      if (scrollTimeout) clearTimeout(scrollTimeout)
      
      // Debounce per evitare troppi aggiornamenti
      scrollTimeout = setTimeout(() => {
        setIsNearBottom(isAtBottom)
        setShowScrollToTop(!isAtTop && !isAtBottom)
        
        // L'utente ha scrollato manualmente solo se NON è un auto-scroll
        if (!isScrolling) {
          setUserHasScrolled(true)
          
          // Se l'utente scorre verso l'alto manualmente, disabilita auto-scroll
          if (!isAtBottom && scrollTop > 0) {
            console.log('🔒 User scrolled up manually - disabling auto-scroll')
            setAutoScroll(false)
          } 
          // Se l'utente torna in bottom manualmente, riabilita auto-scroll
          else if (isAtBottom) {
            console.log('✅ User at bottom - enabling auto-scroll')
            setAutoScroll(true)
          }
        }
      }, 100) // Debounce di 100ms
    }

    chatContainer.addEventListener('scroll', handleScroll, { passive: true })
    
    return () => {
      chatContainer.removeEventListener('scroll', handleScroll)
      if (scrollTimeout) clearTimeout(scrollTimeout)
    }
  }, [isScrolling])

  // Check connection
  useEffect(() => {
    checkConnectionStatus()
    const interval = setInterval(checkConnectionStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  const checkConnectionStatus = async () => {
    setConnectionStatus('checking')
    try {
      const health = await apiCall.getHealth()
      setConnectionStatus('online')
      setBackendInfo(health)
      setLastError(null)
    } catch (error) {
      setConnectionStatus('error')
      setLastError(error instanceof Error ? error.message : 'Connection failed')
    }
  }

  // Auto scroll - MIGLIORATO e CONTROLLATO
  const scrollToBottom = (force = false) => {
    // Solo scrolla se l'auto-scroll è abilitato O se è forzato
    if ((autoScroll && !userHasScrolled) || force) {
      console.log('📜 Scrolling to bottom:', { autoScroll, userHasScrolled, force })
      setIsScrolling(true)
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
      
      // Reset flag dopo un breve delay
      setTimeout(() => setIsScrolling(false), 1000)
    } else {
      console.log('🚫 Scroll blocked:', { autoScroll, userHasScrolled, force })
    }
  }

  const scrollToTop = () => {
    console.log('⬆️ Scrolling to top')
    setIsScrolling(true)
    chatContainerRef.current?.scrollTo({ top: 0, behavior: 'smooth' })
    setAutoScroll(false)
    setUserHasScrolled(true)
    
    setTimeout(() => setIsScrolling(false), 1000)
  }

  const resetScrollState = () => {
    console.log('🔄 Resetting scroll state')
    setAutoScroll(true)
    setUserHasScrolled(false)
    setIsScrolling(false)
  }

  // Auto-scroll intelligente - SOLO quando appropriato
  useEffect(() => {
    // Solo per nuovi messaggi, non per typing indicator
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1]
      const isNewMessage = Date.now() - lastMessage.timestamp.getTime() < 2000 // Messaggio degli ultimi 2 secondi
      
      if (isNewMessage) {
        console.log('📨 New message detected, checking scroll policy')
        // Solo scrolla se l'auto-scroll è abilitato e l'utente non ha scrollato manualmente
        if (autoScroll && !userHasScrolled) {
          scrollToBottom()
        }
      }
    }
  }, [messages.length]) // Solo quando cambia il NUMERO di messaggi

  // Scroll per typing indicator - più conservativo  
  useEffect(() => {
    if (isTyping && autoScroll && !userHasScrolled) {
      console.log('💭 Typing indicator - gentle scroll')
      scrollToBottom()
    }
  }, [isTyping])

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value)
    
    const textarea = e.target
    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
  }

  // Send message
  const sendMessage = async (messageText?: string) => {
    const message = messageText || inputValue.trim()
    if (!message || isLoading || connectionStatus !== 'online') return

    // AUTO-SWITCH TO CHAT su mobile
    if (isMobile && activeMobileTab !== 'chat') {
      setActiveMobileTab('chat')
    }

    setInputValue('')
    setIsLoading(true)
    setLastError(null)
    
    // Quando l'utente invia un messaggio, VUOLE vedere la risposta
    console.log('💬 User sending message - resetting scroll state')
    resetScrollState()
    
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
      }

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

  // Connection status
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

  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('it-IT', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  // 🏠 HOME SECTION CONTENT
  const renderHomeSection = () => (
    <div className="space-y-4">
      {/* CONNECTION STATUS */}
      <motion.div 
        className={`bg-white/5 backdrop-blur-sm border rounded-lg p-3 ${
          connectionStatus === 'online' ? 'border-green-500/30' : 'border-orange-400/30'
        }`}
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
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
      
      {/* HEADER */}
      <motion.div 
        className="text-center"
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.1 }}
      >
        <h2 className="text-xl font-bold text-white mb-1">
          Come posso aiutarti oggi?
        </h2>
        <p className="text-white/60 text-sm">
          {connectionStatus === 'online' 
            ? 'Sistema RAG attivo con 19 documenti assicurativi'
            : 'Connessione al backend in corso...'}
        </p>
      </motion.div>
    </div>
  )

  // ⚡ ACTIONS SECTION CONTENT
  const renderActionsSection = () => (
    <div className="space-y-4">
      <h3 className="text-white font-bold text-lg text-center mb-4">
        🚀 Azioni Rapide
      </h3>
      
      {/* QUICK ACTIONS - GRID */}
      <div className="grid grid-cols-1 gap-3">
        {quickActions.map((action, index) => (
          <motion.button
            key={action.id}
            className={`
              relative p-4 rounded-xl bg-gradient-to-r ${action.color} 
              text-white shadow-lg ${action.shadowColor} 
              hover:shadow-xl transition-all text-left overflow-hidden group
              border border-white/10
              ${connectionStatus !== 'online' ? 'opacity-50 cursor-not-allowed' : ''}
            `}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={connectionStatus === 'online' ? { y: -2, scale: 1.02 } : {}}
            whileTap={connectionStatus === 'online' ? { scale: 0.98 } : {}}
            onClick={() => {
              if (connectionStatus === 'online') {
                sendMessage(action.message)
              }
            }}
            disabled={connectionStatus !== 'online'}
          >
            {/* Shine effect */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 -translate-x-full group-hover:translate-x-full"
              transition={{ duration: 0.6 }}
            />
            
            <div className="relative z-10 flex items-center gap-3">
              <div className="text-2xl group-hover:scale-105 transition-transform duration-300">
                {action.icon}
              </div>
              <div className="flex-1">
                <div className="font-semibold text-sm mb-0.5">{action.title}</div>
                <div className="text-white/90 text-xs">{action.description}</div>
              </div>
              <div className="text-white/60 group-hover:text-white transition-colors text-lg">
                →
              </div>
            </div>
          </motion.button>
        ))}
      </div>

      {/* QUICK SUGGESTIONS */}
      <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3">
        <h4 className="text-white font-medium mb-3 text-sm">
          💬 Suggerimenti rapidi:
        </h4>
        <div className="grid grid-cols-2 gap-2">
          {['🚗 RCA vs Kasko', '📋 Procedura CID', '🛠️ Assistenza 24/7', '💰 Calcolo premio'].map((suggestion, index) => (
            <motion.button
              key={index}
              className={`p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-left text-white/80 hover:text-white text-xs ${
                connectionStatus !== 'online' ? 'opacity-50 cursor-not-allowed' : ''
              }`}
              whileHover={connectionStatus === 'online' ? { scale: 1.02 } : {}}
              whileTap={connectionStatus === 'online' ? { scale: 0.98 } : {}}
              onClick={() => connectionStatus === 'online' && sendMessage(suggestion.substring(2))}
              disabled={connectionStatus !== 'online'}
            >
              {suggestion}
            </motion.button>
          ))}
        </div>
      </div>
    </div>
  )

  // 🔧 SYSTEM SECTION CONTENT  
  const renderSystemSection = () => (
    <div className="space-y-4">
      <h3 className="text-white font-bold text-lg text-center mb-4">
        🛠️ Sistema & Performance
      </h3>
      
      {/* SYSTEM FEATURES */}
      <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
        <h4 className="text-blue-300 font-medium mb-3 text-sm">
          🔧 Components Status:
        </h4>
        <div className="space-y-3">
          {systemFeatures.map((feature, index) => (
            <motion.div
              key={index}
              className="flex items-center gap-3 p-2 rounded-lg bg-white/5"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <span className="text-lg">{feature.icon}</span>
              <span className="flex-1 text-white/90 text-sm">{feature.text}</span>
              <motion.div
                className={`w-3 h-3 rounded-full ${
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
      </div>

      {/* PERFORMANCE METRICS */}
      <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
        <h4 className="text-green-300 font-medium mb-3 text-sm">
          📊 Performance Metrics:
        </h4>
        <div className="space-y-2 text-sm text-white/80">
          <div className="flex justify-between">
            <span>Conversazioni totali:</span>
            <span className="text-green-400">{messages.length}</span>
          </div>
          <div className="flex justify-between">
            <span>Response time:</span>
            <span className="text-blue-400">~2.5s</span>
          </div>
          <div className="flex justify-between">
            <span>Cache hit rate:</span>
            <span className="text-yellow-400">85%</span>
          </div>
          <div className="flex justify-between">
            <span>Uptime:</span>
            <span className="text-green-400">99.9%</span>
          </div>
        </div>
      </div>

      {/* ACTIONS */}
      <div className="space-y-2">
        <motion.button
          className="w-full p-3 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/50 rounded-lg text-blue-300 font-medium transition-colors text-sm"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => window.open('/dashboard', '_blank')}
        >
          🔍 Apri Dashboard Completa
        </motion.button>
        
        <motion.button
          className="w-full p-3 bg-orange-500/20 hover:bg-orange-500/30 border border-orange-500/50 rounded-lg text-orange-300 font-medium transition-colors text-sm"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => {
            setMessages([])
            setConversationId(null)
          }}
        >
          🗑️ Reset Conversazione
        </motion.button>
      </div>
    </div>
  )

  // 📚 DOCS SECTION CONTENT
  const renderDocsSection = () => (
    <div className="space-y-4">
      <h3 className="text-white font-bold text-lg text-center mb-4">
        📚 Knowledge Base
      </h3>
      
      {/* DOCUMENTS LIST */}
      <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
        <h4 className="text-purple-300 font-medium mb-3 text-sm">
          📄 Documenti Indicizzati:
        </h4>
        <div className="space-y-2">
          {documentsInfo.map((doc, index) => (
            <motion.div
              key={index}
              className="flex items-center gap-3 p-2 rounded-lg bg-white/5 border border-white/10"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <DocumentTextIcon className="w-4 h-4 text-purple-400" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-white text-xs font-medium truncate">{doc.name}</div>
                <div className="text-white/60 text-xs">{doc.type} • {doc.chunks} chunks</div>
              </div>
              <div className="text-green-400 text-xs">✓</div>
            </motion.div>
          ))}
        </div>
        
        <div className="mt-3 p-2 bg-green-500/20 border border-green-500/30 rounded-lg">
          <div className="text-green-300 text-xs font-medium">
            ✅ Total: 19 chunks indicizzati
          </div>
          <div className="text-green-400/80 text-xs">
            Vector database: SQLite • Custom RAG Engine
          </div>
        </div>
      </div>

      {/* COVERAGE INFO */}
      <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
        <h4 className="text-blue-300 font-medium mb-3 text-sm">
          🎯 Copertura Topics:
        </h4>
        <div className="grid grid-cols-2 gap-2 text-xs">
          {[
            { topic: 'RCA Obbligatoria', coverage: '100%' },
            { topic: 'Polizze Casa', coverage: '95%' },
            { topic: 'Gestione Sinistri', coverage: '90%' },
            { topic: 'Preventivi', coverage: '85%' }
          ].map((item, index) => (
            <div key={index} className="flex justify-between text-white/80">
              <span>{item.topic}:</span>
              <span className="text-green-400">{item.coverage}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  // 📱 HOME CONTENT COMBINATO (per mobile)
  const renderHomeContent = () => {
    if (isMobile) {
      return (
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {renderHomeSection()}
          {renderActionsSection()}
          {renderSystemSection()}
          {renderDocsSection()}
        </div>
      )
    }

    // Desktop: Mostra sezione attiva
    switch (activeLeftSection) {
      case 'home': return renderHomeSection()
      case 'actions': return renderActionsSection()
      case 'system': return renderSystemSection()
      case 'docs': return renderDocsSection()
      default: return renderHomeSection()
    }
  }

  // 📱 CHAT CONTENT con Scroll Control
  const renderChatContent = () => (
    <div className="flex-1 flex flex-col h-full relative">
      {/* MESSAGES AREA con Scroll Control */}
      <div 
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-3 relative"
      >
        
        {messages.length === 0 ? (
          <motion.div
            className="text-center py-8"
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
            <p className="text-white/60 text-sm leading-relaxed px-4">
              {connectionStatus === 'online'
                ? 'Usa le azioni rapide o scrivi qui la tua domanda'
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

                    {/* SOURCES */}
                    {message.sources && message.sources.length > 0 && (
                      <motion.div 
                        className="mt-3 pt-2 border-t border-white/20"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                      >
                        <div className="text-xs font-medium mb-1 opacity-80 flex items-center gap-1">
                          📚 Fonti:
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

      {/* SCROLL TO TOP BUTTON */}
      <AnimatePresence>
        {showScrollToTop && (
          <motion.button
            className="absolute right-6 bottom-24 w-12 h-12 bg-blue-500/80 hover:bg-blue-500 backdrop-blur-xl border border-white/20 rounded-full flex items-center justify-center text-white shadow-lg z-20"
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={scrollToTop}
          >
            <ArrowUpIcon className="w-5 h-5" />
          </motion.button>
        )}
      </AnimatePresence>

      {/* AUTO-SCROLL INDICATOR */}
      {!autoScroll && messages.length > 0 && (
        <motion.div
          className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-orange-500/90 backdrop-blur-xl border border-orange-300/30 rounded-full px-4 py-2 text-white text-sm font-medium z-20 cursor-pointer"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => {
            console.log('🔄 User manually re-enabled auto-scroll')
            resetScrollState()
            scrollToBottom(true)
          }}
        >
          <div className="flex items-center gap-2">
            <span>📜 Auto-scroll disabilitato</span>
            <span className="text-orange-200 text-xs">• Clicca per riabilitare</span>
          </div>
        </motion.div>
      )}

      {/* INPUT AREA */}
      <motion.div 
        className="bg-white/10 backdrop-blur-xl border border-white/20 border-t-0 p-3 shadow-lg"
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
                  ? "Scrivi qui la tua domanda..."
                  : "Connessione in corso..."
              }
              className="w-full bg-transparent text-white placeholder-white/50 border-none outline-none resize-none min-h-[44px] max-h-[100px] leading-relaxed text-base py-2"
              rows={1}
              disabled={isLoading || connectionStatus !== 'online'}
            />
            <div className="flex justify-between text-white/40 text-xs mt-1">
              <span>{inputValue.length}/500</span>
              <div className="flex items-center gap-2">
                <span>{connectionStatus === 'online' ? 'Premi Invio' : 'Offline'}</span>
                {!autoScroll && (
                  <motion.button
                    className="text-orange-400 hover:text-orange-300 text-xs bg-orange-500/20 px-2 py-1 rounded-full"
                    onClick={() => {
                      console.log('🔄 Auto-scroll re-enabled from input area')
                      resetScrollState()
                      scrollToBottom(true)
                    }}
                    whileHover={{ scale: 1.1 }}
                    title="Riabilita auto-scroll"
                  >
                    📜 Riabilita
                  </motion.button>
                )}
              </div>
            </div>
          </div>

          <motion.button
            className={`w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center text-white shadow-lg relative overflow-hidden transition-all ${
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
              <PaperAirplaneIcon className="w-5 h-5" />
            )}
          </motion.button>
        </div>

        {/* QUICK SUGGESTIONS PILLS */}
        <div className="flex flex-wrap gap-1 mt-3 pt-2 border-t border-white/10">
          <span className="text-white/50 text-xs mr-1">Prova:</span>
          {['🚗 RCA vs Kasko', '📋 CID', '🛠️ Assistenza', '💰 Preventivo'].map((pill, index) => (
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
    </div>
  )

  return (
    <div 
      className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 relative overflow-hidden"
      style={{
        width: '100vw',
        minWidth: '100vw',
        maxWidth: 'none',
        margin: 0,
        padding: 0
      }}
    >
      
      {/* ANIMATED BACKGROUND */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900/50 via-blue-900/30 to-slate-800/50" />
        {/* Floating bubbles */}
        {[...Array(isMobile ? 3 : 8)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full bg-white/5 backdrop-blur-sm"
            style={{
              width: Math.random() * (isMobile ? 60 : 120) + (isMobile ? 30 : 60),
              height: Math.random() * (isMobile ? 60 : 120) + (isMobile ? 30 : 60),
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

      {/* ===== CONDITIONAL LAYOUT RENDERING ===== */}
      {isMobile ? (
        /* 📱 MOBILE LAYOUT - Tab System */
        <div className="relative z-10 h-screen flex flex-col">
          
          {/* MOBILE HEADER */}
          <motion.div 
            className="header-container"
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            <div className="header-left">
              <motion.div 
                className="header-logo"
                whileHover={{ scale: 1.05 }}
                animate={connectionStatus === 'online' ? {
                  boxShadow: ['0 0 0 0 rgba(34, 197, 94, 0.7)', '0 0 0 8px rgba(34, 197, 94, 0)']
                } : {}}
                transition={{ duration: 2, repeat: Infinity }}
              >
                🛡️
              </motion.div>
              <div className="header-title-group">
                <h1 className="header-title">
                  AssistentIA Pro
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                  >
                    <SparklesIcon className="w-4 h-4 text-yellow-400" />
                  </motion.div>
                </h1>
                <p className="header-subtitle">Custom RAG • Railway</p>
              </div>
            </div>
            
            <div className="header-right">
              {/* Connection Status */}
              <motion.div 
                className={`header-status ${connectionIndicator.bgColor}`}
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
                className="header-button"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => window.open('/dashboard', '_blank')}
              >
                <ChartBarIcon className="w-3 h-3" />
                Dashboard
              </motion.button>
            </div>
          </motion.div>

          {/* MOBILE TAB NAVIGATION */}
          <motion.div 
            className="bg-white/5 backdrop-blur-sm border-b border-white/10 flex"
            initial={{ y: -10, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            {[
              { id: 'home', label: 'Home', icon: HomeIcon },
              { id: 'chat', label: 'Chat', icon: ChatBubbleLeftIcon }
            ].map((tab) => (
              <motion.button
                key={tab.id}
                className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-all ${
                  activeMobileTab === tab.id 
                    ? 'text-white bg-white/10 border-b-2 border-blue-400' 
                    : 'text-white/60'
                }`}
                whileTap={{ scale: 0.98 }}
                onClick={() => setActiveMobileTab(tab.id as 'home' | 'chat')}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
                {tab.id === 'chat' && messages.length > 0 && (
                  <span className="bg-blue-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {messages.length}
                  </span>
                )}
              </motion.button>
            ))}
          </motion.div>

          {/* MOBILE TAB CONTENT */}
          <div className="flex-1 overflow-hidden">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeMobileTab}
                className="h-full flex flex-col"
                initial={{ opacity: 0, x: activeMobileTab === 'chat' ? 20 : -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: activeMobileTab === 'chat' ? -20 : 20 }}
                transition={{ duration: 0.3 }}
              >
                {activeMobileTab === 'home' ? renderHomeContent() : renderChatContent()}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      ) : (
        /* 🖥️ DESKTOP LAYOUT con SIDEBAR */
        <div 
          className="relative z-10 desktop-container"
          style={{
            height: '100vh',
            width: '100vw',
            display: 'flex',
            gap: '24px',
            padding: '16px 20px',
            boxSizing: 'border-box',
            margin: 0,
            maxWidth: 'none'
          }}
        >
          
          {/* LEFT PANEL - DESKTOP con SIDEBAR */}
          <motion.div 
            className="desktop-left-panel"
            style={{
              flex: 1,
              minHeight: '100%',
              width: 'calc(50% - 12px)',
              display: 'flex',
              flexDirection: 'column'
            }}
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            
            {/* HEADER DESKTOP */}
            <motion.div 
              className="header-container"
              initial={{ y: -20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.1 }}
            >
              <div className="header-left">
                <motion.div 
                  className="header-logo"
                  whileHover={{ scale: 1.05 }}
                  animate={connectionStatus === 'online' ? {
                    boxShadow: ['0 0 0 0 rgba(34, 197, 94, 0.7)', '0 0 0 10px rgba(34, 197, 94, 0)']
                  } : {}}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  🛡️
                </motion.div>
                <div className="header-title-group">
                  <h1 className="header-title">
                    AssistentIA Pro
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                    >
                      <SparklesIcon className="w-6 h-6 text-yellow-400" />
                    </motion.div>
                  </h1>
                  <p className="header-subtitle">RAG System • Railway Backend</p>
                </div>
              </div>
              
              <div className="header-right">
                <motion.div 
                  className={`header-status ${connectionIndicator.bgColor}`}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  <connectionIndicator.icon className={`w-4 h-4 ${connectionIndicator.color}`} />
                  <span className={`${connectionIndicator.color}`}>
                    {connectionIndicator.text}
                  </span>
                </motion.div>

                <motion.button
                  className="header-button"
                  whileHover={{ scale: 1.02, y: -1 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => window.open('/dashboard', '_blank')}
                >
                  <ChartBarIcon className="w-4 h-4" />
                  Dashboard
                </motion.button>
              </div>
            </motion.div>

            {/* DESKTOP MAIN CONTENT con SIDEBAR */}
            <div className="flex-1 bg-white/5 backdrop-blur-xl border border-white/10 border-t-0 border-b-0 overflow-hidden flex">
              
              {/* SIDEBAR NAVIGATION */}
              <motion.div 
                className={`bg-white/5 border-r border-white/10 flex flex-col transition-all duration-300 ${
                  leftSidebarCollapsed ? 'w-16' : 'w-56'
                }`}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
              >
                {/* SIDEBAR HEADER */}
                <div className="p-4 border-b border-white/10 flex items-center justify-between">
                  {!leftSidebarCollapsed && (
                    <h3 className="text-white font-semibold text-sm">Navigazione</h3>
                  )}
                  <motion.button
                    className="w-8 h-8 bg-white/10 hover:bg-white/20 rounded-lg flex items-center justify-center text-white/60 hover:text-white transition-colors"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setLeftSidebarCollapsed(!leftSidebarCollapsed)}
                  >
                    {leftSidebarCollapsed ? (
                      <ChevronRightIcon className="w-4 h-4" />
                    ) : (
                      <ChevronLeftIcon className="w-4 h-4" />
                    )}
                  </motion.button>
                </div>

                {/* SIDEBAR MENU */}
                <div className="flex-1 p-2">
                  {leftSidebarSections.map((section, index) => (
                    <motion.button
                      key={section.id}
                      className={`w-full flex items-center gap-3 p-3 rounded-lg transition-all mb-1 ${
                        activeLeftSection === section.id
                          ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                          : 'text-white/60 hover:text-white hover:bg-white/10'
                      }`}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.3 + index * 0.05 }}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setActiveLeftSection(section.id as any)}
                      title={leftSidebarCollapsed ? section.label : undefined}
                    >
                      <section.icon className="w-5 h-5 flex-shrink-0" />
                      {!leftSidebarCollapsed && (
                        <div className="text-left min-w-0">
                          <div className="font-medium text-sm">{section.label}</div>
                          <div className="text-xs opacity-60 truncate">{section.description}</div>
                        </div>
                      )}
                      {activeLeftSection === section.id && !leftSidebarCollapsed && (
                        <motion.div
                          className="w-2 h-2 bg-blue-400 rounded-full ml-auto"
                          layoutId="activeIndicator"
                        />
                      )}
                    </motion.button>
                  ))}
                </div>
              </motion.div>

              {/* CONTENT AREA */}
              <div className="flex-1 overflow-y-auto p-4">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={activeLeftSection}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    {renderHomeContent()}
                  </motion.div>
                </AnimatePresence>
              </div>
            </div>

            {/* BOTTOM BORDER */}
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 border-t-0 rounded-b-xl h-4"></div>
          </motion.div>

          {/* RIGHT PANEL - DESKTOP CHAT */}
          <motion.div 
            className="desktop-right-panel"
            style={{
              flex: 1,
              minHeight: '100%',
              width: 'calc(50% - 12px)',
              display: 'flex',
              flexDirection: 'column'
            }}
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            
            {/* CHAT HEADER */}
            <motion.div 
              className="bg-white/10 backdrop-blur-xl border border-white/20 border-b-0 rounded-t-xl p-6 shadow-lg"
              initial={{ y: -20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="flex items-center gap-3">
                <motion.div 
                  className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center text-white shadow-lg"
                  animate={connectionStatus === 'online' ? { 
                    boxShadow: ['0 0 0 0 rgba(59, 130, 246, 0.5)', '0 0 0 8px rgba(59, 130, 246, 0)']
                  } : {}}
                  transition={{ duration: 3, repeat: Infinity }}
                >
                  🤖
                </motion.div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-white font-semibold text-xl">AssistentIA Pro</h3>
                    <motion.div
                      className={`w-2 h-2 rounded-full ${
                        connectionStatus === 'online' ? 'bg-green-400' : 'bg-red-400'
                      }`}
                      animate={{ opacity: [1, 0.4, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                    <span className={`text-sm font-medium ${
                      connectionStatus === 'online' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {connectionIndicator.text}
                    </span>
                  </div>
                  <p className="text-white/60 text-base">
                    {connectionStatus === 'online' 
                      ? 'Custom RAG System • 19 documenti assicurativi'
                      : 'Connessione al backend in corso...'}
                  </p>
                </div>
              </div>
            </motion.div>

            {/* DESKTOP CHAT CONTENT */}
            <div className="flex-1 bg-white/5 backdrop-blur-xl border border-white/10 border-t-0 border-b-0 overflow-hidden flex flex-col shadow-lg">
              {renderChatContent()}
            </div>

            {/* BOTTOM BORDER */}
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 border-t-0 rounded-b-xl h-4"></div>
          </motion.div>
        </div>
      )}
    </div>
  )
}