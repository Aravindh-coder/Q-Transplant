"""Q-Transplant FastAPI application entry point."""
from sqlalchemy import inspect, text
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import auth, donors, doctors, hospitals, patients, matching, organizer, devices, emergency, quantum_router, documents, donor_requests, notifications


def ensure_schema():
    """Create new tables and add donor columns for installations created by older versions."""
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    columns = {c["name"] for c in inspector.get_columns("donor_profiles")}
    with engine.begin() as conn:
        if "medical_information" not in columns:
            conn.execute(text("ALTER TABLE donor_profiles ADD COLUMN medical_information TEXT"))
        if "donation_status" not in columns:
            conn.execute(text("ALTER TABLE donor_profiles ADD COLUMN donation_status VARCHAR(64) DEFAULT 'ACTIVE'"))


ensure_schema()
app = FastAPI(
    title="Q-Transplant API",
    description="Organ-transplant coordination, matching and emergency network platform.",
    version="1.2.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
for router in (
    auth.router, donors.router, doctors.router, hospitals.router, patients.router,
    matching.router, organizer.router, devices.router, emergency.router,
    quantum_router.router, documents.router, donor_requests.router, notifications.router,
):
    app.include_router(router)


@app.get("/")
def root():
    return {"service": "Q-Transplant API", "status": "online"}


@app.get("/health")
def health():
    return {"status": "ok"}
