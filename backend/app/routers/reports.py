from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import RoleChecker
from backend.app.repositories.organ_repo import OrganRepository
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.services.export_service import ExportService

router = APIRouter(prefix="/reports", tags=["Analytics & CSV/PDF Reports"])


@router.get("/export/organs", response_class=Response)
def export_organs_csv(
    db: Session = Depends(get_db),
    current_token: dict = Depends(RoleChecker(["organizer", "doctor", "hospital"]))
):
    repo = OrganRepository(db)
    organs = repo.list_available_organs()

    headers = ["ID", "Organ Type", "Blood Type", "HLA Type", "Cold Box ID", "Status", "Harvested At"]
    rows = [
        [o.id, o.organ_type, o.blood_type, o.hla_type, o.cold_box_id, o.status, str(o.harvested_at)]
        for o in organs
    ]

    csv_data = ExportService.generate_csv(headers, rows)
    return Response(content=csv_data, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=qtransplant_organs_report.csv"
    })


@router.get("/export/audit", response_class=Response)
def export_audit_csv(
    db: Session = Depends(get_db),
    current_token: dict = Depends(RoleChecker(["organizer"]))
):
    repo = AuditRepository(db)
    logs = repo.list_logs(limit=500)

    headers = ["ID", "Timestamp", "User ID", "Action", "Resource", "Details"]
    rows = [
        [l.id, str(l.timestamp), l.user_id or "SYSTEM", l.action, l.resource, l.details or ""]
        for l in logs
    ]

    csv_data = ExportService.generate_csv(headers, rows)
    return Response(content=csv_data, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=qtransplant_audit_report.csv"
    })
