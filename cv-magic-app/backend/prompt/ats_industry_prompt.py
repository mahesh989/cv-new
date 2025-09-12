"""
Industry Fit Analysis Prompt

Analyzes industry background alignment for ATS scoring.
"""

INDUSTRY_FIT_PROMPT = """
You are an expert hiring manager with 15+ years of experience. Analyze industry background alignment.

CV TEXT: {cv_text}
JD REQUIREMENTS: {jd_text}

## Scoring Guidelines (0-100 scale):
- 90-100: Excellent match, minimal gaps
- 75-89: Strong fit, minor development needed
- 60-74: Good fit, moderate gaps manageable
- 40-59: Some alignment, significant development required
- 25-39: Limited fit, major gaps present
- 0-24: Poor match, substantial mismatch

## INDUSTRY FIT ANALYSIS
Analyze industry background alignment. Extract and analyze:
1. Candidate's primary industry background
2. Domain expertise
3. Data/business context familiarity
4. Stakeholder ecosystem
5. Regulatory/business cycle understanding

Return JSON only:
{{
 "industry_analysis": {{
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
 }}
}}
"""
