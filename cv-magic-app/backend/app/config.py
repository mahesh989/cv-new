"""
Application configuration settings
"""
import os
import json
from typing import List

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application Settings
    APP_NAME: str = "CV Management API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:Nepalibabu989@myapp-database.cbo28oqgs6o8.ap-southeast-2.rds.amazonaws.com:5432/myappdb"
    DATABASE_HOST: str = "myapp-database.cbo28oqgs6o8.ap-southeast-2.rds.amazonaws.com"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "myappdb"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "password"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 480  # 8 hours for development
    JWT_REFRESH_EXPIRATION_DAYS: int = 7
    
    # Development Settings
    DEVELOPMENT_MODE: bool = True  # Enable development features
    BYPASS_AUTH: bool = False  # For testing without auth
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:3001",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8080",
        "http://localhost:53350",  # Flutter web ports
        "http://localhost:58155",  # Flutter web ports
        "http://127.0.0.1:53350",  # Flutter web ports
        "http://127.0.0.1:58155",  # Flutter web ports
        "*"  # Allow all origins for development
    ]
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    ALLOWED_HEADERS: List[str] = [
        "*",
        "accept",
        "accept-encoding",
        "authorization",
        "content-type",
        "dnt",
        "origin",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
        "access-control-allow-credentials",
        "access-control-allow-headers",
        "access-control-allow-methods",
        "access-control-allow-origin"
    ]
    
    # File Upload Settings
    UPLOAD_DIR: str = "user/user_admin@admin.com/cv-analysis/uploads"  # Will be updated dynamically per user
    MAX_FILE_SIZE: int = 10485760  # 10MB in bytes
    MAX_FILES_PER_USER: int = 50
    
    # Rate Limiting
    RATE_LIMIT_AUTH: str = "5/minute"
    RATE_LIMIT_UPLOAD: str = "10/hour"
    RATE_LIMIT_GENERAL: str = "100/minute"
    
    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "your_email@gmail.com"
    SMTP_PASSWORD: str = "your_app_password"
    SMTP_USE_TLS: bool = True
    
    # AI/ML Services - API keys now handled dynamically via user configuration
    # OPENAI_API_KEY: str = ""        # Commented out - use dynamic API key management
    # ANTHROPIC_API_KEY: str = ""     # Commented out - use dynamic API key management  
    # CLAUDE_API_KEY: str = ""        # Commented out - use dynamic API key management
    # DEEPSEEK_API_KEY: str = ""      # Commented out - use dynamic API key management
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Handle JSON string parsing for lists
        if isinstance(self.ALLOWED_ORIGINS, str):
            try:
                self.ALLOWED_ORIGINS = json.loads(self.ALLOWED_ORIGINS)
            except json.JSONDecodeError:
                self.ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:3001"]
        
        if isinstance(self.ALLOWED_METHODS, str):
            try:
                self.ALLOWED_METHODS = json.loads(self.ALLOWED_METHODS)
            except json.JSONDecodeError:
                self.ALLOWED_METHODS = ["*"]
                
        if isinstance(self.ALLOWED_HEADERS, str):
            try:
                self.ALLOWED_HEADERS = json.loads(self.ALLOWED_HEADERS)
            except json.JSONDecodeError:
                self.ALLOWED_HEADERS = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


# Create global settings instance
settings = Settings()

# Override for development
if settings.DEVELOPMENT_MODE:
    settings.JWT_EXPIRATION_MINUTES = 480  # 8 hours for development
    print(f"🔧 Development mode: JWT expiration set to {settings.JWT_EXPIRATION_MINUTES} minutes")
