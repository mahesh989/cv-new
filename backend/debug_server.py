#!/usr/bin/env python3
"""
Debug script to test server startup and identify issues
"""

import sys
import os
import traceback

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all critical imports"""
    try:
        print("🔍 Testing imports...")
        
        # Test basic imports
        from src.hybrid_ai_service import HybridAIService
        print("✅ HybridAIService imported")
        
        from src.llm_keyword_matcher import llm_matcher
        print("✅ LLM keyword matcher imported")
        
        from src.ats_tester import router, test_ats_compatibility_llm
        print("✅ ATS tester imported")
        
        from src.main import app
        print("✅ Main app imported")
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        traceback.print_exc()
        return False

def test_server_start():
    """Test server startup"""
    try:
        print("\n🚀 Testing server startup...")
        
        import uvicorn
        from src.main import app
        
        # Test if we can create the app
        print("✅ App created successfully")
        
        # Try to start server
        print("🔧 Starting server on port 8001...")
        uvicorn.run(app, host='0.0.0.0', port=8001, log_level="info")
        
    except Exception as e:
        print(f"❌ Server startup error: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Main debug function"""
    print("🧪 DEBUGGING SERVER STARTUP")
    print("=" * 50)
    
    # Test imports first
    if not test_imports():
        print("❌ Import test failed - stopping")
        return
    
    # Test server startup
    test_server_start()

if __name__ == "__main__":
    main() 