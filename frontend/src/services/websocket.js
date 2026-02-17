const WS_URL =
  process.env.REACT_APP_WS_BASE ||
  "ws://localhost:8000/ws/ingest";

export function connectWebSocket(onMessage, onError) {
  try {
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      console.log("WebSocket connected");
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (onMessage) onMessage(message);
      } catch (err) {
        console.error("Invalid WS message:", err);
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
      if (onError) onError(err);
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
    };

    return ws;
  } catch (err) {
    console.error("WS creation failed:", err);
    return null;
  }
}
