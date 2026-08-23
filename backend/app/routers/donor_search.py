"""
Donor Search router — bulk donor pool (uploaded by doctors via CSV) + a
Grover's-algorithm-styled live search that ranks the pool against a single
patient's medical profile.

The pool is kept in-memory (module-level), the same pattern already used by
emergency.py, so no DB migration is required for the demo.
"""
import csv
import io
import math
import random
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel

router = APIRouter(prefix="/donor-search", tags=["Donor Pool & Grover Search"])

# ── In-memory donor pool (populated via CSV upload by doctors, or demo-seeded) ──
_donor_pool: List[dict] = []

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
ORGAN_TYPES = ["Kidney", "Heart", "Liver", "Lung", "Pancreas", "Cornea"]
INDIAN_CITIES = ["Bengaluru", "Mumbai", "Delhi", "Chennai", "Hyderabad", "Pune", "Kolkata", "Ahmedabad"]
HLA_A = ["A1", "A2", "A3", "A11", "A24"]
HLA_B = ["B7", "B8", "B27", "B35", "B44"]
HLA_DR = ["DR1", "DR2", "DR3", "DR4", "DR7"]

ABO_COMPATIBILITY = {
    "O-": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
    "O+": ["O+", "A+", "B+", "AB+"],
    "A-": ["A-", "A+", "AB-", "AB+"],
    "A+": ["A+", "AB+"],
    "B-": ["B-", "B+", "AB-", "AB+"],
    "B+": ["B+", "AB+"],
    "AB-": ["AB-", "AB+"],
    "AB+": ["AB+"],
}


def _gen_hla() -> str:
    return f"{random.choice(HLA_A)},{random.choice(HLA_B)},{random.choice(HLA_DR)}"


def _hla_similarity(hla_d: str, hla_p: str) -> float:
    d = set(x.strip().upper() for x in (hla_d or "").split(",") if x.strip())
    p = set(x.strip().upper() for x in (hla_p or "").split(",") if x.strip())
    if not d or not p:
        return 50.0
    return round((len(d & p) / len(d | p)) * 100.0, 2)


def _haversine_km(lat1, lng1, lat2, lng2) -> float:
    try:
        r = 6371.0
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2 - lat1)
        dl = math.radians(lng2 - lng1)
        a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
        return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    except Exception:
        return 25.0


class PatientSearchRequest(BaseModel):
    patient_name: Optional[str] = "Patient"
    target_organ: str
    blood_type: str
    hla_type: str
    urgency_score: int = 5
    age: Optional[int] = None
    patient_lat: float = 12.9716
    patient_lng: float = 77.5946
    max_ischemia_hours: Optional[float] = None
    top_n: int = 10


# ── Seed a large synthetic donor pool (stand-in for "1000s of donors saved by doctors") ──
@router.post("/seed-demo")
def seed_demo_pool(count: int = 1000, append: bool = False):
    if count < 1 or count > 20000:
        raise HTTPException(status_code=400, detail="count must be between 1 and 20000")

    if not append:
        _donor_pool.clear()

    for i in range(count):
        organ = random.choice(ORGAN_TYPES)
        city = random.choice(INDIAN_CITIES)
        _donor_pool.append({
            "id": str(uuid.uuid4())[:8],
            "donor_name": f"Donor-{len(_donor_pool) + 1:05d}",
            "hospital": f"{random.choice(['Apollo', 'Fortis', 'AIIMS', 'Manipal', 'Narayana', 'Max', 'Medanta', 'CMC'])} {city}",
            "city": city,
            "organ_type": organ,
            "blood_type": random.choice(BLOOD_GROUPS),
            "hla_type": _gen_hla(),
            "age": random.randint(18, 65),
            "max_ischemia_hours": round(random.uniform(2.0, 12.0), 1),
            "lat": round(12.9716 + random.uniform(-8.0, 8.0), 4),
            "lng": round(77.5946 + random.uniform(-8.0, 8.0), 4),
            "registered_by": "Dr. " + random.choice(["Sharma", "Reddy", "Iyer", "Khan", "Nair", "Gupta"]),
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic",
        })

    return {"status": "SEEDED", "pool_size": len(_donor_pool)}


