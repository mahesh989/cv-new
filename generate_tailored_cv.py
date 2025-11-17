#!/usr/bin/env python3
"""
Script to generate tailored CV for Australia_for_UNHCR
"""
import sys
import os
sys.path.append('/app')

from app.tailored_cv.services.cv_tailoring_service import CVTailoringService
from app.tailored_cv.models.cv_models import CVTailoringRequest
import asyncio
import json

async def generate_tailored_cv():
    """Generate tailored CV for Australia_for_UNHCR"""
    try:
        print("🎯 Starting tailored CV generation for Australia_for_UNHCR...")
        
        # Create service instance
        cv_service = CVTailoringService(user_email="maheshwor@gmail.com")
        
        # Check available companies
        available_companies = cv_service.list_available_companies()
        print(f"📋 Available companies: {available_companies}")
        
        if "Australia_for_UNHCR" not in available_companies:
            print(f"❌ Australia_for_UNHCR not found in available companies")
            return
        
        # Load real CV and recommendation data
        print("📄 Loading real CV and recommendation data...")
        original_cv, recommendation = cv_service.load_real_cv_and_recommendation("Australia_for_UNHCR")
        print(f"✅ Loaded real data for Australia_for_UNHCR")
        
        # Create tailoring request
        request = CVTailoringRequest(
            original_cv=original_cv,
            recommendations=recommendation,
            custom_instructions=None,
            company_folder=None
        )
        
        # Process the CV tailoring
        print("🤖 Generating tailored CV with AI...")
        response = await cv_service.tailor_cv(request)
        
        if response.success:
            print("✅ Tailored CV generated successfully!")
            print(f"📊 Processing summary: {response.processing_summary}")
            
            # Save tailored CV to analysis folder
            file_path = cv_service.save_tailored_cv_to_analysis_folder(response.tailored_cv, "Australia_for_UNHCR")
            print(f"💾 Tailored CV saved to: {file_path}")
            
            return True
        else:
            print(f"❌ Tailored CV generation failed: {response.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Error generating tailored CV: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(generate_tailored_cv())
    if success:
        print("🎉 Tailored CV generation completed successfully!")
    else:
        print("💥 Tailored CV generation failed!")
        sys.exit(1)
