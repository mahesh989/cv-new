#!/usr/bin/env python3

import requests
import json
import time

# Test the ATS endpoint
def test_ats_endpoint():
    base_url = "http://localhost:8000"
    
    # Test data
    test_payload = {
        "cv_filename": "maheshwor_tiwari.pdf"  # This should exist in uploads folder
    }
    
    print("🚀 Testing ATS Rules Engine...")
    print(f"📄 Testing with CV: {test_payload['cv_filename']}")
    print("-" * 50)
    
    try:
        # Test the unified extractor endpoint
        response = requests.post(
            f"{base_url}/test-unified-extractor/",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ATS Evaluation Successful!")
            print(f"📊 Overall Score: {result.get('overall_score', 'N/A')}")
            print(f"🎯 Status: {result.get('status', 'N/A')}")
            print(f"📈 Compatibility: {result.get('compatibility_level', 'N/A')}")
            
            # Show skill breakdown
            skills = result.get('skills', {})
            if skills:
                print("\n🔧 Skills Analysis:")
                for category, score in skills.items():
                    print(f"  {category}: {score}")
            
            # Show recommendations
            recommendations = result.get('recommendations', [])
            if recommendations:
                print("\n💡 Recommendations:")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"  {i}. {rec}")
                    
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_ats_endpoint() 