"""General-purpose real-time event bus for authenticated dashboard clients
(doctor/hospital/organizer/donor browser sessions) -- distinct from the
ESP32 hardware protocol in emergency.py, which has its own connection
list and device-token auth.

Connections are tracked with their user_id/role so events can be targeted
(a doctor-approval notification should only reach that doctor, not every
connected client). REST remains the authoritative CRUD interface; this is
push-only convenience on top of it.

notify()/notify_role() in notifications.py call publish_sync() after
writing the DB Notification row, so every existing call site becomes
real-time automatically with no changes needed at each call site.
"""
import asyncio
import json
import logging
from typing import Optional
from fastapi import WebSocket

logger = logging.getLogger("qtransplant.realtime")

# {WebSocket: {"user_id": str, "role": str}}
CLIENTS: dict = {}

# Captured at app startup (main.py) so publish_sync() can safely schedule
# a broadcast from synchronous route handlers, which run outside the
# event loop that owns these WebSocket connections.
MAIN_LOOP: Optional[asyncio.AbstractEventLoop] = None


def set_main_loop(loop: asyncio.AbstractEventLoop):
    global MAIN_LOOP
    MAIN_LOOP = loop


async def connect(ws: WebSocket, user_id: str, role: str):
    await ws.accept()
    CLIENTS[ws] = {"user_id": user_id, "role": role}


def disconnect(ws: WebSocket):
    CLIENTS.pop(ws, None)


async def publish(event: str, payload: dict, user_id: Optional[str] = None, role: Optional[str] = None):
    """Broadcasts to matching connected clients. user_id/role narrow the
    audience; both None means every connected client (use sparingly)."""
    message = json.dumps({"event": event, "data": payload}, default=str)
    dead = []
    for ws, meta in list(CLIENTS.items()):
        if user_id is not None and meta["user_id"] != user_id:
            continue
        if role is not None and meta["role"] != role:
            continue
        try:
            await ws.send_text(message)
        except Exception:
            dead.append(ws)
    for ws in dead:
        CLIENTS.pop(ws, None)


def publish_sync(event: str, payload: dict, user_id: Optional[str] = None, role: Optional[str] = None):
    """Callable from ordinary synchronous route handlers (most of this
    codebase). Never raises -- a real-time push failing should never
    break the REST call that triggered it; the REST response and DB
    Notification row are always the source of truth regardless."""
    if MAIN_LOOP is None:
        return
    try:
        asyncio.run_coroutine_threadsafe(publish(event, payload, user_id, role), MAIN_LOOP)
    except Exception:
        logger.exception("Failed to schedule real-time publish for event=%s", event)
