import logging
"""
Authentication dependencies for FastAPI.

Token verification order:
1. Try Firebase ID token verification (primary — used by the Flutter app).
2. Fall back to legacy JWT verification (backwards-compat during transition).

This means both Firebase-authenticated users and existing JWT sessions work
simultaneously without a hard cut-over.
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.models.auth import UserData

logger = logging.getLogger(__name__)

# Security scheme — extracts the Bearer token from Authorization header
security = HTTPBearer()


# ── Firebase token path ────────────────────────────────────────────────────────

def _get_or_create_firebase_user(decoded: dict, db: Session) -> UserData:
    """
    Given a verified Firebase token payload, return (and lazily create) the
    matching database user record.
    """
    from app.models.user import User
    from app.utils.user_path_utils import ensure_user_directories

    uid: str = decoded["uid"]
    email: str = decoded.get("email", "")
    display_name: str = decoded.get("name", "") or email.split("@")[0]

    # Look up by firebase_uid first, then fall back to email
    user = db.query(User).filter(User.firebase_uid == uid).first()
    if user is None and email:
        user = db.query(User).filter(User.email == email).first()

    if user is None:
        # First sign-in — auto-provision the user record
        base_username = email.split("@")[0] if email else uid[:20]
        username = base_username
        counter = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1

        user = User(
            username=username,
            email=email,
            full_name=display_name,
            firebase_uid=uid,
            is_active=True,
            is_verified=decoded.get("email_verified", False),
            created_at=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Auto-provisioned Firebase user: {email} (uid={uid})")

    elif user.firebase_uid is None:
        # Legacy account — link to Firebase UID now
        user.firebase_uid = uid
        db.commit()
        logger.info(f"Linked Firebase UID to existing account: {email}")

    # Ensure user directories always exist
    try:
        ensure_user_directories(user.email)
    except Exception as e:
        logger.warning(f"Could not ensure directories for {email}: {e}")

    return UserData(
        id=user.id,
        email=user.email,
        name=user.full_name or display_name,
        created_at=user.created_at or datetime.now(timezone.utc),
        is_active=user.is_active,
    )


def _verify_firebase(token: str, db: Session) -> Optional[UserData]:
    """Return UserData if *token* is a valid Firebase ID token, else None."""
    try:
        from app.core.firebase_admin_sdk import verify_firebase_token
        decoded = verify_firebase_token(token)
        if decoded is None:
            return None
        return _get_or_create_firebase_user(decoded, db)
    except Exception as e:
        logger.debug(f"Firebase verification failed: {e}")
        return None


# ── Legacy JWT path ────────────────────────────────────────────────────────────

def _verify_legacy_jwt(token: str) -> Optional[UserData]:
    """Return UserData if *token* is a valid legacy JWT, else None."""
    try:
        from app.core.auth import verify_token
        token_data = verify_token(token)
        return UserData(
            id=token_data.user_id,
            email=token_data.email,
            name=token_data.email.split("@")[0] if token_data.email else "user",
            created_at=datetime.now(timezone.utc),
            is_active=True,
        )
    except Exception:
        return None


# ── Public dependency ──────────────────────────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(__import__("app.database", fromlist=["get_database"]).get_database),
) -> UserData:
    """
    FastAPI dependency — returns the authenticated user.

    Tries Firebase ID token first, then falls back to legacy JWT.
    Raises HTTP 401 if neither succeeds.
    """
    from app.config import settings

    token = credentials.credentials
    token_preview = token[:20] + "..." if len(token) > 20 else token
    logger.debug(f"Auth attempt with token: {token_preview}")

    # 1. Firebase
    user = _verify_firebase(token, db)
    if user:
        logger.debug(f"✅ Firebase auth OK: {user.email}")
        return user

    # 2. Legacy JWT
    user = _verify_legacy_jwt(token)
    if user:
        logger.debug(f"✅ Legacy JWT auth OK: {user.email}")
        return user

    # 3. Fail
    logger.debug("❌ Auth failed — token invalid for both Firebase and JWT")
    detail = (
        "Token expired — please log in again"
        if settings.DEVELOPMENT_MODE
        else "Invalid authentication token"
    )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(__import__("app.database", fromlist=["get_database"]).get_database),
) -> Optional[UserData]:
    """
    Like get_current_user but returns None instead of raising 401.
    Useful for endpoints that work both authenticated and anonymous.
    """
    if credentials is None:
        return None
    token = credentials.credentials
    user = _verify_firebase(token, db)
    if user:
        return user
    return _verify_legacy_jwt(token)
