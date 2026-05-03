import useAegisStore from '../store/useAegisStore'

let ws = null
let reconnectInterval = 1000

export const connectWebSocket = () => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const url = import.meta.env.VITE_WS_URL || `${protocol}//${window.location.host}/ws/state`
  
  ws = new WebSocket(url)

  ws.onopen = () => {
    console.log('Connected to AEGIS Gateway')
    useAegisStore.getState().setHealth('gateway', 'online')
    reconnectInterval = 1000
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    useAegisStore.getState().updateState(data)
  }

  ws.onclose = () => {
    console.log('Disconnected from AEGIS Gateway')
    useAegisStore.getState().setHealth('gateway', 'offline')
    
    // Simple exponential backoff reconnect
    setTimeout(() => {
      console.log('Reconnecting...')
      reconnectInterval = Math.min(reconnectInterval * 2, 30000)
      connectWebSocket()
    }, reconnectInterval)
  }

  ws.onerror = (error) => {
    console.error('WebSocket Error:', error)
    ws.close()
  }
}

export const sendMessage = (message) => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(message))
  }
}
