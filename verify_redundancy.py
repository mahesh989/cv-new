#!/usr/bin/env python3
"""
Verify redundancy in the API response structure.
Run this with the JSON response to check for duplicate data.
"""

import json
import sys

def verify_redundancy(response_data):
    """Check for redundant three_section_skills data"""
    
    # Extract from three locations
    top_level = response_data.get('jd_three_section_skills', {})
    nested = response_data.get('results', {}).get('jd_analysis', {}).get('three_section_skills', {})
    metadata = response_data.get('results', {}).get('jd_analysis', {}).get('metadata', {}).get('three_section_skills', {})
    
    print("=" * 60)
    print("REDUNDANCY VERIFICATION")
    print("=" * 60)
    
    # Check if all three exist
    print(f"\n📍 Location 1 (Top-level): {'✅ EXISTS' if top_level else '❌ MISSING'}")
    print(f"   Technical: {len(top_level.get('technical_skills', []))} skills")
    print(f"   Soft: {len(top_level.get('soft_skills', []))} skills")
    print(f"   Domain: {len(top_level.get('domain_knowledge', []))} skills")
    
    print(f"\n📍 Location 2 (jd_analysis.three_section_skills): {'✅ EXISTS' if nested else '❌ MISSING'}")
    print(f"   Technical: {len(nested.get('technical_skills', []))} skills")
    print(f"   Soft: {len(nested.get('soft_skills', []))} skills")
    print(f"   Domain: {len(nested.get('domain_knowledge', []))} skills")
    
    print(f"\n📍 Location 3 (jd_analysis.metadata.three_section_skills): {'✅ EXISTS' if metadata else '❌ MISSING'}")
    print(f"   Technical: {len(metadata.get('technical_skills', []))} skills")
    print(f"   Soft: {len(metadata.get('soft_skills', []))} skills")
    print(f"   Domain: {len(metadata.get('domain_knowledge', []))} skills")
    
    # Compare content
    print("\n" + "=" * 60)
    print("CONTENT COMPARISON")
    print("=" * 60)
    
    top_nested_match = top_level == nested
    top_metadata_match = top_level == metadata
    nested_metadata_match = nested == metadata
    
    print(f"\n🔍 Top-level == Nested: {'✅ IDENTICAL' if top_nested_match else '❌ DIFFERENT'}")
    print(f"🔍 Top-level == Metadata: {'✅ IDENTICAL' if top_metadata_match else '❌ DIFFERENT'}")
    print(f"🔍 Nested == Metadata: {'✅ IDENTICAL' if nested_metadata_match else '❌ DIFFERENT'}")
    
    # Calculate redundancy
    if top_nested_match and top_metadata_match:
        print("\n⚠️  REDUNDANCY DETECTED: Same data stored in 3 locations!")
        
        # Estimate size
        import sys
        top_size = len(json.dumps(top_level))
        total_redundant = top_size * 3
        wasted = top_size * 2  # 2 redundant copies
        
        print(f"\n📊 Size Analysis:")
        print(f"   Size per copy: ~{top_size} bytes")
        print(f"   Total stored: ~{total_redundant} bytes")
        print(f"   Wasted (redundant): ~{wasted} bytes")
        print(f"   Efficiency: {top_size / total_redundant * 100:.1f}%")
    
    # Check for other redundancies
    print("\n" + "=" * 60)
    print("OTHER POTENTIAL REDUNDANCIES")
    print("=" * 60)
    
    jd_skills = response_data.get('results', {}).get('jd_skills', {})
    if jd_skills:
        print(f"\n📋 jd_skills exists:")
        print(f"   Technical: {len(jd_skills.get('technical_skills', []))} skills")
        print(f"   Soft: {len(jd_skills.get('soft_skills', []))} skills")
        print(f"   Domain: {len(jd_skills.get('domain_keywords', []))} skills")
        
        # Compare with three_section_skills
        jd_tech = set(jd_skills.get('technical_skills', []))
        top_tech = set(top_level.get('technical_skills', []))
        
        if jd_tech == top_tech:
            print(f"   ⚠️  jd_skills.technical_skills == top-level.technical_skills (REDUNDANT)")
        else:
            print(f"   ✅ jd_skills differs from three_section_skills (not redundant)")
            if jd_tech:
                print(f"      Unique in jd_skills: {jd_tech - top_tech}")
                print(f"      Unique in three_section: {top_tech - jd_tech}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Example usage: paste your JSON here or read from file
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            response_data = json.load(f)
    else:
        # Paste your JSON response here
        response_data = {
            # Your JSON here
        }
        print("Usage: python verify_redundancy.py <json_file>")
        print("Or paste JSON directly in the script")
        sys.exit(1)
    
    verify_redundancy(response_data)

