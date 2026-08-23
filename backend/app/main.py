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
