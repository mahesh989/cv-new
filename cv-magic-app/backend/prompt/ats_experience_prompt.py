"""
Experience Alignment Analysis Prompt

Analyzes experience alignment between CV and JD requirements for ATS scoring.
"""

EXPERIENCE_ALIGNMENT_PROMPT = """
You are an expert hiring manager with 15+ years of experience. Analyze experience alignment between CV and JD requirements.

CV TEXT: {cv_text}
JD REQUIREMENTS: {jd_text}

## Scoring Guidelines (0-100 scale):
- 90-100: Excellent match, minimal gaps
- 75-89: Strong fit, minor development needed
- 60-74: Good fit, moderate gaps manageable
- 40-59: Some alignment, significant development required
- 25-39: Limited fit, major gaps present
- 0-24: Poor match, substantial mismatch

## EXPERIENCE ALIGNMENT ANALYSIS
Analyze experience alignment between CV and JD requirements. Extract and analyze:
1. Years of experience
2. Role level progression
3. Responsibility scope and complexity
4. Achievement quantifications
5. Leadership/management indicators

Return JSON only:
{{
 "experience_analysis": {{
   "cv_experience_years": 4,
   "cv_role_level": "Mid-Senior",
   "cv_progression": ["Junior Developer", "Senior Developer", "Team Lead"],
   "jd_required_years": "3-5 years",
   "jd_role_level": "Senior",
   "alignment_score": 85,
   "experience_gaps": [],
   "experience_strengths": ["Leadership experience", "Technical progression"],
   "quantified_achievements": ["Led team of 5", "Improved performance by 40%"]
 }}
}}
"""
