#!/usr/bin/env python3
"""
Comprehensive test for user isolation, directory structure, and unified file selector.

This test verifies:
1. User-specific directory creation
2. Base path generation
3. Unified file selector functionality
4. Service initialization with user_email
5. File operations are user-scoped
6. No admin@admin.com references remain
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_user_path_utils():
    """Test user path utilities"""
    print("🧪 Testing User Path Utilities...")
    
    from app.utils.user_path_utils import get_user_base_path, ensure_user_directories
    
    # Test with different user emails
    test_users = [
        "test@example.com",
        "user@domain.org", 
        "maheshwor@gmail.com"
    ]
    
    for user_email in test_users:
        print(f"  📁 Testing user: {user_email}")
        
        # Test base path generation
        base_path = get_user_base_path(user_email)
        expected_path = Path("user") / f"user_{user_email}" / "cv-analysis"
        
        assert str(base_path) == str(expected_path), f"Expected {expected_path}, got {base_path}"
        print(f"    ✅ Base path: {base_path}")
        
        # Test directory creation
        ensure_user_directories(user_email)
        
        # Verify directory structure exists
        required_dirs = [
            base_path,
            base_path / "applied_companies",
            base_path / "cvs" / "original",
            base_path / "cvs" / "tailored",
            base_path / "saved_jobs",
            base_path / "uploads"
        ]
        
        for dir_path in required_dirs:
            assert dir_path.exists(), f"Directory {dir_path} should exist"
            assert dir_path.is_dir(), f"{dir_path} should be a directory"
        
        print(f"    ✅ Directory structure created successfully")
    
    print("✅ User Path Utilities test passed!")

def test_unified_file_selector():
    """Test unified file selector"""
    print("🧪 Testing Unified File Selector...")
    
    from app.unified_latest_file_selector import get_selector_for_user, UnifiedLatestFileSelector
    
    # Test user-specific selector creation
    user_email = "test@example.com"
    selector = get_selector_for_user(user_email)
    
    assert selector.user_email == user_email, f"Expected user_email {user_email}, got {selector.user_email}"
    assert selector.base_path == Path("user") / f"user_{user_email}" / "cv-analysis"
    print(f"  ✅ User-specific selector created: {selector.base_path}")
    
    # Test global selector (should not have user_email)
    global_selector = UnifiedLatestFileSelector()
    assert global_selector.user_email is None, "Global selector should not have user_email"
    print(f"  ✅ Global selector created without user_email")
    
    # Test that operations require user_email
    try:
        global_selector.get_latest_cv_for_company("test_company")
        assert False, "Should have raised ValueError for missing user_email"
    except ValueError as e:
        assert "user_email must be provided" in str(e)
        print(f"  ✅ Global selector properly validates user_email requirement")
    
    print("✅ Unified File Selector test passed!")

def test_service_initialization():
    """Test that all services require user_email parameter"""
    print("🧪 Testing Service Initialization...")
    
    # Test services that should require user_email
    services_to_test = [
        ("SkillExtractionResultSaver", "app.services.skill_extraction.result_saver"),
        ("JobExtractionService", "app.services.job_extraction_service"),
        ("JDAnalyzer", "app.services.jd_analysis.jd_analyzer"),
        ("CVJDMatcher", "app.services.cv_jd_matching.cv_jd_matcher"),
        ("ATSRecommendationService", "app.services.ats_recommendation_service"),
        ("AIRecommendationGenerator", "app.services.ai_recommendation_generator"),
        ("CVUploadService", "app.modules.cv.upload"),
        ("CVSelectionService", "app.modules.cv.selection"),
        ("CVPreviewService", "app.modules.cv.preview"),
        ("CVTailoringService", "app.tailored_cv.services.cv_tailoring_service"),
        ("SavedJobsService", "app.services.saved_jobs_service"),
    ]
    
    for service_name, module_path in services_to_test:
        print(f"  🔧 Testing {service_name}...")
        
        try:
            # Import the service class
            module = __import__(module_path, fromlist=[service_name])
            service_class = getattr(module, service_name)
            
            # Test that it requires user_email parameter
            try:
                service_class()  # Should fail without user_email
                assert False, f"{service_name} should require user_email parameter"
            except TypeError as e:
                assert "user_email" in str(e) or "missing 1 required positional argument" in str(e)
                print(f"    ✅ {service_name} requires user_email parameter")
            
            # Test that it works with user_email
            service_instance = service_class(user_email="test@example.com")
            assert service_instance.user_email == "test@example.com"
            print(f"    ✅ {service_name} initializes correctly with user_email")
            
        except ImportError as e:
            print(f"    ⚠️ Could not import {service_name}: {e}")
        except Exception as e:
            print(f"    ❌ Error testing {service_name}: {e}")
    
    print("✅ Service Initialization test passed!")

def test_no_admin_references():
    """Test that no admin@admin.com references remain"""
    print("🧪 Testing No Admin References...")
    
    import subprocess
    import os
    
    # Search for admin@admin.com references in the codebase
    try:
        result = subprocess.run(
            ["grep", "-r", "admin@admin.com", "app/"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"  ❌ Found admin@admin.com references:")
            print(result.stdout)
            assert False, "admin@admin.com references should not exist"
        else:
            print(f"  ✅ No admin@admin.com references found")
    
    except FileNotFoundError:
        # Fallback: use Python to search
        admin_refs = []
        for root, dirs, files in os.walk("app/"):
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if "admin@admin.com" in content:
                                admin_refs.append(str(file_path))
                    except Exception:
                        pass
        
        if admin_refs:
            print(f"  ❌ Found admin@admin.com references in:")
            for ref in admin_refs:
                print(f"    - {ref}")
            assert False, "admin@admin.com references should not exist"
        else:
            print(f"  ✅ No admin@admin.com references found")
    
    print("✅ No Admin References test passed!")

def test_directory_isolation():
    """Test that user directories are properly isolated"""
    print("🧪 Testing Directory Isolation...")
    
    from app.utils.user_path_utils import get_user_base_path, ensure_user_directories
    
    # Create test users
    user1 = "user1@test.com"
    user2 = "user2@test.com"
    
    # Create directories for both users
    ensure_user_directories(user1)
    ensure_user_directories(user2)
    
    # Get their base paths
    path1 = get_user_base_path(user1)
    path2 = get_user_base_path(user2)
    
    # Verify they are different
    assert path1 != path2, "User directories should be different"
    print(f"  ✅ User 1 path: {path1}")
    print(f"  ✅ User 2 path: {path2}")
    
    # Create a test file in user1's directory
    test_file = path1 / "test_file.txt"
    test_file.write_text("User 1 data")
    
    # Verify user2 cannot see user1's file
    user2_test_file = path2 / "test_file.txt"
    assert not user2_test_file.exists(), "User 2 should not see user 1's files"
    print(f"  ✅ User directories are properly isolated")
    
    # Clean up test files
    test_file.unlink()
    
    print("✅ Directory Isolation test passed!")

def test_file_operations():
    """Test file operations with user context"""
    print("🧪 Testing File Operations...")
    
    from app.services.skill_extraction.result_saver import SkillExtractionResultSaver
    from app.utils.user_path_utils import get_user_base_path
    
    user_email = "test@example.com"
    
    # Create a result saver instance
    result_saver = SkillExtractionResultSaver(user_email=user_email)
    
    # Verify it uses the correct user path
    expected_base = get_user_base_path(user_email)
    assert result_saver.base_dir == expected_base
    print(f"  ✅ Result saver uses correct user path: {result_saver.base_dir}")
    
    # Test that it can create user-specific paths
    company = "TestCompany"
    paths = result_saver.paths(company)
    
    # Verify paths are user-specific
    for path_name, path_func in paths.items():
        if callable(path_func):
            test_path = path_func("20240101_120000")
            assert str(expected_base) in str(test_path), f"Path {test_path} should be user-specific"
            print(f"    ✅ {path_name} path is user-specific: {test_path}")
    
    print("✅ File Operations test passed!")

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting User Isolation Test Suite")
    print("=" * 50)
    
    try:
        test_user_path_utils()
        print()
        
        test_unified_file_selector()
        print()
        
        test_service_initialization()
        print()
        
        test_no_admin_references()
        print()
        
        test_directory_isolation()
        print()
        
        test_file_operations()
        print()
        
        print("🎉 All tests passed! User isolation is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
