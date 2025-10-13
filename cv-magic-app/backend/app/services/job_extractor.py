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
        6. RETURN ONLY THE JSON OBJECT - NO markdown, NO explanations, NO code blocks
        
        JOB TITLE EXTRACTION:
        - Look for the MAIN job title throughout the ENTIRE text
        - Job titles can appear anywhere: at the top, in headers, after "Position:", "Role:", "Job Title:", or in the body
        - Common patterns: "Data Entry Officer", "Business Analyst", "Software Engineer", "Marketing Manager"
        - Look for titles with specific roles like "Officer", "Analyst", "Manager", "Engineer", "Specialist", "Coordinator", "Clerk", "Administrator", "Developer", "Designer"
        - Avoid generic terms like "Manager" alone if a more specific title exists (e.g., "Data Analytics Officer" not just "Manager")
        - If multiple titles appear, choose the most specific and prominent one
        - Examples: 
          * "Data Entry Officer" from "Data Entry Officer\nFull-time\nHOBAN Recruitment"
          * "Senior Software Engineer" from "Position: Senior Software Engineer"
          * "Marketing Coordinator" from "We are hiring a Marketing Coordinator to join our team"
        
        COMPANY NAME EXTRACTION:
        - **RECRUITMENT AGENCY DETECTION**:
          * If this is a recruitment agency posting, extract the RECRUITMENT AGENCY NAME, NOT the client company
          * Recruitment agencies often have these characteristics:
            - Company name contains words like "Recruitment", "Recruiter", "Staffing", "Personnel", "Consulting", "Solutions", "Group", "Resources"
            - Mentions "Reference Number:", "Job Reference:", "Job ID:"
            - Has privacy notices, terms about "express consent", data handling
            - Generic language like "our client", "a leading company", "well-known organization"
            - Professional recruiter tone with structured application processes
          * Look for the agency name anywhere in the text: header, footer, contact section, "About us", email signatures
          * Examples: 
            - "HOBAN Recruitment" from anywhere in the text
            - "Robert Half" from "Apply through Robert Half"
            - "Hays" from "Contact: jobs@hays.com.au"
        
        - **DIRECT COMPANY POSTING**:
          * If NOT a recruitment agency, extract the actual hiring company name
          * Look throughout the entire text: headers, "About [Company]", "Join [Company]", contact info, email domains, website URLs
          * Company names are often in:
            - "About us" or "About the company" sections
            - Email domains (e.g., jobs@company.com → "Company")
            - Website URLs (e.g., www.company.com → "Company")
            - "Join our team at [Company]"
            - After the job title (e.g., "Engineer - TechCorp")
          * Avoid generic terms like "Company", "Organization", "Client", "Employer", "warehouse", "sales", "team"
        
        - **IMPORTANT**: Scan the ENTIRE text, not just the beginning. Company names can appear anywhere.
        
        Job Description:
        ```
        {job_description}
        ```
        
        Return ONLY this JSON object with NO additional text:
        {{"job_title": "actual job title or null", "company": "actual company name or null"}}
        """
        
        # Create a mock user for AI extraction
        from app.models.auth import UserData
        from datetime import datetime, timezone
        mock_user = UserData(
            id="extraction_user",
            email="extraction@system.local",
            name="System",
            created_at=datetime.now(timezone.utc),
            is_active=True
        )
        
        # Use the AI service to extract information
        result_text = await ai_service.generate_response(
            prompt=prompt,
            user=mock_user,
            temperature=0.0,
            max_tokens=300
        )
        
        # Clean and parse the AI response
        result_text = result_text.strip()
        
        # Remove markdown code blocks if present
        if result_text.startswith('```'):
            # Remove opening code block
            result_text = re.sub(r'^```(?:json)?\s*\n?', '', result_text)
            # Remove closing code block
            result_text = re.sub(r'\n?```\s*$', '', result_text)
            result_text = result_text.strip()
        
        # Try to find JSON object in the response
        json_match = re.search(r'\{[^{}]*\}', result_text)
        if json_match:
            result_text = json_match.group(0)
        
        # Parse JSON
        result = json.loads(result_text)
        
        # Validate the result structure
        if not isinstance(result, dict):
            return {
                "error": "AI returned invalid format",
                "job_title": None,
                "company": None
            }
        
        # Ensure required keys exist
        job_title = result.get("job_title")
        company = result.get("company")
        
        # Additional validation: reject obviously wrong extractions
        if company and company.lower() in ['company', 'organization', 'client', 'employer', 'warehouse', 'sales', 'marketing', 'unknown']:
            company = None
        
        if job_title and job_title.lower() in ['position', 'role', 'opportunity', 'job', 'unknown']:
            job_title = None
        
        return {
            "job_title": job_title,
            "company": company
        }
            
    except json.JSONDecodeError as e:
        return {
            "error": f"AI returned invalid JSON: {str(e)}",
            "raw_response": result_text[:500] if 'result_text' in locals() else "N/A",
            "job_title": None,
            "company": None
        }
    except Exception as e:
        return {
            "error": f"Failed to extract job metadata: {str(e)}",
            "job_title": None,
            "company": None
        }


# (Removed) extract_job_info_fallback: no longer used; AI-only extraction is enforced.




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
