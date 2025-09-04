#!/usr/bin/env python3
"""
LLM Company Extraction Demo - Show intelligent extraction capabilities
=====================================================================
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analysis_results_saver import AnalysisResultsSaver

def test_llm_extraction_demo():
    """Demo of LLM-based company information extraction"""
    
    print("🤖 LLM-BASED COMPANY INFORMATION EXTRACTION DEMO")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "EthicalJobs - No To Violence",
            "jd": """Data Analyst

No To Violence 

Job Summary

About us
No to Violence is Australia's largest peak body for services and individuals that work with men who use family violence.

Melbourne > CBD & Inner Suburbs Melbourne
Contract, Full Time

The Data Analyst will be responsible for analysing data sets and reporting using different methodologies and business analytical tools."""
        },
        {
            "name": "Google Standard Format",
            "jd": """Software Engineer at Google

Join our team at Google's Sydney office to build innovative solutions that impact billions of users worldwide. 

Location: Sydney, Australia
Contact: +61 2 9374 4000

We are looking for talented engineers who are passionate about technology."""
        },
        {
            "name": "Microsoft with Phone",
            "jd": """Product Manager - Microsoft Corporation

Microsoft Australia is seeking a Product Manager to drive product strategy and development.

Location: Melbourne, Victoria
Phone: 13 20 58

Work with Microsoft teams to deliver cutting-edge solutions."""
        }
    ]
    
    saver = AnalysisResultsSaver()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i}: {test_case['name']}")
        print("-" * 50)
        
        # Extract company information using LLM
        company_name = saver.extract_company_name(test_case['jd'])
        
        print(f"📁 Generated filename: {company_name}_output_log.txt")
        print()

if __name__ == "__main__":
    test_llm_extraction_demo() 