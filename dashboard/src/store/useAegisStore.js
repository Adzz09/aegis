import { create } from 'zustand'

const useAegisStore = create((set) => ({
  // System State
  tracks: {}, // track_id -> track object
  threats: [], // List of track IDs sorted by threat score
  assignments: [], // Current engagement assignments
  systemHealth: {
    gateway: 'offline',
    sim: 'offline',
    fusion: 'offline',
    classifier: 'offline',
    optimizer: 'offline',
  },
  metrics: {
    latencyE2E: 0,
    inferenceLatency: 0,
    kafkaLag: 0,
  },
  
  // UI State
  selectedTrackId: null,
  isScenarioLoading: false,
  
  // Actions
  updateState: (newState) => set((state) => ({
    ...state,
    ...newState
  })),
  
  updateTracks: (newTracks) => set((state) => ({
    tracks: { ...state.tracks, ...newTracks }
  })),
  
  setHealth: (module, status) => set((state) => ({
    systemHealth: { ...state.systemHealth, [module]: status }
  })),
  
  selectTrack: (trackId) => set({ selectedTrackId: trackId }),
  
  setScenarioLoading: (loading) => set({ isScenarioLoading: loading }),
}))

export default useAegisStore
