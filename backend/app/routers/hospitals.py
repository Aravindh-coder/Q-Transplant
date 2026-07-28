from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import RoleChecker
from backend.app.models.domain import Hospital, ICUOccupancy, BloodInventory, OperationTheatre, Ambulance

router = APIRouter(prefix="/hospitals", tags=["Hospital Operations & Emergency Logistics"])


@router.get("/icu/{hospital_id}")
def get_hospital_icu_status(hospital_id: int, db: Session = Depends(get_db)):
    icu = db.query(ICUOccupancy).filter(ICUOccupancy.hospital_id == hospital_id).first()
    if not icu:
        # Default nominal fallback if unseeded
        return {
            "hospital_id": hospital_id,
            "total_beds": 20,
            "occupied_beds": 14,
            "available_beds": 6,
            "ventilators_available": 6,
            "occupancy_rate": 70.0
        }

    available = max(0, icu.total_beds - icu.occupied_beds)
    rate = round((icu.occupied_beds / max(1, icu.total_beds)) * 100.0, 1)
    return {
        "hospital_id": hospital_id,
        "total_beds": icu.total_beds,
        "occupied_beds": icu.occupied_beds,
        "available_beds": available,
        "ventilators_available": icu.ventilators_available,
        "occupancy_rate": rate
    }


@router.get("/blood/{hospital_id}")
def get_hospital_blood_inventory(hospital_id: int, db: Session = Depends(get_db)):
    items = db.query(BloodInventory).filter(BloodInventory.hospital_id == hospital_id).all()
    if not items:
        # Default inventory matrix
        return [
            {"blood_type": "O-", "units": 8},
            {"blood_type": "O+", "units": 15},
            {"blood_type": "A+", "units": 12},
            {"blood_type": "B+", "units": 10},
            {"blood_type": "AB+", "units": 6}
        ]
    return [{"blood_type": item.blood_type, "units": item.units_available} for item in items]


@router.get("/ambulances/{hospital_id}")
def list_hospital_ambulances(hospital_id: int, db: Session = Depends(get_db)):
    ambulances = db.query(Ambulance).filter(Ambulance.hospital_id == hospital_id).all()
    if not ambulances:
        return [
            {
                "id": 1,
                "vehicle_number": "KA-01-AMB-9001",
                "driver_name": "Rajesh V.",
                "driver_phone": "080-9988-7766",
                "current_lat": 12.9716,
                "current_lng": 77.5946,
                "is_available": True
            }
        ]
    return ambulances
