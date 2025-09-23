"""
Custom exceptions for CV processing and selection
"""

class CVError(Exception):
    """Base class for CV-related errors"""
    pass

class CVNotFoundError(CVError):
    """Raised when a CV file is not found"""
    pass

class EmptyContentError(CVError):
    """Raised when CV content is empty or insufficient"""
    pass

class CVFormatError(CVError):
    """Raised when CV format is invalid"""
    pass

class CVVersionError(CVError):
    """Raised when there's an issue with CV versioning"""
    pass

class CVSelectionError(CVError):
    """Raised when there's an error selecting appropriate CV"""
    pass

class TailoredCVNotFoundError(CVError):
    """Raised when a tailored CV is not found for rerun analysis."""
    def __init__(self, company: str):
        self.company = company
        self.message = f"No tailored CV found for company: {company}"
        super().__init__(self.message)
