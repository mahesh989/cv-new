#!/usr/bin/env python3
"""
🎯 ATS Rules Engine - Advanced Production-Ready System
====================================================

Comprehensive ATS evaluation system with:
- Multi-layered scoring algorithms
- Semantic skill matching
- Context-aware evaluation
- Intelligent feedback generation
- Role-based customization
- Australian market optimization
- Real-time adaptability

Author: CV Agent AI System
Version: 2.0.0
"""

import os
import json
import re
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import asyncio
from difflib import SequenceMatcher
import numpy as np

# AI/ML imports
from openai import OpenAI
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    ADVANCED_ML_AVAILABLE = True
except ImportError:
    ADVANCED_ML_AVAILABLE = False
    logging.warning("Advanced ML libraries not available. Using basic matching.")

# Import hybrid AI service
from .hybrid_ai_service import hybrid_ai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AI service (DeepSeek only)
ai_service = hybrid_ai

# ============================================================================
# CORE ENUMS AND CONSTANTS
# ============================================================================

class CompatibilityLevel(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

class SkillCategory(Enum):
    TECHNICAL = "technical"
    SOFT = "soft"
    DOMAIN = "domain"
    CERTIFICATION = "certification"

class EvaluationStatus(Enum):
    PASSED = "passed"
    LIKELY_PASSED = "likely_passed"
    NEEDS_IMPROVEMENT = "needs_improvement"
    NEEDS_MAJOR_IMPROVEMENT = "needs_major_improvement"
    REJECTED = "rejected"

# Advanced scoring constants
SCORING_WEIGHTS = {
    "default": {
        "technical_skills": 0.35,
        "soft_skills": 0.20,
        "domain_knowledge": 0.15,
        "quantitative_impact": 0.25,
        "format_compatibility": 0.05
    },
    "technical_roles": {
        "technical_skills": 0.45,
        "soft_skills": 0.15,
        "domain_knowledge": 0.20,
        "quantitative_impact": 0.20
    },
    "leadership_roles": {
        "technical_skills": 0.25,
        "soft_skills": 0.35,
        "domain_knowledge": 0.15,
        "quantitative_impact": 0.25
    },
    "entry_level": {
        "technical_skills": 0.40,
        "soft_skills": 0.25,
        "domain_knowledge": 0.10,
        "quantitative_impact": 0.15,
        "education_relevance": 0.10
    }
}

# Australian market specific terms
AUSTRALIAN_TERMS = {
    "resume": "CV",
    "college": "university",
    "GPA": "WAM",
    "401k": "superannuation",
    "health insurance": "Medicare",
    "vacation": "annual leave",
    "sick leave": "personal leave"
}

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class SkillMatch:
    skill: str
    category: SkillCategory
    match_type: str  # exact, semantic, contextual, missing
    confidence: float
    context: Optional[str] = None
    suggestions: List[str] = None

@dataclass
class MetricAnalysis:
    value: str
    type: str  # financial, efficiency, scale, timeline
    impact_score: float
    context: str
    normalized_value: Optional[float] = None

@dataclass
class SectionAnalysis:
    section_name: str
    content_quality: float
    keyword_density: float
    structure_score: float
    suggestions: List[str]

@dataclass
class ATSEvaluationResult:
    overall_score: float
    compatibility_level: CompatibilityLevel
    status: EvaluationStatus
    category_scores: Dict[str, float]
    skill_matches: List[SkillMatch]
    metrics_analysis: List[MetricAnalysis]
    section_analysis: List[SectionAnalysis]
    feedback: List[str]
    format_suggestions: List[str]
    improvement_recommendations: List[str]
    processing_metadata: Dict[str, Any]

# ============================================================================
# ADVANCED SKILL EXTRACTION AND MATCHING
# ============================================================================

class AdvancedSkillExtractor:
    """Advanced skill extraction with semantic understanding and context awareness"""
    
    def __init__(self):
        self.skill_synonyms = {
            # Technical Skills
            "python": ["python programming", "python development", "python scripting", "py", "python3"],
            "javascript": ["js", "javascript programming", "node.js", "nodejs", "react", "vue", "angular"],
            "sql": ["structured query language", "database queries", "mysql", "postgresql", "oracle sql"],
            "data analysis": ["data analytics", "statistical analysis", "data science", "data insights"],
            "machine learning": ["ml", "artificial intelligence", "ai", "deep learning", "neural networks"],
            "cloud computing": ["aws", "azure", "google cloud", "gcp", "cloud services", "cloud architecture"],
            
            # Soft Skills
            "leadership": ["team leadership", "leading teams", "management", "supervising", "mentoring"],
            "communication": ["verbal communication", "written communication", "presentation", "stakeholder engagement"],
            "problem solving": ["analytical thinking", "critical thinking", "troubleshooting", "solution design"],
            "teamwork": ["collaboration", "team collaboration", "cross-functional", "cooperative"],
            "project management": ["project coordination", "project planning", "agile", "scrum", "kanban"],
            
            # Domain Specific
            "financial analysis": ["financial modeling", "budgeting", "forecasting", "investment analysis"],
            "digital marketing": ["seo", "sem", "social media marketing", "content marketing", "email marketing"],
            "business intelligence": ["bi", "data visualization", "reporting", "dashboards", "kpi analysis"]
        }
        
        self.context_patterns = {
            "technical_implementation": [
                r"developed?\s+(?:using|with|in)\s+(\w+)",
                r"implemented?\s+(\w+)",
                r"built?\s+(?:using|with)\s+(\w+)",
                r"created?\s+(?:using|with)\s+(\w+)"
            ],
            "leadership_evidence": [
                r"led\s+(?:a\s+)?team\s+of\s+(\d+)",
                r"managed?\s+(\d+)\s+(?:people|employees|staff)",
                r"supervised?\s+(\d+)",
                r"mentored?\s+(\d+)"
            ],
            "quantitative_impact": [
                r"(\d+(?:\.\d+)?%)\s+(?:improvement|increase|decrease|reduction)",
                r"saved?\s+\$?([\d,]+)",
                r"generated?\s+\$?([\d,]+)",
                r"managed?\s+\$?([\d,]+)\s+budget"
            ]
        }
        
        if ADVANCED_ML_AVAILABLE:
            try:
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
                self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
                logger.info("✅ Advanced ML models loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load ML models: {e}")
                self.sentence_model = None
                self.tfidf_vectorizer = None
        else:
            self.sentence_model = None
            self.tfidf_vectorizer = None

    async def extract_skills_with_context(self, text: str, skill_type: SkillCategory) -> List[SkillMatch]:
        """Extract skills with contextual evidence and confidence scoring"""
        skills = []
        
        # Get base skills using LLM
        base_skills = await self._extract_skills_llm(text, skill_type)
        
        for skill in base_skills:
            # Find contextual evidence
            context = self._find_skill_context(skill, text)
            confidence = self._calculate_skill_confidence(skill, text, context)
            
            # Determine match type
            match_type = self._determine_match_type(skill, text)
            
            skills.append(SkillMatch(
                skill=skill,
                category=skill_type,
                match_type=match_type,
                confidence=confidence,
                context=context
            ))
        
        return skills

    async def _extract_skills_llm(self, text: str, skill_type: SkillCategory) -> List[str]:
        """Extract skills using advanced LLM prompting"""
        
        skill_prompts = {
            SkillCategory.TECHNICAL: """
            Extract technical skills, programming languages, software tools, platforms, frameworks, and certifications.
            Focus on concrete, measurable technical competencies.
            
            Examples: Python, SQL, AWS, Docker, React, Tableau, Machine Learning, Data Analysis, Git, Linux
            """,
            
            SkillCategory.SOFT: """
            Extract interpersonal, behavioral, and cognitive competencies with evidence.
            Look for skills demonstrated through actions and achievements.
            
            Examples: Leadership, Communication, Problem Solving, Team Collaboration, Project Management
            """,
            
            SkillCategory.DOMAIN: """
            Extract industry-specific terminology, methodologies, and specialized knowledge.
            Include regulatory knowledge, business domains, and sector-specific concepts.
            
            Examples: Financial Modeling, Agile Methodology, GDPR Compliance, Clinical Trials, Digital Marketing
            """,
            
            SkillCategory.CERTIFICATION: """
            Extract professional certifications, licenses, and formal qualifications.
            Include both completed and in-progress certifications.
            
            Examples: AWS Certified, PMP, Scrum Master, CPA, CISSP, Microsoft Certified
            """
        }
        
        prompt = f"""
        You are an expert skill extraction specialist. Analyze the following text and extract {skill_type.value} skills.
        
        {skill_prompts[skill_type]}
        
        EXTRACTION RULES:
        1. Extract only individual skills, not phrases or sentences
        2. Use standard terminology (e.g., "JavaScript" not "JS")
        3. Include variations when appropriate
        4. Avoid duplicates and generic terms
        5. Focus on skills that would be valuable for job matching
        
        Return only a JSON array of skills:
        ["skill1", "skill2", "skill3"]
        
        Text to analyze:
        {text}
        """
        
        try:
            # Use hybrid AI service (Claude primary, OpenAI fallback)
            content = ai_service.generate_response(
                prompt=prompt,
                temperature=0.1,
                max_tokens=500
            ).strip()
            
            # Parse JSON response
            if content.startswith('[') and content.endswith(']'):
                skills = json.loads(content)
                return [skill.strip() for skill in skills if skill.strip()]
            else:
                # Fallback parsing
                skills = re.findall(r'"([^"]+)"', content)
                return [skill.strip() for skill in skills if skill.strip()]
                
        except Exception as e:
            logger.error(f"Error extracting {skill_type.value} skills: {e}")
            return []

    def _find_skill_context(self, skill: str, text: str) -> Optional[str]:
        """Find contextual evidence for a skill in the text"""
        skill_lower = skill.lower()
        text_lower = text.lower()
        
        # Look for skill in context
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            if skill_lower in sentence.lower():
                # Return the sentence as context
                return sentence.strip()
        
        return None

    def _calculate_skill_confidence(self, skill: str, text: str, context: Optional[str]) -> float:
        """Calculate confidence score for a skill match"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence if skill appears in context
        if context:
            confidence += 0.2
        
        # Boost confidence if skill appears multiple times
        skill_count = text.lower().count(skill.lower())
        confidence += min(skill_count * 0.1, 0.3)
        
        # Boost confidence if skill appears in experience/projects sections
        if re.search(r'(experience|projects?|work|employment).*?' + re.escape(skill), text, re.IGNORECASE | re.DOTALL):
            confidence += 0.2
        
        return min(confidence, 1.0)

    def _determine_match_type(self, skill: str, text: str) -> str:
        """Determine the type of match (exact, semantic, contextual)"""
        skill_lower = skill.lower()
        text_lower = text.lower()
        
        if skill_lower in text_lower:
            return "exact"
        
        # Check for semantic matches using synonyms
        if skill_lower in self.skill_synonyms:
            for synonym in self.skill_synonyms[skill_lower]:
                if synonym in text_lower:
                    return "semantic"
        
        # Check for contextual matches
        for pattern_type, patterns in self.context_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return "contextual"
        
        return "inferred"

    async def semantic_skill_matching(self, cv_skills: List[str], jd_skills: List[str], threshold: float = 0.6) -> List[Tuple[str, str, float]]:
        """Advanced semantic skill matching using embeddings"""
        if not self.sentence_model or not cv_skills or not jd_skills:
            return []
        
        try:
            # Generate embeddings
            cv_embeddings = self.sentence_model.encode(cv_skills)
            jd_embeddings = self.sentence_model.encode(jd_skills)
            
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(jd_embeddings, cv_embeddings)
            
            matches = []
            for i, jd_skill in enumerate(jd_skills):
                max_similarity = np.max(similarity_matrix[i])
                best_match_idx = np.argmax(similarity_matrix[i])
                cv_skill = cv_skills[best_match_idx]
                
                # Check for exact or near-exact matches first
                if jd_skill.lower() in cv_skill.lower() or cv_skill.lower() in jd_skill.lower():
                    matches.append((jd_skill, cv_skill, 1.0))
                elif max_similarity >= threshold:
                    matches.append((jd_skill, cv_skill, float(max_similarity)))
                else:
                    # Try synonym matching
                    for synonym_list in self.skill_synonyms.values():
                        if jd_skill.lower() in synonym_list or any(syn in cv_skill.lower() for syn in synonym_list):
                            matches.append((jd_skill, cv_skill, 0.8))
                            break
            
            return matches
            
        except Exception as e:
            logger.error(f"Error in semantic skill matching: {e}")
            return []

# ============================================================================
# ADVANCED METRICS ANALYSIS
# ============================================================================

class MetricsAnalyzer:
    """Advanced quantitative impact analysis"""
    
    def __init__(self):
        self.metric_patterns = {
            "financial": [
                r"\$?([\d,]+(?:\.\d+)?)\s*(?:k|thousand|million|m|billion|b)?\s*(?:aud|usd|dollars?)?\s*(?:saved|generated|revenue|profit|budget|cost|annually|yearly)",
                r"(?:saved|generated|increased|decreased|reduced|managed|budget)\s+(?:by\s+|of\s+)?\$?([\d,]+(?:\.\d+)?)\s*(?:k|thousand|million|m|billion|b)?\s*(?:aud|usd|dollars?)?",
                r"(?:budget|revenue|profit|cost|savings)\s+(?:of\s+|was\s+|reached\s+)?\$?([\d,]+(?:\.\d+)?)\s*(?:k|thousand|million|m|billion|b)?\s*(?:aud|usd|dollars?)?",
                r"([\d,]+(?:\.\d+)?)\s*(?:k|thousand|million|m|billion|b)?\s*(?:aud|usd|dollars?)\s*(?:saved|generated|revenue|profit|budget|cost|annually|yearly)"
            ],
            "percentage": [
                r"([\d,]+(?:\.\d+)?)\s*%\s*(?:improvement|increase|decrease|reduction|growth|efficiency|accuracy|performance)",
                r"(?:improved|increased|decreased|reduced|grew|achieved|reached)\s+(?:by\s+|up\s+to\s+)?([\d,]+(?:\.\d+)?)\s*%",
                r"([\d,]+(?:\.\d+)?)\s*percent\s*(?:improvement|increase|decrease|reduction|growth|efficiency|accuracy)",
                r"(?:efficiency|performance|accuracy|success|completion)\s+(?:by\s+|of\s+)?([\d,]+(?:\.\d+)?)\s*%"
            ],
            "scale": [
                r"(?:led|managed|supervised|coordinated|mentored)\s+(?:a\s+team\s+of\s+|up\s+to\s+)?([\d,]+)\s*(?:people|employees|staff|members|engineers|developers|students|interns)",
                r"(?:team|group|department|class)\s+of\s+([\d,]+)",
                r"([\d,]+)\s*(?:member|person|employee|student)\s+(?:team|group|class)",
                r"(?:managing|leading|supervising)\s+([\d,]+)\s*(?:people|employees|staff|members)"
            ],
            "timeline": [
                r"(?:completed|delivered|finished|reduced|improved)\s+(?:in\s+|within\s+|from\s+[\d\s\w]+\s+to\s+)?([\d,]+)\s*(?:days?|weeks?|months?|years?|hours?|minutes?)",
                r"([\d,]+)\s*(?:days?|weeks?|months?|years?|hours?|minutes?)\s+(?:ahead|early|before|under|faster|quicker)",
                r"(?:reduced|decreased|improved)\s+(?:time|duration|processing)\s+(?:by\s+|from\s+[\d\s\w]+\s+to\s+)?([\d,]+)\s*(?:days?|weeks?|months?|years?|hours?|minutes?)",
                r"from\s+[\d,]+\s*(?:hours?|minutes?|days?)\s+to\s+([\d,]+)\s*(?:hours?|minutes?|days?)"
            ],
            "volume": [
                r"(?:processed|handled|managed|analyzed|extracted|worked\s+with)\s+([\d,]+(?:\.\d+)?)\s*(?:k|thousand|million|m|billion|b)?\s*(?:\+)?\s*(?:records|transactions|requests|cases|projects|datasets|data\s+points)",
                r"([\d,]+(?:\.\d+)?)\s*(?:k|thousand|million|m|billion|b)?\s*(?:\+)?\s*(?:users|customers|clients|accounts|records|transactions)",
                r"(?:database|system|platform|dataset)\s+(?:with|containing|of|having)\s+([\d,]+(?:\.\d+)?)\s*(?:k|thousand|million|m|billion|b)?\s*(?:\+)?\s*(?:records|entries|rows|data\s+points)",
                r"(?:datasets?|data)\s+(?:with|containing|of)\s+([\d,]+(?:\.\d+)?)\s*(?:k|thousand|million|m|billion|b)?\s*(?:\+)?\s*(?:records|entries|rows|points)"
            ]
        }
        
        self.impact_multipliers = {
            "financial": 1.0,
            "percentage": 0.8,
            "scale": 0.7,
            "timeline": 0.6,
            "volume": 0.5
        }

    def analyze_metrics(self, text: str) -> List[MetricAnalysis]:
        """Extract and analyze quantitative metrics from text"""
        metrics = []
        
        for metric_type, patterns in self.metric_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    value = match.group(1)
                    context = self._extract_metric_context(match, text)
                    
                    metric = MetricAnalysis(
                        value=value,
                        type=metric_type,
                        impact_score=self._calculate_impact_score(value, metric_type),
                        context=context,
                        normalized_value=self._normalize_metric_value(value, metric_type)
                    )
                    metrics.append(metric)
        
        return self._deduplicate_metrics(metrics)

    def _extract_metric_context(self, match, text: str, window: int = 100) -> str:
        """Extract context around a metric"""
        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)
        return text[start:end].strip()

    def _calculate_impact_score(self, value: str, metric_type: str) -> float:
        """Calculate impact score for a metric"""
        try:
            # Parse numeric value
            numeric_value = float(value.replace(',', ''))
            
            # Base score calculation
            base_score = min(numeric_value / 100, 1.0) if metric_type == "percentage" else min(numeric_value / 1000, 1.0)
            
            # Apply type multiplier
            multiplier = self.impact_multipliers.get(metric_type, 0.5)
            
            return base_score * multiplier
            
        except (ValueError, TypeError):
            return 0.1

    def _normalize_metric_value(self, value: str, metric_type: str) -> Optional[float]:
        """Normalize metric value for comparison"""
        try:
            numeric_value = float(value.replace(',', ''))
            
            if metric_type == "financial":
                # Convert to standard currency (thousands)
                return numeric_value / 1000
            elif metric_type == "percentage":
                return numeric_value / 100
            else:
                return numeric_value
                
        except (ValueError, TypeError):
            return None

    def _deduplicate_metrics(self, metrics: List[MetricAnalysis]) -> List[MetricAnalysis]:
        """Remove duplicate metrics"""
        seen = set()
        unique_metrics = []
        
        for metric in metrics:
            key = (metric.value, metric.type)
            if key not in seen:
                seen.add(key)
                unique_metrics.append(metric)
        
        return unique_metrics

# ============================================================================
# MAIN ATS RULES ENGINE
# ============================================================================

class ATSRulesEngine:
    """Main ATS evaluation engine with advanced scoring and feedback"""
    
    def __init__(self):
        self.skill_extractor = AdvancedSkillExtractor()
        self.metrics_analyzer = MetricsAnalyzer()
        self.evaluation_history = []
        
        # Load role-specific configurations
        self.role_configs = self._load_role_configurations()
        
        # Initialize feedback templates
        self.feedback_templates = self._initialize_feedback_templates()

    def _load_role_configurations(self) -> Dict[str, Dict]:
        """Load role-specific evaluation configurations"""
        return {
            "default": {
                "weights": SCORING_WEIGHTS["default"],
                "critical_skills": ["communication", "problem solving", "teamwork"],
                "preferred_skills": ["leadership", "analytical thinking", "adaptability"],
                "domain_keywords": ["project management", "collaboration", "innovation"]
            },
            "data_analyst": {
                "weights": SCORING_WEIGHTS["technical_roles"],
                "critical_skills": ["python", "sql", "data analysis", "statistics"],
                "preferred_skills": ["tableau", "power bi", "r", "machine learning"],
                "domain_keywords": ["data pipeline", "etl", "reporting", "dashboard", "kpi"]
            },
            "software_engineer": {
                "weights": SCORING_WEIGHTS["technical_roles"],
                "critical_skills": ["programming", "software development", "git", "testing"],
                "preferred_skills": ["cloud computing", "devops", "agile", "ci/cd"],
                "domain_keywords": ["api", "microservices", "scalability", "performance"]
            },
            "project_manager": {
                "weights": SCORING_WEIGHTS["leadership_roles"],
                "critical_skills": ["project management", "leadership", "communication", "planning"],
                "preferred_skills": ["agile", "scrum", "risk management", "stakeholder management"],
                "domain_keywords": ["deliverables", "milestones", "budget", "timeline"]
            },
            "entry_level": {
                "weights": SCORING_WEIGHTS["entry_level"],
                "critical_skills": [],
                "preferred_skills": [],
                "domain_keywords": [],
                "education_focus": True
            }
        }

    def _initialize_feedback_templates(self) -> Dict[str, List[str]]:
        """Initialize feedback message templates"""
        return {
            "missing_critical_skills": [
                "Your CV is missing {skill}, which is essential for this role. Consider highlighting any related experience or training.",
                "The job requires {skill} expertise. If you have this skill, make sure it's prominently featured in your CV.",
                "Adding {skill} to your skillset would significantly improve your match for this position."
            ],
            "weak_quantification": [
                "Your achievements would be more impactful with specific numbers. Try quantifying your results.",
                "Consider adding metrics to demonstrate the scale and impact of your work.",
                "Employers love to see measurable outcomes. Add percentages, dollar amounts, or team sizes where possible."
            ],
            "poor_skill_context": [
                "You mentioned {skill} in your skills section, but it's not evident in your experience. Show how you've used it.",
                "Provide specific examples of how you've applied {skill} in your previous roles.",
                "Connect your skills to actual work experiences to make them more credible."
            ],
            "format_improvements": [
                "Consider using bullet points to make your achievements more scannable.",
                "Your CV would benefit from clearer section headers and consistent formatting.",
                "Use action verbs to start your bullet points for more impact."
            ]
        }

    async def evaluate_cv(
        self, 
        cv_text: str, 
        jd_text: str, 
        role_profile: str = "default",
        use_advanced_analysis: bool = True
    ) -> ATSEvaluationResult:
        """
        Comprehensive CV evaluation with advanced analysis
        """
        logger.info(f"Starting ATS evaluation for role: {role_profile}")
        
        # Get role configuration
        role_config = self.role_configs.get(role_profile, self.role_configs["default"])
        weights = role_config.get("weights", SCORING_WEIGHTS["default"])
        
        # Extract skills from both CV and JD
        cv_skills = await self._extract_all_skills(cv_text)
        jd_skills = await self._extract_all_skills(jd_text)
        
        # Analyze metrics
        cv_metrics = self.metrics_analyzer.analyze_metrics(cv_text)
        
        # Perform skill matching
        skill_matches = await self._perform_skill_matching(cv_skills, jd_skills)
        
        # Calculate category scores
        category_scores = await self._calculate_category_scores(
            cv_text, jd_text, skill_matches, cv_metrics, weights
        )
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(category_scores, weights)
        
        # Determine compatibility and status
        compatibility_level = self._determine_compatibility_level(overall_score)
        status = self._determine_evaluation_status(overall_score, skill_matches)
        
        # Generate feedback and recommendations
        feedback = await self._generate_feedback(skill_matches, cv_metrics, category_scores)
        format_suggestions = self._generate_format_suggestions(cv_text)
        improvement_recommendations = await self._generate_improvement_recommendations(
            skill_matches, cv_metrics, role_config
        )
        
        # Analyze sections
        section_analysis = self._analyze_cv_sections(cv_text)
        
        # Create result
        result = ATSEvaluationResult(
            overall_score=overall_score,
            compatibility_level=compatibility_level,
            status=status,
            category_scores=category_scores,
            skill_matches=skill_matches,
            metrics_analysis=cv_metrics,
            section_analysis=section_analysis,
            feedback=feedback,
            format_suggestions=format_suggestions,
            improvement_recommendations=improvement_recommendations,
            processing_metadata={
                "role_profile": role_profile,
                "evaluation_timestamp": datetime.now().isoformat(),
                "cv_word_count": len(cv_text.split()),
                "jd_word_count": len(jd_text.split()),
                "advanced_analysis_used": use_advanced_analysis
            }
        )
        
        # Store in history
        self.evaluation_history.append(result)
        
        logger.info(f"Evaluation completed. Score: {overall_score:.1f}, Status: {status.value}")
        return result

    async def _extract_all_skills(self, text: str) -> Dict[SkillCategory, List[SkillMatch]]:
        """Extract all skill categories from text"""
        skills = {}
        
        for category in SkillCategory:
            skills[category] = await self.skill_extractor.extract_skills_with_context(text, category)
        
        return skills

    async def _perform_skill_matching(
        self, 
        cv_skills: Dict[SkillCategory, List[SkillMatch]], 
        jd_skills: Dict[SkillCategory, List[SkillMatch]]
    ) -> List[SkillMatch]:
        """Perform advanced skill matching between CV and JD"""
        all_matches = []
        
        for category in SkillCategory:
            cv_category_skills = [skill.skill for skill in cv_skills.get(category, [])]
            jd_category_skills = [skill.skill for skill in jd_skills.get(category, [])]
            
            # Perform semantic matching
            semantic_matches = await self.skill_extractor.semantic_skill_matching(
                cv_category_skills, jd_category_skills
            )
            
            # Create SkillMatch objects
            for jd_skill, cv_skill, confidence in semantic_matches:
                match = SkillMatch(
                    skill=jd_skill,
                    category=category,
                    match_type="semantic",
                    confidence=confidence,
                    context=f"Matched with CV skill: {cv_skill}"
                )
                all_matches.append(match)
            
            # Find missing skills
            matched_jd_skills = {match[0] for match in semantic_matches}
            missing_skills = set(jd_category_skills) - matched_jd_skills
            
            for missing_skill in missing_skills:
                match = SkillMatch(
                    skill=missing_skill,
                    category=category,
                    match_type="missing",
                    confidence=0.0,
                    suggestions=[f"Consider adding {missing_skill} to your skillset"]
                )
                all_matches.append(match)
        
        return all_matches

    async def _calculate_category_scores(
        self, 
        cv_text: str, 
        jd_text: str, 
        skill_matches: List[SkillMatch], 
        metrics: List[MetricAnalysis], 
        weights: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate scores for each evaluation category"""
        
        # Technical skills score
        technical_matches = [m for m in skill_matches if m.category == SkillCategory.TECHNICAL]
        technical_score = self._calculate_technical_score(technical_matches)
        
        # Soft skills score
        soft_matches = [m for m in skill_matches if m.category == SkillCategory.SOFT]
        soft_score = self._calculate_soft_skills_score(soft_matches, cv_text)
        
        # Domain knowledge score
        domain_matches = [m for m in skill_matches if m.category == SkillCategory.DOMAIN]
        domain_score = self._calculate_domain_score(domain_matches)
        
        # Quantitative impact score
        impact_score = self._calculate_impact_score(metrics)
        
        # Format compatibility score
        format_score = self._calculate_format_score(cv_text)
        
        return {
            "technical_skills": technical_score,
            "soft_skills": soft_score,
            "domain_knowledge": domain_score,
            "quantitative_impact": impact_score,
            "format_compatibility": format_score
        }

    def _calculate_technical_score(self, matches: List[SkillMatch]) -> float:
        """Calculate technical skills score"""
        if not matches:
            return 0.0
        
        matched_skills = [m for m in matches if m.match_type != "missing"]
        missing_skills = [m for m in matches if m.match_type == "missing"]
        
        if not matched_skills and not missing_skills:
            return 0.0
        
        # Calculate match ratio
        total_jd_skills = len(matches)
        matched_count = len(matched_skills)
        
        if total_jd_skills == 0:
            return 0.0
        
        # Base score from match ratio
        match_ratio = matched_count / total_jd_skills
        base_score = match_ratio * 100
        
        # Bonus for high-confidence matches
        confidence_bonus = 0.0
        for match in matched_skills:
            if match.match_type == "exact":
                confidence_bonus += 5.0
            elif match.match_type == "semantic":
                confidence_bonus += 3.0 * match.confidence
            elif match.match_type == "contextual":
                confidence_bonus += 2.0 * match.confidence
        
        # Normalize confidence bonus
        if matched_count > 0:
            confidence_bonus = confidence_bonus / matched_count
        
        final_score = base_score + min(confidence_bonus, 20.0)
        return max(0.0, min(100.0, final_score))

    def _calculate_soft_skills_score(self, matches: List[SkillMatch], cv_text: str) -> float:
        """Calculate soft skills score with context analysis"""
        if not matches:
            return 0.0
        
        total_score = 0.0
        
        for match in matches:
            if match.match_type == "missing":
                total_score -= 10.0
            elif match.context:
                # Bonus for contextual evidence
                total_score += 7.0 * match.confidence
            else:
                # Penalty for skills without context
                total_score -= 5.0
        
        # Normalize to 0-100 scale
        return max(0.0, min(100.0, total_score + 50))

    def _calculate_domain_score(self, matches: List[SkillMatch]) -> float:
        """Calculate domain knowledge score"""
        if not matches:
            return 0.0
        
        matched_count = sum(1 for m in matches if m.match_type != "missing")
        total_count = len(matches)
        
        if total_count == 0:
            return 0.0
        
        return (matched_count / total_count) * 100

    def _calculate_impact_score(self, metrics: List[MetricAnalysis]) -> float:
        """Calculate quantitative impact score"""
        if not metrics:
            return 0.0
        
        # Base score from number of metrics
        metric_count = len(metrics)
        if metric_count == 0:
            return 0.0
        elif metric_count <= 2:
            base_score = 30.0
        elif metric_count <= 4:
            base_score = 60.0
        else:
            base_score = 80.0
        
        # Bonus from impact scores
        impact_bonus = sum(metric.impact_score for metric in metrics) * 5
        
        return min(100.0, base_score + impact_bonus)

    def _calculate_format_score(self, cv_text: str) -> float:
        """Calculate format compatibility score"""
        score = 100.0
        
        # Check for problematic formatting
        if re.search(r'\|', cv_text):  # Pipe separators
            score -= 5.0
        
        if re.search(r'[^\w\s\-\.\,\;\:\(\)\[\]]', cv_text):  # Special characters
            score -= 10.0
        
        if len(cv_text.split()) < 200:  # Too short
            score -= 20.0
        elif len(cv_text.split()) > 1000:  # Too long
            score -= 10.0
        
        return max(0.0, score)

    def _calculate_overall_score(self, category_scores: Dict[str, float], weights: Dict[str, float]) -> float:
        """Calculate weighted overall score"""
        total_score = 0.0
        total_weight = 0.0
        
        for category, score in category_scores.items():
            weight = weights.get(category, 0.0)
            total_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return total_score / total_weight

    def _determine_compatibility_level(self, score: float) -> CompatibilityLevel:
        """Determine compatibility level based on score"""
        if score >= 85:
            return CompatibilityLevel.EXCELLENT
        elif score >= 75:
            return CompatibilityLevel.GOOD
        elif score >= 65:
            return CompatibilityLevel.FAIR
        elif score >= 50:
            return CompatibilityLevel.POOR
        else:
            return CompatibilityLevel.CRITICAL

    def _determine_evaluation_status(self, score: float, skill_matches: List[SkillMatch]) -> EvaluationStatus:
        """Determine evaluation status"""
        # Check for critical missing skills
        critical_missing = [m for m in skill_matches if m.match_type == "missing" and m.category == SkillCategory.TECHNICAL]
        
        if len(critical_missing) > 3:
            return EvaluationStatus.REJECTED
        elif score >= 85:
            return EvaluationStatus.PASSED
        elif score >= 75:
            return EvaluationStatus.LIKELY_PASSED
        elif score >= 65:
            return EvaluationStatus.NEEDS_IMPROVEMENT
        else:
            return EvaluationStatus.NEEDS_MAJOR_IMPROVEMENT

    async def _generate_feedback(
        self, 
        skill_matches: List[SkillMatch], 
        metrics: List[MetricAnalysis], 
        category_scores: Dict[str, float]
    ) -> List[str]:
        """Generate intelligent feedback messages"""
        feedback = []
        
        # Feedback for missing skills
        missing_skills = [m for m in skill_matches if m.match_type == "missing"]
        if missing_skills:
            critical_missing = [m for m in missing_skills if m.category == SkillCategory.TECHNICAL]
            if critical_missing:
                skills_list = ", ".join([m.skill for m in critical_missing[:3]])
                feedback.append(f"Your CV is missing key technical skills: {skills_list}. Consider highlighting any related experience or training.")
        
        # Feedback for metrics
        if len(metrics) < 3:
            feedback.append("Your achievements would be more impactful with specific numbers. Try quantifying your results with percentages, dollar amounts, or team sizes.")
        
        # Feedback for low category scores
        if category_scores.get("soft_skills", 0) < 60:
            feedback.append("Strengthen your soft skills section by providing specific examples of leadership, communication, and teamwork.")
        
        if category_scores.get("technical_skills", 0) < 70:
            feedback.append("Enhance your technical skills section and show how you've applied these skills in real projects.")
        
        return feedback

    def _generate_format_suggestions(self, cv_text: str) -> List[str]:
        """Generate format improvement suggestions"""
        suggestions = []
        
        # Check for pipe separators
        if re.search(r'\|', cv_text):
            suggestions.append("Use commas instead of pipes (|) to separate skills for better ATS compatibility.")
        
        # Check for section structure
        if not re.search(r'(?i)(experience|employment|work)', cv_text):
            suggestions.append("Include a clear 'Experience' or 'Work History' section.")
        
        if not re.search(r'(?i)(skills|competencies|technologies)', cv_text):
            suggestions.append("Add a dedicated 'Skills' section to highlight your technical abilities.")
        
        # Check for bullet points
        if not re.search(r'[•\-\*]', cv_text):
            suggestions.append("Use bullet points to make your achievements more scannable.")
        
        return suggestions

    async def _generate_improvement_recommendations(
        self, 
        skill_matches: List[SkillMatch], 
        metrics: List[MetricAnalysis], 
        role_config: Dict[str, Any]
    ) -> List[str]:
        """Generate personalized improvement recommendations"""
        recommendations = []
        
        # Skill-based recommendations
        missing_critical = [m for m in skill_matches if m.match_type == "missing" and m.skill in role_config.get("critical_skills", [])]
        if missing_critical:
            for skill_match in missing_critical[:3]:
                recommendations.append(f"Consider gaining experience in {skill_match.skill} as it's critical for this role.")
        
        # Metrics-based recommendations
        if len(metrics) == 0:
            recommendations.append("Add quantifiable achievements to demonstrate your impact (e.g., 'Increased efficiency by 25%', 'Managed $50K budget').")
        
        # Format recommendations
        recommendations.append("Use action verbs to start your bullet points (e.g., 'Developed', 'Implemented', 'Led').")
        recommendations.append("Tailor your CV for each application by emphasizing relevant skills and experiences.")
        
        return recommendations

    def _analyze_cv_sections(self, cv_text: str) -> List[SectionAnalysis]:
        """Analyze individual CV sections"""
        sections = []
        
        # Define section patterns
        section_patterns = {
            "Experience": r'(?i)(experience|employment|work\s+history|professional\s+experience)',
            "Education": r'(?i)(education|academic|qualifications)',
            "Skills": r'(?i)(skills|competencies|technologies|technical\s+skills)',
            "Projects": r'(?i)(projects|portfolio|work\s+samples)'
        }
        
        for section_name, pattern in section_patterns.items():
            if re.search(pattern, cv_text):
                # Extract section content (simplified)
                section_content = self._extract_section_content(cv_text, pattern)
                
                analysis = SectionAnalysis(
                    section_name=section_name,
                    content_quality=self._assess_content_quality(section_content),
                    keyword_density=self._calculate_keyword_density(section_content),
                    structure_score=self._assess_structure(section_content),
                    suggestions=self._generate_section_suggestions(section_name, section_content)
                )
                sections.append(analysis)
        
        return sections

    def _extract_section_content(self, cv_text: str, pattern: str) -> str:
        """Extract content for a specific section"""
        # Simplified section extraction
        match = re.search(pattern, cv_text, re.IGNORECASE)
        if match:
            start = match.end()
            # Find next section or end of text
            next_section = re.search(r'(?i)(experience|education|skills|projects)', cv_text[start:])
            end = start + next_section.start() if next_section else len(cv_text)
            return cv_text[start:end].strip()
        return ""

    def _assess_content_quality(self, content: str) -> float:
        """Assess the quality of section content"""
        if not content:
            return 0.0
        
        # Simple quality metrics
        word_count = len(content.split())
        sentence_count = len(re.split(r'[.!?]+', content))
        
        # Quality score based on content richness
        quality_score = min(100.0, (word_count / 50) * 50 + (sentence_count / 10) * 50)
        return quality_score

    def _calculate_keyword_density(self, content: str) -> float:
        """Calculate keyword density in section"""
        if not content:
            return 0.0
        
        # Count technical keywords (simplified)
        technical_keywords = ['python', 'sql', 'javascript', 'aws', 'docker', 'react', 'data', 'analysis']
        keyword_count = sum(1 for keyword in technical_keywords if keyword.lower() in content.lower())
        
        return (keyword_count / len(technical_keywords)) * 100

    def _assess_structure(self, content: str) -> float:
        """Assess section structure"""
        if not content:
            return 0.0
        
        structure_score = 50.0  # Base score
        
        # Check for bullet points
        if re.search(r'[•\-\*]', content):
            structure_score += 25.0
        
        # Check for dates
        if re.search(r'\d{4}', content):
            structure_score += 25.0
        
        return min(100.0, structure_score)

    def _generate_section_suggestions(self, section_name: str, content: str) -> List[str]:
        """Generate suggestions for specific sections"""
        suggestions = []
        
        if section_name == "Experience":
            if not re.search(r'[•\-\*]', content):
                suggestions.append("Use bullet points to list your achievements and responsibilities.")
            if not re.search(r'\d+', content):
                suggestions.append("Include quantifiable achievements with numbers and percentages.")
        
        elif section_name == "Skills":
            if '|' in content:
                suggestions.append("Use commas instead of pipes to separate skills.")
            if len(content.split()) < 10:
                suggestions.append("Expand your skills section with more relevant technical skills.")
        
        elif section_name == "Education":
            if not re.search(r'\d{4}', content):
                suggestions.append("Include graduation dates for your degrees.")
        
        return suggestions

    def get_evaluation_summary(self) -> Dict[str, Any]:
        """Get summary of all evaluations"""
        if not self.evaluation_history:
            return {"message": "No evaluations performed yet"}
        
        total_evaluations = len(self.evaluation_history)
        avg_score = sum(result.overall_score for result in self.evaluation_history) / total_evaluations
        
        status_counts = {}
        for result in self.evaluation_history:
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_evaluations": total_evaluations,
            "average_score": round(avg_score, 1),
            "status_distribution": status_counts,
            "latest_evaluation": self.evaluation_history[-1].processing_metadata
        }

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_ats_engine() -> ATSRulesEngine:
    """Factory function to create ATS engine instance"""
    return ATSRulesEngine()

