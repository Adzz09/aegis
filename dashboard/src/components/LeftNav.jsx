import React from 'react'

const navItems = [
  { id: 'overview', label: 'Overview', icon: '⧉' },
  { id: 'tracks', label: 'Tracks', icon: '◎' },
  { id: 'sensors', label: 'Sensors', icon: '📡' },
  { id: 'defenders', label: 'Defenders', icon: '🛡' },
  { id: 'history', label: 'History', icon: '◷' },
  { id: 'settings', label: 'Settings', icon: '⚙' },
]

const LeftNav = () => {
  const [active, setActive] = React.useState('overview')
  
  return (
    <div className="w-[200px] bg-bg-void border-r border-border-subtle flex flex-col pt-4">
      {navItems.map((item) => (
        <button
          key={item.id}
          onClick={() => setActive(item.id)}
          className={`
            flex items-center gap-3 px-6 py-3 text-[12px] uppercase tracking-wider font-mono transition-all
            ${active === item.id 
              ? 'text-blue-glow bg-blue-dim border-r-2 border-blue-bright' 
              : 'text-text-muted hover:text-text-secondary hover:bg-bg-overlay'}
          `}
        >
          <span className="text-lg opacity-70">{item.icon}</span>
          {item.label}
        </button>
      ))}
      
      <div className="mt-auto p-6 text-[10px] text-text-disabled font-mono border-t border-border-subtle">
        <p>BUILD v1.0.2</p>
        <p>© 2026 AEGIS DEFENSE</p>
      </div>
    </div>
  )
}

export default LeftNav
