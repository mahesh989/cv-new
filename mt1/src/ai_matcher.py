import os
import re
import json
from .prompt_system import get_prompt
from .hybrid_ai_service import hybrid_ai
from .print_output_logger import append_output_log

def clean_markdown(text: str) -> str:
    """Remove markdown formatting and clean whitespace"""
    if not text:
        return text
    # Remove **, bullets, and extra whitespace
    text = re.sub(r'\*\*', '', text)  # Remove bold markers
    text = re.sub(r'^\s*[-•]\s*', '', text, flags=re.MULTILINE)  # Remove bullets
    return text.strip()

async def analyze_match_fit(cv_text: str, job_text: str, company_name: str = "Company") -> dict:
    # Use recruiter-style analysis prompt
    prompt = get_prompt("cv_analysis", cv_text=cv_text, job_text=job_text)
    
    try:
        content = await hybrid_ai.generate_response(prompt, temperature=0.3, max_tokens=4000)
        
        # Log the full Claude analysis output - extract company name from JD
        from .analysis_results_saver import AnalysisResultsSaver
        saver = AnalysisResultsSaver()
        company_name = saver.extract_company_name(job_text)
        append_output_log(content, company_name=company_name, tag="ANALYZE_MATCH")
        
        # Create result dictionary
        result = {
            "raw_analysis": content.strip(),
            "formatted_result": {}
        }
        
        return result
    
    except Exception as e:
        print(f"\n❌ [AI_MATCHER] Error in hybrid AI service: {str(e)}")
        print(f"❌ [AI_MATCHER] Error type: {type(e)}")
        import traceback
        print(f"❌ [AI_MATCHER] Full traceback:")
        print(traceback.format_exc())
        print("="*80)
        print("🧠 [AI_MATCHER] ANALYZE MATCH FIT - ERROR")
        print("="*80 + "\n")
        raise


async def intelligent_skill_comparison(cv_skills: dict, jd_skills: dict, company_name: str = "Company") -> dict:
    """
    Enhanced skill comparison with AI reasoning inspired by Python implementation
    Compares CV skills against JD requirements with detailed reasoning
    """
    print(f"🧠 [AI_MATCHER] Starting intelligent skill comparison...")
    print(f"📋 [AI_MATCHER] CV Skills: {cv_skills}")
    print(f"📋 [AI_MATCHER] JD Skills: {jd_skills}")
    
    try:
        # Generate enhanced prompt for skill comparison
        prompt = _generate_intelligent_comparison_prompt(cv_skills, jd_skills)
        
        print(f"🚀 [AI_MATCHER] Generated enhanced prompt for LLM")
        
        # Get AI response with reasoning
        response = await hybrid_ai.generate_response(prompt, temperature=0.3, max_tokens=3000)
        
        print(f"📥 [AI_MATCHER] Raw LLM response (COMPLETE):")
        print("="*80)
        print(response)
        print("="*80)
        
        # Log the full Claude skill comparison output - use same company name
        append_output_log(response, company_name=company_name, tag="CLAUDE_SKILL_COMPARISON")
        
        # Parse the structured response
        parsed_result = _parse_intelligent_response(response)
        
        # Calculate summary statistics with CV totals for table
        summary = _calculate_comparison_summary(parsed_result, cv_skills)
        parsed_result['match_summary'] = summary
        
        # === UI-Style Pretty Print AI-Powered Skills Analysis ===
        ui_analysis_output = []
        ui_analysis_output.append("\n" + "="*90)
        ui_analysis_output.append("🤖 AI-POWERED SKILLS ANALYSIS")
        ui_analysis_output.append("Enhanced semantic matching with detailed reasoning")
        ui_analysis_output.append("="*90)
        ui_analysis_output.append(f"\n🎯 OVERALL SUMMARY\n{'-'*40}")
        ui_analysis_output.append(f"Total Requirements: {summary['total_requirements']}")
        ui_analysis_output.append(f"Matched: {summary['total_matched']}")
        ui_analysis_output.append(f"Missing: {summary['total_missing']}")
        ui_analysis_output.append(f"Match Rate: {summary['match_percentage']}%\n")
        ui_analysis_output.append("📊 SUMMARY TABLE\n" + '-'*80)
        ui_analysis_output.append(f"{'Category':<20}{'CV Total':>10}{'JD Total':>10}{'Matched':>10}{'Missing':>10}{'Match Rate (%)':>16}")
        for cat, label in zip(['technical', 'soft', 'domain'], ['Technical Skills', 'Soft Skills', 'Domain Keywords']):
            cat_sum = summary['categories'][cat]
            match_rate = (cat_sum['matched'] / cat_sum['jd_total'] * 100) if cat_sum['jd_total'] else 0
            ui_analysis_output.append(f"{label:<20}{cat_sum['cv_total']:>10}{cat_sum['jd_total']:>10}{cat_sum['matched']:>10}{cat_sum['missing']:>10}{match_rate:>16.1f}")
        ui_analysis_output.append("\n🧠 DETAILED AI ANALYSIS\n" + '-'*80)
        for cat, label in zip(['technical_skills', 'soft_skills', 'domain_keywords'], ['TECHNICAL SKILLS', 'SOFT SKILLS', 'DOMAIN KEYWORDS']):
            matched = parsed_result.get(cat, {}).get('matched', [])
            missing = parsed_result.get(cat, {}).get('missing', [])
            ui_analysis_output.append(f"\n🔹 {label}")
            ui_analysis_output.append(f"  ✅ MATCHED JD REQUIREMENTS ({len(matched)} items):")
            if matched:
                for idx, m in enumerate(matched, 1):
                    ui_analysis_output.append(f"    {idx}. JD Required: '{m.get('jd_skill', '')}'\n       → Found in CV: '{m.get('cv_equivalent', '')}'\n       💡 {m.get('reasoning', '')}")
            else:
                ui_analysis_output.append("    (None)")
            ui_analysis_output.append(f"  ❌ MISSING FROM CV ({len(missing)} items):")
            if missing:
                for idx, m in enumerate(missing, 1):
                    ui_analysis_output.append(f"    {idx}. JD Requires: '{m.get('jd_skill', '')}'\n       💡 {m.get('reasoning', '')}")
            else:
                ui_analysis_output.append("    (None)")
        ui_analysis_output.append("="*90 + "\n")
        
        # Print the UI analysis output
        for line in ui_analysis_output:
            print(line)
        
        # Save the UI analysis output to the same file as analyze match results
        ui_analysis_text = "\n".join(ui_analysis_output)
        append_output_log(ui_analysis_text, company_name=company_name, tag="AI_SKILLS_ANALYSIS")
        
        print(f"✅ [AI_MATCHER] Intelligent comparison completed")
        print(f"📊 [AI_MATCHER] Match rate: {summary.get('match_percentage', 0)}%")
        
        return parsed_result
    
    except Exception as e:
        print(f"❌ [AI_MATCHER] Error in intelligent comparison: {e}")
        # Fallback to basic comparison
        return _fallback_comparison(cv_skills, jd_skills)

