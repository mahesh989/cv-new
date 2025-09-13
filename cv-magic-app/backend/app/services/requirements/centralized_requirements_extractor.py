"""
Centralized Requirements Extractor

Addresses the requirements extraction consistency issue by providing:
1. Single source of truth for parsing job requirements
2. Standardized requirement categorization
3. Priority-based requirement weighting
4. Consistent skill parsing across all components
"""

import logging
import re
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RequirementPriority(Enum):
    REQUIRED = "required"
    PREFERRED = "preferred" 
    NICE_TO_HAVE = "nice_to_have"


class RequirementType(Enum):
    TECHNICAL_SKILL = "technical_skill"
    SOFT_SKILL = "soft_skill"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    CERTIFICATION = "certification"
    DOMAIN_KNOWLEDGE = "domain_knowledge"
    LANGUAGE = "language"
    TOOL = "tool"


@dataclass
class ParsedRequirement:
    """Single parsed requirement with metadata"""
    text: str
    requirement_type: RequirementType
    priority: RequirementPriority
    category: str  # For grouping (e.g., "programming_languages", "databases")
    years_experience: Optional[int] = None
    proficiency_level: Optional[str] = None  # "basic", "intermediate", "advanced", "expert"


@dataclass
class RequirementsExtraction:
    """Complete requirements extraction results"""
    required_skills: List[ParsedRequirement]
    preferred_skills: List[ParsedRequirement] 
    nice_to_have_skills: List[ParsedRequirement]
    
    # Categorized lists for easy access
    technical_skills: List[str]
    soft_skills: List[str]
    domain_keywords: List[str]
    tools_and_platforms: List[str]
    
    # Experience requirements
    years_experience_required: int
    education_requirements: List[str]
    certifications: List[str]
    
    # Metadata
    total_requirements: int
    priority_weights: Dict[str, float]


