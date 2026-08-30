from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models import User, Notification
from app.security import get_current_user
from app.services import realtime
from app.utils import to_dict_list

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.websocket("/ws")
async def notifications_ws(websocket: WebSocket, token: str = ""):
    """Live push for the DB-backed notifications above -- authenticated
    via a JWT passed as a query param (browsers can't set custom headers
    on the WebSocket upgrade request, so this is the standard pattern;
    same approach the ESP32 device socket in emergency.py uses for its
    own token). Every notify()/notify_role() call anywhere in the app
    reaches whichever of these connections match its recipient."""
    import jwt as pyjwt
    from app.config import settings
    try:
        payload = pyjwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGO])
    except pyjwt.PyJWTError:
        await websocket.close(code=4401)
        return
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == payload.get("sub")).first()
    finally:
        db.close()
    if not user or user.status in ("suspended", "inactive"):
        await websocket.close(code=4401)
        return
    await realtime.connect(websocket, user_id=user.id, role=user.role)
    try:
        while True:
            await websocket.receive_text()  # keepalive pings; content ignored
    except WebSocketDisconnect:
        pass
    finally:
        realtime.disconnect(websocket)


@router.get("/me")
def my_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (db.query(Notification)
            .filter(Notification.recipient_user_id == user.id)
            .order_by(Notification.created_at.desc()).limit(100).all())
    return to_dict_list(rows)


@router.post("/{notification_id}/read")
def mark_read(notification_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = (db.query(Notification)
           .filter(Notification.id == notification_id, Notification.recipient_user_id == user.id).first())
    if not row:
        return {"ok": True}
    row.read = True
    db.commit()
    return {"id": row.id, "read": True}
