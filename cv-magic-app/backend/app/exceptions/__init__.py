"""
Custom exceptions package
"""

from .cv_exceptions import (
    CVError,
    CVNotFoundError,
    EmptyContentError,
    CVFormatError,
    CVVersionError,
    CVSelectionError,
    TailoredCVNotFoundError
)

__all__ = [
    'CVError',
    'CVNotFoundError',
    'EmptyContentError',
    'CVFormatError',
    'CVVersionError',
    'CVSelectionError',
    'TailoredCVNotFoundError'
]
