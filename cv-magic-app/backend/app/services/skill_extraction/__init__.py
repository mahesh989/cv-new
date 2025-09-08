"""
Skill Extraction Service Package

This package provides skill extraction capabilities for CV and Job Description analysis.
"""

from .skill_extraction_service import skill_extraction_service
from .result_saver import result_saver

__all__ = ["skill_extraction_service", "result_saver"]
