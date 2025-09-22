"""
CV Tailoring Prompt Templates

This module contains all the prompt templates used for CV tailoring
"""

import logging
from typing import Dict, List, Optional
from app.models.optimization_strategy import OptimizationStrategy

logger = logging.getLogger(__name__)

class CVTailoringPrompts:
    """Centralized prompt templates for CV tailoring"""
    
    @staticmethod
    def get_cv_tailoring_template(
        original_cv: Dict,
        recommendations: Dict,
        strategy: OptimizationStrategy,
        custom_instructions: Optional[str] = None
    ) -> str:
        """
        Create standardized prompt for CV tailoring

        Args:
            original_cv: Original CV data
            recommendations: Recommendation analysis data
            strategy: Optimization strategy to apply
            custom_instructions: Optional custom instructions

        Returns:
            Formatted prompt string
        """
        # Header with instructions
        prompt = f"""You are a senior CV optimization expert. Tailor this CV for {recommendations['company']} based on their job requirements.

ORIGINAL CV:
{original_cv}

COMPANY REQUIREMENTS:
{recommendations}

OPTIMIZATION STRATEGY:
- Education: {strategy.education_strategy}
- Experience: {strategy.experience_strategy}
- Skills: {strategy.skills_strategy}
- Projects: {strategy.projects_strategy}
"""

        # Add custom instructions if provided
        if custom_instructions:
            prompt += f"\nCUSTOM INSTRUCTIONS:\n{custom_instructions}\n"

        # Add structured output format and strict skills taxonomy
        prompt += """
RULES:
1. Keep original CV structure and section order
2. Highlight relevant skills and achievements
3. Match company's tone and terminology
4. Remove irrelevant content
5. Ensure all dates and facts remain accurate
6. Focus on quantifiable achievements
7. Use action verbs
8. Maintain professional formatting

STRICT SKILLS TAXONOMY (VERY IMPORTANT):
- Technical Skills: ONLY tools/technologies/platforms/languages/frameworks (e.g., Python, SQL, Excel, Power BI, VBA, Tableau, Snowflake, AWS). Do NOT include domain concepts.
- Domain Expertise (or Sector Skills): Industry/domain concepts and practices (e.g., International Aid and Development, Fundraising, Not for Profit (NFP), Humanitarian Emergencies, Community Engagement, Social Impact, Donor-Centricity).
- Soft Skills: Communication, leadership, stakeholder management, collaboration, problem solving, etc.

ENFORCEMENT:
- If a skill is a domain concept, place it under "Domain Expertise", not under "Technical Skills".
- If there are no true technical tools relevant to the role, leave non-relevant ones out; do NOT fill "Technical Skills" with domain terms.
- Prefer technical tools explicitly present in the JD/company requirements or the original CV; avoid hallucinations.
- Keep skills concise; comma-separated, no duplicates.

OUTPUT FORMAT:
Return ONLY a complete CV in the exact same format as input, with tailored content for:
- Summary/Objective
- Experience bullets
- Skills section with three clear sub-sections: Technical Skills, Domain Expertise (or Sector Skills), Soft Skills
- Project descriptions
- Education details (if relevant)
"""

        return prompt

    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt for CV tailoring"""
        return "You are a professional CV optimization expert. Focus on highlighting relevant experience and skills while maintaining accuracy and professional tone."