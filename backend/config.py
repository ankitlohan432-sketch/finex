"""
FINEX Production Configuration
Optimized for high traffic, security, and scalability
"""

import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Production Configuration"""
    
    # Application
    APP_NAME: str = "FINEX"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    WORKER_CLASS: str = "uvicorn.workers.UvicornWorker"
    
    # Database
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/finex_db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    JWT_REFRESH_EXPIRATION_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://finex.app",
        "https://www.finex.app"
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = "noreply@finex.app"
    
    # Cache
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 300
    CACHE_MAX_SIZE: int = 1000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/finex.log"
    
    # Performance
    MAX_CONCURRENT_REQUESTS: int = 1000
    REQUEST_TIMEOUT_SECONDS: int = 30
    UPLOAD_MAX_SIZE_MB: int = 100
    
    # Stock API
    STOCK_API_KEY: str = os.getenv("STOCK_API_KEY", "")
    STOCK_API_TIMEOUT: int = 10
    STOCK_PRICE_CACHE_MINUTES: int = 5
    
    # Fraud Detection
    FRAUD_DETECTION_ENABLED: bool = True
    FRAUD_THRESHOLD_SCORE: float = 0.7
    MAX_FAILED_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    
    # WebSocket
    WEBSOCKET_ENABLED: bool = True
    WEBSOCKET_MAX_CONNECTIONS: int = 1000
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    
    # Admin
    ADMIN_EMAIL: str = "admin@finex.app"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Export settings
settings = get_settings()
