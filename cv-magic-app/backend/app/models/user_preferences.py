"""
User preferences models (per-user AI model selection)
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class UserModelPreference(Base):
    __tablename__ = "user_model_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_model_preference_user"),
    )

    def __repr__(self):
        return f"<UserModelPreference(user_id={self.user_id}, provider='{self.provider}', model='{self.model}')>"


