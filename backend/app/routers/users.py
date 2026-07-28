from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import RoleChecker, decode_token, oauth2_scheme
from backend.app.core.email import EmailService
from backend.app.repositories.user_repo import UserRepository
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.schemas.domain import UserOut, ApprovalAction

router = APIRouter(prefix="/users", tags=["User Management & RBAC Approvals"])


@router.get("/", response_model=List[UserOut])
def list_all_users(
    role: Optional[str] = None,
    approved_only: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_token: dict = Depends(RoleChecker(["organizer"]))
):
    repo = UserRepository(db)
    return repo.list_users(role=role, approved_only=approved_only)


@router.get("/pending-approvals", response_model=List[UserOut])
def list_pending_approvals(
    db: Session = Depends(get_db),
    current_token: dict = Depends(RoleChecker(["organizer"]))
):
    repo = UserRepository(db)
    return repo.list_users(approved_only=False)


@router.post("/approve", response_model=UserOut)
def approve_or_reject_user(
    action: ApprovalAction,
    db: Session = Depends(get_db),
    current_token: dict = Depends(RoleChecker(["organizer"]))
):
    repo = UserRepository(db)
    audit = AuditRepository(db)

    user = repo.update_approval(action.user_id, action.approve)
    if not user:
        raise HTTPException(status_code=404, detail="User target not found.")

    admin_id = int(current_token.get("sub"))
    status_str = "APPROVED" if action.approve else "REJECTED"

    audit.log_action(
        user_id=admin_id,
        action=f"USER_{status_str}",
        resource="User",
        details=f"Updated status for user {user.email}: {action.reason}"
    )

    EmailService.send_approval_status(user.email, user.full_name, action.approve, action.reason or "")
    return user
