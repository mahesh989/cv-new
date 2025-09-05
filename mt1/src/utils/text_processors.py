"""
Text Processing Utilities - Pure Functions Only
===============================================

This module contains pure utility functions for text processing and data extraction.
These functions are extracted from analysis_results_saver.py and designed to be:
- Pure functions (no global state modification)
- Deterministic for the same inputs
- Side-effect free (except logging)
- Easily testable
"""

import re
import json
from datetime import datetime
from typing import Dict, Any, Optional


def create_company_slug(company_name: str) -> str:
    """
    Create a filesystem-safe slug from company name
    
    Args:
        company_name: Raw company name
        
    Returns:
        str: Cleaned company slug safe for filenames
    """
    if not company_name or not company_name.strip():
        return f"Company_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Clean up company name for filename
    company_slug = re.sub(r'[^\w\s&.-]', '', company_name)
    company_slug = re.sub(r'\s+', '_', company_slug)
    company_slug = company_slug.strip('_')
    
    # Ensure minimum length
    if len(company_slug) < 3:
        return f"Company_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return company_slug


def extract_json_from_response(response_text: str) -> Optional[Dict]:
    """
    Extract JSON from AI response text that may contain extra content
    
    Args:
        response_text: Raw response text from AI
        
    Returns:
        dict or None: Parsed JSON data or None if parsing fails
    """
    if not response_text:
        return None
    
    try:
        # Try to find JSON in the response (in case there's extra text)
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
        else:
            # Try to parse the whole response as JSON
            return json.loads(response_text)
    
    except (json.JSONDecodeError, ValueError):
        return None


def get_fallback_company_data() -> Dict[str, str]:
    """
    Return fallback company data structure when extraction fails
    
    Returns:
        dict: Standard fallback company information structure
    """
    return {
        "company_name": "Unknown",
        "job_title": "Unknown", 
        "location": "Unknown",
        "experience_required": "Unknown",
        "seniority_level": "Unknown",
        "industry": "Unknown",
        "phone_number": "Unknown",
        "email": "Unknown",
        "website": "Unknown",
        "work_type": "Unknown"
    }


def clean_text_for_analysis(text: str, max_length: int = 3000) -> str:
    """
    Clean and truncate text for AI analysis
    
    Args:
        text: Input text to clean
        max_length: Maximum length to truncate to
        
    Returns:
        str: Cleaned and truncated text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    # Truncate if too long
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned


def create_analysis_metadata(company_name: str, analysis_type: str = "analysis_results") -> Dict[str, Any]:
    """
    Create standard metadata structure for analysis results
    
    Args:
        company_name: Name of the company
        analysis_type: Type of analysis being performed
        
    Returns:
        dict: Standard metadata structure
    """
    return {
        "company_name": company_name,
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "analysis_type": analysis_type
    }


def validate_analysis_inputs(cv_text: str, jd_text: str) -> bool:
    """
    Validate that analysis inputs are not empty
    
    Args:
        cv_text: CV content
        jd_text: Job description content
        
    Returns:
        bool: True if inputs are valid, False otherwise
    """
    return bool(cv_text and cv_text.strip() and jd_text and jd_text.strip())


def extract_text_snippet(text: str, max_words: int = 50) -> str:
    """
    Extract a snippet of text for preview purposes
    
    Args:
        text: Full text to extract from
        max_words: Maximum number of words to include
        
    Returns:
        str: Text snippet with ellipsis if truncated
    """
    if not text:
        return ""
    
    words = text.split()
    if len(words) <= max_words:
        return text
    
    snippet = ' '.join(words[:max_words])
    return snippet + "..."


def normalize_company_name(company_name: str) -> str:
    """
    Normalize company name for consistent processing
    
    Args:
        company_name: Raw company name
        
    Returns:
        str: Normalized company name
    """
    if not company_name:
        return "Unknown Company"
    
    # Remove common corporate suffixes for comparison
    company_clean = company_name.strip()
    
    # Remove extra whitespace
    company_clean = re.sub(r'\s+', ' ', company_clean)
    
    # Remove quotes if they wrap the entire name
    if company_clean.startswith('"') and company_clean.endswith('"'):
        company_clean = company_clean[1:-1]
    
    if company_clean.startswith("'") and company_clean.endswith("'"):
        company_clean = company_clean[1:-1]
    
    return company_clean.strip()


def safe_file_path_component(text: str) -> str:
    """
    Convert text to a safe file path component
    
    Args:
        text: Text to convert
        
    Returns:
        str: Safe filename component
    """
    if not text:
        return "unknown"
    
    # Replace spaces with underscores and remove unsafe characters
    safe_text = re.sub(r'[^\w\s-]', '', text)
    safe_text = re.sub(r'\s+', '_', safe_text.strip())
    safe_text = safe_text.strip('_')
    
    # Ensure it's not empty
    if not safe_text:
        return "unknown"
    
    # Limit length
    if len(safe_text) > 100:
        safe_text = safe_text[:100]
    
    return safe_text.lower()


def format_datetime_for_display(dt: datetime = None) -> str:
    """
    Format datetime for display in reports
    
    Args:
        dt: Datetime object, defaults to now
        
    Returns:
        str: Formatted datetime string
    """
    if dt is None:
        dt = datetime.now()
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def count_words(text: str) -> int:
    """
    Count words in text
    
    Args:
        text: Text to count words in
        
    Returns:
        int: Number of words
    """
    if not text:
        return 0
    
    return len(text.split())


def extract_json_from_file_content(content: str) -> Optional[Dict]:
    """
    Extract JSON from file content that may contain mixed text and JSON
    
    Args:
        content: File content that may contain JSON at the end
        
    Returns:
        dict or None: Parsed JSON data or None if not found
    """
    if not content:
        return None
    
    try:
        # Look for JSON at the end of the file
        json_start = content.rfind('{')
        if json_start != -1:
            json_content = content[json_start:]
            return json.loads(json_content)
    except (json.JSONDecodeError, ValueError):
        pass
    
    return None
