"""
Skill Analysis File Selector Service

This service handles intelligent file selection for skill analysis, implementing:
1. Original analysis files for fresh analysis
2. Latest analysis files for reruns
3. Support for multiple file formats (JSON/TXT)
4. Version tracking
"""

import logging
import json
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime
from app.utils.timestamp_utils import TimestampUtils

logger = logging.getLogger(__name__)


class SkillAnalysisContext:
    """Container for skill analysis selection context and metadata"""
    
    def __init__(self, data: Dict[str, Any]):
        self.analysis_type: str = data.get('analysis_type', 'original')  # 'original' or 'rerun'
        self.version: str = data.get('version', '1.0')
        self.json_path: Optional[Path] = data.get('json_path')
        self.summary_path: Optional[Path] = data.get('summary_path')
        self.source: str = data.get('source', 'original_analysis')
        self.company: Optional[str] = data.get('company')
        self.timestamp: Optional[str] = data.get('timestamp')
        self.is_rerun: bool = data.get('is_rerun', False)
        self.exists: bool = data.get('exists', False)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'analysis_type': self.analysis_type,
            'version': self.version,
            'json_path': str(self.json_path) if self.json_path else None,
            'summary_path': str(self.summary_path) if self.summary_path else None,
            'source': self.source,
            'company': self.company,
            'timestamp': self.timestamp,
            'is_rerun': self.is_rerun,
            'exists': self.exists
        }


