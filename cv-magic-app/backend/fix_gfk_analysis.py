#!/usr/bin/env python3
"""
Fix GfK Analysis - Parse CV skills from comprehensive analysis and complete pipeline
"""

import json
import re
import asyncio
import aiohttp
from pathlib import Path


def extract_skills_from_text(text):
    """Extract skills from the comprehensive analysis text"""
    skills = {
        "technical_skills": [],
        "soft_skills": [],
        "domain_keywords": []
    }
    
    # Extract sections
    sections = text.split("**")
    
    current_section = None
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        if "SOFT SKILLS:" in section:
            current_section = "soft"
            continue
        elif "TECHNICAL SKILLS:" in section:
            current_section = "technical"
            continue
        elif "DOMAIN KEYWORDS:" in section:
            current_section = "domain"
            continue
            
        # Extract skills from section
        if current_section and section.startswith("-"):
            skill = section.strip("- ").strip()
            if current_section == "soft":
                skills["soft_skills"].append(skill)
            elif current_section == "technical":
                skills["technical_skills"].append(skill)
            elif current_section == "domain":
                skills["domain_keywords"].append(skill)
    
    return skills


def fix_cv_skills():
    """Fix the CV skills in the analysis file"""
    
    print("🔧 Fixing CV skills in GfK analysis file...")
    
    file_path = Path("/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend/cv-analysis/GfK/GfK_skills_analysis.json")
    
    # Read the file
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Extract skills from comprehensive analysis
    cv_analysis = data.get("cv_comprehensive_analysis", "")
    cv_skills = extract_skills_from_text(cv_analysis)
    
    print(f"✅ Extracted CV skills:")
    print(f"   - Technical: {len(cv_skills['technical_skills'])} skills")
    print(f"   - Soft: {len(cv_skills['soft_skills'])} skills")
    print(f"   - Domain: {len(cv_skills['domain_keywords'])} keywords")
    
    # Update the cv_skills in the data
    data["cv_skills"]["technical_skills"] = cv_skills["technical_skills"]
    data["cv_skills"]["soft_skills"] = cv_skills["soft_skills"]
    data["cv_skills"]["domain_keywords"] = cv_skills["domain_keywords"]
    
    # Save back to file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("✅ CV skills updated successfully!")
    return True


async def run_preextracted_comparison():
    """Run the preextracted comparison via direct API call"""
    
    print("\n🔄 Running preextracted comparison...")
    
    # Read the skills
    file_path = Path("/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend/cv-analysis/GfK/GfK_skills_analysis.json")
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    cv_skills = data["cv_skills"]
    jd_skills = data["jd_skills"]
    
    # Get auth token
    async with aiohttp.ClientSession() as session:
        # Quick login
        login_resp = await session.post("http://localhost:8000/api/quick-login")
        auth_data = await login_resp.json()
        token = auth_data['access_token']
        
        # Headers
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Prepare data for comparison
        comparison_data = {
            "cv_skills": cv_skills,
            "jd_skills": jd_skills,
            "company_name": "GfK"
        }
        
        # Run preextracted comparison
        try:
            # Import and run directly
            import sys
            sys.path.insert(0, '/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend')
            
            from app.ai.ai_service import ai_service
            from app.services.skill_extraction.preextracted_comparator import execute_skills_semantic_comparison
            from app.services.skill_extraction.result_saver import result_saver
            
            # Run comparison
            result = await execute_skills_semantic_comparison(
                ai_service,
                cv_skills=cv_skills,
                jd_skills=jd_skills
            )
            
            # Save result
            result_saver.append_preextracted_comparison(
                result,
                "GfK",
                "cv-analysis/GfK/GfK_skills_analysis.json"
            )
            
            print("✅ Preextracted comparison completed!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to run comparison: {e}")
            return False


async def trigger_component_analysis():
    """Trigger component analysis for GfK"""
    
    print("\n🚀 Triggering component analysis...")
    
    async with aiohttp.ClientSession() as session:
        response = await session.post("http://localhost:8000/api/trigger-component-analysis/GfK")
        if response.status == 200:
            result = await response.json()
            print("✅ Component analysis triggered successfully!")
            if "extracted_scores" in result:
                print(f"   - Scores extracted: {result['total_scores']} scores")
            return True
        else:
            error = await response.text()
            print(f"❌ Failed to trigger component analysis: {error}")
            return False


async def check_final_results():
    """Check the final analysis results"""
    
    print("\n📊 Checking final results...")
    
    async with aiohttp.ClientSession() as session:
        response = await session.get("http://localhost:8000/api/analysis-results/GfK")
        if response.status == 200:
            data = await response.json()
            result = data['data']
            
            # Check what we have
            print("\n✅ Analysis Components:")
            print(f"   - CV Skills: {'✅' if result['skills_analysis']['cv_skills'].get('technical_skills') else '❌'}")
            print(f"   - JD Skills: {'✅' if result['skills_analysis']['jd_skills'].get('technical_skills') else '❌'}")
            print(f"   - Preextracted Comparison: {'✅' if result['preextracted_comparison'] else '❌'}")
            print(f"   - Component Analysis: {'✅' if result['component_analysis'] else '❌'}")
            print(f"   - ATS Score: {'✅' if result['ats_score'] else '❌'}")
            
            if result['ats_score']:
                ats = result['ats_score']
                print(f"\n🎯 Final ATS Score: {ats['final_ats_score']}/100")
                print(f"   Status: {ats['category_status']}")
                
            if result['preextracted_comparison']:
                rates = result['preextracted_comparison']['match_rates']
                print(f"\n📈 Match Rates:")
                print(f"   - Technical: {rates['technical_skills']}%")
                print(f"   - Soft Skills: {rates['soft_skills']}%")
                print(f"   - Domain: {rates['domain_keywords']}%")


async def main():
    """Main function to fix and complete the analysis"""
    
    print("🔧 GfK Analysis Fix Script")
    print("=" * 60)
    
    # Step 1: Fix CV skills
    if not fix_cv_skills():
        print("❌ Failed to fix CV skills")
        return
    
    # Step 2: Run preextracted comparison
    await run_preextracted_comparison()
    
    # Wait a bit
    print("\n⏳ Waiting 2 seconds...")
    await asyncio.sleep(2)
    
    # Step 3: Trigger component analysis
    await trigger_component_analysis()
    
    # Wait for completion
    print("\n⏳ Waiting 5 seconds for analysis to complete...")
    await asyncio.sleep(5)
    
    # Step 4: Check results
    await check_final_results()
    
    print("\n✅ Fix complete! The analysis should now be available in the frontend.")


if __name__ == "__main__":
    asyncio.run(main())
