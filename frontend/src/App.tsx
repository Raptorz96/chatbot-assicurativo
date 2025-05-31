// 📱 APP.TSX - Mobile-First Router con Debug
import React, { useEffect, useState } from 'react'
import { ChatPage } from './pages/ChatPage'
import './index.css'

function App() {
  const [debugInfo, setDebugInfo] = useState({
    width: 0,
    height: 0,
    userAgent: '',
    isMobile: false,
    path: ''
  })

  // Debug info per mobile detection
  useEffect(() => {
    const updateDebugInfo = () => {
      const width = window.innerWidth
      const height = window.innerHeight
      const userAgent = navigator.userAgent
      const isMobile = width < 768 || /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent)
      const path = window.location.hash.substring(1) || '/'

      setDebugInfo({
        width,
        height,
        userAgent: userAgent.substring(0, 50),
        isMobile,
        path
      })

      console.log('📱 App Debug Info:', {
        width,
        height,
        isMobile,
        userAgent: userAgent.substring(0, 50),
        path
      })
    }

    updateDebugInfo()
    window.addEventListener('resize', updateDebugInfo)
    window.addEventListener('hashchange', updateDebugInfo)

    return () => {
      window.removeEventListener('resize', updateDebugInfo)
      window.removeEventListener('hashchange', updateDebugInfo)
    }
  }, [])

  // Simple router for future expansion
  const currentPath = window.location.hash.substring(1) || '/'

  const renderPage = () => {
    switch (currentPath) {
      case '/test':
        // Test page per debug - accessibile via #/test
        return (
          <div className="min-h-screen bg-slate-900 text-white p-4">
            <h1 className="text-2xl font-bold mb-4">🧪 Debug Test Page</h1>
            
            <div className="bg-white/10 rounded-lg p-4 mb-4">
              <h2 className="text-lg font-semibold mb-2">📱 Mobile Detection Info</h2>
              <div className="space-y-1 text-sm">
                <div>Width: {debugInfo.width}px</div>
                <div>Height: {debugInfo.height}px</div>
                <div>Is Mobile: {debugInfo.isMobile ? '✅ YES' : '❌ NO'}</div>
                <div>User Agent: {debugInfo.userAgent}...</div>
                <div>Current Path: {debugInfo.path}</div>
              </div>
            </div>

            <div className="bg-blue-500/20 rounded-lg p-4 mb-4">
              <h2 className="text-lg font-semibold mb-2">🔗 Navigation</h2>
              <div className="space-y-2">
                <a 
                  href="#/" 
                  className="block text-blue-300 hover:text-blue-100 underline"
                >
                  ← Torna alla Chat Interface
                </a>
                <a 
                  href="/dashboard" 
                  target="_blank" 
                  className="block text-green-300 hover:text-green-100 underline"
                >
                  📊 Apri Dashboard (nuova tab)
                </a>
                <a 
                  href="/api/health" 
                  target="_blank" 
                  className="block text-yellow-300 hover:text-yellow-100 underline"
                >
                  ⚡ Health Check API
                </a>
              </div>
            </div>

            <div className="bg-purple-500/20 rounded-lg p-4">
              <h2 className="text-lg font-semibold mb-2">🛠️ Quick Tests</h2>
              <div className="space-y-2">
                <button 
                  onClick={() => window.location.reload()}
                  className="block w-full text-left bg-white/10 hover:bg-white/20 p-2 rounded transition-colors"
                >
                  🔄 Reload App
                </button>
                <button 
                  onClick={() => {
                    document.body.classList.toggle('force-mobile-layout')
                    document.body.classList.toggle('force-desktop-layout')
                  }}
                  className="block w-full text-left bg-white/10 hover:bg-white/20 p-2 rounded transition-colors"
                >
                  📱 Toggle Mobile/Desktop Layout
                </button>
                <button 
                  onClick={() => console.log('App State:', debugInfo)}
                  className="block w-full text-left bg-white/10 hover:bg-white/20 p-2 rounded transition-colors"
                >
                  🔍 Log Debug Info to Console
                </button>
              </div>
            </div>
          </div>
        )
      
      case '/dashboard':
        // Redirect to actual dashboard
        window.location.href = '/dashboard'
        return (
          <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center">
            <div className="text-center">
              <div className="text-4xl mb-4">📊</div>
              <h1 className="text-xl font-bold mb-2">Redirecting to Dashboard...</h1>
              <p className="text-white/60">Se non funziona automaticamente, <a href="/dashboard" className="text-blue-400 underline">clicca qui</a></p>
            </div>
          </div>
        )
      
      case '/':
      default:
        // Main chat interface
        return <ChatPage />
    }
  }

  return (
    <div className="App">
      {/* Debug panel - solo in development */}
      {process.env.NODE_ENV === 'development' && (
        <div className="debug-mobile">
          {debugInfo.width}x{debugInfo.height} | {debugInfo.isMobile ? 'Mobile' : 'Desktop'}
        </div>
      )}
      
      {renderPage()}
    </div>
  )
}

export default App