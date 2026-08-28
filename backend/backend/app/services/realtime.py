"""Small in-process realtime event bus; REST remains the CRUD interface."""
import asyncio
import json
from typing import Set
from fastapi import WebSocket

CLIENTS: Set[WebSocket] = set()

async def connect(ws: WebSocket):
    await ws.accept(); CLIENTS.add(ws)

async def disconnect(ws: WebSocket):
    CLIENTS.discard(ws)

async def publish(event: str, payload: dict):
    message = json.dumps({"event": event, "data": payload}, default=str)
    dead=[]
    for ws in list(CLIENTS):
        try: await ws.send_text(message)
        except Exception: dead.append(ws)
    for ws in dead: CLIENTS.discard(ws)
