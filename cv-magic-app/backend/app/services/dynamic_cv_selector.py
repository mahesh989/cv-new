"""
Dynamic CV Selector Service

This service dynamically selects the most recent CV files from either the 
original or tailored folders for use in the analysis pipeline.
"""

import logging
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class DynamicCVSelector:
    """
    Service to dynamically select the most recent CV files from cvs folder structure
    """
    
    def __init__(self, cv_analysis_base_path: str = None):
        if cv_analysis_base_path is None:
            cv_analysis_base_path = "cv-analysis"
        
        self.base_path = Path(cv_analysis_base_path)
        self.cvs_path = self.base_path / "cvs"
        self.original_path = self.cvs_path / "original"
        self.tailored_path = self.cvs_path / "tailored"
    
    def get_latest_cv_files(self) -> Dict[str, Optional[Path]]:
        """
        Get the latest CV files (both JSON and TXT) from either original or tailored folders
        
        Returns:
            Dict with keys 'json_path', 'txt_path', 'source_folder', 'json_timestamp', 'txt_timestamp'
        """
        try:
            logger.info("🔍 [DYNAMIC_CV] Starting dynamic CV file selection")
            
            # Find all CV files in both folders
            json_files = self._find_cv_files_by_extension('.json')
            txt_files = self._find_cv_files_by_extension('.txt')
            
            # Get the latest files
            latest_json = self._get_latest_file(json_files)
            latest_txt = self._get_latest_file(txt_files)
            
            result = {
                'json_path': latest_json['path'] if latest_json else None,
                'txt_path': latest_txt['path'] if latest_txt else None,
                'json_source': latest_json['source'] if latest_json else None,
                'txt_source': latest_txt['source'] if latest_txt else None,
                'json_timestamp': latest_json['timestamp'] if latest_json else None,
                'txt_timestamp': latest_txt['timestamp'] if latest_txt else None,
            }
            
            # Log the selection
            if result['json_path']:
                logger.info(f"📄 [DYNAMIC_CV] Selected JSON: {result['json_path']} from {result['json_source']} folder")
            else:
                logger.warning("⚠️ [DYNAMIC_CV] No JSON CV file found")
                
            if result['txt_path']:
                logger.info(f"📄 [DYNAMIC_CV] Selected TXT: {result['txt_path']} from {result['txt_source']} folder")
            else:
                logger.warning("⚠️ [DYNAMIC_CV] No TXT CV file found")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ [DYNAMIC_CV] Error during CV file selection: {e}")
            return {
                'json_path': None,
                'txt_path': None,
                'json_source': None,
                'txt_source': None,
                'json_timestamp': None,
                'txt_timestamp': None,
            }
    
    def _find_cv_files_by_extension(self, extension: str) -> list:
        """Find all CV files with given extension in both original and tailored folders"""
        files = []
        
        # Check original folder
        if self.original_path.exists():
            for file_path in self.original_path.glob(f"*{extension}"):
                files.append({
                    'path': file_path,
                    'source': 'original',
                    'timestamp': file_path.stat().st_mtime,
                    'filename': file_path.name
                })
        
        # Check tailored folder
        if self.tailored_path.exists():
            for file_path in self.tailored_path.glob(f"*{extension}"):
                files.append({
                    'path': file_path,
                    'source': 'tailored',
                    'timestamp': file_path.stat().st_mtime,
                    'filename': file_path.name
                })
        
        return files
    
    def _get_latest_file(self, files: list) -> Optional[Dict]:
        """Get the file with the latest timestamp"""
        if not files:
            return None
        
        # Sort by timestamp (most recent first)
        sorted_files = sorted(files, key=lambda x: x['timestamp'], reverse=True)
        return sorted_files[0]
    
    def get_cv_content_for_analysis(self) -> Dict[str, Any]:
        """
        Get CV content optimized for analysis pipeline
        
        Returns:
            Dict containing both text and structured content with metadata
        """
        try:
            latest_files = self.get_latest_cv_files()
            
            result = {
                'success': False,
                'text_content': None,
                'json_content': None,
                'metadata': {
                    'json_path': str(latest_files['json_path']) if latest_files['json_path'] else None,
                    'txt_path': str(latest_files['txt_path']) if latest_files['txt_path'] else None,
                    'json_source': latest_files['json_source'],
                    'txt_source': latest_files['txt_source'],
                    'selection_timestamp': datetime.now().isoformat()
                }
            }
            
            # Load text content
            if latest_files['txt_path'] and latest_files['txt_path'].exists():
                try:
                    with open(latest_files['txt_path'], 'r', encoding='utf-8') as f:
                        result['text_content'] = f.read().strip()
                    logger.info(f"✅ [DYNAMIC_CV] Loaded text content from {latest_files['txt_path']}")
                except Exception as e:
                    logger.error(f"❌ [DYNAMIC_CV] Failed to load text content: {e}")
            
            # Load JSON content
            if latest_files['json_path'] and latest_files['json_path'].exists():
                try:
                    with open(latest_files['json_path'], 'r', encoding='utf-8') as f:
                        result['json_content'] = json.load(f)
                    logger.info(f"✅ [DYNAMIC_CV] Loaded JSON content from {latest_files['json_path']}")
                except Exception as e:
                    logger.error(f"❌ [DYNAMIC_CV] Failed to load JSON content: {e}")
            
            # Check if we have at least one type of content
            if result['text_content'] or result['json_content']:
                result['success'] = True
                logger.info("✅ [DYNAMIC_CV] CV content successfully loaded for analysis")
            else:
                logger.error("❌ [DYNAMIC_CV] No CV content could be loaded")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ [DYNAMIC_CV] Error loading CV content for analysis: {e}")
            return {
                'success': False,
                'text_content': None,
                'json_content': None,
                'metadata': {
                    'error': str(e),
                    'selection_timestamp': datetime.now().isoformat()
                }
            }
    
    def get_latest_cv_paths_for_services(self) -> Dict[str, str]:
        """
        Get the latest CV file paths formatted for use in existing services
        
        Returns:
            Dict with 'json_path' and 'txt_path' as strings
        """
        latest_files = self.get_latest_cv_files()
        
        return {
            'json_path': str(latest_files['json_path']) if latest_files['json_path'] else None,
            'txt_path': str(latest_files['txt_path']) if latest_files['txt_path'] else None,
            'json_source': latest_files['json_source'],
            'txt_source': latest_files['txt_source']
        }
    
    def validate_cv_files_exist(self) -> Dict[str, Any]:
        """
        Validate that CV files exist and are accessible
        
        Returns:
            Validation result with details
        """
        try:
            latest_files = self.get_latest_cv_files()
            
            validation = {
                'valid': False,
                'has_json': False,
                'has_txt': False,
                'json_readable': False,
                'txt_readable': False,
                'errors': []
            }
            
            # Check JSON file
            if latest_files['json_path']:
                validation['has_json'] = True
                try:
                    with open(latest_files['json_path'], 'r') as f:
                        json.load(f)
                    validation['json_readable'] = True
                except Exception as e:
                    validation['errors'].append(f"JSON file not readable: {e}")
            else:
                validation['errors'].append("No JSON CV file found")
            
            # Check TXT file
            if latest_files['txt_path']:
                validation['has_txt'] = True
                try:
                    with open(latest_files['txt_path'], 'r') as f:
                        content = f.read().strip()
                        if content:
                            validation['txt_readable'] = True
                        else:
                            validation['errors'].append("TXT file is empty")
                except Exception as e:
                    validation['errors'].append(f"TXT file not readable: {e}")
            else:
                validation['errors'].append("No TXT CV file found")
            
            # Overall validation
            validation['valid'] = validation['json_readable'] or validation['txt_readable']
            
            return validation
            
        except Exception as e:
            return {
                'valid': False,
                'has_json': False,
                'has_txt': False,
                'json_readable': False,
                'txt_readable': False,
                'errors': [f"Validation error: {e}"]
            }


# Global instance for easy import
dynamic_cv_selector = DynamicCVSelector()
