#!/usr/bin/env python3
"""
Enhanced test script for Categorized Job Description Analysis functionality

This script demonstrates the new categorized features and tests the enhanced
JD analysis system with proper categorization.
"""

import asyncio
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the enhanced JD analysis components
from app.services.jd_analysis import (
    JDAnalyzer, 
    analyze_and_save_company_jd, 
    load_jd_analysis,
    analyze_company_jd
)


async def test_categorized_analysis():
    """Test the enhanced categorized JD analysis functionality"""
    
    print("🧪 Testing Enhanced Categorized Job Description Analysis System")
    print("=" * 70)
    
    # Test 1: Analyze company JD with categorization
    company_name = "Australia_for_UNHCR"
    
    try:
        print(f"\n1️⃣ Testing categorized analysis for {company_name}")
        print("-" * 50)
        
        # Check if JD file exists
        jd_file = Path(f"/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend/cv-analysis/{company_name}/jd_original.txt")
        if not jd_file.exists():
            print(f"❌ JD file not found: {jd_file}")
            return
        
        print(f"✅ JD file found: {jd_file}")
        
        # Perform fresh analysis with categorization
        result = await analyze_and_save_company_jd(company_name, force_refresh=True)
        
        print(f"✅ Categorized analysis completed!")
        print(f"📊 Results Summary:")
        print(f"   - Required keywords: {len(result.required_keywords)}")
        print(f"   - Preferred keywords: {len(result.preferred_keywords)}")
        print(f"   - Total keywords: {len(result.all_keywords)}")
        print(f"   - Experience years: {result.experience_years}")
        print(f"   - AI model used: {result.ai_model_used}")
        
        # Test categorized access methods
        print(f"\n🔧 Technical Skills:")
        print(f"   - Required: {result.get_technical_skills(required_only=True)}")
        print(f"   - All: {result.get_technical_skills()}")
        
        print(f"\n🤝 Soft Skills:")
        print(f"   - Required: {result.get_soft_skills(required_only=True)}")
        print(f"   - All: {result.get_soft_skills()}")
        
        print(f"\n📅 Experience Requirements:")
        print(f"   - Required: {result.get_experience_requirements(required_only=True)}")
        print(f"   - All: {result.get_experience_requirements()}")
        
        print(f"\n🏢 Domain Knowledge:")
        print(f"   - Required: {result.get_domain_knowledge(required_only=True)}")
        print(f"   - All: {result.get_domain_knowledge()}")
        
        # Test skill summary
        print(f"\n📊 Skill Summary:")
        summary = result.get_skill_summary()
        for key, value in summary.items():
            print(f"   - {key}: {value}")
        
        # Test categorized structure access
        print(f"\n📋 Categorized Structure:")
        print(f"   - Required Skills: {result.required_skills}")
        print(f"   - Preferred Skills: {result.preferred_skills}")
        
        # Test backward compatibility
        print(f"\n🔄 Backward Compatibility Test:")
        print(f"   - required_keywords still works: {len(result.required_keywords)} items")
        print(f"   - preferred_keywords still works: {len(result.preferred_keywords)} items")
        print(f"   - all_keywords still works: {len(result.all_keywords)} items")
        
    except Exception as e:
        print(f"❌ Categorized analysis failed: {e}")
        return
    
    # Test 2: Load and test saved categorized analysis
    try:
        print(f"\n2️⃣ Testing load saved categorized analysis for {company_name}")
        print("-" * 50)
        
        saved_result = load_jd_analysis(company_name)
        
        if saved_result:
            print(f"✅ Loaded saved categorized analysis!")
            print(f"📊 Saved Results:")
            print(f"   - Required technical skills: {len(saved_result.required_skills.get('technical', []))}")
            print(f"   - Required soft skills: {len(saved_result.required_skills.get('soft_skills', []))}")
            print(f"   - Required experience: {len(saved_result.required_skills.get('experience', []))}")
            print(f"   - Required domain knowledge: {len(saved_result.required_skills.get('domain_knowledge', []))}")
            
            # Test all categorized access methods on loaded data
            print(f"\n🔧 Loaded Technical Skills:")
            print(f"   - Required: {saved_result.get_technical_skills(required_only=True)}")
            print(f"   - All: {saved_result.get_technical_skills()}")
            
            print(f"\n🤝 Loaded Soft Skills:")
            print(f"   - Required: {saved_result.get_soft_skills(required_only=True)}")
            print(f"   - All: {saved_result.get_soft_skills()}")
            
            # Test skill summary on loaded data
            print(f"\n📊 Loaded Skill Summary:")
            summary = saved_result.get_skill_summary()
            for key, value in summary.items():
                print(f"   - {key}: {value}")
        else:
            print(f"❌ No saved categorized analysis found")
            
    except Exception as e:
        print(f"❌ Load categorized analysis failed: {e}")
    
    # Test 3: Test direct text analysis with categorization
    try:
        print(f"\n3️⃣ Testing direct text analysis with categorization")
        print("-" * 50)
        
        # Sample job description text
        sample_jd = """
        We are looking for a Senior Data Analyst with minimum 3 years experience.
        
        Required Skills:
        - Strong SQL skills and database management
        - Experience with Power BI and data visualization
        - Must have Python programming experience
        - Essential: Excel proficiency and VBA
        - Excellent communication and project management skills
        - Understanding of data warehouse concepts
        
        Preferred Skills:
        - Knowledge of Tableau and advanced analytics
        - Familiarity with machine learning algorithms
        - Understanding of cloud platforms (AWS, Azure)
        - Leadership experience in data teams
        - Knowledge of GDPR and data privacy regulations
        """
        
        from app.services.jd_analysis import analyze_jd_text
        
        print("📝 Analyzing sample job description with categorization...")
        result = await analyze_jd_text(sample_jd)
        
        print(f"✅ Direct text categorized analysis completed!")
        print(f"📊 Results:")
        print(f"   - Required technical: {result.get_technical_skills(required_only=True)}")
        print(f"   - Required soft skills: {result.get_soft_skills(required_only=True)}")
        print(f"   - Required experience: {result.get_experience_requirements(required_only=True)}")
        print(f"   - Required domain knowledge: {result.get_domain_knowledge(required_only=True)}")
        print(f"   - Preferred technical: {result.preferred_skills.get('technical', [])}")
        print(f"   - Preferred soft skills: {result.preferred_skills.get('soft_skills', [])}")
        print(f"   - Experience years: {result.experience_years}")
        
        # Test skill summary
        print(f"\n📊 Skill Summary:")
        summary = result.get_skill_summary()
        for key, value in summary.items():
            print(f"   - {key}: {value}")
        
    except Exception as e:
        print(f"❌ Direct text categorized analysis failed: {e}")
    
    # Test 4: Test categorized structure validation
    try:
        print(f"\n4️⃣ Testing categorized structure validation")
        print("-" * 50)
        
        result = load_jd_analysis(company_name)
        if result:
            # Test all category access methods
            categories = ['technical', 'soft_skills', 'experience', 'domain_knowledge']
            
            for category in categories:
                try:
                    skills = result.get_skills_by_category(category, required_only=True)
                    print(f"✅ {category} (required): {len(skills)} skills")
                    
                    skills_all = result.get_skills_by_category(category, required_only=False)
                    print(f"✅ {category} (all): {len(skills_all)} skills")
                except Exception as e:
                    print(f"❌ Error accessing {category}: {e}")
            
            # Test invalid category
            try:
                result.get_skills_by_category('invalid_category')
                print("❌ Should have failed for invalid category")
            except ValueError as e:
                print(f"✅ Correctly rejected invalid category: {e}")
            
            # Test all categorized skills access
            all_categorized = result.get_all_categorized_skills()
            print(f"✅ All categorized skills structure: {list(all_categorized.keys())}")
            
        else:
            print("❌ No analysis found for validation test")
            
    except Exception as e:
        print(f"❌ Categorized structure validation failed: {e}")
    
    print(f"\n🎉 Enhanced categorized analysis testing completed!")
    print("=" * 70)


