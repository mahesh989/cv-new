"""
User-specific data models for isolation
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class UserAPIKey(Base):
    """User-specific API keys for AI providers"""
    
    __tablename__ = "user_api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # openai, anthropic, etc.
    encrypted_key = Column(Text, nullable=False)  # Encrypted API key
    is_valid = Column(Boolean, default=True)
    last_validated = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserAPIKey(user_id={self.user_id}, provider='{self.provider}')>"


class UserSettings(Base):
    """User-specific settings and preferences"""
    
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    preferred_ai_model = Column(String(50), nullable=True)
    analysis_preferences = Column(Text, nullable=True)  # JSON string
    notification_settings = Column(Text, nullable=True)  # JSON string
    ui_preferences = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id})>"


class UserFileStorage(Base):
    """User-specific file storage tracking"""
    
    __tablename__ = "user_file_storage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    file_type = Column(String(50), nullable=False)  # cv, analysis, job, etc.
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<UserFileStorage(user_id={self.user_id}, file_type='{self.file_type}')>"


class UserActivityLog(Base):
    """User activity logging for audit and analytics"""
    
    __tablename__ = "user_activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False)  # login, upload, analysis, etc.
    activity_data = Column(Text, nullable=True)  # JSON string with activity details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<UserActivityLog(user_id={self.user_id}, activity='{self.activity_type}')>"
