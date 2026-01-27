from fastapi import APIRouter, WebSocket
from app.ws import ws_front

router = APIRouter()

@router.websocket("/ws/front/{posto_id}")
async def websocket_front(websocket: WebSocket, posto_id: int):
    await ws_front(websocket, posto_id)