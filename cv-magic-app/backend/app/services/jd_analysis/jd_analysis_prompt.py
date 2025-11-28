"""
Job Description Analysis Prompt Template - Pattern-Based with Minimal Examples
Updated to prioritize pattern recognition over example memorization.
"""

JD_ANALYSIS_SYSTEM_PROMPT = """You are a skilled job description analyzer. Extract skills and categorize them into technical, soft skills, and domain knowledge. Return only valid JSON."""

JD_ANALYSIS_USER_PROMPT = """Extract skills from this job description and categorize them:

{job_description}

Return JSON format:
{{
    "experience_years": number,
    "required_skills": {{
        "technical": [],
        "soft_skills": [], 
        "domain_knowledge": []
    }},
    "preferred_skills": {{
        "technical": [],
        "soft_skills": [],
        "domain_knowledge": []
    }}
}}"""


def get_jd_analysis_prompts(job_description: str) -> tuple[str, str]:
    """
    Get system and user prompts for job description analysis
    
    Args:
        job_description: The job description text to analyze
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    return (
        JD_ANALYSIS_SYSTEM_PROMPT,
        JD_ANALYSIS_USER_PROMPT.format(job_description=job_description)
    )