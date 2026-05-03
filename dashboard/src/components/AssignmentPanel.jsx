import React from 'react'
import useAegisStore from '../store/useAegisStore'

const AssignmentPanel = () => {
  const { assignments } = useAegisStore()
  
  return (
    <div className="h-[160px] bg-bg-void border-t border-border-subtle flex flex-col">
      <div className="panel-card__header p-4 pb-2 border-none">Engagement Assignments</div>
      
      <div className="flex-1 overflow-x-auto p-4 pt-0">
        <div className="flex gap-4 h-full">
          {assignments.length > 0 ? (
            assignments.map((asgn) => (
              <div key={asgn.assignment_id} className="min-w-[240px] bg-bg-abyss border border-border-subtle rounded p-3 flex flex-col justify-between">
                <div className="flex justify-between items-start">
                  <div className="flex flex-col">
                    <span className="text-[10px] text-text-muted uppercase">Interceptor</span>
                    <span className="text-text-primary text-[12px] font-bold">{asgn.interceptor_id}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-text-muted uppercase">Status</span>
                    <div className="flex items-center gap-1">
                      <div className="w-1.5 h-1.5 rounded-full bg-threat-engaged animate-pulse" />
                      <span className="text-threat-engaged text-[11px] font-bold uppercase">{asgn.status}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2 my-2">
                  <div className="flex-1 h-[1px] bg-border-subtle relative">
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1 h-1 bg-blue-bright rotate-45" />
                  </div>
                  <span className="text-[10px] text-text-muted">→</span>
                  <span className="text-text-accent text-[11px] font-mono">{asgn.track_id}</span>
                </div>
                
                <div className="flex justify-between text-[10px] font-mono uppercase">
                  <span className="text-text-muted">ETA: <span className="text-text-primary">{asgn.eta_s}S</span></span>
                  <span className="text-text-muted">RANGE: <span className="text-text-primary">{asgn.engagement_range_m}M</span></span>
                </div>
              </div>
            ))
          ) : (
            <div className="w-full flex items-center justify-center text-text-disabled text-[11px] uppercase tracking-[0.2em] italic">
              No Active Engagements
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AssignmentPanel
