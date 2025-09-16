#!/usr/bin/env python3
"""
Comprehensive Test Script for Structured CV Integration

This script tests all components of the structured CV system to ensure
everything is working correctly.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress some verbose logs for cleaner test output
logging.getLogger('app.services.structured_cv_parser').setLevel(logging.WARNING)

# Add app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.append(str(app_dir))

try:
    from app.services.structured_cv_parser import structured_cv_parser
    from app.services.enhanced_cv_upload_service import enhanced_cv_upload_service
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running this from the backend directory")
    sys.exit(1)


class StructuredCVTester:
    """Test suite for structured CV integration"""
    
    def __init__(self):
        self.test_results = []
        self.test_cv_data = self._create_test_cv_data()
    
    def _create_test_cv_data(self) -> Dict[str, Any]:
        """Create test CV data covering all scenarios"""
        return {
            "personal_information": {
                "name": "Test User",
                "phone": "123-456-7890", 
                "email": "test@example.com",
                "location": "Test City, TC",
                "linkedin": "linkedin.com/in/testuser",
                "portfolio_links": {
                    "github": "github.com/testuser",
                    "website": "testuser.com"
                }
            },
            "career_profile": {
                "summary": "Experienced data scientist with 5+ years in machine learning and analytics."
            },
            "technical_skills": [
                "Python programming with 5+ years experience",
                "Machine learning using scikit-learn and TensorFlow",
                "SQL database management and optimization"
            ],
            "education": [
                {
                    "degree": "Master of Data Science",
                    "institution": "Test University",
                    "location": "Test City, TC",
                    "duration": "2020-2022"
                }
            ],
            "experience": [
                {
                    "position": "Senior Data Analyst",
                    "company": "Test Corp",
                    "location": "Test City, TC",
                    "duration": "2022-Present",
                    "achievements": [
                        "Improved data pipeline efficiency by 40%",
                        "Led team of 5 data scientists"
                    ]
                }
            ],
            "soft_skills": [
                "Leadership",
                "Communication",
                "Problem-solving"
            ],
            "unknown_custom_section": {
                "custom_field": "This should be preserved",
                "another_field": ["item1", "item2"]
            }
        }
    
    async def run_all_tests(self) -> bool:
        """Run all integration tests"""
        print("🧪 Starting Structured CV Integration Tests")
        print("=" * 60)
        
        test_methods = [
            self.test_parser_initialization,
            self.test_structured_data_parsing,
            self.test_raw_text_parsing,
            self.test_missing_data_handling,
            self.test_unknown_sections,
            self.test_validation_system,
            self.test_file_operations,
            self.test_upload_service_init,
            self.test_cv_loading,
            self.test_error_handling
        ]
        
        passed = 0
        total = len(test_methods)
        
        for test_method in test_methods:
            try:
                result = await test_method()
                if result:
                    passed += 1
                    print(f"✅ {test_method.__name__}")
                else:
                    print(f"❌ {test_method.__name__}")
                    
            except Exception as e:
                print(f"💥 {test_method.__name__} - EXCEPTION: {str(e)}")
                logger.error(f"Test {test_method.__name__} failed with exception", exc_info=True)
        
        print("\n" + "=" * 60)
        print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Integration is working correctly.")
            await self.run_integration_demo()
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. Please check the logs above.")
            return False
    
    async def test_parser_initialization(self) -> bool:
        """Test that the structured CV parser initializes correctly"""
        try:
            # Test parser has required methods
            required_methods = [
                'parse_cv_content', 'validate_cv_structure', 
                'save_structured_cv', 'load_structured_cv'
            ]
            
            for method in required_methods:
                if not hasattr(structured_cv_parser, method):
                    print(f"   Missing method: {method}")
                    return False
            
            # Test default structure
            default_structure = structured_cv_parser._get_default_structure()
            required_sections = [
                'personal_information', 'technical_skills', 'experience'
            ]
            
            for section in required_sections:
                if section not in default_structure:
                    print(f"   Missing default section: {section}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"   Parser initialization failed: {e}")
            return False
    
    async def test_structured_data_parsing(self) -> bool:
        """Test parsing of already structured data"""
        try:
            result = structured_cv_parser.parse_cv_content(self.test_cv_data)
            
            # Check basic structure
            if not isinstance(result, dict):
                print("   Result is not a dictionary")
                return False
            
            # Check required fields exist
            if 'personal_information' not in result:
                print("   Missing personal_information")
                return False
            
            if result['personal_information']['name'] != "Test User":
                print("   Name not parsed correctly")
                return False
            
            # Check technical skills
            if not result.get('technical_skills'):
                print("   Technical skills not parsed")
                return False
            
            if len(result['technical_skills']) != 3:
                print(f"   Expected 3 technical skills, got {len(result['technical_skills'])}")
                return False
            
            return True
            
        except Exception as e:
            print(f"   Structured data parsing failed: {e}")
            return False
    
    async def test_raw_text_parsing(self) -> bool:
        """Test parsing of raw text CV"""
        try:
            raw_text = """
            John Doe
            john.doe@email.com
            123-456-7890
            
            TECHNICAL SKILLS
            • Python programming
            • Data analysis
            • Machine learning
            
            EXPERIENCE
            Software Engineer at Tech Corp
            """
            
            result = structured_cv_parser.parse_cv_content(raw_text)
            
            # Should not crash and should return structured format
            if not isinstance(result, dict):
                print("   Raw text parsing didn't return dict")
                return False
            
            # Should have basic structure even from raw text
            required_keys = ['personal_information', 'technical_skills', 'saved_at']
            for key in required_keys:
                if key not in result:
                    print(f"   Missing key in raw text result: {key}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"   Raw text parsing failed: {e}")
            return False
    
    async def test_missing_data_handling(self) -> bool:
        """Test handling of missing or incomplete data"""
        try:
            # Test with minimal data
            minimal_data = {
                "personal_information": {
                    "name": "Minimal User"
                }
            }
            
            result = structured_cv_parser.parse_cv_content(minimal_data)
            
            # Should fill in missing fields with empty values
            personal_info = result.get('personal_information', {})
            
            # Should have empty values, not missing keys
            expected_fields = ['name', 'phone', 'email', 'location']
            for field in expected_fields:
                if field not in personal_info:
                    print(f"   Missing field not handled: {field}")
                    return False
            
            # Name should be preserved, others should be empty
            if personal_info['name'] != "Minimal User":
                print("   Name not preserved in minimal data")
                return False
            
            if personal_info['phone'] != "":
                print("   Empty phone not handled correctly")
                return False
            
            return True
            
        except Exception as e:
            print(f"   Missing data handling failed: {e}")
            return False
    
    async def test_unknown_sections(self) -> bool:
        """Test preservation of unknown sections"""
        try:
            result = structured_cv_parser.parse_cv_content(self.test_cv_data)
            
            # Check if unknown section is preserved
            unknown_sections = result.get('unknown_sections', {})
            
            if 'unknown_custom_section' not in unknown_sections:
                print("   Unknown section not preserved")
                return False
            
            preserved_section = unknown_sections['unknown_custom_section']
            if preserved_section['custom_field'] != "This should be preserved":
                print("   Unknown section content not preserved correctly")
                return False
            
            return True
            
        except Exception as e:
            print(f"   Unknown sections test failed: {e}")
            return False
    
    async def test_validation_system(self) -> bool:
        """Test CV structure validation"""
        try:
            # Test valid CV
            valid_result = structured_cv_parser.parse_cv_content(self.test_cv_data)
            validation = structured_cv_parser.validate_cv_structure(valid_result)
            
            if not isinstance(validation, dict):
                print("   Validation didn't return dict")
                return False
            
            required_keys = ['valid', 'errors', 'warnings', 'sections_found']
            for key in required_keys:
                if key not in validation:
                    print(f"   Missing validation key: {key}")
                    return False
            
            # Test invalid CV
            invalid_cv = {}  # Completely empty
            invalid_validation = structured_cv_parser.validate_cv_structure(invalid_cv)
            
            if invalid_validation['valid']:
                print("   Empty CV incorrectly validated as valid")
                return False
            
            return True
            
        except Exception as e:
            print(f"   Validation system test failed: {e}")
            return False
    
    async def test_file_operations(self) -> bool:
        """Test saving and loading CV files"""
        try:
            # Create test directory
            test_dir = Path("test_cv_files")
            test_dir.mkdir(exist_ok=True)
            
            test_file = test_dir / "test_cv.json"
            
            # Test saving
            structured_cv = structured_cv_parser.parse_cv_content(self.test_cv_data)
            save_result = structured_cv_parser.save_structured_cv(structured_cv, str(test_file))
            
            if not save_result:
                print("   Failed to save CV")
                return False
            
            if not test_file.exists():
                print("   CV file was not created")
                return False
            
            # Test loading
            loaded_cv = structured_cv_parser.load_structured_cv(str(test_file))
            
            if not loaded_cv:
                print("   Failed to load CV")
                return False
            
            if loaded_cv['personal_information']['name'] != "Test User":
                print("   Loaded CV has incorrect data")
                return False
            
            # Cleanup
            test_file.unlink()
            test_dir.rmdir()
            
            return True
            
        except Exception as e:
            print(f"   File operations test failed: {e}")
            return False
    
    async def test_upload_service_init(self) -> bool:
        """Test enhanced upload service initialization"""
        try:
            # Test service has required methods
            required_methods = [
                'load_structured_cv', 'get_cv_processing_status', 
                'migrate_existing_cv'
            ]
            
            for method in required_methods:
                if not hasattr(enhanced_cv_upload_service, method):
                    print(f"   Upload service missing method: {method}")
                    return False
            
            # Test required attributes
            required_attrs = ['cv_processor', 'structured_parser', 'original_cv_path']
            for attr in required_attrs:
                if not hasattr(enhanced_cv_upload_service, attr):
                    print(f"   Upload service missing attribute: {attr}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"   Upload service initialization failed: {e}")
            return False
    
    async def test_cv_loading(self) -> bool:
        """Test CV loading functionality"""
        try:
            # Test loading when no CV exists (should handle gracefully)
            result = enhanced_cv_upload_service.load_structured_cv(use_original=True)
            
            # Should return None or valid structure, but shouldn't crash
            if result is not None and not isinstance(result, dict):
                print("   CV loading returned invalid type")
                return False
            
            return True
            
        except Exception as e:
            print(f"   CV loading test failed: {e}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling in edge cases"""
        try:
            # Test parsing invalid JSON
            result1 = structured_cv_parser.parse_cv_content("invalid json {")
            if not isinstance(result1, dict):
                print("   Invalid JSON not handled gracefully")
                return False
            
            # Test parsing None
            result2 = structured_cv_parser.parse_cv_content(None)
            if not isinstance(result2, dict):
                print("   None input not handled gracefully")
                return False
            
            # Test parsing empty string
            result3 = structured_cv_parser.parse_cv_content("")
            if not isinstance(result3, dict):
                print("   Empty string not handled gracefully")
                return False
            
            return True
            
        except Exception as e:
            print(f"   Error handling test failed: {e}")
            return False
    
    async def run_integration_demo(self):
        """Run a demonstration of the integration working"""
        print("\n" + "🎭 INTEGRATION DEMO" + "\n" + "=" * 60)
        
        try:
            # Create a sample CV
            print("📝 Creating sample structured CV...")
            sample_cv = structured_cv_parser.parse_cv_content(self.test_cv_data)
            
            print(f"✅ CV created with {len(sample_cv)} sections")
            
            # Show sections
            print("\n📋 Available sections:")
            for key, value in sample_cv.items():
                if key not in ['saved_at', 'metadata'] and value:
                    if isinstance(value, list):
                        print(f"   • {key}: {len(value)} items")
                    elif isinstance(value, dict):
                        if key == 'personal_information':
                            name = value.get('name', 'N/A')
                            print(f"   • {key}: {name}")
                        elif key == 'unknown_sections':
                            print(f"   • {key}: {len(value)} unknown sections preserved")
                        else:
                            non_empty = sum(1 for v in value.values() if v)
                            print(f"   • {key}: {non_empty} fields")
                    else:
                        print(f"   • {key}: {type(value).__name__}")
            
            # Validate
            print("\n🔍 Validating structure...")
            validation = structured_cv_parser.validate_cv_structure(sample_cv)
            print(f"   Status: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
            print(f"   Sections found: {len(validation['sections_found'])}")
            
            if validation.get('warnings'):
                print(f"   Warnings: {len(validation['warnings'])}")
            
            # Show unknown sections handling
            unknown = sample_cv.get('unknown_sections', {})
            if unknown:
                print(f"\n❓ Unknown sections preserved: {list(unknown.keys())}")
                print("   (These sections will be kept safe and not lost)")
            
            print("\n🎉 Integration demo completed successfully!")
            
        except Exception as e:
            print(f"❌ Integration demo failed: {e}")


async def main():
    """Main test runner"""
    tester = StructuredCVTester()
    
    try:
        success = await tester.run_all_tests()
        
        if success:
            print(f"\n🚀 INTEGRATION STATUS: ✅ WORKING CORRECTLY")
            print("Your structured CV system is ready for use!")
        else:
            print(f"\n🚨 INTEGRATION STATUS: ❌ ISSUES FOUND") 
            print("Please review the failed tests above.")
            
        return success
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        logger.error("Test runner exception", exc_info=True)
        return False


if __name__ == "__main__":
    print("🔬 Structured CV Integration Test Suite")
    print("Testing all components of the structured CV system...\n")
    
    result = asyncio.run(main())
    sys.exit(0 if result else 1)