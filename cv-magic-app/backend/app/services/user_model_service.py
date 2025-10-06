"""
Service for persisting and retrieving per-user selected AI provider and model.
"""

import logging
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.models.user_preferences import UserModelPreference

logger = logging.getLogger(__name__)


class UserModelService:
    def get_user_model(self, db: Session, user_id: str) -> Optional[Tuple[str, str]]:
        pref = db.query(UserModelPreference).filter(UserModelPreference.user_id == user_id).first()
        if not pref:
            return None
        return pref.provider, pref.model

    def set_user_model(self, db: Session, user_id: str, provider: str, model: str) -> None:
        pref = db.query(UserModelPreference).filter(UserModelPreference.user_id == user_id).first()
        if pref:
            pref.provider = provider
            pref.model = model
        else:
            pref = UserModelPreference(user_id=user_id, provider=provider, model=model)
            db.add(pref)
        db.commit()


user_model_service = UserModelService()


