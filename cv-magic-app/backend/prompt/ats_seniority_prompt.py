"""
Role Seniority Analysis Prompt

Analyzes role seniority fit for ATS scoring.
"""

ROLE_SENIORITY_PROMPT = """
You are an expert hiring manager with 15+ years of experience. Analyze role seniority fit.

CV TEXT: {cv_text}
JD REQUIREMENTS: {jd_text}

## Scoring Guidelines (0-100 scale):
- 90-100: Excellent match, minimal gaps
- 75-89: Strong fit, minor development needed
- 60-74: Good fit, moderate gaps manageable
- 40-59: Some alignment, significant development required
- 25-39: Limited fit, major gaps present
- 0-24: Poor match, substantial mismatch

## ROLE SENIORITY ANALYSIS
Analyze role seniority fit. Extract and analyze:
1. Responsibility scope
2. Leadership indicators
3. Decision-making authority
4. Career progression trajectory
5. Mentoring/coaching activities

Return JSON only:
{{
 "seniority_analysis": {{
   "cv_experience_years": 6,
   "cv_responsibility_scope": "Senior Individual Contributor",
   "cv_leadership_indicators": 7,
   "cv_decision_authority": "Project Level",
   "cv_stakeholder_level": "Department",
   "jd_required_seniority": "Senior",
   "jd_leadership_requirements": "Team Leadership Expected",
   "jd_decision_authority_needed": "Program Level",
   "jd_stakeholder_level": "Executive",
   "seniority_score": 75,
   "experience_match_percentage": 85,
   "responsibility_fit_percentage": 70,
   "leadership_readiness_score": 65,
   "growth_trajectory_score": 80,
   "seniority_strengths": ["Strong Technical Leadership", "Cross-functional Collaboration"],
   "seniority_gaps": ["Direct Report Management", "Executive Stakeholder Management"],
   "readiness_assessment": "Stretch Role with Development Support"
 }}
}}
"""
