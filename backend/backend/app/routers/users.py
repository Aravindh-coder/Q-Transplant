from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.security import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "full_name": user.full_name, "email": user.email, "role": user.role, "status": user.status}

@router.get("/{user_id}")
def get_user(user_id: str, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current.role != "organizer" and current.id != user_id:
        raise HTTPException(403, "Not authorized")
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, "User not found")
    return {"id": user.id, "full_name": user.full_name, "email": user.email, "role": user.role, "status": user.status}
