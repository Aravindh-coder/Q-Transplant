from fastapi import APIRouter, Depends
from app.models import User
from app.security import require_role

router = APIRouter(prefix="/api/v1/transplants", tags=["transplants"])

@router.get("/health")
def transplant_api_health(user: User = Depends(require_role("doctor", "hospital", "organizer"))):
    return {"status": "ready", "message": "Transplant coordination API available"}
