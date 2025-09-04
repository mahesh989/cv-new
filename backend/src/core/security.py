"""
Security utilities and middleware for the backend
"""

import os
import re
import hashlib
import secrets
from typing import List, Optional, Set
from pathlib import Path

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import mimetypes

# Security constants
ALLOWED_FILE_EXTENSIONS = {'.pdf', '.docx', '.txt'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
BLOCKED_FILENAMES = {'con', 'prn', 'aux', 'nul', 'com1', 'com2', 'lpt1', 'lpt2'}
DANGEROUS_PATTERNS = [
    r'\.\./',  # Directory traversal
    r'\\\\',   # UNC paths
    r'[<>:"|?*]',  # Invalid filename characters
]


class SecurityValidator:
    """Security validation utilities"""
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """Validate filename for security issues"""
        if not filename or not filename.strip():
            return False
        
        # Check for dangerous patterns
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, filename):
                return False
        
        # Check for blocked filenames
        name_without_ext = Path(filename).stem.lower()
        if name_without_ext in BLOCKED_FILENAMES:
            return False
        
        # Check extension
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_FILE_EXTENSIONS:
            return False
        
        return True
    
    @staticmethod
    def validate_file_content(file_path: str) -> bool:
        """Validate file content type matches extension"""
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            ext = Path(file_path).suffix.lower()
            
            # Expected MIME types
            expected_types = {
                '.pdf': 'application/pdf',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.txt': 'text/plain'
            }
            
            expected = expected_types.get(ext)
            if expected and mime_type != expected:
                # Additional check for common cases
                if ext == '.docx' and not mime_type:
                    # DOCX files might not be detected properly
                    return SecurityValidator._check_docx_header(file_path)
                return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def _check_docx_header(file_path: str) -> bool:
        """Check if file has valid DOCX header"""
        try:
            with open(file_path, 'rb') as f:
                # DOCX files start with PK (ZIP header)
                header = f.read(4)
                return header.startswith(b'PK')
        except Exception:
            return False
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Ensure reasonable length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            max_name_length = 255 - len(ext)
            sanitized = name[:max_name_length] + ext
        
        return sanitized
    
    @staticmethod
    def validate_file_size(file_path: str, max_size: int = MAX_FILE_SIZE) -> bool:
        """Validate file size"""
        try:
            size = os.path.getsize(file_path)
            return size <= max_size
        except Exception:
            return False
    
    @staticmethod
    def validate_directory_traversal(path: str, allowed_base: str) -> bool:
        """Prevent directory traversal attacks"""
        try:
            # Resolve absolute paths
            abs_path = os.path.abspath(path)
            abs_base = os.path.abspath(allowed_base)
            
            # Check if path is within allowed base
            return abs_path.startswith(abs_base)
        except Exception:
            return False


class ContentSecurityPolicy:
    """Content Security Policy utilities"""
    
    @staticmethod
    def get_headers() -> dict:
        """Get CSP headers for responses"""
        return {
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }


class RateLimiter:
    """Enhanced rate limiter with different limits per endpoint"""
    
    def __init__(self):
        self.limits = {
            'default': {'requests': 100, 'window': 60},  # 100 per minute
            'upload': {'requests': 10, 'window': 60},    # 10 uploads per minute
            'analysis': {'requests': 20, 'window': 60},  # 20 analyses per minute
            'ai': {'requests': 30, 'window': 60},        # 30 AI requests per minute
        }
        self.requests = {}
    
    def is_allowed(self, client_id: str, endpoint_type: str = 'default') -> bool:
        """Check if request is allowed"""
        import time
        
        limit_config = self.limits.get(endpoint_type, self.limits['default'])
        max_requests = limit_config['requests']
        window = limit_config['window']
        
        now = time.time()
        window_start = now - window
        
        key = f"{client_id}:{endpoint_type}"
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.requests[key]) >= max_requests:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True


# Global instances
security_validator = SecurityValidator()
csp = ContentSecurityPolicy()
rate_limiter = RateLimiter()


# Middleware functions
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Add CSP headers
    headers = csp.get_headers()
    for key, value in headers.items():
        response.headers[key] = value
    
    return response


async def file_security_middleware(request: Request, call_next):
    """Validate file operations for security"""
    # Only apply to file-related endpoints
    if '/upload' in str(request.url) or '/download' in str(request.url):
        # Additional security checks can be added here
        pass
    
    return await call_next(request)


def validate_upload_security(filename: str, file_path: str, allowed_dir: str) -> None:
    """Comprehensive upload security validation"""
    # Validate filename
    if not security_validator.validate_filename(filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid filename: {filename}"
        )
    
    # Validate directory traversal
    if not security_validator.validate_directory_traversal(file_path, allowed_dir):
        raise HTTPException(
            status_code=400,
            detail="Invalid file path"
        )
    
    # Validate file size
    if os.path.exists(file_path):
        if not security_validator.validate_file_size(file_path):
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Validate file content
        if not security_validator.validate_file_content(file_path):
            raise HTTPException(
                status_code=400,
                detail="File content doesn't match extension or is invalid"
            )


def get_client_id(request: Request) -> str:
    """Extract client identifier for rate limiting"""
    # Use IP address as basic identifier
    forwarded = request.headers.get('x-forwarded-for')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.client.host if request.client else 'unknown'


def check_rate_limit(request: Request, endpoint_type: str = 'default') -> None:
    """Check rate limit for request"""
    client_id = get_client_id(request)
    
    if not rate_limiter.is_allowed(client_id, endpoint_type):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )


class APIKeyValidator:
    """API key validation for protected endpoints"""
    
    def __init__(self, api_keys: Optional[Set[str]] = None):
        self.api_keys = api_keys or set()
        # Add default API key from environment
        default_key = os.getenv('API_KEY')
        if default_key:
            self.api_keys.add(default_key)
    
    def validate_key(self, api_key: str) -> bool:
        """Validate API key"""
        return api_key in self.api_keys
    
    def add_key(self, api_key: str) -> None:
        """Add new API key"""
        self.api_keys.add(api_key)
    
    def remove_key(self, api_key: str) -> None:
        """Remove API key"""
        self.api_keys.discard(api_key)


# Global API key validator
api_key_validator = APIKeyValidator()


def require_api_key(api_key: str = None) -> None:
    """Require valid API key for protected endpoints"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    if not api_key_validator.validate_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )


def generate_secure_filename(original_filename: str) -> str:
    """Generate secure filename with timestamp and random suffix"""
    import time
    
    # Sanitize original filename
    sanitized = security_validator.sanitize_filename(original_filename)
    
    # Extract extension
    name, ext = os.path.splitext(sanitized)
    
    # Generate secure suffix
    timestamp = str(int(time.time()))
    random_suffix = secrets.token_hex(4)
    
    # Combine parts
    secure_name = f"{name[:50]}_{timestamp}_{random_suffix}{ext}"
    
    return secure_name
