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
    
    # Universal Company Name Extraction Prompt - Production Ready
    # Works for any country, any company type, any JD format
    PROMPT = """You are an expert at extracting company names from job descriptions worldwide. Your task is to identify the ACTUAL HIRING COMPANY with 100% accuracy.

═══════════════════════════════════════════════════════════════════════
CRITICAL RULES - FOLLOW THESE ABSOLUTELY
═══════════════════════════════════════════════════════════════════════

1. EXTRACT THE HIRING ORGANIZATION - NOT:
   ❌ Job boards (LinkedIn, Indeed, SEEK, Glassdoor, etc.)
   ❌ Recruitment agencies (unless they ARE the employer)
   ❌ Locations/cities/states/countries alone
   ❌ Job titles or position names
   ❌ Department names alone
   ❌ Benefits or perks
   ❌ Industry sectors

2. INCLUDE STATE/REGION SUFFIX IF IT'S PART OF THE OFFICIAL NAME:
   ✓ "Transport for NSW" (not just "NSW")
   ✓ "Energy and Water Ombudsman NSW" (not just "NSW")
   ✓ "Government of Western Australia" (not just "Western Australia")
   ✓ "Département du Val-d'Oise" (not just "Val-d'Oise")
   ✓ "State of California Department of Education" (full name)

3. RECOGNIZE ORGANIZATIONAL PATTERNS GLOBALLY:
   - Government: "[Agency Name] + [Region/State]"
   - Corporations: "[Brand/Company Name] [Legal Entity]"
   - NGOs: "[Organization Name] + [Region]" or "[Full Legal Name]"
   - Educational: "[Institution Name] [Type]"
   - Healthcare: "[Hospital/Clinic Name] [Location]"

4. NEVER EXTRACT ONLY:
   - State abbreviations (NSW, CA, TX, VIC, QLD, etc.)
   - Country names alone (USA, UK, Australia, etc.)
   - City names alone (Sydney, London, Paris, etc.)
   - Generic terms (Government, Hospital, University, etc.)

═══════════════════════════════════════════════════════════════════════
EXTRACTION STRATEGY - FOLLOW THIS PROCESS
═══════════════════════════════════════════════════════════════════════

STEP 1: LOCATE THE COMPANY REFERENCE
Look in these sections (in order of priority):
a) Header/Title area (first 500 characters)
b) "About [Company]" or "About Us" sections
c) "Who We Are" or "Our Company" sections
d) Footer/Contact information
e) Email domains (e.g., jobs@company.com → "company")

STEP 2: IDENTIFY THE PATTERN
Determine the structure:
- [Job Title] at [Company] [Location]
- [Company] is seeking a [Job Title]
- Join [Company] as a [Job Title]
- [Department] at [Company]
- [Company] - [Job Title]

STEP 3: EXTRACT COMPLETE NAME
Rules for completeness:
- If government/public sector: Include department + jurisdiction
  Example: "Department of Education Victoria" NOT just "Victoria"
  
- If corporate: Include full legal entity if present
  Example: "Accenture Australia Pty Ltd" NOT just "Accenture"
  
- If regional organization: Include region as part of name
  Example: "Red Cross Queensland" NOT just "Red Cross"
  
- If subsidiary: Include parent if mentioned together
  Example: "Google Cloud Australia" NOT just "Google"

STEP 4: VALIDATE YOUR EXTRACTION
Ask yourself:
□ Is this a complete organization name? (Not just a fragment?)
□ Can this entity legally hire employees? (Not just a location?)
□ Would someone searching for this company find them with this name?
□ Does this make sense as an employer in context?
□ Is this specific enough? (Not too generic?)

STEP 5: DETERMINE CONFIDENCE
- HIGH: Company name explicitly stated, clear and unambiguous
- MEDIUM: Company name inferred from context, reasonable certainty
- LOW: Multiple possible interpretations, unclear hiring entity

═══════════════════════════════════════════════════════════════════════
REAL-WORLD EXAMPLES - LEARN FROM THESE
═══════════════════════════════════════════════════════════════════════

EXAMPLE 1 - Government Agency (Australia)
Text: "Data Analyst Energy and Water Ombudsman NSW 2 days left to apply..."
Analysis:
- Job Title: "Data Analyst"
- Organization: "Energy and Water Ombudsman NSW"
- Location suffix: "NSW" is PART of the official name
✓ CORRECT: {{"company": "Energy and Water Ombudsman NSW", "confidence": "high", "is_agency": false}}
✗ WRONG: {{"company": "NSW"}} ← This is just a state!

EXAMPLE 2 - Government Department (USA)
Text: "Software Engineer - California Department of Transportation - Sacramento, CA"
Analysis:
- Job Title: "Software Engineer"
- Organization: "California Department of Transportation"
- Location: "Sacramento, CA" is work location, not part of name
✓ CORRECT: {{"company": "California Department of Transportation", "confidence": "high", "is_agency": false}}
✗ WRONG: {{"company": "California"}} ← Too generic!

EXAMPLE 3 - International Corporation
Text: "Senior Analyst at Deloitte Touche Tohmatsu Limited (Australia)"
Analysis:
- Organization: "Deloitte Touche Tohmatsu Limited"
- Region: "(Australia)" indicates regional office
✓ CORRECT: {{"company": "Deloitte Australia", "confidence": "high", "is_agency": false}}

EXAMPLE 4 - Healthcare (UK)
Text: "Nurse Practitioner | NHS Greater Glasgow and Clyde | Glasgow"
Analysis:
- Organization: "NHS Greater Glasgow and Clyde"
- Location: "Glasgow" is city, not part of official name
✓ CORRECT: {{"company": "NHS Greater Glasgow and Clyde", "confidence": "high", "is_agency": false}}
✗ WRONG: {{"company": "NHS"}} ← Too generic!

EXAMPLE 5 - University (Global)
Text: "Research Fellow - University of Tokyo Department of Physics"
Analysis:
- Primary employer: "University of Tokyo"
- Department: "Department of Physics" is subdivision
✓ CORRECT: {{"company": "University of Tokyo", "confidence": "high", "is_agency": false}}

EXAMPLE 6 - Recruitment Agency Posted (Tricky!)
Text: "Posted by Hays Recruitment on behalf of a leading financial services company..."
Analysis:
- Poster: "Hays Recruitment" (agent)
- Actual employer: "leading financial services company" (confidential)
✓ CORRECT: {{"company": "Hays Recruitment", "confidence": "medium", "is_agency": true}}

EXAMPLE 7 - Small Business (Any Country)
Text: "Join our family-owned bakery 'Sunshine Breads' in downtown..."
Analysis:
- Organization: "Sunshine Breads"
- Type: Small business
✓ CORRECT: {{"company": "Sunshine Breads", "confidence": "high", "is_agency": false}}

EXAMPLE 8 - Multinational with Country Suffix
Text: "Amazon Web Services (AWS) Japan is hiring..."
Analysis:
- Parent: "Amazon Web Services"
- Regional entity: "Japan"
✓ CORRECT: {{"company": "Amazon Web Services Japan", "confidence": "high", "is_agency": false}}

═══════════════════════════════════════════════════════════════════════
SPECIAL CASES - HANDLE THESE CORRECTLY
═══════════════════════════════════════════════════════════════════════

CASE 1: Confidential/Unnamed Employer
If the company is deliberately not named:
- Look for: "confidential", "leading company", "our client"
- Response: {{"company": "Confidential Client", "confidence": "low", "is_agency": false}}

CASE 2: Multiple Entities Mentioned
If multiple organizations are mentioned:
- Priority 1: "We are looking for..." (the "we" is the employer)
- Priority 2: "Join [Company]..." (direct statement)
- Priority 3: Context clues about who's hiring

CASE 3: Parent Company vs Subsidiary
If both mentioned:
- Use the most specific entity doing the hiring
- Example: "Google Cloud Australia" not just "Google"

CASE 4: Abbreviations and Full Names
If both appear:
- Prefer full name: "International Business Machines" over "IBM"
- Unless full name is never stated, then use abbreviation

CASE 5: Non-English Names
Preserve original:
- "Société Générale" not "General Society"
- "Deutsche Bank" not "German Bank"
- Keep accents, special characters, proper spelling

CASE 6: Merged/Partnership Organizations
Include all partners if that's the official name:
- "Ernst & Young" ✓
- "PricewaterhouseCoopers" ✓
- "Kellogg Brown & Root" ✓

═══════════════════════════════════════════════════════════════════════
YOUR RESPONSE FORMAT
═══════════════════════════════════════════════════════════════════════

Return ONLY valid JSON in this exact format:

{{
  "company": "Complete Company Name Here",
  "confidence": "high|medium|low",
  "reasoning": "Brief explanation of why you extracted this name",
  "is_agency": true|false
}}

Rules for the response:
1. "company" must be a string, never empty, never just a location
2. "confidence" must be exactly: "high", "medium", or "low"
3. "reasoning" should be 1-2 sentences explaining your decision
4. "is_agency" should be true if this is a recruitment/staffing agency doing the posting

═══════════════════════════════════════════════════════════════════════
FINAL VALIDATION CHECKLIST
═══════════════════════════════════════════════════════════════════════

Before you submit your answer, verify:

✓ Is the name more than 2-3 characters? (Not just "UK", "NSW", "CA")
✓ Is it a legal entity that can employ people? (Not just a location)
✓ Is it the HIRING organization? (Not the job board, not just a recruiter)
✓ Is it complete? (Not missing key parts like state/region if official)
✓ Would someone searching for this company find them?
✓ Does the name make sense in the context of the job?
✓ Have you included official suffixes/prefixes that are part of the name?

═══════════════════════════════════════════════════════════════════════

Now extract the company name from this job description:

JOB URL: {url}

JOB DESCRIPTION:
{text}

Remember: Extract the ACTUAL HIRING ORGANIZATION with its COMPLETE OFFICIAL NAME. Be thorough, be accurate, be bold.
"""

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
            
            # Call AI service with increased context window for better extraction
            response = await self.ai_service.generate_response(
                prompt=self.PROMPT.format(
                    url=jd_url[:500] if jd_url else "No URL provided",
                    text=jd_text[:8000]  # Increased from 4000 to capture more context
                ),
                user=user,
                temperature=0.0,
                max_tokens=512  # Increased from 256 to accommodate reasoning field
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
    
    def _parse_ai_response(self, response) -> dict:
        """Parse AI JSON response with backward compatibility"""
        try:
            # Handle both string and AIResponse objects
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            # Find JSON in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                
                # New format includes "reasoning" field, old format doesn't
                # Both are valid - we just extract what we need
                # Log reasoning if present for debugging
                if "reasoning" in data:
                    print(f"🧠 AI reasoning: {data['reasoning']}")
                
                return data
            
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
        
        # CRITICAL: Check if result is ONLY a state/territory abbreviation
        # This catches the "NSW" bug directly
        state_abbreviations = [
            'nsw', 'vic', 'qld', 'sa', 'wa', 'tas', 'nt', 'act',  # Australia
            'ca', 'tx', 'ny', 'fl', 'il', 'pa', 'oh', 'ga', 'nc', 'mi',  # USA (common)
            'on', 'bc', 'qc', 'ab', 'mb', 'sk', 'ns', 'nb',  # Canada
            'uk', 'usa', 'au', 'nz', 'sg'  # Countries often misidentified as companies
        ]
        
        if name_lower in state_abbreviations:
            print(f"⚠️ Rejected: '{name}' is just a location abbreviation, not a company")
            return "Unknown"
        
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
                print(f"🔍 Detected job board: {domain}, extracting from text...")
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
            
            # Look for common patterns in text - ordered by priority
            patterns = [
                # Direct company name after job title (most common pattern)
                r'^[A-Z][a-zA-Z\s-]+\s*\n\s*([A-Z][a-zA-Z\s&().-]{10,80}?)\s*\n',
                # Company name in job summary section
                r'Job Summary\s*\n\s*([A-Z][a-zA-Z\s&().-]{10,80}?)\s*\n',
                # Organization patterns with specific context
                r'([A-Z][a-zA-Z\s&().-]{10,80}?)\s+works\s+in\s+partnership',
                r'([A-Z][a-zA-Z\s&().-]{10,80}?)\s+plays\s+a\s+critical\s+role',
                # About company patterns
                r'About\s+([A-Z][a-zA-Z\s&().-]{10,80}?)\s+is',
                r'([A-Z][a-zA-Z\s&().-]{10,80}?)\s+is\s+(?:looking|seeking|hiring)',
                # Direct company labels
                r'Company:\s*([^\n\r]+)',
                r'Employer:\s*([^\n\r]+)',
                # Email domains
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
            "work", "job", "position", "role", "applications", "close", "posted",
            "opportunity", "home", "remote", "flexible", "arrangements", "culture",
            "environment", "supportive", "friendly", "progression", "development",
            "learning", "discounts", "insurance", "career", "attractive", "base"
        ]
        
        if any(term in name_lower for term in invalid_terms):
            return False
        
        # Check for too many words
        if len(name.split()) > 8:
            return False
        
        return True
