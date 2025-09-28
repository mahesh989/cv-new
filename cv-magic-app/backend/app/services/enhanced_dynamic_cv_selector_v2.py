"""
Enhanced Dynamic CV Selector V2

This version supports timestamped CV files and maintains backward compatibility.
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Any, List
from datetime import datetime
from ..exceptions.cv_exceptions import (
    CVError, CVNotFoundError, EmptyContentError,
    CVFormatError, CVVersionError, CVSelectionError
)

logger = logging.getLogger(__name__)

# Constants
MIN_CV_TEXT_LENGTH = 1000  # Minimum characters for CV text
MIN_CV_JSON_SIZE = 500    # Minimum bytes for CV JSON


class CVSelectionContext:
    """Context for CV file selection"""
    
    def __init__(self, data: Dict[str, Any]):
        self.cv_type: str = data.get('cv_type', 'original')  # 'original' or 'tailored'
        self.version: str = data.get('version', '1.0')
        self.json_path: Optional[Path] = data.get('json_path')
        self.txt_path: Optional[Path] = data.get('txt_path')
        self.timestamp: Optional[str] = data.get('timestamp')
        self.exists: bool = data.get('exists', False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'cv_type': self.cv_type,
            'version': self.version,
            'json_path': str(self.json_path) if self.json_path else None,
            'txt_path': str(self.txt_path) if self.txt_path else None,
            'timestamp': self.timestamp,
            'exists': self.exists
        }


class EnhancedDynamicCVSelectorV2:
    """Enhanced CV selector with timestamp support"""
    
    def __init__(self, base_path: Optional[str] = None):
        if base_path is None:
            base_path = "cv-analysis"
        
        self.base_path = Path(base_path)
        self.cvs_path = self.base_path / "cvs"
        self.original_path = self.cvs_path / "original"
        self.tailored_path = self.cvs_path / "tailored"
    
    def get_cv_files(
        self,
        company: Optional[str] = None,
        prefer_tailored: bool = False,
        strict: bool = True
    ) -> CVSelectionContext:
        """
        Get appropriate CV files based on context
        
        Args:
            company: Optional company name for tailored CV
            prefer_tailored: Whether to prefer tailored version if available
            strict: Whether to raise errors instead of falling back
        
        Raises:
            CVNotFoundError: When no CV files are found
            EmptyContentError: When CV content is insufficient
            CVFormatError: When CV files are in wrong format
            CVVersionError: When there's a version mismatch
            CVSelectionError: When CV selection fails
        """
        try:
            # Check tailored CV first if company is specified and tailored is preferred
            if company and prefer_tailored:
                tailored_context = self._get_latest_tailored_cv(company)
                if tailored_context.exists:
                    logger.info(f"Using tailored CV for {company}")
                    if strict:
                        self._validate_cv_content(tailored_context)
                    return tailored_context
                elif strict:
                    raise CVNotFoundError(f"No tailored CV found for {company}")
            
            # Get latest original CV
            original_context = self._get_latest_original_cv()
            if original_context.exists:
                logger.info("Using latest original CV")
                if strict:
                    self._validate_cv_content(original_context)
                return original_context
            
            # Try non-timestamped original only if not strict
            if not strict:
                fallback_context = self._get_fallback_original_cv()
                if fallback_context.exists:
                    logger.info("Using fallback original CV")
                    self._validate_cv_content(fallback_context)
                    return fallback_context
            
            # If we get here in strict mode, no valid CV was found
            raise CVNotFoundError("No valid CV files found")
            
        except CVError as e:
            # Re-raise CV-specific errors
            raise
        except Exception as e:
            # Wrap other errors
            raise CVSelectionError(f"Error selecting CV files: {str(e)}") from e
    
    def _get_latest_original_cv(self) -> CVSelectionContext:
        """Get latest timestamped original CV"""
        try:
            # Find all timestamped JSON files
            json_files = sorted(
                self.original_path.glob("original_cv_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            if not json_files:
                return CVSelectionContext({
                    'cv_type': 'original',
                    'exists': False
                })
            
            # Get latest JSON and corresponding TXT
            latest_json = json_files[0]
            txt_path = latest_json.with_suffix('.txt')
            
            # Verify both files exist
            if not txt_path.exists():
                raise CVFormatError(
                    f"Missing TXT file for {latest_json.name}"
                )
            
            # Extract timestamp from filename
            try:
                timestamp = latest_json.stem.split('_')[-1]
            except Exception as e:
                raise CVVersionError(
                    f"Invalid timestamp format in {latest_json.name}"
                ) from e
            
            # Check file sizes
            if latest_json.stat().st_size < MIN_CV_JSON_SIZE:
                raise EmptyContentError(
                    f"JSON file too small: {latest_json.name} "
                    f"({latest_json.stat().st_size} bytes)"
                )
            
            if txt_path.stat().st_size < MIN_CV_TEXT_LENGTH:
                raise EmptyContentError(
                    f"Text file too small: {txt_path.name} "
                    f"({txt_path.stat().st_size} bytes)"
                )
            
            return CVSelectionContext({
                'cv_type': 'original',
                'version': '1.0',
                'json_path': latest_json,
                'txt_path': txt_path,
                'timestamp': timestamp,
                'exists': True
            })
            
        except CVError:
            # Re-raise CV-specific errors
            raise
        except Exception as e:
            raise CVSelectionError(f"Error getting latest original CV: {str(e)}") from e
    
    def _validate_cv_content(self, context: CVSelectionContext) -> None:
        """Validate CV content for both JSON and TXT formats"""
        if not context.exists:
            raise CVNotFoundError("Cannot validate non-existent CV")
        
        if not context.json_path or not context.txt_path:
            raise CVFormatError("Both JSON and TXT files are required")
        
        if not context.json_path.exists():
            raise CVNotFoundError(f"JSON file not found: {context.json_path}")
        
        if not context.txt_path.exists():
            raise CVNotFoundError(f"TXT file not found: {context.txt_path}")
        
        # Check JSON content
        try:
            with open(context.json_path, 'r', encoding='utf-8') as f:
                json_content = json.load(f)
                
            # Verify JSON structure
            required_fields = ['metadata', 'personal_information', 'experience']
            missing_fields = [f for f in required_fields if f not in json_content]
            if missing_fields:
                raise CVFormatError(
                    f"Missing required fields in JSON: {', '.join(missing_fields)}"
                )
        except json.JSONDecodeError as e:
            raise CVFormatError(f"Invalid JSON format: {str(e)}")
        
        # Check file sizes
        json_size = context.json_path.stat().st_size
        txt_size = context.txt_path.stat().st_size
        
        if json_size < MIN_CV_JSON_SIZE:
            raise EmptyContentError(
                f"JSON file too small: {context.json_path.name} "
                f"({json_size} bytes)"
            )
        
        if txt_size < MIN_CV_TEXT_LENGTH:
            raise EmptyContentError(
                f"Text file too small: {context.txt_path.name} "
                f"({txt_size} bytes)"
            )
        
        # Check text content
        with open(context.txt_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
            
        # Check for common CV sections in text
        required_sections = ['experience', 'education', 'skills']
        found_sections = [s for s in required_sections if s.lower() in text_content.lower()]
        if len(found_sections) < 2:  # At least 2 main sections should be present
            raise CVFormatError(
                f"CV text missing main sections. Found only: {', '.join(found_sections)}"
            )
    
    def _get_fallback_original_cv(self) -> CVSelectionContext:
        """Get non-timestamped original CV as fallback"""
        json_path = self.original_path / "original_cv.json"
        txt_path = self.original_path / "original_cv.txt"
        
        exists = json_path.exists() or txt_path.exists()
        
        return CVSelectionContext({
            'cv_type': 'original',
            'version': '1.0',
            'json_path': json_path if json_path.exists() else None,
            'txt_path': txt_path if txt_path.exists() else None,
            'timestamp': None,
            'exists': exists
        })
    
    def _get_latest_tailored_cv(self, company: str) -> CVSelectionContext:
        """Get latest tailored CV for a company"""
        try:
            # Find all tailored CVs for this company in company-specific folder
            company_tailored_path = self.base_path / "applied_companies" / company
            json_files = sorted(
                company_tailored_path.glob(f"{company}_tailored_cv_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            if not json_files:
                return CVSelectionContext({
                    'cv_type': 'tailored',
                    'exists': False
                })
            
            # Get latest JSON and corresponding TXT
            latest_json = json_files[0]
            txt_path = latest_json.with_suffix('.txt')
            
            # Extract timestamp from filename
            try:
                timestamp = latest_json.stem.split('_')[-1]
            except:
                timestamp = None
            
            return CVSelectionContext({
                'cv_type': 'tailored',
                'version': str(len(json_files)) + '.0',
                'json_path': latest_json,
                'txt_path': txt_path if txt_path.exists() else None,
                'timestamp': timestamp,
                'exists': True
            })
            
        except Exception as e:
            logger.error(f"Error getting tailored CV for {company}: {e}")
            return CVSelectionContext({
                'cv_type': 'tailored',
                'exists': False
            })
    
    def get_all_cv_versions(self, company: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all CV versions (both original and tailored)
        
        Args:
            company: Optional company name for tailored CVs
        """
        versions = []
        
        try:
            # Get original CV versions
            original_files = sorted(
                self.original_path.glob("original_cv_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            for i, json_file in enumerate(original_files):
                txt_file = json_file.with_suffix('.txt')
                try:
                    timestamp = json_file.stem.split('_')[-1]
                except:
                    timestamp = None
                
                versions.append({
                    'type': 'original',
                    'version': f"{len(original_files) - i}.0",
                    'json_path': str(json_file),
                    'txt_path': str(txt_file) if txt_file.exists() else None,
                    'timestamp': timestamp,
                    'created_at': json_file.stat().st_mtime
                })
            
            # Add non-timestamped original if it exists
            fallback_json = self.original_path / "original_cv.json"
            fallback_txt = self.original_path / "original_cv.txt"
            if fallback_json.exists() or fallback_txt.exists():
                versions.append({
                    'type': 'original',
                    'version': '1.0',
                    'json_path': str(fallback_json) if fallback_json.exists() else None,
                    'txt_path': str(fallback_txt) if fallback_txt.exists() else None,
                    'timestamp': None,
                    'created_at': max(
                        fallback_json.stat().st_mtime if fallback_json.exists() else 0,
                        fallback_txt.stat().st_mtime if fallback_txt.exists() else 0
                    )
                })
            
            # Get tailored CV versions if company specified from company-specific folder
            if company:
                company_tailored_path = self.base_path / "applied_companies" / company
                tailored_files = sorted(
                    company_tailored_path.glob(f"{company}_tailored_cv_*.json"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True
                )
                
                for i, json_file in enumerate(tailored_files):
                    txt_file = json_file.with_suffix('.txt')
                    try:
                        timestamp = json_file.stem.split('_')[-1]
                    except:
                        timestamp = None
                    
                    versions.append({
                        'type': 'tailored',
                        'version': f"{len(tailored_files) - i}.0",
                        'json_path': str(json_file),
                        'txt_path': str(txt_file) if txt_file.exists() else None,
                        'timestamp': timestamp,
                        'created_at': json_file.stat().st_mtime
                    })
            
            # Sort all versions by creation time
            versions.sort(key=lambda x: x['created_at'], reverse=True)
            
            return versions
            
        except Exception as e:
            logger.error(f"Error listing CV versions: {e}")
            return []
    
    def get_latest_cv_paths_for_services(
        self,
        company: Optional[str] = None,
        prefer_tailored: bool = False
    ) -> Dict[str, str]:
        """
        Get latest CV paths for compatibility with existing services
        
        Args:
            company: Optional company name
            prefer_tailored: Whether to prefer tailored version
        """
        cv_files = self.get_cv_files(company, prefer_tailored)
        
        return {
            'json_path': str(cv_files.json_path) if cv_files.json_path else None,
            'txt_path': str(cv_files.txt_path) if cv_files.txt_path else None,
            'source': cv_files.cv_type,
            'timestamp': cv_files.timestamp
        }


# Global instance
enhanced_dynamic_cv_selector_v2 = EnhancedDynamicCVSelectorV2()
