"""
Quantification Enforcer Module

Ensures every bullet point has quantifiable metrics through code-level enforcement
rather than relying on AI compliance.
"""

import re
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class QuantificationEnforcer:
    """Enforce quantification in CV bullet points through code-level injection"""
    
    # Default quantification patterns based on context
    QUANTIFICATION_PATTERNS = {
        # Data/Analytics patterns
        "data pipeline": "improving efficiency by 30%",
        "data analysis": "analyzing 100K+ records",
        "dashboard": "creating 10+ dashboards for 50+ stakeholders",
        "report": "generating weekly reports reducing decision time by 40%",
        
        # Development patterns
        "python script": "automating 20+ hours/week of manual tasks",
        "machine learning": "achieving 85% accuracy",
        "model": "improving predictions by 25%",
        "api": "handling 1000+ requests/day",
        "database": "optimizing queries by 60%",
        
        # Process improvements
        "improved": "improved by 35%",
        "reduced": "reduced by 40%",
        "increased": "increased by 25%",
        "enhanced": "enhanced performance by 30%",
        "optimized": "optimized efficiency by 45%",
        
        # Team/Management
        "team": "team of 5-8 members",
        "led": "led initiatives impacting 100+ users",
        "managed": "managed $500K+ budget",
        "collaborated": "collaborated with 3+ departments",
        "mentored": "mentored 5+ junior analysts",
        
        # Time-based
        "delivered": "delivered 2 weeks ahead of schedule",
        "completed": "completed within 3-month timeline",
        "implemented": "implemented in 6 weeks",
    }
    
    # Industry-specific quantification for UNHCR/Non-profit
    NONPROFIT_QUANTIFICATION = {
        "fundraising": "supporting $2M+ annual fundraising campaigns",
        "donor": "managing 500+ donor relationships",
        "international": "across 15+ countries",
        "humanitarian": "impacting 10,000+ beneficiaries",
        "aid": "distributing aid to 5,000+ families",
        "non-profit": "reducing operational costs by 20%",
        "stakeholder": "presenting to 20+ stakeholders monthly",
    }
    
    def enforce_quantification(
        self, 
        bullets: List[str], 
        company_context: str = None,
        role_level: str = "mid"
    ) -> List[str]:
        """
        Force quantification into every bullet point
        
        Args:
            bullets: List of bullet points to enhance
            company_context: Company name/type for context-specific quantification
            role_level: Seniority level (entry/mid/senior) for appropriate metrics
            
        Returns:
            List of quantified bullet points
        """
        quantified_bullets = []
        
        for bullet in bullets:
            if not self._has_quantification(bullet):
                quantified_bullet = self._inject_quantification(bullet, company_context, role_level)
                logger.info(f"Quantified: '{bullet[:50]}...' → '{quantified_bullet[:50]}...'")
            else:
                quantified_bullet = bullet
                
            quantified_bullets.append(quantified_bullet)
            
        return quantified_bullets
    
    def _has_quantification(self, bullet: str) -> bool:
        """Check if bullet already has quantification"""
        # Check for numbers, percentages, dollar amounts
        has_number = bool(re.search(r'\d+', bullet))
        has_percentage = '%' in bullet
        has_dollar = '$' in bullet
        has_timeframe = bool(re.search(r'\d+\s*(hours?|days?|weeks?|months?|years?)', bullet, re.IGNORECASE))
        
        return has_number or has_percentage or has_dollar or has_timeframe
    
    def _inject_quantification(self, bullet: str, company_context: str = None, role_level: str = "mid") -> str:
        """Inject appropriate quantification based on context"""
        
        bullet_lower = bullet.lower()
        
        # First check for non-profit context
        if company_context and any(keyword in company_context.lower() for keyword in ['unhcr', 'nonprofit', 'humanitarian', 'aid']):
            for keyword, quantification in self.NONPROFIT_QUANTIFICATION.items():
                if keyword in bullet_lower:
                    # Insert quantification intelligently
                    return self._smart_inject(bullet, quantification)
        
        # Check general patterns
        for pattern, quantification in self.QUANTIFICATION_PATTERNS.items():
            if pattern in bullet_lower:
                return self._smart_inject(bullet, quantification)
        
        # Fallback quantification based on role level
        if role_level == "entry":
            default_quant = "achieving 15% improvement in first 6 months"
        elif role_level == "senior":
            default_quant = "driving $1M+ in value annually"
        else:  # mid-level
            default_quant = "improving efficiency by 25% across 3 projects"
            
        # Insert at the end if no better place found
        if bullet.rstrip().endswith('.'):
            return bullet[:-1] + f", {default_quant}."
        else:
            return bullet + f", {default_quant}"
    
    def _smart_inject(self, bullet: str, quantification: str) -> str:
        """Intelligently inject quantification into bullet"""
        
        # Common injection points
        improvement_words = ['improving', 'enhancing', 'optimizing', 'reducing', 'increasing']
        action_words = ['created', 'developed', 'built', 'designed', 'implemented']
        
        for word in improvement_words:
            if word in bullet.lower():
                # Replace the vague word with quantified version
                pattern = re.compile(rf'\b{word}\b', re.IGNORECASE)
                return pattern.sub(quantification, bullet, count=1)
        
        for word in action_words:
            if word in bullet.lower():
                # Add quantification after the action
                pattern = re.compile(rf'({word}\s+\S+)', re.IGNORECASE)
                return pattern.sub(rf'\1, {quantification},', bullet, count=1)
        
        # Default: add before the last period
        if bullet.rstrip().endswith('.'):
            return bullet[:-1] + f", {quantification}."
        else:
            return bullet + f", {quantification}"
    
    def validate_quantification_rate(self, bullets: List[str]) -> Tuple[bool, float, List[str]]:
        """
        Validate that all bullets have quantification
        
        Returns:
            Tuple of (is_valid, quantification_rate, failed_bullets)
        """
        failed_bullets = []
        quantified_count = 0
        
        for bullet in bullets:
            if self._has_quantification(bullet):
                quantified_count += 1
            else:
                failed_bullets.append(bullet)
        
        rate = (quantified_count / len(bullets) * 100) if bullets else 0
        is_valid = rate == 100.0
        
        return is_valid, rate, failed_bullets
    
    def generate_quantification_examples(self, role: str, industry: str) -> List[str]:
        """Generate role and industry-specific quantification examples"""
        
        examples = []
        
        # Role-specific examples
        if "analyst" in role.lower():
            examples.extend([
                "Analyzed 1M+ customer records using Python/SQL, identifying $2.5M revenue opportunity",
                "Built 15 Tableau dashboards tracking KPIs for 200+ stakeholders across 5 departments",
                "Reduced data processing time by 65% through Python automation, saving 30 hours/week"
            ])
        elif "engineer" in role.lower():
            examples.extend([
                "Developed microservices handling 10K requests/second with 99.9% uptime",
                "Optimized database queries reducing response time from 5s to 200ms (96% improvement)",
                "Led migration of 50+ applications to cloud, reducing infrastructure costs by $500K/year"
            ])
        
        # Industry-specific examples
        if "nonprofit" in industry.lower() or "humanitarian" in industry.lower():
            examples.extend([
                "Managed donor database of 5,000+ contacts, increasing retention rate by 35%",
                "Analyzed program data across 20 countries, improving aid distribution efficiency by 40%",
                "Developed impact reports reaching 10,000+ stakeholders, securing $3M in funding"
            ])
        
        return examples


# Create global instance
quantification_enforcer = QuantificationEnforcer()