async def quick_ats_evaluation(cv_text: str, jd_text: str, role_profile: str = "default") -> Dict[str, Any]:
    """Quick ATS evaluation function for simple use cases"""
    engine = create_ats_engine()
    result = await engine.evaluate_cv(cv_text, jd_text, role_profile)
    
    return {
        "overall_score": result.overall_score,
        "compatibility_level": result.compatibility_level.value,
        "status": result.status.value,
        "category_scores": result.category_scores,
        "feedback": result.feedback,
        "improvement_recommendations": result.improvement_recommendations
    }

# ============================================================================
# EXPORT FUNCTIONS FOR INTEGRATION
# ============================================================================

# Main engine instance
ats_engine = create_ats_engine()

# Export key functions
async def evaluate_ats_compatibility(cv_text: str, jd_text: str, role_profile: str = "default") -> ATSEvaluationResult:
    """Main function for ATS compatibility evaluation"""
    return await ats_engine.evaluate_cv(cv_text, jd_text, role_profile)

async def extract_skills_unified(text: str) -> Dict[str, List[str]]:
    """Extract skills in unified format for backward compatibility"""
    skills = await ats_engine._extract_all_skills(text)
    
    return {
        "technical_skills": [skill.skill for skill in skills.get(SkillCategory.TECHNICAL, [])],
        "soft_skills": [skill.skill for skill in skills.get(SkillCategory.SOFT, [])],
        "domain_skills": [skill.skill for skill in skills.get(SkillCategory.DOMAIN, [])],
        "certifications": [skill.skill for skill in skills.get(SkillCategory.CERTIFICATION, [])]
    }

