"""
Q-Transplant — Configuration
All secrets come from environment variables. Never hardcode credentials here.
Copy .env.example to .env and fill in real values before running.
"""
import os
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "qtransplant.db")

class Settings:
    # database
    DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

    # auth
    JWT_SECRET = os.environ.get("JWT_SECRET", "CHANGE_ME_IN_PRODUCTION")
    JWT_ALGO = "HS256"
    ACCESS_TOKEN_MINUTES = int(os.environ.get("ACCESS_TOKEN_MINUTES", 60 * 12))
    OTP_EXPIRY_MINUTES = int(os.environ.get("OTP_EXPIRY_MINUTES", 10))

    # organizer email (SMTP sender for all system emails, incl. OTP)
    ORGANIZER_EMAIL = os.environ.get("ORGANIZER_EMAIL", "aravindhjoshua10@gmail.com")
    ORGANIZER_APP_PASSWORD = os.environ.get("ORGANIZER_APP_PASSWORD", "")

    # cors
    ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

    # rate limiting (requests per window, per IP) — enforced in routers that touch auth
    LOGIN_RATE_LIMIT = int(os.environ.get("LOGIN_RATE_LIMIT", 10))
    OTP_RATE_LIMIT = int(os.environ.get("OTP_RATE_LIMIT", 5))
    RATE_LIMIT_WINDOW_MINUTES = int(os.environ.get("RATE_LIMIT_WINDOW_MINUTES", 15))


settings = Settings()
