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
        logger.debug(f"🔍 [{document_type.upper()}] Raw response preview: {response_text[:500]}...")
        
        # Initialize skill lists
        soft_skills = []
        technical_skills = []
        domain_keywords = []
        
        try:
            # Primary parsing strategy: Look for Python list variable assignments
            soft_skills = SkillExtractionParser._extract_python_list(response_text, "SOFT_SKILLS", document_type)
            technical_skills = SkillExtractionParser._extract_python_list(response_text, "TECHNICAL_SKILLS", document_type)  
            domain_keywords = SkillExtractionParser._extract_python_list(response_text, "DOMAIN_KEYWORDS", document_type)
            
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
