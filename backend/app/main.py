from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from sqlalchemy import text

from backend.app.core.config import settings
from backend.app.core.database import engine, Base, SessionLocal
from backend.app.core.security import get_password_hash
from backend.app.core.middleware import RequestLoggingMiddleware
from backend.app.core.logging import logger
from backend.app.models.domain import User, UserRole, Hospital, Doctor, Donor, Patient, Organ, Match, GPSLocation, ICUOccupancy, BloodInventory
from backend.app.routers import auth, users, organs, matches, telemetry, notifications, audit, hospitals, reports, ws, emergency, gis, coordinator, donor_search
from backend.app.routers import ai as ai_router

Base.metadata.create_all(bind=engine)

# Migration safety check for SQLite columns
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE doctors ADD COLUMN avatar_url VARCHAR(255);"))
        conn.commit()
    except Exception:
        pass
    try:
        conn.execute(text("ALTER TABLE doctors ADD COLUMN certificate_url VARCHAR(255);"))
        conn.commit()
    except Exception:
        pass
    try:
        conn.execute(text("ALTER TABLE matches ADD COLUMN match_rationale TEXT;"))
        conn.commit()
    except Exception:
        pass
    try:
        conn.execute(text("ALTER TABLE donors ADD COLUMN qr_code_token VARCHAR(100);"))
        conn.commit()
    except Exception:
        pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Uploads Folder
