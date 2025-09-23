"""
Enhanced Dynamic CV Selector Service

This service provides context-aware CV selection based on analysis scenario:
- Fresh analysis: Always uses original CV
- Rerun analysis: Uses latest tailored CV (if exists) for the specific company
"""

import logging
import json
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime
from app.utils.timestamp_utils import TimestampUtils
from app.exceptions import TailoredCVNotFoundError

logger = logging.getLogger(__name__)


class CVSelectionContext:
    """Container for CV selection context and metadata"""
    
    def __init__(self, data: Dict[str, Any]):
        self.cv_type: str = data.get('cv_type', 'original')  # 'original' or 'tailored'
        self.version: str = data.get('version', '1.0')
        self.json_path: Optional[Path] = data.get('json_path')
        self.txt_path: Optional[Path] = data.get('txt_path')
        self.source: str = data.get('source', 'original_cv_fresh_analysis')
        self.company: Optional[str] = data.get('company')
        self.timestamp: Optional[str] = data.get('timestamp')
        self.is_rerun: bool = data.get('is_rerun', False)
        self.exists: bool = data.get('exists', False)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'cv_type': self.cv_type,
            'version': self.version,
            'json_path': str(self.json_path) if self.json_path else None,
            'txt_path': str(self.txt_path) if self.txt_path else None,
            'source': self.source,
            'company': self.company,
            'timestamp': self.timestamp,
            'is_rerun': self.is_rerun,
            'exists': self.exists
        }


