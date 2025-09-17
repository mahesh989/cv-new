"""
Keyword Injection System

Forces integration of critical missing keywords into CV content through
intelligent code-level placement rather than AI compliance.
"""

import re
from typing import List, Dict, Any, Set, Tuple
import logging

logger = logging.getLogger(__name__)


class KeywordInjector:
    """Force integration of critical missing keywords into CV content"""
    
    # Context mapping for intelligent keyword placement
    KEYWORD_CONTEXT_MAP = {
        # Non-profit/Humanitarian keywords
        "fundraising": {
            "contexts": ["financial", "budget", "revenue", "cost", "analysis"],
            "templates": [
                "with applications to fundraising analytics",
                "supporting fundraising data initiatives",
                "enabling data-driven fundraising strategies"
            ]
        },
        "international aid": {
            "contexts": ["global", "cross", "multiple", "diverse", "distributed"],
            "templates": [
                "applicable to international aid programs",
                "supporting international aid distribution",
                "aligned with international aid objectives"
            ]
        },
        "non-profit sector": {
            "contexts": ["organization", "stakeholder", "impact", "efficiency"],
            "templates": [
                "optimized for non-profit sector requirements",
                "tailored to non-profit sector needs",
                "addressing non-profit sector challenges"
            ]
        },
        "humanitarian": {
            "contexts": ["support", "assist", "help", "impact", "benefit"],
            "templates": [
                "supporting humanitarian missions",
                "with humanitarian impact focus",
                "enabling humanitarian data insights"
            ]
        },
        
        # Technical keywords
        "data mining": {
            "contexts": ["analysis", "extract", "pattern", "insight", "discover"],
            "templates": [
                "using data mining techniques",
                "leveraging data mining for insights",
                "applying data mining methodologies"
            ]
        },
        "project management": {
            "contexts": ["led", "coordinated", "delivered", "managed", "oversaw"],
            "templates": [
                "demonstrating project management expertise",
                "with strong project management focus",
                "utilizing project management best practices"
            ]
        },
        "stakeholder management": {
            "contexts": ["collaborated", "presented", "communicated", "aligned"],
            "templates": [
                "ensuring effective stakeholder management",
                "with focus on stakeholder management",
                "demonstrating stakeholder management skills"
            ]
        },
        "business intelligence": {
            "contexts": ["dashboard", "report", "metric", "kpi", "visualization"],
            "templates": [
                "delivering business intelligence solutions",
                "enabling business intelligence insights",
                "supporting business intelligence initiatives"
            ]
        }
    }
    
    def inject_keywords(
        self, 
        cv_content: Dict[str, Any], 
        required_keywords: List[str],
        force_injection: bool = True
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        Force integration of critical missing keywords
        
        Args:
            cv_content: CV data dictionary
            required_keywords: List of keywords that must be integrated
            force_injection: If True, force keywords even without perfect context
            
        Returns:
            Tuple of (enhanced_cv, successfully_injected_keywords)
        """
        injected_keywords = []
        cv_content = cv_content.copy()  # Don't modify original
        
        for keyword in required_keywords:
            keyword_lower = keyword.lower()
            
            # Check if keyword already exists
            if self._keyword_exists(cv_content, keyword_lower):
                injected_keywords.append(keyword)
                logger.info(f"Keyword '{keyword}' already exists in CV")
                continue
            
            # Try to inject in experience section first
            if self._inject_in_experience(cv_content, keyword_lower):
                injected_keywords.append(keyword)
                logger.info(f"✅ Injected '{keyword}' in experience section")
                continue
            
            # Try skills section next
            if self._inject_in_skills(cv_content, keyword_lower):
                injected_keywords.append(keyword)
                logger.info(f"✅ Injected '{keyword}' in skills section")
                continue
            
            # Force injection if required
            if force_injection:
                self._force_inject(cv_content, keyword_lower)
                injected_keywords.append(keyword)
                logger.warning(f"⚠️ Force-injected '{keyword}' - review placement")
        
        return cv_content, injected_keywords
    
    def _keyword_exists(self, cv_content: Dict[str, Any], keyword: str) -> bool:
        """Check if keyword already exists in CV"""
        cv_text = self._extract_all_text(cv_content).lower()
        return keyword in cv_text
    
    def _extract_all_text(self, cv_content: Dict[str, Any]) -> str:
        """Extract all text from CV for analysis"""
        text_parts = []
        
        # Experience bullets
        for exp in cv_content.get("experience", []):
            text_parts.extend(exp.get("bullets", []))
        
        # Skills
        for skill_cat in cv_content.get("skills", []):
            text_parts.extend(skill_cat.get("skills", []))
            text_parts.append(skill_cat.get("category", ""))
        
        # Projects if available
        if cv_content.get("projects"):
            for project in cv_content["projects"]:
                text_parts.extend(project.get("bullets", []))
                text_parts.append(project.get("name", ""))
        
        return " ".join(text_parts)
    
    def _inject_in_experience(self, cv_content: Dict[str, Any], keyword: str) -> bool:
        """Try to inject keyword in relevant experience bullet"""
        
        keyword_context = self.KEYWORD_CONTEXT_MAP.get(keyword, {})
        contexts = keyword_context.get("contexts", [])
        templates = keyword_context.get("templates", [])
        
        for exp in cv_content.get("experience", []):
            for i, bullet in enumerate(exp.get("bullets", [])):
                bullet_lower = bullet.lower()
                
                # Check if bullet has relevant context
                for context in contexts:
                    if context in bullet_lower and keyword not in bullet_lower:
                        # Found relevant context - inject keyword
                        template = templates[0] if templates else f"with {keyword} applications"
                        
                        # Smart injection based on bullet structure
                        if bullet.rstrip().endswith('.'):
                            enhanced_bullet = bullet[:-1] + f", {template}."
                        else:
                            enhanced_bullet = bullet + f", {template}"
                        
                        exp["bullets"][i] = enhanced_bullet
                        return True
        
        return False
    
    def _inject_in_skills(self, cv_content: Dict[str, Any], keyword: str) -> bool:
        """Try to inject keyword in skills section"""
        
        # Determine best category for keyword
        if any(tech in keyword for tech in ["data", "mining", "intelligence", "analytics"]):
            target_category = "technical"
        elif any(mgmt in keyword for mgmt in ["management", "stakeholder", "project"]):
            target_category = "soft"
        else:
            target_category = "domain"
        
        for skill_cat in cv_content.get("skills", []):
            cat_name = skill_cat.get("category", "").lower()
            
            if target_category in cat_name or len(cv_content.get("skills", [])) == 1:
                # Add keyword to this category
                skills = skill_cat.get("skills", [])
                
                # Capitalize properly
                formatted_keyword = keyword.title() if len(keyword.split()) > 1 else keyword.capitalize()
                
                if formatted_keyword not in skills:
                    skills.append(formatted_keyword)
                    skill_cat["skills"] = skills
                    return True
        
        return False
    
    def _force_inject(self, cv_content: Dict[str, Any], keyword: str) -> None:
        """Force keyword injection when no good context found"""
        
        # Find the most recent/relevant experience entry
        if cv_content.get("experience"):
            exp = cv_content["experience"][0]  # Most recent
            bullets = exp.get("bullets", [])
            
            if bullets:
                # Enhance the first bullet with keyword context
                template = self.KEYWORD_CONTEXT_MAP.get(keyword, {}).get("templates", [f"with {keyword} focus"])[0]
                
                bullet = bullets[0]
                if bullet.rstrip().endswith('.'):
                    bullets[0] = bullet[:-1] + f", {template}."
                else:
                    bullets[0] = bullet + f", {template}"
                
                exp["bullets"] = bullets
        
        # Also add to skills as backup
        if not cv_content.get("skills"):
            cv_content["skills"] = [{"category": "Additional Skills", "skills": []}]
        
        cv_content["skills"][0]["skills"].append(keyword.title())
    
    def validate_keyword_integration(
        self, 
        cv_content: Dict[str, Any], 
        required_keywords: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all required keywords are present
        
        Returns:
            Tuple of (all_present, missing_keywords)
        """
        cv_text = self._extract_all_text(cv_content).lower()
        missing_keywords = []
        
        for keyword in required_keywords:
            if keyword.lower() not in cv_text:
                missing_keywords.append(keyword)
        
        return len(missing_keywords) == 0, missing_keywords
    
    def generate_keyword_examples(self, keywords: List[str], role: str) -> Dict[str, List[str]]:
        """Generate examples of how to integrate keywords naturally"""
        
        examples = {}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            if "fundraising" in keyword_lower:
                examples[keyword] = [
                    f"Analyzed donor data to optimize fundraising campaigns, increasing donations by 35%",
                    f"Developed Python-based fundraising analytics dashboard tracking $5M in annual contributions",
                    f"Applied data mining techniques to fundraising databases, identifying 500+ high-value prospects"
                ]
            elif "international" in keyword_lower:
                examples[keyword] = [
                    f"Managed data systems supporting international aid distribution across 20 countries",
                    f"Analyzed international aid program metrics, improving efficiency by 40%",
                    f"Built reporting framework for international aid initiatives reaching 50K+ beneficiaries"
                ]
            elif "non-profit" in keyword_lower or "nonprofit" in keyword_lower:
                examples[keyword] = [
                    f"Optimized data processes for non-profit sector, reducing operational costs by 25%",
                    f"Developed analytics solutions tailored to non-profit sector requirements",
                    f"Led data initiatives supporting non-profit sector growth and sustainability"
                ]
            elif "project management" in keyword_lower:
                examples[keyword] = [
                    f"Demonstrated strong project management skills delivering 10+ projects on time",
                    f"Applied project management methodologies to coordinate cross-functional teams",
                    f"Led data initiatives using agile project management, improving delivery speed by 30%"
                ]
            else:
                # Generic examples
                examples[keyword] = [
                    f"Applied {keyword} expertise to drive operational improvements",
                    f"Leveraged {keyword} skills to enhance team productivity by 25%",
                    f"Demonstrated {keyword} capabilities across multiple projects"
                ]
        
        return examples


# Create global instance
keyword_injector = KeywordInjector()