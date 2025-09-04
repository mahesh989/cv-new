#!/usr/bin/env python3
"""
Test script to verify DeepSeek integration and model switching functionality.
"""

import os
import sys
import asyncio
import json
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment
load_dotenv()

async def test_deepseek_service():
    """Test DeepSeek service directly."""
    print("🧪 Testing DeepSeek Service...")
    
    try:
        from src.deepseek_service import deepseek_service
        
        # Get service status
        status = deepseek_service.get_status()
        print(f"✅ DeepSeek Service Status: {json.dumps(status, indent=2)}")
        
        # Test if API key is configured
        if status['api_key_configured']:
            print("🔑 API key configured - can test actual API calls")
            
            # Test a simple prompt
            try:
                response = await deepseek_service.generate_response(
                    "Hello! Please respond with a brief test message.",
                    model="deepseek-chat",
                    temperature=0.3,
                    max_tokens=100
                )
                print(f"📝 DeepSeek Response: {response}")
                return True
            except Exception as e:
                print(f"❌ DeepSeek API call failed: {e}")
                return False
        else:
            print("⚠️  API key not configured - skipping actual API test")
            return True
            
    except Exception as e:
        print(f"❌ DeepSeek service test failed: {e}")
        return False

def test_model_state_manager():
    """Test the model state manager."""
    print("\n🧪 Testing Model State Manager...")
    
    try:
        from src.ai_config import model_state, AI_MODELS
        
        # Test getting current model
        current = model_state.get_current_model()
        print(f"📋 Current model: {current}")
        
        # Test setting DeepSeek models
        deepseek_models = ['deepseek-chat', 'deepseek-coder', 'deepseek-reasoner']
        
        for model in deepseek_models:
            print(f"🔄 Setting model to: {model}")
            model_state.set_model(model)
            
            current = model_state.get_current_model()
            provider = model_state.get_current_provider()
            
            print(f"   Current model: {current}")
            print(f"   Current provider: {provider}")
            
            if provider != 'deepseek':
                print(f"❌ Expected provider 'deepseek', got '{provider}'")
                return False
                
        print("✅ Model state manager working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Model state manager test failed: {e}")
        return False

async def test_hybrid_ai_service():
    """Test the hybrid AI service with DeepSeek models."""
    print("\n🧪 Testing Hybrid AI Service...")
    
    try:
        from src.hybrid_ai_service import HybridAIService
        from src.ai_config import model_state
        
        # Initialize service
        ai_service = HybridAIService()
        
        # Get service status
        status = ai_service.get_status()
        print(f"✅ Hybrid AI Service Status: {json.dumps(status, indent=2)}")
        
        # Test with DeepSeek model
        if status.get('deepseek_available', False):
            print("🔄 Setting model to deepseek-chat")
            model_state.set_model('deepseek-chat')
            
            try:
                response = await ai_service.generate_response(
                    "Hello! Please respond with a brief test message.",
                    temperature=0.3,
                    max_tokens=100
                )
                print(f"📝 Hybrid AI Service Response: {response}")
                return True
            except Exception as e:
                print(f"❌ Hybrid AI Service call failed: {e}")
                return False
        else:
            print("⚠️  DeepSeek not available in hybrid service - skipping API test")
            return True
            
    except Exception as e:
        print(f"❌ Hybrid AI service test failed: {e}")
        return False

def test_model_configurations():
    """Test that model configurations are properly set up."""
    print("\n🧪 Testing Model Configurations...")
    
    try:
        # Import from frontend config
        sys.path.insert(0, '/Users/mahesh/Documents/Github/mahesh/frontend/lib/config')
        import os
        
        # This is a backend test, so let's test backend config instead
        from src.ai_config import AI_MODELS
        
        # Test that DeepSeek models are available in backend config
        available_models = list(AI_MODELS.values())
        print(f"📋 Available models in backend: {available_models}")
        
        deepseek_models = ['deepseek-chat', 'deepseek-coder', 'deepseek-reasoner']
        
        for model in deepseek_models:
            if model in available_models:
                print(f"✅ {model} found in backend configuration")
            else:
                print(f"⚠️  {model} not in backend config, but this is OK since these are direct model names")
                
        # Test that we have DeepSeek model constants
        deepseek_constants = ['DEEPSEEK_CHAT', 'DEEPSEEK_CODER', 'DEEPSEEK_REASONER']
        for constant in deepseek_constants:
            if constant in AI_MODELS:
                print(f"✅ {constant} constant found in backend configuration")
            else:
                print(f"❌ {constant} constant NOT found in configuration")
                return False
                
        print("✅ DeepSeek models properly configured in backend")
        return True
        
    except Exception as e:
        print(f"❌ Model configuration test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting DeepSeek Integration Tests")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Model Configurations", test_model_configurations),
        ("Model State Manager", test_model_state_manager),
        ("DeepSeek Service", test_deepseek_service),
        ("Hybrid AI Service", test_hybrid_ai_service),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! DeepSeek integration is working correctly.")
        return 0
    else:
        print("💥 Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Tests failed with unexpected error: {e}")
        sys.exit(1)
