#!/usr/bin/env python3

import asyncio
import httpx
import json
from pathlib import Path

async def test_ai_extraction():
    # Load the actual prompt
    prompt_file = Path("prompt/job_extraction_prompt.txt")
    if prompt_file.exists():
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    else:
        prompt_template = """Extract job information from the following text and return ONLY valid JSON without any additional text, explanations, or markdown formatting.

REQUIRED JSON FORMAT:
{{
  "company_name": "string or null",
  "job_title": "string or null", 
  "location": "string or null",
  "experience_required": "string or null",
  "seniority_level": "string or null",
  "industry": "string or null",
  "phone_number": "string or null",
  "email": "string or null",
  "website": "string or null",
  "work_type": "string or null"
}}

IMPORTANT: Return ONLY the JSON object. Do not wrap it in markdown code blocks or add any other text.

TEXT TO ANALYZE:
{job_description}"""
    
    job_description = "Full Stack Developer at Spotify. Stockholm, Sweden. 5+ years experience in JavaScript, Python, and cloud technologies."
    prompt = prompt_template.format(job_description=job_description)
    
    # Get token
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMzY4NGU1MTAtOTYxMS00ZDdjLWE0NTgtNjRmYmFlMGE5OGJmIiwiZW1haWwiOiJkZW1vQGN2YXBwLmNvbSIsImV4cCI6MTc1NzE4MTEzMSwiaWF0IjoxNzU3MTUyMzMxLCJ0eXBlIjoiYWNjZXNzIn0.l_PxUbVYrc6ZIDSSoMG2iLxkXz4RuELPnWHoDVNXoQ8"
    
    async with httpx.AsyncClient() as client:
        print("🔍 Making AI API call...")
        print(f"🔍 Prompt length: {len(prompt)}")
        print(f"🔍 First 200 chars of prompt: {prompt[:200]}...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = await client.post(
            "http://localhost:8000/api/ai/chat",
            headers=headers,
            json={
                "prompt": prompt,
                "system_prompt": "You are a precise job information extractor. You MUST return ONLY a complete, valid JSON object without any additional text, explanations, or markdown formatting. Start with { and end with }. Never return incomplete JSON or wrap in code blocks. Use null for missing information.",
                "temperature": 0.1,
                "max_tokens": 1000
            },
            timeout=30.0
        )
        
        print(f"🔍 Response status: {response.status_code}")
        print(f"🔍 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            ai_response = response.json()
            response_text = ai_response.get("content", "")
            print(f"🔍 AI response length: {len(response_text)}")
            print(f"🔍 AI response: {repr(response_text)}")
            print(f"🔍 AI response (formatted): {response_text}")
            
            # Try to parse it
            try:
                parsed = json.loads(response_text)
                print(f"✅ JSON parsing successful: {parsed}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print(f"❌ Trying to debug the issue...")
                
                # Check if it starts/ends correctly
                print(f"❌ Starts with brace: {response_text.startswith('{')}")
                print(f"❌ Ends with brace: {response_text.endswith('}')}")
                print(f"❌ First 50 chars: {repr(response_text[:50])}")
                print(f"❌ Last 50 chars: {repr(response_text[-50:])}")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"❌ Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_ai_extraction())
