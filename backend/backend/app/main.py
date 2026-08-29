"""Q-Transplant FastAPI application entry point."""
import logging
import os
from sqlalchemy import inspect, text
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings, BASE_DIR
from app.database import Base, engine
from app.routers import auth, donors, doctors, hospitals, patients, matching, organizer, devices, emergency, quantum_router, documents, donor_requests, notifications, users, hla, transplants
from app.routers import doctor_workflow, hospital_workflow
from app.services.security_headers import SecurityHeadersMiddleware
from app.services.observability import configure_logging, safe_event

configure_logging()
logger=logging.getLogger("qtransplant.startup")
PUBLIC_DIR=os.path.join(BASE_DIR,"public")

def ensure_schema():
 Base.metadata.create_all(bind=engine)
 additions={"donor_profiles":[("medical_information","TEXT"),("donation_status","VARCHAR(64) DEFAULT 'ACTIVE'")],"doctor_profiles":[("professional_information","TEXT"),("photo_document_id","VARCHAR(64)"),("certificate_document_id","VARCHAR(64)"),("identity_check_result","TEXT"),("identity_check_confidence","VARCHAR(32)")],"hospital_profiles":[("location","TEXT"),("registration_number","VARCHAR(255)"),("authorized_contact","VARCHAR(255)")]}
 inspector=inspect(engine)
 with engine.begin() as conn:
  for table,cols in additions.items():
   existing={c["name"] for c in inspector.get_columns(table)}
   for name,typ in cols:
    if name not in existing: conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {typ}"))
def ensure_organizer_bootstrap():
    from app.models import User
    from app.security import hash_password
    from app.database import SessionLocal
    if not (settings.ORGANIZER_BOOTSTRAP_EMAIL and settings.ORGANIZER_BOOTSTRAP_PASSWORD):
        return
    db=SessionLocal()
    try:
        if db.query(User).filter(User.role=="organizer").first():
            return  # an organizer already exists — never overwrite silently
        db.add(User(email=settings.ORGANIZER_BOOTSTRAP_EMAIL,hashed_password=hash_password(settings.ORGANIZER_BOOTSTRAP_PASSWORD),role="organizer",full_name="Organizer",status="active",email_verified=True))
        db.commit()
        logger.info("Bootstrapped the first organizer account from ORGANIZER_BOOTSTRAP_EMAIL.")
    finally:
        db.close()
try:
    ensure_schema()
except Exception:
    # A transient DB hiccup (cold Aiven connection, brief network blip) at
    # import time used to take the whole process down before it could even
    # bind to a port. Log it loudly and let the app boot; DB-dependent
    # routes will surface their own errors instead of the service never
    # coming up at all.
    logger.exception("ensure_schema() failed at startup — app is booting anyway; DB-dependent routes may fail until this is resolved.")
try:
    ensure_organizer_bootstrap()
except Exception:
    logger.exception("ensure_organizer_bootstrap() failed at startup.")
app=FastAPI(title="Q-Transplant API",description="Organ-transplant coordination, matching and emergency network platform.",version="2.2.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.ALLOWED_ORIGINS,allow_credentials=True,allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],allow_headers=["Authorization","Content-Type"],max_age=600)
app.add_middleware(SecurityHeadersMiddleware)

_STATUS_CODES={400:"BAD_REQUEST",401:"UNAUTHORIZED",403:"FORBIDDEN",404:"NOT_FOUND",405:"METHOD_NOT_ALLOWED",409:"CONFLICT",413:"PAYLOAD_TOO_LARGE",422:"VALIDATION_ERROR",429:"RATE_LIMITED"}

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as StarletteHTTPException, RequestValidationError

@app.exception_handler(StarletteHTTPException)
async def _http_exception_handler(request:Request,exc:StarletteHTTPException):
    code=_STATUS_CODES.get(exc.status_code,f"HTTP_{exc.status_code}")
    return JSONResponse(status_code=exc.status_code,content={"success":False,"error":{"code":code,"message":exc.detail}},headers=getattr(exc,"headers",None))

@app.exception_handler(RequestValidationError)
async def _validation_exception_handler(request:Request,exc:RequestValidationError):
    # Pydantic's default 422 body is a list of field errors -- flatten to
    # one readable message while keeping the same structured shape as
    # every other error response.
    first=exc.errors()[0] if exc.errors() else {}
    field=".".join(str(p) for p in first.get("loc",[]) if p not in ("body","query","path"))
    message=(f"{field}: {first.get('msg','Invalid request')}" if field else first.get("msg","Invalid request"))
    return JSONResponse(status_code=422,content={"success":False,"error":{"code":"VALIDATION_ERROR","message":message}})

@app.exception_handler(Exception)
async def _unhandled_exception_handler(request:Request,exc:Exception):
    logger.exception("Unhandled exception on %s %s",request.method,request.url.path)
    return JSONResponse(status_code=500,content={"success":False,"error":{"code":"INTERNAL_ERROR","message":"Something went wrong on our end. Please try again."}})

for router in (auth.router,users.router,donors.router,doctors.router,hospitals.router,patients.router,matching.router,organizer.router,devices.router,emergency.router,quantum_router.router,documents.router,donor_requests.router,notifications.router,hla.router,transplants.router,doctor_workflow.router,hospital_workflow.router): app.include_router(router)
@app.get("/api")
def api_status(): return {"service":"Q-Transplant API","status":"online","version":"2.2.0"}
@app.get("/health")
def health():
    try:
        with engine.connect() as conn: conn.execute(text("SELECT 1"))
        return {"status":"ok","database":"connected"}
    except Exception as e:
        return {"status":"ok","database":"unreachable","detail":str(e)}
# Mounted last so it never shadows the API routes above — this serves
# public/index.html at "/", and public/app.html, public/donor.html, and
# static assets by filename. Same-origin means the frontend's fetch calls
# to /api/... need no CORS handling at all.
if os.path.isdir(PUBLIC_DIR):
    app.mount("/",StaticFiles(directory=PUBLIC_DIR,html=True),name="frontend")
else:
    logger.warning("public/ directory not found at %s — frontend will not be served.",PUBLIC_DIR)
