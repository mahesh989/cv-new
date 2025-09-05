import os
import json
import re
import httpx
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

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
        return """
        Extract the following information from this job description. Return ONLY a JSON object with these exact keys:
        
        {
            "company_name": "exact company name",
            "job_title": "job title/position", 
            "location": "job location/city",
            "experience_required": "experience requirements",
            "seniority_level": "entry-level/mid-level/senior/lead/principal",
            "industry": "industry/sector",
            "phone_number": "phone number if mentioned, otherwise null",
            "email": "email address if mentioned, otherwise null",
            "website": "company website if mentioned, otherwise null",
            "work_type": "remote/hybrid/onsite if mentioned, otherwise null"
        }
        
        Job Description:
        {job_description}
        """
    
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
        Extract job information using the selected AI model
        
        Args:
            job_description: The job description text
            auth_token: Optional authentication token for AI API calls
            
        Returns:
            Dictionary containing extracted job information
        """
        if not job_description or len(job_description.strip()) < 10:
            return {"error": "Job description too short or empty"}
        
        try:
            # Use LLM-based extraction with the selected AI model
            if auth_token:
                # Load the prompt template only when using AI
                prompt_template = self._load_prompt()
                
                # Format the prompt with the job description
                prompt = prompt_template.format(job_description=job_description[:3000])  # Limit to 3000 chars
                try:
                    # Make authenticated call to AI API
                    async with httpx.AsyncClient() as client:
                        headers = {
                            "Authorization": f"Bearer {auth_token}",
                            "Content-Type": "application/json"
                        }
                        
                        response = await client.post(
                            "http://localhost:8000/api/ai/chat",
                            headers=headers,
                            json={
                                "prompt": prompt,
                                "temperature": 0.1,
                                "max_tokens": 500
                            },
                            timeout=30.0
                        )
                        
                        if response.status_code == 200:
                            ai_response = response.json()
                            response_text = ai_response.get("content", "")
                            
                            # Parse the JSON response
                            job_info = self._parse_json_response(response_text)
                            
                            # Validate and clean the extracted data
                            job_info = self._validate_job_info(job_info)
                            
                            print(f"✅ LLM extraction successful: {job_info.get('company_name', 'Unknown')}")
                            return job_info
                        else:
                            print(f"AI API call failed with status {response.status_code}: {response.text}")
                            # Fall through to rule-based extraction
                except Exception as ai_error:
                    print(f"AI API call failed: {ai_error}")
                    # Fall through to rule-based extraction
            
            # Fallback to rule-based extraction if AI is not available
            print("⚠️ Using rule-based extraction as fallback")
            return self._extract_with_rules(job_description)
            
        except Exception as e:
            print(f"Job extraction error: {e}")
            raise Exception(f"Failed to extract job information: {str(e)}")
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from AI response"""
        try:
            # Clean the response
            response = response.strip()
            
            # Remove any markdown formatting if present
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            # Try to find JSON in the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # Try to parse the entire response as JSON
                return json.loads(response)
                
        except json.JSONDecodeError as e:
            # If JSON parsing fails, raise exception
            print(f"JSON parsing failed: {e}")
            print(f"Response was: {response}")
            raise Exception(f"Failed to parse JSON response: {str(e)}")
    
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
            # Look for company names in "About us" sections (most reliable)
            r'About\s+us\s+([A-Z][a-zA-Z\s&.-]+?)\s+is',
            r'About\s+the\s+company\s+([A-Z][a-zA-Z\s&.-]+?)\s+is',
            # Look for repeated company names (like "No To Violence" appearing twice)
            r'([A-Z][a-zA-Z\s&.-]+?)\s+Job\s+Summary\s+\1',
            r'([A-Z][a-zA-Z\s&.-]+?)\s+Applications\s+close.*?\1',
            # Look for company names in job titles/headers (but exclude job titles)
            r'(?:^|\n)\s*([A-Z][a-zA-Z\s&.-]+?)\s+Job\s+Summary',
            r'(?:^|\n)\s*([A-Z][a-zA-Z\s&.-]+?)\s+Applications\s+close',
            # Look for company names after "at", "with", "for" (but not job titles)
            r'(?:^|\n)\s*[A-Z][a-zA-Z\s]*\s+at\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s|,|\.|$)',
            r'(?:^|\n)\s*[A-Z][a-zA-Z\s]*\s+with\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s|,|\.|$)',
            r'(?:^|\n)\s*[A-Z][a-zA-Z\s]*\s+for\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s|,|\.|$)',
            # Look for company names in email domains
            r'@([a-zA-Z0-9.-]+)\.(?:com|org|au|net)',
            # Look for company names in website URLs
            r'https?://(?:www\.)?([a-zA-Z0-9.-]+)\.(?:com|org|au|net)',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                company_name = match.group(1).strip()
                # Filter out invalid company names
                if (len(company_name) > 3 and len(company_name) < 50 and 
                    not company_name.lower() in ['work', 'job', 'position', 'role', 'applications', 'close', 'posted', 'summary', 'description', 'requirements', 'responsibilities', 'experience', 'skills', 'qualifications', 'benefits', 'offer', 'apply', 'contact', 'email', 'phone', 'website', 'location', 'salary', 'full', 'time', 'part', 'contract', 'permanent', 'temporary', 'remote', 'hybrid', 'onsite', 'office', 'home', 'based', 'melbourne', 'sydney', 'brisbane', 'perth', 'adelaide', 'canberra', 'darwin', 'hobart', 'australia', 'new', 'zealand']):
                    job_info["company_name"] = company_name
                    break
        
        # Job title extraction patterns
        title_patterns = [
            r'(Senior|Junior|Lead|Principal|Staff)?\s*(Software Engineer|Data Analyst|Developer|Manager|Analyst|Designer|Consultant|Specialist)',
            r'(Software Engineer|Data Analyst|Developer|Manager|Analyst|Designer|Consultant|Specialist)',
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
        
        # Location extraction patterns
        location_patterns = [
            r'(Melbourne|Sydney|Brisbane|Perth|Adelaide|Canberra|Darwin|Hobart)',
            r'(Australia|New Zealand)',
            r'Location:\s*([A-Z][a-zA-Z\s,-]+?)(?:\s|,|\.|$)',
            r'Based in\s+([A-Z][a-zA-Z\s,-]+?)(?:\s|,|\.|$)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                if len(location) > 2 and len(location) < 50:
                    job_info["location"] = location
                    break
        
        # Experience extraction patterns
        experience_patterns = [
            r'(\d+[\+\-\s]*\d*)\s*years?\s*(?:of\s*)?experience',
            r'(\d+[\+\-\s]*\d*)\s*years?\s*(?:in|with)',
            r'minimum\s*(\d+)\s*years?',
            r'at least\s*(\d+)\s*years?',
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                experience = match.group(1).strip()
                job_info["experience_required"] = experience
                break
        
        # Seniority level extraction
        if re.search(r'senior|lead|principal|staff', job_description, re.IGNORECASE):
            job_info["seniority_level"] = "senior"
        elif re.search(r'junior|entry|graduate|trainee', job_description, re.IGNORECASE):
            job_info["seniority_level"] = "entry-level"
        elif re.search(r'mid|intermediate', job_description, re.IGNORECASE):
            job_info["seniority_level"] = "mid-level"
        
        # Industry extraction
        industry_keywords = {
            'technology': ['software', 'tech', 'IT', 'programming', 'development'],
            'healthcare': ['health', 'medical', 'hospital', 'clinic'],
            'finance': ['banking', 'financial', 'investment', 'fintech'],
            'education': ['education', 'university', 'school', 'teaching'],
            'retail': ['retail', 'commerce', 'e-commerce', 'shopping'],
        }
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in job_description.lower() for keyword in keywords):
                job_info["industry"] = industry
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
        
        # Work type extraction
        if re.search(r'remote|work from home|WFH', job_description, re.IGNORECASE):
            job_info["work_type"] = "Remote"
        elif re.search(r'hybrid', job_description, re.IGNORECASE):
            job_info["work_type"] = "Hybrid"
        elif re.search(r'onsite|on-site|office', job_description, re.IGNORECASE):
            job_info["work_type"] = "Onsite"
        
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
            
            # Save job_info JSON file
            job_info_file = company_dir / f"job_info_{company_slug}.json"
            job_info_data = job_info.copy()
            job_info_data["extracted_at"] = datetime.now().isoformat()
            if job_url:
                job_info_data["job_url"] = job_url
            
            with open(job_info_file, 'w', encoding='utf-8') as f:
                json.dump(job_info_data, f, indent=2, ensure_ascii=False)
            
            # Save original job description as text file
            jd_original_file = company_dir / "jd_original.txt"
            with open(jd_original_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("ORIGINAL JOB DESCRIPTION\n")
                f.write(f"Company: {job_info['company_name']}\n")
                f.write(f"Job Title: {job_info['job_title']}\n")
                f.write(f"Extracted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Length: {len(job_description)} characters\n")
                if job_url:
                    f.write(f"URL: {job_url}\n")
                f.write("=" * 80 + "\n\n")
                f.write(job_description)
            
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
                    jd_original_files = list(company_dir.glob("jd_original.txt"))
                    
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
