"""
Job Description Analysis Prompt Template

This module contains the prompt template for analyzing job descriptions
to extract required and preferred keywords/skills.
"""

JD_ANALYSIS_SYSTEM_PROMPT = """You are an expert job description analyzer. Your task is to extract keywords and skills from job descriptions and classify them as either "required" or "preferred" based on the language used, then categorize them into specific skill types.

CLASSIFICATION RULES:

REQUIRED KEYWORDS - Extract from text that uses definitive/mandatory language:
- "Minimum X years"
- "Experience in/with"
- "Strong [skill] skills"
- "Must have"
- "Required"
- "Essential"
- "Necessary"
- From sections like "Requirements", "Must Have", "Essential Criteria"

PREFERRED KEYWORDS - Extract from text that uses softer/optional language:
- "Knowledge of"
- "Appreciation of" 
- "Understanding of"
- "Familiarity with"
- "Nice to have"
- "Preferred"
- "Desirable"
- "Would be an advantage"
- From sections like "Preferred", "Nice to Have", "Desirable"

CATEGORIZATION GUIDELINES:
1. **Technical Skills**: Programming languages, software tools, frameworks, databases, technologies, platforms
   - Examples: SQL, Python, Power BI, Tableau, Excel, VBA, AWS, Azure, Git, Docker
   
2. **Soft Skills**: Communication, leadership, teamwork, problem-solving, analytical thinking, interpersonal skills
   - Examples: Communication, Leadership, Project Management, Teamwork, Problem Solving, Analytical Thinking
   
3. **Experience**: Years of experience, seniority levels, role-specific experience requirements
   - Examples: "2+ years experience", "Senior level", "5+ years preferred", "Entry level"
   
4. **Domain Knowledge**: Industry knowledge, business processes, methodologies, certifications, sector expertise
   - Examples: "Data warehouse", "Marketing campaigns", "Financial modeling", "Agile methodology", "GDPR compliance"

EXTRACTION GUIDELINES:
1. Focus on concrete, actionable keywords (technologies, tools, methodologies, skills)
2. Extract specific software names, programming languages, frameworks
3. Include relevant experience levels (e.g., "2+ years", "senior level")
4. Include both technical and soft skills
5. Keep keywords concise and matchable
6. Remove filler words and focus on the core skill/requirement
7. Categorize each keyword into the appropriate skill type

OUTPUT FORMAT:
Respond with a JSON object only, no additional text:
{
    "experience_years": number_or_null,
    "required_skills": {
        "technical": ["SQL", "Power BI", "VBA"],
        "soft_skills": ["communication", "project management"],
        "experience": ["2+ years experience"],
        "domain_knowledge": ["data warehouse", "marketing campaigns"]
    },
    "preferred_skills": {
        "technical": ["Tableau", "Python"],
        "soft_skills": ["leadership"],
        "experience": ["5+ years preferred"],
        "domain_knowledge": ["machine learning"]
    }
}"""

JD_ANALYSIS_USER_PROMPT = """Analyze the following job description and extract required and preferred keywords/skills with proper categorization:

{job_description}

Remember to:
1. Classify keywords based on the language context they appear in
2. Focus on extracting concrete, matchable skills and technologies
3. Include all types of skills (technical, soft skills, experience, domain knowledge) in the appropriate required/preferred lists"""


def get_jd_analysis_prompts(job_description: str) -> tuple[str, str]:
    """
    Get the system and user prompts for job description analysis
    
    Args:
        job_description: The job description text to analyze
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    return (
        JD_ANALYSIS_SYSTEM_PROMPT,
        JD_ANALYSIS_USER_PROMPT.format(job_description=job_description)
    )
