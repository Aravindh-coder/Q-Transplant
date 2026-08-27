"""
Q-Transplant — Backend Entry Point

Run locally:
    uvicorn app.main:app --reload --port 8000

First run creates all tables (SQLite by default — see app/config.py to
point DATABASE_URL at Postgres for production).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import auth, donors, doctors, hospitals, patients, matching, organizer, devices, emergency, quantum_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Q-Transplant API",
    description="Organ-transplant coordination, matching, and emergency network platform.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(donors.router)
app.include_router(doctors.router)
app.include_router(hospitals.router)
app.include_router(patients.router)
app.include_router(matching.router)
app.include_router(organizer.router)
app.include_router(devices.router)
app.include_router(emergency.router)
app.include_router(quantum_router.router)


@app.get("/")
def root():
    return {"service": "Q-Transplant API", "status": "online"}


@app.get("/health")
def health():
    return {"status": "ok"}
