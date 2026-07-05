import json
import asyncio
from fastapi import WebSocket
from ..db.models import ScoredEvent

class ConnectionManager:
    def __init__(self):
        self.active_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, event: ScoredEvent):
        if not self.active_connections:
            return
            
        payload = event.model_dump_json()
        dead = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception:
                dead.add(connection)
                
        self.active_connections -= dead
