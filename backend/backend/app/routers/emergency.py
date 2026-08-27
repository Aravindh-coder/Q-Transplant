"""
Q-Transplant — Emergency Network
Persists emergency requests and supports authenticated real-time WebSocket state.
"""
import json
from datetime import datetime, timezone
from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import SessionLocal, get_db
from app.models import User, HospitalProfile, EmergencyRequest, Device
from app.security import require_role
from app.services.audit import log_action

router = APIRouter(prefix="/api/v1/emergency", tags=["emergency"])
CONNECTIONS: List[WebSocket] = []
DEVICE_TOKEN_HASHES: Dict[str, str] = {}

def now_iso(): return datetime.now(timezone.utc).isoformat()

def _hospital_state(db):
    out={}
    for h in db.query(HospitalProfile).all():
        req=(db.query(EmergencyRequest).filter(EmergencyRequest.hospital_id==h.id, EmergencyRequest.status.notin_(["RESOLVED","CANCELLED"])).order_by(EmergencyRequest.created_at.desc()).first())
        out[h.id]={"name":h.hospital_name,"status":"idle" if not req else ("donor_found" if req.responding_hospital_id else "emergency"),"requirement":req.requirement if req else ""}
    return out

async def broadcast(payload):
    dead=[]
    for ws in CONNECTIONS:
        try: await ws.send_text(json.dumps(payload,default=str))
        except Exception: dead.append(ws)
    for ws in dead:
        if ws in CONNECTIONS: CONNECTIONS.remove(ws)

async def broadcast_state():
    db=SessionLocal()
    try: await broadcast({"type":"state","hospitals":_hospital_state(db),"timestamp":now_iso()})
    finally: db.close()

class EmergencyIn(BaseModel):
    requirement: str

@router.post("/create")
async def create_emergency(body: EmergencyIn, user: User = Depends(require_role("doctor","hospital")), db: Session = Depends(get_db)):
    hospital_id = None
    if user.role == "hospital":
        h=db.query(HospitalProfile).filter(HospitalProfile.user_id==user.id).first()
        hospital_id=h.id if h else None
    else:
        from app.models import DoctorProfile
        d=db.query(DoctorProfile).filter(DoctorProfile.user_id==user.id).first()
        hospital_id=d.hospital_id if d else None
    if not hospital_id: raise HTTPException(400,"Your account is not linked to a hospital.")
    req=EmergencyRequest(hospital_id=hospital_id,raised_by=user.id,requirement=body.requirement,status="NOTIFIED")
    db.add(req); db.commit(); db.refresh(req)
    log_action(db,"EMERGENCY_CREATED",user_id=user.id,target=req.id,meta={"requirement":body.requirement})
    await broadcast_state()
    return {"id":req.id,"status":req.status,"hospital_id":hospital_id}

@router.get("")
def list_emergencies(user: User = Depends(require_role("doctor","hospital","organizer")), db: Session = Depends(get_db)):
    q=db.query(EmergencyRequest).order_by(EmergencyRequest.created_at.desc())
    if user.role=="hospital":
        h=db.query(HospitalProfile).filter(HospitalProfile.user_id==user.id).first()
        if h: q=q.filter(EmergencyRequest.hospital_id==h.id)
    return [{"id":x.id,"hospital_id":x.hospital_id,"requirement":x.requirement,"status":x.status,"created_at":x.created_at,"resolved_at":x.resolved_at} for x in q.limit(100).all()]

@router.websocket("/ws")
async def emergency_ws(websocket: WebSocket, hospital_id: str = "", device_token: str = ""):
    from app.security import verify_password
    if device_token:
        expected=DEVICE_TOKEN_HASHES.get(hospital_id)
        if not expected or not verify_password(device_token,expected):
            await websocket.close(code=4401); return
    await websocket.accept(); CONNECTIONS.append(websocket)
    db=SessionLocal()
    try: await websocket.send_text(json.dumps({"type":"state","hospitals":_hospital_state(db),"timestamp":now_iso()}))
    finally: db.close()
    try:
        while True:
            msg=json.loads(await websocket.receive_text()); hid=msg.get("hospital_id")
            if not hid: continue
            db=SessionLocal()
            try:
                hospital=db.query(HospitalProfile).filter(HospitalProfile.id==hid).first()
                if not hospital: continue
                if msg.get("type")=="emergency":
                    req=EmergencyRequest(hospital_id=hid,requirement=msg.get("requirement",""),status="NOTIFIED"); db.add(req); db.commit(); log_action(db,"EMERGENCY_CREATED",target=hid,meta={"requirement":msg.get("requirement","")})
                elif msg.get("type")=="requirement_update":
                    req=(db.query(EmergencyRequest).filter(EmergencyRequest.hospital_id==hid,EmergencyRequest.status.notin_(["RESOLVED","CANCELLED"])).order_by(EmergencyRequest.created_at.desc()).first())
                    if req: req.requirement=msg.get("requirement",""); db.commit()
                elif msg.get("type")=="donor_found":
                    target=msg.get("target_hospital_id"); req=(db.query(EmergencyRequest).filter(EmergencyRequest.hospital_id==target,EmergencyRequest.status.notin_(["RESOLVED","CANCELLED"])).order_by(EmergencyRequest.created_at.desc()).first())
                    if req: req.responding_hospital_id=hid; req.status="ACKNOWLEDGED"; db.commit(); log_action(db,"MATCH_GENERATED",target=target,meta={"responding_hospital":hid})
                elif msg.get("type")=="acknowledge":
                    req=(db.query(EmergencyRequest).filter(EmergencyRequest.hospital_id==hid,EmergencyRequest.status.notin_(["RESOLVED","CANCELLED"])).order_by(EmergencyRequest.created_at.desc()).first())
                    if req: req.status="RESOLVED"; req.resolved_at=datetime.now(timezone.utc); db.commit(); log_action(db,"EMERGENCY_ACKNOWLEDGED",target=hid)
                device=db.query(Device).filter(Device.hospital_id==hid).first()
                if device: device.last_seen=datetime.now(timezone.utc); device.connection_status="online"; db.commit()
            finally: db.close()
            await broadcast_state()
    except WebSocketDisconnect:
        if websocket in CONNECTIONS: CONNECTIONS.remove(websocket)