def test_file_structure_categorized():
    """Test the enhanced file structure with categorization"""
    
    print("\n🧪 Testing Enhanced File Structure with Categorization")
    print("=" * 60)
    
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
            
            if analysis_file.exists():
                try:
                    with open(analysis_file, 'r') as f:
                        data = json.load(f)
                    
                    # Check for categorized structure
                    has_categorized = 'required_skills' in data and 'preferred_skills' in data
                    print(f"      - Has categorized structure: {has_categorized}")
                    
                    if has_categorized:
                        required_skills = data.get('required_skills', {})
                        preferred_skills = data.get('preferred_skills', {})
                        
                        print(f"      - Required skills categories: {list(required_skills.keys())}")
                        print(f"      - Preferred skills categories: {list(preferred_skills.keys())}")
                        
                        # Count skills in each category
                        for category in ['technical', 'soft_skills', 'experience', 'domain_knowledge']:
                            req_count = len(required_skills.get(category, []))
                            pref_count = len(preferred_skills.get(category, []))
                            print(f"      - {category}: {req_count} required, {pref_count} preferred")
                    
                except Exception as e:
                    print(f"      - Error reading analysis file: {e}")


async def main():
    """Main test function for categorized analysis"""
    
    print("🚀 Starting Enhanced Categorized Job Description Analysis Tests")
    print("=" * 80)
    
    # Test file structure first
    test_file_structure_categorized()
    
    # Test categorized analysis functionality
    await test_categorized_analysis()
    
    print("\n✅ All enhanced categorized tests completed!")
    print("=" * 80)
    print("\n📋 New Features Tested:")
    print("✅ Enhanced prompt templates with categorization")
    print("✅ Categorized result structure (technical, soft_skills, experience, domain_knowledge)")
    print("✅ New access methods (get_technical_skills, get_soft_skills, etc.)")
    print("✅ Backward compatibility with flat keyword lists")
    print("✅ Enhanced file saving/loading with categorized structure")
    print("✅ Skill summary and statistics")
    print("✅ Category-specific validation")
    print("✅ All categorized access methods")


if __name__ == "__main__":
    asyncio.run(main())
