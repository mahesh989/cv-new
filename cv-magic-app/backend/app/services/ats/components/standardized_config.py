"""
Standardized Configuration for ATS Component Analyzers

Ensures consistent AI parameters, prompt structure, and validation across all analyzers.
"""

# Standardized AI Parameters
STANDARD_AI_PARAMS = {
    "temperature": 0.0,  # Zero temperature for maximum consistency
    "max_tokens": 3000,  # Increased for comprehensive analysis (was 1500, too low for skills analysis)
    "system_prompt": "You are an expert ATS analyst with 15+ years of experience. Analyze the provided CV and JD content with precision and consistency. Always return valid JSON format."
}

# Standardized CV Content Interpretation Guidelines
CV_INTERPRETATION_GUIDELINES = """
## CV CONTENT INTERPRETATION GUIDELINES

### Experience Analysis:
- Count ALL relevant work experience (including internships, part-time, freelance)
- PhD/Master's research experience counts as professional experience
- Academic projects with real-world applications count as experience
- Look for quantified achievements and leadership indicators

### Seniority Analysis:
- PhD holders typically have 3-6 years of research experience
- Master's with thesis = 1-2 years research experience
- Academic leadership (TA, RA, project lead) = leadership experience
- Research publications and presentations = senior-level contributions

### Skills Analysis:
- Academic projects demonstrate practical skill application
- Research methodologies show analytical thinking
- Thesis work shows deep technical expertise
- Conference presentations show communication skills

### Industry Analysis:
- Academic research in relevant fields = industry experience
- Cross-disciplinary work shows adaptability
- International experience shows cultural awareness
- Research publications show domain expertise

### Technical Analysis:
- Academic projects demonstrate technical depth
- Research tools and methodologies show sophistication
- Thesis work shows problem-solving complexity
- Publications show technical communication skills
"""

# Standardized Prompt Template Structure
STANDARD_PROMPT_TEMPLATE = """
You are an expert hiring manager with 15+ years of experience. Analyze the following CV and JD requirements with precision and consistency.

CV TEXT: {cv_text}
JD REQUIREMENTS: {jd_text}
MATCHED SKILLS: {matched_skills}

## CRITICAL INTERPRETATION RULES:
{CV_INTERPRETATION_GUIDELINES}

## Scoring Guidelines (0-100 scale):
- 90-100: Excellent match, minimal gaps
- 75-89: Strong fit, minor development needed  
- 60-74: Good fit, moderate gaps manageable
- 40-59: Some alignment, significant development required
- 25-39: Limited fit, major gaps present
- 0-24: Poor match, substantial mismatch

## ANALYSIS REQUIREMENTS:
{ANALYSIS_SPECIFIC_REQUIREMENTS}

Return JSON only:
{JSON_SCHEMA}
"""

# Validation Rules
VALIDATION_RULES = {
    "experience_years_range": (0, 20),  # Reasonable range
    "seniority_score_range": (0, 100),
    "skills_score_range": (0, 100),
    "industry_score_range": (0, 100),
    "technical_score_range": (0, 100),
    "required_fields": {
        "experience": ["cv_experience_years", "cv_role_level", "alignment_score"],
        "seniority": ["cv_experience_years", "seniority_score", "experience_match_percentage"],
        "skills": ["overall_skills_score", "strength_areas", "improvement_areas"],
        "industry": ["industry_alignment_score", "domain_overlap_percentage"],
        "technical": ["technical_depth_score", "core_skills_match_percentage"]
    }
}

def validate_analysis_result(result: dict, analysis_type: str) -> bool:
    """
    Validate analysis result for consistency and completeness.
    
    Args:
        result: Analysis result dictionary
        analysis_type: Type of analysis (experience, seniority, skills, industry, technical)
        
    Returns:
        bool: True if valid, False otherwise
    """
    if analysis_type not in VALIDATION_RULES["required_fields"]:
        return False
    
    required_fields = VALIDATION_RULES["required_fields"][analysis_type]
    
    # Check if all required fields are present
    for field in required_fields:
        if field not in result:
            return False
    
    # Check score ranges
    score_field = f"{analysis_type}_score" if analysis_type != "experience" else "alignment_score"
    if score_field in result:
        score_value = result[score_field]
        try:
            numeric_score = float(score_value)
        except (TypeError, ValueError):
            return False
        if not (0.0 <= numeric_score <= 100.0):
            return False
    
    return True

def get_standardized_prompt(analysis_type: str, cv_text: str, jd_text: str, matched_skills: str = "") -> str:
    """
    Get standardized prompt for specific analysis type.
    
    Args:
        analysis_type: Type of analysis
        cv_text: CV content
        jd_text: JD content  
        matched_skills: Matched skills (optional)
        
    Returns:
        str: Formatted prompt
    """
    # This would be implemented with specific requirements for each analysis type
    # For now, return the base template
    return STANDARD_PROMPT_TEMPLATE.format(
        cv_text=cv_text[:5000],  # Limit CV text
        jd_text=jd_text[:3000],  # Limit JD text
        matched_skills=matched_skills,
        CV_INTERPRETATION_GUIDELINES=CV_INTERPRETATION_GUIDELINES,
        ANALYSIS_SPECIFIC_REQUIREMENTS="[Analysis-specific requirements would go here]",
        JSON_SCHEMA="[JSON schema would go here]"
    )
