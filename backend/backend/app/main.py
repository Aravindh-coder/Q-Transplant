"""Q-Transplant FastAPI application entry point."""
from sqlalchemy import inspect, text
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app.routers import auth, donors, doctors, hospitals, patients, matching, organizer, devices, emergency, quantum_router, documents, donor_requests, notifications, users, hla, transplants
from app.routers import doctor_workflow, hospital_workflow
from app.services.security_headers import SecurityHeadersMiddleware

def ensure_schema():
 Base.metadata.create_all(bind=engine)
 additions={"donor_profiles":[("medical_information","TEXT"),("donation_status","VARCHAR(64) DEFAULT 'ACTIVE'")],"doctor_profiles":[("professional_information","TEXT"),("photo_document_id","VARCHAR(64)"),("certificate_document_id","VARCHAR(64)")],"hospital_profiles":[("location","TEXT"),("registration_number","VARCHAR(255)"),("authorized_contact","VARCHAR(255)")]}
 inspector=inspect(engine)
 with engine.begin() as conn:
  for table,cols in additions.items():
   existing={c["name"] for c in inspector.get_columns(table)}
   for name,typ in cols:
    if name not in existing: conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {typ}"))
ensure_schema()
app=FastAPI(title="Q-Transplant API",description="Organ-transplant coordination, matching and emergency network platform.",version="2.2.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.ALLOWED_ORIGINS,allow_credentials=True,allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],allow_headers=["Authorization","Content-Type"],max_age=600)
app.add_middleware(SecurityHeadersMiddleware)
for router in (auth.router,users.router,donors.router,doctors.router,hospitals.router,patients.router,matching.router,organizer.router,devices.router,emergency.router,quantum_router.router,documents.router,donor_requests.router,notifications.router,hla.router,transplants.router,doctor_workflow.router,hospital_workflow.router): app.include_router(router)
@app.get("/")
def root(): return {"service":"Q-Transplant API","status":"online","version":"2.2.0"}
@app.get("/health")
def health(): return {"status":"ok"}
