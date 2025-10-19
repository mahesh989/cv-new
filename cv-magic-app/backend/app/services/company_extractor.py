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
    
    PROMPT = """Extract the company name from this job posting. Return ONLY a JSON object.

SIMPLE RULES:
1. Look for the ACTUAL company name (not job boards like Seek, Indeed)
2. If it's a recruitment agency posting → return the AGENCY name
3. If it's a direct company posting → return the COMPANY name
4. NEVER extract benefits like "superannuation", "leave loading", "salary package"
5. If no company found → return null

EXAMPLES:

Recruitment Agency:
Text: "Robert Half is seeking a Data Analyst for our client..."
JSON: {{"company": "Robert Half", "confidence": "high", "is_agency": true}}

Direct Company:
Text: "Microsoft is looking for a Software Engineer..."
JSON: {{"company": "Microsoft", "confidence": "high", "is_agency": false}}

Benefits Text (NOT a company):
Text: "Salary plus superannuation and leave loading..."
JSON: {{"company": null, "confidence": "low", "is_agency": false}}

EXTRACT FROM:
URL: {url}
Text: {text}

JSON:"""

    def __init__(self, ai_service: AIServiceManager):
        """Initialize with AI service dependency"""
        self.ai_service = ai_service
    
    async def extract(self, jd_url: str, jd_text: str, user: Any = None) -> CompanyResult:
        """
        Extract company name from job description
        
        Args:
            jd_url: Job description URL (can be empty string)
            jd_text: Job description text content
            user: User context for AI service initialization
            
        Returns:
            CompanyResult with extraction details
        """
        try:
            # Initialize AI service for user if needed
            if hasattr(self.ai_service, 'initialize_for_user') and user:
                self.ai_service.initialize_for_user(user)
            
            # Call AI service
            response = await self.ai_service.generate_response(
                prompt=self.PROMPT.format(
                    url=jd_url[:500] if jd_url else "No URL provided",
                    text=jd_text[:4000]
                ),
                user=user,
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
            print("🔄 Falling back to URL-based extraction...")
            
            # Use URL-based fallback
            fallback_result = self._url_based_fallback(jd_url, jd_text)
            company = fallback_result.get("company", "Unknown")
            conf = fallback_result.get("confidence", "low")
            is_agency = fallback_result.get("is_agency", False)
        
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
    
    def _url_based_fallback(self, jd_url: str, jd_text: str) -> dict:
        """
        URL-based fallback when AI extraction fails
        Extract company name from URL patterns
        """
        try:
            if not jd_url or not jd_url.startswith("http"):
                return {"company": "Unknown", "confidence": "low", "is_agency": False}
            
            from urllib.parse import urlparse
            parsed_url = urlparse(jd_url)
            domain = parsed_url.netloc.lower()
            
            # Remove www. prefix
            if domain.startswith("www."):
                domain = domain[4:]
            
            # Known job boards (extract from text instead)
            job_boards = [
                "seek.com.au", "indeed.com", "linkedin.com", "glassdoor.com",
                "ziprecruiter.com", "monster.com", "careerbuilder.com",
                "ethicaljobs.com.au", "jora.com.au", "adzuna.com.au"
            ]
            
            if any(board in domain for board in job_boards):
                # For job boards, try to extract from text
                return self._extract_from_text_fallback(jd_text)
            
            # Extract company from domain
            # careers.company.com → company
            # company.com/careers → company
            # jobs.company.com → company
            
            # Remove common subdomains
            subdomains_to_remove = ["careers", "jobs", "work", "employment", "hr", "talent"]
            domain_parts = domain.split(".")
            
            if len(domain_parts) >= 2:
                # Check if first part is a subdomain to remove
                if domain_parts[0] in subdomains_to_remove:
                    company_domain = ".".join(domain_parts[1:])
                else:
                    company_domain = domain
                
                # Extract company name from domain
                company_name = company_domain.split(".")[0]
                
                # Clean up the name
                company_name = company_name.replace("-", " ").replace("_", " ")
                company_name = " ".join(word.capitalize() for word in company_name.split())
                
                # Check if it's a valid company name
                if len(company_name) >= 2 and len(company_name) < 50:
                    return {
                        "company": company_name,
                        "confidence": "medium",
                        "is_agency": False
                    }
            
            # If URL extraction fails, try text extraction
            return self._extract_from_text_fallback(jd_text)
            
        except Exception as e:
            print(f"URL-based fallback failed: {str(e)}")
            return {"company": "Unknown", "confidence": "low", "is_agency": False}
    
    def _extract_from_text_fallback(self, jd_text: str) -> dict:
        """
        Simple text-based fallback extraction
        """
        try:
            import re
            
            # Look for common patterns in text
            patterns = [
                r'About\s+([A-Z][a-zA-Z\s&.-]{2,30}?)\s+is',
                r'([A-Z][a-zA-Z\s&.-]{2,30}?)\s+is\s+(?:looking|seeking|hiring)',
                r'Company:\s*([^\n\r]+)',
                r'Employer:\s*([^\n\r]+)',
                r'@([a-zA-Z0-9.-]+)\.(?:com|org|au|net)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, jd_text, re.IGNORECASE)
                if match:
                    company_name = match.group(1).strip()
                    
                    # Validate the extracted name
                    if self._is_valid_company_name(company_name):
                        return {
                            "company": company_name,
                            "confidence": "low",
                            "is_agency": False
                        }
            
            return {"company": "Unknown", "confidence": "low", "is_agency": False}
            
        except Exception as e:
            print(f"Text-based fallback failed: {str(e)}")
            return {"company": "Unknown", "confidence": "low", "is_agency": False}
    
    def _is_valid_company_name(self, name: str) -> bool:
        """Check if extracted name is a valid company name"""
        if not name or len(name.strip()) < 2:
            return False
        
        name_lower = name.lower().strip()
        
        # Check for invalid terms
        invalid_terms = [
            "superannuation", "leave", "loading", "benefits", "salary", "package",
            "compensation", "remuneration", "bonus", "incentive", "allowance",
            "work", "job", "position", "role", "applications", "close", "posted"
        ]
        
        if any(term in name_lower for term in invalid_terms):
            return False
        
        # Check for too many words
        if len(name.split()) > 8:
            return False
        
        return True
