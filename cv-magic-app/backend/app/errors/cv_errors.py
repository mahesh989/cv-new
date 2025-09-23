"""
Custom exceptions for CV processing
"""

class CVError(Exception):
    """Base exception for CV-related errors"""
    pass


class CVNotFoundError(CVError):
    """Raised when a CV file is not found"""
    pass


class CVFormatError(CVError):
    """Raised when a CV file has invalid format"""
    pass


class CVVersionError(CVError):
    """Raised when there's an error with CV versioning"""
    pass