import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Grid, Line, Float } from '@react-three/drei'
import * as THREE from 'three'
import useAegisStore from '../store/useAegisStore'

const MAP_COLORS = {
  terrain: 0x0D1A2D,
  terrain_grid: 0x1A2D4A,
  zone_fill: 0x1565C0,
  zone_border: 0x1E88E5,
  track_cleared: 0x10B981,
  track_unknown: 0xF59E0B,
  track_caution: 0xF97316,
  track_hostile: 0xEF4444,
  track_critical: 0xDC2626,
  track_engaged: 0x8B5CF6,
  interception_line: 0xA78BFA,
};

const Track = ({ track, isSelected }) => {
  const meshRef = useRef()
  const color = MAP_COLORS[`track_${track.threat_level === 'ENGAGED' ? 'engaged' : (track.threat_level || 'unknown').toLowerCase()}`] || MAP_COLORS.track_unknown
  
  const position = [track.pos_x / 100, track.pos_z / 100, -track.pos_y / 100]

  useFrame((state) => {
    if (meshRef.current) {
      const s = 1 + Math.sin(state.clock.elapsedTime * (track.threat_level === 'CRITICAL' ? 10 : 2)) * 0.1
      meshRef.current.scale.set(s, s, s)
    }
  })

  return (
    <group position={position}>
      <mesh ref={meshRef}>
        <sphereGeometry args={[0.5, 16, 16]} />
        <meshBasicMaterial color={color} />
      </mesh>
      
      {/* Uncertainty Ring */}
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.8, 0.9, 32]} />
        <meshBasicMaterial color={color} transparent opacity={0.3} />
      </mesh>

      {/* Trajectory Arc (Simple Line) */}
      <Line
        points={[[0, 0, 0], [track.vel_x / 10, track.vel_z / 10, -track.vel_y / 10]]}
        color={color}
        lineWidth={1}
        transparent
        opacity={0.5}
      />
    </group>
  )
}

const EngagementBeam = ({ start, end }) => {
  return (
    <Line
      points={[start, end]}
      color={MAP_COLORS.interception_line}
      lineWidth={2}
      transparent
      opacity={0.6}
      dashed
      dashScale={2}
      gapSize={1}
    />
  )
}

const TacticalMap = () => {
  const { tracks, assignments, selectedTrackId } = useAegisStore()
  
  // Simulated interceptor positions
  const interceptors = {
    "INT-01": [5, 2, -5],
    "INT-02": [-5, 2, -5],
    "INT-03": [5, 2, 5],
    "INT-04": [-5, 2, 5],
  }

  return (
    <div className="flex-1 bg-bg-deep relative overflow-hidden">
      <Canvas camera={{ position: [0, 80, 80], fov: 45 }}>
        <color attach="background" args={['#080C14']} />
        
        <Grid 
          infiniteGrid 
          fadeDistance={200} 
          fadeStrength={5} 
          cellSize={10} 
          sectionSize={50}
          sectionColor={MAP_COLORS.terrain_grid}
          cellColor={MAP_COLORS.terrain}
        />
        
        <ambientLight intensity={0.5} />
        
        {/* Protected Zone */}
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.1, 0]}>
          <ringGeometry args={[0, 20, 64]} />
          <meshBasicMaterial color={MAP_COLORS.zone_fill} transparent opacity={0.1} />
        </mesh>
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.1, 0]}>
          <ringGeometry args={[19.8, 20, 64]} />
          <meshBasicMaterial color={MAP_COLORS.zone_border} />
        </mesh>

        {/* Tracks */}
        {Object.values(tracks).map((track) => (
          <Track 
            key={track.track_id} 
            track={track}
            isSelected={selectedTrackId === track.track_id}
          />
        ))}

        {/* Engagement Beams */}
        {assignments.map((asgn) => {
          const track = tracks[asgn.track_id]
          const intPos = interceptors[asgn.interceptor_id]
          if (track && intPos) {
            const trackPos = [track.pos_x / 100, track.pos_z / 100, -track.pos_y / 100]
            return <EngagementBeam key={asgn.assignment_id} start={intPos} end={trackPos} />
          }
          return null
        })}

        {/* Interceptors */}
        {Object.entries(interceptors).map(([id, pos]) => (
          <mesh key={id} position={pos}>
            <boxGeometry args={[1, 0.5, 1]} />
            <meshBasicMaterial color={MAP_COLORS.track_engaged} />
          </mesh>
        ))}

        <OrbitControls makeDefault />
      </Canvas>

      {/* Overlay UI */}
      <div className="absolute top-4 left-4 flex flex-col gap-2">
        <div className="bg-bg-void/80 backdrop-blur-md border border-border-subtle p-3 rounded font-mono">
          <div className="text-[10px] text-text-muted uppercase mb-1">Sector Control</div>
          <div className="text-[12px] text-blue-glow font-bold">NORAD-WEST-04</div>
          <div className="h-[1px] bg-border-subtle my-2" />
          <div className="text-[9px] text-text-secondary">
            GRID: 10Q KH 420 690<br />
            ALT: MSL 1420 FT
          </div>
        </div>
      </div>
    </div>
  )
}

export default TacticalMap
