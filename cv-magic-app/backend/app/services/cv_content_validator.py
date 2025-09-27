"""
CV Content Validator

Validates CV content to prevent AI hallucination and ensure analysis is based only on actual content.
"""

import logging
from typing import Dict, List, Any, Optional
import re

logger = logging.getLogger(__name__)


class CVContentValidator:
    """Validates CV content to ensure AI analysis is data-driven"""
    
    def __init__(self):
        self.min_content_length = 200  # Minimum characters for meaningful CV
        self.required_sections = ['experience', 'skills', 'education']
    
    def validate_cv_content(self, cv_text: str) -> Dict[str, Any]:
        """
        Validate CV content and extract available information
        
        Args:
            cv_text: CV text content
            
        Returns:
            Dict with validation results and content analysis
        """
        try:
            # Basic content validation
            content_length = len(cv_text.strip())
            is_minimal_cv = content_length < self.min_content_length
            
            # Extract available sections
            available_sections = self._extract_sections(cv_text)
            
            # Extract experience information
            experience_info = self._extract_experience_info(cv_text)
            
            # Extract skills information
            skills_info = self._extract_skills_info(cv_text)
            
            # Extract education information
            education_info = self._extract_education_info(cv_text)
            
            # Calculate content completeness
            completeness_score = self._calculate_completeness_score(
                available_sections, experience_info, skills_info, education_info
            )
            
            # Determine analysis constraints
            analysis_constraints = self._determine_analysis_constraints(
                is_minimal_cv, completeness_score, experience_info
            )
            
            return {
                'is_valid': True,
                'content_length': content_length,
                'is_minimal_cv': is_minimal_cv,
                'available_sections': available_sections,
                'experience_info': experience_info,
                'skills_info': skills_info,
                'education_info': education_info,
                'completeness_score': completeness_score,
                'analysis_constraints': analysis_constraints,
                'warnings': self._generate_warnings(is_minimal_cv, completeness_score)
            }
            
        except Exception as e:
            logger.error(f"❌ [CV_VALIDATOR] Content validation failed: {e}")
            return {
                'is_valid': False,
                'error': str(e),
                'analysis_constraints': {
                    'max_seniority_score': 20,
                    'max_experience_score': 20,
                    'max_leadership_score': 10,
                    'requires_explicit_evidence': True
                }
            }
    
    def _extract_sections(self, cv_text: str) -> List[str]:
        """Extract available sections from CV"""
        sections = []
        text_lower = cv_text.lower()
        
        if 'experience' in text_lower or 'work' in text_lower or 'employment' in text_lower:
            sections.append('experience')
        if 'skills' in text_lower or 'technical' in text_lower:
            sections.append('skills')
        if 'education' in text_lower or 'degree' in text_lower or 'university' in text_lower:
            sections.append('education')
        if 'projects' in text_lower:
            sections.append('projects')
        if 'achievements' in text_lower or 'accomplishments' in text_lower:
            sections.append('achievements')
            
        return sections
    
    def _extract_experience_info(self, cv_text: str) -> Dict[str, Any]:
        """Extract experience information from CV"""
        experience_info = {
            'has_experience_section': False,
            'explicit_years': 0,
            'explicit_roles': [],
            'explicit_achievements': [],
            'explicit_leadership': [],
            'explicit_management': []
        }
        
        # Check for experience section
        if 'experience' in cv_text.lower():
            experience_info['has_experience_section'] = True
            
            # Extract years of experience (basic pattern matching)
            year_patterns = [
                r'(\d+)\s*years?\s*(?:of\s*)?experience',
                r'(\d+)\s*years?\s*in\s*\w+',
                r'(\d{4})\s*[-–]\s*(\d{4}|\w+)',  # Date ranges
            ]
            
            for pattern in year_patterns:
                matches = re.findall(pattern, cv_text, re.IGNORECASE)
                if matches:
                    try:
                        years = [int(match[0]) if isinstance(match, tuple) else int(match) for match in matches]
                        experience_info['explicit_years'] = max(years)
                    except:
                        pass
            
            # Extract explicit roles
            role_patterns = [
                r'(?:Senior|Junior|Lead|Manager|Director|Analyst|Developer|Engineer)',
                r'(?:Data\s+Analyst|Software\s+Engineer|Project\s+Manager)'
            ]
            
            for pattern in role_patterns:
                matches = re.findall(pattern, cv_text, re.IGNORECASE)
                experience_info['explicit_roles'].extend(matches)
            
            # Check for leadership indicators
            leadership_indicators = [
                'managed', 'led', 'supervised', 'directed', 'oversaw', 'team lead',
                'team leader', 'managed team', 'led team', 'supervised team'
            ]
            
            for indicator in leadership_indicators:
                if indicator in cv_text.lower():
                    experience_info['explicit_leadership'].append(indicator)
        
        return experience_info
    
    def _extract_skills_info(self, cv_text: str) -> Dict[str, Any]:
        """Extract skills information from CV"""
        skills_info = {
            'has_skills_section': False,
            'explicit_skills': [],
            'technical_skills': [],
            'soft_skills': []
        }
        
        if 'skills' in cv_text.lower() or 'technical' in cv_text.lower():
            skills_info['has_skills_section'] = True
            
            # Extract skills from bullet points or lists
            skill_patterns = [
                r'•\s*([^•\n]+)',  # Bullet points
                r'-\s*([^-\n]+)',  # Dashes
                r'\*\s*([^*\n]+)',  # Asterisks
            ]
            
            for pattern in skill_patterns:
                matches = re.findall(pattern, cv_text)
                skills_info['explicit_skills'].extend([match.strip() for match in matches])
        
        return skills_info
    
    def _extract_education_info(self, cv_text: str) -> Dict[str, Any]:
        """Extract education information from CV"""
        education_info = {
            'has_education_section': False,
            'explicit_degrees': [],
            'explicit_institutions': []
        }
        
        if 'education' in cv_text.lower() or 'degree' in cv_text.lower():
            education_info['has_education_section'] = True
            
            # Extract degrees
            degree_patterns = [
                r'(?:Bachelor|Master|PhD|Doctorate|BSc|MSc|MBA|BEng|MEng)',
                r'(?:Bachelor of|Master of|Doctor of)'
            ]
            
            for pattern in degree_patterns:
                matches = re.findall(pattern, cv_text, re.IGNORECASE)
                education_info['explicit_degrees'].extend(matches)
        
        return education_info
    
    def _calculate_completeness_score(self, sections: List[str], experience_info: Dict, 
                                    skills_info: Dict, education_info: Dict) -> int:
        """Calculate content completeness score (0-100)"""
        score = 0
        
        # Section presence (40 points)
        score += len(sections) * 10
        
        # Experience quality (30 points)
        if experience_info['has_experience_section']:
            score += 15
            if experience_info['explicit_years'] > 0:
                score += 15
        
        # Skills quality (20 points)
        if skills_info['has_skills_section']:
            score += 10
            if len(skills_info['explicit_skills']) > 0:
                score += 10
        
        # Education quality (10 points)
        if education_info['has_education_section']:
            score += 10
        
        return min(score, 100)
    
    def _determine_analysis_constraints(self, is_minimal_cv: bool, completeness_score: int, 
                                      experience_info: Dict) -> Dict[str, Any]:
        """Determine analysis constraints based on content quality"""
        constraints = {
            'max_seniority_score': 100,
            'max_experience_score': 100,
            'max_leadership_score': 100,
            'requires_explicit_evidence': True
        }
        
        if is_minimal_cv or completeness_score < 30:
            constraints.update({
                'max_seniority_score': 20,
                'max_experience_score': 20,
                'max_leadership_score': 10,
                'requires_explicit_evidence': True
            })
        elif completeness_score < 60:
            constraints.update({
                'max_seniority_score': 50,
                'max_experience_score': 50,
                'max_leadership_score': 30,
                'requires_explicit_evidence': True
            })
        
        # Adjust based on explicit experience
        if experience_info['explicit_years'] == 0:
            constraints['max_seniority_score'] = min(constraints['max_seniority_score'], 25)
            constraints['max_experience_score'] = min(constraints['max_experience_score'], 25)
        
        if not experience_info['explicit_leadership']:
            constraints['max_leadership_score'] = min(constraints['max_leadership_score'], 20)
        
        return constraints
    
    def _generate_warnings(self, is_minimal_cv: bool, completeness_score: int) -> List[str]:
        """Generate warnings about content limitations"""
        warnings = []
        
        if is_minimal_cv:
            warnings.append("CV content is minimal - analysis will be limited")
        
        if completeness_score < 30:
            warnings.append("CV lacks essential sections - scores will be low")
        
        if completeness_score < 60:
            warnings.append("CV is incomplete - analysis may be inaccurate")
        
        return warnings


# Global instance
cv_content_validator = CVContentValidator()
