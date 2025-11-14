"""
AI Recommendation Prompt Template

This template generates strategic CV optimization recommendations based on comprehensive analysis data
including CV/JD analysis, skills comparison, component analysis, and ATS scores.

UPDATED: Compatible with optimized recommendation input structure
OUTPUT: Structured JSON for machine-readable CV generation
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
    
    # CRITICAL FIX: Filter out keywords that appear in both matched and missing lists
    # This handles case-sensitivity issues where the same keyword appears in both lists
    def normalize_keyword(kw):
        """Normalize keyword for comparison (lowercase, strip)"""
        return str(kw).lower().strip()
    
    def filter_missing_keywords(missing_list, matched_list):
        """Remove keywords from missing list that also appear in matched list (case-insensitive)"""
        matched_normalized = {normalize_keyword(kw) for kw in matched_list}
        filtered = []
        for kw in missing_list:
            if normalize_keyword(kw) not in matched_normalized:
                filtered.append(kw)
        return filtered
    
    # Filter missing keywords to exclude those already matched
    if technical_match.get('missing') and technical_match.get('matched'):
        technical_match['missing'] = filter_missing_keywords(
            technical_match['missing'], 
            technical_match['matched']
        )
    
    if soft_match.get('missing') and soft_match.get('matched'):
        soft_match['missing'] = filter_missing_keywords(
            soft_match['missing'], 
            soft_match['matched']
        )
    
    if domain_match.get('missing') and domain_match.get('matched'):
        domain_match['missing'] = filter_missing_keywords(
            domain_match['missing'], 
            domain_match['matched']
        )
    
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
    
    prompt = f"""Strategic CV Optimization Recommendations Generator

Role: Senior CV Strategist and Hiring Consultant with expertise in ATS optimization, skills matching, and strategic positioning.

Objective: Generate precise, actionable recommendations in structured JSON format for programmatic CV generation.

ANALYSIS DATA:

Current ATS Performance:
- Final Score: {final_ats_score}/100
- Status: {category_status}
- Target: {target_score}/100
- Improvement Needed: {improvement_needed} points

Match Assessment:
- Decision: {decision} (Confidence: {confidence}%, Match: {match_score}%)
- Primary Reason: {primary_reason}
- Critical Missing: {', '.join(critical_missing) if critical_missing else 'None'}
- Implicit Likely: {', '.join(implicit_likely) if implicit_likely else 'None'}

Skills Match (Overall: {overall_match_rate}%):
- Technical: {technical_match.get('match_rate', 0)}% ({len(technical_match.get('matched', []))} matched, {len(technical_match.get('missing', []))} missing)
- Soft: {soft_match.get('match_rate', 0)}% ({len(soft_match.get('matched', []))} matched, {len(soft_match.get('missing', []))} missing)
- Domain: {domain_match.get('match_rate', 0)}% ({len(domain_match.get('matched', []))} matched, {len(domain_match.get('missing', []))} missing)

🚨 CRITICAL: ALL MISSING KEYWORDS MUST BE CATEGORIZED
The following keywords are MISSING from the CV (NOT present in CV, but present in JD) and MUST be categorized into Tier 1, Tier 2, or Tier 3:

⚠️ CRITICAL: DO NOT categorize keywords that are ALREADY in the CV. 
The following keywords are ALREADY in the CV (MATCHED) and MUST NOT be categorized:
- Matched Technical: {', '.join(technical_match.get('matched', [])[:10]) if technical_match.get('matched', []) else 'None'}
- Matched Soft: {', '.join(soft_match.get('matched', [])[:10]) if soft_match.get('matched', []) else 'None'}
- Matched Domain: {', '.join(domain_match.get('matched', [])[:10]) if domain_match.get('matched', []) else 'None'}

If a keyword appears in both the MATCHED list above AND the MISSING list below, it is ALREADY in the CV and MUST NOT be categorized.

MISSING TECHNICAL KEYWORDS ({len(technical_match.get('missing', []))} total) - NOT in CV, but in JD:
{chr(10).join(f'  - {kw}' for kw in technical_match.get('missing', [])) if technical_match.get('missing', []) else '  - None'}

MISSING SOFT SKILLS ({len(soft_match.get('missing', []))} total) - NOT in CV, but in JD:
{chr(10).join(f'  - {kw}' for kw in soft_match.get('missing', [])) if soft_match.get('missing', []) else '  - None'}

MISSING DOMAIN KEYWORDS ({len(domain_match.get('missing', []))} total) - NOT in CV, but in JD:
{chr(10).join(f'  - {kw}' for kw in domain_match.get('missing', [])) if domain_match.get('missing', []) else '  - None'}

⚠️ STRICT REQUIREMENT: You MUST categorize EVERY SINGLE missing keyword listed above into exactly ONE tier:
- Tier 1 (tier1_integrate_immediately): Generic, transferable keywords that can be safely added
- Tier 2 (tier2_add_with_evidence): Keywords that require semantic evidence from CV
- Tier 3 (tier3_never_add): Unverifiable or domain-specific keywords without evidence

The total number of keywords in tier1 + tier2 + tier3 MUST equal the total missing keywords count above.

