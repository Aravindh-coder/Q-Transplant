from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import RoleChecker
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


@router.get("/all-detailed")
def get_all_users_detailed(
    db: Session = Depends(get_db),
    current_token: dict = Depends(RoleChecker(["organizer"]))
):
    """Returns all users grouped by role — for Organizer master dashboard."""
    from backend.app.models.domain import User, Doctor, Hospital, Donor, Patient
    users = db.query(User).all()
    result = {
        "doctors": [],
        "hospitals": [],
        "donors": [],
        "patients": [],
        "organizers": [],
        "pending": []
    }
    for u in users:
        entry = {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role,
            "phone": u.phone,
            "is_approved": u.is_approved,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        role_key = u.role.lower() + "s" if u.role.lower() not in ("organizer",) else "organizers"
        if role_key in result:
            result[role_key].append(entry)
        if not u.is_approved and u.role.lower() != "organizer":
            result["pending"].append(entry)
    return result


@router.get("/pending-approvals", response_model=List[UserOut])
def list_pending_approvals(
    db: Session = Depends(get_db),
    current_token: dict = Depends(RoleChecker(["organizer"]))
):
    repo = UserRepository(db)
    return repo.list_users(approved_only=False)


@router.get("/quick-approve", response_class=HTMLResponse)
def quick_approve_or_reject_via_email(
    user_id: int = Query(...),
    approve: bool = Query(...),
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """One-click GET endpoint invoked directly from Organizer executive email."""
    verified_id = EmailService.verify_quick_approval_token(token)
    if not verified_id or verified_id != user_id:
        return HTMLResponse(content="""
        <html style="background-color: #161616; color: #f4f4f4; font-family: sans-serif; padding: 40px;">
            <div style="max-width: 500px; margin: 0 auto; background: #262626; border-top: 4px solid #da1e28; padding: 30px;">
                <h2 style="color: #da1e28;">Security Error: Invalid or Expired Token</h2>
                <p>The quick approval link is invalid or has expired. Please log in to the Q-Transplant Organizer Portal to review this user request manually.</p>
                <a href="http://localhost:5173" style="color: #0f62fe;">Go to Q-Transplant Portal</a>
            </div>
        </html>
        """, status_code=400)

    repo = UserRepository(db)
    audit = AuditRepository(db)

    user = repo.update_approval(user_id, approve)
    if not user:
        raise HTTPException(status_code=404, detail="Target user profile not found.")

    status_str = "APPROVED" if approve else "REJECTED"
    color = "#24a148" if approve else "#da1e28"

    audit.log_action(
        user_id=1,  # System Admin / Organizer
        action=f"EMAIL_QUICK_{status_str}",
        resource="User",
        details=f"One-click executive email action for {user.email} -> {status_str}"
    )

    # Dispatches email to Doctor
    EmailService.send_approval_status(user.email, user.full_name, approve, "One-Click Executive Action by Organizer")

    return HTMLResponse(content=f"""
    <html style="background-color: #161616; color: #f4f4f4; font-family: 'Helvetica Neue', sans-serif; padding: 50px;">
        <head><title>Q-Transplant - User {status_str}</title></head>
        <body>
            <div style="max-width: 550px; margin: 0 auto; background: #262626; border-top: 4px solid {color}; padding: 35px; border-radius: 4px; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
                <h2 style="color: {color}; margin-top: 0;">User Registration {status_str}</h2>
                <p style="font-size: 16px;">Action successfully executed for <strong>{user.full_name}</strong> ({user.email}).</p>
                <div style="background: #161616; padding: 15px; border-left: 3px solid {color}; margin: 20px 0;">
                    <p style="margin: 4px 0;"><strong>Status:</strong> <span style="color: {color}; font-weight: bold;">{status_str}</span></p>
                    <p style="margin: 4px 0;"><strong>Role:</strong> {user.role.upper()}</p>
                    <p style="margin: 4px 0;"><strong>Notification Email:</strong> Dispatched to {user.email}</p>
                </div>
                <p>The applicant's account state has been updated live in the database.</p>
                <div style="margin-top: 25px;">
                    <a href="http://localhost:5174" style="background-color: #0f62fe; color: white; padding: 10px 20px; text-decoration: none; font-weight: bold; border-radius: 2px;">RETURN TO ORGANIZER DASHBOARD</a>
                </div>
            </div>
        </body>
    </html>
    """)


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


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_token: dict = Depends(RoleChecker(["organizer"]))
):
    """Allows Organizer to permanently remove a Doctor or User profile."""
    repo = UserRepository(db)
    audit = AuditRepository(db)

    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Target user not found.")

    if user.role.lower() == "organizer":
        raise HTTPException(status_code=400, detail="Cannot delete organizer admin user.")

    email = user.email
    name = user.full_name
    role = user.role

    from backend.app.models.domain import User, Doctor, Hospital, Donor, Patient
    if role.lower() == "doctor":
        db.query(Doctor).filter(Doctor.user_id == user_id).delete()
    elif role.lower() == "hospital":
        db.query(Hospital).filter(Hospital.user_id == user_id).delete()
    elif role.lower() == "donor":
        db.query(Donor).filter(Donor.user_id == user_id).delete()
    elif role.lower() == "patient":
        db.query(Patient).filter(Patient.user_id == user_id).delete()

    db.query(User).filter(User.id == user_id).delete()
    db.commit()

    admin_id = int(current_token.get("sub", 1))
    audit.log_action(
        user_id=admin_id,
        action="DELETE_USER",
        resource="User",
        details=f"Organizer removed {role} user: {name} ({email})"
    )

    return {"message": f"Successfully removed {role} {name} ({email}) from system.", "user_id": user_id}
