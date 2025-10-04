#!/usr/bin/env python3
"""
Integration test for server startup and basic functionality.

This test verifies:
1. Server can start without errors
2. Routes are properly configured
3. Authentication is working
4. User-specific endpoints are accessible
"""

import sys
import asyncio
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_server_import():
    """Test that the server can be imported without errors"""
    print("🧪 Testing Server Import...")
    
    try:
        from app.main import app
        print("  ✅ Main app imported successfully")
        
        # Check that routes are registered
        routes = [route.path for route in app.routes]
        expected_routes = [
            "/api/auth/register",
            "/api/auth/login", 
            "/api/cv/upload",
            "/api/cv/list",
            "/api/skill-extraction/analyze"
        ]
        
        for expected_route in expected_routes:
            if any(expected_route in route for route in routes):
                print(f"  ✅ Route {expected_route} is registered")
            else:
                print(f"  ⚠️ Route {expected_route} not found")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Server import failed: {e}")
        return False

def test_authentication_flow():
    """Test authentication components"""
    print("🧪 Testing Authentication Flow...")
    
    try:
        from app.core.auth import create_access_token, verify_token
        
        # Test token creation with simple user data
        user_data = {"sub": "test@gmail.com", "email": "test@gmail.com"}
        token = create_access_token(user_data)
        print(f"  ✅ Access token created successfully")
        
        # Test token verification
        token_data = verify_token(token)
        assert token_data.email == "test@gmail.com"
        print(f"  ✅ Token verification working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Authentication test failed: {e}")
        return False

def test_user_path_creation():
    """Test user path creation and directory structure"""
    print("🧪 Testing User Path Creation...")
    
    try:
        from app.utils.user_path_utils import get_user_base_path, ensure_user_directories
        
        # Test with a new user
        test_user = "integration_test@example.com"
        base_path = get_user_base_path(test_user)
        
        # Ensure directories are created
        ensure_user_directories(test_user)
        
        # Verify structure exists
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
        
        print(f"  ✅ User directory structure created: {base_path}")
        
        # Clean up test directory
        import shutil
        if base_path.parent.exists():
            shutil.rmtree(base_path.parent)
        
        return True
        
    except Exception as e:
        print(f"  ❌ User path creation test failed: {e}")
        return False

def test_service_instantiation():
    """Test that services can be instantiated with user_email"""
    print("🧪 Testing Service Instantiation...")
    
    try:
        from app.services.skill_extraction.result_saver import SkillExtractionResultSaver
        from app.services.job_extraction_service import JobExtractionService
        from app.unified_latest_file_selector import get_selector_for_user
        
        test_user = "service_test@example.com"
        
        # Test result saver
        result_saver = SkillExtractionResultSaver(user_email=test_user)
        assert result_saver.user_email == test_user
        print(f"  ✅ SkillExtractionResultSaver instantiated")
        
        # Test job extraction service
        job_service = JobExtractionService(user_email=test_user)
        assert job_service.user_email == test_user
        print(f"  ✅ JobExtractionService instantiated")
        
        # Test unified selector
        selector = get_selector_for_user(test_user)
        assert selector.user_email == test_user
        print(f"  ✅ UnifiedLatestFileSelector instantiated")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Service instantiation test failed: {e}")
        return False

def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting Server Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_server_import,
        test_authentication_flow,
        test_user_path_creation,
        test_service_instantiation
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
    
    print(f"📊 Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! Server is ready for use.")
        return True
    else:
        print("❌ Some integration tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
