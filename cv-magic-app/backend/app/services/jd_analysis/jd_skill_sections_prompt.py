"""
Lightweight JD skill section prompt.

Generates concise technical/soft/domain skill lists for JD summaries.
"""

THREE_SECTION_SYSTEM_PROMPT = """You are a skilled job description analyzer. Extract skills and categorize them into technical skills, soft skills, and domain knowledge. Return ONLY valid JSON.

CATEGORIZATION RULES:
- TECHNICAL: Tools (SQL, Excel), processes (data cleaning, ETL), technical artifacts (dashboards)
- SOFT SKILLS: Human interaction + behavioral traits (communication, leadership)  
- DOMAIN: Industry-specific terms (Healthcare, Finance, Nonprofit, Fundraising, Marketing)

EXTRACTION RULES:
- Extract direct mentions AS-IS
- Remove qualifiers from ALL skills: "strong SQL" → "SQL", "proactive problem-solving" → "problem-solving"
- Remove behavioral adverbs: "work independently" → "independence", "collaborate effectively" → "collaboration"
- Common qualifiers to remove: "strong", "excellent", "proactive", "effective", "good", "advanced", "exceptional"
- Preserve specific tools: "Power BI" → "Power BI", "Tableau" → "Tableau"
- Extract ALL mentioned tools (if "Power BI, Tableau, etc." → extract both)
- Include implied skills from context
- Don't extract skills that are not mentioned in the job description
- Remove duplicates (same skill listed multiple times)
- For soft skills, extract the base skill without qualifiers: 'proactive problem solving' and 'problem-solving' should both become 'problem-solving'


def get_three_section_prompts(job_description: str) -> tuple[str, str]:
    """Return prompts for three-section JD extraction."""
    user_prompt = f"""Extract ALL skills from this job description and categorize them:
{job_description}

Return ONLY this JSON format (three sections only):
{{
    "technical_skills": [],
    "soft_skills": [], 
    "domain_knowledge": []
}}

Be comprehensive - extract ALL mentioned tools, technologies, processes, and domain terms."""

    return THREE_SECTION_SYSTEM_PROMPT, user_prompt

