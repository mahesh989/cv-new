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


class APIKeyError(Exception):
    """Base class for API key related errors"""
    pass


class APIKeyNotFoundError(APIKeyError):
    """Raised when no API key is found for a user and provider"""
    def __init__(self, provider: str, user_email: str = None):
        self.provider = provider
        self.user_email = user_email
        if user_email:
            self.message = f"No API key configured for {provider}. Please configure your API key in settings."
        else:
            self.message = f"No API key configured for {provider}. Please configure your API key."
        super().__init__(self.message)


class APIKeyInvalidError(APIKeyError):
    """Raised when an API key is invalid or expired"""
    def __init__(self, provider: str, user_email: str = None):
        self.provider = provider
        self.user_email = user_email
        if user_email:
            self.message = f"Invalid API key for {provider}. Please check and update your API key in settings."
        else:
            self.message = f"Invalid API key for {provider}. Please check and update your API key."
        super().__init__(self.message)


class AIProviderUnavailableError(APIKeyError):
    """Raised when AI provider is unavailable"""
    def __init__(self, provider: str, user_email: str = None):
        self.provider = provider
        self.user_email = user_email
        if user_email:
            self.message = f"AI provider {provider} is currently unavailable. Please try again later or contact support."
        else:
            self.message = f"AI provider {provider} is currently unavailable. Please try again later."
        super().__init__(self.message)
