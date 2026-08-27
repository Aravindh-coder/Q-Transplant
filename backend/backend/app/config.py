"""Q-Transplant configuration. Secrets are environment-only."""
import os
from dotenv import load_dotenv
load_dotenv()
BASE_DIR=os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..",".."))
DEFAULT_DB_PATH=os.path.join(BASE_DIR,"qtransplant.db")
class Settings:
    DATABASE_URL=os.environ.get("DATABASE_URL",f"sqlite:///{DEFAULT_DB_PATH}")
    JWT_SECRET=os.environ.get("JWT_SECRET","")
    JWT_ALGO="HS256"
    ACCESS_TOKEN_MINUTES=int(os.environ.get("ACCESS_TOKEN_MINUTES",720))
    OTP_EXPIRY_MINUTES=int(os.environ.get("OTP_EXPIRY_MINUTES",10))
    ORGANIZER_EMAIL=os.environ.get("ORGANIZER_EMAIL","")
    ORGANIZER_APP_PASSWORD=os.environ.get("ORGANIZER_APP_PASSWORD","")
    ALLOWED_ORIGINS=os.environ.get("ALLOWED_ORIGINS","http://localhost:5173").split(",")
    LOGIN_RATE_LIMIT=int(os.environ.get("LOGIN_RATE_LIMIT",10))
    OTP_RATE_LIMIT=int(os.environ.get("OTP_RATE_LIMIT",5))
    RATE_LIMIT_WINDOW_MINUTES=int(os.environ.get("RATE_LIMIT_WINDOW_MINUTES",15))
    MIN_PASSWORD_LENGTH=int(os.environ.get("MIN_PASSWORD_LENGTH",8))
settings=Settings()
if not settings.JWT_SECRET:
    raise RuntimeError("JWT_SECRET must be configured in the environment.")
