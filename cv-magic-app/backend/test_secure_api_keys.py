#!/usr/bin/env python3
"""
Test script for the secure user-specific API key system

This script tests the new user-specific API key storage and retrieval functionality.
"""

import os
import sys
import asyncio
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.auth import UserData
from app.services.user_api_key_manager import user_api_key_manager


async def test_user_api_key_system():
    """Test the user-specific API key system"""
    
    print("🔐 Testing Secure User-Specific API Key System")
    print("=" * 50)
    
    # Create a test user
    test_user = UserData(
        id="test-user-123",
        email="test@example.com",
        name="Test User",
        created_at=datetime.now(),
        is_active=True
    )
    
    print(f"📧 Test User: {test_user.email} (ID: {test_user.id})")
    
    # Test 1: Set API key
    print("\n1️⃣ Testing API Key Storage...")
    test_api_key = "sk-test-key-12345"
    success, message = user_api_key_manager.set_api_key(test_user, "openai", test_api_key)
    
    if success:
        print(f"✅ API key stored successfully: {message}")
    else:
        print(f"❌ Failed to store API key: {message}")
        return
    
    # Test 2: Retrieve API key
    print("\n2️⃣ Testing API Key Retrieval...")
    retrieved_key = user_api_key_manager.get_api_key(test_user, "openai")
    
    if retrieved_key == test_api_key:
        print("✅ API key retrieved successfully and matches original")
    else:
        print(f"❌ Retrieved key doesn't match. Expected: {test_api_key}, Got: {retrieved_key}")
        return
    
    # Test 3: Check if key exists
    print("\n3️⃣ Testing Key Existence Check...")
    has_key = user_api_key_manager.has_api_key(test_user, "openai")
    
    if has_key:
        print("✅ Key existence check passed")
    else:
        print("❌ Key existence check failed")
        return
    
    # Test 4: Get provider status
    print("\n4️⃣ Testing Provider Status...")
    status = user_api_key_manager.get_provider_status(test_user)
    
    if "openai" in status and status["openai"]["has_api_key"]:
        print("✅ Provider status check passed")
        print(f"   - Has API key: {status['openai']['has_api_key']}")
        print(f"   - Is valid: {status['openai']['is_valid']}")
    else:
        print("❌ Provider status check failed")
        return
    
    # Test 5: Update API key
    print("\n5️⃣ Testing API Key Update...")
    new_api_key = "sk-updated-key-67890"
    success, message = user_api_key_manager.set_api_key(test_user, "openai", new_api_key)
    
    if success:
        print(f"✅ API key updated successfully: {message}")
        
        # Verify the update
        updated_key = user_api_key_manager.get_api_key(test_user, "openai")
        if updated_key == new_api_key:
            print("✅ Updated key retrieved successfully")
        else:
            print(f"❌ Updated key doesn't match. Expected: {new_api_key}, Got: {updated_key}")
    else:
        print(f"❌ Failed to update API key: {message}")
    
    # Test 6: Test multiple providers
    print("\n6️⃣ Testing Multiple Providers...")
    providers = ["anthropic", "deepseek"]
    
    for provider in providers:
        test_key = f"sk-{provider}-test-key"
        success, message = user_api_key_manager.set_api_key(test_user, provider, test_key)
        
        if success:
            print(f"✅ {provider} key stored successfully")
        else:
            print(f"❌ Failed to store {provider} key: {message}")
    
    # Test 7: Final status check
    print("\n7️⃣ Final Status Check...")
    final_status = user_api_key_manager.get_provider_status(test_user)
    
    print("📊 Final Provider Status:")
    for provider, data in final_status.items():
        print(f"   - {provider}: {'✅' if data['has_api_key'] else '❌'} "
              f"(Valid: {'✅' if data['is_valid'] else '❌'})")
    
    # Test 8: Remove API key
    print("\n8️⃣ Testing API Key Removal...")
    success, message = user_api_key_manager.remove_api_key(test_user, "openai")
    
    if success:
        print(f"✅ API key removed successfully: {message}")
        
        # Verify removal
        has_key_after_removal = user_api_key_manager.has_api_key(test_user, "openai")
        if not has_key_after_removal:
            print("✅ Key removal verified")
        else:
            print("❌ Key still exists after removal")
    else:
        print(f"❌ Failed to remove API key: {message}")
    
    # Test 9: Clear all keys
    print("\n9️⃣ Testing Clear All Keys...")
    success, message = user_api_key_manager.clear_all_keys(test_user)
    
    if success:
        print(f"✅ All keys cleared successfully: {message}")
        
        # Verify all keys are cleared
        final_status = user_api_key_manager.get_provider_status(test_user)
        all_cleared = all(not data['has_api_key'] for data in final_status.values())
        
        if all_cleared:
            print("✅ All keys cleared verified")
        else:
            print("❌ Some keys still exist after clearing")
    else:
        print(f"❌ Failed to clear all keys: {message}")
    
    print("\n🎉 User-Specific API Key System Test Complete!")
    print("=" * 50)


def test_encryption():
    """Test the encryption functionality"""
    print("\n🔒 Testing Encryption System...")
    
    try:
        from app.models.user_api_keys import UserAPIKey
        
        # Create a test API key instance
        test_key = UserAPIKey(
            user_id="test-user-123",
            provider="test",
            api_key="sk-test-encryption-key-12345"
        )
        
        # Test encryption/decryption
        encrypted = test_key.encrypted_key
        decrypted = test_key.get_api_key()
        
        if decrypted == "sk-test-encryption-key-12345":
            print("✅ Encryption/Decryption test passed")
        else:
            print(f"❌ Encryption/Decryption test failed. Expected: sk-test-encryption-key-12345, Got: {decrypted}")
        
        # Test key hashing
        original_hash = test_key.key_hash
        test_key.update_api_key("sk-new-test-key-67890")
        new_hash = test_key.key_hash
        
        if original_hash != new_hash:
            print("✅ Key hashing test passed")
        else:
            print("❌ Key hashing test failed - hashes should be different")
            
    except Exception as e:
        print(f"❌ Encryption test failed with error: {e}")


if __name__ == "__main__":
    print("🚀 Starting Secure API Key System Tests...")
    
    # Test encryption first
    test_encryption()
    
    # Test the full system
    try:
        asyncio.run(test_user_api_key_system())
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✨ All tests completed!")
