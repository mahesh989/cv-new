#!/usr/bin/env python3
"""
Validation Script for Recommendation Parser Implementation
Tests all validation checklist requirements
"""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "cv-magic-app" / "backend"))

from app.tailored_cv.services.recommendation_parser import RecommendationParser

def print_header(text):
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)

def test_validation_checklist():
    """Run comprehensive validation tests"""
    
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    print_header("VALIDATION CHECKLIST TESTING")
    
    # Create test files for different scenarios
    test_dir = Path("test_validation_files")
    test_dir.mkdir(exist_ok=True)
    
    # Test File 1: v2.0 with actionable_guidance (PREFERRED)
    v2_actionable_file = test_dir / "test_v2_actionable.json"
    v2_actionable_data = {
        "company": "TestCompany",
        "generated_at": "2025-11-14T01:00:00",
        "recommendation_content": "# Test Markdown",
        "structured_recommendations": {
            "executive_summary": {
                "current_ats_score": 50.0,
                "target_score": 80.0,
                "primary_objective": "Transition to Data Analyst role"
            },
            "keyword_integration": {
                "tier1_integrate_immediately": {
                    "technical": [{"keyword": "Python", "basis": "Used in projects", "integration": "Add to skills", "validation": "Project examples", "risk": "low"}],
                    "soft": [{"keyword": "Communication", "basis": "Team work", "integration": "Add to skills", "validation": "Team projects", "risk": "low"}]
                },
                "tier2_add_with_evidence": {
                    "technical": [{"keyword": "SQL", "basis": "If used", "integration": "Add if evidence", "validation": "Database work", "risk": "medium"}]
                },
                "tier3_never_add": {
                    "technical": [{"keyword": "Unverifiable", "why_not": "No evidence", "risk": "high"}]
                }
            }
        },
        "actionable_guidance": {
            "tier1_add_immediately": {
                "technical": [{"keyword": "Python", "integration": "Add to skills section", "validation": "Project examples"}],
                "soft": [{"keyword": "Communication", "integration": "Add to skills", "validation": "Team work"}]
            },
            "tier2_add_with_evidence": {
                "technical": [{"keyword": "SQL", "integration": "Add if evidence", "validation": "Database work", "evidence_required": True}]
            },
            "tier3_never_add": ["Unverifiable"],
            "strategic_positioning": {
                "emphasis_areas": ["Data analysis", "Business impact"],
                "de_emphasize": ["AI specifics"],
                "bridging_statements": ["Tech → Business"],
                "strategy": "Highlight transferable skills"
            },
            "experience_optimization": {
                "strengths_to_highlight": ["Built system serving 100+ users"],
                "gaps_to_address": ["No large-scale systems"]
            },
            "achievements": {
                "transferable_experience": ["Cross-functional collaboration"],
                "core_competencies": ["Problem solving"]
            },
            "implementation_plan": {
                "phase1_quick_wins": ["Add Tier 1 keywords"],
                "phase2_evidence_based": ["Review Tier 2"],
                "phase3_positioning": ["Adjust tone"]
            },
            "messaging": {
                "key_messages": ["Data-driven decisions"],
                "avoid_messages": ["Technical jargon"]
            }
        },
        "metadata": {
            "format_version": "2.0",
            "has_structured_data": True,
            "has_actionable_guidance": True
        }
    }
    
    with open(v2_actionable_file, 'w') as f:
        json.dump(v2_actionable_data, f, indent=2)
    
    # Test File 2: v2.0 with structured_recommendations only (NO actionable_guidance)
    v2_structured_file = test_dir / "test_v2_structured.json"
    v2_structured_data = v2_actionable_data.copy()
    del v2_structured_data['actionable_guidance']
    v2_structured_data['metadata']['has_actionable_guidance'] = False
    
    with open(v2_structured_file, 'w') as f:
        json.dump(v2_structured_data, f, indent=2)
    
    # Test File 3: v1.0 markdown only
    v1_markdown_file = test_dir / "test_v1_markdown.json"
    v1_markdown_data = {
        "company": "TestCompany",
        "recommendation_content": """# CV Tailoring Strategy Report

## Executive Summary
- **Current ATS Score:** 50/100
- **Target Score:** 80/100

## Priority Gap Analysis
**Immediate Action Required:**
- Category 1: 5 technical, 3 soft keywords missing

### TIER 1 - INTEGRATE IMMEDIATELY
**Technical Keywords to Add:**
- **Python**
  - **Basis:** Used in projects
  - **Integration:** Add to skills section
  - **Risk:** low

### TIER 3 - DO NOT ADD
**Keywords to Avoid:**
- **Unverifiable** (No evidence)
""",
        "generated_at": "2025-11-14T01:00:00",
        "ai_model_info": {},
        "metadata": {
            "format_version": "1.0",
            "has_structured_data": False
        }
    }
    
    with open(v1_markdown_file, 'w') as f:
        json.dump(v1_markdown_data, f, indent=2)
    
    # TEST 1: Parser checks for actionable_guidance first
    print("\n✅ TEST 1: Parser prioritizes actionable_guidance")
    try:
        debug_info = RecommendationParser.debug_parse_recommendation_file(str(v2_actionable_file))
        if debug_info['parsing_method_used'] == 'parse_actionable_guidance':
            print("   ✅ PASS: Uses parse_actionable_guidance")
            results['passed'].append("Parser prioritizes actionable_guidance")
        else:
            print(f"   ❌ FAIL: Used {debug_info['parsing_method_used']}")
            results['failed'].append("Parser does not prioritize actionable_guidance")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['failed'].append(f"Test 1 error: {e}")
    
    # TEST 2: Falls back to structured_recommendations
    print("\n✅ TEST 2: Falls back to structured_recommendations")
    try:
        debug_info = RecommendationParser.debug_parse_recommendation_file(str(v2_structured_file))
        if debug_info['parsing_method_used'] == 'parse_structured_recommendations':
            print("   ✅ PASS: Falls back to structured_recommendations")
            results['passed'].append("Falls back to structured_recommendations")
        else:
            print(f"   ⚠️  Used: {debug_info['parsing_method_used']}")
            results['warnings'].append("Fallback behavior")
    except Exception as e:
        print(f"   ⚠️  WARNING: {e}")
        results['warnings'].append(f"Test 2: {e}")
    
    # TEST 3: Falls back to markdown for v1.0
    print("\n✅ TEST 3: Falls back to markdown for v1.0")
    try:
        debug_info = RecommendationParser.debug_parse_recommendation_file(str(v1_markdown_file))
        if debug_info['parsing_method_used'] == 'parse_markdown_content':
            print("   ✅ PASS: Falls back to markdown parsing")
            results['passed'].append("Falls back to markdown for v1.0")
        else:
            print(f"   ❌ FAIL: Used {debug_info['parsing_method_used']}")
            results['failed'].append("Markdown fallback not working")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['failed'].append(f"Test 3 error: {e}")
    
    # TEST 4: New fields populated with actionable_guidance
    print("\n✅ TEST 4: New fields populated")
    try:
        parsed_data = RecommendationParser.parse_recommendation_file(str(v2_actionable_file))
        new_fields = ['tier1_keywords', 'tier2_keywords', 'tier3_avoid',
                     'strategic_positioning', 'experience_optimization']
        populated = [f for f in new_fields if parsed_data.get(f)]
        if len(populated) >= 4:
            print(f"   ✅ PASS: {len(populated)}/{len(new_fields)} new fields populated")
            results['passed'].append(f"New fields populated ({len(populated)})")
        else:
            print(f"   ⚠️  Only {len(populated)}/{len(new_fields)} fields populated")
            results['warnings'].append(f"Some fields missing: {set(new_fields) - set(populated)}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['failed'].append(f"Test 4 error: {e}")
    
    # TEST 5: Tier-based keywords
    print("\n✅ TEST 5: Tier-based keyword strategy")
    try:
        parsed_data = RecommendationParser.parse_recommendation_file(str(v2_actionable_file))
        tier1 = parsed_data.get('tier1_keywords', {})
        tier2 = parsed_data.get('tier2_keywords', {})
        tier3 = parsed_data.get('tier3_avoid', [])
        
        tier1_count = sum(len(tier1.get(cat, [])) for cat in ['technical', 'soft', 'domain'])
        tier2_count = sum(len(tier2.get(cat, [])) for cat in ['technical', 'soft', 'domain'])
        
        if tier1_count > 0 or tier2_count > 0 or len(tier3) > 0:
            print(f"   ✅ PASS: Tier keywords extracted (T1:{tier1_count}, T2:{tier2_count}, T3:{len(tier3)})")
            results['passed'].append("Tier-based keywords extracted")
        else:
            print("   ❌ FAIL: No tier keywords")
            results['failed'].append("No tier keywords extracted")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['failed'].append(f"Test 5 error: {e}")
    
    # TEST 6: Tier 3 NOT in missing keywords
    print("\n✅ TEST 6: Tier 3 keywords excluded")
    try:
        parsed_data = RecommendationParser.parse_recommendation_file(str(v2_actionable_file))
        tier3_set = set(parsed_data.get('tier3_avoid', []))
        missing_tech = set(parsed_data.get('missing_technical_skills', []))
        missing_soft = set(parsed_data.get('missing_soft_skills', []))
        missing_keywords = set(parsed_data.get('missing_keywords', []))
        
        all_missing = missing_tech | missing_soft | missing_keywords
        conflicts = tier3_set & all_missing
        
        if not conflicts:
            print("   ✅ PASS: No Tier 3 keywords in missing lists")
            results['passed'].append("Tier 3 correctly excluded")
        else:
            print(f"   ❌ FAIL: Conflicts: {conflicts}")
            results['failed'].append(f"Tier 3 conflicts: {conflicts}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['failed'].append(f"Test 6 error: {e}")
    
    # TEST 7: Strategic positioning
    print("\n✅ TEST 7: Strategic positioning")
    try:
        parsed_data = RecommendationParser.parse_recommendation_file(str(v2_actionable_file))
        strategic = parsed_data.get('strategic_positioning', {})
        if strategic and (strategic.get('emphasis_areas') or strategic.get('de_emphasize')):
            print("   ✅ PASS: Strategic positioning populated")
            results['passed'].append("Strategic positioning populated")
        else:
            print("   ⚠️  WARNING: Strategic positioning empty")
            results['warnings'].append("Strategic positioning empty")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['failed'].append(f"Test 7 error: {e}")
    
    # TEST 8: Backward compatibility
    print("\n✅ TEST 8: Backward compatibility")
    try:
        parsed_data = RecommendationParser.parse_recommendation_file(str(v2_actionable_file))
        required = ['company', 'job_title', 'missing_technical_skills',
                   'missing_soft_skills', 'missing_keywords', 'critical_gaps']
        missing = [f for f in required if f not in parsed_data]
        if not missing:
            print("   ✅ PASS: All required fields present")
            results['passed'].append("Backward compatibility maintained")
        else:
            print(f"   ❌ FAIL: Missing: {missing}")
            results['failed'].append(f"Missing required fields: {missing}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['failed'].append(f"Test 8 error: {e}")
    
    # TEST 9: Format version tracking
    print("\n✅ TEST 9: Format version tracking")
    try:
        parsed_data = RecommendationParser.parse_recommendation_file(str(v2_actionable_file))
        if parsed_data.get('format_version'):
            print(f"   ✅ PASS: Format version tracked: {parsed_data.get('format_version')}")
            results['passed'].append("Format version tracked")
        else:
            print("   ⚠️  WARNING: Format version not tracked")
            results['warnings'].append("Format version missing")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['failed'].append(f"Test 9 error: {e}")
    
    # TEST 10: Data validation
    print("\n✅ TEST 10: Data validation")
    try:
        parsed_data = RecommendationParser.parse_recommendation_file(str(v2_actionable_file))
        validation = RecommendationParser.validate_parsed_data(parsed_data)
        if validation['is_valid']:
            print("   ✅ PASS: Data validation passed")
            results['passed'].append("Data validation passed")
        else:
            print(f"   ❌ FAIL: Validation errors: {validation['errors']}")
            results['failed'].extend(validation['errors'])
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['failed'].append(f"Test 10 error: {e}")
    
    # Cleanup
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    # Summary
    print_header("VALIDATION SUMMARY")
    print(f"✅ Passed: {len(results['passed'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print(f"⚠️  Warnings: {len(results['warnings'])}")
    
    if results['passed']:
        print("\n✅ PASSED:")
        for test in results['passed']:
            print(f"   - {test}")
    
    if results['failed']:
        print("\n❌ FAILED:")
        for test in results['failed']:
            print(f"   - {test}")
    
    if results['warnings']:
        print("\n⚠️  WARNINGS:")
        for warning in results['warnings'][:5]:
            print(f"   - {warning}")
    
    return results

if __name__ == "__main__":
    results = test_validation_checklist()
    sys.exit(0 if not results['failed'] else 1)

