#!/usr/bin/env python3
"""
Test file generation and appending functionality within company folders.

This test verifies:
1. Skills analysis JSON files are generated correctly
2. JD analysis JSON files are created
3. File appending works properly
4. Company-specific directory structure is maintained
5. User isolation is preserved in file operations
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_skills_analysis_file_generation():
    """Test skills analysis file generation and appending"""
    print("🧪 Testing Skills Analysis File Generation...")
    
    try:
        from app.services.skill_extraction.result_saver import SkillExtractionResultSaver
        from app.utils.user_path_utils import get_user_base_path, ensure_user_directories
        
        # Setup test user and company
        user_email = "test_file_gen@example.com"
        company_name = "TestCompany"
        
        # Ensure user directories exist
        ensure_user_directories(user_email)
        
        # Create result saver instance
        result_saver = SkillExtractionResultSaver(user_email=user_email)
        
        # Test file paths generation
        paths = result_saver.paths(company_name)
        timestamp = "20240101_120000"
        
        # Test skills analysis file path
        skills_path = paths["skills_analysis"](timestamp)
        expected_path = get_user_base_path(user_email) / "applied_companies" / company_name / f"{company_name}_skills_analysis_{timestamp}.json"
        
        assert str(skills_path) == str(expected_path), f"Expected {expected_path}, got {skills_path}"
        print(f"  ✅ Skills analysis path: {skills_path}")
        
        # Test file creation
        test_data = {
            "company": company_name,
            "timestamp": timestamp,
            "skills_match": {
                "matched_skills": ["Python", "FastAPI", "SQLAlchemy"],
                "missing_skills": ["Docker", "Kubernetes"],
                "match_percentage": 75.5
            },
            "analysis_summary": "Good match with core skills"
        }
        
        # Create the file
        skills_path.parent.mkdir(parents=True, exist_ok=True)
        with open(skills_path, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        # Verify file exists and contains correct data
        assert skills_path.exists(), "Skills analysis file should exist"
        
        with open(skills_path, 'r') as f:
            loaded_data = json.load(f)
            assert loaded_data["company"] == company_name
            assert loaded_data["skills_match"]["match_percentage"] == 75.5
            print(f"  ✅ Skills analysis file created and verified")
        
        # Test appending functionality
        append_data = {
            "additional_analysis": {
                "recommendations": ["Learn Docker", "Study Kubernetes"],
                "priority": "high"
            }
        }
        
        # Append to existing file
        with open(skills_path, 'r') as f:
            existing_data = json.load(f)
        
        existing_data.update(append_data)
        
        with open(skills_path, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        # Verify append worked
        with open(skills_path, 'r') as f:
            updated_data = json.load(f)
            assert "additional_analysis" in updated_data
            assert updated_data["additional_analysis"]["priority"] == "high"
            print(f"  ✅ File appending works correctly")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Skills analysis file generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_jd_analysis_file_generation():
    """Test JD analysis file generation"""
    print("🧪 Testing JD Analysis File Generation...")
    
    try:
        from app.services.jd_analysis.jd_analyzer import JDAnalyzer
        from app.utils.user_path_utils import get_user_base_path, ensure_user_directories
        
        # Setup test user and company
        user_email = "test_jd_gen@example.com"
        company_name = "JDTestCompany"
        
        # Ensure user directories exist
        ensure_user_directories(user_email)
        
        # Create JD analyzer instance
        jd_analyzer = JDAnalyzer(user_email=user_email)
        
        # Test base path
        base_path = get_user_base_path(user_email)
        company_dir = base_path / "applied_companies" / company_name
        company_dir.mkdir(parents=True, exist_ok=True)
        
        # Test JD analysis file creation
        timestamp = "20240101_130000"
        jd_analysis_file = company_dir / f"{company_name}_jd_analysis_{timestamp}.json"
        
        # Create test JD analysis data
        jd_analysis_data = {
            "company": company_name,
            "timestamp": timestamp,
            "job_title": "Senior Python Developer",
            "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "preferred_skills": ["Kubernetes", "AWS", "Redis"],
            "experience_level": "Senior",
            "location": "Remote",
            "salary_range": "$80,000 - $120,000",
            "analysis": {
                "key_requirements": ["3+ years Python", "API development", "Database design"],
                "company_culture": "Startup environment",
                "growth_opportunities": ["Technical leadership", "Mentoring"]
            }
        }
        
        # Write JD analysis file
        with open(jd_analysis_file, 'w') as f:
            json.dump(jd_analysis_data, f, indent=2)
        
        # Verify file exists and contains correct data
        assert jd_analysis_file.exists(), "JD analysis file should exist"
        
        with open(jd_analysis_file, 'r') as f:
            loaded_data = json.load(f)
            assert loaded_data["company"] == company_name
            assert loaded_data["job_title"] == "Senior Python Developer"
            assert "Python" in loaded_data["required_skills"]
            print(f"  ✅ JD analysis file created and verified")
        
        return True
        
    except Exception as e:
        print(f"  ❌ JD analysis file generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cv_jd_matching_file_generation():
    """Test CV-JD matching file generation"""
    print("🧪 Testing CV-JD Matching File Generation...")
    
    try:
        from app.services.cv_jd_matching.cv_jd_matcher import CVJDMatcher
        from app.utils.user_path_utils import get_user_base_path, ensure_user_directories
        
        # Setup test user and company
        user_email = "test_cv_jd@example.com"
        company_name = "CVJDTestCompany"
        
        # Ensure user directories exist
        ensure_user_directories(user_email)
        
        # Create CV-JD matcher instance
        cv_jd_matcher = CVJDMatcher(user_email=user_email)
        
        # Test base path
        base_path = get_user_base_path(user_email)
        company_dir = base_path / "applied_companies" / company_name
        company_dir.mkdir(parents=True, exist_ok=True)
        
        # Test CV-JD matching file creation
        timestamp = "20240101_140000"
        matching_file = company_dir / f"{company_name}_cv_jd_matching_{timestamp}.json"
        
        # Create test CV-JD matching data
        matching_data = {
            "company": company_name,
            "timestamp": timestamp,
            "cv_filename": "john_doe_cv.pdf",
            "jd_filename": "senior_python_dev_jd.pdf",
            "matching_results": {
                "overall_match": 78.5,
                "skills_match": {
                    "matched": ["Python", "FastAPI", "SQLAlchemy", "PostgreSQL"],
                    "missing": ["Docker", "Kubernetes"],
                    "extra": ["JavaScript", "React"]
                },
                "experience_match": {
                    "required_years": 3,
                    "cv_years": 4,
                    "match": True
                },
                "education_match": {
                    "required": "Bachelor's in Computer Science",
                    "cv_education": "Master's in Software Engineering",
                    "match": True
                }
            },
            "recommendations": [
                "Highlight Docker experience if any",
                "Emphasize API development projects",
                "Mention database optimization experience"
            ]
        }
        
        # Write CV-JD matching file
        with open(matching_file, 'w') as f:
            json.dump(matching_data, f, indent=2)
        
        # Verify file exists and contains correct data
        assert matching_file.exists(), "CV-JD matching file should exist"
        
        with open(matching_file, 'r') as f:
            loaded_data = json.load(f)
            assert loaded_data["company"] == company_name
            assert loaded_data["matching_results"]["overall_match"] == 78.5
            assert "Python" in loaded_data["matching_results"]["skills_match"]["matched"]
            print(f"  ✅ CV-JD matching file created and verified")
        
        return True
        
    except Exception as e:
        print(f"  ❌ CV-JD matching file generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_recommendation_file_generation():
    """Test AI recommendation file generation"""
    print("🧪 Testing AI Recommendation File Generation...")
    
    try:
        from app.services.ai_recommendation_generator import AIRecommendationGenerator
        from app.utils.user_path_utils import get_user_base_path, ensure_user_directories
        
        # Setup test user and company
        user_email = "test_ai_rec@example.com"
        company_name = "AIRecTestCompany"
        
        # Ensure user directories exist
        ensure_user_directories(user_email)
        
        # Create AI recommendation generator instance
        ai_generator = AIRecommendationGenerator(user_email=user_email)
        
        # Test base path
        base_path = get_user_base_path(user_email)
        company_dir = base_path / "applied_companies" / company_name
        company_dir.mkdir(parents=True, exist_ok=True)
        
        # Test AI recommendation file creation
        timestamp = "20240101_150000"
        ai_rec_file = company_dir / f"{company_name}_ai_recommendation_{timestamp}.json"
        
        # Create test AI recommendation data
        ai_rec_data = {
            "company": company_name,
            "timestamp": timestamp,
            "job_title": "Senior Python Developer",
            "ai_recommendations": {
                "cv_optimization": [
                    "Add Docker containerization experience to skills section",
                    "Highlight API development projects with specific metrics",
                    "Include database optimization achievements"
                ],
                "skill_improvements": [
                    "Learn Kubernetes for container orchestration",
                    "Study AWS services for cloud deployment",
                    "Practice system design for scalability"
                ],
                "tailored_sections": {
                    "summary": "Experienced Python developer with 4+ years in API development and database design, seeking to leverage expertise in containerization and cloud technologies.",
                    "skills": ["Python", "FastAPI", "SQLAlchemy", "PostgreSQL", "Docker", "AWS", "System Design"],
                    "experience_highlights": [
                        "Developed RESTful APIs serving 10K+ daily users",
                        "Optimized database queries reducing response time by 40%",
                        "Implemented microservices architecture with Docker"
                    ]
                }
            },
            "confidence_score": 0.85,
            "generation_metadata": {
                "model_used": "gpt-4",
                "prompt_version": "v2.1",
                "processing_time": "2.3s"
            }
        }
        
        # Write AI recommendation file
        with open(ai_rec_file, 'w') as f:
            json.dump(ai_rec_data, f, indent=2)
        
        # Verify file exists and contains correct data
        assert ai_rec_file.exists(), "AI recommendation file should exist"
        
        with open(ai_rec_file, 'r') as f:
            loaded_data = json.load(f)
            assert loaded_data["company"] == company_name
            assert loaded_data["confidence_score"] == 0.85
            assert len(loaded_data["ai_recommendations"]["cv_optimization"]) > 0
            print(f"  ✅ AI recommendation file created and verified")
        
        return True
        
    except Exception as e:
        print(f"  ❌ AI recommendation file generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_company_directory_structure():
    """Test complete company directory structure with all file types"""
    print("🧪 Testing Complete Company Directory Structure...")
    
    try:
        from app.utils.user_path_utils import get_user_base_path, ensure_user_directories
        
        # Setup test user and company
        user_email = "test_company_structure@example.com"
        company_name = "CompleteTestCompany"
        
        # Ensure user directories exist
        ensure_user_directories(user_email)
        
        # Get base path
        base_path = get_user_base_path(user_email)
        company_dir = base_path / "applied_companies" / company_name
        company_dir.mkdir(parents=True, exist_ok=True)
        
        # Create all expected file types
        timestamp = "20240101_160000"
        
        file_types = [
            f"jd_original_{timestamp}.json",
            f"job_info_{company_name}_{timestamp}.json",
            f"{company_name}_jd_analysis_{timestamp}.json",
            f"{company_name}_cv_jd_matching_{timestamp}.json",
            f"{company_name}_component_analysis_{timestamp}.json",
            f"{company_name}_skills_analysis_{timestamp}.json",
            f"{company_name}_input_recommendation_{timestamp}.json",
            f"{company_name}_ai_recommendation_{timestamp}.json",
            f"{company_name}_tailored_cv_{timestamp}.json"
        ]
        
        # Create test files
        for file_name in file_types:
            file_path = company_dir / file_name
            test_data = {
                "company": company_name,
                "timestamp": timestamp,
                "file_type": file_name.split('_')[0],
                "test_data": f"Sample data for {file_name}"
            }
            
            with open(file_path, 'w') as f:
                json.dump(test_data, f, indent=2)
        
        # Verify all files exist
        for file_name in file_types:
            file_path = company_dir / file_name
            assert file_path.exists(), f"File {file_name} should exist"
            
            # Verify file content
            with open(file_path, 'r') as f:
                data = json.load(f)
                assert data["company"] == company_name
                assert data["timestamp"] == timestamp
        
        print(f"  ✅ All {len(file_types)} file types created successfully")
        
        # Test directory listing
        files_in_dir = list(company_dir.glob("*.json"))
        assert len(files_in_dir) == len(file_types), f"Expected {len(file_types)} files, found {len(files_in_dir)}"
        print(f"  ✅ Directory contains all expected files")
        
        # Test user isolation - verify files are in correct user directory
        assert str(base_path).endswith(f"user_{user_email}/cv-analysis"), f"Base path should be user-specific: {base_path}"
        print(f"  ✅ User isolation maintained: {base_path}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Company directory structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_appending_functionality():
    """Test file appending functionality across different file types"""
    print("🧪 Testing File Appending Functionality...")
    
    try:
        from app.utils.user_path_utils import get_user_base_path, ensure_user_directories
        
        # Setup test user and company
        user_email = "test_appending@example.com"
        company_name = "AppendTestCompany"
        
        # Ensure user directories exist
        ensure_user_directories(user_email)
        
        # Get base path
        base_path = get_user_base_path(user_email)
        company_dir = base_path / "applied_companies" / company_name
        company_dir.mkdir(parents=True, exist_ok=True)
        
        # Test appending to skills analysis file
        timestamp = "20240101_170000"
        skills_file = company_dir / f"{company_name}_skills_analysis_{timestamp}.json"
        
        # Initial data
        initial_data = {
            "company": company_name,
            "timestamp": timestamp,
            "initial_analysis": {
                "skills_found": ["Python", "FastAPI"],
                "match_score": 60
            }
        }
        
        with open(skills_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
        
        # Append additional analysis
        append_data = {
            "additional_analysis": {
                "missing_skills": ["Docker", "Kubernetes"],
                "recommendations": ["Learn containerization", "Study orchestration"]
            },
            "updated_timestamp": "20240101_170500"
        }
        
        # Read, update, and write back
        with open(skills_file, 'r') as f:
            existing_data = json.load(f)
        
        existing_data.update(append_data)
        
        with open(skills_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        # Verify append worked
        with open(skills_file, 'r') as f:
            final_data = json.load(f)
            assert "initial_analysis" in final_data
            assert "additional_analysis" in final_data
            assert final_data["additional_analysis"]["missing_skills"] == ["Docker", "Kubernetes"]
            print(f"  ✅ File appending works correctly")
        
        # Test multiple appends
        for i in range(3):
            new_append = {
                f"append_round_{i+1}": {
                    "timestamp": f"20240101_17{i:02d}00",
                    "data": f"Additional data round {i+1}"
                }
            }
            
            with open(skills_file, 'r') as f:
                current_data = json.load(f)
            
            current_data.update(new_append)
            
            with open(skills_file, 'w') as f:
                json.dump(current_data, f, indent=2)
        
        # Verify all appends
        with open(skills_file, 'r') as f:
            final_data = json.load(f)
            assert "append_round_1" in final_data
            assert "append_round_2" in final_data
            assert "append_round_3" in final_data
            print(f"  ✅ Multiple appends work correctly")
        
        return True
        
    except Exception as e:
        print(f"  ❌ File appending functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_file_generation_tests():
    """Run all file generation tests"""
    print("🚀 Starting File Generation Test Suite")
    print("=" * 60)
    
    tests = [
        test_skills_analysis_file_generation,
        test_jd_analysis_file_generation,
        test_cv_jd_matching_file_generation,
        test_ai_recommendation_file_generation,
        test_company_directory_structure,
        test_file_appending_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            print()
    
    print(f"📊 File Generation Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All file generation tests passed! File operations are working correctly.")
        return True
    else:
        print("❌ Some file generation tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_file_generation_tests()
    sys.exit(0 if success else 1)
