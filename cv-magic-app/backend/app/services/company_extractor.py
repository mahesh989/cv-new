"""
Single AI-Powered Company Name Extractor
Replaces scattered extraction logic across multiple files
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import json
import re
from app.ai.ai_service import AIServiceManager
from app.config import settings


class Confidence(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CompanyResult:
    """Structured company extraction result"""
    name: str                    # Clean company name
    confidence: Confidence       # Extraction confidence
    is_agency: bool             # Is recruitment agency
    normalized: str             # File-system safe name
    display_name: Optional[str] # Optional display name


class CompanyExtractor:
    """Single source of truth for company name extraction"""
    
    PROMPT = """Extract the company name from this job posting and return JSON.

EXAMPLE:
URL: https://www.seek.com.au/job/78901234
Text: "Senior Data Analyst - Ref: DA2024-456
Robert Half Technology is seeking a Senior Data Analyst for our client, a leading ASX-listed financial services company in Melbourne CBD. 

About the Role:
Our client, a major Australian bank, is looking for...

How to Apply:
By clicking 'apply', you give your express consent that Robert Half may use your personal information to process your job application...

Contact: applications@roberthalf.com.au
Robert Half International Inc. Privacy Policy applies."

ANALYSIS:
- URL shows: seek.com.au (job board, not employer)
- "Robert Half Technology" mentioned as recruiter
- "Ref: DA2024-456" → recruitment reference number
- "our client" → agency placing for someone else
- Privacy consent for "Robert Half" → confirms agency
- Real employer kept confidential ("leading ASX-listed financial services company")

JSON:
{
  "company": "Robert Half",
  "confidence": "high",
  "is_agency": true
}

RULES:
1. Recruitment agency posting → return AGENCY name (look for: reference numbers, "our client", "on behalf of", privacy consents, known agencies like Robert Half, Hays, Randstad, Seek Talent, Hudson, Michael Page)
2. Direct employer posting → return COMPANY name (look for: "About [Company]", company websites, direct contact emails, no reference numbers)
3. Parent company over divisions (Microsoft not Azure, Nine Entertainment not Drive, Google not Google Cloud)
4. Check: headers, "About" sections, email domains (@company.com), website URLs (www.company.com)
5. Avoid generic terms: "Company", "Client", "Organization", "Employer"

Now extract from:
URL: {url}
Text: {text}

JSON:"""

    def __init__(self, ai_service: AIServiceManager):
        """Initialize with AI service dependency"""
        self.ai_service = ai_service
    
    async def extract(self, jd_url: str, jd_text: str) -> CompanyResult:
        """
        Extract company name from job description
        
        Args:
            jd_url: Job description URL (can be empty string)
            jd_text: Job description text content
            
        Returns:
            CompanyResult with extraction details
        """
        try:
            # Call AI service
            response = await self.ai_service.generate_response(
                prompt=self.PROMPT.format(
                    url=jd_url[:500] if jd_url else "No URL provided",
                    text=jd_text[:4000]
                ),
                temperature=0.0,
                max_tokens=256
            )
            
            # Parse JSON response
            data = self._parse_ai_response(response)
            company = data.get("company", "Unknown").strip()
            conf = data.get("confidence", "low")
            is_agency = data.get("is_agency", False)
            
        except Exception as e:
            # Log error and use fallback
            print(f"AI extraction failed: {str(e)}")
            company = "Unknown"
            conf = "low"
            is_agency = False
        
        # Validate and clean
        company = self._validate_company_name(company)
        
        return CompanyResult(
            name=company,
            confidence=Confidence[conf.upper()],
            is_agency=is_agency,
            normalized=self._normalize(company),
            display_name=company
        )
    
    def _parse_ai_response(self, response: str) -> dict:
        """Parse AI JSON response"""
        try:
            # Find JSON in response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            
            # If no JSON found, return default
            return {"company": "Unknown", "confidence": "low", "is_agency": False}
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {str(e)}")
            return {"company": "Unknown", "confidence": "low", "is_agency": False}
    
    def _validate_company_name(self, name: str) -> str:
        """Validate and clean company name"""
        # Check for invalid names
        invalid_names = [
            "unknown", "company", "organization", "client", "employer", "", "n/a",
            "superannuation", "leave", "loading", "benefits", "salary", "wage", 
            "compensation", "package", "remuneration", "bonus", "incentive", 
            "allowance", "entitlement", "plus", "including", "with", "and", "or"
        ]
        
        name_lower = name.lower().strip()
        
        # Check for invalid names
        if name_lower in invalid_names:
            return "Unknown"
        
        # Check for benefits/compensation phrases
        benefits_terms = ['superannuation', 'leave', 'loading', 'benefits', 'salary', 'package', 'compensation']
        if any(term in name_lower for term in benefits_terms):
            return "Unknown"
        
        # Check for too many words (likely not a company name)
        if len(name.split()) > 8:
            return "Unknown"
        
        # Check for too many spaces
        if name.count(' ') > 6:
            return "Unknown"
        
        # Check for no letters
        if not any(c.isalpha() for c in name):
            return "Unknown"
        
        # Minimum length check
        if len(name.strip()) < 2:
            return "Unknown"
        
        return name.strip()
    
    def _normalize(self, name: str) -> str:
        """Convert to file-system safe name"""
        # Keep only alphanumeric, spaces, hyphens
        safe = ''.join(c for c in name if c.isalnum() or c in ' -')
        
        # Replace spaces with underscores
        safe = safe.replace(' ', '_').strip('_')
        
        # Remove multiple underscores
        while '__' in safe:
            safe = safe.replace('__', '_')
        
        # Truncate at word boundary if too long
        if len(safe) > 50:
            parts = safe[:50].rsplit('_', 1)
            safe = parts[0] if parts[0] else safe[:50]
        
        return safe if safe else "Unknown_Company"
    
    def match_existing(
        self, 
        result: CompanyResult, 
        existing: List[str]
    ) -> Optional[str]:
        """
        Match against existing company folders
        
        Args:
            result: Extraction result
            existing: List of existing company folder names
            
        Returns:
            Matched folder name or None
        """
        normalized = result.normalized.lower()
        
        # Exact match
        for folder in existing:
            if folder.lower() == normalized:
                return folder
        
        # Fuzzy match (substring)
        for folder in existing:
            folder_lower = folder.lower()
            if normalized in folder_lower or folder_lower in normalized:
                if len(folder) >= len(result.normalized) * 0.7:
                    return folder
        
        return None
