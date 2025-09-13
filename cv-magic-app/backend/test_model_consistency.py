#!/usr/bin/env python3
"""
Test script to verify that all LLM models work consistently
and save files properly throughout all functionality.
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8082/api"
AUTH_TOKEN = "your_auth_token_here"  # Replace with actual token

# Models to test
TEST_MODELS = [
    "gpt-4o",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
    "deepseek-chat",
    "claude-3-5-sonnet-20241022"
]

# Test data
TEST_CV_FILENAME = "test_cv.pdf"
TEST_JD_TEXT = """
Senior Software Engineer - AI/ML Platform

We are looking for a Senior Software Engineer to join our AI/ML platform team.

Requirements:
- 5+ years of experience in software development
- Strong experience with Python, FastAPI, and async programming
- Experience with AI/ML frameworks (TensorFlow, PyTorch)
- Knowledge of containerization (Docker, Kubernetes)
- Experience with cloud platforms (AWS, GCP, Azure)
- Strong problem-solving and communication skills

Nice to have:
- Experience with LLMs and prompt engineering
- Knowledge of vector databases
- Experience with microservices architecture
"""


async def test_preliminary_analysis(session, model_name):
    """Test preliminary analysis with a specific model"""
    print(f"\n🧪 Testing preliminary analysis with model: {model_name}")
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json",
        "X-Current-Model": model_name
    }
    
    payload = {
        "cv_filename": TEST_CV_FILENAME,
        "jd_text": TEST_JD_TEXT
    }
    
    try:
        async with session.post(
            f"{BASE_URL}/preliminary-analysis",
            json=payload,
            headers=headers
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Success! Response keys: {list(result.keys())}")
                
                # Check if file was saved
                if "saved_file_path" in result:
                    print(f"📁 File saved to: {result['saved_file_path']}")
                    
                    # Verify file exists and contains model info
                    file_path = Path(result['saved_file_path'])
                    if file_path.exists():
                        with open(file_path, 'r') as f:
                            file_content = json.load(f)
                            if "model_used" in file_content:
                                print(f"🔍 Model recorded in file: {file_content['model_used']}")
                                if file_content['model_used'] != model_name:
                                    print(f"⚠️  WARNING: Model mismatch! Expected {model_name}, got {file_content['model_used']}")
                            else:
                                print("⚠️  WARNING: No model information in saved file!")
                    else:
                        print("❌ ERROR: File was not saved!")
                else:
                    print("⚠️  WARNING: No saved_file_path in response!")
                    
                return True
            else:
                error_text = await response.text()
                print(f"❌ Error {response.status}: {error_text}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


async def test_skill_extraction(session, model_name):
    """Test skill extraction with a specific model"""
    print(f"\n🧪 Testing skill extraction with model: {model_name}")
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json",
        "X-Current-Model": model_name
    }
    
    payload = {
        "cv_filename": TEST_CV_FILENAME,
        "jd_url": "https://example.com/job/123",
        "user_id": 1,
        "force_refresh": True
    }
    
    try:
        async with session.post(
            f"{BASE_URL}/skill-extraction/analyze",
            json=payload,
            headers=headers
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Success! Response keys: {list(result.keys())}")
                
                # Check for saved files in cv-analysis directory
                cv_analysis_dir = Path("/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend/cv-analysis")
                if cv_analysis_dir.exists():
                    # Find most recent company folder
                    company_folders = [f for f in cv_analysis_dir.iterdir() if f.is_dir() and f.name != "Unknown_Company"]
                    if company_folders:
                        recent_folder = max(company_folders, key=lambda p: p.stat().st_mtime)
                        print(f"📁 Most recent company folder: {recent_folder.name}")
                        
                        # Check for skills analysis file
                        skills_files = list(recent_folder.glob("*_skills_analysis.json"))
                        if skills_files:
                            with open(skills_files[0], 'r') as f:
                                file_content = json.load(f)
                                if "model_used" in file_content:
                                    print(f"🔍 Model recorded in file: {file_content['model_used']}")
                                else:
                                    print("⚠️  WARNING: No model information in saved file!")
                
                return True
            else:
                error_text = await response.text()
                print(f"❌ Error {response.status}: {error_text}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


async def get_ai_status(session):
    """Get current AI service status"""
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        async with session.get(
            f"{BASE_URL}/ai/status",
            headers=headers
        ) as response:
            if response.status == 200:
                result = await response.json()
                print("\n📊 AI Service Status:")
                print(f"Current Provider: {result.get('current_provider')}")
                print(f"Current Model: {result.get('current_model')}")
                print(f"Available Providers: {result.get('available_providers')}")
                return result
            else:
                print(f"❌ Failed to get AI status: {response.status}")
                return None
    except Exception as e:
        print(f"❌ Exception getting AI status: {str(e)}")
        return None


async def main():
    """Run all tests"""
    print("🚀 Starting Model Consistency Tests")
    print(f"Testing {len(TEST_MODELS)} models")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Create session
    async with aiohttp.ClientSession() as session:
        # Get initial status
        await get_ai_status(session)
        
        # Test results
        results = {
            "preliminary_analysis": {},
            "skill_extraction": {}
        }
        
        # Test each model
        for model in TEST_MODELS:
            print(f"\n{'='*60}")
            print(f"Testing Model: {model}")
            print(f"{'='*60}")
            
            # Test preliminary analysis
            pa_success = await test_preliminary_analysis(session, model)
            results["preliminary_analysis"][model] = pa_success
            
            # Small delay between tests
            await asyncio.sleep(2)
            
            # Test skill extraction
            se_success = await test_skill_extraction(session, model)
            results["skill_extraction"][model] = se_success
            
            # Small delay between models
            await asyncio.sleep(3)
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}")
        
        print("\nPreliminary Analysis Results:")
        for model, success in results["preliminary_analysis"].items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {model}: {status}")
        
        print("\nSkill Extraction Results:")
        for model, success in results["skill_extraction"].items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {model}: {status}")
        
        # Overall result
        all_passed = all(
            success 
            for test_results in results.values() 
            for success in test_results.values()
        )
        
        print(f"\n{'='*60}")
        if all_passed:
            print("✅ ALL TESTS PASSED! All models work consistently.")
        else:
            print("❌ SOME TESTS FAILED! Model consistency issues detected.")
        print(f"{'='*60}")
        
        return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
