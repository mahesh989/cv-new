"""
Minimal CV Analyzer

Provides realistic analysis for CVs with very limited information.
Prevents AI hallucination and provides honest, data-driven assessments.
"""

import logging
from typing import Dict, Any, List
import re

logger = logging.getLogger(__name__)


class MinimalCVAnalyzer:
    """
    Analyzes minimal CVs with realistic constraints to prevent AI hallucination.
    Provides honest assessments based only on available information.
    """
    
    def __init__(self):
        self.min_content_length = 200
        self.min_skills_threshold = 5
        self.min_experience_threshold = 1  # years
    
    def analyze_minimal_cv(self, cv_text: str, jd_text: str) -> Dict[str, Any]:
        """
        Analyze a minimal CV with realistic constraints.
        
        Args:
            cv_text: CV content
            jd_text: Job description content
            
        Returns:
            Dict with realistic analysis results
        """
        try:
            # Assess CV completeness
            completeness = self._assess_cv_completeness(cv_text)
            
            # Extract available information
            available_info = self._extract_available_info(cv_text)
            
            # Generate realistic constraints
            constraints = self._generate_realistic_constraints(completeness, available_info)
            
            # Analyze with constraints
            analysis = self._analyze_with_constraints(cv_text, jd_text, constraints)
            
            return {
                'is_minimal_cv': completeness['is_minimal'],
                'completeness_score': completeness['score'],
                'available_info': available_info,
                'constraints': constraints,
                'realistic_analysis': analysis,
                'warnings': self._generate_warnings(completeness, available_info)
            }
            
        except Exception as e:
            logger.error(f"❌ [MINIMAL_CV_ANALYZER] Analysis failed: {e}")
            return {
                'is_minimal_cv': True,
                'error': str(e),
                'realistic_analysis': self._get_default_minimal_analysis()
            }
    
    def _assess_cv_completeness(self, cv_text: str) -> Dict[str, Any]:
        """Assess how complete the CV is"""
        content_length = len(cv_text.strip())
        is_minimal = content_length < self.min_content_length
        
        # Count sections
        sections = self._count_sections(cv_text)
        
        # Count skills
        skills_count = self._count_skills(cv_text)
        
        # Count experience indicators
        experience_indicators = self._count_experience_indicators(cv_text)
        
        # Calculate completeness score
        score = 0
        if content_length >= self.min_content_length:
            score += 20
        if sections >= 3:
            score += 20
        if skills_count >= self.min_skills_threshold:
            score += 30
        if experience_indicators >= 2:
            score += 30
        
        return {
            'is_minimal': is_minimal,
            'score': score,
            'content_length': content_length,
            'sections_count': sections,
            'skills_count': skills_count,
            'experience_indicators': experience_indicators
        }
    
    def _extract_available_info(self, cv_text: str) -> Dict[str, Any]:
        """Extract what information is actually available"""
        return {
            'skills': self._extract_skills(cv_text),
            'experience': self._extract_experience(cv_text),
            'education': self._extract_education(cv_text),
            'achievements': self._extract_achievements(cv_text)
        }
    
    def _generate_realistic_constraints(self, completeness: Dict, available_info: Dict) -> Dict[str, Any]:
        """Generate realistic constraints based on available information"""
        constraints = {
            'max_technical_depth': 100,
            'max_skills_match': 100,
            'max_experience_score': 100,
            'max_leadership_score': 100,
            'max_seniority_score': 100,
            'requires_explicit_evidence': True
        }
        
        # Adjust based on completeness
        if completeness['is_minimal']:
            constraints.update({
                'max_technical_depth': 30,
                'max_skills_match': 40,
                'max_experience_score': 25,
                'max_leadership_score': 15,
                'max_seniority_score': 20
            })
        elif completeness['score'] < 50:
            constraints.update({
                'max_technical_depth': 50,
                'max_skills_match': 60,
                'max_experience_score': 40,
                'max_leadership_score': 25,
                'max_seniority_score': 35
            })
        
        # Adjust based on available information
        if len(available_info['skills']) < 3:
            constraints['max_skills_match'] = min(constraints['max_skills_match'], 30)
        
        if not available_info['experience']:
            constraints['max_experience_score'] = min(constraints['max_experience_score'], 20)
            constraints['max_seniority_score'] = min(constraints['max_seniority_score'], 15)
        
        if not available_info['achievements']:
            constraints['max_leadership_score'] = min(constraints['max_leadership_score'], 20)
        
        return constraints
    
    def _analyze_with_constraints(self, cv_text: str, jd_text: str, constraints: Dict) -> Dict[str, Any]:
        """Analyze CV with realistic constraints"""
        # Core competency analysis with constraints
        core_competency = self._analyze_core_competency(cv_text, jd_text, constraints)
        
        # Experience analysis with constraints
        experience_analysis = self._analyze_experience(cv_text, jd_text, constraints)
        
        # Skills analysis with constraints
        skills_analysis = self._analyze_skills(cv_text, jd_text, constraints)
        
        return {
            'core_competency': core_competency,
            'experience_analysis': experience_analysis,
            'skills_analysis': skills_analysis,
            'overall_assessment': self._generate_overall_assessment(core_competency, experience_analysis, skills_analysis)
        }
    
    def _analyze_core_competency(self, cv_text: str, jd_text: str, constraints: Dict) -> Dict[str, Any]:
        """Analyze core competency with realistic constraints"""
        # Extract skills from CV
        cv_skills = self._extract_skills(cv_text)
        
        # Extract required skills from JD
        jd_skills = self._extract_jd_skills(jd_text)
        
        # Calculate match percentage
        if not cv_skills:
            match_percentage = 0
        else:
            matches = set(cv_skills) & set(jd_skills)
            match_percentage = (len(matches) / len(jd_skills)) * 100 if jd_skills else 0
        
        # Apply constraints
        constrained_score = min(match_percentage, constraints['max_skills_match'])
        
        return {
            'technical_depth': min(25, constraints['max_technical_depth']),
            'core_skills_match_percentage': constrained_score,
            'technical_stack_fit_percentage': min(30, constraints['max_technical_depth']),
            'data_familiarity_score': min(20, constraints['max_technical_depth']),
            'available_skills': cv_skills,
            'required_skills': jd_skills,
            'skill_gaps': list(set(jd_skills) - set(cv_skills)) if jd_skills else [],
            'realistic_assessment': self._generate_skill_assessment(cv_skills, jd_skills)
        }
    
    def _analyze_experience(self, cv_text: str, jd_text: str, constraints: Dict) -> Dict[str, Any]:
        """Analyze experience with realistic constraints"""
        experience_info = self._extract_experience(cv_text)
        
        if not experience_info:
            return {
                'experience_alignment': 0,
                'experience_match_percentage': 0,
                'responsibility_fit_percentage': 0,
                'role_seniority': 0,
                'leadership_readiness_score': 0,
                'realistic_assessment': "No experience information available"
            }
        
        # Calculate basic scores with constraints
        base_score = min(20, constraints['max_experience_score'])
        
        return {
            'experience_alignment': base_score,
            'experience_match_percentage': base_score,
            'responsibility_fit_percentage': base_score,
            'role_seniority': min(15, constraints['max_seniority_score']),
            'leadership_readiness_score': min(10, constraints['max_leadership_score']),
            'available_experience': experience_info,
            'realistic_assessment': f"Limited experience information: {len(experience_info)} entries"
        }
    
    def _analyze_skills(self, cv_text: str, jd_text: str, constraints: Dict) -> Dict[str, Any]:
        """Analyze skills with realistic constraints"""
        cv_skills = self._extract_skills(cv_text)
        jd_skills = self._extract_jd_skills(jd_text)
        
        if not cv_skills:
            return {
                'technical_depth': 0,
                'core_skills_match_percentage': 0,
                'technical_stack_fit_percentage': 0,
                'data_familiarity_score': 0,
                'realistic_assessment': "No skills information available"
            }
        
        # Basic skill analysis
        base_score = min(25, constraints['max_technical_depth'])
        
        return {
            'technical_depth': base_score,
            'core_skills_match_percentage': min(30, constraints['max_skills_match']),
            'technical_stack_fit_percentage': base_score,
            'data_familiarity_score': base_score,
            'available_skills': cv_skills,
            'realistic_assessment': f"Limited skills information: {len(cv_skills)} skills listed"
        }
    
    def _generate_overall_assessment(self, core_competency: Dict, experience: Dict, skills: Dict) -> Dict[str, Any]:
        """Generate overall realistic assessment"""
        # Calculate average scores
        avg_core = (core_competency['technical_depth'] + 
                   core_competency['core_skills_match_percentage'] + 
                   core_competency['technical_stack_fit_percentage'] + 
                   core_competency['data_familiarity_score']) / 4
        
        avg_experience = (experience['experience_alignment'] + 
                        experience['experience_match_percentage'] + 
                        experience['responsibility_fit_percentage'] + 
                        experience['role_seniority'] + 
                        experience['leadership_readiness_score']) / 5
        
        avg_skills = (skills['technical_depth'] + 
                     skills['core_skills_match_percentage'] + 
                     skills['technical_stack_fit_percentage'] + 
                     skills['data_familiarity_score']) / 4
        
        overall_score = (avg_core + avg_experience + avg_skills) / 3
        
        return {
            'overall_score': overall_score,
            'core_competency_score': avg_core,
            'experience_score': avg_experience,
            'skills_score': avg_skills,
            'realistic_summary': self._generate_realistic_summary(overall_score, core_competency, experience, skills)
        }
    
    def _generate_realistic_summary(self, overall_score: float, core: Dict, experience: Dict, skills: Dict) -> str:
        """Generate realistic summary based on actual data"""
        if overall_score < 20:
            return "Very limited information available. CV needs significant development to be competitive."
        elif overall_score < 40:
            return "Minimal information provided. Consider adding more details about experience, skills, and achievements."
        elif overall_score < 60:
            return "Basic information available. Some development needed to improve competitiveness."
        else:
            return "Adequate information for basic analysis. Consider adding more specific details."
    
    def _generate_warnings(self, completeness: Dict, available_info: Dict) -> List[str]:
        """Generate warnings about limitations"""
        warnings = []
        
        if completeness['is_minimal']:
            warnings.append("CV content is very limited - analysis will be constrained")
        
        if len(available_info['skills']) < 3:
            warnings.append("Very few skills listed - consider adding more technical skills")
        
        if not available_info['experience']:
            warnings.append("No experience information - consider adding work experience or projects")
        
        if not available_info['achievements']:
            warnings.append("No achievements listed - consider adding quantified accomplishments")
        
        return warnings
    
    def _get_default_minimal_analysis(self) -> Dict[str, Any]:
        """Get default analysis for minimal CVs"""
        return {
            'core_competency': {
                'technical_depth': 15,
                'core_skills_match_percentage': 20,
                'technical_stack_fit_percentage': 15,
                'data_familiarity_score': 10
            },
            'experience_analysis': {
                'experience_alignment': 10,
                'experience_match_percentage': 10,
                'responsibility_fit_percentage': 10,
                'role_seniority': 5,
                'leadership_readiness_score': 5
            },
            'skills_analysis': {
                'technical_depth': 15,
                'core_skills_match_percentage': 20,
                'technical_stack_fit_percentage': 15,
                'data_familiarity_score': 10
            },
            'overall_assessment': {
                'overall_score': 12.5,
                'realistic_summary': "Very limited information available. CV needs significant development."
            }
        }
    
    # Helper methods
    def _count_sections(self, cv_text: str) -> int:
        """Count CV sections"""
        sections = 0
        text_lower = cv_text.lower()
        if 'experience' in text_lower or 'work' in text_lower:
            sections += 1
        if 'skills' in text_lower or 'technical' in text_lower:
            sections += 1
        if 'education' in text_lower or 'degree' in text_lower:
            sections += 1
        if 'projects' in text_lower:
            sections += 1
        return sections
    
    def _count_skills(self, cv_text: str) -> int:
        """Count skills in CV"""
        skills = self._extract_skills(cv_text)
        return len(skills)
    
    def _count_experience_indicators(self, cv_text: str) -> int:
        """Count experience indicators"""
        indicators = 0
        text_lower = cv_text.lower()
        if 'experience' in text_lower:
            indicators += 1
        if 'work' in text_lower or 'employment' in text_lower:
            indicators += 1
        if 'years' in text_lower:
            indicators += 1
        return indicators
    
    def _extract_skills(self, cv_text: str) -> List[str]:
        """Extract skills from CV"""
        skills = []
        text_lower = cv_text.lower()
        
        # Common technical skills
        tech_skills = ['python', 'sql', 'excel', 'java', 'javascript', 'html', 'css', 'react', 'node', 'git']
        for skill in tech_skills:
            if skill in text_lower:
                skills.append(skill.title())
        
        # Extract from bullet points
        bullet_patterns = [r'•\s*([^•\n]+)', r'-\s*([^-\n]+)', r'\*\s*([^*\n]+)']
        for pattern in bullet_patterns:
            matches = re.findall(pattern, cv_text)
            for match in matches:
                if len(match.strip()) < 50:  # Likely a skill
                    skills.append(match.strip())
        
        return list(set(skills))  # Remove duplicates
    
    def _extract_experience(self, cv_text: str) -> List[str]:
        """Extract experience information"""
        experience = []
        text_lower = cv_text.lower()
        
        if 'experience' in text_lower:
            # Extract experience section
            exp_section = re.search(r'experience[^a-z]*(.*?)(?=\n\n|\n[A-Z]|$)', cv_text, re.IGNORECASE | re.DOTALL)
            if exp_section:
                exp_text = exp_section.group(1)
                # Extract job titles or roles
                job_patterns = [
                    r'(?:Senior|Junior|Lead|Manager|Director|Analyst|Developer|Engineer|Data\s+Analyst)',
                    r'(?:Software\s+Engineer|Project\s+Manager|Business\s+Analyst)'
                ]
                for pattern in job_patterns:
                    matches = re.findall(pattern, exp_text, re.IGNORECASE)
                    experience.extend(matches)
        
        return list(set(experience))
    
    def _extract_education(self, cv_text: str) -> List[str]:
        """Extract education information"""
        education = []
        text_lower = cv_text.lower()
        
        if 'education' in text_lower or 'degree' in text_lower:
            # Extract degrees
            degree_patterns = [
                r'(?:Bachelor|Master|PhD|Doctorate|BSc|MSc|MBA|BEng|MEng)',
                r'(?:Bachelor of|Master of|Doctor of)'
            ]
            for pattern in degree_patterns:
                matches = re.findall(pattern, cv_text, re.IGNORECASE)
                education.extend(matches)
        
        return list(set(education))
    
    def _extract_achievements(self, cv_text: str) -> List[str]:
        """Extract achievements"""
        achievements = []
        text_lower = cv_text.lower()
        
        if 'achievement' in text_lower or 'accomplishment' in text_lower:
            # Extract achievement section
            ach_section = re.search(r'(?:achievement|accomplishment)[^a-z]*(.*?)(?=\n\n|\n[A-Z]|$)', cv_text, re.IGNORECASE | re.DOTALL)
            if ach_section:
                ach_text = ach_section.group(1)
                # Extract bullet points
                bullet_patterns = [r'•\s*([^•\n]+)', r'-\s*([^-\n]+)', r'\*\s*([^*\n]+)']
                for pattern in bullet_patterns:
                    matches = re.findall(pattern, ach_text)
                    achievements.extend([match.strip() for match in matches])
        
        return achievements
    
    def _extract_jd_skills(self, jd_text: str) -> List[str]:
        """Extract required skills from job description"""
        skills = []
        text_lower = jd_text.lower()
        
        # Common technical skills
        tech_skills = ['python', 'sql', 'excel', 'java', 'javascript', 'html', 'css', 'react', 'node', 'git', 'tableau', 'powerbi']
        for skill in tech_skills:
            if skill in text_lower:
                skills.append(skill.title())
        
        return list(set(skills))
    
    def _generate_skill_assessment(self, cv_skills: List[str], jd_skills: List[str]) -> str:
        """Generate realistic skill assessment"""
        if not cv_skills:
            return "No skills information available in CV"
        
        if not jd_skills:
            return f"CV lists {len(cv_skills)} skills but no specific requirements found in job description"
        
        matches = set(cv_skills) & set(jd_skills)
        if matches:
            return f"CV has {len(matches)} matching skills: {', '.join(matches)}"
        else:
            return f"CV has {len(cv_skills)} skills but none match job requirements"


# Global instance
minimal_cv_analyzer = MinimalCVAnalyzer()
