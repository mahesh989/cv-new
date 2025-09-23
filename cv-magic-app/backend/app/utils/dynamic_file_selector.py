"""
Dynamic File Selector

Provides utilities for selecting latest files from company folders and CV directories.
"""

import logging
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class DynamicFileSelector:
    """Dynamic file selector for CV analysis system"""
    
    def __init__(self, base_path: Optional[str] = None):
        if base_path is None:
            base_path = "/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis"
        self.base_path = Path(base_path)
        self.cvs_path = self.base_path / "cvs"
        self.original_path = self.cvs_path / "original"
        self.tailored_path = self.cvs_path / "tailored"
    
    def get_latest_cv_files(self, company: str) -> Dict[str, Dict[str, str]]:
        """
        Get latest CV files by checking both original and tailored directories
        
        Args:
            company: Company name
            
        Returns:
            Dict containing file info:
            {
                'latest': {
                    'json_path': str,  # Path to latest JSON file
                    'txt_path': str,   # Path to latest TXT file
                    'source': str,     # 'original' or 'tailored'
                    'timestamp': str   # Timestamp if available
                },
                'original': {
                    'json_path': str,
                    'txt_path': str
                },
                'tailored': {
                    'json_path': str,
                    'txt_path': str,
                    'timestamp': str
                }
            }
        """
        # Get original CV files
        original_json = self.original_path / "original_cv.json"
        original_txt = self.original_path / "original_cv.txt"
        original_time = max(
            original_json.stat().st_mtime if original_json.exists() else 0,
            original_txt.stat().st_mtime if original_txt.exists() else 0
        )
        
        # Find latest tailored CV
        tailored_files = self._find_latest_tailored_cv(company)
        tailored_time = 0
        if tailored_files and tailored_files['json_path']:
            tailored_json = Path(tailored_files['json_path'])
            tailored_time = tailored_json.stat().st_mtime if tailored_json.exists() else 0
        
        # Determine which is latest
        result = {
            'original': {
                'json_path': str(original_json) if original_json.exists() else None,
                'txt_path': str(original_txt) if original_txt.exists() else None
            },
            'tailored': tailored_files or {
                'json_path': None,
                'txt_path': None,
                'timestamp': None
            }
        }
        
        # Set latest based on modification time
        if tailored_time > original_time and tailored_files:
            result['latest'] = {
                'json_path': tailored_files['json_path'],
                'txt_path': tailored_files['txt_path'],
                'source': 'tailored',
                'timestamp': tailored_files['timestamp']
            }
            logger.info(f"Using latest tailored CV for {company}")
        else:
            result['latest'] = {
                'json_path': str(original_json) if original_json.exists() else None,
                'txt_path': str(original_txt) if original_txt.exists() else None,
                'source': 'original',
                'timestamp': None
            }
            logger.info(f"Using original CV for {company}")
        
        return result
    
    def get_latest_company_file(
        self,
        company: str,
        file_pattern: str,
        fallback_file: Optional[str] = None
    ) -> Optional[Path]:
        """
        Get latest file matching pattern from company directory
        
        Args:
            company: Company name
            file_pattern: File name pattern (e.g., "jd_original", "skills_analysis")
            fallback_file: Optional fallback file name if no timestamped file found
            
        Returns:
            Path to latest file or None if not found
        """
        company_dir = self.base_path / company
        if not company_dir.exists():
            return None
        
        # Find all matching files
        pattern = f"*{file_pattern}*.json"  # Add wildcard for timestamps
        matching_files = list(company_dir.glob(pattern))
        
        if not matching_files and fallback_file:
            # Try fallback file
            fallback_path = company_dir / fallback_file
            return fallback_path if fallback_path.exists() else None
        
        # Sort by modification time and return latest
        return max(matching_files, key=lambda p: p.stat().st_mtime) if matching_files else None
    
    def _find_latest_tailored_cv(self, company: str) -> Optional[Dict[str, str]]:
        """Find latest tailored CV for company"""
        if not self.tailored_path.exists():
            return None
            
        # Find all tailored CVs for this company
        pattern = f"{company}_tailored_cv_*.json"
        json_files = list(self.tailored_path.glob(pattern))
        
        if not json_files:
            return None
        
        # Get latest JSON file
        latest_json = max(json_files, key=lambda p: p.stat().st_mtime)
        
        # Get corresponding TXT file
        txt_path = latest_json.with_suffix('.txt')
        
        # Extract timestamp from filename
        timestamp = None
        try:
            # Format: company_tailored_cv_YYYYMMDD_HHMMSS.json
            timestamp_part = latest_json.stem.split('_')[-2:]
            if len(timestamp_part) == 2:
                timestamp = f"{timestamp_part[0]}_{timestamp_part[1]}"
        except Exception:
            pass
        
        return {
            'json_path': str(latest_json),
            'txt_path': str(txt_path) if txt_path.exists() else None,
            'timestamp': timestamp
        }
    
    def get_latest_analysis_files(self, company: str) -> Dict[str, str]:
        """
        Get all latest analysis files for a company
        
        Args:
            company: Company name
            
        Returns:
            Dict containing paths to latest files:
            {
                'cv': {path info from get_latest_cv_files},
                'jd_original': str,
                'jd_analysis': str,
                'skills_analysis': str,
                'cv_jd_match': str,
                ...
            }
        """
        result = {
            'cv': self.get_latest_cv_files(company),
            'jd_original': None,
            'jd_analysis': None,
            'skills_analysis': None,
            'cv_jd_match': None,
            'recommendations': None
        }
        
        # Get latest files for each type
        jd_original = self.get_latest_company_file(
            company,
            'jd_original',
            'jd_original.json'
        )
        result['jd_original'] = str(jd_original) if jd_original else None
        
        jd_analysis = self.get_latest_company_file(
            company,
            'jd_analysis',
            'jd_analysis.json'
        )
        result['jd_analysis'] = str(jd_analysis) if jd_analysis else None
        
        skills_analysis = self.get_latest_company_file(
            company,
            f'{company}_skills_analysis',
            f'{company}_skills_analysis.json'
        )
        result['skills_analysis'] = str(skills_analysis) if skills_analysis else None
        
        cv_jd_match = self.get_latest_company_file(
            company,
            'cv_jd_match_results',
            'cv_jd_match_results.json'
        )
        result['cv_jd_match'] = str(cv_jd_match) if cv_jd_match else None
        
        recommendations = self.get_latest_company_file(
            company,
            f'{company}_input_recommendation',
            f'{company}_input_recommendation.json'
        )
        result['recommendations'] = str(recommendations) if recommendations else None
        
        return result


# Global instance
dynamic_file_selector = DynamicFileSelector()