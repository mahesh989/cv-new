"""
Dynamic AI Recommendation Prompt for 

This module provides the AI prompt template for generating CV recommendations.
"""

def get_prompt() -> str:
    """Generate the AI recommendation prompt"""
    return """
Analyze this job requirement data and provide specific CV optimization recommendations:

COMPANY REQUIREMENTS:
- Required Technical Skills: []
- Required Soft Skills: []
- Preferred Technical Skills: []
- Preferred Soft Skills: []
- Experience Required: 0 years

PROVIDE RECOMMENDATIONS FOR:
1. Skills to Emphasize
2. Experience Highlights
3. CV Structure Optimization
4. Keywords to Include
5. Formatting Suggestions

Format your response as structured recommendations with clear sections and bullet points.
"""
