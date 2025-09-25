#!/usr/bin/env python3
"""
Test script to verify model switching functionality
"""

import asyncio
import logging
from app.ai.ai_service import ai_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_model_switching():
    """Test that model switching works correctly across different providers"""
    
    print("🔬 Testing Model Switching Functionality")
    print("=" * 50)
    
    # Test 1: Check initial status
    print("\n1️⃣ Initial AI Service Status:")
    status = ai_service.get_current_status()
    print(f"   Current Provider: {status['current_provider']}")
    print(f"   Current Model: {status['current_model']}")
    print(f"   Available Providers: {status['available_providers']}")
    
    # Test 2: Try switching to different models
    test_models = [
        "gpt-4o-mini",
        "deepseek-chat", 
        "claude-3-5-sonnet-20241022",
        "gpt-4o"
    ]
    
    print(f"\n2️⃣ Testing Model Switching:")
    for model in test_models:
        print(f"\n   Testing switch to: {model}")
        success = ai_service.switch_model(model)
        if success:
            current_model = ai_service.get_current_model_name()
            print(f"   ✅ Successfully switched to: {current_model}")
            
            # Test a simple AI call
            try:
                response = await ai_service.generate_response(
                    prompt="Say 'Hello from' followed by your model name",
                    temperature=0.1,
                    max_tokens=50
                )
                print(f"   🤖 AI Response: {response.content[:100]}...")
                print(f"   📊 Model Used: {response.model}")
                print(f"   🏭 Provider: {response.provider}")
            except Exception as e:
                print(f"   ❌ AI call failed: {e}")
        else:
            print(f"   ❌ Failed to switch to: {model}")
    
    # Test 3: Check final status
    print(f"\n3️⃣ Final Status:")
    final_status = ai_service.get_current_status()
    print(f"   Final Provider: {final_status['current_provider']}")
    print(f"   Final Model: {final_status['current_model']}")
    
    print("\n✅ Model switching test completed!")

if __name__ == "__main__":
    asyncio.run(test_model_switching())
