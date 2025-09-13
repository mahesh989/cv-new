#!/usr/bin/env python3
"""
Test Component Analysis Integration

This script tests the component analysis functionality that runs after AI-powered skills analysis.
It verifies that:
1. Component analysis is triggered after skills analysis
2. Results are saved properly in the skills_analysis.json file
3. All 5 components are analyzed correctly
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
import sys

# Add the backend directory to the Python path
sys.path.insert(0, '/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend')

from app.services.ats.modular_ats_orchestrator import modular_ats_orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_required_files(company: str) -> dict:
    """Check if all required files exist for component analysis."""
    base_dir = Path("/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend/cv-analysis")
    
    required_files = {
        "cv_file": base_dir / "original_cv.json",
        "jd_file": base_dir / company / "jd_original.json",
        "skills_analysis": base_dir / company / f"{company}_skills_analysis.json",
        "match_file": base_dir / company / "cv_jd_match_results.json"
    }
    
    missing_files = []
    existing_files = []
    
    for name, path in required_files.items():
        if path.exists():
            existing_files.append((name, str(path)))
        else:
            missing_files.append((name, str(path)))
    
    return {
        "all_exist": len(missing_files) == 0,
        "existing": existing_files,
        "missing": missing_files
    }


def get_latest_analysis_entry(company: str) -> dict:
    """Get the latest component analysis entry from the skills analysis file."""
    base_dir = Path("/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend/cv-analysis")
    analysis_file = base_dir / company / f"{company}_skills_analysis.json"
    
    if not analysis_file.exists():
        return None
    
    try:
        with open(analysis_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entries = data.get("component_analysis_entries", [])
        if entries:
            return entries[-1]  # Return the latest entry
        return None
    except Exception as e:
        logger.error(f"Failed to read analysis file: {e}")
        return None


def print_component_scores(scores: dict):
    """Pretty print component scores."""
    print("\n📊 Component Analysis Scores:")
    print("=" * 50)
    
    # Main component scores
    main_components = [
        ("Skills Relevance", "skills_relevance"),
        ("Experience Alignment", "experience_alignment"),
        ("Industry Fit", "industry_fit"),
        ("Role Seniority", "role_seniority"),
        ("Technical Depth", "technical_depth")
    ]
    
    for name, key in main_components:
        if key in scores:
            print(f"{name:.<30} {scores[key]:>6.1f}")
    
    print("\n📈 Detailed Scores:")
    print("-" * 50)
    
    # Other detailed scores
    for key, value in scores.items():
        if key not in [c[1] for c in main_components]:
            formatted_key = key.replace('_', ' ').title()
            print(f"{formatted_key:.<30} {value:>6.1f}")


async def test_component_analysis(company: str):
    """Test component analysis for a specific company."""
    print(f"\n🧪 Testing Component Analysis for: {company}")
    print("=" * 60)
    
    # Step 1: Check required files
    print("\n📁 Checking required files...")
    file_check = check_required_files(company)
    
    if not file_check["all_exist"]:
        print("❌ Missing required files:")
        for name, path in file_check["missing"]:
            print(f"   - {name}: {path}")
        print("\n⚠️  Please ensure all required files exist before running component analysis.")
        return False
    
    print("✅ All required files exist:")
    for name, path in file_check["existing"]:
        print(f"   - {name}: {path}")
    
    # Step 2: Get baseline (before running analysis)
    print("\n📊 Getting baseline...")
    baseline_entry = get_latest_analysis_entry(company)
    baseline_count = len(baseline_entry.get("component_analysis_entries", [])) if baseline_entry else 0
    
    # Step 3: Run component analysis
    print(f"\n🔧 Running component analysis for {company}...")
    try:
        result = await modular_ats_orchestrator.run_component_analysis(company)
        print("✅ Component analysis completed successfully!")
        
        # Print immediate results
        if "extracted_scores" in result:
            print_component_scores(result["extracted_scores"])
        
    except Exception as e:
        print(f"❌ Component analysis failed: {e}")
        logger.error(f"Component analysis error: {e}", exc_info=True)
        return False
    
    # Step 4: Verify results were saved
    print("\n💾 Verifying saved results...")
    latest_entry = get_latest_analysis_entry(company)
    
    if not latest_entry:
        print("❌ No component analysis entry found in skills analysis file")
        return False
    
    # Check if a new entry was added
    current_count = len(latest_entry.get("component_analysis_entries", []))
    if current_count <= baseline_count:
        print("⚠️  No new component analysis entry was added")
        return False
    
    print("✅ Component analysis results saved successfully!")
    
    # Print saved scores
    if "extracted_scores" in latest_entry:
        print("\n📊 Saved scores:")
        print_component_scores(latest_entry["extracted_scores"])
    
    # Print component details
    if "component_analyses" in latest_entry:
        components = latest_entry["component_analyses"]
        print(f"\n🔍 Components analyzed: {len(components)}")
        for comp_name in components:
            print(f"   - {comp_name}")
    
    print(f"\n✅ Component analysis test passed for {company}!")
    return True


async def list_available_companies():
    """List all companies with required files for component analysis."""
    base_dir = Path("/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend/cv-analysis")
    
    if not base_dir.exists():
        print("❌ cv-analysis directory not found")
        return []
    
    companies = []
    for company_dir in base_dir.iterdir():
        if company_dir.is_dir() and company_dir.name != "Unknown_Company":
            # Check if skills analysis file exists
            skills_file = company_dir / f"{company_dir.name}_skills_analysis.json"
            if skills_file.exists():
                companies.append(company_dir.name)
    
    return companies


async def main():
    """Main test function."""
    print("\n🚀 Component Analysis Test Script")
    print("=" * 60)
    
    # List available companies
    print("\n📋 Checking available companies...")
    companies = await list_available_companies()
    
    if not companies:
        print("❌ No companies found with skills analysis files")
        print("   Please run skills analysis first before testing component analysis")
        return
    
    print(f"✅ Found {len(companies)} companies with skills analysis:")
    for i, company in enumerate(companies, 1):
        print(f"   {i}. {company}")
    
    # Test each company or specific one
    if len(sys.argv) > 1:
        # Test specific company from command line
        test_company = sys.argv[1]
        if test_company in companies:
            await test_component_analysis(test_company)
        else:
            print(f"\n❌ Company '{test_company}' not found or doesn't have skills analysis")
            print(f"   Available companies: {', '.join(companies)}")
    else:
        # Test all companies
        print(f"\n🔄 Testing all {len(companies)} companies...")
        
        success_count = 0
        for company in companies:
            success = await test_component_analysis(company)
            if success:
                success_count += 1
            print("\n" + "-" * 60)
        
        print(f"\n📊 Test Summary: {success_count}/{len(companies)} companies passed")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
