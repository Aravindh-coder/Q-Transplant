from fastapi import APIRouter, Depends
from app.models import User
from app.security import require_role
from app.services.hla import calculate_hla_match

router = APIRouter(prefix="/api/v1/hla", tags=["hla"])

@router.get("/health")
def hla_health(user: User = Depends(require_role("doctor", "hospital", "organizer"))):
    return {"status": "ready", "supported_markers": ["HLA-A", "HLA-B", "HLA-C", "HLA-DR", "HLA-DQ"]}
