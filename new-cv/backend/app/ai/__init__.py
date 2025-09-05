"""
AI Package

This package provides centralized AI management for the CV application.
"""

from .ai_config import ai_config
from .ai_service import ai_service
from .base_provider import BaseAIProvider, AIResponse

__all__ = [
    "ai_config",
    "ai_service", 
    "BaseAIProvider",
    "AIResponse"
]
