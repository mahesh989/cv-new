#!/usr/bin/env python3
"""
Test script to debug prompt construction for CV tailoring
"""
import json
import sys
import os

# Add the backend directory to Python path
sys.path.append('/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend')

from app.tailored_cv.services.recommendation_parser import RecommendationParser
from app.tailored_cv.services.cv_tailoring_service import CVTailoringService
from app.tailored_cv.models.cv_models import OriginalCV, RecommendationAnalysis

def test_prompt_construction():
    """Test the prompt construction to see what data is being sent to AI"""
    print("🔍 Testing prompt construction...")
    
    try:
        # Load real CV and recommendation data
        cv_tailoring_service = CVTailoringService()
        original_cv, recommendation = cv_tailoring_service.load_real_cv_and_recommendation("Australia_for_UNHCR")
        
        print(f"📄 Loaded CV for: {original_cv.contact.name}")
        print(f"📄 CV has {len(original_cv.experience)} experience entries")
        print(f"📄 First company: {original_cv.experience[0].company if original_cv.experience else 'No experience'}")
        
        # Get optimization strategy
        strategy = cv_tailoring_service._determine_optimization_strategy(original_cv, recommendation)
        
        # Build the user prompt
        user_prompt = cv_tailoring_service._build_user_prompt(
            original_cv, 
            recommendation, 
            strategy, 
            None
        )
        
        print(f"\n📝 User prompt length: {len(user_prompt)} characters")
        print(f"📝 First 500 characters of prompt:")
        print(user_prompt[:500])
        print("...")
        print(f"📝 Last 200 characters of prompt:")
        print(user_prompt[-200:])
        
        # Check if the real CV data is in the prompt
        if "Maheshwor Tiwari" in user_prompt:
            print("\n✅ Real CV name found in prompt")
        else:
            print("\n❌ Real CV name NOT found in prompt")
            
        if "The Bitrates" in user_prompt:
            print("✅ Real company name found in prompt")
        else:
            print("❌ Real company name NOT found in prompt")
        
    except Exception as e:
        print(f"❌ Error testing prompt construction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_prompt_construction()