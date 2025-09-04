"""
Standardized exception handling and validation for the backend
"""

from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from pydantic import BaseModel, ValidationError
import logging

# Configure logger
logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base API error class"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationError(APIError):
    """Validation error"""
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, details)
        self.field = field


class FileNotFoundError(APIError):
    """File not found error"""
    def __init__(self, filename: str, path: Optional[str] = None):
        message = f"File not found: {filename}"
        if path:
            message += f" at {path}"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class UnsupportedFileTypeError(APIError):
    """Unsupported file type error"""
    def __init__(self, filename: str, supported_types: List[str]):
        message = f"Unsupported file type for {filename}. Supported types: {', '.join(supported_types)}"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class AIServiceError(APIError):
    """AI service error"""
    def __init__(self, message: str, service: str = "AI", details: Optional[Dict[str, Any]] = None):
        super().__init__(f"{service} service error: {message}", status.HTTP_503_SERVICE_UNAVAILABLE, details)


class TimeoutError(APIError):
    """Timeout error"""
    def __init__(self, operation: str, timeout_seconds: int):
        message = f"Operation '{operation}' timed out after {timeout_seconds} seconds"
        super().__init__(message, status.HTTP_408_REQUEST_TIMEOUT)


def handle_api_error(error: APIError) -> HTTPException:
    """Convert APIError to HTTPException"""
    logger.error(f"API Error: {error.message}", extra={"details": error.details})
    return HTTPException(
        status_code=error.status_code,
        detail={
            "message": error.message,
            "details": error.details
        }
    )


def handle_validation_error(error: ValidationError) -> HTTPException:
    """Handle Pydantic validation errors"""
    logger.error(f"Validation Error: {error}")
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "message": "Validation failed",
            "errors": error.errors()
        }
    )


def handle_unexpected_error(error: Exception, context: str = "") -> HTTPException:
    """Handle unexpected errors"""
    logger.exception(f"Unexpected error in {context}: {error}")
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "message": "An unexpected error occurred",
            "context": context
        }
    )


# Decorator for consistent error handling
def handle_errors(context: str = ""):
    """Decorator to handle errors consistently"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except APIError as e:
                raise handle_api_error(e)
            except ValidationError as e:
                raise handle_validation_error(e)
            except Exception as e:
                raise handle_unexpected_error(e, context or func.__name__)
        
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except APIError as e:
                raise handle_api_error(e)
            except ValidationError as e:
                raise handle_validation_error(e)
            except Exception as e:
                raise handle_unexpected_error(e, context or func.__name__)
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Validation schemas
class CVFilenameRequest(BaseModel):
    cv_filename: str
    
    class Config:
        str_strip_whitespace = True


class AnalyzeFitRequest(BaseModel):
    cv_filename: str
    text: str
    
    class Config:
        str_strip_whitespace = True


class JobSaveRequest(BaseModel):
    job_link: str
    jd_text: str
    tailored_cv: str
    applied: bool = False
    
    class Config:
        str_strip_whitespace = True


# Validation functions
def validate_filename(filename: str, supported_extensions: List[str]) -> None:
    """Validate filename and extension"""
    if not filename:
        raise ValidationError("Filename cannot be empty")
    
    if not filename.strip():
        raise ValidationError("Filename cannot be only whitespace")
    
    file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
    if f".{file_extension}" not in supported_extensions:
        raise UnsupportedFileTypeError(filename, supported_extensions)


def validate_file_exists(filepath: str) -> None:
    """Validate that file exists"""
    import os
    if not os.path.exists(filepath):
        filename = os.path.basename(filepath)
        raise FileNotFoundError(filename, filepath)


def validate_text_content(text: str, min_length: int = 10, field_name: str = "text") -> None:
    """Validate text content"""
    if not text or not text.strip():
        raise ValidationError(f"{field_name} cannot be empty")
    
    if len(text.strip()) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters")


def validate_json_data(data: dict, required_fields: List[str]) -> None:
    """Validate JSON data has required fields"""
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
