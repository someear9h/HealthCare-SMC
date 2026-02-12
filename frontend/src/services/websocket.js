// WebSocket service for real-time ingestion updates
const BASE_WS = process.env.REACT_APP_WS_BASE || 'ws://localhost:8000'

export function connectWebSocket(onMessage, onError) {
  try {
    const ws = new WebSocket(`${BASE_WS}/ws`)

    ws.onopen = () => {
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        if (onMessage) onMessage(message)
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      if (onError) onError(error)
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
    }

    return ws
  } catch (e) {
    console.error('Failed to create WebSocket:', e)
    if (onError) onError(e)
    return null
  }
}
