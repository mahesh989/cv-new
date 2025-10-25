#!/usr/bin/env python3
"""
Test Tier 1 Adaptation System
Tests the enhanced keyword integration with Tier 1 modifications
"""

import sys
import os
import json

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.tailored_cv.services.enhanced_keyword_integrator import EnhancedKeywordIntegrator

def test_tier1_adaptation():
    """Test Tier 1 adaptation system with real CV data"""
    
    # Load the real CV data
    with open('user/test@example.com/cv-analysis/cvs/tailored/Google_tailored_cv_20241220_120000.json', 'r') as f:
        cv_data = json.load(f)

    # Extract CV content
    cv_content = ''
    for exp in cv_data['experience']:
        for bullet in exp.get('bullets', []):
            cv_content += bullet + ' '

    print('🔧 ENHANCED TIER 1 ADAPTATION SYSTEM')
    print('=' * 60)

    # Test keywords that were missing
    test_keywords = ['leadership', 'communication', 'teamwork', 'problem solving']

    integrator = EnhancedKeywordIntegrator(cv_content, 'tier1_adaptation_test')

    print('📊 TESTING TIER 1 ADAPTATION LOGIC:')
    print()

    for keyword in test_keywords:
        print(f'Testing keyword: "{keyword}"')
        
        # Classify the keyword
        classification = integrator.classify_keyword(keyword)
        print(f'  Classification: Tier {classification.tier} ({classification.category})')
        
        # Check for semantic evidence
        has_evidence, reason = integrator.has_semantic_evidence(keyword)
        print(f'  Evidence: {has_evidence} - {reason}')
        
        if classification.tier == 1:
            if has_evidence:
                print(f'  ✅ Action: Integrate directly (has evidence)')
            else:
                print(f'  🔧 Action: Adapt with modifications (generic skill)')
                # Generate modification
                modifications = integrator.generate_tier1_modifications([keyword])
                print(f'  📝 Modification: "{modifications[keyword]}"')
        print()

    print('🎯 FULL INTEGRATION TEST:')
    results = integrator.validate_keyword_integration(test_keywords)

    print('📊 Integration Results:')
    for category, keywords in results.items():
        if keywords:
            print(f'  {category}: {keywords}')

    print()
    print('🔧 Tier 1 Modifications:')
    if results['tier1_adapt']:
        modifications = integrator.generate_tier1_modifications(results['tier1_adapt'])
        for keyword, modification in modifications.items():
            print(f'  "{keyword}" → "{modification}"')

if __name__ == "__main__":
    test_tier1_adaptation()
