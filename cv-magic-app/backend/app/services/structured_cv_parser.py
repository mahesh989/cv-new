"""
Structured CV Parser Service

This service handles parsing and saving CVs in the structured format,
with robust error handling for missing information and unknown sections.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class StructuredCVParser:
    """Parser for structured CV format with comprehensive error handling"""

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
                "portfolio_links": {
                    "blogs": "",
                    "github": "",
                    "dashboard_portfolio": "",
                    "website": ""
                }
            },
            "career_profile": {
                "summary": ""
            },
            "technical_skills": [],
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "soft_skills": [],
            "domain_expertise": [],
            "languages": [],
            "awards": [],
            "publications": [],
            "volunteer_work": [],
            "professional_memberships": [],
            "unknown_sections": {},  # For handling unknown sections
            "saved_at": ""
        }

    def parse_cv_content(self, cv_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse CV content from various formats into structured format
        
        Args:
            cv_data: CV data as string (raw text) or dictionary (structured)
            
        Returns:
            Structured CV dictionary with all sections
        """
        try:
            # If input is string, try to parse as JSON first, then as raw text
            if isinstance(cv_data, str):
                try:
                    parsed_data = json.loads(cv_data)
                    return self._parse_structured_data(parsed_data)
                except json.JSONDecodeError:
                    # If JSON parsing fails, treat as raw text
                    return self._parse_raw_text(cv_data)
            
            # If input is already a dictionary
            elif isinstance(cv_data, dict):
                return self._parse_structured_data(cv_data)
            
            else:
                logger.warning(f"Unsupported CV data type: {type(cv_data)}")
                return self._get_empty_structure()
                
        except Exception as e:
            logger.error(f"Error parsing CV content: {e}")
            return self._get_empty_structure()

    def _parse_structured_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse already structured CV data with validation and error handling"""
        result = self._get_empty_structure()
        
        try:
            # Handle personal information
            result["personal_information"] = self._parse_personal_information(
                data.get("personal_information", {})
            )
            
            # Handle career profile
            result["career_profile"] = self._parse_career_profile(
                data.get("career_profile", {})
            )
            
            # Handle technical skills
            result["technical_skills"] = self._parse_technical_skills(
                data.get("technical_skills", [])
            )
            
            # Handle education
            result["education"] = self._parse_education(
                data.get("education", [])
            )
            
            # Handle experience
            result["experience"] = self._parse_experience(
                data.get("experience", [])
            )
            
            # Handle projects
            result["projects"] = self._parse_projects(
                data.get("projects", [])
            )
            
            # Handle certifications
            result["certifications"] = self._parse_certifications(
                data.get("certifications", [])
            )
            
            # Handle simple arrays
            result["soft_skills"] = self._parse_simple_array(data.get("soft_skills", []))
            result["domain_expertise"] = self._parse_simple_array(data.get("domain_expertise", []))
            result["awards"] = self._parse_simple_array(data.get("awards", []))
            result["publications"] = self._parse_simple_array(data.get("publications", []))
            result["volunteer_work"] = self._parse_simple_array(data.get("volunteer_work", []))
            result["professional_memberships"] = self._parse_simple_array(data.get("professional_memberships", []))
            
            # Handle languages
            result["languages"] = self._parse_languages(data.get("languages", []))
            
            # Handle unknown sections
            result["unknown_sections"] = self._parse_unknown_sections(data, result)
            
            # Preserve metadata if it exists
            if "metadata" in data:
                result["metadata"] = data["metadata"]
            
            # Set timestamp
            result["saved_at"] = data.get("saved_at", datetime.now().isoformat())
            
            logger.info("Successfully parsed structured CV data")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing structured data: {e}")
            return self._get_empty_structure()
    
    # Helper methods for structured data parsing
    def _parse_personal_information(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse personal information with error handling"""
        default_personal = self.default_structure["personal_information"].copy()
        
        if not isinstance(data, dict):
            return default_personal
        
        # Safely extract each field
        default_personal["name"] = str(data.get("name", "")).strip()
        default_personal["phone"] = str(data.get("phone", "")).strip()
        default_personal["email"] = str(data.get("email", "")).strip()
        default_personal["location"] = str(data.get("location", "")).strip()
        default_personal["linkedin"] = str(data.get("linkedin", "")).strip()
        
        # Handle portfolio links
        portfolio_links = data.get("portfolio_links", {})
        if isinstance(portfolio_links, dict):
            default_personal["portfolio_links"]["blogs"] = str(portfolio_links.get("blogs", "")).strip()
            default_personal["portfolio_links"]["github"] = str(portfolio_links.get("github", "")).strip()
            default_personal["portfolio_links"]["dashboard_portfolio"] = str(portfolio_links.get("dashboard_portfolio", "")).strip()
            default_personal["portfolio_links"]["website"] = str(portfolio_links.get("website", "")).strip()
        
        return default_personal
    
    def _parse_career_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse career profile with error handling"""
        if not isinstance(data, dict):
            return {"summary": ""}
        
        return {
            "summary": str(data.get("summary", "")).strip()
        }
    
    def _parse_technical_skills(self, data: List[Any]) -> List[str]:
        """Parse technical skills array"""
        if not isinstance(data, list):
            return []
        
        skills = []
        for skill in data:
            if isinstance(skill, str) and skill.strip():
                skills.append(skill.strip())
        
        return skills
    
    def _parse_education(self, data: List[Any]) -> List[Dict[str, Any]]:
        """Parse education array with comprehensive error handling"""
        if not isinstance(data, list):
            return []
        
        education_list = []
        for item in data:
            if isinstance(item, dict):
                education_entry = {
                    "degree": str(item.get("degree", "")).strip(),
                    "institution": str(item.get("institution", "")).strip(),
                    "location": str(item.get("location", "")).strip(),
                    "duration": str(item.get("duration", "")).strip(),
                    "additional_info": str(item.get("additional_info", "")).strip(),
                    "gpa": str(item.get("gpa", "")).strip(),
                    "honors": str(item.get("honors", "")).strip(),
                    "relevant_coursework": item.get("relevant_coursework", []) if isinstance(item.get("relevant_coursework"), list) else []
                }
                education_list.append(education_entry)
        
        return education_list
    
    def _parse_experience(self, data: List[Any]) -> List[Dict[str, Any]]:
        """Parse experience array with comprehensive error handling"""
        if not isinstance(data, list):
            return []
        
        experience_list = []
        for item in data:
            if isinstance(item, dict):
                experience_entry = {
                    "position": str(item.get("position", "")).strip(),
                    "company": str(item.get("company", "")).strip(),
                    "location": str(item.get("location", "")).strip(),
                    "duration": str(item.get("duration", "")).strip(),
                    "employment_type": str(item.get("employment_type", "")).strip(),
                    "achievements": [],
                    "responsibilities": []
                }
                
                # Handle achievements
                achievements = item.get("achievements", [])
                if isinstance(achievements, list):
                    experience_entry["achievements"] = [str(a).strip() for a in achievements if str(a).strip()]
                
                # Handle responsibilities (alternative to achievements)
                responsibilities = item.get("responsibilities", [])
                if isinstance(responsibilities, list):
                    experience_entry["responsibilities"] = [str(r).strip() for r in responsibilities if str(r).strip()]
                
                experience_list.append(experience_entry)
        
        return experience_list
    
    def _parse_projects(self, data: List[Any]) -> List[Dict[str, Any]]:
        """Parse projects array with comprehensive error handling"""
        if not isinstance(data, list):
            return []
        
        projects_list = []
        for item in data:
            if isinstance(item, dict):
                project_entry = {
                    "name": str(item.get("name", "")).strip(),
                    "duration": str(item.get("duration", "")).strip(),
                    "company": str(item.get("company", "")).strip(),
                    "description": str(item.get("description", "")).strip(),
                    "technologies": [],
                    "achievements": [],
                    "url": str(item.get("url", "")).strip()
                }
                
                # Handle technologies
                technologies = item.get("technologies", [])
                if isinstance(technologies, list):
                    project_entry["technologies"] = [str(t).strip() for t in technologies if str(t).strip()]
                
                # Handle achievements
                achievements = item.get("achievements", [])
                if isinstance(achievements, list):
                    project_entry["achievements"] = [str(a).strip() for a in achievements if str(a).strip()]
                
                projects_list.append(project_entry)
        
        return projects_list
    
    def _parse_certifications(self, data: List[Any]) -> List[Dict[str, Any]]:
        """Parse certifications array with comprehensive error handling"""
        if not isinstance(data, list):
            return []
        
        certifications_list = []
        for item in data:
            if isinstance(item, dict):
                cert_entry = {
                    "name": str(item.get("name", "")).strip(),
                    "issuing_organization": str(item.get("issuing_organization", "")).strip(),
                    "date_obtained": str(item.get("date_obtained", "")).strip(),
                    "expiry_date": str(item.get("expiry_date", "")).strip(),
                    "status": str(item.get("status", "")).strip(),
                    "description": str(item.get("description", "")).strip(),
                    "credential_id": str(item.get("credential_id", "")).strip(),
                    "url": str(item.get("url", "")).strip()
                }
                certifications_list.append(cert_entry)
        
        return certifications_list
    
    def _parse_languages(self, data: List[Any]) -> List[Dict[str, Any]]:
        """Parse languages array with error handling"""
        if not isinstance(data, list):
            return []
        
        languages_list = []
        for item in data:
            if isinstance(item, dict):
                language_entry = {
                    "language": str(item.get("language", "")).strip(),
                    "proficiency": str(item.get("proficiency", "")).strip(),
                    "certification": str(item.get("certification", "")).strip()
                }
                languages_list.append(language_entry)
        
        return languages_list
    
    def _parse_simple_array(self, data: List[Any]) -> List[str]:
        """Parse simple string arrays with error handling"""
        if not isinstance(data, list):
            return []
        
        result = []
        for item in data:
            if isinstance(item, str) and item.strip():
                result.append(item.strip())
        
        return result
    
    def _parse_unknown_sections(self, original_data: Dict[str, Any], parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify and store unknown sections"""
        known_sections = {
            "personal_information", "career_profile", "technical_skills", "education", 
            "experience", "projects", "certifications", "soft_skills", "domain_expertise", 
            "languages", "awards", "publications", "volunteer_work", "professional_memberships", 
            "saved_at", "metadata"  # Include metadata as a known section
        }
        
        unknown_sections = {}
        for key, value in original_data.items():
            if key not in known_sections:
                unknown_sections[key] = value
                logger.info(f"Found unknown section: {key}")
        
        return unknown_sections

    def _parse_raw_text(self, text: str) -> Dict[str, Any]:
        """Parse raw text CV format with enhanced extraction"""
        result = self._get_empty_structure()
        
        try:
            # Extract personal information
            result["personal_information"] = self._extract_personal_info_from_text(text)
            
            # Extract sections based on headers
            sections = self._extract_sections_from_text(text)
            
            # Map sections to structured format
            if "CAREER PROFILE" in sections:
                result["career_profile"]["summary"] = sections["CAREER PROFILE"].strip()
            
            if "KEY SKILLS" in sections:
                result["technical_skills"] = self._extract_skills_from_text(sections["KEY SKILLS"])
            elif "TECHNICAL SKILLS" in sections:
                result["technical_skills"] = self._text_to_skills_array(sections["TECHNICAL SKILLS"])
            
            if "EDUCATION" in sections:
                result["education"] = self._text_to_education_array(sections["EDUCATION"])
            
            if "PROFESSIONAL EXPERIENCE" in sections:
                result["experience"] = self._text_to_experience_array(sections["PROFESSIONAL EXPERIENCE"])
            elif "EXPERIENCE" in sections:
                result["experience"] = self._text_to_experience_array(sections["EXPERIENCE"])
            
            if "UNIVERSITY PROJECT" in sections:
                # Enhanced project parsing with education context
                result["projects"] = self._text_to_projects_array_with_context(
                    sections["UNIVERSITY PROJECT"], 
                    result["education"]
                )
            elif "PROJECTS" in sections:
                result["projects"] = self._text_to_projects_array_with_context(
                    sections["PROJECTS"], 
                    result["education"]
                )
            
            if "CERTIFICATIONS" in sections:
                result["certifications"] = self._text_to_certifications_array(sections["CERTIFICATIONS"])
            
            # Store unknown sections
            known_headers = {
                "CAREER PROFILE", "KEY SKILLS", "TECHNICAL SKILLS", "EDUCATION", 
                "PROFESSIONAL EXPERIENCE", "EXPERIENCE", "UNIVERSITY PROJECT", 
                "PROJECTS", "CERTIFICATIONS"
            }
            for header, content in sections.items():
                if header not in known_headers:
                    result["unknown_sections"][header] = content
            
            result["saved_at"] = datetime.now().isoformat()
            
            logger.info("Successfully parsed raw text CV with enhanced extraction")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing raw text: {e}")
            return self._get_empty_structure()

    def _extract_personal_info_from_text(self, text: str) -> Dict[str, Any]:
        """Extract personal information from raw text with enhanced parsing"""
        import re
        
        lines = text.split('\n')
        personal_info = self.default_structure["personal_information"].copy()
        
        # Extract name from first line
        if lines:
            personal_info["name"] = lines[0].strip()
        
        # Look for contact information in the first few lines
        contact_text = '\n'.join(lines[:5])
        
        # Extract phone number
        phone_pattern = r'(\d{4}\s\d{3}\s\d{3})'
        phone_match = re.search(phone_pattern, contact_text)
        if phone_match:
            personal_info["phone"] = phone_match.group(1)
        
        # Extract email
        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        email_match = re.search(email_pattern, contact_text)
        if email_match:
            personal_info["email"] = email_match.group(1)
        
        # Extract location from the entire text (look for Australian locations)
        full_text = text.lower()
        if 'sydney' in full_text and 'australia' in full_text:
            personal_info["location"] = "Sydney, Australia"
        elif 'melbourne' in full_text and 'australia' in full_text:
            personal_info["location"] = "Melbourne, Australia"
        elif 'brisbane' in full_text and 'australia' in full_text:
            personal_info["location"] = "Brisbane, Australia"
        elif 'perth' in full_text and 'australia' in full_text:
            personal_info["location"] = "Perth, Australia"
        elif 'australia' in full_text:
            # More specific location extraction
            location_patterns = [
                r'([A-Za-z\s]+,\s*(?:NSW|VIC|QLD|WA|SA|TAS|NT|ACT),?\s*\d{4})',
                r'([A-Za-z\s]+,\s*(?:New South Wales|Victoria|Queensland|Western Australia|South Australia|Tasmania|Northern Territory|Australian Capital Territory))',
                r'(Sydney|Melbourne|Brisbane|Perth|Adelaide|Darwin|Hobart|Canberra),\s*Australia'
            ]
            
            for pattern in location_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    personal_info["location"] = match.group(1).strip()
                    break
            
            # Fallback to just Australia if specific location not found
            if not personal_info["location"]:
                personal_info["location"] = "Australia"
        
        # Extract portfolio links
        if 'GitHub' in contact_text:
            personal_info["portfolio_links"]["github"] = "GitHub Profile Available"
        if 'Medium' in contact_text or 'Blog' in contact_text:
            personal_info["portfolio_links"]["blogs"] = "Medium Blog Available"
        if 'Dashboard Portfolio' in contact_text:
            personal_info["portfolio_links"]["dashboard_portfolio"] = "Dashboard Portfolio Available"
        
        # Extract LinkedIn
        if 'LinkedIn' in contact_text:
            personal_info["linkedin"] = "LinkedIn Profile Available"
        
        return personal_info

    def _extract_sections_from_text(self, text: str) -> Dict[str, str]:
        """Extract sections from raw text based on headers"""
        sections = {}
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        # Define section headers to look for
        section_headers = {
            'CAREER PROFILE', 'KEY SKILLS', 'TECHNICAL SKILLS', 'EDUCATION', 
            'PROFESSIONAL EXPERIENCE', 'EXPERIENCE', 'UNIVERSITY PROJECT', 
            'PROJECTS', 'CERTIFICATIONS'
        }
        
        for line in lines:
            line_stripped = line.strip()
            line_upper = line_stripped.upper()
            
            # Check if this line is a section header
            if line_upper in section_headers:
                # Save previous section if exists
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                current_section = line_upper
                current_content = []
            elif current_section and line_stripped:  # Only add non-empty lines
                current_content.append(line_stripped)
        
        # Don't forget the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract technical skills from KEY SKILLS section"""
        skills = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and ':' in line:
                # Handle "Category: Description" format
                skill_desc = line.split(':', 1)[1].strip()
                if skill_desc:
                    skills.append(skill_desc)
            elif line and len(line) > 10:  # Standalone skill descriptions
                skills.append(line)
        
        return skills

    def _text_to_education_array(self, text: str) -> List[Dict[str, Any]]:
        """Convert education text to structured array with enhanced parsing"""
        import re
        
        education_list = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for degree lines (usually contain degree names)
            if any(degree_word in line.upper() for degree_word in ['MASTER', 'BACHELOR', 'DIPLOMA', 'CERTIFICATE', 'PHD', 'DOCTORATE']):
                education_entry = {
                    "degree": "",
                    "institution": "",
                    "location": "",
                    "duration": "",
                    "additional_info": "",
                    "gpa": "",
                    "honors": "",
                    "relevant_coursework": []
                }
                
                # Extract degree and dates from the same line
                date_pattern = r'(\w{3}\s\d{4}\s*[-–]\s*\w{3}\s\d{4}|\w{3}\s\d{4}\s*[-–]\s*\w{3}\s\d{4})'
                date_match = re.search(date_pattern, line)
                
                if date_match:
                    education_entry["duration"] = date_match.group(1)
                    degree_part = line.replace(date_match.group(1), '').strip()
                    education_entry["degree"] = degree_part
                else:
                    education_entry["degree"] = line
                
                # Look for institution in next line
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not any(degree_word in next_line.upper() for degree_word in ['MASTER', 'BACHELOR', 'DIPLOMA']):
                        # Extract GPA if present
                        gpa_match = re.search(r'GPA\s*[-:]?\s*([\d.]+\s*/\s*[\d.]+|[\d.]+%)', next_line)
                        if gpa_match:
                            education_entry["gpa"] = gpa_match.group(1)
                            institution_part = next_line.replace(gpa_match.group(0), '').strip().rstrip(',')
                            education_entry["institution"] = institution_part
                        else:
                            education_entry["institution"] = next_line
                        
                        # Extract location from institution name
                        education_entry["location"] = self._extract_location_from_text(education_entry["institution"])
                        
                        # Clean institution name by removing location
                        if education_entry["location"]:
                            clean_institution = education_entry["institution"]
                            clean_institution = clean_institution.replace(f", {education_entry['location']}", "")
                            clean_institution = clean_institution.replace(education_entry['location'], "")
                            education_entry["institution"] = clean_institution.strip().rstrip(',').strip()
                        
                        i += 1
                
                education_list.append(education_entry)
            
            i += 1
        
        return education_list

    def _extract_location_from_text(self, text: str) -> str:
        """Extract location from a text string (for institutions and companies)"""
        import re
        
        if not text:
            return ""
        
        # Australian location patterns - ordered by specificity (most specific first)
        location_patterns = [
            # Specific City, Country patterns (most specific first)
            r'(Sydney, Australia)',
            r'(Melbourne, Australia)', 
            r'(Brisbane, Australia)',
            r'(Perth, Australia)',
            r'(Adelaide, Australia)',
            r'(Darwin, Australia)',
            r'(Hobart, Australia)',
            r'(Canberra, Australia)',
            r'(Victoria, Australia)',  # Must come before general VIC pattern
            
            # Full state names with Australia
            r'((?:New South Wales|Victoria|Queensland|Western Australia|South Australia|Tasmania|Northern Territory|Australian Capital Territory), Australia)',
            
            # State abbreviations with Australia
            r'((?:NSW|QLD|WA|SA|TAS|NT|ACT), Australia)',
            
            # International locations
            r'(Kathmandu, Nepal)',
            r'(Nepal)',
            
            # General patterns (least specific, last)
            r'([A-Za-z\s]+, (?:New South Wales|Victoria|Queensland|Western Australia|South Australia|Tasmania|Northern Territory|Australian Capital Territory))',
            r'([A-Za-z\s]+, (?:NSW|QLD|WA|SA|TAS|NT|ACT))'  # VIC removed to avoid conflict with Victoria, Australia
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""

    def _text_to_experience_array(self, text: str) -> List[Dict[str, Any]]:
        """Convert experience text to structured array with enhanced parsing"""
        import re
        
        experience_list = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for job titles (lines with dates at the end)
            date_pattern = r'(\w{3}\s\d{4}\s*[-–]\s*\w{3}\s\d{4}|\w{3}\s\d{4}\s*[-–]\s*Present|\d{4}\s*[-–]\s*\d{4})'
            date_match = re.search(date_pattern, line)
            
            if date_match or (line and not line.startswith('•') and len(line) > 10):
                experience_entry = {
                    "position": "",
                    "company": "",
                    "location": "",
                    "duration": "",
                    "employment_type": "",
                    "achievements": [],
                    "responsibilities": []
                }
                
                if date_match:
                    experience_entry["duration"] = date_match.group(1).strip()
                    position_part = line.replace(date_match.group(0), '').strip()
                    experience_entry["position"] = position_part
                else:
                    experience_entry["position"] = line
                
                # Look for company in next line
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith('•') and not re.search(date_pattern, next_line):
                        experience_entry["company"] = next_line
                        
                        # Extract location from company name
                        experience_entry["location"] = self._extract_location_from_text(experience_entry["company"])
                        
                        # Clean company name by removing location
                        if experience_entry["location"]:
                            clean_company = experience_entry["company"]
                            clean_company = clean_company.replace(f", {experience_entry['location']}", "")
                            clean_company = clean_company.replace(experience_entry['location'], "")
                            experience_entry["company"] = clean_company.strip().rstrip(',').strip()
                        
                        i += 1
                
                # Collect achievements/responsibilities
                i += 1
                while i < len(lines):
                    achievement_line = lines[i].strip()
                    if achievement_line.startswith('•') or achievement_line.startswith('-'):
                        achievement_text = achievement_line[1:].strip()
                        if achievement_text:
                            experience_entry["achievements"].append(achievement_text)
                        i += 1
                    elif achievement_line and not re.search(date_pattern, achievement_line):
                        # Non-bullet point achievement
                        experience_entry["achievements"].append(achievement_line)
                        i += 1
                    else:
                        # End of this experience entry
                        i -= 1
                        break
                
                experience_list.append(experience_entry)
            
            i += 1
        
        return experience_list

    def _text_to_projects_array_with_context(self, text: str, education: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert projects text to structured array with education context for university/duration info"""
        import re
        
        projects_list = []
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Find the most recent degree (likely Master's for thesis work)
        master_degree = None
        bachelor_degree = None
        
        for edu in education:
            degree_text = edu.get('degree', '').lower()
            if 'master' in degree_text or 'masters' in degree_text:
                master_degree = edu
            elif 'bachelor' in degree_text:
                bachelor_degree = edu
        
        # Use master's degree as default context, fallback to bachelor's
        university_context = master_degree or bachelor_degree
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Look for project titles - either with colon or with grade info
            is_project_title = (
                (':' in line and ('Grade' in line or 'Thesis' in line)) or
                (re.search(r'\(Grade.*?\)', line)) or
                (re.search(r'\t.*?\d{4}', line))  # Tab followed by date
            )
            
            if is_project_title:
                project_entry = {
                    "name": "",
                    "duration": "",
                    "company": "",
                    "description": "",
                    "technologies": [],
                    "achievements": [],
                    "url": ""
                }
                
                # Extract project name and metadata
                if ':' in line:
                    # Format: "Project Name: Description (Grade: X/Y)"
                    name_part = line.split(':', 1)[0].strip()
                    rest_part = line.split(':', 1)[1].strip()
                    
                    project_entry["name"] = name_part
                    
                    # For thesis projects, use university context
                    if 'thesis' in name_part.lower() and university_context:
                        project_entry["company"] = university_context.get('institution', '')
                        project_entry["duration"] = university_context.get('duration', '')
                    
                    # Extract grade
                    grade_match = re.search(r'\(Grade[:\s]*([^)]+)\)', rest_part)
                    if grade_match:
                        project_entry["achievements"].append(f"Grade: {grade_match.group(1)}")
                        rest_part = re.sub(r'\(Grade[:\s]*[^)]+\)', '', rest_part).strip()
                    
                    # Any remaining part goes to description
                    if rest_part:
                        project_entry["description"] = rest_part
                
                else:
                    # Format: "Project Name (Grade: X/Y) \tDate"
                    # Extract date first
                    date_match = re.search(r'\t.*?(\w{3}\s\d{4})', line)
                    if date_match:
                        project_entry["duration"] = date_match.group(1)
                    
                    # Extract grade
                    grade_match = re.search(r'\(Grade.*?([\d/]+)\)', line)
                    if grade_match:
                        project_entry["achievements"].append(f"Grade: {grade_match.group(1)}")
                    
                    # Clean up name by removing grade and date parts
                    name = line
                    name = re.sub(r'\(Grade.*?\)', '', name)
                    name = re.sub(r'\t.*', '', name)
                    project_entry["name"] = name.strip()
                    
                    # For non-thesis projects with specific dates, try to match with education
                    if project_entry["duration"] and university_context:
                        # Check if project date falls within degree duration
                        project_entry["company"] = university_context.get('institution', '')
                
                # Collect project details from following lines until next project or end
                i += 1
                description_parts = []
                
                while i < len(lines):
                    next_line = lines[i]
                    
                    # Check if this is the start of another project
                    is_next_project = (
                        (':' in next_line and ('Grade' in next_line or 'Thesis' in next_line)) or
                        (re.search(r'\(Grade.*?\)', next_line)) or
                        (re.search(r'\t.*?\d{4}', next_line))
                    )
                    
                    if is_next_project:
                        break
                    else:
                        description_parts.append(next_line)
                        i += 1
                
                # Add description parts to the project
                if description_parts:
                    if project_entry["description"]:
                        project_entry["description"] += " " + " ".join(description_parts)
                    else:
                        project_entry["description"] = " ".join(description_parts)
                
                # Extract technologies from description
                tech_keywords = [
                    'Python', 'SQL', 'Machine Learning', 'Deep Learning', 'YOLOv8', 'YOLO',
                    'Logistic Regression', 'Random Forest', 'Pruning', 'TensorFlow', 
                    'PyTorch', 'Visualization', 'Data Analysis', 'Neural Networks',
                    'Computer Vision', 'Object Detection', 'Fine-tuning'
                ]
                
                for tech in tech_keywords:
                    if tech.lower() in project_entry["description"].lower():
                        if tech not in project_entry["technologies"]:
                            project_entry["technologies"].append(tech)
                
                projects_list.append(project_entry)
                
                # Don't increment i here as the while loop will handle it
                continue
            
            i += 1
        
        return projects_list

    def _text_to_certifications_array(self, text: str) -> List[Dict[str, Any]]:
        """Convert certifications text to structured array"""
        certifications_list = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and ',' in line:
                # Format: "Certification Name, Issuing Organization"
                parts = line.split(',', 1)
                if len(parts) == 2:
                    cert_entry = {
                        "name": parts[0].strip(),
                        "issuing_organization": parts[1].strip(),
                        "date_obtained": "",
                        "expiry_date": "",
                        "status": "Active",
                        "description": "",
                        "credential_id": "",
                        "url": ""
                    }
                    certifications_list.append(cert_entry)
            elif line:
                # Single line certification
                cert_entry = {
                    "name": line,
                    "issuing_organization": "",
                    "date_obtained": "",
                    "expiry_date": "",
                    "status": "Active",
                    "description": "",
                    "credential_id": "",
                    "url": ""
                }
                certifications_list.append(cert_entry)
        
        return certifications_list

    def _get_empty_structure(self) -> Dict[str, Any]:
        """Get empty CV structure with current timestamp"""
        structure = self.default_structure.copy()
        structure["saved_at"] = datetime.now().isoformat()
        return structure

    def save_structured_cv(self, cv_data: Dict[str, Any], file_path: str) -> bool:
        """Save structured CV to file"""
        try:
            cv_data["saved_at"] = datetime.now().isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cv_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully saved structured CV to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving structured CV: {e}")
            return False
    
    def load_structured_cv(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load structured CV from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return self.parse_cv_content(data)
            
        except Exception as e:
            logger.error(f"Error loading structured CV from {file_path}: {e}")
            return None
    
    def validate_cv_structure(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate CV structure and return validation report"""
        report = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "sections_found": [],
            "missing_required": []
        }
        
        required_sections = ["personal_information", "career_profile", "technical_skills"]
        
        for section in required_sections:
            if section not in cv_data or not cv_data[section]:
                report["missing_required"].append(section)
                report["valid"] = False
        
        for section in cv_data.keys():
            if section != "saved_at":
                report["sections_found"].append(section)
        
        # Check for empty critical fields
        if cv_data.get("personal_information", {}).get("name", "").strip() == "":
            report["warnings"].append("Name field is empty")
        
        if not cv_data.get("technical_skills", []):
            report["warnings"].append("No technical skills found")
        
        return report

    # Additional helper methods for backward compatibility...
    def _text_to_skills_array(self, text: str) -> List[str]:
        """Convert skills text to array"""
        skills = []
        for line in text.split('\n'):
            line = line.strip()
            if line and line.startswith('•'):
                skills.append(line[1:].strip())
        return skills


# Global instance
structured_cv_parser = StructuredCVParser()