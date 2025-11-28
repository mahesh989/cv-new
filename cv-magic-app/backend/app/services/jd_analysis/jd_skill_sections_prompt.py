"""
Lightweight JD skill section prompt.

Generates concise technical/soft/domain skill lists for JD summaries.
"""

THREE_SECTION_SYSTEM_PROMPT = """You are a skilled job description analyzer.
Extract all explicitly or implicitly mentioned skills and categorize them into
technical skills, soft skills, and domain knowledge. Return ONLY valid JSON.

CATEGORIZATION RULES:
- TECHNICAL: Tools (SQL, Excel), processes (data cleaning, ETL), technical artifacts (dashboards)
- SOFT SKILLS: Human interaction + behavioral traits (communication, leadership)
- DOMAIN: Industry/sector/mission-specific terms (Healthcare, Finance, Nonprofit)

EXTRACTION RULES:
- Extract direct mentions AS-IS
- Remove qualifiers: "strong SQL" → "SQL"
- Preserve specific tools: "Power BI" → "Power BI"
- Include implied skills when clearly supported by context
- Exclude skills that are not mentioned or cannot be inferred from the JD
"""


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

Be comprehensive – capture every tool, technology, process, soft skill, and domain term that appears."""

    return THREE_SECTION_SYSTEM_PROMPT, user_prompt

