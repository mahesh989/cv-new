"""
Skills Relevance Analysis Prompt

Analyzes skills relevance beyond simple keyword matching for ATS scoring.
"""

SKILLS_RELEVANCE_PROMPT = """
You are an expert hiring manager with 15+ years of experience. Analyze skills relevance beyond simple keyword matching.

CV TEXT: {cv_text}
JD REQUIREMENTS: {jd_text}
MATCHED SKILLS: {matched_skills}

## Scoring Guidelines (0-100 scale):
- 90-100: Excellent match, minimal gaps
- 75-89: Strong fit, minor development needed
- 60-74: Good fit, moderate gaps manageable
- 40-59: Some alignment, significant development required
- 25-39: Limited fit, major gaps present
- 0-24: Poor match, substantial mismatch

## SKILLS RELEVANCE ANALYSIS
Analyze skills relevance beyond simple keyword matching. For each matched skill, analyze:
1. Context Relevance
2. Skill Level (Beginner/Intermediate/Advanced/Expert)
3. Application Depth
4. Synergy Score

Return JSON only:
{{
 "skills_analysis": [
   {{
     "skill": "Python",
     "cv_evidence": "3+ years, pandas, scikit-learn, multiple projects",
     "jd_application": "Data analysis and automation tasks",
     "relevance_score": 95,
     "skill_level": "Advanced",
     "depth_indicators": ["Multiple libraries", "Project leadership", "3+ years"],
     "synergy_bonus": 10
   }}
 ],
 "overall_skills_score": 87,
 "strength_areas": ["Data Analysis", "Programming"],
 "improvement_areas": ["Database Administration", "Cloud Platforms"]
}}
"""
