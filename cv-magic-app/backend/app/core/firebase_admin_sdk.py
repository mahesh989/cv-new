"""
Firebase Admin SDK initialisation and token verification.

Supports two initialisation modes (checked in order):
1. FIREBASE_SERVICE_ACCOUNT_JSON env var — JSON string of the service-account key.
2. FIREBASE_SERVICE_ACCOUNT_PATH env var — file path to the service-account JSON file.

To generate a service-account key:
  Firebase Console → Project Settings → Service Accounts → Generate new private key
  Download the JSON and set it as FIREBASE_SERVICE_ACCOUNT_JSON (or path).
"""
import json
import logging
import os
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

_firebase_initialized = False


def _initialize_firebase() -> bool:
    """Lazy-initialise the Firebase Admin SDK (idempotent)."""
    global _firebase_initialized
    if _firebase_initialized:
        return True

    try:
        import firebase_admin
        from firebase_admin import credentials

        if firebase_admin._DEFAULT_APP_NAME in firebase_admin._apps:
            _firebase_initialized = True
            return True

        # ── Option 1: JSON string from env ────────────────────────────────
        sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
        if sa_json:
            sa_dict = json.loads(sa_json)
            cred = credentials.Certificate(sa_dict)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialised from FIREBASE_SERVICE_ACCOUNT_JSON env var")
            _firebase_initialized = True
            return True

        # ── Option 2: File path from env ──────────────────────────────────
        sa_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH")
        if sa_path and os.path.exists(sa_path):
            cred = credentials.Certificate(sa_path)
            firebase_admin.initialize_app(cred)
            logger.info(f"Firebase Admin SDK initialised from file: {sa_path}")
            _firebase_initialized = True
            return True

        # ── Option 3: Default Application Credentials (GCP) ──────────────
        firebase_admin.initialize_app()
        logger.info("Firebase Admin SDK initialised with Application Default Credentials")
        _firebase_initialized = True
        return True

    except Exception as e:
        logger.error(f"Failed to initialise Firebase Admin SDK: {e}")
        return False


def verify_firebase_token(id_token: str) -> Optional[dict]:
    """
    Verify a Firebase ID token and return its decoded claims.

    Returns a dict with at minimum:
        uid       — Firebase UID (stable unique identifier)
        email     — user email
        name      — display name (may be absent for email/password users)
        picture   — avatar URL (may be absent)
        email_verified — bool

    Returns None if the token is invalid or Firebase is not configured.
    """
    if not _initialize_firebase():
        logger.warning("Firebase not configured — token verification skipped")
        return None

    try:
        from firebase_admin import auth
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        logger.warning(f"Firebase token verification failed: {e}")
        return None


def get_firebase_user(uid: str) -> Optional[dict]:
    """Fetch Firebase user record by UID (used for admin lookups)."""
    if not _initialize_firebase():
        return None
    try:
        from firebase_admin import auth
        user = auth.get_user(uid)
        return {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "photo_url": user.photo_url,
            "email_verified": user.email_verified,
        }
    except Exception as e:
        logger.warning(f"Failed to fetch Firebase user {uid}: {e}")
        return None
