#!/usr/bin/env python3
"""
Test Comprehensive Analysis Fix
Tests that comprehensive analysis is now being saved to the analysis file
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.routes.skills_analysis import perform_preliminary_skills_analysis

async def test_comprehensive_analysis_fix():
    """Test that comprehensive analysis is now being saved"""
    
    print("🧪 Testing Comprehensive Analysis Fix...")
    print("=" * 60)
    
    try:
        # Read CV content
        cv_file = backend_dir / "cv-analysis" / "original_cv.txt"
        if not cv_file.exists():
            print(f"❌ CV file not found: {cv_file}")
            return False
        
        with open(cv_file, 'r') as f:
            cv_content = f.read()
        
        # Sample job description
        jd_text = """
        Senior Data Analyst - International Aid Organization
        
        We are seeking a Senior Data Analyst to join our team and help drive data-driven decisions 
        in international aid and development.
        
        REQUIREMENTS:
        - 3-5 years of experience in data analysis
        - Strong Python programming skills
        - SQL database experience
        - Experience with data visualization tools (Tableau, Power BI)
        - Excellent communication skills
        - Leadership experience preferred
        - Experience in non-profit or international development preferred
        
        RESPONSIBILITIES:
        - Analyze donor data and fundraising metrics
        - Create data mining strategies for profile analysis
        - Develop segmentation strategies for donor engagement
        - Lead data analysis projects
        - Present findings to executive stakeholders
        - Manage junior analysts
        """
        
        print("📊 Running preliminary skills analysis...")
        
        # Run the analysis
        result = await perform_preliminary_skills_analysis(
            cv_content=cv_content,
            jd_text=jd_text,
            cv_filename="test_cv.txt",
            current_model="claude-3-5-sonnet-20240620",
            config_name=None,
            user_id=1
        )
        
        print("✅ Analysis completed!")
        
        # Check if comprehensive analysis is in the result
        if 'cv_comprehensive_analysis' in result and result['cv_comprehensive_analysis']:
            print("✅ CV comprehensive analysis found in result!")
            print(f"   Length: {len(result['cv_comprehensive_analysis'])} characters")
        else:
            print("❌ CV comprehensive analysis missing from result")
        
        if 'jd_comprehensive_analysis' in result and result['jd_comprehensive_analysis']:
            print("✅ JD comprehensive analysis found in result!")
            print(f"   Length: {len(result['jd_comprehensive_analysis'])} characters")
        else:
            print("❌ JD comprehensive analysis missing from result")
        
        # Check if the analysis was saved to file
        print("\n📁 Checking if analysis was saved to file...")
        
        # Look for the most recent analysis file
        cv_analysis_dir = backend_dir / "cv-analysis"
        if cv_analysis_dir.exists():
            company_dirs = [d for d in cv_analysis_dir.iterdir() if d.is_dir()]
            if company_dirs:
                # Get the most recent company directory
                latest_company_dir = max(company_dirs, key=lambda d: d.stat().st_mtime)
                analysis_file = latest_company_dir / f"{latest_company_dir.name}_skills_analysis.json"
                
                if analysis_file.exists():
                    print(f"✅ Found analysis file: {analysis_file}")
                    
                    # Read and check the file
                    with open(analysis_file, 'r') as f:
                        saved_analysis = json.load(f)
                    
                    if 'cv_comprehensive_analysis' in saved_analysis and saved_analysis['cv_comprehensive_analysis']:
                        print("✅ CV comprehensive analysis found in saved file!")
                        print(f"   Length: {len(saved_analysis['cv_comprehensive_analysis'])} characters")
                    else:
                        print("❌ CV comprehensive analysis missing from saved file")
                    
                    if 'jd_comprehensive_analysis' in saved_analysis and saved_analysis['jd_comprehensive_analysis']:
                        print("✅ JD comprehensive analysis found in saved file!")
                        print(f"   Length: {len(saved_analysis['jd_comprehensive_analysis'])} characters")
                    else:
                        print("❌ JD comprehensive analysis missing from saved file")
                    
                    # Save a sample for verification
                    sample_output_path = backend_dir / "test_comprehensive_analysis_sample.json"
                    with open(sample_output_path, 'w') as f:
                        json.dump({
                            "cv_comprehensive_analysis": saved_analysis.get('cv_comprehensive_analysis', ''),
                            "jd_comprehensive_analysis": saved_analysis.get('jd_comprehensive_analysis', ''),
                            "cv_skills_count": len(saved_analysis.get('cv_skills', {}).get('technical_skills', [])),
                            "jd_skills_count": len(saved_analysis.get('jd_skills', {}).get('technical_skills', []))
                        }, f, indent=2)
                    
                    print(f"💾 Sample saved to: {sample_output_path}")
                    
                else:
                    print(f"❌ Analysis file not found: {analysis_file}")
            else:
                print("❌ No company directories found")
        else:
            print("❌ CV analysis directory not found")
        
        print("\n🎉 Comprehensive analysis fix test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_comprehensive_analysis_fix()
    if success:
        print("\n🎉 Test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
