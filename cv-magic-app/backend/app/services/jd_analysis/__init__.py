"""
Job Description Analysis Service

This module provides functionality to analyze job descriptions and extract
required and preferred keywords using the centralized AI system.
"""

from .jd_analyzer import (
    JDAnalyzer, 
    JDAnalysisResult, 
    analyze_company_jd, 
    analyze_jd_file, 
    analyze_jd_text,
    analyze_and_save_company_jd,
    load_jd_analysis
)
from .jd_analysis_prompt import get_jd_analysis_prompts

__all__ = [
    'JDAnalyzer',
    'JDAnalysisResult', 
    'analyze_company_jd',
    'analyze_jd_file',
    'analyze_jd_text',
    'analyze_and_save_company_jd',
    'load_jd_analysis',
    'get_jd_analysis_prompts'
]