def _generate_intelligent_comparison_prompt(cv_skills: dict, jd_skills: dict) -> str:
    """Generate enhanced prompt with semantic matching examples"""
    
    prompt = f"""
You are an expert HR analyst and ATS skill matcher. Compare CV skills against JD requirements with intelligent reasoning.

**OBJECTIVE**: Determine which JD requirements are satisfied by CV skills, and which are missing.

**CRITICAL RULES**:
- Direction: JD → CV (match JD requirements against CV skills)
- MATCHED: JD requirement has corresponding CV skill (including semantic matches)
- MISSING: JD requirement has NO corresponding CV skill
- Provide clear reasoning for each decision
- Use intelligent semantic matching, not just exact text

**CV SKILLS** (What candidate has):
Technical: {', '.join(cv_skills.get('technical_skills', []))}
Soft: {', '.join(cv_skills.get('soft_skills', []))}
Domain: {', '.join(cv_skills.get('domain_keywords', []))}

**JD REQUIREMENTS** (What job needs):
Technical: {', '.join(jd_skills.get('technical_skills', []))}
Soft: {', '.join(jd_skills.get('soft_skills', []))}
Domain: {', '.join(jd_skills.get('domain_keywords', []))}

**INTELLIGENT MATCHING EXAMPLES**:
- "Database proficiency" (JD) matches "SQL, PostgreSQL, MySQL" (CV) → MATCHED
- "BI tools" (JD) matches "Power BI, Tableau" (CV) → MATCHED
- "Management skills" (JD) matches "Leadership, Mentoring" (CV) → MATCHED
- "Data analysis methodologies" (JD) matches "Data analysis, Predictive analytics" (CV) → MATCHED
- "Communication skills" (JD) matches "Communication skills" (CV) → MATCHED

**RETURN STRUCTURED JSON**:
{{
    "technical_skills": {{
        "matched": [
            {{
                "jd_skill": "exact JD requirement",
                "cv_equivalent": "matching CV skill(s)",
                "reasoning": "brief explanation of match"
            }}
        ],
        "missing": [
            {{
                "jd_skill": "exact JD requirement",
                "reasoning": "why not found in CV"
            }}
        ]
    }},
    "soft_skills": {{
        "matched": [...],
        "missing": [...]
    }},
    "domain_keywords": {{
        "matched": [...],
        "missing": [...]
    }}
}}

**INSTRUCTIONS**:
- Be intelligent about semantic matching
- Only mark as MISSING if truly no equivalent skill exists
- Provide clear, helpful reasoning for each decision
- Focus on helping candidate understand gaps
"""
    
    return prompt

def _parse_intelligent_response(response: str) -> dict:
    """Parse the AI response into structured format"""
    try:
        # Extract JSON from response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)
            
            print(f"✅ [AI_MATCHER] Successfully parsed JSON response")
            return parsed
        else:
            print(f"⚠️ [AI_MATCHER] No valid JSON found, using fallback parsing")
            return _extract_skills_from_text(response)
            
    except json.JSONDecodeError as e:
        print(f"❌ [AI_MATCHER] JSON parsing failed: {e}")
        return _extract_skills_from_text(response)

