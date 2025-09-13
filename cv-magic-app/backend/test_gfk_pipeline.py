#!/usr/bin/env python3
"""
Test Complete Pipeline for GfK

This script tests the complete analysis pipeline for GfK company.
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, '/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend')

async def trigger_complete_pipeline(company: str = "GfK"):
    """Trigger the complete analysis pipeline via API"""
    
    print(f"\n🚀 Triggering complete pipeline for {company}...")
    print("=" * 60)
    
    # API endpoint
    url = f"http://localhost:8000/api/trigger-complete-pipeline/{company}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Pipeline triggered successfully!")
                    print(f"\nResults:")
                    print(json.dumps(result, indent=2))
                    
                    # Check if all steps succeeded
                    if result.get("overall_status") == "success":
                        print(f"\n🎉 All steps completed successfully!")
                        
                        # Now check the analysis file
                        await check_analysis_file(company)
                    else:
                        print(f"\n⚠️  Some steps failed. Check the results above.")
                else:
                    error = await response.text()
                    print(f"❌ API request failed with status {response.status}")
                    print(f"Error: {error}")
                    
    except Exception as e:
        print(f"❌ Failed to trigger pipeline: {e}")


async def check_analysis_file(company: str):
    """Check the analysis file for completeness"""
    
    print(f"\n📊 Checking analysis file for {company}...")
    print("-" * 60)
    
    file_path = Path(f"/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend/cv-analysis/{company}/{company}_skills_analysis.json")
    
    if not file_path.exists():
        print(f"❌ Analysis file not found: {file_path}")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check what's available
        checks = {
            "CV Skills": bool(data.get("cv_skills")),
            "JD Skills": bool(data.get("jd_skills")),
            "Preextracted Comparison": bool(data.get("preextracted_comparison_entries")),
            "Component Analysis": bool(data.get("component_analysis_entries")),
            "ATS Calculation": bool(data.get("ats_calculation_entries"))
        }
        
        print("Analysis Components:")
        for component, exists in checks.items():
            status = "✅" if exists else "❌"
            print(f"  {status} {component}")
        
        # Show latest ATS score if available
        ats_entries = data.get("ats_calculation_entries", [])
        if ats_entries:
            latest_ats = ats_entries[-1]
            print(f"\n🎯 Latest ATS Score: {latest_ats.get('final_ats_score', 'N/A')}/100")
            print(f"   Status: {latest_ats.get('category_status', 'N/A')}")
            print(f"   Timestamp: {latest_ats.get('timestamp', 'N/A')}")
        
        # Show component analysis scores if available
        component_entries = data.get("component_analysis_entries", [])
        if component_entries:
            latest_component = component_entries[-1]
            scores = latest_component.get("extracted_scores", {})
            if scores:
                print(f"\n📈 Component Analysis Scores:")
                main_scores = [
                    ("Skills Relevance", "skills_relevance"),
                    ("Experience Alignment", "experience_alignment"),
                    ("Industry Fit", "industry_fit"),
                    ("Role Seniority", "role_seniority"),
                    ("Technical Depth", "technical_depth")
                ]
                for name, key in main_scores:
                    if key in scores:
                        print(f"   {name}: {scores[key]:.1f}")
        
    except Exception as e:
        print(f"❌ Failed to read analysis file: {e}")


async def main():
    """Main function"""
    
    print("🧪 GfK Pipeline Test")
    print("=" * 60)
    
    # Check if GfK analysis already exists
    analysis_file = Path("/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend/cv-analysis/GfK/GfK_skills_analysis.json")
    
    if analysis_file.exists():
        print(f"✅ GfK analysis file exists: {analysis_file}")
        
        # Check current state
        await check_analysis_file("GfK")
        
        print("\n" + "=" * 60)
        response = input("\nDo you want to run the complete pipeline again? (y/n): ")
        
        if response.lower() != 'y':
            print("Exiting without running pipeline.")
            return
    else:
        print(f"⚠️  No existing analysis found for GfK")
    
    # Run the pipeline
    await trigger_complete_pipeline("GfK")


if __name__ == "__main__":
    asyncio.run(main())
