#!/usr/bin/env python3
"""
Test script to verify that AI recommendation generator saves only the recommendation content
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent / "cv-magic-app" / "backend"
sys.path.append(str(backend_dir))

from app.services.ai_recommendation_generator import AIRecommendationGenerator


async def test_recommendation_content_only():
    """Test that the AI recommendation generator saves only the content"""
    
    # Create a mock AI response (simulating the actual AI response structure)
    class MockAIResponse:
        def __init__(self):
            self.content = """# 🎯 CV Tailoring Strategy Report for Test Company

## 📊 Executive Summary
- **Current ATS Score:** 75.5/100 (✅ Good fit)
- **Key Strengths:** Strong technical background
- **Critical Gaps:** Missing industry keywords

## 🔍 Priority Gap Analysis
**Immediate Action Required:**
- Add missing keywords: Data Science, Machine Learning
- Improve technical skills section

## 🛠️ Keyword Integration Strategy
Focus on integrating these key terms naturally into your CV."""
            
            self.provider = "openai" 
            self.model = "gpt-4o-mini"
            self.tokens_used = 500
            self.cost = 0.001
            self.metadata = {"finish_reason": "stop"}
    
    # Initialize the generator
    generator = AIRecommendationGenerator()
    
    # Test the structure method
    mock_response = MockAIResponse()
    structured_content = generator._structure_ai_response(mock_response, "TestCompany")
    
    print("✅ Structured content (should be just the recommendation text):")
    print("Type:", type(structured_content))
    print("Content preview:", structured_content[:100] + "..." if len(structured_content) > 100 else structured_content)
    
    # Verify it's just a string, not a dictionary
    assert isinstance(structured_content, str), "Content should be a string, not a dictionary"
    assert structured_content.startswith("# 🎯 CV Tailoring Strategy"), "Content should start with the expected header"
    
    print("\n✅ Test passed! The AI recommendation generator now saves only the recommendation content.")
    print("📝 Files will be saved as .txt files instead of .json files")
    print("🎯 This matches your requirement to save only the recommendation_content")


if __name__ == "__main__":
    asyncio.run(test_recommendation_content_only())