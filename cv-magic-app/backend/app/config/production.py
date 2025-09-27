"""
Production configuration settings
"""
import os
from typing import List, Optional
from pydantic import BaseSettings, validator


class ProductionSettings(BaseSettings):
    """Production environment settings"""
    
    # Application Settings
    APP_NAME: str = "CV Management API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Database Configuration
    DATABASE_URL: str
    DATABASE_HOST: str
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    # Security Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60  # 1 hour for production
    JWT_REFRESH_EXPIRATION_DAYS: int = 7
    
    # Email Configuration
    SMTP_SERVER: str
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str
    FROM_NAME: str = "CV App"
    FRONTEND_URL: str
    
    # Redis Configuration (for caching and rate limiting)
    REDIS_URL: str
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = []
    
    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_STORAGE: str = "redis"  # redis or memory
    RATE_LIMIT_DEFAULT: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    LOG_FILE: Optional[str] = None
    LOG_ROTATION: str = "daily"
    LOG_RETENTION: int = 30  # days
    
    # Monitoring Configuration
    MONITORING_ENABLED: bool = True
    METRICS_ENABLED: bool = True
    HEALTH_CHECK_ENABLED: bool = True
    
    # Performance Configuration
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB
    REQUEST_TIMEOUT: int = 30  # seconds
    KEEP_ALIVE_TIMEOUT: int = 5  # seconds
    
    # Security Configuration
    SECURITY_HEADERS_ENABLED: bool = True
    CORS_ENABLED: bool = True
    RATE_LIMITING_ENABLED: bool = True
    AUDIT_LOGGING_ENABLED: bool = True
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "doc", "docx", "txt"]
    UPLOAD_DIRECTORY: str = "/app/uploads"
    
    # Cache Configuration
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # 1 hour
    CACHE_MAX_SIZE: int = 1000
    
    # Session Configuration
    SESSION_TIMEOUT: int = 8 * 60 * 60  # 8 hours
    MAX_SESSIONS_PER_USER: int = 5
    SESSION_CLEANUP_INTERVAL: int = 3600  # 1 hour
    
    # Admin Configuration
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    ADMIN_NOTIFICATIONS: bool = True
    
    # Backup Configuration
    BACKUP_ENABLED: bool = True
    BACKUP_SCHEDULE: str = "0 2 * * *"  # Daily at 2 AM
    BACKUP_RETENTION: int = 30  # days
    BACKUP_STORAGE: str = "local"  # local, s3, gcs
    
    # Alert Configuration
    ALERT_EMAIL: Optional[str] = None
    ALERT_WEBHOOK: Optional[str] = None
    ALERT_THRESHOLDS: dict = {
        "error_rate": 0.05,  # 5%
        "response_time": 2.0,  # 2 seconds
        "memory_usage": 0.8,  # 80%
        "disk_usage": 0.9  # 90%
    }
    
    @validator('ALLOWED_ORIGINS', pre=True)
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('ALLOWED_FILE_TYPES', pre=True)
    def parse_file_types(cls, v):
        if isinstance(v, str):
            return [ft.strip() for ft in v.split(',')]
        return v
    
    class Config:
        env_file = ".env.production"
        case_sensitive = True


# Create production settings instance
production_settings = ProductionSettings()
