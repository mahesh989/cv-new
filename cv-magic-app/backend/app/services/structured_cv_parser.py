"""
LLM-Based Structured CV Parser

This service uses the centralized AI system to parse CV content from original_cv.txt
into a structured JSON format (original_cv.json) with comprehensive sections and metadata.
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from ..ai.ai_service import ai_service

logger = logging.getLogger(__name__)


class LLMStructuredCVParser:
    """LLM-based parser for converting CV text into structured format"""

    def __init__(self):
        self.default_structure = self._get_default_structure()
        
    def _get_default_structure(self) -> Dict[str, Any]:
        """Get the default CV structure with empty values"""
        return {
            "personal_information": {
                "name": "",
                "phone": "",
                "email": "",
                "location": "",
                "linkedin": "",
                "github": "",
                "portfolio_links": {
                    "blogs": "",
                    "dashboard_portfolio": "",
                    "website": ""
                },
                "residency_status": "",
                "open_to": ""
            },
            "career_profile": {
                "summary": ""
            },
            "skills": {
                "technical_skills": [],
                "key_skills": [],
                "soft_skills": [],
                "domain_expertise": []
            },
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "languages": [],
            "awards": [],
            "publications": [],
            "volunteer_work": [],
            "professional_memberships": [],
            "unknown_sections": {},
            "original_sections": {
                "section_headers_found": [],
                "parsing_approach": "content_preserving"
            },
            "saved_at": "",
            "metadata": {
                "parsing_version": "4.0_content_preserving",
                "content_hash": "",
                "parsing_notes": [],
                "quality_score": 0,
                "completeness_score": 0,
                "source_file": "",
                "processed_at": "",
                "ai_model_used": "",
                "content_preservation": "enabled"
            }
        }

    async def parse_cv_content(self, cv_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse CV content using LLM into structured format
        
        Args:
            cv_data: CV data as string (raw text) or dictionary (structured)
            
        Returns:
            Structured CV dictionary with all sections
        """
        try:
            # If input is already a dictionary, validate and return
            if isinstance(cv_data, dict) and "personal_information" in cv_data:
                logger.info("CV data is already in structured format")
                return cv_data
            
            # Convert to string if needed
            cv_text = str(cv_data)
            
            # Use LLM to parse the CV content
            structured_cv = await self._parse_with_llm(cv_text)
            
            # Add original content preservation (without raw text)
            structured_cv["original_sections"]["section_headers_found"] = self._extract_section_headers(cv_text)
            
            # Add metadata
            structured_cv["saved_at"] = datetime.now().isoformat()
            structured_cv["metadata"]["processed_at"] = datetime.now().isoformat()
            structured_cv["metadata"]["content_hash"] = self._generate_content_hash(cv_text)
            structured_cv["metadata"]["quality_score"] = self._calculate_quality_score(structured_cv)
            structured_cv["metadata"]["completeness_score"] = self._calculate_completeness_score(structured_cv)
            structured_cv["metadata"]["parsing_notes"].append("Content-preserving parser used - maintains original formatting")
            
            return structured_cv
            
        except Exception as e:
            logger.error(f"Error parsing CV content with LLM: {e}")
            # Return empty structure with error info
            empty_structure = self._get_empty_structure()
            empty_structure["parsing_error"] = str(e)
            empty_structure["original_text"] = cv_text[:1000] + "..." if len(cv_text) > 1000 else cv_text
            return empty_structure

    async def _parse_with_llm(self, cv_text: str) -> Dict[str, Any]:
        """Use LLM to parse CV text into structured format"""
        try:
            # Create the parsing prompt
            parsing_prompt = self._create_parsing_prompt(cv_text)
            
            # Get response from AI service
            ai_response = await ai_service.generate_response(
                prompt=parsing_prompt,
                system_prompt="You are an expert CV parser that preserves original content structure. Your primary goal is to maintain the exact formatting, bullet points, and descriptions as they appear in the original CV while organizing them into the specified JSON structure. Do NOT break down, summarize, or restructure the original content - preserve it exactly as written.",
                max_tokens=4000,
                temperature=0.0
            )
            
            # Parse the JSON response
            try:
                parsed_data = json.loads(ai_response.content.strip())
                
                # Validate and merge with default structure
                structured_cv = self._merge_with_default_structure(parsed_data)
                structured_cv["metadata"]["ai_model_used"] = ai_service.current_model
                
                logger.info(f"Successfully parsed CV using {ai_service.current_model}")
                return structured_cv
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                # Try to extract JSON from response if it's wrapped in markdown
                json_match = self._extract_json_from_response(ai_response.content)
                if json_match:
                    parsed_data = json.loads(json_match)
                    structured_cv = self._merge_with_default_structure(parsed_data)
                    structured_cv["metadata"]["ai_model_used"] = ai_service.current_model
                    return structured_cv
                else:
                    raise e
            
        except Exception as e:
            logger.error(f"Error in LLM parsing: {e}")
            raise e

    def _create_parsing_prompt(self, cv_text: str) -> str:
        """Create a content-preserving prompt for CV parsing"""
        return f"""
PARSE THIS CV INTO STRUCTURED JSON - PRESERVE ORIGINAL CONTENT EXACTLY AS WRITTEN

CV TEXT:
{cv_text}

INSTRUCTIONS FOR CONTENT PRESERVATION:
- MAINTAIN original bullet points, descriptions, and formatting exactly as they appear
- DO NOT break down or fragment content - keep complete sentences and descriptions intact
- PRESERVE the original wording, structure, and flow of each section
- If the CV has bullet points with detailed descriptions, maintain those complete descriptions
- If skills are presented in paragraph form, preserve the paragraph structure
- Keep all original context and details - do not summarize or simplify

Return a JSON object with this structure, but PRESERVE the original content format:

{{
    "personal_information": {{
        "name": "Exact name as written",
        "phone": "Phone number as written",
        "email": "Email as written", 
        "location": "Extract location from contact line (city, state, postcode) - look for address information in header",
        "linkedin": "LinkedIn text/URL as written",
        "github": "GitHub text/URL as written",
        "portfolio_links": {{
            "blogs": "Blog text/URL as written",
            "dashboard_portfolio": "Portfolio text/URL as written",
            "website": "Website text/URL as written"
        }},
        "residency_status": "Status as mentioned",
        "open_to": "Preferences as mentioned"
    }},
    "career_profile": {{
        "summary": "Complete summary/objective text exactly as written"
    }},
    "skills": {{
        "technical_skills": ["PRESERVE ORIGINAL FORMAT: If bullet points, keep complete bullet descriptions. If paragraph, keep as paragraph. If list, keep as individual items."],
        "key_skills": ["Only if CV has separate 'Key Skills' section - preserve original format"],
        "soft_skills": ["Only if CV has separate 'Soft Skills' section - preserve original format"],
        "domain_expertise": ["Derived expertise areas based on CV content"]
    }},
    "education": [
        {{
            "degree": "Exact degree name as written",
            "institution": "Exact institution name as written",
            "year": "Exact date/year format as written",
            "gpa": "GPA exactly as mentioned (including 'GPA' text if shown)",
            "relevant_courses": ["Courses exactly as listed"],
            "honors": ["List of honors/achievements as individual items, or empty list if none"],
            "location": "Extract city, country from institution line - look for location info near institution name"
        }}
    ],
    "experience": [
        {{
            "title": "Exact job title as written",
            "company": "Exact company name as written",
            "duration": "Exact duration format as written",
            "location": "Exact location as written",
            "responsibilities": ["Each bullet point or responsibility EXACTLY as written - do not break down or modify"],
            "achievements": ["ONLY if there is a separate 'Achievements' section or subsection in the CV - otherwise leave empty"],
            "technologies": ["ONLY if there is a separate 'Technologies' section or subsection in the CV - otherwise leave empty"]
        }}
    ],
    "projects": [
        {{
            "name": "Project name exactly as written",
            "description": ["PRESERVE BULLET POINTS: If project has bullet points, keep each bullet point as a separate array item exactly as written. If single paragraph, use one array item."],
            "technologies": ["Technologies as listed"],
            "duration": "Duration as mentioned",
            "role": "Role as mentioned",
            "achievements": ["Achievements as written"],
            "url": "URL if provided"
        }}
    ],
    "certifications": ["Parse if section exists, preserve exact format"],
    "languages": ["Parse if section exists, preserve exact format"],
    "awards": ["Parse if section exists, preserve exact format"],
    "publications": ["Parse if section exists, preserve exact format"],
    "volunteer_work": ["Parse if section exists, preserve exact format"],
    "professional_memberships": ["Parse if section exists, preserve exact format"]
}}

CRITICAL CONTENT PRESERVATION RULES:
1. **EXACT WORDING**: Use the exact words, phrases, and descriptions from the original CV
2. **COMPLETE CONTENT**: If a bullet point has a full sentence/description, keep it complete - don't fragment it
3. **ORIGINAL STRUCTURE**: If skills are in bullet format, keep as bullets. If paragraph, keep as paragraph
4. **NO SUMMARIZATION**: Never summarize, paraphrase, or simplify the original content
5. **CONTEXT PRESERVATION**: Maintain all context, details, and qualifiers from the original
6. **FORMATTING CUES**: Preserve formatting indicators (bullet symbols, numbering, etc.) in the text
7. **EMPTY SECTIONS**: Only populate sections that exist in the CV - leave others empty
8. **NO FALSE EXTRACTIONS**: Do NOT create 'achievements' or 'technologies' arrays unless they exist as separate sections in the original CV
9. **SECTION IDENTIFICATION**: Only identify actual section headers (like 'EXPERIENCE', 'SKILLS') - not names, job titles, or degree names
10. **LOCATION EXTRACTION**: Carefully extract location information from contact details and institution descriptions - look for city, state, country patterns
11. **PROJECT FORMAT PRESERVATION**: For projects with bullet points, keep each bullet as a separate array item in 'description'. For paragraph projects, use single array item.

Return ONLY the JSON object with preserved original content.
"""

    def _extract_json_from_response(self, response: str) -> Optional[str]:
        """Extract JSON from response that might be wrapped in markdown"""
        import re
        # Try to find JSON wrapped in code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        # Try to find JSON object in the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return None
    
    def _extract_section_headers(self, cv_text: str) -> List[str]:
        """Extract section headers from CV text to understand structure"""
        import re
        
        # Known CV section keywords (must contain these to be considered headers)
        section_keywords = [
            'EXPERIENCE', 'WORK', 'EMPLOYMENT', 'CAREER', 'PROFESSIONAL',
            'EDUCATION', 'ACADEMIC', 'QUALIFICATION', 'DEGREE',
            'SKILLS', 'TECHNICAL', 'COMPETENCIES', 'ABILITIES',
            'PROFILE', 'SUMMARY', 'OBJECTIVE', 'ABOUT',
            'PROJECTS', 'PORTFOLIO', 'ACHIEVEMENTS', 'ACCOMPLISHMENTS',
            'CERTIFICATIONS', 'CERTIFICATES', 'TRAINING',
            'LANGUAGES', 'PUBLICATIONS', 'RESEARCH',
            'AWARDS', 'HONORS', 'VOLUNTEER', 'ACTIVITIES'
        ]
        
        # Patterns for section headers (must be ALL CAPS or clearly formatted)
        header_patterns = [
            r'^([A-Z][A-Z\s&-]+)\s*$',  # ALL CAPS headers only
            r'^\*\*([A-Za-z\s&]+)\*\*',  # Bold headers
            r'^#+ ([A-Za-z\s&]+)',  # Markdown headers
        ]
        
        headers_found = []
        lines = cv_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            for pattern in header_patterns:
                match = re.match(pattern, line)
                if match:
                    header = match.group(1).strip()
                    # Check if this looks like a section header
                    if (len(header) > 3 and len(header) < 50 and 
                        any(keyword in header.upper() for keyword in section_keywords)):
                        headers_found.append(header)
                    break
        
        return list(set(headers_found))  # Remove duplicates

    def _merge_with_default_structure(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge parsed data with default structure to ensure completeness"""
        structured_cv = self.default_structure.copy()
        
        # Recursively merge the structures
        def merge_dict(default: Dict, parsed: Dict) -> Dict:
            result = default.copy()
            for key, value in parsed.items():
                if key in result:
                    if isinstance(result[key], dict) and isinstance(value, dict):
                        result[key] = merge_dict(result[key], value)
                    else:
                        result[key] = value
                else:
                    # Store unknown sections
                    if key not in ["saved_at", "metadata"]:
                        if "unknown_sections" not in result:
                            result["unknown_sections"] = {}
                        result["unknown_sections"][key] = value
            return result
        
        return merge_dict(structured_cv, parsed_data)

    def _generate_content_hash(self, content: str) -> str:
        """Generate a hash for content verification"""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _calculate_quality_score(self, cv_data: Dict[str, Any]) -> int:
        """Calculate CV quality score based on completeness and content"""
        score = 0
        
        # Personal information (30 points)
        personal = cv_data.get("personal_information", {})
        if personal.get("name"): score += 10
        if personal.get("email"): score += 8
        if personal.get("phone"): score += 5
        if personal.get("location"): score += 4
        if personal.get("linkedin"): score += 3
        
        # Career profile (15 points)
        if cv_data.get("career_profile", {}).get("summary"): score += 15
        
        # Skills (25 points)
        skills = cv_data.get("skills", {})
        tech_skills = len(skills.get("technical_skills", []))
        if tech_skills > 0: score += 10
        if tech_skills >= 5: score += 5
        if tech_skills >= 10: score += 5
        if len(skills.get("key_skills", [])) > 0: score += 5
        
        # Experience (20 points)
        experience = cv_data.get("experience", [])
        if len(experience) > 0: score += 10
        if len(experience) >= 2: score += 5
        if len(experience) >= 3: score += 5
        
        # Education (10 points)
        if len(cv_data.get("education", [])) > 0: score += 10
        
        return min(score, 100)

    def _calculate_completeness_score(self, cv_data: Dict[str, Any]) -> int:
        """Calculate completeness score based on filled sections"""
        total_sections = 11  # Main sections count
        filled_sections = 0
        
        sections_to_check = [
            "personal_information", "career_profile", "skills", "education", 
            "experience", "projects", "certifications", "languages", 
            "awards", "publications", "volunteer_work"
        ]
        
        for section in sections_to_check:
            section_data = cv_data.get(section, {})
            if isinstance(section_data, dict):
                if any(v for v in section_data.values() if v):
                    filled_sections += 1
            elif isinstance(section_data, list):
                if section_data:
                    filled_sections += 1
        
        return int((filled_sections / total_sections) * 100)

    def _get_empty_structure(self) -> Dict[str, Any]:
        """Get empty structure for error cases"""
        return self.default_structure.copy()

    def save_structured_cv(self, cv_data: Dict[str, Any], file_path: str) -> bool:
        """Save structured CV to JSON file"""
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cv_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully saved structured CV to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving structured CV: {e}")
            return False

    def load_structured_cv(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load structured CV from JSON file"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"CV file not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                cv_data = json.load(f)
            
            logger.info(f"Successfully loaded structured CV from {file_path}")
            return cv_data
            
        except Exception as e:
            logger.error(f"Error loading structured CV: {e}")
            return None

    def validate_cv_structure(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate CV structure and content"""
        report = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "missing_required": [],
            "sections_found": [],
            "completeness_score": 0,
            "quality_score": 0,
            "content_integrity": "good"
        }
        
        # Check required sections
        required_sections = ["personal_information", "skills"]
        for section in required_sections:
            if section not in cv_data or not cv_data[section]:
                report["missing_required"].append(section)
                report["valid"] = False
        
        # Check sections found
        for section in cv_data.keys():
            if section not in ["saved_at", "metadata", "unknown_sections"]:
                if cv_data[section]:  # Only count non-empty sections
                    report["sections_found"].append(section)
        
        # Calculate scores
        report["quality_score"] = self._calculate_quality_score(cv_data)
        report["completeness_score"] = self._calculate_completeness_score(cv_data)
        
        # Check parsing notes for warnings
        parsing_notes = cv_data.get("metadata", {}).get("parsing_notes", [])
        if parsing_notes:
            report["warnings"].extend(parsing_notes)
        
        # Quality-based warnings
        if report["quality_score"] < 50:
            report["warnings"].append("CV quality score is below 50")
        
        if report["completeness_score"] < 40:
            report["warnings"].append("CV completeness score is below 40")
        
        return report


# Global instance
enhanced_cv_parser = LLMStructuredCVParser()