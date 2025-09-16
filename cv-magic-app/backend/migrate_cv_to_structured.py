#!/usr/bin/env python3
"""
CV Migration Script

This script migrates your existing original_cv.json from the old format 
to the new structured format, with backup and validation.
"""

import asyncio
import json
import logging
from pathlib import Path
import sys

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.append(str(app_dir))

from app.services.enhanced_cv_upload_service import enhanced_cv_upload_service
from app.services.structured_cv_parser import structured_cv_parser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main migration function"""
    
    print("🔄 CV Migration Script - Converting to Structured Format")
    print("=" * 60)
    
    # Define paths
    current_cv_path = Path("cv-analysis/original_cv.json")
    backup_path = Path("cv-analysis/original_cv.backup.json")
    
    if not current_cv_path.exists():
        print(f"❌ Current CV file not found: {current_cv_path}")
        print("Please ensure original_cv.json exists in cv-analysis directory")
        return
    
    try:
        # Step 1: Load and inspect current CV
        print(f"📖 Loading current CV from: {current_cv_path}")
        with open(current_cv_path, 'r', encoding='utf-8') as f:
            current_data = json.load(f)
        
        print(f"✅ Current CV loaded ({len(str(current_data))} characters)")
        
        # Check if already in structured format
        if isinstance(current_data, dict) and "personal_information" in current_data:
            print("ℹ️  CV appears to already be in structured format")
            
            # Validate current structure
            validation_report = structured_cv_parser.validate_cv_structure(current_data)
            print(f"📊 Validation: {'✅ Valid' if validation_report['valid'] else '❌ Invalid'}")
            
            if validation_report.get("warnings"):
                print("⚠️  Warnings found:")
                for warning in validation_report["warnings"]:
                    print(f"   - {warning}")
            
            if validation_report.get("missing_required"):
                print("📝 Missing required sections:")
                for missing in validation_report["missing_required"]:
                    print(f"   - {missing}")
            
            choice = input("\n🤔 CV is already structured. Re-process anyway? (y/N): ")
            if choice.lower() not in ['y', 'yes']:
                print("✋ Migration cancelled by user")
                return
        
        # Step 2: Create backup
        print(f"💾 Creating backup: {backup_path}")
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(current_data, f, indent=2, ensure_ascii=False)
        print("✅ Backup created successfully")
        
        # Step 3: Migrate to structured format
        print("🔄 Converting to structured format...")
        
        result = enhanced_cv_upload_service.migrate_existing_cv(
            source_path=str(current_cv_path),
            backup=False  # We already created backup
        )
        
        if not result["success"]:
            print(f"❌ Migration failed: {result.get('error', 'Unknown error')}")
            return
        
        print("✅ Migration completed successfully!")
        
        # Step 4: Validate migrated CV
        print("🔍 Validating migrated CV...")
        
        migrated_cv = enhanced_cv_upload_service.load_structured_cv(use_original=True)
        if not migrated_cv:
            print("❌ Could not load migrated CV for validation")
            return
        
        validation_report = result["validation_report"]
        print(f"📊 Validation: {'✅ Valid' if validation_report['valid'] else '❌ Invalid'}")
        
        # Step 5: Show migration summary
        print("\n" + "=" * 60)
        print("📈 MIGRATION SUMMARY")
        print("=" * 60)
        
        print(f"✅ Source: {current_cv_path}")
        print(f"💾 Backup: {backup_path}")
        print(f"📁 Sections found: {len(result['sections_found'])}")
        
        for section in result["sections_found"]:
            section_data = migrated_cv.get(section, {})
            if section_data:
                if isinstance(section_data, list):
                    print(f"   📋 {section}: {len(section_data)} items")
                elif isinstance(section_data, dict):
                    if section == "personal_information":
                        name = section_data.get("name", "Not provided")
                        print(f"   👤 {section}: {name}")
                    else:
                        non_empty_fields = sum(1 for v in section_data.values() if v)
                        print(f"   📝 {section}: {non_empty_fields} fields")
                else:
                    print(f"   📄 {section}: {type(section_data).__name__}")
        
        if result.get("unknown_sections"):
            print(f"❓ Unknown sections: {', '.join(result['unknown_sections'])}")
        
        if validation_report.get("warnings"):
            print(f"⚠️  Warnings: {len(validation_report['warnings'])}")
            for warning in validation_report["warnings"]:
                print(f"   - {warning}")
        
        if validation_report.get("missing_required"):
            print(f"📝 Missing required: {len(validation_report['missing_required'])}")
            for missing in validation_report["missing_required"]:
                print(f"   - {missing}")
        
        # Step 6: Show file comparison
        original_size = current_cv_path.stat().st_size
        new_size = current_cv_path.stat().st_size
        
        print(f"\n💾 File size: {original_size} bytes → {new_size} bytes")
        
        print("\n🎉 Migration completed successfully!")
        print("Your CV is now in the structured format and ready for enhanced processing.")
        
        # Step 7: Offer to test the new format
        test_choice = input("\n🧪 Test the new structured format? (Y/n): ")
        if test_choice.lower() not in ['n', 'no']:
            await test_structured_format(migrated_cv)
        
    except Exception as e:
        print(f"❌ Migration error: {str(e)}")
        logger.error(f"Migration failed: {str(e)}", exc_info=True)
        
        # Restore from backup if available
        if backup_path.exists():
            print("🔄 Attempting to restore from backup...")
            try:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                
                with open(current_cv_path, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False)
                
                print("✅ Restored from backup successfully")
            except Exception as restore_error:
                print(f"❌ Backup restore failed: {str(restore_error)}")


async def test_structured_format(cv_data):
    """Test the structured format functionality"""
    print("\n" + "=" * 60)
    print("🧪 TESTING STRUCTURED FORMAT")
    print("=" * 60)
    
    # Test section access
    print("📋 Testing section access...")
    
    sections_to_test = ["personal_information", "technical_skills", "experience", "education"]
    
    for section in sections_to_test:
        if section in cv_data and cv_data[section]:
            data = cv_data[section]
            if isinstance(data, list):
                print(f"   ✅ {section}: {len(data)} items")
                if data and isinstance(data[0], dict):
                    print(f"      Sample keys: {list(data[0].keys())}")
            elif isinstance(data, dict):
                print(f"   ✅ {section}: {len(data)} fields")
                if section == "personal_information":
                    print(f"      Name: {data.get('name', 'Not provided')}")
                    print(f"      Email: {data.get('email', 'Not provided')}")
            else:
                print(f"   ✅ {section}: {type(data).__name__}")
        else:
            print(f"   ⚠️  {section}: Not found or empty")
    
    # Test skill extraction
    if cv_data.get("technical_skills"):
        skills = cv_data["technical_skills"]
        print(f"\n🔧 Technical Skills ({len(skills)} items):")
        for i, skill in enumerate(skills[:3]):  # Show first 3
            print(f"   {i+1}. {skill[:80]}{'...' if len(skill) > 80 else ''}")
        if len(skills) > 3:
            print(f"   ... and {len(skills) - 3} more")
    
    # Test experience extraction
    if cv_data.get("experience"):
        experiences = cv_data["experience"]
        print(f"\n💼 Experience ({len(experiences)} positions):")
        for exp in experiences[:2]:  # Show first 2
            position = exp.get("position", "Unknown Position")
            company = exp.get("company", "Unknown Company")
            duration = exp.get("duration", "Unknown Duration")
            print(f"   • {position} at {company} ({duration})")
            achievements = exp.get("achievements", [])
            if achievements:
                print(f"     {len(achievements)} achievements listed")
    
    print("\n✅ Structured format test completed!")


if __name__ == "__main__":
    print("Starting CV migration...")
    asyncio.run(main())