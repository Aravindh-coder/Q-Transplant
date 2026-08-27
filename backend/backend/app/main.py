"""Q-Transplant FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app.routers import auth, donors, doctors, hospitals, patients, matching, organizer, devices, emergency, quantum_router, documents

Base.metadata.create_all(bind=engine)
app=FastAPI(title="Q-Transplant API",description="Organ-transplant coordination, matching and emergency network platform.",version="1.1.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.ALLOWED_ORIGINS,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
for router in (auth.router,donors.router,doctors.router,hospitals.router,patients.router,matching.router,organizer.router,devices.router,emergency.router,quantum_router.router,documents.router):
    app.include_router(router)
@app.get("/")
def root(): return {"service":"Q-Transplant API","status":"online"}
@app.get("/health")
def health(): return {"status":"ok"}
