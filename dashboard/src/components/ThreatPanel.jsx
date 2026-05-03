import React from 'react'
import useAegisStore from '../store/useAegisStore'

const ThreatRow = ({ track }) => {
  const isCritical = (track.threat_level === 'CRITICAL')
  
  return (
    <div className={`threat-row ${isCritical ? 'threat-row--critical' : ''}`}>
      <div className={`w-2 h-2 rounded-full bg-threat-${track.threat_level?.toLowerCase() || 'unknown'}`} />
      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex justify-between items-center">
          <span className="text-text-primary text-[11px] truncate">{track.track_id}</span>
          <span className="text-text-accent text-[10px]">{Math.round((track.threat_score || 0) * 100)}%</span>
        </div>
        <div className="flex justify-between items-center text-[9px] text-text-muted uppercase">
          <span>{track.classification || 'UNKNOWN'}</span>
          <span>ETA: {track.eta_s ? `${track.eta_s}s` : '--'}</span>
        </div>
      </div>
    </div>
  )
}

const ThreatPanel = () => {
  const { tracks } = useAegisStore()
  const confirmedThreats = Object.values(tracks)
    .filter(t => t.threat_score > 0.3)
    .sort((a, b) => b.threat_score - a.threat_score)
  
  return (
    <div className="w-[280px] bg-bg-void border-l border-border-subtle flex flex-col">
      <div className="panel-card__header p-4 pb-2 border-none">Active Threats</div>
      
      <div className="flex-1 overflow-y-auto px-2">
        {confirmedThreats.length > 0 ? (
          confirmedThreats.map(track => (
            <ThreatRow key={track.track_id} track={track} />
          ))
        ) : (
          <div className="h-full flex items-center justify-center text-text-disabled text-[11px] uppercase tracking-widest italic">
            No Active Threats
          </div>
        )}
      </div>
      
      <div className="p-4 border-t border-border-subtle bg-bg-deep/50 text-[10px] font-mono">
        <div className="flex justify-between mb-1">
          <span className="text-text-muted">TOTAL TRACKS:</span>
          <span className="text-text-secondary">{Object.keys(tracks).length}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-text-muted">HOSTILE:</span>
          <span className="text-threat-3">{Object.values(tracks).filter(t => t.threat_level === 'HOSTILE' || t.threat_level === 'CRITICAL').length}</span>
        </div>
      </div>
    </div>
  )
}

export default ThreatPanel
