from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# ########################################################################
# HUGE CHANGE: ENSURING CORRECT IMPORT FROM UPDATED SERVICE
# ########################################################################
from services.ingestion_service import get_recent, get_failed
from core.ws_manager import manager

router = APIRouter(prefix="/logs", tags=["Logs & Real-time Stream"])

@router.get("/recent")
async def get_recent_transactions_log():
    """Returns the last 50 individual patient transactions."""
    return get_recent(50)

@router.get("/failed")
async def get_failed_transactions_log():
    """Returns the last 50 failed ingestion attempts for debugging."""
    return get_failed(50)

@router.websocket("/ws/ingest")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket for the Live Command Center feed.
    Broadcasts every 'CASE' or 'VACCINATION' event immediately.
    """
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)