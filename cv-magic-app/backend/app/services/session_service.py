"""
Advanced session management service
"""
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.database import get_database
from app.models.user import UserSession
from app.services.audit_service import audit_service
import logging

logger = logging.getLogger(__name__)


class SessionService:
    """Advanced session management service"""
    
    def __init__(self):
        self.max_sessions_per_user = 5
        self.session_timeout = timedelta(hours=8)
        self.inactive_timeout = timedelta(minutes=30)
    
    def create_session(self, user_id: int, user_agent: str, ip_address: str, 
                      device_fingerprint: Optional[str] = None) -> str:
        """Create a new session for user"""
        try:
            # Check if user has too many active sessions
            if self._exceeds_max_sessions(user_id):
                self._cleanup_oldest_sessions(user_id)
            
            # Generate session token
            session_token = self._generate_session_token()
            token_hash = hashlib.sha256(session_token.encode()).hexdigest()
            
            # Create session record
            db = next(get_database())
            session = UserSession(
                user_id=user_id,
                token_jti=token_hash,
                expires_at=datetime.now(timezone.utc) + self.session_timeout,
                user_agent=user_agent,
                ip_address=ip_address,
                is_blacklisted=False
            )
            
            db.add(session)
            db.commit()
            
            # Log session creation
            audit_service.log_authentication_event(
                user_id, "session_created", True, None,
                {"device_fingerprint": device_fingerprint}
            )
            
            return session_token
            
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create session"
            )
    
    def validate_session(self, session_token: str, user_agent: str, 
                       ip_address: str) -> Optional[Dict[str, Any]]:
        """Validate session token"""
        try:
            if not session_token:
                return None
            
            # Hash the token
            token_hash = hashlib.sha256(session_token.encode()).hexdigest()
            
            # Find session
            db = next(get_database())
            session = db.query(UserSession).filter(
                UserSession.token_jti == token_hash,
                UserSession.is_blacklisted == False,
                UserSession.expires_at > datetime.now(timezone.utc)
            ).first()
            
            if not session:
                return None
            
            # Check for session hijacking
            if self._is_session_hijacked(session, user_agent, ip_address):
                self._blacklist_session(session.id, "Session hijacking detected")
                return None
            
            # Update last activity
            session.last_activity = datetime.now(timezone.utc)
            db.commit()
            
            return {
                "user_id": session.user_id,
                "session_id": session.id,
                "created_at": session.created_at,
                "expires_at": session.expires_at
            }
            
        except Exception as e:
            logger.error(f"Failed to validate session: {str(e)}")
            return None
    
    def refresh_session(self, session_token: str) -> bool:
        """Refresh session expiry"""
        try:
            token_hash = hashlib.sha256(session_token.encode()).hexdigest()
            
            db = next(get_database())
            session = db.query(UserSession).filter(
                UserSession.token_jti == token_hash,
                UserSession.is_blacklisted == False
            ).first()
            
            if not session:
                return False
            
            # Extend session
            session.expires_at = datetime.now(timezone.utc) + self.session_timeout
            session.last_activity = datetime.now(timezone.utc)
            db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh session: {str(e)}")
            return False
    
    def invalidate_session(self, session_token: str, reason: str = "User logout") -> bool:
        """Invalidate session"""
        try:
            token_hash = hashlib.sha256(session_token.encode()).hexdigest()
            
            db = next(get_database())
            session = db.query(UserSession).filter(
                UserSession.token_jti == token_hash
            ).first()
            
            if not session:
                return False
            
            # Blacklist session
            session.is_blacklisted = True
            session.blacklist_reason = reason
            db.commit()
            
            # Log session invalidation
            audit_service.log_authentication_event(
                session.user_id, "session_invalidated", True, None,
                {"reason": reason}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to invalidate session: {str(e)}")
            return False
    
    def invalidate_all_user_sessions(self, user_id: int, reason: str = "Security action") -> int:
        """Invalidate all sessions for a user"""
        try:
            db = next(get_database())
            sessions = db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_blacklisted == False
            ).all()
            
            for session in sessions:
                session.is_blacklisted = True
                session.blacklist_reason = reason
            
            db.commit()
            
            # Log action
            audit_service.log_security_event(
                user_id, "all_sessions_invalidated", "medium", None,
                {"reason": reason, "sessions_count": len(sessions)}
            )
            
            return len(sessions)
            
        except Exception as e:
            logger.error(f"Failed to invalidate user sessions: {str(e)}")
            return 0
    
    def get_user_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all active sessions for user"""
        try:
            db = next(get_database())
            sessions = db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_blacklisted == False,
                UserSession.expires_at > datetime.now(timezone.utc)
            ).order_by(UserSession.created_at.desc()).all()
            
            return [
                {
                    "id": session.id,
                    "user_agent": session.user_agent,
                    "ip_address": session.ip_address,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat() if session.last_activity else None,
                    "expires_at": session.expires_at.isoformat(),
                    "is_current": False  # Will be determined by client
                }
                for session in sessions
            ]
            
        except Exception as e:
            logger.error(f"Failed to get user sessions: {str(e)}")
            return []
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            db = next(get_database())
            now = datetime.now(timezone.utc)
            
            # Get expired sessions
            expired_sessions = db.query(UserSession).filter(
                UserSession.expires_at < now
            ).all()
            
            # Delete expired sessions
            count = len(expired_sessions)
            for session in expired_sessions:
                db.delete(session)
            
            db.commit()
            
            logger.info(f"Cleaned up {count} expired sessions")
            return count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {str(e)}")
            return 0
    
    def _exceeds_max_sessions(self, user_id: int) -> bool:
        """Check if user exceeds maximum sessions"""
        try:
            db = next(get_database())
            active_sessions = db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_blacklisted == False,
                UserSession.expires_at > datetime.now(timezone.utc)
            ).count()
            
            return active_sessions >= self.max_sessions_per_user
            
        except Exception as e:
            logger.error(f"Failed to check max sessions: {str(e)}")
            return False
    
    def _cleanup_oldest_sessions(self, user_id: int):
        """Clean up oldest sessions for user"""
        try:
            db = next(get_database())
            oldest_sessions = db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_blacklisted == False
            ).order_by(UserSession.created_at.asc()).limit(1).all()
            
            for session in oldest_sessions:
                session.is_blacklisted = True
                session.blacklist_reason = "Maximum sessions exceeded"
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to cleanup oldest sessions: {str(e)}")
    
    def _is_session_hijacked(self, session: UserSession, user_agent: str, 
                           ip_address: str) -> bool:
        """Check if session is hijacked"""
        # Check for significant changes in user agent
        if session.user_agent and session.user_agent != user_agent:
            # Allow minor changes but flag major changes
            if len(session.user_agent) > 0 and len(user_agent) > 0:
                # Simple similarity check
                similarity = self._calculate_similarity(session.user_agent, user_agent)
                if similarity < 0.5:  # Less than 50% similar
                    return True
        
        # Check for IP address changes (if available)
        if session.ip_address and session.ip_address != ip_address:
            # Allow same subnet but flag different countries/regions
            # This is a simplified check - in production, you'd use GeoIP
            if not self._is_same_network(session.ip_address, ip_address):
                return True
        
        return False
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        if not str1 or not str2:
            return 0.0
        
        # Simple Jaccard similarity
        set1 = set(str1.lower().split())
        set2 = set(str2.lower().split())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _is_same_network(self, ip1: str, ip2: str) -> bool:
        """Check if two IPs are from the same network"""
        # Simplified check - in production, use proper IP analysis
        try:
            # Extract first 3 octets for basic network comparison
            network1 = ".".join(ip1.split(".")[:3])
            network2 = ".".join(ip2.split(".")[:3])
            return network1 == network2
        except:
            return False
    
    def _generate_session_token(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
    
    def _blacklist_session(self, session_id: int, reason: str):
        """Blacklist a session"""
        try:
            db = next(get_database())
            session = db.query(UserSession).filter(UserSession.id == session_id).first()
            
            if session:
                session.is_blacklisted = True
                session.blacklist_reason = reason
                db.commit()
                
                # Log security event
                audit_service.log_security_event(
                    session.user_id, "session_blacklisted", "high", None,
                    {"reason": reason, "session_id": session_id}
                )
                
        except Exception as e:
            logger.error(f"Failed to blacklist session: {str(e)}")


# Global session service instance
session_service = SessionService()
