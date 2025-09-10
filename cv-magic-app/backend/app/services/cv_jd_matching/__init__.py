"""
CV-JD Matching Module

This module provides functionality to match CV content against job description keywords
using AI-powered smart matching logic.
"""

from .cv_jd_matcher import (
    CVJDMatcher,
    CVJDMatchResult,
    match_cv_against_company_jd,
    match_and_save_cv_jd
)

from .cv_jd_matching_prompt import (
    get_cv_jd_matching_prompts,
    CV_JD_MATCHING_SYSTEM_PROMPT,
    CV_JD_MATCHING_USER_PROMPT
)

__all__ = [
    'CVJDMatcher',
    'CVJDMatchResult', 
    'match_cv_against_company_jd',
    'match_and_save_cv_jd',
    'get_cv_jd_matching_prompts',
    'CV_JD_MATCHING_SYSTEM_PROMPT',
    'CV_JD_MATCHING_USER_PROMPT'
]
