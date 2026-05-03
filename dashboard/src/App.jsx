import React, { useEffect } from 'react'
import Topbar from './components/Topbar'
import LeftNav from './components/LeftNav'
import TacticalMap from './components/TacticalMap'
import ThreatPanel from './components/ThreatPanel'
import AssignmentPanel from './components/AssignmentPanel'
import { connectWebSocket, sendMessage } from './ws/websocket'
import useAegisStore from './store/useAegisStore'

function App() {
  const { isScenarioLoading, setScenarioLoading } = useAegisStore()

  useEffect(() => {
    connectWebSocket()
  }, [])

  const triggerScenario = async () => {
    setScenarioLoading(true)
    try {
      console.log('Triggering 50-drone swarm attack scenario...')
      const response = await fetch('/api/sim/scenario', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ drone_count: 50 })
      })
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }
      
      setTimeout(() => setScenarioLoading(false), 500)
    } catch (error) {
      console.error('Failed to trigger scenario:', error)
      setScenarioLoading(false)
    }
  }

  return (
    <div className="h-screen w-screen flex flex-col bg-bg-deep text-text-secondary select-none overflow-hidden">
      <Topbar />
      
      <div className="flex-1 flex overflow-hidden">
        <LeftNav />
        
        <div className="flex-1 flex flex-col min-w-0 relative">
          <div className="flex-1 flex min-h-0">
            <TacticalMap />
            <ThreatPanel />
          </div>
          
          <AssignmentPanel />

          {/* Scenario Launcher FAB */}
          <button
            onClick={triggerScenario}
            disabled={isScenarioLoading}
            className={`
              absolute top-20 right-[300px] px-4 py-2 bg-blue-core hover:bg-blue-bright 
              text-text-primary font-mono text-[11px] font-bold tracking-widest uppercase
              border border-blue-glow shadow-[0_0_15px_rgba(21,101,192,0.4)]
              transition-all flex items-center gap-2 z-50
              ${isScenarioLoading ? 'opacity-50 cursor-wait' : ''}
            `}
          >
            {isScenarioLoading ? (
              <span className="w-2 h-2 bg-text-primary rounded-full animate-ping" />
            ) : (
              <span className="text-lg">⚡</span>
            )}
            {isScenarioLoading ? 'Initializing Swarm...' : 'Trigger Swarm Attack'}
          </button>
        </div>
      </div>
      
      {/* HUD Scanline Overlay */}
      <div className="fixed inset-0 pointer-events-none z-[100] opacity-[0.03] bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,0,0.06))] bg-[length:100%_4px,3px_100%]" />
      <div className="fixed inset-0 pointer-events-none z-[101] shadow-[inset_0_0_100px_rgba(0,0,0,0.5)]" />
    </div>
  )
}

export default App
