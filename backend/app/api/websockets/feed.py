import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.api.websockets.connection_manager import manager
from backend.app.services.fraud_detector import fraud_detector
from backend.app.models.schemas.transaction import EnrichedTransaction

router = APIRouter(tags=["WebSockets"])

def on_transaction_processed(enriched: EnrichedTransaction):
    data = enriched.model_dump(mode="json")
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(manager.broadcast(data))
    except RuntimeError:
        pass

fraud_detector.register_listener(on_transaction_processed)

@router.websocket("/ws/stream")
async def websocket_stream_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({"type": "CONNECTION_ESTABLISHED", "message": "Connected to ShieldPlus AI Real-Time Feed"})
        while True:
            await websocket.receive_text()
    except (WebSocketDisconnect, Exception):
        manager.disconnect(websocket)

