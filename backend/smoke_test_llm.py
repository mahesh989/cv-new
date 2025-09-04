#!/usr/bin/env python3
"""
Smoke test for LLM client with new Claude 3.5 Sonnet model.
Tests both the HybridAIService and direct Anthropic client calls.
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hybrid_ai_service import HybridAIService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_hybrid_ai_service():
    """Test the HybridAIService with the new model."""
    print("🔬 Testing HybridAIService...")
    
    # Initialize service
    ai_service = HybridAIService()
    
    # Get service status
    status = ai_service.get_status()
    print(f"✅ Service Status: {json.dumps(status, indent=2)}")
    
    # Test prompt
    test_prompt = "Hello! Please respond with a brief message confirming you are working correctly."
    
    # Test with the new Claude 3.5 Sonnet model
    new_model = "claude-3-5-sonnet-20241022"
    
    try:
        print(f"\n🧪 Testing with new Claude model: {new_model}")
        response = ai_service.generate_response(
            prompt=test_prompt,
            provider="claude",
            model=new_model,
            temperature=0.3,
            max_tokens=100
        )
        print(f"✅ SUCCESS: Claude model {new_model} responded successfully!")
        print(f"📝 Response: {response}")
        return True
    except Exception as e:
        print(f"❌ ERROR: Claude model {new_model} failed - {str(e)}")
        return False

def test_openai_models():
    """Test OpenAI models through HybridAIService."""
    print("\n🔬 Testing OpenAI models...")
    
    ai_service = HybridAIService()
    test_prompt = "Hello! Please respond with a brief message confirming you are working correctly."
    
    openai_models = [
        "gpt-4o",
        "gpt-4o-mini", 
        "gpt-3.5-turbo",
        "gpt-4"
    ]
    
    successful_models = []
    
    for model in openai_models:
        try:
            print(f"🧪 Testing OpenAI model: {model}")
            response = ai_service.generate_response(
                prompt=test_prompt,
                provider="openai",
                model=model,
                temperature=0.3,
                max_tokens=100
            )
            print(f"✅ SUCCESS: OpenAI model {model} worked!")
            print(f"📝 Response: {response[:100]}...")
            successful_models.append(model)
        except Exception as e:
            print(f"❌ ERROR: OpenAI model {model} failed - {str(e)}")
    
    return successful_models

def test_direct_anthropic_client():
    """Test direct Anthropic client with the new model."""
    print("\n🔬 Testing direct Anthropic client...")
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key or anthropic_key == "your_claude_api_key_here":
        print("❌ ANTHROPIC_API_KEY not found or placeholder value")
        return False
    
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=anthropic_key)
        
        # Test with the new model
        new_model = "claude-3-5-sonnet-20241022"
        
        print(f"🧪 Testing direct call with model: {new_model}")
        response = client.messages.create(
            model=new_model,
            max_tokens=100,
            temperature=0.3,
            messages=[{
                "role": "user", 
                "content": "Hello! Please respond with a brief message confirming you are working correctly."
            }]
        )
        
        response_text = response.content[0].text.strip()
        print(f"✅ SUCCESS: Direct Anthropic client with {new_model} worked!")
        print(f"📝 Response: {response_text}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Direct Anthropic client failed - {str(e)}")
        return False

def test_fallback_models():
    """Test fallback to older models if new one fails."""
    print("\n🔬 Testing fallback models...")
    
    ai_service = HybridAIService()
    test_prompt = "Hello! Please respond with a brief message confirming you are working correctly."
    
    fallback_models = [
        "claude-3-5-sonnet-20241022",  # Updated default
        "claude-3-haiku-20240307"    # Lightweight option
    ]
    
    successful_models = []
    
    for model in fallback_models:
        try:
            print(f"🧪 Testing fallback model: {model}")
            response = ai_service.generate_response(
                prompt=test_prompt,
                provider="claude",
                model=model,
                temperature=0.3,
                max_tokens=100
            )
            print(f"✅ SUCCESS: Fallback model {model} worked!")
            successful_models.append(model)
        except Exception as e:
            print(f"❌ ERROR: Fallback model {model} failed - {str(e)}")
    
    return successful_models

def main():
    """Run all smoke tests."""
    print("🚀 Starting LLM Client Smoke Tests")
    print("=" * 50)
    
    # Test results
    results = {
        "hybrid_ai_service": False,
        "direct_anthropic": False,
        "openai_models": [],
        "fallback_models": []
    }
    
    # Run tests
    results["hybrid_ai_service"] = test_hybrid_ai_service()
    results["openai_models"] = test_openai_models()
    results["direct_anthropic"] = test_direct_anthropic_client()
    results["fallback_models"] = test_fallback_models()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    if results["hybrid_ai_service"]:
        print("✅ HybridAIService with new Claude model: PASSED")
    else:
        print("❌ HybridAIService with new Claude model: FAILED")
    
    if results["openai_models"]:
        print(f"✅ OpenAI models working: {', '.join(results['openai_models'])}")
    else:
        print("❌ No OpenAI models working")
    
    if results["direct_anthropic"]:
        print("✅ Direct Anthropic client with new model: PASSED")
    else:
        print("❌ Direct Anthropic client with new model: FAILED")
    
    if results["fallback_models"]:
        print(f"✅ Claude fallback models working: {', '.join(results['fallback_models'])}")
    else:
        print("❌ No Claude fallback models working")
    
    # Overall result
    overall_success = (results["hybrid_ai_service"] or 
                      results["direct_anthropic"] or 
                      len(results["openai_models"]) > 0 or
                      len(results["fallback_models"]) > 0)
    
    if overall_success:
        print("\n🎉 OVERALL: At least one model configuration is working!")
        return 0
    else:
        print("\n💥 OVERALL: All model configurations failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
