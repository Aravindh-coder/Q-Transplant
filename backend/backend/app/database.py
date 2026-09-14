import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings, DEFAULT_DB_PATH

logger = logging.getLogger("qtransplant.database")

def create_app_engine(url: str):
    connect_args = {"check_same_thread": False, "timeout": 30} if "sqlite" in url else {}
    return create_engine(url, connect_args=connect_args, pool_pre_ping=True)

db_url = settings.DATABASE_URL
engine = create_app_engine(db_url)

# Fallback to SQLite if PostgreSQL host is dead/unreachable
if "sqlite" not in db_url:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        logger.info("Configured PostgreSQL DATABASE_URL is unreachable. Defaulting to local SQLite database.")
        db_url = f"sqlite:///{DEFAULT_DB_PATH}"
        engine = create_app_engine(db_url)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
