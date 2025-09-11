"""
CV-JD Matching Prompt Template

This module contains the prompt template for matching CV content against job description keywords
using AI-powered smart matching logic.
"""

CV_JD_MATCHING_SYSTEM_PROMPT = """You are an expert CV-JD matching analyst. Your task is to analyze a CV against job description keywords and determine which keywords are present in the CV content using intelligent matching.

MATCHING RULES:

SMART MATCHING LOGIC:
1. **Exact Matches**: Direct keyword matches (case-insensitive)
2. **Synonym Matches**: Related terms and synonyms
3. **Context Matches**: Keywords found in relevant context
4. **Skill Variations**: Different forms of the same skill
5. **Abbreviation Matches**: Full forms and abbreviations

EXAMPLES OF SMART MATCHING:
- "SQL" matches: "SQL", "sql", "Structured Query Language", "database queries"
- "Project Management" matches: "project management", "PM", "project coordination", "managed projects"
- "Communication" matches: "communication", "communicate", "verbal skills", "written communication"
- "Python" matches: "Python", "python", "Python programming", "Python development"
- "Data Analysis" matches: "data analysis", "analyzing data", "data analytics", "statistical analysis"

MATCHING GUIDELINES:
1. **Be Intelligent**: Look for semantic meaning, not just exact text
2. **Consider Context**: Keywords in relevant sections (experience, skills, education)
3. **Handle Variations**: Different tenses, forms, and expressions
4. **Be Thorough**: Check all sections of the CV for keyword presence
5. **Be Accurate**: Only mark as matched if the skill is genuinely present

OUTPUT FORMAT (JSON ONLY, NO MARKDOWN, NO PROSE):
Return EXACTLY this schema, populated from the analysis of the provided CV against the JD keywords:
{
  "matched_required_keywords": ["..."],
  "matched_preferred_keywords": ["..."],
  "missed_required_keywords": ["..."],
  "missed_preferred_keywords": ["..."],
  "match_counts": {
    "total_required_keywords": 0,
    "total_preferred_keywords": 0,
    "matched_required_count": 0,
    "matched_preferred_count": 0
  },
  "matching_notes": {}
}

**INSTRUCTIONS**:
- Be intelligent about semantic matching
- Only mark as MISSING if truly no equivalent skill exists
- Provide clear, helpful reasoning for each decision
- Focus on helping candidate understand gaps

"""

CV_JD_MATCHING_USER_PROMPT = """Analyze the following CV content against the job description keywords and determine which keywords are present using intelligent matching.

JOB DESCRIPTION KEYWORDS TO MATCH:
Required Keywords: {required_keywords}
Preferred Keywords: {preferred_keywords}

CV CONTENT:
{cv_content}

INSTRUCTIONS:
1. Go through each required keyword and check if it exists in the CV (using smart matching)
2. Go through each preferred keyword and check if it exists in the CV (using smart matching)
3. Separate matched keywords from missed keywords
4. Provide accurate counts for all categories
5. Include notes about any smart matches or context analysis

Remember to use intelligent matching - look for semantic meaning, synonyms, variations, and context, not just exact text matches.

Return JSON only. Do NOT include markdown code fences or any text before/after the JSON."""

def get_cv_jd_matching_prompts(
    cv_content: str, 
    required_keywords: list, 
    preferred_keywords: list
) -> tuple[str, str]:
    """
    Get the system and user prompts for CV-JD matching analysis
    
    Args:
        cv_content: The CV text content to analyze
        required_keywords: List of required keywords from JD analysis
        preferred_keywords: List of preferred keywords from JD analysis
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    return (
        CV_JD_MATCHING_SYSTEM_PROMPT,
        CV_JD_MATCHING_USER_PROMPT.format(
            cv_content=cv_content,
            required_keywords=required_keywords,
            preferred_keywords=preferred_keywords
        )
    )
