"""
AI Recommendation Prompt Template

This template generates strategic CV optimization recommendations based on comprehensive analysis data
including CV/JD analysis, skills comparison, component analysis, and ATS scores.
"""

def generate_ai_recommendation_prompt(company: str, analysis_data: dict) -> str:
    """
    Generate AI recommendation prompt using comprehensive analysis data
    
    Args:
        company: Company name
        analysis_data: Comprehensive analysis data from recommendation file
        
    Returns:
        Formatted prompt string for AI recommendation generation
    """
    
    # Extract key data from comprehensive analysis
    cv_analysis = analysis_data.get("cv_comprehensive_analysis", "")
    jd_analysis = analysis_data.get("jd_comprehensive_analysis", "")
    
    # Get latest entries
    ats_entries = analysis_data.get("ats_calculation_entries", [])
    latest_ats = ats_entries[-1] if ats_entries else {}
    
    preextracted_entries = analysis_data.get("preextracted_comparison_entries", [])
    latest_comparison = preextracted_entries[-1] if preextracted_entries else {}
    
    component_entries = analysis_data.get("component_analysis_entries", [])
    latest_component = component_entries[-1] if component_entries else {}
    
    match_entries = analysis_data.get("analyze_match_entries", [])
    latest_match = match_entries[-1] if match_entries else {}
    
    # Extract scores and metrics
    final_ats_score = latest_ats.get("final_ats_score", 0)
    category_status = latest_ats.get("category_status", "Unknown")
    ats_breakdown = latest_ats.get("breakdown", {})
    
    extracted_scores = latest_component.get("extracted_scores", {}) if latest_component else {}
    component_analyses = latest_component.get("component_analyses", {}) if latest_component else {}
    
    comparison_content = latest_comparison.get("content", "") if latest_comparison else ""
    match_content = latest_match.get("content", "") if latest_match else ""
    
    prompt = f"""# Strategic CV Optimization Recommendations Generator

**Role:** You are a Senior CV Strategist and Hiring Consultant with expertise in ATS optimization, skills matching, and strategic positioning.  

**Objective:** Analyze the candidate's comprehensive profile against {company}'s job requirements and generate precise, actionable recommendations to maximize interview probability and ATS performance.

---

## 📊 Comprehensive Analysis Data

### Current ATS Performance
- **Final ATS Score:** {final_ats_score}/100
- **Category Status:** {category_status}
- **Recommendation:** {latest_ats.get('recommendation', 'N/A')}

### Skills Match Summary
{comparison_content[:1000]}{'...' if len(comparison_content) > 1000 else ''}

### Strategic Assessment
{match_content[:1500]}{'...' if len(match_content) > 1500 else ''}

### Component Analysis Scores
- **Skills Relevance:** {extracted_scores.get('skills_relevance', 0)}/100
- **Experience Alignment:** {extracted_scores.get('experience_alignment', 0)}/100
- **Industry Fit:** {extracted_scores.get('industry_fit', 0)}/100
- **Role Seniority:** {extracted_scores.get('role_seniority', 0)}/100
- **Technical Depth:** {extracted_scores.get('technical_depth', 0)}/100

### Detailed Skill Breakdown
**CV Skills Analysis:**
{cv_analysis[:2000]}{'...' if len(cv_analysis) > 2000 else ''}

**JD Requirements Analysis:**
{jd_analysis[:2000]}{'...' if len(jd_analysis) > 2000 else ''}

### Category Breakdown
- **Category 1 (Skills Matching):** {ats_breakdown.get('category1', {}).get('score', 0)}/40
  - Technical Skills Match: {ats_breakdown.get('category1', {}).get('technical_skills_match_rate', 0)}%
  - Soft Skills Match: {ats_breakdown.get('category1', {}).get('soft_skills_match_rate', 0)}%
  - Domain Keywords Match: {ats_breakdown.get('category1', {}).get('domain_keywords_match_rate', 0)}%

- **Category 2 (Experience & Competency):** {ats_breakdown.get('category2', {}).get('score', 0)}/60
  - Core Competency: {ats_breakdown.get('category2', {}).get('core_competency_avg', 0)}%
  - Experience/Seniority: {ats_breakdown.get('category2', {}).get('experience_seniority_avg', 0)}%
  - Potential/Ability: {ats_breakdown.get('category2', {}).get('potential_ability_avg', 0)}%
  - Company Fit: {ats_breakdown.get('category2', {}).get('company_fit_avg', 0)}%

---

## 🎯 Strategic Constraints & Guidelines

### Evidence-Based Approach
- **No Fabrication:** Only reframe or highlight existing CV experiences
- **Transferable Skills:** Infer soft skills if logically supported by evidence
- **Risk Assessment:** Each recommendation must include risk evaluation

### Validation Requirements
For each recommendation provide:
- **Basis:** Existing CV evidence supporting the claim
- **Integration:** How to naturally incorporate into CV
- **Validation:** How to defend if questioned in interview
- **Risk Level:** Low/Medium/High likelihood of challenge

---

## 📋 Required Analysis & Recommendations

Generate a comprehensive strategic report covering:

### 1. Missing Keywords Analysis
Focus on the lowest-scoring categories from the analysis:
- **Critical Gaps:** Highest-impact missing JD keywords (prioritize {ats_breakdown.get('category1', {}).get('domain_keywords_match_rate', 0)}% domain match)
- **Technical Gaps:** Missing technical skills with {ats_breakdown.get('category1', {}).get('technical_skills_match_rate', 0)}% current match
- **Soft Skills Gaps:** Missing soft skills with {ats_breakdown.get('category1', {}).get('soft_skills_match_rate', 0)}% current match

### 2. ATS Score Optimization Strategy
Current ATS breakdown shows specific improvement areas:
- **Category 1 Improvements:** Target the {ats_breakdown.get('category1', {}).get('missing_counts', {}).get('technical', 0)} missing technical skills
- **Category 2 Enhancement:** Address the {ats_breakdown.get('category2', {}).get('company_fit_avg', 0)}% company fit score
- **Bonus Points:** Optimize for the current {ats_breakdown.get('bonus_points', 0)} bonus points

### 3. Industry Transition Strategy
Based on {extracted_scores.get('industry_fit', 0)}/100 industry fit score:
- **Transferable Strengths:** Leverage existing skills for new domain
- **Domain Knowledge Gaps:** Address industry-specific terminology
- **Adaptation Timeline:** Realistic skill development plan

### 4. Experience & Seniority Positioning
Current seniority score: {extracted_scores.get('role_seniority', 0)}/100
- **Leadership Indicators:** How to highlight existing leadership experience
- **Responsibility Scope:** Reframe current roles for target seniority
- **Growth Trajectory:** Position career progression strategically

### 5. Technical Stack Alignment
Technical depth score: {extracted_scores.get('technical_depth', 0)}/100
- **Core Skills Emphasis:** Highlight {extracted_scores.get('core_skills_match_percentage', 0)}% matched skills
- **Stack Fit Optimization:** Improve {extracted_scores.get('technical_stack_fit_percentage', 0)}% alignment
- **Learning Agility:** Showcase {extracted_scores.get('learning_agility_score', 0)}% adaptability

---

## 📄 Required Output Format

# 🎯 CV Tailoring Strategy Report for {company}

## 📊 Executive Summary
- **Current ATS Score:** {final_ats_score}/100 ({category_status})
- **Key Strengths:** [Top 3-4 highest-scoring areas]
- **Critical Gaps:** [Top 3-4 lowest-scoring areas requiring immediate attention]
- **Success Probability:** [Based on strategic assessment and component scores]

## 🔍 Priority Gap Analysis
**Immediate Action Required (Low Scores):**
- [List areas with scores below 50]

**Optimization Opportunities (Medium Scores):**
- [List areas with scores 50-75]

**Strength Amplification (High Scores):**
- [List areas with scores above 75]

## 🛠️ Keyword Integration Strategy
**Critical Missing Keywords (0% domain match):**
- [Specific domain keywords to integrate with injection points]

**Technical Skills Enhancement ({ats_breakdown.get('category1', {}).get('technical_skills_match_rate', 0)}% current match):**
- [Technical keywords to add/emphasize]

**Soft Skills Optimization ({ats_breakdown.get('category1', {}).get('soft_skills_match_rate', 0)}% current match):**
- [Soft skills to highlight with evidence]

## 🎪 Experience Reframing Strategy
**Industry Transition Focus ({extracted_scores.get('industry_fit', 0)}/100 current fit):**
- [How to reframe existing experience for target industry]

**Seniority Positioning ({extracted_scores.get('role_seniority', 0)}/100 current match):**
- [Leadership and responsibility indicators to emphasize]

**Technical Depth Showcase ({extracted_scores.get('technical_depth', 0)}/100 current score):**
- [Technical achievements and complexity indicators]

## 📈 ATS Score Improvement Roadmap
**Target Score:** [Realistic target based on current {final_ats_score}]

**High-Impact Changes (Expected +10-15 points):**
- [Top 3 recommendations with highest ROI]

**Medium-Impact Changes (Expected +5-10 points):**
- [Secondary optimizations]

**Fine-Tuning (Expected +2-5 points):**
- [Final polish recommendations]


---

**Strategic Note:** This analysis is based on comprehensive data including actual ATS calculations, component analysis, and strategic assessment. Focus on evidence-based improvements that maximize authenticity while optimizing for ATS performance and interview success.
"""

    return prompt


