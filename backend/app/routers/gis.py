"""
National Organ Command Center GIS & Live Tracking API
Provides real-time GIS data for all entities in the system.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import random
import math
from datetime import datetime

from backend.app.core.database import get_db
from backend.app.models.domain import (
    Hospital, Doctor, Patient, Donor, Organ, Ambulance, 
    Transport, Match, ICUOccupancy, BloodInventory, User
)

router = APIRouter(prefix="/gis", tags=["National Organ Command Center - GIS"])


def haversine_km(lat1, lng1, lat2, lng2):
    """Calculate distance in km between two GPS coords."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))


@router.get("/overview")
def get_gis_overview(db: Session = Depends(get_db)):
    """Full GIS overview — all entity positions, counts, and status for command center."""
    hospitals = db.query(Hospital).all()
    doctors = db.query(Doctor).all()
    donors = db.query(Donor).all()
    patients = db.query(Patient).all()
    organs = db.query(Organ).all()
    ambulances = db.query(Ambulance).all()
    active_transports = db.query(Transport).filter(Transport.status == "dispatched").all()
    pending_matches = db.query(Match).filter(Match.status == "pending").count()

    hospital_data = []
    for h in hospitals:
        icu = db.query(ICUOccupancy).filter(ICUOccupancy.hospital_id == h.id).first()
        blood = db.query(BloodInventory).filter(BloodInventory.hospital_id == h.id).all()
        # slightly jitter lat/lng for demo
        hospital_data.append({
            "id": h.id,
            "name": h.name,
            "city": h.city,
            "state": h.state,
            "address": h.address,
            "lat": h.lat + random.uniform(-0.001, 0.001),
            "lng": h.lng + random.uniform(-0.001, 0.001),
            "contact_phone": h.contact_phone,
            "doctor_count": len([d for d in doctors if d.hospital_id == h.id]),
            "patient_count": len([p for p in patients if p.hospital_id == h.id]),
            "icu_total": icu.total_beds if icu else 0,
            "icu_occupied": icu.occupied_beds if icu else 0,
            "icu_available": (icu.total_beds - icu.occupied_beds) if icu else 0,
            "icu_capacity_pct": round(icu.occupied_beds / icu.total_beds * 100, 1) if icu and icu.total_beds > 0 else 0,
            "blood_types": [{"type": b.blood_type, "units": b.units_available} for b in blood],
            "ambulance_count": len([a for a in ambulances if a.hospital_id == h.id]),
            "has_icu": bool(icu and (icu.total_beds - icu.occupied_beds) > 0),
        })

    ambulance_data = []
    for a in ambulances:
        hosp = next((h for h in hospitals if h.id == a.hospital_id), None)
        # Simulate GPS near hospital
        base_lat = hosp.lat if hosp else 12.9716
        base_lng = hosp.lng if hosp else 77.5946
        ambulance_data.append({
            "id": a.id,
            "vehicle_number": a.vehicle_number,
            "driver_name": a.driver_name,
            "driver_phone": a.driver_phone,
            "hospital_name": hosp.name if hosp else "Unknown",
            "lat": base_lat + random.uniform(-0.05, 0.05),
            "lng": base_lng + random.uniform(-0.05, 0.05),
            "is_available": a.is_available,
            "status": "available" if a.is_available else "dispatched"
        })

    donor_data = []
    for d in donors:
        user = db.query(User).filter(User.id == d.user_id).first()
        donor_data.append({
            "id": d.id,
            "name": user.full_name if user else "Unknown",
            "blood_type": d.blood_type,
            "hla_type": d.hla_type,
            "status": d.status,
            "organ_count": len([o for o in organs if o.donor_id == d.id])
        })

    patient_data = []
    for p in patients:
        user = db.query(User).filter(User.id == p.user_id).first()
        hosp = next((h for h in hospitals if h.id == p.hospital_id), None)
        patient_data.append({
            "id": p.id,
            "name": user.full_name if user else "Unknown",
            "blood_type": p.blood_type,
            "target_organ": p.target_organ,
            "urgency_score": p.urgency_score,
            "status": p.status,
            "hospital_name": hosp.name if hosp else "Unknown",
            "hospital_lat": hosp.lat if hosp else 12.9716,
            "hospital_lng": hosp.lng if hosp else 77.5946,
        })

    organ_data = []
    for o in organs:
        donor = next((d for d in donors if d.id == o.donor_id), None)
        organ_data.append({
            "id": o.id,
            "organ_type": o.organ_type,
            "blood_type": o.blood_type,
            "hla_type": o.hla_type,
            "status": o.status,
            "max_ischemia_hours": o.max_ischemia_hours,
            "cold_box_id": o.cold_box_id,
            "harvested_at": o.harvested_at.isoformat() if o.harvested_at else None,
            "viability_remaining_hours": round(
                max(0, o.max_ischemia_hours - (
                    (datetime.utcnow() - o.harvested_at).total_seconds() / 3600
                    if o.harvested_at else 0
                )), 2
            ),
        })

    return {
        "summary": {
            "total_hospitals": len(hospitals),
            "total_doctors": len(doctors),
            "total_donors": len(donors),
            "total_patients": len(patients),
            "total_organs": len(organs),
            "available_organs": len([o for o in organs if o.status == "available"]),
            "total_ambulances": len(ambulances),
            "available_ambulances": len([a for a in ambulances if a.is_available]),
            "active_transports": len(active_transports),
            "pending_matches": pending_matches,
            "patients_waiting": len([p for p in patients if p.status == "waiting_list"]),
        },
        "hospitals": hospital_data,
        "ambulances": ambulance_data,
        "donors": donor_data,
        "patients": patient_data,
        "organs": organ_data,
        "center": {"lat": 20.5937, "lng": 78.9629, "zoom": 5},  # India center
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/hospitals")
def get_hospitals_gis(db: Session = Depends(get_db)):
    """All hospitals with GIS data and capacity."""
    hospitals = db.query(Hospital).all()
    result = []
    for h in hospitals:
        icu = db.query(ICUOccupancy).filter(ICUOccupancy.hospital_id == h.id).first()
        result.append({
            "id": h.id, "name": h.name, "city": h.city, "state": h.state,
            "lat": h.lat, "lng": h.lng, "contact_phone": h.contact_phone,
            "icu_available": (icu.total_beds - icu.occupied_beds) if icu else 0,
            "icu_pct": round(icu.occupied_beds / icu.total_beds * 100, 1) if icu and icu.total_beds > 0 else 0,
        })
    return result


@router.get("/nearest-icu")
def find_nearest_icu(lat: float = 12.9716, lng: float = 77.5946, db: Session = Depends(get_db)):
    """Find nearest hospital with ICU availability."""
    hospitals = db.query(Hospital).all()
    candidates = []
    for h in hospitals:
        icu = db.query(ICUOccupancy).filter(ICUOccupancy.hospital_id == h.id).first()
        if icu and (icu.total_beds - icu.occupied_beds) > 0:
            dist = haversine_km(lat, lng, h.lat, h.lng)
            candidates.append({
                "hospital_id": h.id, "name": h.name, "city": h.city,
                "lat": h.lat, "lng": h.lng, "distance_km": round(dist, 2),
                "icu_available": icu.total_beds - icu.occupied_beds,
            })
    candidates.sort(key=lambda x: x["distance_km"])
    return candidates[:5]


@router.get("/stats")
def get_national_stats(db: Session = Depends(get_db)):
    """Live national statistics for command center KPIs."""
    return {
        "total_hospitals": db.query(Hospital).count(),
        "total_doctors": db.query(Doctor).count(),
        "total_donors": db.query(Donor).count(),
        "total_patients": db.query(Patient).count(),
        "organs_available": db.query(Organ).filter(Organ.status == "available").count(),
        "organs_total": db.query(Organ).count(),
        "pending_matches": db.query(Match).filter(Match.status == "pending").count(),
        "approved_matches": db.query(Match).filter(Match.status == "approved").count(),
        "active_transports": db.query(Transport).filter(Transport.status == "dispatched").count(),
        "ambulances_available": db.query(Ambulance).filter(Ambulance.is_available == True).count(),
    }