class EnhancedDynamicCVSelector:
    """
    Enhanced CV Selector with context awareness for fresh vs rerun analysis
    """
    
    def __init__(self, cv_analysis_base_path: str = None):
        if cv_analysis_base_path is None:
            cv_analysis_base_path = "/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis"
        
        self.base_path = Path(cv_analysis_base_path)
        self.cvs_path = self.base_path / "cvs"
        self.original_path = self.cvs_path / "original"
        self.tailored_path = self.cvs_path / "tailored"
        
        logger.info(f"🔧 [ENHANCED_CV_SELECTOR] Initialized with base path: {self.base_path}")
    
    def get_cv_for_analysis(self, company: str, is_rerun: bool = False) -> CVSelectionContext:
        """
        Select appropriate CV based on analysis context
        
        Args:
            company: Company name for the current analysis
            is_rerun: True if user clicked "Run ATS Test Again"
        
        Returns:
            CVSelectionContext with CV file paths and metadata
        """
        try:
            logger.info(f"🎯 [ENHANCED_CV_SELECTOR] Selecting CV for {company}, rerun={is_rerun}")
            
            if is_rerun:
                # Try to use latest tailored CV for this specific company
                tailored_context = self._get_latest_tailored_cv_for_company(company)
                if tailored_context.exists:
                    logger.info(f"✅ [ENHANCED_CV_SELECTOR] Using tailored CV v{tailored_context.version} for rerun")
                    return tailored_context
                else:
                    # Raise explicit error for rerun when tailored CV is missing
                    logger.error(f"❌ [ENHANCED_CV_SELECTOR] No tailored CV found for {company} during rerun")
                    raise TailoredCVNotFoundError(company)
            
            # Default: Use original CV for fresh analysis
            original_context = self._get_original_cv_context(company, is_rerun)
            logger.info(f"✅ [ENHANCED_CV_SELECTOR] Using original CV for fresh analysis")
            return original_context
            
        except TailoredCVNotFoundError as e:
            # Re-raise to be handled by API layer for explicit popup behavior
            logger.error(f"❌ [ENHANCED_CV_SELECTOR] {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ [ENHANCED_CV_SELECTOR] Error selecting CV: {e}")
            # Return fallback context
            return self._get_fallback_context(company, is_rerun, str(e))
    
    def _get_latest_tailored_cv_for_company(self, company: str) -> CVSelectionContext:
        """Get the latest tailored CV files for a specific company"""
        try:
            if not self.tailored_path.exists():
                return CVSelectionContext({
                    'cv_type': 'tailored',
                    'company': company,
                    'exists': False,
                    'source': 'tailored_not_found'
                })
            
            # Find all tailored CV files for this company
            logger.info(f"🔍 [ENHANCED_CV_SELECTOR] Searching for {company} tailored CVs in: {self.tailored_path}")
            
            json_files = TimestampUtils.find_all_timestamped_files(
                self.tailored_path, f"{company}_tailored_cv", "json"
            )
            txt_files = TimestampUtils.find_all_timestamped_files(
                self.tailored_path, f"{company}_tailored_cv", "txt"
            )
            
            logger.info(f"📄 [ENHANCED_CV_SELECTOR] Found {len(json_files)} JSON and {len(txt_files)} TXT tailored CVs for {company}")
            
            # Debug: Print all found files
            for f in json_files:
                logger.info(f"   JSON: {f.name} (modified: {datetime.fromtimestamp(f.stat().st_mtime)})")
            for f in txt_files:
                logger.info(f"   TXT: {f.name} (modified: {datetime.fromtimestamp(f.stat().st_mtime)})")
            
            if not json_files:
                return CVSelectionContext({
                    'cv_type': 'tailored',
                    'company': company,
                    'exists': False,
                    'source': 'no_tailored_files_for_company'
                })
            
            # Get latest files (first in sorted list)
            latest_json = json_files[0]
            latest_txt = txt_files[0] if txt_files else None
            
            # Extract version from timestamp
            timestamp = TimestampUtils.extract_timestamp_from_filename(latest_json.name)
            version = self._calculate_version_from_files(json_files)
            
            return CVSelectionContext({
                'cv_type': 'tailored',
                'version': version,
                'json_path': latest_json,
                'txt_path': latest_txt,
                'source': 'tailored_cv_rerun',
                'company': company,
                'timestamp': timestamp,
                'is_rerun': True,
                'exists': True
            })
            
        except Exception as e:
            logger.error(f"❌ [ENHANCED_CV_SELECTOR] Error getting tailored CV for {company}: {e}")
            return CVSelectionContext({
                'cv_type': 'tailored',
                'company': company,
                'exists': False,
                'source': f'tailored_error: {str(e)}'
            })
    
    def _get_original_cv_context(self, company: str, is_rerun: bool) -> CVSelectionContext:
        """Get original CV context"""
        try:
            json_path = self.original_path / "original_cv.json"
            txt_path = self.original_path / "original_cv.txt"
            
            exists = json_path.exists()
            
            return CVSelectionContext({
                'cv_type': 'original',
                'version': '1.0',
                'json_path': json_path if exists else None,
                'txt_path': txt_path if txt_path.exists() else None,
                'source': 'original_cv_rerun_fallback' if is_rerun else 'original_cv_fresh_analysis',
                'company': company,
                'timestamp': None,
                'is_rerun': is_rerun,
                'exists': exists
            })
            
        except Exception as e:
            logger.error(f"❌ [ENHANCED_CV_SELECTOR] Error getting original CV: {e}")
            return self._get_fallback_context(company, is_rerun, str(e))
    
    def _calculate_version_from_files(self, files: List[Path]) -> str:
        """Calculate version number based on number of tailored CV files"""
        # Version is based on the count of files (v1, v2, v3, etc.)
        return f"{len(files)}.0"
    
    def _get_fallback_context(self, company: str, is_rerun: bool, error: str) -> CVSelectionContext:
        """Get fallback context when errors occur"""
        return CVSelectionContext({
            'cv_type': 'error',
            'version': '0.0',
            'json_path': None,
            'txt_path': None,
            'source': f'error_fallback: {error}',
            'company': company,
            'timestamp': None,
            'is_rerun': is_rerun,
            'exists': False
        })
    
    def get_cv_content_for_analysis(self, company: str, is_rerun: bool = False) -> Dict[str, Any]:
        """
        Get CV content optimized for analysis pipeline with context awareness
        
        Args:
            company: Company name
            is_rerun: Whether this is a rerun analysis
            
        Returns:
            Dict containing CV content, metadata, and selection context
        """
        try:
            # Get appropriate CV based on context
            cv_context = self.get_cv_for_analysis(company, is_rerun)
            
            result = {
                'success': False,
                'text_content': None,
                'json_content': None,
                'context': cv_context.to_dict(),
                'metadata': {
                    'selection_timestamp': datetime.now().isoformat(),
                    'company': company,
                    'is_rerun': is_rerun
                }
            }
            
            if not cv_context.exists:
                logger.error(f"❌ [ENHANCED_CV_SELECTOR] Selected CV does not exist: {cv_context.source}")
                return result
            
            # Load text content
            if cv_context.txt_path and cv_context.txt_path.exists():
                logger.info(f"🔍 [ENHANCED_CV_SELECTOR] Attempting to load TXT CV: {cv_context.txt_path}")
                try:
                    with open(cv_context.txt_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    
                    # Validate content length
                    if len(content) < 100:  # Basic validation - CV should have meaningful content
                        logger.warning(f"⚠️ [ENHANCED_CV_SELECTOR] CV file {cv_context.txt_path} has insufficient content (length: {len(content)})")
                        result['text_content'] = None
                    else:
                        result['text_content'] = content
                        logger.info(f"✅ [ENHANCED_CV_SELECTOR] Loaded valid text content from {cv_context.txt_path} (length: {len(content)})")
                except Exception as e:
                    logger.error(f"❌ [ENHANCED_CV_SELECTOR] Failed to load text content: {e}")
            
            # Load JSON content
            if cv_context.json_path and cv_context.json_path.exists():
                try:
                    with open(cv_context.json_path, 'r', encoding='utf-8') as f:
                        result['json_content'] = json.load(f)
                    logger.info(f"✅ [ENHANCED_CV_SELECTOR] Loaded JSON content from {cv_context.json_path}")
                except Exception as e:
                    logger.error(f"❌ [ENHANCED_CV_SELECTOR] Failed to load JSON content: {e}")
            
            # Check if we have at least one type of content
            if result['text_content'] or result['json_content']:
                result['success'] = True
                logger.info(f"✅ [ENHANCED_CV_SELECTOR] Successfully loaded CV content for {company}")
            else:
                logger.error(f"❌ [ENHANCED_CV_SELECTOR] No CV content could be loaded for {company}")
            
            return result
            
        except TailoredCVNotFoundError as e:
            logger.error(f"❌ [ENHANCED_CV_SELECTOR] {str(e)}")
            # Propagate for API layer to present explicit error to frontend
            raise
        except Exception as e:
            logger.error(f"❌ [ENHANCED_CV_SELECTOR] Error getting CV content for analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'text_content': None,
                'json_content': None,
                'context': {'error': str(e)},
                'metadata': {
                    'selection_timestamp': datetime.now().isoformat(),
                    'company': company,
                    'is_rerun': is_rerun
                }
            }
    
    def get_latest_cv_paths_for_services(self, company: str = None, is_rerun: bool = False) -> Dict[str, Optional[str]]:
        """
        Compatibility method for existing services that expect the old format
        
        Args:
            company: Company name (if None, uses general logic)
            is_rerun: Whether this is a rerun analysis
            
        Returns:
            Dict with txt_path, json_path, txt_source, json_source keys
        """
        try:
            if company:
                cv_context = self.get_cv_for_analysis(company, is_rerun)
            else:
                # Fallback to original behavior for services that don't specify company
                cv_context = self._get_original_cv_context("Unknown", False)
            
            return {
                'txt_path': str(cv_context.txt_path) if cv_context.txt_path else None,
                'json_path': str(cv_context.json_path) if cv_context.json_path else None,
                'txt_source': cv_context.cv_type,
                'json_source': cv_context.cv_type
            }
            
        except Exception as e:
            logger.error(f"❌ [ENHANCED_CV_SELECTOR] Error in compatibility method: {e}")
            return {
                'txt_path': None,
                'json_path': None,
                'txt_source': 'error',
                'json_source': 'error'
            }
    
    def list_available_cv_versions(self, company: str) -> List[Dict[str, Any]]:
        """
        List all available CV versions for a company
        
        Args:
            company: Company name
            
        Returns:
            List of CV version information
        """
        try:
            versions = []
            
            # Add original CV
            original_json = self.original_path / "original_cv.json"
            if original_json.exists():
                versions.append({
                    'type': 'original',
                    'version': '1.0',
                    'path': str(original_json),
                    'timestamp': None,
                    'created_at': original_json.stat().st_mtime
                })
            
            # Add tailored CV versions
            if self.tailored_path.exists():
                tailored_files = TimestampUtils.find_all_timestamped_files(
                    self.tailored_path, f"{company}_tailored_cv", "json"
                )
                
                for i, file_path in enumerate(tailored_files):
                    timestamp = TimestampUtils.extract_timestamp_from_filename(file_path.name)
                    versions.append({
                        'type': 'tailored',
                        'version': f"{len(tailored_files) - i}.0",  # Reverse order for version numbering
                        'path': str(file_path),
                        'timestamp': timestamp,
                        'created_at': file_path.stat().st_mtime
                    })
            
            # Sort by creation time (newest first)
            versions.sort(key=lambda x: x['created_at'], reverse=True)
            
            return versions
            
        except Exception as e:
            logger.error(f"❌ [ENHANCED_CV_SELECTOR] Error listing CV versions for {company}: {e}")
            return []


# Global instance for backward compatibility
enhanced_dynamic_cv_selector = EnhancedDynamicCVSelector()
