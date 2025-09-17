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

        # Add structured output format
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

OUTPUT FORMAT:
Return ONLY a complete CV in the exact same format as input, with tailored content for:
- Summary/Objective
- Experience bullets
- Skills section
- Project descriptions
- Education details (if relevant)
"""

        return prompt

    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt for CV tailoring"""
        return "You are a professional CV optimization expert. Focus on highlighting relevant experience and skills while maintaining accuracy and professional tone."