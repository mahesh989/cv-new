#!/usr/bin/env python3
"""
Test script for Job Description Analysis functionality

This script demonstrates how to use the new JD analysis features
and tests the integration with the centralized AI system.
"""

import asyncio
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the JD analysis components
from app.services.jd_analysis import (
    JDAnalyzer, 
    analyze_and_save_company_jd, 
    load_jd_analysis,
    analyze_company_jd
)


async def test_jd_analysis():
    """Test the JD analysis functionality"""
    
    print("🧪 Testing Job Description Analysis System")
    print("=" * 50)
    
    # Test 1: Analyze company JD
    company_name = "Australia_for_UNHCR"
    
    try:
        print(f"\n1️⃣ Testing analysis for {company_name}")
        print("-" * 30)
        
        # Check if JD file exists
        jd_file = Path(f"/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend/cv-analysis/{company_name}/jd_original.txt")
        if not jd_file.exists():
            print(f"❌ JD file not found: {jd_file}")
            print("Please ensure the JD file exists before running this test.")
            return
        
        print(f"✅ JD file found: {jd_file}")
        
        # Perform analysis
        result = await analyze_and_save_company_jd(company_name, force_refresh=True)
        
        print(f"✅ Analysis completed!")
        print(f"📊 Results:")
        print(f"   - Required keywords: {len(result.required_keywords)}")
        print(f"   - Preferred keywords: {len(result.preferred_keywords)}")
        print(f"   - Total keywords: {len(result.all_keywords)}")
        print(f"   - Experience years: {result.experience_years}")
        print(f"   - AI model used: {result.ai_model_used}")
        print(f"   - Analysis timestamp: {result.analysis_timestamp}")
        
        # Show some keywords
        if result.required_keywords:
            print(f"   - Sample required keywords: {result.required_keywords[:3]}")
        if result.preferred_keywords:
            print(f"   - Sample preferred keywords: {result.preferred_keywords[:3]}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return
    
    # Test 2: Load saved analysis
    try:
        print(f"\n2️⃣ Testing load saved analysis for {company_name}")
        print("-" * 30)
        
        saved_result = load_jd_analysis(company_name)
        
        if saved_result:
            print(f"✅ Loaded saved analysis!")
            print(f"📊 Saved Results:")
            print(f"   - Required keywords: {len(saved_result.required_keywords)}")
            print(f"   - Preferred keywords: {len(saved_result.preferred_keywords)}")
            print(f"   - Analysis timestamp: {saved_result.analysis_timestamp}")
        else:
            print(f"❌ No saved analysis found")
            
    except Exception as e:
        print(f"❌ Load failed: {e}")
    
    # Test 3: Test with different company (if exists)
    try:
        print(f"\n3️⃣ Testing with different company")
        print("-" * 30)
        
        # Check for other companies
        analysis_dir = Path("/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend/cv-analysis")
        companies = [d.name for d in analysis_dir.iterdir() if d.is_dir()]
        
        print(f"📁 Available companies: {companies}")
        
        if len(companies) > 1:
            other_company = companies[1] if companies[1] != company_name else companies[0]
            print(f"🔍 Testing with: {other_company}")
            
            result = await analyze_and_save_company_jd(other_company, force_refresh=False)
            print(f"✅ Analysis completed for {other_company}")
            print(f"   - Keywords found: {len(result.all_keywords)}")
        else:
            print("ℹ️ Only one company found, skipping multi-company test")
            
    except Exception as e:
        print(f"❌ Multi-company test failed: {e}")
    
    # Test 4: Test AI service integration
    try:
        print(f"\n4️⃣ Testing AI service integration")
        print("-" * 30)
        
        analyzer = JDAnalyzer()
        status = analyzer.get_ai_service_status()
        
        print(f"🤖 AI Service Status:")
        print(f"   - Current provider: {status.get('current_provider', 'N/A')}")
        print(f"   - Current model: {status.get('current_model', 'N/A')}")
        print(f"   - Provider available: {status.get('provider_available', False)}")
        print(f"   - Available providers: {status.get('available_providers', [])}")
        
    except Exception as e:
        print(f"❌ AI service status check failed: {e}")
    
    print(f"\n🎉 Testing completed!")
    print("=" * 50)


async def test_direct_text_analysis():
    """Test analyzing JD text directly"""
    
    print("\n🧪 Testing Direct Text Analysis")
    print("=" * 50)
    
    # Sample job description text
    sample_jd = """
    We are looking for a Senior Data Analyst with minimum 3 years experience.
    
    Required Skills:
    - Strong SQL skills
    - Experience with Power BI
    - Must have Python programming experience
    - Essential: Excel proficiency
    
    Preferred Skills:
    - Knowledge of Tableau
    - Understanding of machine learning
    - Familiarity with cloud platforms
    - Nice to have: R programming
    """
    
    try:
        from app.services.jd_analysis import analyze_jd_text
        
        print("📝 Analyzing sample job description...")
        result = await analyze_jd_text(sample_jd)
        
        print(f"✅ Direct text analysis completed!")
        print(f"📊 Results:")
        print(f"   - Required keywords: {result.required_keywords}")
        print(f"   - Preferred keywords: {result.preferred_keywords}")
        print(f"   - Experience years: {result.experience_years}")
        
    except Exception as e:
        print(f"❌ Direct text analysis failed: {e}")


def test_file_structure():
    """Test the file structure and paths"""
    
    print("\n🧪 Testing File Structure")
    print("=" * 50)
    
    base_path = Path("/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend/cv-analysis")
    
    print(f"📁 Base analysis path: {base_path}")
    print(f"   - Exists: {base_path.exists()}")
    
    if base_path.exists():
        companies = [d.name for d in base_path.iterdir() if d.is_dir()]
        print(f"   - Companies found: {companies}")
        
        for company in companies:
            company_dir = base_path / company
            jd_file = company_dir / "jd_original.txt"
            analysis_file = company_dir / "jd_analysis.json"
            
            print(f"   📂 {company}:")
            print(f"      - JD file exists: {jd_file.exists()}")
            print(f"      - Analysis file exists: {analysis_file.exists()}")
            
            if jd_file.exists():
                size = jd_file.stat().st_size
                print(f"      - JD file size: {size} bytes")


async def main():
    """Main test function"""
    
    print("🚀 Starting Job Description Analysis Tests")
    print("=" * 60)
    
    # Test file structure first
    test_file_structure()
    
    # Test JD analysis functionality
    await test_jd_analysis()
    
    # Test direct text analysis
    await test_direct_text_analysis()
    
    print("\n✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
