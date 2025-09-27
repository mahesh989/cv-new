"""
Security middleware for API protection
"""
import time
from typing import Dict, List, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for adding security headers and protection"""
    
    def __init__(self, app, allowed_origins: List[str] = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]
        self.blocked_ips = set()
        self.suspicious_ips = {}  # Track suspicious activity
    
    async def dispatch(self, request: Request, call_next):
        # Check for blocked IPs
        client_ip = self._get_client_ip(request)
        if client_ip in self.blocked_ips:
            return JSONResponse(
                status_code=403,
                content={"detail": "Access denied"}
            )
        
        # Check for suspicious activity
        if self._is_suspicious_request(request):
            self._handle_suspicious_activity(client_ip, request)
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(response, request)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _is_suspicious_request(self, request: Request) -> bool:
        """Check if request is suspicious"""
        # Check for common attack patterns
        path = request.url.path.lower()
        user_agent = request.headers.get("user-agent", "").lower()
        
        # SQL injection patterns
        sql_patterns = ["'", '"', "union", "select", "drop", "delete", "insert", "update"]
        if any(pattern in path for pattern in sql_patterns):
            return True
        
        # XSS patterns
        xss_patterns = ["<script", "javascript:", "onload=", "onerror="]
        if any(pattern in path for pattern in xss_patterns):
            return True
        
        # Suspicious user agents
        suspicious_agents = ["bot", "crawler", "scanner", "hack", "exploit"]
        if any(agent in user_agent for agent in suspicious_agents):
            return True
        
        # Too many requests from same IP
        client_ip = self._get_client_ip(request)
        now = time.time()
        if client_ip in self.suspicious_ips:
            if now - self.suspicious_ips[client_ip]["last_seen"] < 60:  # Within 1 minute
                self.suspicious_ips[client_ip]["count"] += 1
                if self.suspicious_ips[client_ip]["count"] > 100:  # More than 100 requests per minute
                    return True
            else:
                self.suspicious_ips[client_ip] = {"count": 1, "last_seen": now}
        else:
            self.suspicious_ips[client_ip] = {"count": 1, "last_seen": now}
        
        return False
    
    def _handle_suspicious_activity(self, client_ip: str, request: Request):
        """Handle suspicious activity"""
        logger.warning(f"Suspicious activity detected from {client_ip}: {request.url.path}")
        
        # Increment suspicious count
        if client_ip in self.suspicious_ips:
            self.suspicious_ips[client_ip]["count"] += 1
        else:
            self.suspicious_ips[client_ip] = {"count": 1, "last_seen": time.time()}
        
        # Block IP if too many suspicious activities
        if self.suspicious_ips[client_ip]["count"] > 10:
            self.blocked_ips.add(client_ip)
            logger.warning(f"IP {client_ip} blocked due to suspicious activity")
    
    def _add_security_headers(self, response: Response, request: Request):
        """Add security headers to response"""
        # CORS headers
        origin = request.headers.get("origin")
        if origin and (origin in self.allowed_origins or "*" in self.allowed_origins):
            response.headers["Access-Control-Allow-Origin"] = origin
        elif "*" in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = "*"
        
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        # HSTS (only for HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Remove server information
        if "server" in response.headers:
            del response.headers["server"]


class SessionSecurityMiddleware(BaseHTTPMiddleware):
    """Session security middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.active_sessions = {}  # Track active sessions
        self.max_sessions_per_user = 5  # Maximum sessions per user
    
    async def dispatch(self, request: Request, call_next):
        # Check for session hijacking
        if self._is_session_hijacking_attempt(request):
            return JSONResponse(
                status_code=403,
                content={"detail": "Session security violation"}
            )
        
        # Check for concurrent sessions
        if self._exceeds_max_sessions(request):
            return JSONResponse(
                status_code=403,
                content={"detail": "Maximum sessions exceeded"}
            )
        
        response = await call_next(request)
        
        # Add session security headers
        response.headers["X-Session-Security"] = "enabled"
        
        return response
    
    def _is_session_hijacking_attempt(self, request: Request) -> bool:
        """Check for session hijacking attempts"""
        # Check for suspicious user agent changes
        user_agent = request.headers.get("user-agent", "")
        client_ip = self._get_client_ip(request)
        
        # In a real implementation, you'd check against stored session data
        # For now, we'll do basic checks
        if len(user_agent) < 10:  # Suspiciously short user agent
            return True
        
        return False
    
    def _exceeds_max_sessions(self, request: Request) -> bool:
        """Check if user exceeds maximum sessions"""
        # In a real implementation, you'd check against database
        # For now, we'll do basic tracking
        client_ip = self._get_client_ip(request)
        
        if client_ip in self.active_sessions:
            if self.active_sessions[client_ip] >= self.max_sessions_per_user:
                return True
            self.active_sessions[client_ip] += 1
        else:
            self.active_sessions[client_ip] = 1
        
        return False
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


def create_security_middleware(app, allowed_origins: List[str] = None):
    """Create security middleware"""
    return SecurityMiddleware(app, allowed_origins)


def create_session_security_middleware(app):
    """Create session security middleware"""
    return SessionSecurityMiddleware(app)
