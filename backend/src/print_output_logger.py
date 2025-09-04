#!/usr/bin/env python3
"""
Output logger for appending all analysis results to a single file per company.
All outputs (Preliminary Analysis, Analyze Match, ATS Test, etc.) are appended to the same file.
"""

import os
import re
from datetime import datetime
from pathlib import Path


def append_output_log(output, company_name="Company", tag=None, role_name="UnknownRole", cv_label="BaseCV", 
stage="Analysis"):
    """
    Append output to a single file per company.
    
    Args:
        output (str): The content to append
        company_name (str): Company name for filename
        tag (str): Optional tag for the output
        role_name (str): Role name for filename
        cv_label (str): CV label (e.g., "BaseCV", "TailoredCV_v2")
        stage (str): Stage of analysis (e.g., "PrelimAnalysis", "ATS_Initial", "ATS_Tailored")
    """
    try:
        # Create analysis_results directory if it doesn't exist
        # Use the local analysis_results directory in backend
        analysis_dir = Path("analysis_results")
        analysis_dir.mkdir(exist_ok=True)
        
        # Sanitize company name for filename
        safe_company = re.sub(r'[^\w\s-]', '', company_name).strip()
        safe_company = re.sub(r'[-\s]+', '_', safe_company)
        if not safe_company:
            safe_company = "UnknownCompany"
        
        # Create filename: {company_name}_output_log.txt
        filename = f"{safe_company}_output_log.txt"
        filepath = analysis_dir / filename
        
        # Get current timestamp
        timestamp = datetime.now().isoformat()
        
        # Format the output with timestamp and tag
        formatted_output = f"""
================================================================================
[{timestamp}] [{tag or stage.upper()}] OUTPUT:
{output}
================================================================================
"""
        
        # Append to file
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(formatted_output)
        
        print(f"✅ [LOGGER] Appended {tag or stage} output to: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ [LOGGER] Error appending output: {e}")
        return False


def get_company_filename(company_name):
    """
    Get the filename for a given company name.
    
    Args:
        company_name (str): Company name
        
    Returns:
        str: Filename for the company
    """
    safe_company = re.sub(r'[^\w\s-]', '', company_name).strip()
    safe_company = re.sub(r'[-\s]+', '_', safe_company)
    if not safe_company:
        safe_company = "UnknownCompany"
    
    return f"{safe_company}_output_log.txt"


def list_company_files():
    """
    List all company output log files.
    
    Returns:
        list: List of company filenames
    """
    analysis_dir = Path("analysis_results")
    if not analysis_dir.exists():
        return []
    
    files = [f.name for f in analysis_dir.glob("*_output_log.txt")]
    return sorted(files)


def clear_company_log(company_name):
    """
    Clear the log file for a specific company.
    
    Args:
        company_name (str): Company name
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        filename = get_company_filename(company_name)
        filepath = Path("analysis_results") / filename
        
        if filepath.exists():
            filepath.unlink()
            print(f"✅ [LOGGER] Cleared log file: {filename}")
            return True
        else:
            print(f"⚠️ [LOGGER] Log file not found: {filename}")
            return False
            
    except Exception as e:
        print(f"❌ [LOGGER] Error clearing log file: {e}")
        return False 