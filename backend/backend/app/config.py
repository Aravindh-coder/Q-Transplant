"""Q-Transplant configuration. Secrets are environment-only."""
import os
from dotenv import load_dotenv
load_dotenv()
BASE_DIR=os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..",".."))
DEFAULT_DB_PATH=os.path.join(BASE_DIR,"qtransplant.db")

def _normalize_db_url(url:str)->str:
    # Aiven/Heroku-style URLs use the legacy "postgres://" scheme, which
    # modern SQLAlchemy refuses to parse — rewrite it to "postgresql://".
    if url.startswith("postgres://"):
        url="postgresql://"+url[len("postgres://"):]
    # Aiven requires SSL; add it if the caller didn't already specify a mode.
    if url.startswith("postgresql://") and "sslmode" not in url:
        url += ("&" if "?" in url else "?") + "sslmode=require"
    return url

class Settings:
    DATABASE_URL=_normalize_db_url(os.environ.get("DATABASE_URL",f"sqlite:///{DEFAULT_DB_PATH}"))
    JWT_SECRET=os.environ.get("JWT_SECRET","")
    JWT_ALGO="HS256"
    ACCESS_TOKEN_MINUTES=int(os.environ.get("ACCESS_TOKEN_MINUTES",720))
    OTP_EXPIRY_MINUTES=int(os.environ.get("OTP_EXPIRY_MINUTES",10))
    ORGANIZER_EMAIL=os.environ.get("ORGANIZER_EMAIL","")
    ORGANIZER_APP_PASSWORD=os.environ.get("ORGANIZER_APP_PASSWORD","")
    # Distinct from the two vars above, which are the Gmail sender account
    # used to deliver system emails — NOT a platform login. These, if set,
    # are used once at startup to create the first organizer login if one
    # doesn't already exist (registration deliberately blocks self-signup
    # for the organizer role, so without this there is no way to ever get
    # an organizer account into a fresh production database).
    ORGANIZER_BOOTSTRAP_EMAIL=os.environ.get("ORGANIZER_BOOTSTRAP_EMAIL","")
    ORGANIZER_BOOTSTRAP_PASSWORD=os.environ.get("ORGANIZER_BOOTSTRAP_PASSWORD","")
    # Optional. Enables AI-assisted (never authoritative) comparison of a
    # doctor's live selfie against their license/certificate photo during
    # onboarding. Without it, uploads still work — the organizer just sees
    # "not_run" and reviews the two images manually.
    ANTHROPIC_API_KEY=os.environ.get("ANTHROPIC_API_KEY","")
    ALLOWED_ORIGINS=os.environ.get("ALLOWED_ORIGINS","http://localhost:5173").split(",")
    LOGIN_RATE_LIMIT=int(os.environ.get("LOGIN_RATE_LIMIT",10))
    OTP_RATE_LIMIT=int(os.environ.get("OTP_RATE_LIMIT",5))
    RATE_LIMIT_WINDOW_MINUTES=int(os.environ.get("RATE_LIMIT_WINDOW_MINUTES",15))
    MIN_PASSWORD_LENGTH=int(os.environ.get("MIN_PASSWORD_LENGTH",8))
settings=Settings()
if not settings.JWT_SECRET:
    raise RuntimeError("JWT_SECRET must be configured in the environment.")
if settings.DATABASE_URL.startswith("sqlite") and os.environ.get("RENDER"):
    # On Render, sqlite means DATABASE_URL wasn't actually set — data won't
    # persist across deploys/restarts. Fail loudly instead of silently.
    raise RuntimeError("DATABASE_URL is not set — refusing to fall back to sqlite in production (Render).")