# ── Doctors upload real donor CSVs here (cumulative — appends to the pool) ──
@router.post("/upload-csv", status_code=status.HTTP_201_CREATED)
async def upload_donor_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    raw = await file.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV appears empty or malformed")

    # Flexible header mapping so doctors' real-world exports still work
    def col(row: dict, *names, default=""):
        for n in names:
            for key in row:
                if key and key.strip().lower() == n:
                    return (row[key] or "").strip()
        return default

    added, skipped = 0, 0
    for row in reader:
        organ = col(row, "organ_type", "organ")
        blood = col(row, "blood_type", "blood_group", "bloodtype")
        if not organ or not blood:
            skipped += 1
            continue
        try:
            lat = float(col(row, "lat", "latitude", default="12.9716") or 12.9716)
            lng = float(col(row, "lng", "longitude", default="77.5946") or 77.5946)
        except ValueError:
            lat, lng = 12.9716, 77.5946
        try:
            age = int(col(row, "age", "donor_age", default="35") or 35)
        except ValueError:
            age = 35
        try:
            max_isch = float(col(row, "max_ischemia_hours", "cold_ischemia_hours", default="6") or 6)
        except ValueError:
            max_isch = 6.0

        _donor_pool.append({
            "id": str(uuid.uuid4())[:8],
            "donor_name": col(row, "donor_name", "name", default=f"Donor-{len(_donor_pool) + 1:05d}"),
            "hospital": col(row, "hospital", "hospital_name", default="Unregistered Hospital"),
            "city": col(row, "city", default="Bengaluru"),
            "organ_type": organ.title(),
            "blood_type": blood.upper(),
            "hla_type": col(row, "hla_type", "hla", default=_gen_hla()),
            "age": age,
            "max_ischemia_hours": max_isch,
            "lat": lat,
            "lng": lng,
            "registered_by": col(row, "registered_by", "doctor", default="Attending Doctor"),
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "source": "csv_upload",
        })
        added += 1

    return {
        "status": "UPLOADED",
        "rows_added": added,
        "rows_skipped": skipped,
        "pool_size": len(_donor_pool),
    }


@router.get("/pool-stats")
def pool_stats():
    by_organ: dict = {}
    by_blood: dict = {}
    for d in _donor_pool:
        by_organ[d["organ_type"]] = by_organ.get(d["organ_type"], 0) + 1
        by_blood[d["blood_type"]] = by_blood.get(d["blood_type"], 0) + 1
    return {
        "pool_size": len(_donor_pool),
        "by_organ": by_organ,
        "by_blood_type": by_blood,
    }


@router.delete("/pool")
def clear_pool():
    _donor_pool.clear()
    return {"status": "CLEARED", "pool_size": 0}


# ── The core search: score every donor, rank, return top N + Grover metadata ──
@router.post("/search")
def search_donors(payload: PatientSearchRequest):
    n = len(_donor_pool)
    if n == 0:
        raise HTTPException(status_code=400, detail="Donor pool is empty — upload a CSV or seed demo donors first.")

    scored = []
    for d in _donor_pool:
        if d["organ_type"].lower() != payload.target_organ.lower():
            continue
        allowed = ABO_COMPATIBILITY.get(d["blood_type"], [])
        abo_ok = payload.blood_type in allowed
        hla_score = _hla_similarity(d["hla_type"], payload.hla_type)
        urgency_score = min(100.0, max(1, payload.urgency_score) * 10.0)
        distance_km = round(_haversine_km(payload.patient_lat, payload.patient_lng, d["lat"], d["lng"]), 1)
        transit_hrs = (distance_km / 50.0) + 0.5
        max_isch = d.get("max_ischemia_hours") or 6.0
        ischemia_decay = max(0.0, (1.0 - (transit_hrs / max_isch))) * 100.0
        distance_score = max(0.0, 100.0 - (distance_km * 0.8))

        overall = (
            (hla_score * 0.40) +
            (urgency_score * 0.25) +
            (ischemia_decay * 0.20) +
            (distance_score * 0.15)
        )
        if not abo_ok:
            overall = 0.0
        overall = round(min(100.0, max(0.0, overall)), 2)

        scored.append({
            **d,
            "match_score": overall,
            "abo_compatible": abo_ok,
            "hla_score": hla_score,
            "distance_km": distance_km,
            "eta_minutes": round((distance_km / 45.0) * 60.0, 1),
            "is_viable": abo_ok and overall >= 35.0,
        })

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    top = scored[: max(1, payload.top_n)]

    # Grover's algorithm complexity metadata — used to pace the frontend animation
    grover_iterations = max(1, round((math.pi / 4) * math.sqrt(max(1, n))))
    classical_ops = n

    return {
        "patient_name": payload.patient_name,
        "pool_size": n,
        "candidates_matching_organ": len(scored),
        "grover_iterations": grover_iterations,
        "classical_ops": classical_ops,
        "quantum_ops": round(math.sqrt(max(1, n))),
        "speedup_factor": round(classical_ops / max(1, math.sqrt(max(1, n))), 1),
        "results": top,
    }
