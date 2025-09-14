#!/usr/bin/env python3
"""
Test script for recommendation input generation

This script tests the automatic generation of recommendation input files
from existing skills analysis files.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.utils.recommendation_input_generator import generate_recommendation_input_from_file


def test_recommendation_input_generation():
    """Test the recommendation input generation functionality"""
    
    print("🧪 Testing Recommendation Input Generation")
    print("=" * 60)
    
    # Test with the existing Australia_for_UNHCR analysis
    company_name = "Australia_for_UNHCR"
    
    print(f"📁 Testing with company: {company_name}")
    
    try:
        # Generate recommendation input from existing analysis
        recommendation_file = generate_recommendation_input_from_file(company_name)
        
        if recommendation_file:
            print(f"✅ Successfully generated recommendation input file:")
            print(f"   📄 File: {recommendation_file}")
            
            # Check if file exists and has content
            if os.path.exists(recommendation_file):
                file_size = os.path.getsize(recommendation_file)
                print(f"   📊 File size: {file_size:,} bytes")
                
                # Read and display a summary of the content
                import json
                with open(recommendation_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"   📋 Content summary:")
                print(f"      - CV comprehensive analysis: {'✅' if 'cv_comprehensive_analysis' in data else '❌'}")
                print(f"      - JD comprehensive analysis: {'✅' if 'jd_comprehensive_analysis' in data else '❌'}")
                print(f"      - Analyze match entries: {'✅' if 'analyze_match_entries' in data else '❌'}")
                print(f"      - Preextracted comparison: {'✅' if 'preextracted_comparison_entries' in data else '❌'}")
                print(f"      - Component analysis: {'✅' if 'component_analysis_entries' in data else '❌'}")
                print(f"      - ATS calculation: {'✅' if 'ats_calculation_entries' in data else '❌'}")
                
                # Show ATS score if available
                if 'ats_calculation_entries' in data and data['ats_calculation_entries']:
                    ats_score = data['ats_calculation_entries'][0].get('final_ats_score')
                    if ats_score:
                        print(f"      - ATS Score: {ats_score}/100")
                
                print(f"\n🎯 Recommendation input file is ready for use!")
                
            else:
                print(f"❌ Generated file does not exist: {recommendation_file}")
                
        else:
            print(f"❌ Failed to generate recommendation input file")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


def test_with_different_companies():
    """Test with different company names to see what's available"""
    
    print(f"\n🔍 Checking available analysis files...")
    
    analysis_dir = Path("cv-analysis")
    if not analysis_dir.exists():
        print(f"❌ Analysis directory not found: {analysis_dir}")
        return
    
    companies = []
    for company_dir in analysis_dir.iterdir():
        if company_dir.is_dir():
            skills_file = company_dir / f"{company_dir.name}_skills_analysis.json"
            if skills_file.exists():
                companies.append(company_dir.name)
    
    print(f"📁 Found {len(companies)} companies with analysis files:")
    for company in companies:
        print(f"   - {company}")
    
    if companies:
        print(f"\n🧪 Testing with first available company: {companies[0]}")
        try:
            recommendation_file = generate_recommendation_input_from_file(companies[0])
            if recommendation_file:
                print(f"✅ Successfully generated for {companies[0]}")
            else:
                print(f"❌ Failed to generate for {companies[0]}")
        except Exception as e:
            print(f"❌ Error testing {companies[0]}: {e}")


if __name__ == "__main__":
    test_recommendation_input_generation()
    test_with_different_companies()
    
    print(f"\n✅ Testing completed!")
    print(f"💡 The recommendation input generator is now integrated into the ATS calculation pipeline.")
    print(f"   It will automatically create [company_name]_recommendation_input.json files")
    print(f"   whenever ATS calculation is completed.")
