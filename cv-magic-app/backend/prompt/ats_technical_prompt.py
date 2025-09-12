"""
Technical Depth Analysis Prompt

Analyzes technical sophistication and depth for ATS scoring.
"""

TECHNICAL_DEPTH_PROMPT = """
You are an expert hiring manager with 15+ years of experience. Analyze technical sophistication and depth.

CV TEXT: {cv_text}
JD REQUIREMENTS: {jd_text}

## Scoring Guidelines (0-100 scale):
- 90-100: Excellent match, minimal gaps
- 75-89: Strong fit, minor development needed
- 60-74: Good fit, moderate gaps manageable
- 40-59: Some alignment, significant development required
- 25-39: Limited fit, major gaps present
- 0-24: Poor match, substantial mismatch

## TECHNICAL DEPTH ANALYSIS
Analyze technical sophistication and depth. Extract and analyze:
1. Sophistication level
2. Core competency depth
3. Problem complexity handled
4. Innovation contributions
5. Technical leadership activities

Return JSON only:
{{
 "technical_analysis": {{
   "cv_sophistication_level": "Advanced",
   "cv_primary_domain": "Machine Learning & Data Science",
   "cv_core_competencies": ["Python", "SQL", "ML Algorithms", "Data Visualization"],
   "cv_problem_complexity": 8,
   "cv_innovation_indicators": ["Published Research", "Framework Development"],
   "jd_required_sophistication": "Intermediate",
   "jd_core_tech_stack": ["Python", "SQL", "Tableau", "Excel"],
   "jd_problem_complexity": 6,
   "jd_innovation_requirements": false,
   "technical_depth_score": 90,
   "core_skills_match_percentage": 85,
   "technical_stack_fit_percentage": 80,
   "complexity_readiness_score": 95,
   "learning_agility_score": 85,
   "technical_strengths": ["Advanced Analytics", "ML Implementation", "Data Architecture"],
   "technical_gaps": ["Tableau Proficiency", "Business Domain Context"],
   "overqualification_risk": "Moderate"
 }}
}}
"""
