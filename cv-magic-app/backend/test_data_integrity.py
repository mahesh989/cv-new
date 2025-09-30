import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

def verify_json_structure(data: dict, required_structure: Dict[str, Any], path: str = "") -> List[str]:
    """Recursively verify JSON structure matches requirements"""
    issues = []
    
    for key, expected in required_structure.items():
        current_path = f"{path}.{key}" if path else key
        
        if key not in data:
            issues.append(f"Missing required field: {current_path}")
            continue
            
        value = data[key]
        
        if isinstance(expected, dict):
            if not isinstance(value, dict):
                issues.append(f"Field {current_path} should be an object, got {type(value)}")
            else:
                issues.extend(verify_json_structure(value, expected, current_path))
        
        elif isinstance(expected, list):
            if not isinstance(value, list):
                issues.append(f"Field {current_path} should be an array, got {type(value)}")
            elif expected and value:  # If expected has type hints
                expected_type = expected[0]
                for i, item in enumerate(value):
                    if not isinstance(item, type(expected_type)):
                        issues.append(f"Item {i} in {current_path} should be {type(expected_type)}, got {type(item)}")
        
        elif not isinstance(value, type(expected)):
            issues.append(f"Field {current_path} should be {type(expected)}, got {type(value)}")
            
    return issues

def check_cv_content(file_path: Path) -> List[str]:
    """Check CV file content structure"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        required_structure = {
            "text": "",  # String
            "saved_at": "",  # String
            "sections": {
                "personal_info": {},
                "education": [{}],
                "experience": [{}],
                "skills": [{}]
            }
        }
        
        return verify_json_structure(data, required_structure)
    except Exception as e:
        return [f"Error reading CV file: {str(e)}"]

def check_skills_content(file_path: Path) -> List[str]:
    """Check skills analysis file content structure"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        required_structure = {
            "analysis": {
                "skill_categories": {},
                "overall_score": 0.0
            },
            "matched_skills": [""],  # Array of strings
            "missing_skills": [""],  # Array of strings
            "recommendations": [""]  # Array of strings
        }
        
        return verify_json_structure(data, required_structure)
    except Exception as e:
        return [f"Error reading skills file: {str(e)}"]

def verify_file_data() -> Dict[str, Any]:
    base_path = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/user/user_admin@admin.com/cv-analysis")
    company = "Australia_for_UNHCR"
    
    results = {
        "cv_files": {},
        "skills_files": {},
        "recommendation_files": {},
        "issues_found": []
    }
    
    # Check CV files
    cv_paths = {
        "original_json": base_path / "cvs/original/original_cv.json",
        "original_txt": base_path / "cvs/original/original_cv.txt",
        "tailored": base_path / f"cvs/tailored/{company}_tailored_cv_20250929_215026.json"
    }
    
    for name, path in cv_paths.items():
        if not path.exists():
            results["issues_found"].append(f"Missing CV file: {path}")
            results["cv_files"][name] = {"exists": False}
            continue
            
        results["cv_files"][name] = {"exists": True}
        if name != "original_txt":  # Skip txt file content check
            issues = check_cv_content(path)
            if issues:
                results["cv_files"][name]["issues"] = issues
                results["issues_found"].extend(f"[{name}] {issue}" for issue in issues)
    
    # Check skills files
    company_dir = base_path / "applied_companies" / company
    skills_file = list(company_dir.glob("*skills_analysis*.json"))
    
    if not skills_file:
        results["issues_found"].append("No skills analysis file found")
    else:
        issues = check_skills_content(skills_file[0])
        results["skills_files"]["analysis"] = {
            "exists": True,
            "path": str(skills_file[0])
        }
        if issues:
            results["skills_files"]["analysis"]["issues"] = issues
            results["issues_found"].extend(f"[skills_analysis] {issue}" for issue in issues)
    
    # Check recommendation files
    recommendation_patterns = [
        "*input_recommendation*.json",
        "*ai_recommendation*.json"
    ]
    
    for pattern in recommendation_patterns:
        rec_files = list(company_dir.glob(pattern))
        rec_type = "input" if "input" in pattern else "ai"
        
        if not rec_files:
            results["issues_found"].append(f"No {rec_type} recommendation file found")
            continue
            
        with open(rec_files[0], 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if not isinstance(data, dict):
                    results["issues_found"].append(f"{rec_type} recommendation file contains invalid JSON")
            except Exception as e:
                results["issues_found"].append(f"Error reading {rec_type} recommendation file: {str(e)}")
    
    return results

if __name__ == "__main__":
    results = verify_file_data()
    
    print("\n=== Data Integrity Verification ===\n")
    
    # Print CV files status
    print("CV Files:")
    for name, info in results["cv_files"].items():
        status = "✅" if info.get("exists", False) and "issues" not in info else "❌"
        print(f"{status} {name}")
        if "issues" in info:
            for issue in info["issues"]:
                print(f"  - {issue}")
    
    # Print skills files status
    print("\nSkills Files:")
    for name, info in results["skills_files"].items():
        status = "✅" if info.get("exists", False) and "issues" not in info else "❌"
        print(f"{status} {name}")
        if "issues" in info:
            for issue in info["issues"]:
                print(f"  - {issue}")
    
    # Print overall issues
    if results["issues_found"]:
        print("\nIssues Found:")
        for issue in results["issues_found"]:
            print(f"❌ {issue}")
    else:
        print("\n✅ No data integrity issues found!")