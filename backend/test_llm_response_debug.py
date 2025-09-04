#!/usr/bin/env python3
"""
Debug script to test LLM response parsing
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.analysis_results_saver import AnalysisResultsSaver

def test_llm_response_debug():
    """Test LLM response parsing directly"""
    print("🔍 Testing LLM Response Parsing...")
    
    # Find the most recent analysis file
    analysis_dir = "analysis_results"
    analysis_files = [f for f in os.listdir(analysis_dir) if f.endswith('.txt')]
    analysis_files.sort(key=lambda x: os.path.getmtime(os.path.join(analysis_dir, x)), reverse=True)
    latest_file = analysis_files[0]
    filepath = os.path.join(analysis_dir, latest_file)
    
    print(f"📁 Using analysis file: {filepath}")
    
    # Initialize saver with debug
    saver = AnalysisResultsSaver(debug=True)
    
    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found")
        return
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    try:
        # Read the analysis file
        with open(filepath, 'r', encoding='utf-8') as f:
            analysis_content = f.read()
        
        print(f"📊 Analysis content length: {len(analysis_content)} characters")
        
        # Create prompt
        prompt = saver._create_recommendation_prompt(analysis_content)
        print(f"📝 Prompt length: {len(prompt)} characters")
        
        # Initialize LLM client
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        print("🚀 Sending request to Claude...")
        
        # Get LLM recommendations
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.1,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        llm_response = response.content[0].text
        print(f"📄 LLM Response length: {len(llm_response)} characters")
        print(f"📄 LLM Response preview: {llm_response[:500]}...")
        
        # Try to parse the response
        print("\n🔍 Attempting to parse LLM response...")
        recommendations = saver._parse_llm_recommendations(llm_response)
        
        print(f"✅ Parsing successful!")
        print(f"📊 Recommendations keys: {list(recommendations.keys())}")
        
        # Check if we got the expected structure
        expected_keys = ['cv_improvements', 'keyword_optimizations', 'experience_enhancements', 
                        'project_additions', 'certification_recommendations', 'section_optimizations',
                        'score_projection', 'priority_actions', 'overall_cv_strategy']
        
        for key in expected_keys:
            if key in recommendations:
                print(f"✅ Found key: {key}")
            else:
                print(f"❌ Missing key: {key}")
        
        # Print a sample of the recommendations
        if 'cv_improvements' in recommendations and recommendations['cv_improvements']:
            print(f"\n📝 Sample CV improvement:")
            print(json.dumps(recommendations['cv_improvements'][0], indent=2))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_response_debug() 