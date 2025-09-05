#!/usr/bin/env python3
"""
Test script for LLM recommendation generation from saved analysis files
"""

import requests
import json
import os
from datetime import datetime

def test_recommendations_generation():
    """Test the recommendations generation endpoint"""
    print("🧪 Testing LLM Recommendations Generation...")
    
    # Find the most recent analysis file
    analysis_dir = "analysis_results"
    if not os.path.exists(analysis_dir):
        print("❌ No analysis_results directory found")
        return
    
    # Get the most recent analysis file
    analysis_files = [f for f in os.listdir(analysis_dir) if f.endswith('.txt')]
    if not analysis_files:
        print("❌ No analysis files found")
        return
    
    # Sort by modification time (most recent first)
    analysis_files.sort(key=lambda x: os.path.getmtime(os.path.join(analysis_dir, x)), reverse=True)
    latest_file = analysis_files[0]
    filepath = os.path.join(analysis_dir, latest_file)
    
    print(f"📁 Using analysis file: {filepath}")
    print(f"📊 File size: {os.path.getsize(filepath)} bytes")
    
    # Test the recommendations endpoint
    url = "http://localhost:8000/api/generate-recommendations"
    
    payload = {
        "analysis_filepath": filepath
    }
    
    try:
        print(f"🚀 Sending request to: {url}")
        response = requests.post(url, json=payload, timeout=60)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Recommendations generated successfully!")
            print(f"📁 Source file: {result.get('source_file', 'Unknown')}")
            
            # Print recommendations summary
            recommendations = result.get('recommendations', {})
            
            print("\n" + "="*60)
            print("📝 CV IMPROVEMENT RECOMMENDATIONS")
            print("="*60)
            
            # CV Improvements
            cv_improvements = recommendations.get('cv_improvements', [])
            print(f"\n🔧 CV SECTIONS TO MODIFY ({len(cv_improvements)}):")
            for i, improvement in enumerate(cv_improvements, 1):
                print(f"  {i}. Section: {improvement.get('section', 'N/A')}")
                print(f"     Current: {improvement.get('current_content', 'N/A')}")
                changes = improvement.get('recommended_changes', [])
                print(f"     Changes:")
                for change in changes:
                    print(f"       • {change}")
                print(f"     Expected Impact: {improvement.get('expected_score_impact', 'N/A')}")
                print(f"     Priority: {improvement.get('priority', 'N/A')}")
                print(f"     Timeline: {improvement.get('timeline', 'N/A')}")
                print()
            
            # Keyword Optimizations
            keyword_optimizations = recommendations.get('keyword_optimizations', [])
            print(f"🎯 KEYWORD OPTIMIZATIONS ({len(keyword_optimizations)}):")
            for i, opt in enumerate(keyword_optimizations, 1):
                missing = opt.get('missing_keywords', [])
                synonyms = opt.get('synonyms_to_add', [])
                placement = opt.get('placement', 'N/A')
                print(f"  {i}. Missing Keywords: {', '.join(missing)}")
                print(f"     Synonyms to Add: {', '.join(synonyms)}")
                print(f"     Placement: {placement}")
                print()
            
            # Experience Enhancements
            experience_enhancements = recommendations.get('experience_enhancements', [])
            print(f"💼 EXPERIENCE ENHANCEMENTS ({len(experience_enhancements)}):")
            for i, enhancement in enumerate(experience_enhancements, 1):
                print(f"  {i}. Section: {enhancement.get('section', 'N/A')}")
                print(f"     Current: {enhancement.get('current_description', 'N/A')}")
                print(f"     Enhanced: {enhancement.get('enhanced_description', 'N/A')}")
                keywords = enhancement.get('keywords_added', [])
                print(f"     Keywords Added: {', '.join(keywords)}")
                print(f"     Score Impact: {enhancement.get('score_impact', 'N/A')}")
                print()
            
            # Project Additions
            project_additions = recommendations.get('project_additions', [])
            print(f"🚀 PROJECT ADDITIONS ({len(project_additions)}):")
            for i, project in enumerate(project_additions, 1):
                print(f"  {i}. Project: {project.get('project_name', 'N/A')}")
                print(f"     Description: {project.get('description', 'N/A')}")
                skills = project.get('skills_demonstrated', [])
                print(f"     Skills Demonstrated: {', '.join(skills)}")
                print(f"     Score Impact: {project.get('score_impact', 'N/A')}")
                print()
            
            # Certification Recommendations
            certification_recommendations = recommendations.get('certification_recommendations', [])
            print(f"🏆 CERTIFICATION RECOMMENDATIONS ({len(certification_recommendations)}):")
            for i, cert in enumerate(certification_recommendations, 1):
                print(f"  {i}. Certification: {cert.get('certification', 'N/A')}")
                print(f"     Timeline: {cert.get('timeline', 'N/A')}")
                print(f"     Score Impact: {cert.get('score_impact', 'N/A')}")
                print(f"     Urgency: {cert.get('urgency', 'N/A')}")
                print(f"     Reasoning: {cert.get('reasoning', 'N/A')}")
                print()
            
            # Section Optimizations
            section_optimizations = recommendations.get('section_optimizations', [])
            print(f"📋 SECTION OPTIMIZATIONS ({len(section_optimizations)}):")
            for i, opt in enumerate(section_optimizations, 1):
                print(f"  {i}. Section: {opt.get('section', 'N/A')}")
                print(f"     Current: {opt.get('current', 'N/A')}")
                print(f"     Optimized: {opt.get('optimized', 'N/A')}")
                keywords = opt.get('keywords_added', [])
                print(f"     Keywords Added: {', '.join(keywords)}")
                print(f"     Score Impact: {opt.get('score_impact', 'N/A')}")
                print()
            
            # Priority Actions
            priority_actions = recommendations.get('priority_actions', [])
            print(f"⚡ PRIORITY ACTIONS ({len(priority_actions)}):")
            for i, action in enumerate(priority_actions, 1):
                print(f"  {i}. {action.get('action', 'N/A')}")
                print(f"     Timeline: {action.get('timeline', 'N/A')}")
                print(f"     Urgency: {action.get('urgency', 'N/A')}")
                print(f"     Expected Impact: {action.get('expected_impact', 'N/A')}")
                implementation = action.get('implementation', 'N/A')
                if implementation != 'N/A':
                    print(f"     Implementation: {implementation}")
                print()
            
            # Score Projection
            score_projection = recommendations.get('score_projection', {})
            print(f"📈 SCORE PROJECTION:")
            print(f"     Current Score: {score_projection.get('current_score', 'N/A')}")
            print(f"     Projected Score: {score_projection.get('projected_score', 'N/A')}")
            print(f"     Timeline: {score_projection.get('improvement_timeline', 'N/A')}")
            
            key_improvements = score_projection.get('key_improvements', [])
            if key_improvements:
                print(f"     Key Improvements:")
                for improvement in key_improvements:
                    print(f"       • {improvement}")
            
            total_improvement = score_projection.get('total_improvement', 'N/A')
            print(f"     Total Improvement: {total_improvement}")
            
            # Overall CV Strategy
            overall_cv_strategy = recommendations.get('overall_cv_strategy', 'N/A')
            if overall_cv_strategy != 'N/A':
                print(f"\n📋 OVERALL CV STRATEGY:")
                print(f"     {overall_cv_strategy}")
            
            # Check for additional keys that might be present
            additional_keys = ['quick_wins', 'long_term_improvements', 'format_optimization', 'projected_impact']
            for key in additional_keys:
                if key in recommendations and recommendations[key]:
                    print(f"\n🔍 {key.upper().replace('_', ' ')}:")
                    if isinstance(recommendations[key], list):
                        for item in recommendations[key]:
                            print(f"     • {item}")
                    else:
                        print(f"     {recommendations[key]}")
            
            print("="*60)
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_recommendations_generation() 