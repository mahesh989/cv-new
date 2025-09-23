"""
Test script for dynamic file selector
"""

import json
from pathlib import Path
from dynamic_file_selector import dynamic_file_selector

def test_file_selection():
    company = "Australia_for_UNHCR"
    
    # Test CV file selection
    print("\nTesting CV file selection:")
    cv_files = dynamic_file_selector.get_latest_cv_files(company)
    print("\nCV Files:")
    print(json.dumps(cv_files, indent=2))
    
    # Test latest files for all analysis types
    print("\nTesting analysis file selection:")
    analysis_files = dynamic_file_selector.get_latest_analysis_files(company)
    print("\nAnalysis Files:")
    print(json.dumps(analysis_files, indent=2))
    
    # Verify file existence and content type
    print("\nVerifying latest CV file:")
    latest_cv = cv_files['latest']
    if latest_cv['json_path'] and Path(latest_cv['json_path']).exists():
        print(f"Latest CV JSON exists: {latest_cv['json_path']}")
        print(f"Source: {latest_cv['source']}")
        if latest_cv['timestamp']:
            print(f"Timestamp: {latest_cv['timestamp']}")
    
    print("\nVerifying latest analysis files:")
    for file_type, file_path in analysis_files.items():
        if file_type != 'cv':
            if file_path and Path(file_path).exists():
                print(f"{file_type}: {file_path}")

if __name__ == "__main__":
    test_file_selection()