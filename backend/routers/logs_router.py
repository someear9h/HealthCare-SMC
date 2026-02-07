from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.ingestion_service import get_recent, get_failed
from core.ws_manager import manager

router = APIRouter(prefix="/logs")


@router.get("/recent")
async def recent():
    return get_recent(50)


@router.get("/failed")
async def failed():
    return get_failed(50)


@router.websocket("/ws/ingest")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # keep connection open; clients can send pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
