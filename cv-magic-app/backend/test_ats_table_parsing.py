#!/usr/bin/env python3
"""
Test script to verify ATS calculator correctly parses the new table format
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ats.ats_score_calculator import ATSScoreCalculator

def test_table_format_parsing():
    """Test that the ATS calculator correctly parses the new table format"""
    
    # Sample content in the new table format
    test_content = """🎯 OVERALL SUMMARY
----------------------------------------
Total Requirements: 43
Matched: 28
Missing: 15
Match Rate: 65.12%

📊 SUMMARY TABLE
--------------------------------------------------------------------------------
Category              CV Total  JD Total   Matched   Missing  Match Rate (%)
Technical Skills            18          7           7           0          100.00
Soft Skills                   5         14           5           9           35.71
Domain Keywords             18         22          16           6           72.73

🧠 DETAILED AI ANALYSIS
--------------------------------------------------------------------------------

🔹 TECHNICAL SKILLS
  ✅ MATCHED JD REQUIREMENTS (7 items):
    1. JD Required: 'Excel'
       → Found in CV: 'Excel'
       💡 Exact match.
  ❌ MISSING FROM CV (0 items):
    None

🔹 SOFT SKILLS
  ✅ MATCHED JD REQUIREMENTS (5 items):
    1. JD Required: 'Communication'
       → Found in CV: 'Communication'
       💡 Exact match.
  ❌ MISSING FROM CV (9 items):
    1. JD Requires: 'Time Management'
       💡 Not found in CV.

🔹 DOMAIN KEYWORDS
  ✅ MATCHED JD REQUIREMENTS (16 items):
    1. JD Required: 'Data Science'
       → Found in CV: 'Data Science'
       💡 Exact match.
  ❌ MISSING FROM CV (6 items):
    1. JD Requires: 'Point of Sale data'
       💡 Not found in CV.
"""

    calculator = ATSScoreCalculator()
    
    # Test parsing
    tech_rate, domain_rate, soft_rate, tech_missing, soft_missing, domain_missing = \
        calculator._calculate_match_rates({"content": test_content})
    
    print("=== ATS Table Format Parsing Test ===")
    print(f"Technical Skills Match Rate: {tech_rate}% (expected: 100.0)")
    print(f"Soft Skills Match Rate: {soft_rate}% (expected: 35.71)")
    print(f"Domain Keywords Match Rate: {domain_rate}% (expected: 72.73)")
    print(f"Technical Missing: {tech_missing} (expected: 0)")
    print(f"Soft Missing: {soft_missing} (expected: 9)")
    print(f"Domain Missing: {domain_missing} (expected: 6)")
    
    # Verify results
    assert tech_rate == 100.0, f"Tech rate mismatch: {tech_rate} != 100.0"
    assert soft_rate == 35.71, f"Soft rate mismatch: {soft_rate} != 35.71"
    assert domain_rate == 72.73, f"Domain rate mismatch: {domain_rate} != 72.73"
    assert tech_missing == 0, f"Tech missing mismatch: {tech_missing} != 0"
    assert soft_missing == 9, f"Soft missing mismatch: {soft_missing} != 9"
    assert domain_missing == 6, f"Domain missing mismatch: {domain_missing} != 6"
    
    print("\n✅ All tests passed! Table format parsing is working correctly.")

if __name__ == "__main__":
    test_table_format_parsing()
