#!/usr/bin/env python3
"""
Test API Routes Import

Quick test to ensure all the new routes can be imported properly.
"""

import sys
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.append(str(app_dir))

def test_imports():
    """Test that all components can be imported"""
    
    print("🔬 Testing API Routes Import")
    print("=" * 50)
    
    try:
        # Test core services
        print("📦 Testing core service imports...")
        from app.services.structured_cv_parser import structured_cv_parser
        print("   ✅ structured_cv_parser imported")
        
        from app.services.enhanced_cv_upload_service import enhanced_cv_upload_service
        print("   ✅ enhanced_cv_upload_service imported")
        
        from app.services.cv_processor import cv_processor
        print("   ✅ cv_processor imported")
        
        # Test routes
        print("\n🚀 Testing route imports...")
        from app.routes.cv_structured import router as cv_structured_router
        print("   ✅ cv_structured routes imported")
        
        # Check router configuration
        print(f"   📋 Router prefix: {cv_structured_router.prefix}")
        print(f"   🏷️  Router tags: {cv_structured_router.tags}")
        print(f"   🛣️  Routes count: {len(cv_structured_router.routes)}")
        
        # List available endpoints
        print("\n🛣️  Available endpoints:")
        for route in cv_structured_router.routes:
            methods = ', '.join(route.methods) if hasattr(route, 'methods') else 'N/A'
            path = route.path if hasattr(route, 'path') else 'N/A'
            print(f"   • {methods}: {path}")
        
        print("\n✅ All imports successful!")
        print("🎉 API integration is working correctly!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)