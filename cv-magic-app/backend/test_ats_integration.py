#!/usr/bin/env python3
"""
Test ATS Integration with GfK Analysis File
Tests that ATS results are properly saved to the existing analysis file
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.ats.enhanced_ats_orchestrator import EnhancedATSOrchestrator

async def test_ats_integration():
    """Test ATS integration with GfK analysis file"""
    
    print("🧪 Testing ATS Integration with GfK Analysis File...")
    
    # Initialize orchestrator
    orchestrator = EnhancedATSOrchestrator()
    
    # Test with GfK company
    company_name = "GfK"
    
    try:
        print(f"📊 Running ATS analysis for {company_name}...")
        
        # Run the enhanced analysis
        ats_result = await orchestrator.run_enhanced_analysis(company_name)
        
        if "error" in ats_result:
            print(f"❌ ATS analysis failed: {ats_result['error']}")
            return False
        
        print("✅ ATS analysis completed successfully!")
        
        # Check if the analysis file was updated
        base_dir = Path("/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend/cv-analysis")
        analysis_file = base_dir / company_name / f"{company_name}_skills_analysis.json"
        
        if not analysis_file.exists():
            print(f"❌ Analysis file not found: {analysis_file}")
            return False
        
        # Read the updated analysis file
        with open(analysis_file, 'r') as f:
            updated_analysis = json.load(f)
        
        # Check if ATS analysis was added
        if 'ats_analysis' not in updated_analysis:
            print("❌ ATS analysis not found in the updated file")
            return False
        
        ats_analysis = updated_analysis['ats_analysis']
        
        print("✅ ATS analysis found in the updated file!")
        print(f"📈 Final ATS Score: {ats_analysis.get('final_ats_score', 'N/A')}/100")
        print(f"📊 Category Status: {ats_analysis.get('category_status', 'N/A')}")
        print(f"💡 Recommendation: {ats_analysis.get('recommendation', 'N/A')}")
        print(f"🔧 Technical Skills Match Rate: {ats_analysis.get('technical_skills_match_rate', 'N/A')}%")
        print(f"🎯 Soft Skills Match Rate: {ats_analysis.get('soft_skills_match_rate', 'N/A')}%")
        print(f"🏷️ Domain Keywords Match Rate: {ats_analysis.get('domain_keywords_match_rate', 'N/A')}%")
        print(f"⭐ Category 1 Score: {ats_analysis.get('cat1_score', 'N/A')}")
        print(f"⭐ Category 2 Score: {ats_analysis.get('cat2_score', 'N/A')}")
        print(f"🎁 Bonus Points: {ats_analysis.get('bonus_points', 'N/A')}")
        
        print(f"\n💪 Key Strengths:")
        for strength in ats_analysis.get('key_strengths', []):
            print(f"  • {strength}")
        
        print(f"\n⚠️ Critical Gaps:")
        for gap in ats_analysis.get('critical_gaps', []):
            print(f"  • {gap}")
        
        print(f"\n💡 Recommendations:")
        for rec in ats_analysis.get('improvement_recommendations', []):
            print(f"  • {rec}")
        
        print(f"\n📊 Overall Assessment: {ats_analysis.get('overall_assessment', 'N/A')}")
        print(f"⏱️ Processing Time: {ats_analysis.get('processing_time_ms', 'N/A')}ms")
        print(f"🎯 Confidence Score: {ats_analysis.get('confidence_score', 'N/A')}")
        
        # Save a copy of the updated analysis for verification
        test_output_path = backend_dir / "test_gfk_analysis_with_ats.json"
        with open(test_output_path, 'w') as f:
            json.dump(updated_analysis, f, indent=2, default=str)
        
        print(f"\n💾 Updated analysis saved to: {test_output_path}")
        print("✅ ATS integration test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ ATS integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_ats_integration()
    if success:
        print("\n🎉 ATS integration test passed!")
        sys.exit(0)
    else:
        print("\n💥 ATS integration test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
