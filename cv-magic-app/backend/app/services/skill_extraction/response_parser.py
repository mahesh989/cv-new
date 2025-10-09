"""
Response Parser for Skill Extraction

Parses AI responses and extracts skills into structured format
"""

import re
import ast
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SkillExtractionParser:
    """Parser for skill extraction AI responses"""
    
    @staticmethod
    def parse_response(response_text: str, document_type: str) -> Dict[str, any]:
        """
        Parse AI response and extract skills
        
        Args:
            response_text: Raw AI response text
            document_type: Type of document analyzed ("CV" or "JD")
            
        Returns:
            Dictionary containing extracted skills and metadata
        """
        logger.info(f"🔍 [{document_type.upper()}] Starting response parsing...")
        logger.info(f"🔍 [{document_type.upper()}] Raw response preview: {response_text[:500]}...")
        if document_type.upper() == "CV":
            logger.info(f"🔍 [{document_type.upper()}] FULL CV RESPONSE: {response_text}")
        
        # Initialize skill lists
        soft_skills = []
        technical_skills = []
        domain_keywords = []
        
        try:
            # Multiple parsing strategies for different AI models
            # Strategy 1: Python list variable assignments (original format for GPT-4o Mini)
            soft_skills = SkillExtractionParser._extract_python_list(response_text, "SOFT_SKILLS", document_type)
            technical_skills = SkillExtractionParser._extract_python_list(response_text, "TECHNICAL_SKILLS", document_type)  
            domain_keywords = SkillExtractionParser._extract_python_list(response_text, "DOMAIN_KEYWORDS", document_type)
            
            # Strategy 2: If no Python lists found, try markdown format (GPT-3.5, Claude, DeepSeek)
            if not soft_skills and not technical_skills and not domain_keywords:
                logger.info(f"🔄 [{document_type.upper()}] Python format not found, trying markdown format...")
                soft_skills = SkillExtractionParser._extract_markdown_list(response_text, "SOFT SKILLS", document_type)
                technical_skills = SkillExtractionParser._extract_markdown_list(response_text, "TECHNICAL SKILLS", document_type)
                domain_keywords = SkillExtractionParser._extract_markdown_list(response_text, "DOMAIN KEYWORDS", document_type)
            
            # Strategy 3: If still no results, try section headers format
            if not soft_skills and not technical_skills and not domain_keywords:
                logger.info(f"🔄 [{document_type.upper()}] Markdown format not found, trying section headers...")
                soft_skills = SkillExtractionParser._extract_section_list(response_text, ["Soft Skills", "SOFT SKILLS"], document_type)
                technical_skills = SkillExtractionParser._extract_section_list(response_text, ["Technical Skills", "TECHNICAL SKILLS"], document_type)
                domain_keywords = SkillExtractionParser._extract_section_list(response_text, ["Domain Keywords", "DOMAIN KEYWORDS"], document_type)
            
            # Log which parsing strategy worked
            if soft_skills or technical_skills or domain_keywords:
                total_skills = len(soft_skills) + len(technical_skills) + len(domain_keywords)
                logger.info(f"✅ [{document_type.upper()}] Successfully extracted {total_skills} total skills using multi-format parser")
            
            # Validate and clean extracted skills
            soft_skills = SkillExtractionParser._validate_and_clean_skills(soft_skills, "soft_skills", document_type)
            technical_skills = SkillExtractionParser._validate_and_clean_skills(technical_skills, "technical_skills", document_type)
            domain_keywords = SkillExtractionParser._validate_and_clean_skills(domain_keywords, "domain_keywords", document_type)
            
            # Log parsing results
            logger.info(f"📊 [{document_type.upper()}] Parsing completed:")
            logger.info(f"   Soft Skills ({len(soft_skills)}): {soft_skills[:3]}{'...' if len(soft_skills) > 3 else ''}")
            logger.info(f"   Technical Skills ({len(technical_skills)}): {technical_skills[:3]}{'...' if len(technical_skills) > 3 else ''}")
            logger.info(f"   Domain Keywords ({len(domain_keywords)}): {domain_keywords[:3]}{'...' if len(domain_keywords) > 3 else ''}")
            
            # Validate results
            if not soft_skills and not technical_skills and not domain_keywords:
                logger.error(f"❌ [{document_type.upper()}] No skills extracted - parsing failed")
                raise ValueError(f"Failed to extract any skills from {document_type} response")
            
            return {
                "soft_skills": soft_skills,
                "technical_skills": technical_skills, 
                "domain_keywords": domain_keywords,
                "raw_response": response_text,
                "parsing_success": True
            }
            
        except Exception as e:
            logger.error(f"❌ [{document_type.upper()}] Parsing error: {str(e)}")
            return {
                "soft_skills": [],
                "technical_skills": [],
                "domain_keywords": [],
                "raw_response": response_text,
                "parsing_success": False,
                "error": str(e)
            }
    
    @staticmethod
    def _extract_python_list(text: str, variable_name: str, document_type: str) -> List[str]:
        """
        Extract Python list from variable assignment
        
        Args:
            text: Response text to search
            variable_name: Variable name to look for (e.g., "SOFT_SKILLS")
            document_type: Type of document for logging
            
        Returns:
            List of extracted skills
        """
        try:
            # Look for variable assignment pattern like SOFT_SKILLS = ["skill1", "skill2"]
            pattern = rf'{variable_name}\s*=\s*(\[.*?\])'
            match = re.search(pattern, text, re.DOTALL)
            
            if match:
                list_string = match.group(1)
                # Use ast.literal_eval to safely parse the Python list
                skill_list = ast.literal_eval(list_string)
                logger.debug(f"🔍 [{document_type.upper()}] Extracted {variable_name}: {len(skill_list)} items")
                
                # Clean and validate the list
                cleaned_list = SkillExtractionParser._clean_skill_list(skill_list)
                return cleaned_list
            else:
                logger.warning(f"⚠️ [{document_type.upper()}] No {variable_name} variable found in response")
                return []
                
        except Exception as e:
            logger.error(f"❌ [{document_type.upper()}] Failed to extract {variable_name}: {e}")
            return []
    
    @staticmethod
    def _extract_markdown_list(text: str, section_name: str, document_type: str) -> List[str]:
        """
        Extract skills from markdown format like:
        ## SOFT SKILLS:
        **EXPLICIT (directly stated):**
        - Communication
        - Leadership
        
        Args:
            text: Response text to search
            section_name: Section name to look for (e.g., "SOFT SKILLS")
            document_type: Type of document for logging
            
        Returns:
            List of extracted skills
        """
        try:
            # Look for markdown sections with hash headers and bullet points
            # Pattern matches: ## SECTION_NAME: followed by optional **EXPLICIT** and bullet points
            pattern = rf'## {re.escape(section_name)}:\s*\n(?:\*\*[^*]+\*\*\s*\n)?((?:- .+\n?)+)'
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            if match:
                skills_text = match.group(1)
                # Extract individual skills from bullet points
                skill_lines = re.findall(r'- (.+)', skills_text)
                skills = [skill.strip() for skill in skill_lines if skill.strip()]
                logger.debug(f"🔍 [{document_type.upper()}] Extracted {section_name} (markdown): {len(skills)} items")
                return skills
            else:
                # Fallback: try the old format with double asterisks
                pattern_old = rf'\*\*{re.escape(section_name)}:\*\*\s*\n((?:- .+\n?)+)'
                match_old = re.search(pattern_old, text, re.IGNORECASE | re.MULTILINE)
                
                if match_old:
                    skills_text = match_old.group(1)
                    skill_lines = re.findall(r'- (.+)', skills_text)
                    skills = [skill.strip() for skill in skill_lines if skill.strip()]
                    logger.debug(f"🔍 [{document_type.upper()}] Extracted {section_name} (old markdown): {len(skills)} items")
                    return skills
                else:
                    logger.debug(f"🔍 [{document_type.upper()}] No {section_name} markdown section found")
                    return []
                
        except Exception as e:
            logger.error(f"❌ [{document_type.upper()}] Failed to extract {section_name} (markdown): {e}")
            return []
    
    @staticmethod
    def _extract_section_list(text: str, section_names: List[str], document_type: str) -> List[str]:
        """
        Extract skills from general section format with various headers
        
        Args:
            text: Response text to search
            section_names: List of possible section names to look for
            document_type: Type of document for logging
            
        Returns:
            List of extracted skills
        """
        try:
            for section_name in section_names:
                # Try multiple patterns for section headers
                patterns = [
                    rf'## {re.escape(section_name)}:\s*\n(?:\*\*[^*]+\*\*\s*\n)?((?:- .+\n?)+)',  # Hash header with optional **EXPLICIT** and bullets
                    rf'## {re.escape(section_name)}:\s*\n((?:- .+\n?)+)',  # Hash header with bullets
                    rf'{re.escape(section_name)}:\s*\n((?:- .+\n?)+)',  # Header with bullets
                    rf'{re.escape(section_name)}\s*\n((?:- .+\n?)+)',   # Header without colon
                    rf'{re.escape(section_name)}:\s*\n((?:\* .+\n?)+)', # Header with asterisks
                    rf'{re.escape(section_name)}\s*\n((?:\* .+\n?)+)',  # Header with asterisks, no colon
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                    if match:
                        skills_text = match.group(1)
                        # Extract individual skills from bullet points (both - and *)
                        skill_lines = re.findall(r'[*-] (.+)', skills_text)
                        skills = [skill.strip() for skill in skill_lines if skill.strip()]
                        if skills:
                            logger.debug(f"🔍 [{document_type.upper()}] Extracted {section_name} (section): {len(skills)} items")
                            return skills
            
            logger.debug(f"🔍 [{document_type.upper()}] No section format found for {section_names}")
            return []
                
        except Exception as e:
            logger.error(f"❌ [{document_type.upper()}] Failed to extract section {section_names}: {e}")
            return []
    
    @staticmethod
    def _clean_skill_list(skill_list: List) -> List[str]:
        """
        Clean and validate skill list
        
        Args:
            skill_list: Raw skill list from AI response
            
        Returns:
            Cleaned list of skills
        """
        cleaned = []
        for skill in skill_list:
            if isinstance(skill, str):
                skill = skill.strip()
                if skill and skill.lower() not in ['n/a', 'none', '']:
                    cleaned.append(skill)
        
        return cleaned
    
    @staticmethod
    def format_for_logging(skills_data: Dict, document_type: str, company_name: str = "Company") -> str:
        """
        Format skills data for logging in the required template format
        
        Args:
            skills_data: Extracted skills data
            document_type: Type of document ("CV" or "JD")
            company_name: Company name for logging
            
        Returns:
            Formatted string for logging
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        tag = f"{document_type.upper()}_CLAUDE_ANALYSIS" if document_type == "CV" else f"{document_type.upper()}_CLAUDE_ANALYSIS"
        
        formatted_output = f"""================================================================================
[{timestamp}] [{tag}] OUTPUT:
{skills_data.get('raw_response', '')}
================================================================================"""
        
        return formatted_output
    
    @staticmethod
    def _validate_and_clean_skills(skills: List[str], skill_type: str, document_type: str) -> List[str]:
        """
        Validate and clean extracted skills with improved error handling
        
        Args:
            skills: List of extracted skills
            skill_type: Type of skills (soft_skills, technical_skills, domain_keywords)
            document_type: Type of document for logging
            
        Returns:
            Cleaned and validated list of skills
        """
        if not skills:
            return []
        
        cleaned_skills = []
        invalid_skills = []
        
        for skill in skills:
            if not isinstance(skill, str):
                invalid_skills.append(str(skill))
                continue
                
            # Clean the skill
            cleaned_skill = skill.strip()
            
            # Skip empty or very short skills
            if len(cleaned_skill) < 2:
                invalid_skills.append(cleaned_skill)
                continue
                
            # Skip skills that are too long (likely parsing errors)
            if len(cleaned_skill) > 100:
                invalid_skills.append(cleaned_skill)
                continue
                
            # Skip common non-skill words
            non_skill_words = {
                'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
                'above', 'below', 'between', 'among', 'within', 'without', 'upon', 'across'
            }
            
            if cleaned_skill.lower() in non_skill_words:
                invalid_skills.append(cleaned_skill)
                continue
                
            cleaned_skills.append(cleaned_skill)
        
        if invalid_skills:
            logger.warning(f"⚠️ [{document_type.upper()}] Filtered out {len(invalid_skills)} invalid {skill_type}: {invalid_skills[:5]}{'...' if len(invalid_skills) > 5 else ''}")
        
        logger.info(f"✅ [{document_type.upper()}] Validated {skill_type}: {len(cleaned_skills)} valid skills")
        return cleaned_skills