# Constants for backward compatibility
MIN_MATCH_THRESHOLD = 0.7
MAX_SKILLS_TO_SHOW = 15
MAX_SKILLS_TO_MATCH = 30

# Enhanced ATS matcher instance for backward compatibility
class EnhancedATSMatcher:
    def __init__(self):
        self.engine = ats_engine
    
    async def comprehensive_keyword_analysis(self, cv_text: str, jd_keywords: List[str]) -> Dict[str, Any]:
        """Comprehensive keyword analysis for backward compatibility"""
        # Convert keywords to skill matches format
        total_keywords = len(jd_keywords)
        if total_keywords == 0:
            return {
                "match_percentage": 0.0,
                "matched_keywords": [],
                "missing_keywords": [],
                "total_keywords": 0
            }
        
        # Simple keyword matching for backward compatibility
        cv_text_lower = cv_text.lower()
        matched_keywords = []
        missing_keywords = []
        
        for keyword in jd_keywords:
            if keyword.lower() in cv_text_lower:
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        match_percentage = (len(matched_keywords) / total_keywords) * 100
        
        return {
            "match_percentage": match_percentage,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "total_keywords": total_keywords
        }

# Export enhanced matcher instance
enhanced_ats_matcher = EnhancedATSMatcher()

if __name__ == "__main__":
    # Test the system
    import asyncio
    
    async def test_ats_engine():
        sample_cv = """
        John Doe
        Software Engineer
        
        Experience:
        - Developed web applications using Python and React
        - Improved system performance by 30%
        - Led a team of 5 developers
        - Managed $100K project budget
        
        Skills:
        Python, JavaScript, React, SQL, AWS, Docker, Git
        
        Education:
        Bachelor of Computer Science, 2020
        """
        
        sample_jd = """
        We are seeking a Senior Software Engineer with:
        
        Required Skills:
        - Python programming
        - React.js development
        - AWS cloud services
        - Team leadership
        - Project management
        
        Preferred:
        - Docker containerization
        - SQL databases
        - Agile methodologies
        """
        
        result = await evaluate_ats_compatibility(sample_cv, sample_jd, "software_engineer")
        print(f"Overall Score: {result.overall_score:.1f}")
        print(f"Status: {result.status.value}")
        print(f"Compatibility: {result.compatibility_level.value}")
        print("\nFeedback:")
        for feedback in result.feedback:
            print(f"- {feedback}")
    
    asyncio.run(test_ats_engine()) 