def _extract_skills_from_text(response: str) -> dict:
    """Fallback text parsing if JSON fails"""
    result = {
        "technical_skills": {"matched": [], "missing": []},
        "soft_skills": {"matched": [], "missing": []},
        "domain_keywords": {"matched": [], "missing": []}
    }
    
    # Basic text extraction logic
    lines = response.split('\n')
    current_category = None
    current_type = None
    
    for line in lines:
        line = line.strip()
        if 'technical' in line.lower():
            current_category = 'technical_skills'
        elif 'soft' in line.lower():
            current_category = 'soft_skills'
        elif 'domain' in line.lower():
            current_category = 'domain_keywords'
        elif 'matched' in line.lower():
            current_type = 'matched'
        elif 'missing' in line.lower():
            current_type = 'missing'
        elif line and current_category and current_type:
            # Extract skill from line
            skill = line.replace('-', '').replace('*', '').strip()
            if skill:
                if current_type == 'matched':
                    result[current_category]['matched'].append({
                        "jd_skill": skill,
                        "cv_equivalent": skill,
                        "reasoning": "Parsed from text response"
                    })
                else:
                    result[current_category]['missing'].append({
                        "jd_skill": skill,
                        "reasoning": "Not found in CV"
                    })
    
    return result

def _calculate_comparison_summary(results: dict, cv_skills: dict = None) -> dict:
    """Calculate overall match statistics with CV totals for summary table"""
    total_matched = 0
    total_missing = 0
    
    for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
        if category in results:
            total_matched += len(results[category].get('matched', []))
            total_missing += len(results[category].get('missing', []))
    
    total_requirements = total_matched + total_missing
    match_percentage = (total_matched / total_requirements * 100) if total_requirements > 0 else 0
    
    # Enhanced summary with CV totals for table display (Python-inspired)
    summary = {
        'total_requirements': total_requirements,
        'total_matched': total_matched,
        'total_missing': total_missing,
        'match_percentage': round(match_percentage, 1),
        'categories': {
            'technical': {
                'matched': len(results.get('technical_skills', {}).get('matched', [])),
                'missing': len(results.get('technical_skills', {}).get('missing', [])),
                'cv_total': len(cv_skills.get('technical_skills', [])) if cv_skills else 0,
                'jd_total': len(results.get('technical_skills', {}).get('matched', [])) + len(results.get('technical_skills', {}).get('missing', []))
            },
            'soft': {
                'matched': len(results.get('soft_skills', {}).get('matched', [])),
                'missing': len(results.get('soft_skills', {}).get('missing', [])),
                'cv_total': len(cv_skills.get('soft_skills', [])) if cv_skills else 0,
                'jd_total': len(results.get('soft_skills', {}).get('matched', [])) + len(results.get('soft_skills', {}).get('missing', []))
            },
            'domain': {
                'matched': len(results.get('domain_keywords', {}).get('matched', [])),
                'missing': len(results.get('domain_keywords', {}).get('missing', [])),
                'cv_total': len(cv_skills.get('domain_keywords', [])) if cv_skills else 0,
                'jd_total': len(results.get('domain_keywords', {}).get('matched', [])) + len(results.get('domain_keywords', {}).get('missing', []))
            }
        }
    }
    
    return summary

def _fallback_comparison(cv_skills: dict, jd_skills: dict) -> dict:
    """Fallback comparison if AI fails"""
    print(f"🔄 [AI_MATCHER] Using fallback comparison logic")
    
    result = {
        "technical_skills": {"matched": [], "missing": []},
        "soft_skills": {"matched": [], "missing": []},
        "domain_keywords": {"matched": [], "missing": []}
    }
    
    for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
        cv_list = cv_skills.get(category, [])
        jd_list = jd_skills.get(category, [])
        
        for jd_skill in jd_list:
            matched = False
            for cv_skill in cv_list:
                if _is_basic_match(cv_skill, jd_skill):
                    result[category]['matched'].append({
                        "jd_skill": jd_skill,
                        "cv_equivalent": cv_skill,
                        "reasoning": "Basic text match"
                    })
                    matched = True
                    break
            
            if not matched:
                result[category]['missing'].append({
                    "jd_skill": jd_skill,
                    "reasoning": "No matching skill found in CV"
                })
    
    # Add summary with CV totals
    result['match_summary'] = _calculate_comparison_summary(result, cv_skills)
    
    return result

def _is_basic_match(cv_skill: str, jd_skill: str) -> bool:
    """Basic string matching for fallback"""
    cv_lower = cv_skill.lower().strip()
    jd_lower = jd_skill.lower().strip()
    
    return (
        cv_lower == jd_lower or
        cv_lower in jd_lower or
        jd_lower in cv_lower or
        any(word in cv_lower for word in jd_lower.split() if len(word) > 3)
    )
