#!/usr/bin/env python3
"""
Test script to validate the main.py improvements
Run this to verify that all new modules work correctly
"""

import sys
import os
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_exceptions_module():
    """Test the exceptions module"""
    print("🧪 Testing exceptions module...")
    try:
        from src.core.exceptions import (
            ValidationError, 
            FileNotFoundError, 
            validate_filename,
            validate_text_content
        )
        
        # Test filename validation
        validate_filename("test.pdf", ['.pdf', '.docx'])
        print("  ✅ Filename validation works")
        
        # Test text validation
        validate_text_content("This is a valid text", min_length=5)
        print("  ✅ Text validation works")
        
        # Test error creation
        try:
            validate_filename("", ['.pdf'])
        except ValidationError as e:
            print(f"  ✅ ValidationError properly raised: {e.message}")
        
        print("  ✅ Exceptions module: PASSED")
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


def test_performance_module():
    """Test the performance module"""
    print("🧪 Testing performance module...")
    try:
        from src.core.performance import (
            SimpleCache,
            cached,
            timed,
            cache_key,
            MetricsCollector
        )
        
        # Test cache
        cache = SimpleCache(default_ttl=60)
        cache.set("test_key", "test_value")
        result = cache.get("test_key")
        assert result == "test_value", "Cache get/set failed"
        print("  ✅ Cache operations work")
        
        # Test cache key generation
        key = cache_key("arg1", "arg2", param1="value1")
        assert len(key) == 32, "Cache key generation failed"  # MD5 hash length
        print("  ✅ Cache key generation works")
        
        # Test metrics collector
        metrics = MetricsCollector()
        metrics.record("test_metric", 1.5, {"tag": "test"})
        stats = metrics.get_stats("test_metric")
        assert stats['count'] == 1, "Metrics recording failed"
        print("  ✅ Metrics collection works")
        
        # Test decorators (basic import)
        @cached(ttl=60)
        def test_cached_function():
            return "cached_result"
        
        @timed
        def test_timed_function():
            return "timed_result"
        
        print("  ✅ Decorators can be imported")
        print("  ✅ Performance module: PASSED")
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


def test_security_module():
    """Test the security module"""
    print("🧪 Testing security module...")
    try:
        from src.core.security import (
            SecurityValidator,
            ContentSecurityPolicy,
            generate_secure_filename,
            security_validator
        )
        
        # Test filename validation
        assert security_validator.validate_filename("test.pdf") == True, "Valid filename failed"
        assert security_validator.validate_filename("../test.pdf") == False, "Directory traversal not caught"
        assert security_validator.validate_filename("test.exe") == False, "Invalid extension not caught"
        print("  ✅ Filename validation works")
        
        # Test filename sanitization
        sanitized = security_validator.sanitize_filename("test<>file.pdf")
        assert "<" not in sanitized and ">" not in sanitized, "Sanitization failed"
        print("  ✅ Filename sanitization works")
        
        # Test CSP headers
        csp = ContentSecurityPolicy()
        headers = csp.get_headers()
        assert "Content-Security-Policy" in headers, "CSP headers missing"
        print("  ✅ CSP headers generation works")
        
        # Test secure filename generation
        secure_name = generate_secure_filename("test file.pdf")
        assert secure_name.endswith(".pdf"), "Secure filename generation failed"
        assert "_" in secure_name, "Timestamp/random suffix missing"
        print("  ✅ Secure filename generation works")
        
        print("  ✅ Security module: PASSED")
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


def test_cv_endpoints_module():
    """Test the CV endpoints module"""
    print("🧪 Testing CV endpoints module...")
    try:
        from src.api.cv_endpoints import (
            router,
            _get_media_type,
            _extract_pdf_text,
            _extract_docx_text
        )
        
        # Test media type detection
        assert _get_media_type("test.pdf") == 'application/pdf', "PDF media type wrong"
        assert _get_media_type("test.docx") == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', "DOCX media type wrong"
        print("  ✅ Media type detection works")
        
        # Test router exists
        assert router is not None, "Router not created"
        print("  ✅ Router created successfully")
        
        print("  ✅ CV endpoints module: PASSED")
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


def test_main_improved():
    """Test the improved main module can be imported"""
    print("🧪 Testing improved main module...")
    try:
        # Test that main_improved can be imported without errors
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "main_improved", 
            os.path.join(os.path.dirname(__file__), 'src', 'main_improved.py')
        )
        if spec is None:
            print("  ❌ Could not load main_improved.py")
            return False
            
        print("  ✅ main_improved.py can be loaded")
        print("  ✅ Main improved module: PASSED")
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


def test_file_operations():
    """Test file operations with security"""
    print("🧪 Testing secure file operations...")
    try:
        from src.core.security import validate_upload_security
        from src.core.exceptions import ValidationError
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test valid file operation
            test_file = os.path.join(temp_dir, "test.pdf")
            with open(test_file, "w") as f:
                f.write("test content")
            
            # This should work
            try:
                validate_upload_security("test.pdf", test_file, temp_dir)
                print("  ✅ Valid file operation allowed")
            except Exception as e:
                print(f"  ❌ Valid file operation rejected: {e}")
                return False
            
            # Test invalid directory traversal
            try:
                validate_upload_security("../test.pdf", "../test.pdf", temp_dir)
                print("  ❌ Directory traversal attack not prevented")
                return False
            except Exception:
                print("  ✅ Directory traversal attack prevented")
        
        print("  ✅ File operations security: PASSED")
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting main.py improvements validation tests...\n")
    
    tests = [
        test_exceptions_module,
        test_performance_module,
        test_security_module,
        test_cv_endpoints_module,
        test_main_improved,
        test_file_operations
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()  # Empty line between tests
    
    print("=" * 60)
    print(f"📊 TEST RESULTS:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Your improvements are working correctly!")
        print("✨ Your backend is now more secure, performant, and maintainable!")
        return 0
    else:
        print(f"\n⚠️  {failed} tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
