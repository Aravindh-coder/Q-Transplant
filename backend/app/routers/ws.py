from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.core.websockets import ws_manager

router = APIRouter(tags=["WebSocket Real-Time Sync"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo heartbeat or client ack
            await websocket.send_json({"type": "ACK", "payload": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
