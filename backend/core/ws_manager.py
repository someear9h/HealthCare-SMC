from typing import List
from fastapi import WebSocket
import asyncio


class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, message: dict):
        living = []
        for conn in list(self.active):
            try:
                await conn.send_json(message)
                living.append(conn)
            except Exception:
                try:
                    conn.close()
                except Exception:
                    pass
        self.active = living


manager = ConnectionManager()
