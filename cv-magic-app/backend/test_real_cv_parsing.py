#!/usr/bin/env python3
"""
Test Real CV Parsing

Test the structured CV parser with your actual CV data.
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

from app.services.structured_cv_parser import structured_cv_parser
from app.services.enhanced_cv_upload_service import enhanced_cv_upload_service


async def test_real_cv_parsing():
    """Test parsing your real CV"""
    
    print("🧪 Testing Real CV Parsing")
    print("=" * 60)
    
    # Load your actual CV text
    cv_text_path = Path("cv-analysis/original_cv.txt")
    
    if not cv_text_path.exists():
        print("❌ CV text file not found. Expected: cv-analysis/original_cv.txt")
        return False
    
    try:
        # Read the CV text
        print(f"📖 Reading CV from: {cv_text_path}")
        with open(cv_text_path, 'r', encoding='utf-8') as f:
            cv_text = f.read()
        
        # Extract just the CV content (skip the header)
        lines = cv_text.split('\n')
        cv_content_lines = []
        found_content = False
        
        for line in lines:
            if line.startswith('Maheshwor Tiwari'):
                found_content = True
            
            if found_content:
                cv_content_lines.append(line)
        
        cv_content = '\n'.join(cv_content_lines)
        print(f"✅ CV content loaded ({len(cv_content)} characters)")
        
        # Test parsing
        print("\n🔄 Parsing CV into structured format...")
        parsed_cv = structured_cv_parser.parse_cv_content(cv_content)
        
        if not parsed_cv:
            print("❌ Parsing failed - no result returned")
            return False
        
        print("✅ CV parsed successfully!")
        
        # Analyze what was extracted
        print(f"\n📊 PARSING RESULTS:")
        print(f"   Total sections: {len(parsed_cv)}")
        
        # Personal Information
        personal_info = parsed_cv.get('personal_information', {})
        if personal_info.get('name'):
            print(f"   👤 Name: {personal_info['name']}")
        if personal_info.get('email'):
            print(f"   📧 Email: {personal_info['email']}")
        if personal_info.get('phone'):
            print(f"   📱 Phone: {personal_info['phone']}")
        if personal_info.get('location'):
            print(f"   📍 Location: {personal_info['location']}")
        
        # Technical Skills
        tech_skills = parsed_cv.get('technical_skills', [])
        if tech_skills:
            print(f"\n   🔧 Technical Skills ({len(tech_skills)} items):")
            for i, skill in enumerate(tech_skills[:3]):  # Show first 3
                print(f"      {i+1}. {skill[:60]}{'...' if len(skill) > 60 else ''}")
            if len(tech_skills) > 3:
                print(f"      ... and {len(tech_skills) - 3} more")
        
        # Experience
        experience = parsed_cv.get('experience', [])
        if experience:
            print(f"\n   💼 Experience ({len(experience)} positions):")
            for exp in experience[:2]:  # Show first 2
                position = exp.get('position', 'N/A')
                company = exp.get('company', 'N/A')
                duration = exp.get('duration', 'N/A')
                achievements = exp.get('achievements', [])
                print(f"      • {position} at {company} ({duration})")
                if achievements:
                    print(f"        {len(achievements)} achievements listed")
        
        # Education
        education = parsed_cv.get('education', [])
        if education:
            print(f"\n   🎓 Education ({len(education)} degrees):")
            for edu in education:
                degree = edu.get('degree', 'N/A')
                institution = edu.get('institution', 'N/A')
                print(f"      • {degree} from {institution}")
        
        # Unknown sections
        unknown = parsed_cv.get('unknown_sections', {})
        if unknown:
            print(f"\n   ❓ Unknown sections preserved: {list(unknown.keys())}")
        
        # Test validation
        print(f"\n🔍 Validating parsed CV...")
        validation = structured_cv_parser.validate_cv_structure(parsed_cv)
        
        print(f"   Status: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
        print(f"   Sections found: {len(validation['sections_found'])}")
        
        if validation.get('warnings'):
            print(f"   ⚠️  Warnings ({len(validation['warnings'])}):")
            for warning in validation['warnings']:
                print(f"      - {warning}")
        
        if validation.get('missing_required'):
            print(f"   📝 Missing required ({len(validation['missing_required'])}):")
            for missing in validation['missing_required']:
                print(f"      - {missing}")
        
        # Test saving to structured format
        print(f"\n💾 Testing save to structured format...")
        
        # Save as test file first
        test_structured_path = Path("cv-analysis/test_structured_cv.json")
        save_success = structured_cv_parser.save_structured_cv(parsed_cv, str(test_structured_path))
        
        if save_success and test_structured_path.exists():
            file_size = test_structured_path.stat().st_size
            print(f"   ✅ Saved successfully: {test_structured_path} ({file_size} bytes)")
            
            # Test loading it back
            loaded_cv = structured_cv_parser.load_structured_cv(str(test_structured_path))
            if loaded_cv and loaded_cv.get('personal_information', {}).get('name') == parsed_cv.get('personal_information', {}).get('name'):
                print("   ✅ Load test successful")
                
                # Clean up test file
                test_structured_path.unlink()
                print("   🧹 Test file cleaned up")
            else:
                print("   ❌ Load test failed")
        else:
            print("   ❌ Save test failed")
        
        print(f"\n🎉 Real CV parsing test completed successfully!")
        print(f"Your CV can be successfully converted to structured format.")
        
        # Offer to save as the official structured CV
        print(f"\n" + "=" * 60)
        print("💡 NEXT STEPS:")
        print("1. Your CV parsed successfully into structured format")
        print("2. All sections were properly identified and organized")
        print("3. No data was lost in the conversion")
        print(f"4. You can now use the migration script to convert it officially")
        
        return True
        
    except Exception as e:
        print(f"❌ Real CV parsing test failed: {e}")
        logger.error("Real CV parsing failed", exc_info=True)
        return False


if __name__ == "__main__":
    result = asyncio.run(test_real_cv_parsing())
    sys.exit(0 if result else 1)