def generate_company_specific_prompt(company: str, analysis_data: dict) -> str:
    """
    Generate a company-specific prompt file
    
    Args:
        company: Company name
        analysis_data: Analysis data dictionary
        
    Returns:
        Company-specific prompt content
    """
    base_prompt = generate_ai_recommendation_prompt(company, analysis_data)
    
    company_prompt = f'''"""
AI Recommendation Prompt for {company}
Generated automatically from comprehensive analysis data
"""

# Company: {company}
# Generated: {analysis_data.get("timestamp", "Unknown")}
# ATS Score: {analysis_data.get("ats_calculation_entries", [{}])[-1].get("final_ats_score", "N/A") if analysis_data.get("ats_calculation_entries") else "N/A"}

AI_RECOMMENDATION_PROMPT = """
{base_prompt}
"""

def get_prompt() -> str:
    """Return the AI recommendation prompt for {company}"""
    return AI_RECOMMENDATION_PROMPT
'''
    
    return company_prompt


# Example usage function
def create_company_prompt_file(company: str, analysis_file_path: str) -> str:
    """
    Create a company-specific prompt file from analysis data
    
    Args:
        company: Company name
        analysis_file_path: Path to the analysis JSON file
        
    Returns:
        Path to created prompt file
    """
    import json
    from pathlib import Path
    
    # Read analysis data
    with open(analysis_file_path, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    # Generate prompt content
    prompt_content = generate_company_specific_prompt(company, analysis_data)
    
    # Create prompt file
    prompt_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/prompt")
    prompt_dir.mkdir(exist_ok=True)
    
    prompt_file = prompt_dir / f"{company}_prompt_recommendation.py"
    
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(prompt_content)
    
    return str(prompt_file)