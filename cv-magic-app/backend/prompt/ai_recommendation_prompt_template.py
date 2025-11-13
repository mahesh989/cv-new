"""
AI Recommendation Prompt Template

This template generates strategic CV optimization recommendations based on comprehensive analysis data
including CV/JD analysis, skills comparison, component analysis, and ATS scores.

UPDATED: Compatible with optimized recommendation input structure
"""

def generate_ai_recommendation_prompt(company: str, analysis_data: dict) -> str:
    """
    Generate AI recommendation prompt using optimized analysis data
    
    Args:
        company: Company name
        analysis_data: Optimized analysis data from recommendation file
        
    Returns:
        Formatted prompt string for AI recommendation generation
    """
    
    # Extract optimized data structures
    metadata = analysis_data.get("metadata", {})
    skills_extraction = analysis_data.get("skills_extraction", {})
    preliminary_decision = analysis_data.get("preliminary_decision", {})
    match_summary = analysis_data.get("match_summary", {})
    keyword_guidance = analysis_data.get("keyword_integration_guidance", {})
    component_summary = analysis_data.get("component_summary", {})
    tailoring_strategy = analysis_data.get("tailoring_strategy", {})
    ats_scoring = analysis_data.get("ats_scoring", {})
    
    # Extract CV and JD skills (clean structured data)
    cv_skills = skills_extraction.get("cv", {})
    jd_skills = skills_extraction.get("jd", {})
    
    # Extract scores and metrics
    final_ats_score = ats_scoring.get("final_score", 0)
    category_status = ats_scoring.get("status", "Unknown")
    target_score = ats_scoring.get("target_score", 75.0)
    improvement_needed = ats_scoring.get("improvement_needed", 0)
    category1_score = ats_scoring.get("category1_keywords", 0)
    category2_score = ats_scoring.get("category2_ai_analysis", 0)
    missing_counts = ats_scoring.get("missing_counts", {})
    
    # Extract match data
    overall_match_rate = match_summary.get("overall_match_rate", 0)
    technical_match = match_summary.get("by_category", {}).get("technical", {})
    soft_match = match_summary.get("by_category", {}).get("soft", {})
    domain_match = match_summary.get("by_category", {}).get("domain", {})
    
    # Extract component scores
    technical_component = component_summary.get("technical", {})
    skills_component = component_summary.get("skills", {})
    experience_component = component_summary.get("experience", {})
    seniority_component = component_summary.get("seniority", {})
    industry_component = component_summary.get("industry", {})
    
    # Extract keyword tiers
    tier1_keywords = keyword_guidance.get("tier1_always_add", {})
    tier2_keywords = keyword_guidance.get("tier2_add_if_evidence", {})
    tier3_keywords = keyword_guidance.get("tier3_never_add", {})
    integration_instructions = keyword_guidance.get("integration_instructions", "")
    
    # Extract tailoring strategy
    primary_objective = tailoring_strategy.get("primary_objective", "Optimize CV for target role")
    emphasis_areas = tailoring_strategy.get("emphasis_areas", [])
    de_emphasize_areas = tailoring_strategy.get("de_emphasize", [])
    critical_additions = tailoring_strategy.get("critical_additions", {})
    tone_guidance = tailoring_strategy.get("tone_guidance", "Professional and results-oriented")
    industry_bridging = tailoring_strategy.get("industry_bridging", [])
    
    # Extract preliminary decision
    decision = preliminary_decision.get("decision", "UNKNOWN")
    confidence = preliminary_decision.get("confidence", 0)
    match_score = preliminary_decision.get("match_score", 0)
    primary_reason = preliminary_decision.get("primary_reason", "")
    critical_missing = preliminary_decision.get("critical_missing", [])
    implicit_likely = preliminary_decision.get("implicit_likely", [])
    blocker_found = preliminary_decision.get("blocker_found", False)
    
    prompt = f"""# Strategic CV Optimization Recommendations Generator

**Role:** You are a Senior CV Strategist and Hiring Consultant with expertise in ATS optimization, skills matching, and strategic positioning.  

**Objective:** Analyze the candidate's comprehensive profile against {company}'s job requirements and generate precise, actionable recommendations to maximize interview probability and ATS performance.

---

## 📊 Comprehensive Analysis Data

### Current ATS Performance
- **Final ATS Score:** {final_ats_score}/100
- **Category Status:** {category_status}
- **Target Score:** {target_score}/100
- **Improvement Needed:** {improvement_needed} points

### Preliminary Match Assessment
- **Decision:** {decision}
- **Confidence:** {confidence}%
- **Match Score:** {match_score}%
- **Primary Reason:** {primary_reason}
- **Critical Missing:** {', '.join(critical_missing) if critical_missing else 'None'}
- **Implicit Likely:** {', '.join(implicit_likely) if implicit_likely else 'None'}
- **Blocker Found:** {'Yes' if blocker_found else 'No'}

### Skills Match Summary
**Overall Match Rate:** {overall_match_rate}%

**Technical Skills (Match Rate: {technical_match.get('match_rate', 0)}%):**
- **Matched:** {', '.join(technical_match.get('matched', [])[:10])}{'...' if len(technical_match.get('matched', [])) > 10 else ''}
- **Missing:** {', '.join(technical_match.get('missing', [])[:10])}{'...' if len(technical_match.get('missing', [])) > 10 else ''}

**Soft Skills (Match Rate: {soft_match.get('match_rate', 0)}%):**
- **Matched:** {', '.join(soft_match.get('matched', []))}
- **Missing:** {', '.join(soft_match.get('missing', []))}

**Domain Keywords (Match Rate: {domain_match.get('match_rate', 0)}%):**
- **Matched:** {', '.join(domain_match.get('matched', []))}
- **Missing:** {', '.join(domain_match.get('missing', []))}

### CV Skills Inventory
**Technical Skills:** {', '.join(cv_skills.get('technical', [])[:15])}{'...' if len(cv_skills.get('technical', [])) > 15 else ''}
**Soft Skills:** {', '.join(cv_skills.get('soft', []))}
**Domain Keywords:** {', '.join(cv_skills.get('domain', []))}

### JD Requirements
**Technical Skills:** {', '.join(jd_skills.get('technical', [])[:15])}{'...' if len(jd_skills.get('technical', [])) > 15 else ''}
**Soft Skills:** {', '.join(jd_skills.get('soft', []))}
**Domain Keywords:** {', '.join(jd_skills.get('domain', []))}

### Component Analysis Scores
**Technical:**
- Overall Score: {technical_component.get('score', 0)}/100
- Core Skills Match: {technical_component.get('core_match', 0)}%
- Stack Fit: {technical_component.get('stack_fit', 0)}%
- Strengths: {'; '.join(technical_component.get('strengths', [])[:3])}
- Gaps: {'; '.join(technical_component.get('gaps', [])[:3])}

**Skills:**
- Overall Score: {skills_component.get('score', 0)}/100
- Business Readiness: {skills_component.get('business_readiness', 0)}/100
- Strengths: {'; '.join(skills_component.get('strengths', [])[:3])}
- Critical Gaps: {', '.join(skills_component.get('critical_gaps', []))}

**Experience:**
- Total Years: {experience_component.get('years', 0)}
- Corporate Years: {experience_component.get('corporate_years', 0)}
- Alignment Score: {experience_component.get('alignment_score', 0)}/100
- Strengths: {'; '.join(experience_component.get('strengths', [])[:3])}
- Gaps: {'; '.join(experience_component.get('gaps', [])[:3])}

**Seniority:**
- Score: {seniority_component.get('score', 0)}/100
- CV Level: {seniority_component.get('cv_level', 'Unknown')}
- JD Level: {seniority_component.get('jd_level', 'Unknown')}
- Match: {seniority_component.get('match', 0)}%

**Industry:**
- CV Industry: {industry_component.get('cv_industry', 'Unknown')}
- JD Industry: {industry_component.get('jd_industry', 'Unknown')}
- Alignment Score: {industry_component.get('alignment_score', 0)}/100
- Transition Type: {industry_component.get('transition_type', 'Unknown')}
- Transition Difficulty: {industry_component.get('transition_difficulty', 'UNKNOWN')}
- Adaptation Timeline: {industry_component.get('adaptation_timeline', 'Unknown')}

### ATS Category Breakdown
- **Category 1 (Keyword Matching):** {category1_score} points
  - Missing Technical: {missing_counts.get('technical', 0)} keywords
  - Missing Soft: {missing_counts.get('soft', 0)} keywords
  - Missing Domain: {missing_counts.get('domain', 0)} keywords

- **Category 2 (AI Analysis):** {category2_score} points

---

## 🔑 Keyword Integration Guidance (Framework-Based)

{integration_instructions}

### TIER 1 - ALWAYS ADD (Generic/Transferable Skills)
These are generic/transferable skills. Integrate ALL into CV naturally in skills section and relevant bullets.

**Technical:** {', '.join(tier1_keywords.get('technical', [])) if tier1_keywords.get('technical') else 'None'}
**Soft Skills:** {', '.join(tier1_keywords.get('soft', [])) if tier1_keywords.get('soft') else 'None'}
**Domain:** {', '.join(tier1_keywords.get('domain', [])) if tier1_keywords.get('domain') else 'None'}

### TIER 2 - ADD IF EVIDENCE EXISTS
Add ONLY if you can find semantic evidence in CV experience. Require validation.

**Technical:** {', '.join(tier2_keywords.get('technical', [])) if tier2_keywords.get('technical') else 'None'}
**Soft Skills:** {', '.join(tier2_keywords.get('soft', [])) if tier2_keywords.get('soft') else 'None'}
**Domain:** {', '.join(tier2_keywords.get('domain', [])) if tier2_keywords.get('domain') else 'None'}

### TIER 3 - NEVER ADD (Unverifiable/Domain-Specific)
DO NOT add these. They are domain-specific, certifications, or unverifiable without direct evidence.

**Technical:** {', '.join(tier3_keywords.get('technical', [])) if tier3_keywords.get('technical') else 'None'}
**Soft Skills:** {', '.join(tier3_keywords.get('soft', [])) if tier3_keywords.get('soft') else 'None'}
**Domain:** {', '.join(tier3_keywords.get('domain', [])) if tier3_keywords.get('domain') else 'None'}

---

## 🎯 Strategic Tailoring Guidance

### Primary Objective
{primary_objective}

### EMPHASIS AREAS (Highlight These Strengths)
{chr(10).join(f'- {area}' for area in emphasis_areas) if emphasis_areas else '- Focus on transferable skills and achievements'}

### DE-EMPHASIZE (Minimize These)
{chr(10).join(f'- {area}' for area in de_emphasize_areas) if de_emphasize_areas else '- No specific areas to de-emphasize'}

### CRITICAL ADDITIONS NEEDED
**Technical:** {', '.join(critical_additions.get('technical', [])) if critical_additions.get('technical') else 'None'}
**Soft Skills:** {', '.join(critical_additions.get('soft', [])) if critical_additions.get('soft') else 'None'}
**Domain:** {', '.join(critical_additions.get('domain', [])) if critical_additions.get('domain') else 'None'}

### TONE GUIDANCE
{tone_guidance}

### INDUSTRY TRANSITION BRIDGING
{chr(10).join(f'- {bridge}' for bridge in industry_bridging) if industry_bridging else '- No industry transition required'}

---

## 🎯 Strategic Constraints & Guidelines

### Constraints
- **No Fabrication:** Only reframe or highlight existing CV experiences. Do not invent new ones.
- **Transferable Skills:** Soft skills can be inferred if logically supported (e.g., teaching → communication; leading tutorials → team management).
- **Evidence Required:** Each recommendation must include:
  - **Basis:** CV evidence supporting the claim
  - **Integration:** How to add naturally
  - **Validation:** How to defend if asked in interview
  - **Risk Level:** Low/Medium/High likelihood of challenge

### Section Completeness Guidance
- If the provided CV lacks certain sections (e.g., Projects, Certifications), DO NOT recommend creating entirely new sections.
- Instead, provide concise recommendations on how to strengthen the CV within the existing sections only.
- If a section is missing but relevant, suggest content ideas as guidance, clearly labeled as suggestions, not mandatory additions.

### Keyword Integration Rules
- **Tier 1 Keywords:** Integrate ALL - these are generic/transferable
- **Tier 2 Keywords:** Integrate ONLY if semantic evidence exists
- **Tier 3 Keywords:** NEVER add - unverifiable or domain-specific

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
Focus on the missing keywords identified:
- **Critical Technical Gaps:** {missing_counts.get('technical', 0)} missing keywords with {technical_match.get('match_rate', 0)}% current match
- **Soft Skills Gaps:** {missing_counts.get('soft', 0)} missing keywords with {soft_match.get('match_rate', 0)}% current match
- **Domain Gaps:** {missing_counts.get('domain', 0)} missing keywords with {domain_match.get('match_rate', 0)}% current match

For each gap, classify as:
- **Safe to Add (Tier 1):** Generic/transferable, integrate immediately
- **Add with Evidence (Tier 2):** Requires validation, add if semantic evidence exists
- **Do Not Add (Tier 3):** Unverifiable or domain-specific without direct experience

### 2. ATS Score Optimization Strategy
Current score: {final_ats_score}/100, Target: {target_score}/100, Gap: {improvement_needed} points

**Category 1 Improvements (Keyword Matching - {category1_score} points):**
- Address {missing_counts.get('technical', 0)} missing technical keywords
- Address {missing_counts.get('soft', 0)} missing soft skill keywords
- Address {missing_counts.get('domain', 0)} missing domain keywords

**Category 2 Enhancement (AI Analysis - {category2_score} points):**
- Technical depth optimization
- Experience alignment improvement
- Industry fit enhancement

### 3. Industry Transition Strategy
Based on {industry_component.get('alignment_score', 0)}/100 industry fit score:
- **Current Industry:** {industry_component.get('cv_industry', 'Unknown')}
- **Target Industry:** {industry_component.get('jd_industry', 'Unknown')}
- **Transition Difficulty:** {industry_component.get('transition_difficulty', 'UNKNOWN')}
- **Adaptation Timeline:** {industry_component.get('adaptation_timeline', 'Unknown')}

Strategy:
- **Transferable Strengths:** Leverage existing skills for new domain
- **Domain Knowledge Gaps:** Address industry-specific terminology using Tier 1/2 keywords only
- **Soft/Transferable Skills:** Suggested inferences following the Evidence Required format
- **Skills Gap Mitigation:** Show transferable skills, learning trajectory, and foundational strengths for missing requirements
- **Bridging Statements:** Use the industry bridging guidance provided above

### 4. Experience & Seniority Positioning
Current seniority score: {seniority_component.get('score', 0)}/100
- **CV Level:** {seniority_component.get('cv_level', 'Unknown')}
- **JD Level:** {seniority_component.get('jd_level', 'Unknown')}
- **Match:** {seniority_component.get('match', 0)}%

Strategy:
- **Leadership Indicators:** How to highlight existing leadership experience
- **Responsibility Scope:** Reframe current roles for target seniority
- **Growth Trajectory:** Position career progression strategically

### 5. Technical Stack Alignment
Technical score: {technical_component.get('score', 0)}/100
- **Core Skills Match:** {technical_component.get('core_match', 0)}%
- **Stack Fit:** {technical_component.get('stack_fit', 0)}%
- **Strengths:** {'; '.join(technical_component.get('strengths', [])[:3])}
- **Gaps:** {'; '.join(technical_component.get('gaps', [])[:3])}

Strategy:
- **Core Skills Emphasis:** Highlight matched technical skills prominently
- **Stack Fit Optimization:** Bridge gaps using Tier 1/2 keywords
- **Learning Agility:** Showcase adaptability and quick learning

---

## 📄 Required Output Format

# 🎯 CV Tailoring Strategy Report for {company}

## 🔍 Executive Summary
- **Current ATS Score:** {final_ats_score}/100
- **Target Score:** {target_score}/100
- **Improvement Needed:** {improvement_needed} points
- **Overall Match Rate:** {overall_match_rate}%
- **Primary Objective:** {primary_objective}
- **Key Challenge:** {industry_component.get('transition_difficulty', 'UNKNOWN')} industry transition from {industry_component.get('cv_industry', 'Unknown')} to {industry_component.get('jd_industry', 'Unknown')}

## 🔍 Priority Gap Analysis
**Immediate Action Required (Critical Gaps):**
- Category 1: {missing_counts.get('technical', 0)} technical, {missing_counts.get('soft', 0)} soft, {missing_counts.get('domain', 0)} domain keywords missing
- Technical Match: {technical_match.get('match_rate', 0)}%
- Soft Skills Match: {soft_match.get('match_rate', 0)}%
- Domain Match: {domain_match.get('match_rate', 0)}%

**Optimization Opportunities:**
- Technical Depth: {technical_component.get('score', 0)}/100
- Experience Alignment: {experience_component.get('alignment_score', 0)}/100
- Industry Fit: {industry_component.get('alignment_score', 0)}/100

## 🔑 Keyword Integration Strategy

### TIER 1 - INTEGRATE IMMEDIATELY (Low Risk)
**Technical Keywords to Add:**
- List each Tier 1 technical keyword with:
  - **Basis:** Why it's safe to add (generic/transferable nature)
  - **Integration:** Where to add in CV (skills section, which bullets)
  - **Validation:** How to explain if asked
  - **Risk:** Low (generic/transferable skill)

**Soft Skills to Add:**
- List each Tier 1 soft skill with same format

### TIER 2 - ADD WITH EVIDENCE (Medium Risk)
**Technical Keywords (If Evidence Exists):**
- List each Tier 2 technical keyword with:
  - **Basis:** Semantic evidence in CV (specific experience/project)
  - **Integration:** How to naturally incorporate
  - **Validation:** Concrete example to give in interview
  - **Risk:** Medium (requires defense)

**Soft Skills (If Evidence Exists):**
- List each Tier 2 soft skill with same format

### TIER 3 - DO NOT ADD (High Risk)
**Keywords to Avoid:**
- List each Tier 3 keyword with:
  - **Why Not:** Reason (domain-specific, unverifiable, certification)
  - **Risk:** High (cannot defend in interview)
  - **Alternative:** Suggest Tier 1/2 alternatives if applicable

## 🎪 Experience Reframing Strategy

### Industry Transition Focus
**Objective:** {primary_objective}

**Emphasis Areas:**
{chr(10).join(f'- {area}' for area in emphasis_areas) if emphasis_areas else '- Focus on transferable skills'}

**De-Emphasize:**
{chr(10).join(f'- {area}' for area in de_emphasize_areas) if de_emphasize_areas else '- No specific de-emphasis needed'}

**Bridging Statements to Use:**
{chr(10).join(f'- {bridge}' for bridge in industry_bridging) if industry_bridging else '- Direct industry match'}

### Seniority Positioning
**Current:** {seniority_component.get('cv_level', 'Unknown')}
**Target:** {seniority_component.get('jd_level', 'Unknown')}
**Strategy:** [Leadership and responsibility indicators to emphasize]

### Technical Depth Showcase
**Strengths to Highlight:**
{chr(10).join(f'- {strength}' for strength in technical_component.get('strengths', []))}

**Gaps to Address:**
{chr(10).join(f'- {gap}' for gap in technical_component.get('gaps', []))}

## ⚠️ Strategic Warnings

### Don't Oversell (Avoid These Claims)
- **Tier 3 Keywords:** Never add without direct evidence
- **Domain-Specific Terms:** {', '.join(tier3_keywords.get('domain', []))} - Cannot claim without industry experience
- **Unverifiable Skills:** {', '.join(tier3_keywords.get('technical', [])[:5])} - No supporting evidence

### Don't Undersell (Emphasize These Strengths)
- **Matched Skills:** {', '.join(technical_match.get('matched', [])[:5])}
- **Transferable Experience:** {'; '.join(experience_component.get('strengths', [])[:3])}
- **Core Competencies:** {'; '.join(skills_component.get('strengths', [])[:3])}

## 📌 Implementation Roadmap

### Phase 1: High-Impact Quick Wins
1. Add ALL Tier 1 keywords to skills section
2. Emphasize matched technical skills in experience bullets
3. Reframe experience using industry bridging statements

### Phase 2: Evidence-Based Additions
1. Review Tier 2 keywords for semantic evidence
2. Add only keywords with concrete validation
3. Document defense strategy for each addition

### Phase 3: Strategic Positioning
1. Adjust tone per guidance: {tone_guidance}
2. De-emphasize non-relevant skills
3. Optimize for target seniority level

## 📌 Section Completeness Notes
- Identify any missing sections in the current CV structure (purely observational).
- Provide targeted suggestions on how the candidate could improve those areas in the future.
- Do NOT instruct to add new sections in the immediate tailoring; recommendations should respect the current CV structure.

---

**Strategic Note:** This analysis uses optimized data structures with keyword tier classification and strategic tailoring guidance. Focus on evidence-based improvements that maximize authenticity while optimizing for ATS performance ({final_ats_score} → {target_score}) and interview success.

**Integration Priority:** 
1. Tier 1 keywords (100% safe)
2. Tier 2 keywords with evidence (validation required)
3. Strategic reframing (no fabrication)
4. Never add Tier 3 keywords without direct experience
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
    
    # Extract metadata for header
    metadata = analysis_data.get("metadata", {})
    generated_at = metadata.get("generated_at", "Unknown")
    ats_score = analysis_data.get("ats_scoring", {}).get("final_score", "N/A")
    match_rate = metadata.get("match_rate_current", "N/A")
    
    company_prompt = f'''"""
AI Recommendation Prompt for {company}
Generated automatically from optimized analysis data
"""

# Company: {company}
# Generated: {generated_at}
# ATS Score: {ats_score}/100
# Match Rate: {match_rate}%

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