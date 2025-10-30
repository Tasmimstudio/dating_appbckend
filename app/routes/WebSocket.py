# app/routes/WebSocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

active_connections = []

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    active_connections.append((client_id, websocket))
    try:
        while True:
            data = await websocket.receive_text()
            # Echo message back (for testing)
            await websocket.send_text(f"Client {client_id} says: {data}")
    except WebSocketDisconnect:
        active_connections.remove((client_id, websocket))
        print(f"Client {client_id} disconnected.")
