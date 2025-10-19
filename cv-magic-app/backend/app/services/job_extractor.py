import json
import re
from typing import Dict, Any, Optional
from ..ai.ai_service import ai_service

async def extract_job_metadata(job_description: str, user: Any = None) -> Dict[str, Any]:
    """
    Extract metadata from job description using AI.
    
    Args:
        job_description: The job description text
        user: User context for AI service initialization
        
    Returns:
        Dictionary containing extracted metadata
    """
    if not job_description or len(job_description.strip()) < 10:
        return {"error": "Job description too short or empty"}
    
    # Use the new v2 function for better company extraction
    return await extract_job_metadata_v2("", job_description, user)


def extract_job_info_fallback(job_description: str) -> Dict[str, Any]:
    """
    Fallback method to extract job information using regex patterns.
    
    Args:
        job_description: The job description text
        
    Returns:
        Dictionary containing extracted metadata
    """
    job_title = None
    company = None
    
    try:
        # Common patterns for job titles
        title_patterns = [
            r'(?:Job\s+Title|Position|Role):\s*([^\n\r]+)',
            r'(?:We\s+are\s+looking\s+for\s+a\s+)([^\n\r]+)',
            r'(?:Seeking\s+a\s+)([^\n\r]+)',
            r'(?:Hiring\s+for\s+)([^\n\r]+)',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                job_title = match.group(1).strip()
                break
        
        # Common patterns for company names (prioritize recruitment agencies)
        company_patterns = [
            # Recruitment agency patterns (highest priority)
            r'(?:Reference Number:.*?)([A-Z][a-zA-Z\s&.-]+?)(?:\s+privacy|\s+recruitment|$)',
            r'(?:By clicking \'apply\', you give your express consent that )([A-Z][a-zA-Z\s&.-]+?)(?:\s+may use)',
            r'(?:Robert Half|Hays|Randstad|Adecco|Manpower|Michael Page|Hudson|Chandler Macleod|SEEK)',
            
            # Standard company patterns
            r'(?:Company|Organization|Employer):\s*([^\n\r]+)',
            r'(?:About\s+)([^\n\r]+?)(?:\s+is\s+looking|\s+seeks|\s+hires)',
            r'(?:at\s+)([^\n\r]+?)(?:\s+we\s+are|\s+is\s+seeking)',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                break
        
        return {
            "job_title": job_title,
            "company": company
        }
        
    except Exception as e:
        return {"error": f"Fallback extraction failed: {str(e)}"}




def validate_job_description(job_description: str) -> Dict[str, Any]:
    """
    Validate job description content.
    
    Args:
        job_description: The job description text to validate
        
    Returns:
        Dictionary containing validation results
    """
    if not job_description:
        return {"valid": False, "error": "Job description is empty"}
    
    if len(job_description.strip()) < 10:
        return {"valid": False, "error": "Job description is too short"}
    
    if len(job_description) > 50000:
        return {"valid": False, "error": "Job description is too long"}
    
    # Check for common job description indicators
    job_indicators = [
        r'responsibilities',
        r'requirements',
        r'qualifications',
        r'experience',
        r'skills',
        r'position',
        r'role',
        r'job',
    ]
    
    found_indicators = []
    for indicator in job_indicators:
        if re.search(indicator, job_description, re.IGNORECASE):
            found_indicators.append(indicator)
    
    if len(found_indicators) < 2:
        return {
            "valid": False, 
            "error": "Content doesn't appear to be a job description",
            "found_indicators": found_indicators
        }
    
    return {
        "valid": True,
        "length": len(job_description),
        "found_indicators": found_indicators
    }


# ============================================================================
# NEW: Single AI Method Integration
# Added: [DATE]
# Maintains backward compatibility while using new CompanyExtractor
# ============================================================================

from app.services.company_extractor import CompanyExtractor

async def extract_job_metadata_v2(jd_url: str, jd_text: str, user: Any = None) -> Dict[str, Any]:
    """
    New version using single AI company extractor
    
    Args:
        jd_url: Job description URL
        jd_text: Job description text
        user: User context for AI service initialization
        
    Returns:
        Dictionary with job metadata including company name
    """
    from app.ai.ai_service import AIServiceManager
    
    ai_service = AIServiceManager()
    extractor = CompanyExtractor(ai_service)
    
    result = await extractor.extract(jd_url, jd_text, user)
    
    return {
        "job_title": "",  # TODO: Extract job title separately if needed
        "company": result.name,
        "company_normalized": result.normalized,
        "confidence": result.confidence.value,
        "is_agency": result.is_agency
    }


# Note: The original extract_job_metadata function is preserved above
# New code should use extract_job_metadata_v2 for better company extraction