Component Scores:
- Technical: {technical_component.get('score', 0)}/100 (Core Match: {technical_component.get('core_match', 0)}%, Stack Fit: {technical_component.get('stack_fit', 0)}%)
- Skills: {skills_component.get('score', 0)}/100 (Business Readiness: {skills_component.get('business_readiness', 0)}/100)
- Experience: {experience_component.get('alignment_score', 0)}/100 ({experience_component.get('years', 0)} years total, {experience_component.get('corporate_years', 0)} corporate)
- Seniority: {seniority_component.get('score', 0)}/100 (CV: {seniority_component.get('cv_level', 'Unknown')}, JD: {seniority_component.get('jd_level', 'Unknown')})
- Industry: {industry_component.get('alignment_score', 0)}/100 ({industry_component.get('cv_industry', 'Unknown')} → {industry_component.get('jd_industry', 'Unknown')}, Difficulty: {industry_component.get('transition_difficulty', 'UNKNOWN')})

ATS Breakdown:
- Category 1 (Keywords): {category1_score} points (Missing: {missing_counts.get('technical', 0)} technical, {missing_counts.get('soft', 0)} soft, {missing_counts.get('domain', 0)} domain)
- Category 2 (AI Analysis): {category2_score} points

⚠️ NOTE: The "Keyword Tiers" section above shows PRE-CLASSIFIED keywords from previous analysis. 
You MUST re-categorize ALL missing keywords listed in the "MISSING KEYWORDS" section below, 
regardless of any pre-classification. ONLY use the missing keywords lists for categorization.

Keyword Tiers (Reference Only - Use MISSING KEYWORDS lists below instead):
- Tier 1 (Always Add): Technical: {', '.join(tier1_keywords.get('technical', [])) if tier1_keywords.get('technical') else 'None'} | Soft: {', '.join(tier1_keywords.get('soft', [])) if tier1_keywords.get('soft') else 'None'}
- Tier 2 (Add with Evidence): Technical: {', '.join(tier2_keywords.get('technical', [])) if tier2_keywords.get('technical') else 'None'} | Soft: {', '.join(tier2_keywords.get('soft', [])) if tier2_keywords.get('soft') else 'None'}
- Tier 3 (Never Add): Technical: {', '.join(tier3_keywords.get('technical', [])) if tier3_keywords.get('technical') else 'None'} | Domain: {', '.join(tier3_keywords.get('domain', [])) if tier3_keywords.get('domain') else 'None'}

Strategic Guidance:
- Primary Objective: {primary_objective}
- Tone: {tone_guidance}
- Emphasis: {', '.join(emphasis_areas) if emphasis_areas else 'Transferable skills and achievements'}
- De-emphasize: {', '.join(de_emphasize_areas) if de_emphasize_areas else 'None'}
- Bridging: {', '.join(industry_bridging) if industry_bridging else 'None'}

Constraints:
- No Fabrication: Only reframe/highlight existing CV experiences
- Evidence Required: All recommendations need basis, integration, validation, risk
- Tier 1: Integrate ALL (generic/transferable)
- Tier 2: Add ONLY with semantic evidence
- Tier 3: NEVER add (unverifiable/domain-specific)

REQUIRED OUTPUT FORMAT (CRITICAL)

**IMPORTANT:** You MUST return a valid JSON object with the following structure. Do NOT return markdown or any other format.

Return ONLY this JSON structure (no preamble, no markdown formatting, no code blocks):

