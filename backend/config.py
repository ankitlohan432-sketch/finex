import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FINEX"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # SQLite fallback so app starts even without a DB env var
    DATABASE_URL: str = "sqlite:///./finex.db"

    SECRET_KEY: str = "finex-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    JWT_REFRESH_EXPIRATION_DAYS: int = 7

    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@finex.app"

    STOCK_API_KEY: str = ""
    STOCK_API_URL: str = "https://api.twelvedata.com"

    ADMIN_EMAIL: str = "ankitlohan432@gmail.com"
    ADMIN_USERNAME: str = "rohan"
    ADMIN_PASSWORD: str = "finex_admin_secret_2024"

    SENDGRID_API_KEY: str = ""

    FRAUD_DETECTION_ENABLED: bool = True
    FRAUD_THRESHOLD_SCORE: float = 0.7
    MAX_FAILED_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

