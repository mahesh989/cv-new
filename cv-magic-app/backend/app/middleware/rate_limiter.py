"""
Rate limiting middleware for API endpoints
"""
import time
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from collections import defaultdict, deque
import asyncio
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter using sliding window algorithm"""
    
    def __init__(self):
        # Store rate limit data: {key: deque of timestamps}
        self.requests = defaultdict(deque)
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed based on rate limit"""
        now = time.time()
        
        # Clean up old entries periodically
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(now)
            self.last_cleanup = now
        
        # Get request history for this key
        request_times = self.requests[key]
        
        # Remove requests outside the window
        cutoff = now - window
        while request_times and request_times[0] <= cutoff:
            request_times.popleft()
        
        # Check if under limit
        if len(request_times) < limit:
            request_times.append(now)
            return True
        
        return False
    
    def _cleanup_old_entries(self, now: float):
        """Clean up old entries to prevent memory leaks"""
        cutoff = now - 3600  # Remove entries older than 1 hour
        keys_to_remove = []
        
        for key, request_times in self.requests.items():
            while request_times and request_times[0] <= cutoff:
                request_times.popleft()
            
            if not request_times:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.requests[key]
    
    def get_remaining_requests(self, key: str, limit: int, window: int) -> int:
        """Get remaining requests for a key"""
        now = time.time()
        request_times = self.requests[key]
        
        # Remove old entries
        cutoff = now - window
        while request_times and request_times[0] <= cutoff:
            request_times.popleft()
        
        return max(0, limit - len(request_times))
    
    def get_reset_time(self, key: str, window: int) -> float:
        """Get time when rate limit resets"""
        if not self.requests[key]:
            return time.time()
        
        oldest_request = self.requests[key][0]
        return oldest_request + window


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware:
    """Rate limiting middleware for FastAPI"""
    
    def __init__(self, app, default_limit: int = 100, default_window: int = 60):
        self.app = app
        self.default_limit = default_limit
        self.default_window = default_window
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Get rate limit configuration
            limit, window = self._get_rate_limit_config(request)
            
            # Get client identifier
            client_id = self._get_client_id(request)
            
            # Check rate limit
            if not rate_limiter.is_allowed(client_id, limit, window):
                response = JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Rate limit exceeded",
                        "retry_after": rate_limiter.get_reset_time(client_id, window)
                    },
                    headers={
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(rate_limiter.get_reset_time(client_id, window))),
                        "Retry-After": str(int(rate_limiter.get_reset_time(client_id, window) - time.time()))
                    }
                )
                await response(scope, receive, send)
                return
            
            # Add rate limit headers
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = dict(message.get("headers", []))
                    headers.extend([
                        (b"x-ratelimit-limit", str(limit).encode()),
                        (b"x-ratelimit-remaining", str(rate_limiter.get_remaining_requests(client_id, limit, window)).encode()),
                        (b"x-ratelimit-reset", str(int(rate_limiter.get_reset_time(client_id, window))).encode())
                    ])
                    message["headers"] = list(headers.items())
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)
    
    def _get_rate_limit_config(self, request: Request) -> tuple[int, int]:
        """Get rate limit configuration for request"""
        path = request.url.path
        
        # Different limits for different endpoints
        if path.startswith("/api/auth/login"):
            return 5, 60  # 5 attempts per minute for login
        elif path.startswith("/api/auth/register"):
            return 3, 60  # 3 registrations per minute
        elif path.startswith("/api/auth/forgot-password"):
            return 3, 300  # 3 password reset requests per 5 minutes
        elif path.startswith("/api/auth/send-verification"):
            return 5, 300  # 5 verification emails per 5 minutes
        elif path.startswith("/api/user/files/upload"):
            return 10, 60  # 10 file uploads per minute
        elif path.startswith("/api/user/analysis"):
            return 20, 60  # 20 analysis requests per minute
        elif path.startswith("/api/admin"):
            return 50, 60  # 50 admin requests per minute
        else:
            return self.default_limit, self.default_window
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get user ID from token first
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                # Extract user ID from JWT token (simplified)
                # In production, you'd properly decode the JWT
                return f"user:{auth_header[7:15]}"  # Use first 8 chars of token
            except:
                pass
        
        # Fall back to IP address
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        return f"ip:{ip}"


def create_rate_limit_middleware(app, default_limit: int = 100, default_window: int = 60):
    """Create rate limiting middleware"""
    return RateLimitMiddleware(app, default_limit, default_window)
