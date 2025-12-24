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

OUTPUT FORMAT:
Return a JSON object with this exact structure:

{
  "matched_keywords": ["keyword1", "keyword2", "keyword3"],
  "missed_keywords": ["keyword4", "keyword5"],
  "match_counts": {
    "total_keywords": 5,
    "matched_count": 3,
    "missed_count": 2
  },
  "matching_notes": {
    "Excel": "Found in technical skills section",
    "SQL": "Mentioned multiple times in experience",
    "Python": "Explicitly listed and used in projects"
  }
}

MATCHING NOTES REQUIREMENTS:
- Provide notes for ALL MATCHED keywords explaining where/how they were found
- Optionally provide notes for MISSED keywords if they're borderline cases or close matches
- Format: {"keyword": "brief explanation (10 words max)"}
- Focus on helping candidate understand where skills appear and why keywords were matched/missed
- Examples:
  * Matched: "SQL" → "Found in database experience section"
  * Matched: "Python" → "Listed in technical skills and used in projects"
  * Missed (optional): "VBA" → "Not mentioned, but Excel experience suggests familiarity"

INSTRUCTIONS:
- Be intelligent about semantic matching
- Only mark as MISSING if truly no equivalent skill exists
- Provide clear, helpful reasoning for each matched keyword in matching_notes
- Focus on helping candidate understand gaps and where their skills appear

"""

CV_JD_MATCHING_USER_PROMPT = """Analyze the following CV content against the job description keywords and determine which keywords are present using intelligent matching.

JOB DESCRIPTION KEYWORDS TO MATCH:
Keywords: {all_keywords}

CV CONTENT:
{cv_content}

INSTRUCTIONS:
1. Go through each keyword and check if it exists in the CV (using smart matching)
2. Separate matched keywords from missed keywords
3. Provide accurate counts
4. For matching_notes: Include notes for ALL matched keywords (required). Optionally include notes for missed keywords if they're borderline cases

Remember to use intelligent matching - look for semantic meaning, synonyms, variations, and context, not just exact text matches.

Return ONLY the JSON response with no additional text."""

def get_cv_jd_matching_prompts(
    cv_content: str,
    all_keywords: list
) -> tuple[str, str]:
    """
    Get the system and user prompts for CV-JD matching analysis

    Args:
        cv_content: The CV text content to analyze
        all_keywords: List of all keywords from JD three_section_skills

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    return (
        CV_JD_MATCHING_SYSTEM_PROMPT,
        CV_JD_MATCHING_USER_PROMPT.format(
            cv_content=cv_content,
            all_keywords=all_keywords
        )
    )
