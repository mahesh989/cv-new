PROMPT = """
You are an expert hiring manager with 15+ years of experience. Analyze candidate-role fit across five dimensions: Skills Relevance, Experience Alignment, Industry Fit, Role Seniority, and Technical Depth. Use the provided CV and job description to complete each analysis section.

CV TEXT:{cv_text}
JD REQUIREMENTS:{jd_text}
MATCHED SKILLS:{matched_skills}

## Scoring Guidelines (0-100 scale for all categories):
- 90-100: Excellent match, minimal gaps
- 75-89: Strong fit, minor development needed
- 60-74: Good fit, moderate gaps manageable
- 40-59: Some alignment, significant development required
- 25-39: Limited fit, major gaps present
- 0-24: Poor match, substantial mismatch

---

## SKILLS RELEVANCE ANALYSIS
Analyze skills relevance beyond simple keyword matching. For each matched skill, analyze:
1. Context Relevance
2. Skill Level (Beginner/Intermediate/Advanced/Expert)
3. Application Depth
4. Synergy Score

Return JSON:
{
 "skills_analysis": [
   {
     "skill": "Python",
     "cv_evidence": "3+ years, pandas, scikit-learn, multiple projects",
     "jd_application": "Data analysis and automation tasks",
     "relevance_score": 95,
     "skill_level": "Advanced",
     "depth_indicators": ["Multiple libraries", "Project leadership", "3+ years"],
     "synergy_bonus": 10
   }
 ],
 "overall_skills_score": 87,
 "strength_areas": ["Data Analysis", "Programming"],
 "improvement_areas": ["Database Administration", "Cloud Platforms"]
}

---

## EXPERIENCE ALIGNMENT ANALYSIS
Analyze experience alignment between CV and JD requirements. Extract and analyze:
1. Years of experience
2. Role level progression
3. Responsibility scope and complexity
4. Achievement quantifications
5. Leadership/management indicators

Return JSON:
{
 "experience_analysis": {
   "cv_experience_years": 4,
   "cv_role_level": "Mid-Senior",
   "cv_progression": ["Junior Developer", "Senior Developer", "Team Lead"],
   "jd_required_years": "3-5 years",
   "jd_role_level": "Senior",
   "alignment_score": 85,
   "experience_gaps": [],
   "experience_strengths": ["Leadership experience", "Technical progression"],
   "quantified_achievements": ["Led team of 5", "Improved performance by 40%"]
 }
}

---

## INDUSTRY FIT ANALYSIS
Analyze industry background alignment. Extract and analyze:
1. Candidate's primary industry background
2. Domain expertise
3. Data/business context familiarity
4. Stakeholder ecosystem
5. Regulatory/business cycle understanding

Return JSON:
{
 "industry_analysis": {
   "cv_primary_industry": "Financial Services",
   "cv_domain_expertise": ["Algorithmic Trading", "Risk Analytics", "Market Data"],
   "jd_target_industry": "Consumer Goods",
   "jd_domain_requirements": ["POS Data", "Brand Analytics", "Retail Metrics"],
   "industry_alignment_score": 45,
   "domain_overlap_percentage": 30,
   "data_familiarity_score": 40,
   "stakeholder_fit_score": 60,
   "business_cycle_alignment": 35,
   "transferable_strengths": ["Data Analysis", "Statistical Modeling", "Business Intelligence"],
   "industry_gaps": ["Retail Domain Knowledge", "POS Systems", "Brand Management Context"],
   "adaptation_timeline": "6-12 months"
 }
}

---

## ROLE SENIORITY ANALYSIS
Analyze role seniority fit. Extract and analyze:
1. Responsibility scope
2. Leadership indicators
3. Decision-making authority
4. Career progression trajectory
5. Mentoring/coaching activities

Return JSON:
{
 "seniority_analysis": {
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
 }
}

---

## TECHNICAL DEPTH ANALYSIS
Analyze technical sophistication and depth. Extract and analyze:
1. Sophistication level
2. Core competency depth
3. Problem complexity handled
4. Innovation contributions
5. Technical leadership activities

Return JSON:
{
 "technical_analysis": {
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
 }
}

---

## INTEGRATED SCORE SUMMARY
Provide the integrated summary based on all analyses.

Return JSON:
{
 "score_summary": {
   "skills_relevance": 87,
   "experience_alignment": 85,
   "industry_fit": 45,
   "role_seniority": 75,
   "technical_depth": 90,
   "overall_weighted_score": 76
 }
}
"""
