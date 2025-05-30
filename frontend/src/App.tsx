import React from 'react'
import { ChatPage } from './pages/ChatPage'
import { TestMinimal } from './pages/TestMinimal'
import './index.css'

function App() {
  // Simple router for future expansion
  const currentPath = window.location.hash.substring(1) || '/'

  const renderPage = () => {
    switch (currentPath) {
      case '/test':
        // Keep test functionality available via #/test
        return (
          <div style={{ padding: '20px', fontFamily: 'Arial' }}>
            <h1>🧪 API Test Still Available</h1>
            <p>Per tornare alla chat: <a href="#/">Chat Interface</a></p>
            <p>Oppure vai direttamente alla chat senza hash</p>
          </div>
        )
      case '/':
      default:
        return <ChatPage />
    }
  }

  return (
    <div className="App">
      {renderPage()}
    </div>
  )
}

export default App