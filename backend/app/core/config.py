from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Q-Transplant Enterprise Platform"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"

    # Environment & Database
    ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./qtransplant.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security: never commit real secrets. Production must provide JWT_SECRET.
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 120

    # Email / SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_TLS: bool = True
    ORGANIZER_EMAIL: str = ""

    # CORS: comma-separated URLs in the environment.
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
