import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Q-Transplant Enterprise Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Database
    ENV: str = os.getenv("ENV", "development")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite:///./qtransplant.db"
    )
    
    # JWT Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-transplant-key-change-in-production-32-bytes-min!")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours for dev convenience
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 120
    
    # Email / SMTP Settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.example.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "notifications@qtransplant.org")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "secret")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "notifications@qtransplant.org")
    SMTP_TLS: bool = True
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
