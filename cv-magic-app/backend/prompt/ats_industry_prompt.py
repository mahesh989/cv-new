"""
Industry Fit Analysis Prompt

Analyzes industry background alignment for ATS scoring.
"""

INDUSTRY_FIT_PROMPT = """
You are an expert hiring manager with 15+ years of experience. Analyze industry background alignment.

CV TEXT: {cv_text}
JD REQUIREMENTS: {jd_text}

## Scoring Guidelines (0-100 scale):
- 90-100: Excellent match, same industry/domain
- 75-89: Strong fit, closely related industries
- 60-74: Good fit, transferable skills, some domain shift
- 40-59: Moderate fit, major industry shift but data skills transfer
- 25-39: Limited fit, significant industry/domain change
- 0-24: Poor match, completely different sectors

## Industry Transition Realism:
- Technical/Academic → Non-profit/Fundraising: MAX 55 (major domain shift)
- Data Science → Business Intelligence: 75-95 (related domains)
- Finance → Healthcare: 40-60 (data skills transfer)
- Marketing → Engineering: 20-35 (major shift)
- Same industry, different role: 80-95
- Completely different sectors: 15-35

## INDUSTRY FIT ANALYSIS
Analyze industry background alignment. Be REALISTIC about major industry shifts. Extract and analyze:
1. Candidate's primary industry background (technical/academic vs business/non-profit)
2. Domain expertise (data science vs fundraising/marketing)
3. Data/business context familiarity (research projects vs donor management)
4. Stakeholder ecosystem (academic/technical vs donors/fundraisers)
5. Regulatory/business cycle understanding (research vs fundraising cycles)

## CRITICAL: For Technical/Academic → Non-profit/Fundraising:
- Score should be 35-55 MAX (major domain shift)
- Acknowledge data skills transfer (+10-15 points)
- Penalize for missing fundraising/donor context (-15-20 points)
- Penalize for different stakeholder types (-10 points)
- Consider adaptation difficulty (6-12 months minimum)

Return JSON only:
{{
 "industry_analysis": {{
   "cv_primary_industry": "Data Science and Analytics",
   "cv_domain_expertise": ["Data Analysis", "Business Intelligence", "Data Visualization"],
   "jd_target_industry": "International Aid and Development", 
   "jd_domain_requirements": ["Data Mining", "Profile Analysis", "Segmentation Strategies"],
   "industry_alignment_score": 45,
   "domain_overlap_percentage": 50,
   "data_familiarity_score": 65,
   "stakeholder_fit_score": 40,
   "business_cycle_alignment": 30,
   "transferable_strengths": ["SQL Proficiency", "Power BI Dashboard Creation", "Analytical Problem-Solving"],
   "industry_gaps": ["Fundraising Analytics", "Non-Profit Sector Experience", "Donor-Centric Strategies"],
   "adaptation_timeline": "6-12 months"
 }}
}}
"""
