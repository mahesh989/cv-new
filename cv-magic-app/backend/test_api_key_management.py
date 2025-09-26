#!/usr/bin/env python3
"""
Test script for API Key Management System

This script tests the complete API key management functionality including:
- API key storage and retrieval
- API key validation
- Provider status checking
- Error handling
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "cv-magic-app" / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.api_key_manager import api_key_manager
from app.services.enhanced_ai_service import enhanced_ai_service
from app.ai.ai_config import ai_config


async def test_api_key_management():
    """Test the complete API key management system"""
    print("🧪 Testing API Key Management System")
    print("=" * 50)
    
    # Test 1: Check initial status
    print("\n1. Checking initial provider status...")
    status = api_key_manager.get_provider_status()
    for provider, info in status.items():
        print(f"   {provider}: has_key={info['has_api_key']}, valid={info['is_valid']}")
    
    # Test 2: Set test API keys (using dummy keys for testing)
    print("\n2. Setting test API keys...")
    test_keys = {
        'openai': 'sk-test-openai-key-12345',
        'anthropic': 'sk-ant-test-anthropic-key-67890',
        'deepseek': 'sk-test-deepseek-key-abcdef'
    }
    
    for provider, key in test_keys.items():
        success = api_key_manager.set_api_key(provider, key)
        print(f"   Set {provider} key: {'✅' if success else '❌'}")
    
    # Test 3: Check status after setting keys
    print("\n3. Checking status after setting keys...")
    status = api_key_manager.get_provider_status()
    for provider, info in status.items():
        print(f"   {provider}: has_key={info['has_api_key']}, valid={info['is_valid']}")
    
    # Test 4: Test API key retrieval
    print("\n4. Testing API key retrieval...")
    for provider in ['openai', 'anthropic', 'deepseek']:
        key = api_key_manager.get_api_key(provider)
        print(f"   {provider}: {'✅ Key found' if key else '❌ No key'}")
    
    # Test 5: Test enhanced AI service status
    print("\n5. Testing enhanced AI service...")
    try:
        enhanced_status = enhanced_ai_service.get_provider_status()
        print("   Enhanced AI service status:")
        for provider, info in enhanced_status.items():
            print(f"     {provider}: {info}")
    except Exception as e:
        print(f"   ❌ Enhanced AI service error: {e}")
    
    # Test 6: Test AI configuration integration
    print("\n6. Testing AI configuration integration...")
    for provider in ['openai', 'anthropic', 'deepseek']:
        key = ai_config.get_api_key(provider)
        print(f"   {provider} via ai_config: {'✅ Key found' if key else '❌ No key'}")
    
    # Test 7: Test validation (this will fail with dummy keys, but tests the flow)
    print("\n7. Testing API key validation...")
    for provider in ['openai', 'anthropic', 'deepseek']:
        try:
            is_valid, message = api_key_manager.validate_api_key(provider)
            print(f"   {provider}: {'✅' if is_valid else '❌'} - {message}")
        except Exception as e:
            print(f"   {provider}: ❌ Validation error: {e}")
    
    # Test 8: Test AI call with validation (this will fail with dummy keys)
    print("\n8. Testing AI call with validation...")
    try:
        response = await enhanced_ai_service.generate_response_with_validation(
            prompt="Hello, this is a test.",
            system_prompt="You are a helpful assistant.",
            temperature=0.7,
            max_tokens=100
        )
        print(f"   ✅ AI call successful: {response.content[:50]}...")
    except Exception as e:
        print(f"   ❌ AI call failed (expected with dummy keys): {e}")
    
    # Test 9: Test error handling
    print("\n9. Testing error handling...")
    try:
        # Try to set invalid provider
        success = api_key_manager.set_api_key('invalid_provider', 'test-key')
        print(f"   Invalid provider handling: {'✅' if not success else '❌'}")
    except Exception as e:
        print(f"   ❌ Error handling failed: {e}")
    
    # Test 10: Cleanup
    print("\n10. Cleaning up test data...")
    for provider in ['openai', 'anthropic', 'deepseek']:
        success = api_key_manager.remove_api_key(provider)
        print(f"   Removed {provider}: {'✅' if success else '❌'}")
    
    print("\n🎉 API Key Management System Test Complete!")
    print("=" * 50)


async def test_api_endpoints():
    """Test the API endpoints (requires running server)"""
    print("\n🌐 Testing API Endpoints")
    print("=" * 30)
    
    import requests
    
    base_url = "http://localhost:8000"
    
    # Test endpoints
    endpoints = [
        "/api/api-keys/status",
        "/api/api-keys/set",
        "/api/api-keys/validate/openai",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"   {endpoint}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"   {endpoint}: ❌ Connection failed - {e}")
        except Exception as e:
            print(f"   {endpoint}: ❌ Error - {e}")


if __name__ == "__main__":
    print("🚀 Starting API Key Management Tests")
    
    # Run the main test
    asyncio.run(test_api_key_management())
    
    # Test API endpoints if server is running
    try:
        asyncio.run(test_api_endpoints())
    except Exception as e:
        print(f"\n⚠️  API endpoint tests skipped: {e}")
    
    print("\n✨ All tests completed!")
