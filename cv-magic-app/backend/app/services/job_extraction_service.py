import os
import json
import re
import httpx
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from app.utils.timestamp_utils import TimestampUtils

logger = logging.getLogger(__name__)

class JobExtractionService:
    """Service for extracting job information and saving to organized folders"""
    
    def __init__(self):
        self.cv_analysis_dir = Path("cv-analysis")
        self.prompt_file = Path("prompt/job_extraction_prompt.txt")
    
    def _load_prompt(self) -> str:
        """Load the job extraction prompt from file"""
        try:
            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback prompt if file not found
            return self._get_fallback_prompt()
    
    def _get_fallback_prompt(self) -> str:
        """Fallback prompt if file is not found"""
        return """EXTRACT JOB INFORMATION FROM THE FOLLOWING TEXT AND RETURN ONLY VALID JSON.

CRITICAL INSTRUCTIONS:
1. Return ONLY a valid JSON object without any additional text, explanations, or markdown formatting
2. Do NOT wrap the JSON in code blocks (no ```json ```)
3. Start with {{ and end with }}
4. Use double quotes for all keys and string values
5. If information is not available, use null

REQUIRED JSON FORMAT:
{{
  "company_name": "string or null",
  "job_title": "string or null", 
  "location": "string or null",
  "experience_required": "string or null",
  "seniority_level": "string or null",
  "industry": "string or null",
  "phone_number": "string or null",
  "email": "string or null",
  "website": "string or null",
  "work_type": "string or null"
}}

IMPORTANT: YOUR RESPONSE MUST BE PARSABLE BY json.loads() WITHOUT ANY MODIFICATION.

TEXT TO ANALYZE:
{job_description}"""
    
    
    def _create_company_slug(self, company_name: str) -> str:
        """Create a safe company slug for folder names"""
        if not company_name or company_name.lower() in ['unknown', 'null', '']:
            return f"Unknown_Company_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Remove special characters except alphanumeric, spaces, &, ., -
        company_slug = re.sub(r'[^\w\s&.-]', '', company_name)
        # Replace spaces with underscores
        company_slug = re.sub(r'\s+', '_', company_slug)
        # Remove leading/trailing underscores
        company_slug = company_slug.strip('_')
        # Truncate if too long (max 50 characters)
        if len(company_slug) > 50:
            company_slug = company_slug[:50]
        
        return company_slug
    
    async def extract_job_information(self, job_description: str, auth_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract job information using the selected AI model with comprehensive error handling
        
        Args:
            job_description: The job description text
            auth_token: Optional authentication token for AI API calls
            
        Returns:
            Dictionary containing extracted job information
        """
        if not job_description or len(job_description.strip()) < 10:
            return {"error": "Job description too short or empty"}
        
        # Step 1: Try AI extraction if auth token is provided
        if auth_token:
            print(f"🔍 Starting AI extraction with token: {auth_token[:20]}...")
            try:
                ai_result = await self._try_ai_extraction(job_description, auth_token)
                print(f"🔍 AI extraction result: {ai_result}")
                if ai_result and "error" not in ai_result:
                    print(f"✅ AI extraction successful: {ai_result.get('company_name', 'Unknown')}")
                    return ai_result
                else:
                    print(f"⚠️ AI extraction failed: {ai_result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"⚠️ AI extraction exception: {str(e)}")
                print(f"⚠️ Exception details: {repr(e)}")
        else:
            print(f"⚠️ No auth token provided, skipping AI extraction")
        
        # Step 2: Fallback to rule-based extraction
        print("⚠️ Using rule-based extraction as fallback")
        try:
            return self._extract_with_rules(job_description)
        except Exception as e:
            print(f"Rule-based extraction failed: {str(e)}")
            # Step 3: Return minimal default if everything fails
            return self._get_default_job_info()
    
    async def _try_ai_extraction(self, job_description: str, auth_token: str) -> Dict[str, Any]:
        """Attempt AI extraction using centralized AI service"""
        try:
            # Load prompt template
            prompt_template = self._load_prompt()
            # Use safe string replacement to avoid format issues with braces
            prompt = prompt_template.replace('{job_description}', job_description[:3000])
            
            # Use enhanced AI service with API key validation
            from app.services.enhanced_ai_service import enhanced_ai_service
            
            try:
                ai_response = await enhanced_ai_service.generate_response_with_validation(
                    prompt=prompt,
                    system_prompt="You are a precise job information extractor. CRITICAL: Return ONLY a valid JSON object that starts with { and ends with }. Do NOT wrap in code blocks. Do NOT add any text before or after the JSON. Use double quotes for all keys. If information is not available, use null. Your response must be parsable by json.loads() without modification.",
                    temperature=0.0,
                    max_tokens=1000
                )
                
                response_text = ai_response.content
                
                if not response_text.strip():
                    return {"error": "AI returned empty response"}
                
                # Debug logging
                logger.debug("AI response length: %s", len(response_text))
                logger.debug("Response type: %s", type(response_text))
                logger.debug("Response preview: %s", str(response_text)[:200] + "...")
                print(f"🤖 AI raw response (first 100 chars): '{response_text[:100]}'")
                print(f"🤖 AI raw response (last 50 chars): '{response_text[-50:]}'")
                print(f"🤖 Response length: {len(response_text)} characters")
                print(f"🤖 Starts with: '{response_text[:10]}'")
                
                # Parse the AI response as JSON
                job_info = self._parse_ai_response(response_text)
                if job_info and self._validate_ai_response(job_info):
                    validated_info = self._validate_job_info(job_info)
                    print(f"✅ Successfully extracted and validated job info: {validated_info.get('company_name', 'Unknown')}")
                    return validated_info
                else:
                    print(f"❌ AI response failed validation")
                    return {"error": "AI response failed validation"}
                
            except Exception as ai_error:
                logger.error(f"AI service error: {ai_error}")
                return {"error": f"AI service failed: {str(ai_error)}"}
                
        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            return {"error": f"AI extraction failed: {str(e)}"}
    
    def _get_default_job_info(self) -> Dict[str, Any]:
        """Return default job info when all extraction methods fail"""
        return {
            "company_name": "Unknown_Company",
            "job_title": "Unknown_Position",
            "location": "Unknown_Location",
            "experience_required": "Not specified",
            "seniority_level": "Unknown",
            "industry": "Unknown",
            "phone_number": None,
            "email": None,
            "website": None,
            "work_type": None
        }
    
    
    def _fix_json_issues(self, json_string: str) -> str:
        """
        Fix common JSON formatting issues from AI responses.
        Handles cases where JSON might be missing braces, have malformed keys, etc.
        """
        if not json_string or not isinstance(json_string, str):
            return "{}"
        
        # Clean the string first
        cleaned = json_string.strip()
        
        logger.debug("Original AI response: %s", cleaned[:200] + "...")
        
        # Case 1: If it starts with a quoted key without opening brace (your specific error)
        if cleaned.startswith('"') and not cleaned.startswith('{'):
            logger.debug("Fixing JSON: missing opening brace")
            # Check if it has a closing brace at the end
            if not cleaned.endswith('}'):
                cleaned = '{' + cleaned + '}'
            else:
                cleaned = '{' + cleaned
        
        # Case 2: If it's missing both braces but has key-value pairs
        elif not cleaned.startswith('{') and not cleaned.endswith('}'):
            if ':' in cleaned and ('"' in cleaned or "'" in cleaned):
                logger.debug("Fixing JSON: missing both braces")
                cleaned = '{' + cleaned + '}'
        
        # Case 3: Handle newlines/whitespace before keys (common with GPT models)
        if '\n' in cleaned and any(line.strip().startswith('"') for line in cleaned.split('\n') if line.strip()):
            logger.debug("Fixing JSON: newline formatting issues")
            # Remove excessive whitespace but maintain structure
            lines = []
            for line in cleaned.split('\n'):
                stripped = line.strip()
                if stripped:  # Only keep non-empty lines
                    lines.append(stripped)
            cleaned = ' '.join(lines)  # Join as single line
        
        # Case 4: Handle markdown code blocks
        if '```json' in cleaned:
            logger.debug("Extracting JSON from markdown code block")
            start_idx = cleaned.find('```json') + 7
            end_idx = cleaned.find('```', start_idx)
            if end_idx != -1:
                cleaned = cleaned[start_idx:end_idx].strip()
        elif '```' in cleaned:
            logger.debug("Extracting JSON from generic code block")
            start_idx = cleaned.find('```') + 3
            end_idx = cleaned.find('```', start_idx)
            if end_idx != -1:
                cleaned = cleaned[start_idx:end_idx].strip()
        
        # Final validation and cleanup
        if not cleaned.startswith('{'):
            logger.debug("Adding missing opening brace")
            cleaned = '{' + cleaned
        if not cleaned.endswith('}'):
            logger.debug("Adding missing closing brace")
            cleaned += '}'
        
        logger.debug("Fixed JSON: %s", cleaned[:200] + "...")
        return cleaned
    
    def _extract_key_values(self, response: str) -> Dict[str, Any]:
        """Extract key-value pairs as last resort"""
        result = self._get_default_job_info()
        
        # Look for key-value patterns
        patterns = [
            r'"(company_name|job_title|location|experience_required|seniority_level|industry|phone_number|email|website|work_type)"\s*:\s*"([^"]+)"',
            r'"(company_name|job_title|location|experience_required|seniority_level|industry|phone_number|email|website|work_type)"\s*:\s*([^,}\n]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for key, value in matches:
                value = value.strip().strip('"').strip("'")
                if value and value.lower() not in ['null', 'none', 'unknown']:
                    result[key] = value
        
        return result
    
    def _validate_ai_response(self, data: Dict[str, Any]) -> bool:
        """Validate that the AI response contains expected job information."""
        if not isinstance(data, dict):
            return False
        
        # Check for at least one of these key fields
        required_fields = ['company_name', 'job_title', 'location', 'experience_required']
        has_required_field = any(field in data and data[field] and str(data[field]).strip() for field in required_fields)
        
        if not has_required_field:
            print(f"⚠️ AI response missing required fields: {list(data.keys())}")
            return False
        
        # Validate field types
        for field in ['company_name', 'job_title', 'location', 'experience_required', 'seniority_level', 'industry']:
            if field in data and data[field] is not None and not isinstance(data[field], str):
                print(f"⚠️ Field '{field}' has invalid type: {type(data[field])}")
                return False
        
        return True
    
    def _parse_ai_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse AI response with multiple fallback strategies."""
        if not response:
            return None
        
        logger.debug("_parse_ai_response called with: %s", repr(response[:100]) + "...")
        logger.debug("Response length: %s", len(response))
        
        parsing_attempts = [
            self._attempt_direct_json_parse,
            self._attempt_fixed_json_parse,
            self._attempt_regex_json_extraction,
            self._attempt_manual_json_reconstruction
        ]
        
        for attempt in parsing_attempts:
            try:
                result = attempt(response)
                if result and self._validate_ai_response(result):
                    logger.debug("Parsing successful with %s", attempt.__name__)
                    return result
            except (json.JSONDecodeError, ValueError) as e:
                logger.debug("%s failed: %s", attempt.__name__, str(e))
                continue
        
        logger.warning("All JSON parsing attempts failed")
        print(f"❌ Could not parse AI response with any method")
        print(f"❌ Full response: {repr(response)}")
        return None
    
    def _attempt_direct_json_parse(self, response: str) -> Optional[Dict[str, Any]]:
        """Attempt direct JSON parsing."""
        logger.debug("Attempting direct JSON parsing")
        result = json.loads(response.strip())
        logger.debug("Direct JSON parsing successful")
        return result
    
    def _attempt_fixed_json_parse(self, response: str) -> Optional[Dict[str, Any]]:
        """Attempt parsing after fixing common issues."""
        logger.debug("Attempting fixed JSON parsing")
        fixed = self._fix_json_issues(response)
        result = json.loads(fixed)
        logger.debug("Fixed JSON parsing successful")
        return result
    
    def _attempt_regex_json_extraction(self, response: str) -> Optional[Dict[str, Any]]:
        """Attempt to extract JSON using regex patterns."""
        logger.debug("Attempting regex JSON extraction")
        json_patterns = [
            r'\{.*\}',  # Basic JSON object
            r'```json\s*(\{.*\})\s*```',  # Markdown JSON code block
            r'```\s*(\{.*\})\s*```',  # Generic code block
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1) if match.groups() else match.group(0)
                    result = json.loads(json_str.strip())
                    logger.debug("Regex JSON extraction successful")
                    return result
                except json.JSONDecodeError:
                    continue
        return None
    
    def _attempt_manual_json_reconstruction(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to manually reconstruct JSON from malformed key-value pairs.
        Handles cases like: "key": "value" without braces.
        """
        logger.debug("Attempting manual JSON reconstruction")
        lines = response.strip().split('\n')
        json_lines = []
        
        for line in lines:
            line = line.strip()
            if line and ':' in line and line.count('"') >= 2:
                # This looks like a key-value pair
                json_lines.append(line)
        
        if json_lines:
            try:
                # Reconstruct as proper JSON
                reconstructed = '{' + ', '.join(json_lines) + '}'
                result = json.loads(reconstructed)
                logger.debug("Manual JSON reconstruction successful")
                return result
            except json.JSONDecodeError:
                pass
        
        return None
    
    
    def _validate_job_info(self, job_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted job information"""
        # Ensure all required keys exist
        required_keys = [
            "company_name", "job_title", "location", "experience_required",
            "seniority_level", "industry", "phone_number", "email", 
            "website", "work_type"
        ]
        
        for key in required_keys:
            if key not in job_info:
                job_info[key] = None
        
        # Clean and validate company name
        if not job_info.get("company_name") or job_info["company_name"].lower() in ['unknown', 'null', '']:
            job_info["company_name"] = "Unknown_Company"
        
        # Clean and validate other fields
        for key in ["job_title", "location", "experience_required", "seniority_level", "industry"]:
            if not job_info.get(key) or job_info[key].lower() in ['unknown', 'null', '']:
                job_info[key] = "Unknown"
        
        # Clean contact information
        for key in ["phone_number", "email", "website", "work_type"]:
            if not job_info.get(key) or job_info[key].lower() in ['unknown', 'null', '']:
                job_info[key] = None
        
        return job_info
    
    def _extract_with_rules(self, job_description: str) -> Dict[str, Any]:
        """Extract job information using rule-based patterns when AI is not available"""
        # Initialize with defaults
        job_info = {
            "company_name": "Unknown_Company",
            "job_title": "Unknown",
            "location": "Unknown",
            "experience_required": "Unknown",
            "seniority_level": "Unknown",
            "industry": "Unknown",
            "phone_number": None,
            "email": None,
            "website": None,
            "work_type": None
        }
        
        # Company name extraction patterns (improved)
        company_patterns = [
            # Company heritage/establishment patterns
            r'For\s+over\s+\d+\s+years,\s+([A-Z][a-zA-Z\s&.-]+?)\s+has\s+been',
            r'In\s+\d+,\s+([A-Z][a-zA-Z\s&.-]+?)\s+combined\s+with',
            
            # Brand/division patterns (prioritize parent company)
            r'Drive\s+is\s+([A-Z][a-zA-Z\s&.-]+?)\'s\s+brand',
            r'([A-Z][a-zA-Z\s&.-]+?)\s+Entertainment',
            r'wholly\s+owned\s+by\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s+with|\s+is|\s+offers|$)',
            r'Australia\'s\s+largest\s+media\s+organisation,\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s+with|\s+is|\s+offers|$)',
            
            # About us/company patterns
            r'About\s+us\s+([A-Z][a-zA-Z\s&.-]+?)\s+is',
            r'About\s+the\s+company\s+([A-Z][a-zA-Z\s&.-]+?)\s+is',
            r'([A-Z][a-zA-Z\s&.-]+?)\s+Job\s+Summary\s+\1',
            r'([A-Z][a-zA-Z\s&.-]+?)\s+Applications\s+close.*?\1',
            r'(?:^|\n)\s*([A-Z][a-zA-Z\s&.-]+?)\s+Job\s+Summary',
            r'(?:^|\n)\s*([A-Z][a-zA-Z\s&.-]+?)\s+Applications\s+close',
            r'(?:^|\n)\s*[A-Z][a-zA-Z\s]*\s+at\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s|,|\.|$)',
            r'(?:^|\n)\s*[A-Z][a-zA-Z\s]*\s+with\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s|,|\.|$)',
            r'(?:^|\n)\s*[A-Z][a-zA-Z\s]*\s+for\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s|,|\.|$)',
            r'@([a-zA-Z0-9.-]+)\.(?:com|org|au|net)',
            r'https?://(?:www\.)?([a-zA-Z0-9.-]+)\.(?:com|org|au|net)',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                company_name = match.group(1).strip()
                # Filter out invalid company names (allow short names like GfK, NIQ)
                if (len(company_name) >= 2 and len(company_name) < 50 and 
                    not company_name.lower() in ['work', 'job', 'position', 'role', 'applications', 'close', 'posted', 'summary']):
                    job_info["company_name"] = company_name
                    break
        
        # Job title extraction patterns
        title_patterns = [
            r'(Senior|Junior|Lead|Principal|Staff)?\s*(Software Engineer|Data Analyst|Developer|Manager|Analyst|Designer|Consultant|Specialist)',
            r'Position:\s*([A-Z][a-zA-Z\s-]+?)(?:\s|,|\.|$)',
            r'Role:\s*([A-Z][a-zA-Z\s-]+?)(?:\s|,|\.|$)',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                job_title = match.group(0).strip()
                if len(job_title) > 3 and len(job_title) < 100:
                    job_info["job_title"] = job_title
                    break
        
        # Experience extraction patterns
        experience_patterns = [
            r'\d+\s*[-–]\s*\d+\s*years?',
            r'\d+\+\s*years?',
            r'\d+\s*to\s*\d+\s*years?',
            r'minimum\s+\d+\s*years?',
            r'at\s+least\s+\d+\s*years?',
            r'\d+\s*[-–]\s*\d+\s*years?\s*experience',
            r'\d+\+\s*years?\s*experience',
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                job_info["experience_required"] = match.group(0).strip()
                break
        
        # Email extraction
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', job_description)
        if email_match:
            job_info["email"] = email_match.group(0)
        
        # Phone extraction
        phone_match = re.search(r'(\+?[\d\s\-\(\)]{10,})', job_description)
        if phone_match:
            job_info["phone_number"] = phone_match.group(1).strip()
        
        # Website extraction
        website_match = re.search(r'https?://[^\s]+', job_description)
        if website_match:
            job_info["website"] = website_match.group(0)
        
        return job_info
    
    async def save_job_analysis(self, job_description: str, job_url: Optional[str] = None, auth_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract job information and save to organized folder structure
        
        Args:
            job_description: The job description text
            job_url: Optional job posting URL
            
        Returns:
            Dictionary with save results and extracted information
        """
        try:
            # Extract job information using AI
            job_info = await self.extract_job_information(job_description, auth_token)
            
            if "error" in job_info:
                return job_info
            
            # Create company slug for folder name
            company_slug = self._create_company_slug(job_info["company_name"])
            
            # Create company-specific directory
            company_dir = self.cv_analysis_dir / company_slug
            company_dir.mkdir(parents=True, exist_ok=True)
            
            # Save job_info JSON file with timestamp
            timestamp = TimestampUtils.get_timestamp()
            job_info_file = company_dir / f"job_info_{company_slug}_{timestamp}.json"
            job_info_data = job_info.copy()
            job_info_data["extracted_at"] = datetime.now().isoformat()
            if job_url:
                job_info_data["job_url"] = job_url
            
            with open(job_info_file, 'w', encoding='utf-8') as f:
                json.dump(job_info_data, f, indent=2, ensure_ascii=False)
            
            # Save original job description as JSON file with timestamp
            jd_original_file = company_dir / f"jd_original_{timestamp}.json"
            with open(jd_original_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "company": job_info['company_name'],
                    "job_title": job_info['job_title'],
                    "extracted_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "length_chars": len(job_description),
                    "job_url": job_url,
                    "text": job_description
                }, f, ensure_ascii=False, indent=2)
            
            return {
                "success": True,
                "company_slug": company_slug,
                "company_name": job_info["company_name"],
                "job_title": job_info["job_title"],
                "job_info_file": str(job_info_file),
                "jd_original_file": str(jd_original_file),
                "extracted_info": job_info
            }
            
        except Exception as e:
            return {"error": f"Failed to save job analysis: {str(e)}"}
    
    def list_analyzed_jobs(self) -> Dict[str, Any]:
        """List all analyzed jobs in the cv-analysis directory"""
        try:
            jobs = []
            
            if not self.cv_analysis_dir.exists():
                return {"jobs": []}
            
            for company_dir in self.cv_analysis_dir.iterdir():
                if company_dir.is_dir():
                    # Look for job_info JSON file
                    job_info_files = list(company_dir.glob("job_info_*.json"))
                    jd_original_files = list(company_dir.glob("jd_original.json"))
                    
                    for job_info_file in job_info_files:
                        try:
                            with open(job_info_file, 'r', encoding='utf-8') as f:
                                job_data = json.load(f)
                            
                            jobs.append({
                                "company_slug": company_dir.name,
                                "company_name": job_data.get("company_name", "Unknown"),
                                "job_title": job_data.get("job_title", "Unknown"),
                                "location": job_data.get("location", "Unknown"),
                                "industry": job_data.get("industry", "Unknown"),
                                "extracted_at": job_data.get("extracted_at", ""),
                                "job_info_file": str(job_info_file),
                                "jd_original_file": str(jd_original_files[0]) if jd_original_files else None,
                                "has_jd_original": len(jd_original_files) > 0
                            })
                        except Exception as e:
                            continue
            
            # Sort by extracted_at (newest first)
            jobs.sort(key=lambda x: x.get("extracted_at", ""), reverse=True)
            
            return {"jobs": jobs}
            
        except Exception as e:
            return {"error": f"Failed to list analyzed jobs: {str(e)}"}

# Create a global instance
job_extraction_service = JobExtractionService()
