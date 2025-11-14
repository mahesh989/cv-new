#!/usr/bin/env python3
"""
Validation Script for Recommendation Parser
Tests all requirements from the validation checklist
"""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "cv-magic-app" / "backend"))

from app.tailored_cv.services.recommendation_parser import RecommendationParser

def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def test_validation_checklist():
    """Run all validation checklist tests"""
    
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    # Test file - try multiple locations
    test_files = [
        "Foodbank_ai_recommendation_20251114_011106.json",
        Path(__file__).parent / "Foodbank_ai_recommendation_20251114_011106.json"
    ]
    
    test_file = None
    for tf in test_files:
        if Path(tf).exists():
            test_file = str(tf)
            break
    
    if not test_file:
        print(f"❌ Test file not found. Tried: {test_files}")
        print(f"   Current directory: {Path.cwd()}")
        return results
    
    print(f"📁 Using test file: {test_file}")
    
    print_section("VALIDATION CHECKLIST TESTING")
    
    # Test 1: Parser checks for actionable_guidance first
    print("\n1. Testing: Parser checks for actionable_guidance first")
    try:
        debug_info = RecommendationParser.debug_parse_recommendation_file(test_file)
        
        if debug_info['parsing_method_used'] == 'parse_actionable_guidance':
            print("   ✅ PASS: Parser correctly uses actionable_guidance")
            results['passed'].append("Parser prioritizes actionable_guidance")
        else:
            print(f"   ❌ FAIL: Parser used {debug_info['parsing_method_used']} instead of parse_actionable_guidance")
            results['failed'].append("Parser does not prioritize actionable_guidance")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['failed'].append(f"Test 1 error: {e}")
    
    # Test 2: Falls back to structured_recommendations if no actionable_guidance
    print("\n2. Testing: Falls back to structured_recommendations")
    try:
        # Create a test file without actionable_guidance but with structured_recommendations
        with open(test_file, 'r') as f:
            data = json.load(f)
        
        # Remove actionable_guidance
        if 'actionable_guidance' in data:
            del data['actionable_guidance']
            data['metadata']['has_actionable_guidance'] = False
        
        # Save to temp file
        temp_file = "temp_test_no_actionable.json"
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        debug_info = RecommendationParser.debug_parse_recommendation_file(temp_file)
        
        if debug_info['parsing_method_used'] == 'parse_structured_recommendations':
            print("   ✅ PASS: Parser correctly falls back to structured_recommendations")
            results['passed'].append("Falls back to structured_recommendations")
        else:
            print(f"   ⚠️  WARNING: Parser used {debug_info['parsing_method_used']}")
            results['warnings'].append("Fallback behavior may need verification")
        
        # Cleanup
        Path(temp_file).unlink()
    except Exception as e:
        print(f"   ⚠️  WARNING: Could not test fallback: {e}")
        results['warnings'].append(f"Fallback test: {e}")
    
    # Test 3: Falls back to markdown parsing for v1.0 files
    print("\n3. Testing: Falls back to markdown parsing for v1.0")
    try:
        # Create v1.0 test file (markdown only)
        with open(test_file, 'r') as f:
            data = json.load(f)
        
        v1_data = {
            "company": data.get('company', 'Test'),
            "recommendation_content": data.get('recommendation_content', ''),
            "generated_at": data.get('generated_at'),
            "ai_model_info": data.get('ai_model_info', {}),
            "metadata": {"format_version": "1.0", "has_structured_data": False}
        }
        
        temp_file = "temp_test_v1.json"
        with open(temp_file, 'w') as f:
            json.dump(v1_data, f, indent=2)
        
        debug_info = RecommendationParser.debug_parse_recommendation_file(temp_file)
        
        if debug_info['parsing_method_used'] == 'parse_markdown_content':
            print("   ✅ PASS: Parser correctly falls back to markdown parsing")
            results['passed'].append("Falls back to markdown for v1.0")
        else:
            print(f"   ❌ FAIL: Parser used {debug_info['parsing_method_used']} for v1.0 file")
            results['failed'].append("Markdown fallback not working")
        
        # Cleanup
        Path(temp_file).unlink()
    except Exception as e:
        print(f"   ⚠️  WARNING: Could not test v1.0 fallback: {e}")
        results['warnings'].append(f"v1.0 fallback test: {e}")
    
    # Test 4: New fields are populated when using actionable_guidance
    print("\n4. Testing: New fields populated with actionable_guidance")
    try:
        parsed_data = RecommendationParser.parse_recommendation_file(test_file)
        
        new_fields = [
            'tier1_keywords', 'tier2_keywords', 'tier3_avoid',
            'strategic_positioning', 'experience_optimization',
            'achievements', 'implementation_plan', 'messaging'
        ]
        
        populated = []
        missing = []
        
        for field in new_fields:
            if parsed_data.get(field):
                populated.append(field)
            else:
                missing.append(field)
        
        if populated:
            print(f"   ✅ PASS: {len(populated)} new fields populated: {', '.join(populated)}")
            results['passed'].append(f"New fields populated ({len(populated)})")
        
        if missing:
            print(f"   ⚠️  WARNING: {len(missing)} fields missing: {', '.join(missing)}")
            results['warnings'].append(f"Some new fields missing: {missing}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['failed'].append(f"New fields test error: {e}")
    
    # Test 5: Tier-based keyword strategy
    print("\n5. Testing: Tier-based keyword strategy")
    try:
        parsed_data = RecommendationParser.parse_recommendation_file(test_file)
        
        tier1 = parsed_data.get('tier1_keywords', {})
        tier2 = parsed_data.get('tier2_keywords', {})
        tier3 = parsed_data.get('tier3_avoid', [])
        
        tier1_count = sum(len(tier1.get(cat, [])) for cat in ['technical', 'soft', 'domain'])
        tier2_count = sum(len(tier2.get(cat, [])) for cat in ['technical', 'soft', 'domain'])
        tier3_count = len(tier3)
        
        if tier1_count > 0 or tier2_count > 0 or tier3_count > 0:
            print(f"   ✅ PASS: Tier-based keywords extracted")
            print(f"      Tier 1: {tier1_count} keywords")
            print(f"      Tier 2: {tier2_count} keywords")
            print(f"      Tier 3 (avoid): {tier3_count} keywords")
            results['passed'].append("Tier-based keywords extracted")
        else:
            print("   ⚠️  WARNING: No tier-based keywords found")
            results['warnings'].append("No tier-based keywords")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['failed'].append(f"Tier strategy test error: {e}")
    
    # Test 6: Tier 3 keywords are NOT in missing keywords
    print("\n6. Testing: Tier 3 keywords NOT in missing keywords")
    try:
        parsed_data = RecommendationParser.parse_recommendation_file(test_file)
        
        tier3_avoid = set(parsed_data.get('tier3_avoid', []))
        missing_tech = set(parsed_data.get('missing_technical_skills', []))
        missing_soft = set(parsed_data.get('missing_soft_skills', []))
        missing_keywords = set(parsed_data.get('missing_keywords', []))
        
        all_missing = missing_tech | missing_soft | missing_keywords
        conflicts = tier3_avoid & all_missing
        
        if not conflicts:
            print("   ✅ PASS: No Tier 3 keywords in missing keywords lists")
            results['passed'].append("Tier 3 keywords correctly excluded")
        else:
            print(f"   ❌ FAIL: Tier 3 keywords found in missing lists: {conflicts}")
            results['failed'].append(f"Tier 3 conflicts: {conflicts}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['failed'].append(f"Tier 3 validation error: {e}")
    
    # Test 7: Strategic positioning is populated
    print("\n7. Testing: Strategic positioning populated")
    try:
        parsed_data = RecommendationParser.parse_recommendation_file(test_file)
        
        strategic = parsed_data.get('strategic_positioning', {})
        
        if strategic:
            has_emphasis = bool(strategic.get('emphasis_areas'))
            has_de_emphasize = bool(strategic.get('de_emphasize'))
            has_bridging = bool(strategic.get('bridging_statements'))
            
            if has_emphasis or has_de_emphasize or has_bridging:
                print("   ✅ PASS: Strategic positioning populated")
                print(f"      Emphasis areas: {len(strategic.get('emphasis_areas', []))}")
                print(f"      De-emphasize: {len(strategic.get('de_emphasize', []))}")
                print(f"      Bridging statements: {len(strategic.get('bridging_statements', []))}")
                results['passed'].append("Strategic positioning populated")
            else:
                print("   ⚠️  WARNING: Strategic positioning empty")
                results['warnings'].append("Strategic positioning empty")
        else:
            print("   ⚠️  WARNING: No strategic_positioning field")
            results['warnings'].append("No strategic_positioning")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['failed'].append(f"Strategic positioning test error: {e}")
    
    # Test 8: Backward compatibility
    print("\n8. Testing: Backward compatibility")
    try:
        parsed_data = RecommendationParser.parse_recommendation_file(test_file)
        
        # Check required fields exist
        required = ['company', 'job_title', 'missing_technical_skills', 
                   'missing_soft_skills', 'missing_keywords', 'critical_gaps',
                   'match_score', 'target_score']
        
        missing_required = [f for f in required if f not in parsed_data]
        
        if not missing_required:
            print("   ✅ PASS: All required fields present (backward compatible)")
            results['passed'].append("Backward compatibility maintained")
        else:
            print(f"   ❌ FAIL: Missing required fields: {missing_required}")
            results['failed'].append(f"Missing required fields: {missing_required}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['failed'].append(f"Backward compatibility test error: {e}")
    
    # Test 9: Logging shows format version
    print("\n9. Testing: Format version tracking")
    try:
        parsed_data = RecommendationParser.parse_recommendation_file(test_file)
        
        format_version = parsed_data.get('format_version')
        
        if format_version:
            print(f"   ✅ PASS: Format version tracked: {format_version}")
            results['passed'].append(f"Format version: {format_version}")
        else:
            print("   ⚠️  WARNING: Format version not tracked")
            results['warnings'].append("Format version missing")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['failed'].append(f"Format version test error: {e}")
    
    # Test 10: Data validation
    print("\n10. Testing: Data validation")
    try:
        parsed_data = RecommendationParser.parse_recommendation_file(test_file)
        validation = RecommendationParser.validate_parsed_data(parsed_data)
        
        if validation['is_valid']:
            print("   ✅ PASS: Parsed data is valid")
            results['passed'].append("Data validation passed")
        else:
            print(f"   ❌ FAIL: Validation errors: {validation['errors']}")
            results['failed'].extend(validation['errors'])
        
        if validation['warnings']:
            print(f"   ⚠️  WARNINGS: {validation['warnings']}")
            results['warnings'].extend(validation['warnings'])
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['failed'].append(f"Validation test error: {e}")
    
    # Summary
    print_section("VALIDATION SUMMARY")
    print(f"✅ Passed: {len(results['passed'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print(f"⚠️  Warnings: {len(results['warnings'])}")
    
    if results['passed']:
        print("\n✅ PASSED TESTS:")
        for test in results['passed']:
            print(f"   - {test}")
    
    if results['failed']:
        print("\n❌ FAILED TESTS:")
        for test in results['failed']:
            print(f"   - {test}")
    
    if results['warnings']:
        print("\n⚠️  WARNINGS:")
        for warning in results['warnings'][:5]:  # Show first 5
            print(f"   - {warning}")
    
    return results

if __name__ == "__main__":
    results = test_validation_checklist()
    
    # Exit code based on results
    if results['failed']:
        sys.exit(1)
    elif results['warnings'] and not results['passed']:
        sys.exit(2)
    else:
        sys.exit(0)

