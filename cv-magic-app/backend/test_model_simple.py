#!/usr/bin/env python3
"""
Simple test to verify model consistency - saves results for each model
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8082/api"
AUTH_TOKEN = "your-token-here"  # Replace with your actual token

# Test with these models
MODELS_TO_TEST = ["gpt-4o", "gpt-4-turbo", "deepseek-chat"]

# Simple test data
TEST_DATA = {
    "cv_filename": "test_cv.pdf",
    "jd_text": "Software Engineer position requiring Python, FastAPI, and AI/ML experience."
}

def test_model(model_name):
    """Test a single model and return results"""
    print(f"\n{'='*50}")
    print(f"Testing model: {model_name}")
    print(f"{'='*50}")
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json",
        "X-Current-Model": model_name
    }
    
    # Make request
    response = requests.post(
        f"{BASE_URL}/preliminary-analysis",
        json=TEST_DATA,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        
        # Check if file was saved
        if "saved_file_path" in result:
            print(f"📁 File saved to: {result['saved_file_path']}")
            
            # Read the file to check model info
            try:
                with open(result['saved_file_path'], 'r') as f:
                    file_data = json.load(f)
                    if "model_used" in file_data:
                        print(f"🔍 Model in file: {file_data['model_used']}")
                        if file_data['model_used'] == model_name:
                            print("✅ Model correctly recorded!")
                        else:
                            print(f"❌ Model mismatch! Expected {model_name}, got {file_data['model_used']}")
                    else:
                        print("❌ No model information in file!")
            except Exception as e:
                print(f"❌ Error reading file: {e}")
        else:
            print("❌ No file was saved!")
            
        # Show skill counts
        if "cv_skills" in result:
            cv_skills = result["cv_skills"]
            print(f"\nExtracted CV skills:")
            print(f"  - Technical: {len(cv_skills.get('technical_skills', []))}")
            print(f"  - Soft: {len(cv_skills.get('soft_skills', []))}")
            print(f"  - Domain: {len(cv_skills.get('domain_keywords', []))}")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

def main():
    print("🚀 Model Consistency Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test each model
    for model in MODELS_TO_TEST:
        test_model(model)
        print()  # Blank line between tests
    
    print("\n✅ Test complete! Check the output above to verify:")
    print("1. Each model successfully processes the request")
    print("2. Files are saved for each model")
    print("3. The correct model name is recorded in each file")

if __name__ == "__main__":
    main()