```json
{{
  "executive_summary": {{
    "current_ats_score": {final_ats_score},
    "target_score": {target_score},
    "improvement_needed": {improvement_needed},
    "overall_match_rate": {overall_match_rate},
    "primary_objective": "{primary_objective}",
    "key_challenge": "{industry_component.get('transition_difficulty', 'UNKNOWN')} industry transition from {industry_component.get('cv_industry', 'Unknown')} to {industry_component.get('jd_industry', 'Unknown')}"
  }},
  
  "priority_gaps": {{
    "immediate_action": {{
      "category1_missing": {{
        "technical": {missing_counts.get('technical', 0)},
        "soft": {missing_counts.get('soft', 0)},
        "domain": {missing_counts.get('domain', 0)}
      }},
      "match_rates": {{
        "technical": {technical_match.get('match_rate', 0)},
        "soft": {soft_match.get('match_rate', 0)},
        "domain": {domain_match.get('match_rate', 0)}
      }}
    }},
    "optimization_opportunities": {{
      "technical_depth": {technical_component.get('score', 0)},
      "experience_alignment": {experience_component.get('alignment_score', 0)},
      "industry_fit": {industry_component.get('alignment_score', 0)}
    }}
  }},
  
  "keyword_integration": {{
    "tier1_integrate_immediately": {{
      "technical": [
        {{
          "keyword": "keyword_name",
          "basis": "Why it's safe to add (generic/transferable nature)",
          "integration": "Where to add in CV (skills section, which bullets)",
          "validation": "How to explain if asked",
          "risk": "low"
        }}
      ],
      "soft": [
        {{
          "keyword": "Collaboration",
          "basis": "Already present in CV, can be expanded",
          "integration": "Highlight in skills section and in bullets related to teamwork",
          "validation": "Discuss examples of successful team projects",
          "risk": "low"
        }}
      ]
    }},
    
    "tier2_add_with_evidence": {{
      "technical": [
        {{
          "keyword": "Business process design",
          "basis": "If any project involved process optimization",
          "integration": "Mention in relevant project bullet points",
          "validation": "Describe a specific instance of process improvement",
          "risk": "medium"
        }}
      ],
      "soft": [
        {{
          "keyword": "Relationship development",
          "basis": "If involved in stakeholder or client interactions",
          "integration": "Highlight in skills section and in bullets related to stakeholder engagement",
          "validation": "Provide examples of building and maintaining professional relationships",
          "risk": "medium"
        }}
      ]
    }},
    
    "tier3_never_add": {{
      "technical": [
        {{
          "keyword": "IAM",
          "why_not": "No direct experience or evidence in CV",
          "risk": "high",
          "alternative": "Focus on transferable skills and learning potential"
        }}
      ],
      "domain": [
        {{
          "keyword": "Christian identity",
          "why_not": "Domain-specific without direct experience",
          "risk": "high",
          "alternative": "Emphasize adaptability and willingness to learn"
        }}
      ]
    }}
  }},
  
  "experience_reframing": {{
    "industry_transition": {{
      "objective": "{primary_objective}",
      "emphasis_areas": {emphasis_areas if emphasis_areas else ["Focus on transferable skills and achievements"]},
      "de_emphasize": {de_emphasize_areas if de_emphasize_areas else []},
      "bridging_statements": {industry_bridging if industry_bridging else []}
    }},
    
    "seniority_positioning": {{
      "current_level": "{seniority_component.get('cv_level', 'Unknown')}",
      "target_level": "{seniority_component.get('jd_level', 'Unknown')}",
      "strategy": "Highlight leadership potential through project ownership and initiative-taking in current roles"
    }},
    
    "technical_showcase": {{
      "strengths_to_highlight": {technical_component.get('strengths', [])},
      "gaps_to_address": {technical_component.get('gaps', [])}
    }}
  }},
  
  "strategic_warnings": {{
    "dont_oversell": {{
      "tier3_keywords": "Never add without direct evidence",
      "domain_specific": {tier3_keywords.get('domain', [])},
      "unverifiable_skills": {tier3_keywords.get('technical', [])[:5]}
    }},
    "dont_undersell": {{
      "matched_skills": {technical_match.get('matched', [])[:5]},
      "transferable_experience": {experience_component.get('strengths', [])[:3]},
      "core_competencies": {skills_component.get('strengths', [])[:3]}
    }}
  }},
  
  "implementation_roadmap": {{
    "phase1_quick_wins": [
      "Add ALL Tier 1 keywords to skills section",
      "Emphasize matched technical skills in experience bullets",
      "Reframe experience using industry bridging statements"
    ],
    "phase2_evidence_based": [
      "Review Tier 2 keywords for semantic evidence",
      "Add only keywords with concrete validation",
      "Document defense strategy for each addition"
    ],
    "phase3_positioning": [
      "Adjust tone per guidance: {tone_guidance}",
      "De-emphasize non-relevant skills",
      "Optimize for target seniority level"
    ]
  }},
  
  "tone_and_style": {{
    "overall_tone": "{tone_guidance}",
    "key_messages": {emphasis_areas if emphasis_areas else ["Transferable skills", "Business impact", "Quantified results"]},
    "avoid_messages": {de_emphasize_areas if de_emphasize_areas else []}
  }}
}}
```

**VALIDATION RULES:**
1. All keyword recommendations MUST include: keyword, basis, integration, validation, risk
2. Risk levels MUST be: "low", "medium", or "high"
3. All arrays MUST be valid JSON arrays
4. All strings MUST be properly escaped
5. Return ONLY valid JSON, no markdown formatting
6. No preamble text before the JSON
7. No code block markers (no ```json or ```)

**🚨 CRITICAL KEYWORD CATEGORIZATION REQUIREMENT:**
- You MUST categorize EVERY SINGLE missing keyword listed in the "MISSING KEYWORDS" section above
- ⚠️ DO NOT categorize keywords that are ALREADY in the CV (matched keywords). ONLY categorize keywords from the MISSING lists.
- Count verification: tier1_integrate_immediately (all categories) + tier2_add_with_evidence (all categories) + tier3_never_add (all categories) = Total missing keywords
- Example: If there are 14 missing technical keywords, the sum of technical keywords in tier1 + tier2 + tier3 MUST equal 14
- NO keyword should be omitted or left uncategorized
- If a keyword appears in the missing list, it MUST appear in exactly ONE tier (tier1, tier2, or tier3)
- If a keyword is ALREADY in the CV (matched), it MUST NOT appear in any tier (tier1, tier2, or tier3)

**CRITICAL:** The output will be parsed programmatically. Invalid JSON will cause system failure. Ensure perfect JSON syntax.
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
OUTPUT: Structured JSON for machine-readable CV generation
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