class SkillAnalysisFileSelector:
    """
    Service for intelligent skill analysis file selection with version tracking
    """
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = "/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis"
        
        self.base_path = Path(base_path)
        self.skills_path = self.base_path / "skills"
        self.original_path = self.skills_path / "original"
        self.rerun_path = self.skills_path / "reruns"
        
        # Ensure directories exist
        self.skills_path.mkdir(parents=True, exist_ok=True)
        self.original_path.mkdir(parents=True, exist_ok=True)
        self.rerun_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🔧 [SKILL_SELECTOR] Initialized with base path: {self.base_path}")
    
    def get_analysis_files(self, company: str, is_rerun: bool = False) -> SkillAnalysisContext:
        """
        Select appropriate skill analysis files based on context
        
        Args:
            company: Company name for the analysis
            is_rerun: True if this is a rerun analysis
        
        Returns:
            SkillAnalysisContext with file paths and metadata
        """
        try:
            logger.info(f"🎯 [SKILL_SELECTOR] Selecting analysis for {company}, rerun={is_rerun}")
            
            if is_rerun:
                # Try to use latest rerun analysis for this company
                rerun_context = self._get_latest_rerun_analysis(company)
                if rerun_context.exists:
                    logger.info(f"✅ [SKILL_SELECTOR] Using rerun analysis v{rerun_context.version}")
                    return rerun_context
                else:
                    logger.info(f"⚠️ [SKILL_SELECTOR] No rerun analysis found for {company}")
            
            # Default: Use original analysis
            original_context = self._get_original_analysis_context(company)
            logger.info(f"✅ [SKILL_SELECTOR] Using original analysis for {company}")
            return original_context
            
        except Exception as e:
            logger.error(f"❌ [SKILL_SELECTOR] Error selecting analysis files: {e}")
            return self._get_fallback_context(company, is_rerun, str(e))
    
    def _get_latest_rerun_analysis(self, company: str) -> SkillAnalysisContext:
        """Get the latest rerun analysis files for a company"""
        try:
            company_rerun_path = self.rerun_path / company
            
            if not company_rerun_path.exists():
                return SkillAnalysisContext({
                    'analysis_type': 'rerun',
                    'company': company,
                    'exists': False,
                    'source': 'rerun_not_found'
                })
            
            # Find all analysis files for this company
            json_files = TimestampUtils.find_all_timestamped_files(
                company_rerun_path, f"{company}_skills_analysis", "json"
            )
            summary_files = TimestampUtils.find_all_timestamped_files(
                company_rerun_path, f"{company}_skills_summary", "txt"
            )
            
            if not json_files:
                return SkillAnalysisContext({
                    'analysis_type': 'rerun',
                    'company': company,
                    'exists': False,
                    'source': 'no_rerun_files'
                })
            
            # Get latest files
            latest_json = json_files[0]
            latest_summary = summary_files[0] if summary_files else None
            
            # Extract version information
            timestamp = TimestampUtils.extract_timestamp_from_filename(latest_json.name)
            version = self._calculate_version_from_files(json_files)
            
            return SkillAnalysisContext({
                'analysis_type': 'rerun',
                'version': version,
                'json_path': latest_json,
                'summary_path': latest_summary,
                'source': 'latest_rerun',
                'company': company,
                'timestamp': timestamp,
                'is_rerun': True,
                'exists': True
            })
            
        except Exception as e:
            logger.error(f"❌ [SKILL_SELECTOR] Error getting rerun analysis: {e}")
            return SkillAnalysisContext({
                'analysis_type': 'rerun',
                'company': company,
                'exists': False,
                'source': f'rerun_error: {str(e)}'
            })
    
    def _get_original_analysis_context(self, company: str) -> SkillAnalysisContext:
        """Get original analysis context"""
        try:
            company_path = self.original_path / company
            json_path = company_path / f"{company}_original_skills.json"
            summary_path = company_path / f"{company}_original_summary.txt"
            
            exists = json_path.exists()
            
            return SkillAnalysisContext({
                'analysis_type': 'original',
                'version': '1.0',
                'json_path': json_path if exists else None,
                'summary_path': summary_path if summary_path.exists() else None,
                'source': 'original_analysis',
                'company': company,
                'timestamp': None,
                'is_rerun': False,
                'exists': exists
            })
            
        except Exception as e:
            logger.error(f"❌ [SKILL_SELECTOR] Error getting original analysis: {e}")
            return self._get_fallback_context(company, False, str(e))
    
    def _calculate_version_from_files(self, files: List[Path]) -> str:
        """Calculate version number based on number of analysis files"""
        return f"{len(files)}.0"
    
    def _get_fallback_context(self, company: str, is_rerun: bool, error: str) -> SkillAnalysisContext:
        """Get fallback context when errors occur"""
        return SkillAnalysisContext({
            'analysis_type': 'error',
            'version': '0.0',
            'json_path': None,
            'summary_path': None,
            'source': f'error_fallback: {error}',
            'company': company,
            'timestamp': None,
            'is_rerun': is_rerun,
            'exists': False
        })
    
    def get_analysis_content(self, company: str, is_rerun: bool = False) -> Dict[str, Any]:
        """
        Get analysis content with proper file selection
        
        Args:
            company: Company name
            is_rerun: Whether this is a rerun analysis
            
        Returns:
            Dict containing analysis content and metadata
        """
        try:
            # Get appropriate files based on context
            analysis_context = self.get_analysis_files(company, is_rerun)
            
            result = {
                'success': False,
                'json_content': None,
                'summary_content': None,
                'context': analysis_context.to_dict(),
                'metadata': {
                    'selection_timestamp': datetime.now().isoformat(),
                    'company': company,
                    'is_rerun': is_rerun
                }
            }
            
            if not analysis_context.exists:
                logger.error(f"❌ [SKILL_SELECTOR] Selected analysis does not exist: {analysis_context.source}")
                return result
            
            # Load JSON content
            if analysis_context.json_path and analysis_context.json_path.exists():
                try:
                    with open(analysis_context.json_path, 'r', encoding='utf-8') as f:
                        result['json_content'] = json.load(f)
                    logger.info(f"✅ [SKILL_SELECTOR] Loaded JSON from {analysis_context.json_path}")
                except Exception as e:
                    logger.error(f"❌ [SKILL_SELECTOR] Failed to load JSON: {e}")
            
            # Load summary content
            if analysis_context.summary_path and analysis_context.summary_path.exists():
                try:
                    with open(analysis_context.summary_path, 'r', encoding='utf-8') as f:
                        result['summary_content'] = f.read().strip()
                    logger.info(f"✅ [SKILL_SELECTOR] Loaded summary from {analysis_context.summary_path}")
                except Exception as e:
                    logger.error(f"❌ [SKILL_SELECTOR] Failed to load summary: {e}")
            
            # Check if we have at least JSON content
            if result['json_content']:
                result['success'] = True
                logger.info(f"✅ [SKILL_SELECTOR] Successfully loaded analysis for {company}")
            else:
                logger.error(f"❌ [SKILL_SELECTOR] No analysis content found for {company}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ [SKILL_SELECTOR] Error getting analysis content: {e}")
            return {
                'success': False,
                'error': str(e),
                'json_content': None,
                'summary_content': None,
                'context': {'error': str(e)},
                'metadata': {
                    'selection_timestamp': datetime.now().isoformat(),
                    'company': company,
                    'is_rerun': is_rerun
                }
            }
    
    def list_available_versions(self, company: str) -> List[Dict[str, Any]]:
        """
        List all available analysis versions for a company
        
        Args:
            company: Company name
            
        Returns:
            List of analysis version information
        """
        try:
            versions = []
            
            # Add original analysis if exists
            original_json = self.original_path / company / f"{company}_original_skills.json"
            if original_json.exists():
                versions.append({
                    'type': 'original',
                    'version': '1.0',
                    'path': str(original_json),
                    'timestamp': None,
                    'created_at': original_json.stat().st_mtime
                })
            
            # Add rerun versions
            company_rerun_path = self.rerun_path / company
            if company_rerun_path.exists():
                rerun_files = TimestampUtils.find_all_timestamped_files(
                    company_rerun_path, f"{company}_skills_analysis", "json"
                )
                
                for i, file_path in enumerate(rerun_files):
                    timestamp = TimestampUtils.extract_timestamp_from_filename(file_path.name)
                    versions.append({
                        'type': 'rerun',
                        'version': f"{len(rerun_files) - i}.0",  # Reverse order
                        'path': str(file_path),
                        'timestamp': timestamp,
                        'created_at': file_path.stat().st_mtime
                    })
            
            # Sort by creation time (newest first)
            versions.sort(key=lambda x: x['created_at'], reverse=True)
            
            return versions
            
        except Exception as e:
            logger.error(f"❌ [SKILL_SELECTOR] Error listing versions for {company}: {e}")
            return []


# Global instance
skill_analysis_file_selector = SkillAnalysisFileSelector()