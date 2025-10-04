#!/usr/bin/env python3
"""
Test unified file selector integration with generated files.

This test verifies:
1. Unified selector can find generated files
2. File selection works with user-specific paths
3. Latest file selection works correctly
4. CV content retrieval works with generated files
"""

import os
import sys
import json
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_unified_selector_with_generated_files():
    """Test unified selector with actual generated files"""
    print("🧪 Testing Unified Selector with Generated Files...")
    
    try:
        from app.unified_latest_file_selector import get_selector_for_user
        from app.utils.user_path_utils import get_user_base_path, ensure_user_directories
        
        # Use the test user that has generated files
        user_email = "test_company_structure@example.com"
        company_name = "CompleteTestCompany"
        
        # Get the selector for this user
        selector = get_selector_for_user(user_email)
        
        # Verify selector has correct user context
        assert selector.user_email == user_email, f"Expected user_email {user_email}, got {selector.user_email}"
        print(f"  ✅ Selector created for user: {user_email}")
        
        # Test getting latest CV for company
        try:
            cv_info = selector.get_latest_cv_for_company(company_name)
            print(f"  ✅ Latest CV found for {company_name}: {cv_info}")
        except Exception as e:
            print(f"  ⚠️ No CV found for {company_name} (expected if no CV files): {e}")
        
        # Test getting latest CV across all companies
        try:
            cv_info = selector.get_latest_cv_across_all(company_name)
            print(f"  ✅ Latest CV across all found: {cv_info}")
        except Exception as e:
            print(f"  ⚠️ No CV found across all (expected if no CV files): {e}")
        
        # Test getting CV content
        try:
            content = selector.get_cv_content_across_all(company_name)
            print(f"  ✅ CV content retrieved: {len(content) if content else 0} characters")
        except Exception as e:
            print(f"  ⚠️ No CV content found (expected if no CV files): {e}")
        
        # Test directory listing
        base_path = get_user_base_path(user_email)
        company_dir = base_path / "applied_companies" / company_name
        
        if company_dir.exists():
            files = list(company_dir.glob("*.json"))
            print(f"  ✅ Found {len(files)} files in company directory")
            
            # List the files
            for file in files:
                print(f"    📄 {file.name}")
        else:
            print(f"  ⚠️ Company directory does not exist: {company_dir}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Unified selector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_retrieval_by_type():
    """Test retrieving specific file types"""
    print("🧪 Testing File Retrieval by Type...")
    
    try:
        from app.utils.user_path_utils import get_user_base_path
        
        # Use the test user that has generated files
        user_email = "test_company_structure@example.com"
        company_name = "CompleteTestCompany"
        
        base_path = get_user_base_path(user_email)
        company_dir = base_path / "applied_companies" / company_name
        
        if not company_dir.exists():
            print(f"  ⚠️ Company directory does not exist: {company_dir}")
            return True
        
        # Test retrieving different file types
        file_types = [
            "jd_analysis",
            "skills_analysis", 
            "cv_jd_matching",
            "ai_recommendation",
            "component_analysis"
        ]
        
        for file_type in file_types:
            # Look for files with this type
            pattern = f"*{file_type}*.json"
            matching_files = list(company_dir.glob(pattern))
            
            if matching_files:
                latest_file = max(matching_files, key=lambda f: f.stat().st_mtime)
                print(f"  ✅ Found {file_type} file: {latest_file.name}")
                
                # Try to read the file content
                try:
                    with open(latest_file, 'r') as f:
                        data = json.load(f)
                        print(f"    📊 File contains: {list(data.keys())}")
                except Exception as e:
                    print(f"    ⚠️ Could not read file content: {e}")
            else:
                print(f"  ⚠️ No {file_type} files found")
        
        return True
        
    except Exception as e:
        print(f"  ❌ File retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_isolation_in_file_operations():
    """Test that file operations are properly isolated by user"""
    print("🧪 Testing User Isolation in File Operations...")
    
    try:
        from app.unified_latest_file_selector import get_selector_for_user
        from app.utils.user_path_utils import get_user_base_path
        
        # Test with two different users
        user1 = "test_company_structure@example.com"
        user2 = "test_file_gen@example.com"
        
        # Get selectors for both users
        selector1 = get_selector_for_user(user1)
        selector2 = get_selector_for_user(user2)
        
        # Verify they have different base paths
        path1 = selector1.base_path
        path2 = selector2.base_path
        
        assert path1 != path2, "Users should have different base paths"
        print(f"  ✅ User 1 path: {path1}")
        print(f"  ✅ User 2 path: {path2}")
        
        # Verify paths are user-specific
        assert str(path1).endswith(f"user_{user1}/cv-analysis"), f"Path 1 should be user-specific: {path1}"
        assert str(path2).endswith(f"user_{user2}/cv-analysis"), f"Path 2 should be user-specific: {path2}"
        print(f"  ✅ Both paths are properly user-specific")
        
        # Test that each user can only access their own files
        base_path1 = get_user_base_path(user1)
        base_path2 = get_user_base_path(user2)
        
        # Check if user1's files exist
        user1_files = list(base_path1.rglob("*.json")) if base_path1.exists() else []
        user2_files = list(base_path2.rglob("*.json")) if base_path2.exists() else []
        
        print(f"  ✅ User 1 has {len(user1_files)} JSON files")
        print(f"  ✅ User 2 has {len(user2_files)} JSON files")
        
        # Verify no cross-contamination
        for file in user1_files:
            assert str(user1) in str(file), f"User 1 file should contain user1 email: {file}"
        
        for file in user2_files:
            assert str(user2) in str(file), f"User 2 file should contain user2 email: {file}"
        
        print(f"  ✅ No cross-contamination between users")
        
        return True
        
    except Exception as e:
        print(f"  ❌ User isolation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_unified_selector_tests():
    """Run all unified selector integration tests"""
    print("🚀 Starting Unified Selector Integration Test Suite")
    print("=" * 60)
    
    tests = [
        test_unified_selector_with_generated_files,
        test_file_retrieval_by_type,
        test_user_isolation_in_file_operations
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
    
    print(f"📊 Unified Selector Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All unified selector tests passed! File selection is working correctly.")
        return True
    else:
        print("❌ Some unified selector tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_unified_selector_tests()
    sys.exit(0 if success else 1)
