import json
import re
from typing import Dict, Any, Optional
from ..ai.ai_service import ai_service

async def extract_job_metadata(job_description: str) -> Dict[str, Any]:
    """
    Extract metadata from job description using AI.
    
    Args:
        job_description: The job description text
        
    Returns:
        Dictionary containing extracted metadata
    """
    if not job_description or len(job_description.strip()) < 10:
        return {"error": "Job description too short or empty"}
    
    try:
        # Create a prompt for extracting job information
        prompt = f"""
        Analyze the following job description and extract the job title and company name.
        
        CRITICAL RULES:
        1. Extract ONLY information that ACTUALLY APPEARS in the text
        2. Do NOT infer or assume information not explicitly stated
        3. Return result in JSON format with exactly these keys: "job_title" and "company"
        4. If you cannot find either piece of information, return null for that field
        5. Be precise and extract only the actual job title and company name, not additional descriptive text
        
        COMPANY NAME EXTRACTION PRIORITY:
        - If this is a recruitment agency posting (look for "Reference Number:", "Robert Half", "Hays", "Randstad", "Adecco", "Manpower", "Michael Page", "Hudson", "Chandler Macleod", "SEEK", privacy notices, "express consent"), extract the RECRUITMENT AGENCY NAME
        - If it's a direct company posting, extract the hiring company name
        - Look for company names in headers, contact info, email domains, or website URLs
        - Avoid generic terms like "Company", "Organization", "Client"
        
        Job Description:
        {job_description}
        
        Return ONLY a JSON object in this exact format:
        {{"job_title": "actual job title or null", "company": "actual company name or null"}}
        """
        
        # Use the AI service to extract information
        result_text = await ai_service.generate_response(
            prompt=prompt,
            user=user,
            temperature=0.0,
            max_tokens=200
        )
        
        # Try to parse the JSON response
        try:
            # Clean the response text
            result_text = result_text.strip()
            
            # Remove any markdown formatting if present
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            result_text = result_text.strip()
            
            # Parse JSON
            result = json.loads(result_text)
            
            # Validate the result structure
            if not isinstance(result, dict):
                raise ValueError("Response is not a dictionary")
            
            # Ensure required keys exist
            if "job_title" not in result:
                result["job_title"] = None
            if "company" not in result:
                result["company"] = None
                
            return result
            
        except (json.JSONDecodeError, ValueError) as parse_error:
            # Fallback: try to extract using regex patterns
            return extract_job_info_fallback(job_description)
            
    except Exception as e:
        return {"error": f"Failed to extract job metadata: {str(e)}"}


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
