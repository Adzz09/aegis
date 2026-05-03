import React, { useState, useEffect } from 'react'
import useAegisStore from '../store/useAegisStore'

const AlertTimeline = () => {
  const [alerts, setAlerts] = useState([
    { id: 1, time: '13:20:01', msg: 'SYSTEM INITIALIZED' },
    { id: 2, time: '13:20:05', msg: 'KAFKA MESSAGE BUS ONLINE' },
    { id: 3, time: '13:20:10', msg: 'SENSOR RADAR-01 CONNECTED' },
  ])

  // Simulate incoming alerts
  useEffect(() => {
    const timer = setInterval(() => {
      const newAlert = {
        id: Date.now(),
        time: new Date().toLocaleTimeString('en-GB'),
        msg: 'HEARTBEAT: ALL MODULES NOMINAL'
      }
      setAlerts(prev => [newAlert, ...prev.slice(0, 4)])
    }, 15000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="flex items-center gap-4 text-[11px] font-mono text-text-muted overflow-hidden">
      <div className="flex items-center gap-2 text-threat-3 animate-pulse border-r border-border-subtle pr-3">
        <span className="w-1.5 h-1.5 bg-threat-3 rounded-full" />
        LIVE FEED
      </div>
      <div className="flex gap-6 animate-marquee whitespace-nowrap">
        {alerts.map(alert => (
          <div key={alert.id} className="flex gap-2">
            <span className="text-text-accent">[{alert.time}]</span>
            <span className="text-text-secondary uppercase">{alert.msg}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

const Topbar = () => {
  const { systemHealth } = useAegisStore()
  
  return (
    <div className="h-12 bg-bg-void border-b border-border-subtle flex items-center justify-between px-4 z-50">
      <div className="flex items-center gap-6 overflow-hidden flex-1">
        <div className="flex flex-col min-w-fit">
          <span className="font-bold text-blue-glow tracking-[0.25em] text-lg leading-tight font-mono">AEGIS</span>
          <span className="text-[9px] text-text-muted tracking-[0.2em] -mt-1 uppercase">Counter-Swarm Defense</span>
        </div>
        
        <div className="h-8 w-[1px] bg-border-subtle mx-2" />
        
        <AlertTimeline />
      </div>
      
      <div className="flex items-center gap-6 ml-4">
        <div className="flex items-center gap-4">
          {Object.entries(systemHealth).map(([module, status]) => (
            <div key={module} className="flex items-center gap-2 group cursor-help relative">
              <div className={`health-dot health-dot--${status}`} />
              <span className="text-[10px] uppercase text-text-muted font-mono group-hover:text-text-secondary transition-colors">{module}</span>
              
              {/* Tooltip */}
              <div className="absolute top-8 right-0 bg-bg-abyss border border-border-subtle p-2 text-[9px] rounded hidden group-hover:block whitespace-nowrap z-[60]">
                STATUS: {status.toUpperCase()}<br />
                LATENCY: 12ms
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Topbar