class CentralizedRequirementsExtractor:
    """
    Centralized requirements extractor ensuring consistency across all analysis components
    """
    
    def __init__(self):
        self._initialize_skill_patterns()
        self._initialize_priority_keywords()
        self._initialize_category_mappings()
    
    def _initialize_skill_patterns(self):
        """Initialize regex patterns for different skill types"""
        
        # Technical skills patterns
        self.technical_patterns = {
            "programming_languages": [
                r'\b(?i)(python|java|javascript|typescript|c\+\+|c#|ruby|php|go|rust|scala|kotlin|swift)\b',
                r'\b(?i)(html|css|sql|r|matlab|stata)\b'
            ],
            "frameworks_libraries": [
                r'\b(?i)(react|angular|vue|django|flask|spring|express|bootstrap)\b',
                r'\b(?i)(tensorflow|pytorch|pandas|numpy|scikit-learn)\b'
            ],
            "databases": [
                r'\b(?i)(mysql|postgresql|mongodb|oracle|sql server|sqlite|redis|cassandra)\b'
            ],
            "cloud_platforms": [
                r'\b(?i)(aws|azure|google cloud|gcp|cloud computing)\b'
            ],
            "tools_platforms": [
                r'\b(?i)(docker|kubernetes|jenkins|git|github|gitlab|jira|confluence)\b',
                r'\b(?i)(tableau|power bi|excel|salesforce|sap|workday)\b'
            ]
        }
        
        # Soft skills patterns
        self.soft_skills_patterns = [
            r'\b(?i)(leadership|management|communication|teamwork|collaboration)\b',
            r'\b(?i)(problem.solving|analytical.thinking|critical.thinking)\b',
            r'\b(?i)(adaptability|flexibility|learning.agility|curiosity)\b',
            r'\b(?i)(organized|organisation|time.management|multitasking)\b',
            r'\b(?i)(presentation|public.speaking|negotiation|interpersonal)\b'
        ]
        
        # Domain knowledge patterns
        self.domain_patterns = [
            r'\b(?i)(data.science|machine.learning|artificial.intelligence|ai|ml)\b',
            r'\b(?i)(financial.analysis|accounting|investment|banking|fintech)\b',
            r'\b(?i)(digital.marketing|seo|sem|social.media|content.marketing)\b',
            r'\b(?i)(project.management|agile|scrum|kanban|waterfall)\b',
            r'\b(?i)(cybersecurity|information.security|compliance|governance)\b'
        ]
        
        # Experience patterns
        self.experience_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience',
            r'minimum\s+(\d+)\s+(?:years?|yrs?)',
            r'at\s+least\s+(\d+)\s+(?:years?|yrs?)',
            r'(\d+)-(\d+)\s+(?:years?|yrs?)\s+(?:of\s+)?experience'
        ]
    
    def _initialize_priority_keywords(self):
        """Initialize keywords that indicate requirement priority"""
        
        self.priority_indicators = {
            RequirementPriority.REQUIRED: [
                "required", "must have", "essential", "mandatory", "critical",
                "minimum", "necessary", "key requirement", "basic requirement"
            ],
            RequirementPriority.PREFERRED: [
                "preferred", "desired", "ideal", "strong preference", "advantage",
                "plus", "beneficial", "valuable", "welcome", "appreciated"
            ],
            RequirementPriority.NICE_TO_HAVE: [
                "nice to have", "bonus", "additional", "extra", "optional",
                "would be great", "icing on the cake", "cherry on top"
            ]
        }
    
    def _initialize_category_mappings(self):
        """Initialize mappings from skills to categories"""
        
        self.skill_categories = {
            # Programming languages
            "python": ("programming_languages", RequirementType.TECHNICAL_SKILL),
            "java": ("programming_languages", RequirementType.TECHNICAL_SKILL),
            "javascript": ("programming_languages", RequirementType.TECHNICAL_SKILL),
            "typescript": ("programming_languages", RequirementType.TECHNICAL_SKILL),
            "c++": ("programming_languages", RequirementType.TECHNICAL_SKILL),
            "c#": ("programming_languages", RequirementType.TECHNICAL_SKILL),
            
            # Frameworks
            "react": ("frameworks", RequirementType.TECHNICAL_SKILL),
            "angular": ("frameworks", RequirementType.TECHNICAL_SKILL),
            "django": ("frameworks", RequirementType.TECHNICAL_SKILL),
            "flask": ("frameworks", RequirementType.TECHNICAL_SKILL),
            
            # Databases
            "mysql": ("databases", RequirementType.TECHNICAL_SKILL),
            "postgresql": ("databases", RequirementType.TECHNICAL_SKILL),
            "mongodb": ("databases", RequirementType.TECHNICAL_SKILL),
            "sql": ("databases", RequirementType.TECHNICAL_SKILL),
            
            # Cloud platforms
            "aws": ("cloud_platforms", RequirementType.TECHNICAL_SKILL),
            "azure": ("cloud_platforms", RequirementType.TECHNICAL_SKILL),
            "google cloud": ("cloud_platforms", RequirementType.TECHNICAL_SKILL),
            
            # Soft skills
            "leadership": ("leadership", RequirementType.SOFT_SKILL),
            "communication": ("communication", RequirementType.SOFT_SKILL),
            "teamwork": ("collaboration", RequirementType.SOFT_SKILL),
            "problem solving": ("analytical", RequirementType.SOFT_SKILL),
            "analytical thinking": ("analytical", RequirementType.SOFT_SKILL),
            "organized": ("organization", RequirementType.SOFT_SKILL),
            "time management": ("organization", RequirementType.SOFT_SKILL),
            
            # Domain knowledge
            "data science": ("data_analytics", RequirementType.DOMAIN_KNOWLEDGE),
            "machine learning": ("data_analytics", RequirementType.DOMAIN_KNOWLEDGE),
            "financial analysis": ("finance", RequirementType.DOMAIN_KNOWLEDGE),
            "project management": ("management", RequirementType.DOMAIN_KNOWLEDGE)
        }
    
    def _determine_priority(self, text: str, context: str = "") -> RequirementPriority:
        """Determine priority level of a requirement based on context"""
        
        full_text = (text + " " + context).lower()
        
        # Check for explicit priority indicators
        for priority, indicators in self.priority_indicators.items():
            for indicator in indicators:
                if indicator in full_text:
                    return priority
        
        # Default priority logic based on position and context
        # Requirements in the first section tend to be required
        if any(word in full_text for word in ["experience", "degree", "years"]):
            return RequirementPriority.REQUIRED
        
        return RequirementPriority.PREFERRED  # Default
    
    def _extract_experience_requirements(self, text: str) -> Tuple[int, List[str]]:
        """Extract experience requirements from text"""
        
        years_required = 0
        experience_details = []
        
        for pattern in self.experience_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.group(1).isdigit():
                    years = int(match.group(1))
                    years_required = max(years_required, years)
                    experience_details.append(match.group(0))
        
        return years_required, experience_details
    
    def _categorize_skill(self, skill: str) -> Tuple[str, RequirementType]:
        """Categorize a skill and determine its type"""
        
        skill_lower = skill.lower().strip()
        
        # Check direct mapping first
        if skill_lower in self.skill_categories:
            return self.skill_categories[skill_lower]
        
        # Pattern-based categorization
        # Technical skills
        for category, patterns in self.technical_patterns.items():
            for pattern in patterns:
                if re.search(pattern, skill_lower):
                    return (category, RequirementType.TECHNICAL_SKILL)
        
        # Soft skills
        for pattern in self.soft_skills_patterns:
            if re.search(pattern, skill_lower):
                return ("soft_skills", RequirementType.SOFT_SKILL)
        
        # Domain knowledge
        for pattern in self.domain_patterns:
            if re.search(pattern, skill_lower):
                return ("domain_knowledge", RequirementType.DOMAIN_KNOWLEDGE)
        
        # Default categorization
        return ("general", RequirementType.TECHNICAL_SKILL)
    
    def _extract_skills_from_section(self, text: str, section_context: str = "") -> List[ParsedRequirement]:
        """Extract skills from a text section"""
        
        requirements = []
        
        # Split into sentences and bullet points
        sentences = re.split(r'[.\n•·]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 10:
                continue
            
            # Determine priority
            priority = self._determine_priority(sentence, section_context)
            
            # Extract technical skills using patterns
            for category, patterns in self.technical_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, sentence, re.IGNORECASE)
                    for match in matches:
                        skill_text = match.group(0).strip()
                        requirements.append(ParsedRequirement(
                            text=skill_text,
                            requirement_type=RequirementType.TECHNICAL_SKILL,
                            priority=priority,
                            category=category
                        ))
            
            # Extract soft skills
            for pattern in self.soft_skills_patterns:
                matches = re.finditer(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    skill_text = match.group(0).strip()
                    requirements.append(ParsedRequirement(
                        text=skill_text,
                        requirement_type=RequirementType.SOFT_SKILL,
                        priority=priority,
                        category="soft_skills"
                    ))
            
            # Extract domain knowledge
            for pattern in self.domain_patterns:
                matches = re.finditer(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    skill_text = match.group(0).strip()
                    requirements.append(ParsedRequirement(
                        text=skill_text,
                        requirement_type=RequirementType.DOMAIN_KNOWLEDGE,
                        priority=priority,
                        category="domain_knowledge"
                    ))
        
        return requirements
    
    def extract_requirements(self, job_description: str, company_info: str = "") -> RequirementsExtraction:
        """
        Centralized requirements extraction from job description
        
        Args:
            job_description: Full job description text
            company_info: Additional company information
            
        Returns:
            RequirementsExtraction with all parsed requirements
        """
        logger.info("[Requirements] Starting centralized requirements extraction")
        
        try:
            full_text = job_description + " " + company_info
            
            # Split into sections (basic approach - can be enhanced)
            sections = {
                "requirements": "",
                "qualifications": "",
                "skills": "",
                "experience": "",
                "responsibilities": ""
            }
            
            # Simple section detection
            for section_name in sections.keys():
                section_pattern = rf'{section_name}[:\s]*([^#]*?)(?=(?:requirements|qualifications|skills|experience|responsibilities|$))'
                match = re.search(section_pattern, full_text, re.IGNORECASE | re.DOTALL)
                if match:
                    sections[section_name] = match.group(1).strip()
            
            # If no clear sections, use entire text as requirements
            if not any(sections.values()):
                sections["requirements"] = full_text
            
            # Extract requirements from each section
            all_requirements = []
            for section_name, section_text in sections.items():
                if section_text:
                    section_requirements = self._extract_skills_from_section(section_text, section_name)
                    all_requirements.extend(section_requirements)
            
            # Extract experience requirements
            years_required, experience_details = self._extract_experience_requirements(full_text)
            
            # Categorize requirements by priority
            required_skills = [req for req in all_requirements if req.priority == RequirementPriority.REQUIRED]
            preferred_skills = [req for req in all_requirements if req.priority == RequirementPriority.PREFERRED]
            nice_to_have = [req for req in all_requirements if req.priority == RequirementPriority.NICE_TO_HAVE]
            
            # Create categorized lists for backwards compatibility
            technical_skills = [req.text for req in all_requirements if req.requirement_type == RequirementType.TECHNICAL_SKILL]
            soft_skills = [req.text for req in all_requirements if req.requirement_type == RequirementType.SOFT_SKILL]
            domain_keywords = [req.text for req in all_requirements if req.requirement_type == RequirementType.DOMAIN_KNOWLEDGE]
            tools_and_platforms = [req.text for req in all_requirements if req.category in ["tools_platforms", "cloud_platforms"]]
            
            # Remove duplicates while preserving order
            technical_skills = list(dict.fromkeys(technical_skills))
            soft_skills = list(dict.fromkeys(soft_skills))
            domain_keywords = list(dict.fromkeys(domain_keywords))
            tools_and_platforms = list(dict.fromkeys(tools_and_platforms))
            
            # Calculate priority weights
            priority_weights = {
                "required": 1.0,
                "preferred": 0.7,
                "nice_to_have": 0.3
            }
            
            extraction = RequirementsExtraction(
                required_skills=required_skills,
                preferred_skills=preferred_skills,
                nice_to_have_skills=nice_to_have,
                
                technical_skills=technical_skills,
                soft_skills=soft_skills,
                domain_keywords=domain_keywords,
                tools_and_platforms=tools_and_platforms,
                
                years_experience_required=years_required,
                education_requirements=experience_details,
                certifications=[],  # TODO: Add certification extraction
                
                total_requirements=len(all_requirements),
                priority_weights=priority_weights
            )
            
            logger.info(f"[Requirements] Extraction complete - Total: {len(all_requirements)}, "
                       f"Required: {len(required_skills)}, Preferred: {len(preferred_skills)}, "
                       f"Technical: {len(technical_skills)}, Soft: {len(soft_skills)}, "
                       f"Domain: {len(domain_keywords)}")
            
            return extraction
            
        except Exception as e:
            logger.error(f"[Requirements] Error in extraction: {e}")
            # Return empty extraction on error
            return RequirementsExtraction(
                required_skills=[], preferred_skills=[], nice_to_have_skills=[],
                technical_skills=[], soft_skills=[], domain_keywords=[], tools_and_platforms=[],
                years_experience_required=0, education_requirements=[], certifications=[],
                total_requirements=0, priority_weights={"required": 1.0, "preferred": 0.7, "nice_to_have": 0.3}
            )
    
    def get_requirement_lists_for_matching(self, extraction: RequirementsExtraction) -> Dict[str, List[str]]:
        """
        Get standardized requirement lists for use by matching components
        
        Returns:
            Dictionary with consistent skill lists for all matching components
        """
        return {
            "technical": extraction.technical_skills,
            "soft": extraction.soft_skills,
            "domain": extraction.domain_keywords,
            "tools": extraction.tools_and_platforms,
            "all_requirements": extraction.technical_skills + extraction.soft_skills + extraction.domain_keywords
        }