uploads_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
if not os.path.exists(uploads_path):
    os.makedirs(uploads_path, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(organs.router, prefix=settings.API_V1_STR)
app.include_router(matches.router, prefix=settings.API_V1_STR)
app.include_router(telemetry.router, prefix=settings.API_V1_STR)
app.include_router(hospitals.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(notifications.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(ws.router, prefix=settings.API_V1_STR)
app.include_router(emergency.router, prefix=settings.API_V1_STR)
app.include_router(ai_router.router, prefix=settings.API_V1_STR)
app.include_router(gis.router, prefix=settings.API_V1_STR)
app.include_router(coordinator.router, prefix=settings.API_V1_STR)
app.include_router(donor_search.router, prefix=settings.API_V1_STR)


EXTRA_HOSPITALS = [
    {"name": "Fortis Healthcare, Bengaluru", "email": "fortis@qtransplant.org", "city": "Bengaluru", "state": "Karnataka",
     "address": "Bannerghatta Rd, Richmond Town, 560025", "lat": 12.8924, "lng": 77.5975, "phone": "080-6621-4444",
     "license": "LIC-KA-2026-9042", "beds": 18, "occupied": 10, "vents": 5},
    {"name": "Manipal Hospital", "email": "manipal@qtransplant.org", "city": "Bengaluru", "state": "Karnataka",
     "address": "Old Airport Rd, HAL, 560017", "lat": 12.9581, "lng": 77.6482, "phone": "080-2502-4444",
     "license": "LIC-KA-2026-9043", "beds": 22, "occupied": 15, "vents": 7},
    {"name": "Narayana Health City", "email": "narayana@qtransplant.org", "city": "Bengaluru", "state": "Karnataka",
     "address": "Bommasandra, Hosur Rd, 560099", "lat": 12.8103, "lng": 77.6920, "phone": "080-7122-2222",
     "license": "LIC-KA-2026-9044", "beds": 25, "occupied": 12, "vents": 8},
    {"name": "AIIMS Delhi", "email": "aiims-delhi@qtransplant.org", "city": "Delhi", "state": "Delhi",
     "address": "Ansari Nagar, New Delhi, 110029", "lat": 28.5672, "lng": 77.2100, "phone": "011-2658-8500",
     "license": "LIC-DL-2026-9045", "beds": 30, "occupied": 20, "vents": 10},
    {"name": "CMC Vellore", "email": "cmc-vellore@qtransplant.org", "city": "Vellore", "state": "Tamil Nadu",
     "address": "Ida Scudder Rd, Vellore, 632004", "lat": 12.9260, "lng": 79.1350, "phone": "0416-228-1000",
     "license": "LIC-TN-2026-9046", "beds": 20, "occupied": 9, "vents": 6},
    {"name": "Apollo Hospitals, Chennai", "email": "apollo-chennai@qtransplant.org", "city": "Chennai", "state": "Tamil Nadu",
     "address": "Greams Rd, Thousand Lights, 600006", "lat": 13.0604, "lng": 80.2496, "phone": "044-2829-3333",
     "license": "LIC-TN-2026-9047", "beds": 24, "occupied": 16, "vents": 9},
    {"name": "Max Super Speciality Hospital", "email": "max-delhi@qtransplant.org", "city": "Delhi", "state": "Delhi",
     "address": "Press Enclave Rd, Saket, 110017", "lat": 28.5286, "lng": 77.2124, "phone": "011-2651-5050",
     "license": "LIC-DL-2026-9048", "beds": 16, "occupied": 11, "vents": 4},
]


def seed_additional_hospitals():
    """Ensures the wider hospital network (beyond the single default Apollo
    Bengaluru record) exists in the DB — runs every startup and only inserts
    hospitals that aren't already present by name, so it's safe on an
    existing/live database and never duplicates rows."""
    db = SessionLocal()
    try:
        for h in EXTRA_HOSPITALS:
            existing = db.query(Hospital).filter(Hospital.name == h["name"]).first()
            if existing:
                continue

            hosp_user = db.query(User).filter(User.email == h["email"]).first()
            if not hosp_user:
                hosp_user = User(
                    email=h["email"],
                    password_hash=get_password_hash("HospitalPass123!"),
                    full_name=h["name"],
                    role=UserRole.HOSPITAL.value,
                    phone=h["phone"],
                    is_active=True,
                    is_approved=True
                )
                db.add(hosp_user)
                db.commit()
                db.refresh(hosp_user)

            hosp_profile = Hospital(
                user_id=hosp_user.id,
                name=h["name"],
                license_number=h["license"],
                city=h["city"],
                state=h["state"],
                address=h["address"],
                lat=h["lat"],
                lng=h["lng"],
                contact_phone=h["phone"]
            )
            db.add(hosp_profile)
            db.commit()
            db.refresh(hosp_profile)

            db.add(ICUOccupancy(
                hospital_id=hosp_profile.id,
                total_beds=h["beds"],
                occupied_beds=h["occupied"],
                ventilators_available=h["vents"]
            ))
            for bt in ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]:
                db.add(BloodInventory(hospital_id=hosp_profile.id, blood_type=bt, units_available=8))
            db.commit()
            logger.info(f"Seeded additional hospital: {h['name']}")
    except Exception as e:
        logger.error(f"Error seeding additional hospitals: {e}")
        db.rollback()
    finally:
        db.close()


@app.on_event("startup")
def seed_initial_data():
    """Seeds initial administrative organizer and sample operational data if missing."""
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "aravindhjoshua10@gmail.com").first()
        if not admin:
            logger.info("Seeding default Administrator (Organizer)...")
            admin = User(
                email="aravindhjoshua10@gmail.com",
                password_hash=get_password_hash("AdminPass123!"),
                full_name="Aravindh Joshua (Organizer Admin)",
                role=UserRole.ORGANIZER.value,
                phone="080-9999-0000",
                is_active=True,
                is_approved=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

            hosp_user = User(
                email="apollo@qtransplant.org",
                password_hash=get_password_hash("HospitalPass123!"),
                full_name="Apollo Specialty Hospital",
                role=UserRole.HOSPITAL.value,
                phone="080-4444-1111",
                is_active=True,
                is_approved=True
            )
            db.add(hosp_user)
            db.commit()
            db.refresh(hosp_user)

            hosp_profile = Hospital(
                user_id=hosp_user.id,
                name="Apollo Specialty Hospital",
                license_number="LIC-KA-2026-9041",
                city="Bengaluru",
                state="Karnataka",
                address="Bannerghatta Road, 560076",
                lat=12.8945,
                lng=77.5989,
                contact_phone="080-4444-1111"
            )
            db.add(hosp_profile)
            db.commit()
            db.refresh(hosp_profile)

            # Seed ICU & Blood Inventory
            icu = ICUOccupancy(
                hospital_id=hosp_profile.id,
                total_beds=20,
                occupied_beds=14,
                ventilators_available=6
            )
            db.add(icu)

            doc_user = User(
                email="doctor@qtransplant.org",
                password_hash=get_password_hash("DoctorPass123!"),
                full_name="Dr. Rajesh Kumar",
                role=UserRole.DOCTOR.value,
                phone="080-4444-2222",
                is_active=True,
                is_approved=True
            )
            db.add(doc_user)
            db.commit()
            db.refresh(doc_user)

            doc_profile = Doctor(
                user_id=doc_user.id,
                hospital_id=hosp_profile.id,
                medical_license="MED-CARD-2024-88",
                specialization="Cardiothoracic Surgery",
                department="Organ Transplantation Unit",
                phone="080-4444-2222"
            )
            db.add(doc_profile)

            donor_user = User(
                email="donor@qtransplant.org",
                password_hash=get_password_hash("DonorPass123!"),
                full_name="David Miller",
                role=UserRole.DONOR.value,
                phone="080-7777-3333",
                is_active=True,
                is_approved=True
            )
            db.add(donor_user)
            db.commit()
            db.refresh(donor_user)

            donor_profile = Donor(
                user_id=donor_user.id,
                doctor_id=doc_profile.id,
                blood_type="O+",
                hla_type="A2,B7,DR4",
                age=32,
                gender="Male",
                status="verified",
                qr_code_token="QR-DONOR-O-PLUS-001"
            )
            db.add(donor_profile)
            db.commit()

            organ = Organ(
                donor_id=donor_profile.id,
                organ_type="Heart",
                blood_type="O+",
                hla_type="A2,B7,DR4",
                max_ischemia_hours=4.0,
                cold_box_id="BOX-ESP32-001",
                status="available"
            )
            db.add(organ)

            patient_user = User(
                email="patient@qtransplant.org",
                password_hash=get_password_hash("PatientPass123!"),
                full_name="Sarah Jenkins",
                role=UserRole.PATIENT.value,
                phone="080-8888-4444",
                is_active=True,
                is_approved=True
            )
            db.add(patient_user)
            db.commit()
            db.refresh(patient_user)

            patient_profile = Patient(
                user_id=patient_user.id,
                hospital_id=hosp_profile.id,
                doctor_id=doc_profile.id,
                blood_type="O+",
                hla_type="A2,B7,DR4",
                target_organ="Heart",
                urgency_score=9,
                status="waiting_list"
            )
            db.add(patient_profile)

            telemetry = GPSLocation(
                cold_box_id="BOX-ESP32-001",
                lat=12.9716,
                lng=77.5946,
                temp_celsius=4.2,
                humidity_percent=84.5,
                battery_level=96.0
            )
            db.add(telemetry)

            db.commit()
            logger.info("Database successfully seeded with default operational data!")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

    seed_additional_hospitals()


@app.get("/health", tags=["System Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "connected"
    }


@app.get("/", tags=["System Information"])
def root():
    return {
        "title": settings.PROJECT_NAME,
        "docs": f"{settings.API_V1_STR}/docs",
        "health": "/health"
    }
