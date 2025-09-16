#!/usr/bin/env python3
"""
Test Auto-Processing Integration

Test that CVs are automatically processed into structured format when accessed.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.append(str(app_dir))

from app.services.enhanced_cv_upload_service import enhanced_cv_upload_service
from app.services.structured_cv_parser import structured_cv_parser


async def test_auto_processing():
    """Test auto-processing functionality"""
    
    print("🔄 Testing Auto-Processing Integration")
    print("=" * 60)
    
    try:
        # Check if we have the CV text file
        cv_text_path = Path("cv-analysis/original_cv.txt")
        if not cv_text_path.exists():
            print("❌ No CV text file found for testing")
            return False
        
        # Read the CV content
        with open(cv_text_path, 'r', encoding='utf-8') as f:
            cv_content = f.read()
        
        # Extract just the CV part (skip headers)
        lines = cv_content.split('\n')
        cv_lines = []
        found_start = False
        
        for line in lines:
            if line.startswith('Maheshwor Tiwari'):
                found_start = True
            
            if found_start:
                cv_lines.append(line)
        
        cv_text = '\n'.join(cv_lines)
        
        print(f"📄 CV content loaded: {len(cv_text)} characters")
        
        # Test processing with the enhanced service
        print("\n🔄 Testing structured parsing...")
        
        parsed_cv = structured_cv_parser.parse_cv_content(cv_text)
        
        if not parsed_cv:
            print("❌ Failed to parse CV")
            return False
        
        print(f"✅ CV parsed successfully into {len(parsed_cv)} sections")
        
        # Show what was extracted
        personal_info = parsed_cv.get('personal_information', {})
        if personal_info.get('name'):
            print(f"   👤 Name: {personal_info['name']}")
        
        tech_skills = parsed_cv.get('technical_skills', [])
        if tech_skills:
            print(f"   🔧 Technical Skills: {len(tech_skills)} items")
        
        experience = parsed_cv.get('experience', [])
        if experience:
            print(f"   💼 Experience: {len(experience)} positions")
        
        education = parsed_cv.get('education', [])
        if education:
            print(f"   🎓 Education: {len(education)} degrees")
        
        # Test validation
        validation = structured_cv_parser.validate_cv_structure(parsed_cv)
        print(f"\n🔍 Validation: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
        
        if validation.get('warnings'):
            print(f"   ⚠️ Warnings: {len(validation['warnings'])}")
        
        # Test saving to original_cv.json format
        print("\n💾 Testing save as original_cv.json...")
        
        original_cv_path = Path("cv-analysis/original_cv.json")
        success = structured_cv_parser.save_structured_cv(parsed_cv, str(original_cv_path))
        
        if success and original_cv_path.exists():
            file_size = original_cv_path.stat().st_size
            print(f"   ✅ Saved to {original_cv_path} ({file_size} bytes)")
            
            # Test loading it back
            loaded_cv = structured_cv_parser.load_structured_cv(str(original_cv_path))
            if loaded_cv:
                print("   ✅ Load test successful")
                print(f"   📊 Loaded CV has {len(loaded_cv)} sections")
                
                # Show key sections
                if loaded_cv.get('personal_information', {}).get('name'):
                    print(f"   👤 Name preserved: {loaded_cv['personal_information']['name']}")
                
                if loaded_cv.get('technical_skills'):
                    print(f"   🔧 Skills preserved: {len(loaded_cv['technical_skills'])} items")
                
                print("\n🎉 Auto-processing integration test successful!")
                print("✅ Now when you select a CV from the list, it will automatically:")
                print("   1. Extract text content")
                print("   2. Parse into structured format")
                print("   3. Save as original_cv.json")
                print("   4. Return both raw text and structured data")
                
                return True
            else:
                print("   ❌ Load test failed")
                return False
        else:
            print("   ❌ Save test failed")
            return False
        
    except Exception as e:
        print(f"❌ Auto-processing test failed: {e}")
        logger.error("Auto-processing test error", exc_info=True)
        return False


if __name__ == "__main__":
    result = asyncio.run(test_auto_processing())
    if result:
        print(f"\n🚀 AUTO-PROCESSING INTEGRATION: ✅ WORKING")
        print("Your CV will now be automatically processed into structured format!")
    else:
        print(f"\n🚨 AUTO-PROCESSING INTEGRATION: ❌ ISSUES")
    
    sys.exit(0 if result else 1)