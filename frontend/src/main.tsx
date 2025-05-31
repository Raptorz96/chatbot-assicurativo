// 📱 MAIN.TSX - React Entry Point con Mobile Detection
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Console banner per debug
console.log(`
🛡️ AssistentIA Pro - Frontend Started
📱 Mobile Detection: ${window.innerWidth < 768 ? 'MOBILE' : 'DESKTOP'}
🔧 Mode: ${import.meta.env.MODE}
🌍 Environment: ${import.meta.env.DEV ? 'Development' : 'Production'}
📐 Viewport: ${window.innerWidth}x${window.innerHeight}
🔗 API Base: ${window.location.origin}
`)

// Mobile detection immediata per CSS
const isMobile = window.innerWidth < 768 || /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
if (isMobile) {
  document.body.classList.add('force-mobile-layout')
  document.body.classList.remove('force-desktop-layout')
  console.log('📱 Mobile layout FORCED')
} else {
  document.body.classList.add('force-desktop-layout')
  document.body.classList.remove('force-mobile-layout')
  console.log('🖥️ Desktop layout FORCED')
}

// Viewport meta per mobile (se non già presente)
if (!document.querySelector('meta[name="viewport"]')) {
  const viewport = document.createElement('meta')
  viewport.name = 'viewport'
  viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
  document.head.appendChild(viewport)
  console.log('📱 Viewport meta added')
}

// Theme color per mobile browsers
if (!document.querySelector('meta[name="theme-color"]')) {
  const themeColor = document.createElement('meta')
  themeColor.name = 'theme-color'
  themeColor.content = '#0f172a'
  document.head.appendChild(themeColor)
}

// Disable zoom on iOS double-tap
document.addEventListener('touchstart', function(event) {
  if (event.touches.length > 1) {
    event.preventDefault()
  }
}, { passive: false })

let lastTouchEnd = 0
document.addEventListener('touchend', function(event) {
  const now = (new Date()).getTime()
  if (now - lastTouchEnd <= 300) {
    event.preventDefault()
  }
  lastTouchEnd = now
}, false)

// Resize handler per dynamic layout switching
window.addEventListener('resize', () => {
  const newIsMobile = window.innerWidth < 768
  
  if (newIsMobile && !document.body.classList.contains('force-mobile-layout')) {
    document.body.classList.add('force-mobile-layout')
    document.body.classList.remove('force-desktop-layout')
    console.log('📱 Switched to mobile layout')
  } else if (!newIsMobile && !document.body.classList.contains('force-desktop-layout')) {
    document.body.classList.add('force-desktop-layout')
    document.body.classList.remove('force-mobile-layout')
    console.log('🖥️ Switched to desktop layout')
  }
})

// Error boundary per development
window.addEventListener('error', (event) => {
  console.error('🚨 Global Error:', event.error)
})

window.addEventListener('unhandledrejection', (event) => {
  console.error('🚨 Unhandled Promise Rejection:', event.reason)
})

// Performance monitoring
if (import.meta.env.DEV) {
  window.addEventListener('load', () => {
    setTimeout(() => {
      const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
      console.log('⚡ Performance Metrics:', {
        loadTime: Math.round(perfData.loadEventEnd - perfData.loadEventStart),
        domContentLoaded: Math.round(perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart),
        fullLoad: Math.round(perfData.loadEventEnd - perfData.fetchStart)
      })
    }, 1000)
  })
}

// React Strict Mode per development quality
const container = document.getElementById('root')
if (!container) {
  throw new Error('Failed to find the root element')
}

const root = createRoot(container)

root.render(
  <StrictMode>
    <App />
  </StrictMode>,
)

// Export per hot reload
if (import.meta.hot) {
  import.meta.hot.accept()
}