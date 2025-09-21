"""
Job Description Cache Manager

This service manages caching and reuse of JD analysis data to avoid redundant AI calls
when the same JD URL is analyzed multiple times (especially during "Run ATS Test Again").
"""

import logging
import json
from pathlib import Path
from typing import Dict, Optional, List, Any, Tuple
from datetime import datetime
from app.utils.timestamp_utils import TimestampUtils

logger = logging.getLogger(__name__)


class JDCacheData:
    """Container for cached JD analysis data"""
    
    def __init__(self, data: Dict[str, Any]):
        self.jd_url: str = data.get('jd_url', '')
        self.company: str = data.get('company', '')
        self.jd_skills: Dict = data.get('jd_skills', {})
        self.jd_analysis: Dict = data.get('jd_analysis', {})
        self.job_info: Dict = data.get('job_info', {})
        self.jd_original: Dict = data.get('jd_original', {})
        self.cached_at: str = data.get('cached_at', '')
        self.last_used: str = data.get('last_used', '')
        self.use_count: int = data.get('use_count', 0)
        self.cache_valid: bool = data.get('cache_valid', True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'jd_url': self.jd_url,
            'company': self.company,
            'jd_skills': self.jd_skills,
            'jd_analysis': self.jd_analysis,
            'job_info': self.job_info,
            'jd_original': self.jd_original,
            'cached_at': self.cached_at,
            'last_used': self.last_used,
            'use_count': self.use_count,
            'cache_valid': self.cache_valid
        }
    
    def mark_used(self):
        """Mark this cache entry as used"""
        self.last_used = datetime.now().isoformat()
        self.use_count += 1


class JDCacheManager:
    """
    Manages caching and reuse of JD analysis data based on URL comparison
    """
    
    def __init__(self, cv_analysis_base_path: str = None):
        if cv_analysis_base_path is None:
            cv_analysis_base_path = "/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis"
        
        self.base_path = Path(cv_analysis_base_path)
        logger.info(f"🗄️ [JD_CACHE_MANAGER] Initialized with base path: {self.base_path}")
    
    def should_reuse_jd_analysis(self, jd_url: str, company: str) -> bool:
        """
        Check if JD analysis can be reused based on URL comparison
        
        Args:
            jd_url: Job description URL
            company: Company name
            
        Returns:
            True if JD analysis can be reused, False otherwise
        """
        try:
            logger.info(f"🔍 [JD_CACHE_MANAGER] Checking if JD analysis can be reused for {company}")
            logger.info(f"🔍 [JD_CACHE_MANAGER] URL: {jd_url}")
            
            cached_data = self._load_latest_jd_cache(company)
            if not cached_data:
                logger.info(f"❌ [JD_CACHE_MANAGER] No cached JD data found for {company}")
                return False
            
            # Compare URLs (exact match required)
            if cached_data.jd_url == jd_url:
                logger.info(f"✅ [JD_CACHE_MANAGER] URL matches cached data - can reuse JD analysis")
                return True
            else:
                logger.info(f"❌ [JD_CACHE_MANAGER] URL mismatch:")
                logger.info(f"    Cached: {cached_data.jd_url}")
                logger.info(f"    Current: {jd_url}")
                return False
                
        except Exception as e:
            logger.error(f"❌ [JD_CACHE_MANAGER] Error checking JD reuse for {company}: {e}")
            return False
    
    def get_cached_jd_data(self, company: str) -> Optional[JDCacheData]:
        """
        Get cached JD analysis data for a company
        
        Args:
            company: Company name
            
        Returns:
            JDCacheData if found and valid, None otherwise
        """
        try:
            cached_data = self._load_latest_jd_cache(company)
            if cached_data and cached_data.cache_valid:
                # Mark as used
                cached_data.mark_used()
                self._update_cache_usage(company, cached_data)
                
                logger.info(f"✅ [JD_CACHE_MANAGER] Retrieved cached JD data for {company}")
                logger.info(f"📊 [JD_CACHE_MANAGER] Cache usage count: {cached_data.use_count}")
                return cached_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ [JD_CACHE_MANAGER] Error getting cached JD data for {company}: {e}")
            return None
    
    def cache_jd_analysis(self, company: str, jd_url: str, jd_data: Dict[str, Any]) -> bool:
        """
        Cache JD analysis data for future reuse
        
        Args:
            company: Company name
            jd_url: Job description URL
            jd_data: Dictionary containing all JD analysis results
                    Expected keys: jd_skills, jd_analysis, job_info, jd_original
            
        Returns:
            True if caching successful, False otherwise
        """
        try:
            logger.info(f"💾 [JD_CACHE_MANAGER] Caching JD analysis for {company}")
            
            # Create cache data
            cache_data = JDCacheData({
                'jd_url': jd_url,
                'company': company,
                'jd_skills': jd_data.get('jd_skills', {}),
                'jd_analysis': jd_data.get('jd_analysis', {}),
                'job_info': jd_data.get('job_info', {}),
                'jd_original': jd_data.get('jd_original', {}),
                'cached_at': datetime.now().isoformat(),
                'last_used': datetime.now().isoformat(),
                'use_count': 1,
                'cache_valid': True
            })
            
            # Save to file with timestamp
            success = self._save_jd_cache(company, cache_data)
            
            if success:
                logger.info(f"✅ [JD_CACHE_MANAGER] Successfully cached JD analysis for {company}")
            else:
                logger.error(f"❌ [JD_CACHE_MANAGER] Failed to cache JD analysis for {company}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ [JD_CACHE_MANAGER] Error caching JD analysis for {company}: {e}")
            return False
    
    def invalidate_jd_cache(self, company: str) -> bool:
        """
        Invalidate cached JD data for a company (mark as invalid)
        
        Args:
            company: Company name
            
        Returns:
            True if invalidation successful, False otherwise
        """
        try:
            cached_data = self._load_latest_jd_cache(company)
            if cached_data:
                cached_data.cache_valid = False
                return self._save_jd_cache(company, cached_data)
            
            return True  # No cache to invalidate
            
        except Exception as e:
            logger.error(f"❌ [JD_CACHE_MANAGER] Error invalidating JD cache for {company}: {e}")
            return False
    
    def get_cache_stats(self, company: str) -> Dict[str, Any]:
        """
        Get cache statistics for a company
        
        Args:
            company: Company name
            
        Returns:
            Dictionary with cache statistics
        """
        try:
            cached_data = self._load_latest_jd_cache(company)
            if not cached_data:
                return {
                    'has_cache': False,
                    'company': company
                }
            
            return {
                'has_cache': True,
                'company': company,
                'jd_url': cached_data.jd_url,
                'cached_at': cached_data.cached_at,
                'last_used': cached_data.last_used,
                'use_count': cached_data.use_count,
                'cache_valid': cached_data.cache_valid,
                'age_hours': self._calculate_cache_age_hours(cached_data.cached_at)
            }
            
        except Exception as e:
            logger.error(f"❌ [JD_CACHE_MANAGER] Error getting cache stats for {company}: {e}")
            return {
                'has_cache': False,
                'company': company,
                'error': str(e)
            }
    
    def _load_latest_jd_cache(self, company: str) -> Optional[JDCacheData]:
        """Load the latest JD cache data for a company"""
        try:
            company_dir = self.base_path / company
            if not company_dir.exists():
                return None
            
            # Find latest JD cache file
            cache_file = TimestampUtils.find_latest_timestamped_file(
                company_dir, f"{company}_jd_cache", "json"
            )
            
            if not cache_file or not cache_file.exists():
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return JDCacheData(data)
            
        except Exception as e:
            logger.error(f"❌ [JD_CACHE_MANAGER] Error loading JD cache for {company}: {e}")
            return None
    
    def _save_jd_cache(self, company: str, cache_data: JDCacheData) -> bool:
        """Save JD cache data to file"""
        try:
            company_dir = self.base_path / company
            company_dir.mkdir(parents=True, exist_ok=True)
            
            # Create timestamped filename
            timestamp = TimestampUtils.get_timestamp()
            cache_file = company_dir / f"{company}_jd_cache_{timestamp}.json"
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 [JD_CACHE_MANAGER] Saved JD cache to: {cache_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ [JD_CACHE_MANAGER] Error saving JD cache for {company}: {e}")
            return False
    
    def _update_cache_usage(self, company: str, cache_data: JDCacheData) -> bool:
        """Update cache usage statistics"""
        try:
            # Save updated cache data with new usage stats
            return self._save_jd_cache(company, cache_data)
            
        except Exception as e:
            logger.error(f"❌ [JD_CACHE_MANAGER] Error updating cache usage for {company}: {e}")
            return False
    
    def _calculate_cache_age_hours(self, cached_at: str) -> float:
        """Calculate cache age in hours"""
        try:
            cached_time = datetime.fromisoformat(cached_at.replace('Z', '+00:00'))
            current_time = datetime.now()
            age_delta = current_time - cached_time
            return age_delta.total_seconds() / 3600
            
        except Exception as e:
            logger.error(f"❌ [JD_CACHE_MANAGER] Error calculating cache age: {e}")
            return 0.0
    
    def list_all_cached_companies(self) -> List[Dict[str, Any]]:
        """
        List all companies with cached JD data
        
        Returns:
            List of company cache information
        """
        try:
            companies = []
            
            if not self.base_path.exists():
                return companies
            
            for company_dir in self.base_path.iterdir():
                if not company_dir.is_dir() or company_dir.name == 'cvs':
                    continue
                
                # Check for JD cache files
                cache_files = TimestampUtils.find_all_timestamped_files(
                    company_dir, f"{company_dir.name}_jd_cache", "json"
                )
                
                if cache_files:
                    cache_stats = self.get_cache_stats(company_dir.name)
                    companies.append(cache_stats)
            
            # Sort by last used (most recent first)
            companies.sort(key=lambda x: x.get('last_used', ''), reverse=True)
            
            return companies
            
        except Exception as e:
            logger.error(f"❌ [JD_CACHE_MANAGER] Error listing cached companies: {e}")
            return []
    
    def cleanup_old_cache(self, max_age_hours: int = 168) -> Dict[str, Any]:  # Default: 7 days
        """
        Clean up old cache files
        
        Args:
            max_age_hours: Maximum age in hours before cache is considered old
            
        Returns:
            Cleanup statistics
        """
        try:
            cleanup_stats = {
                'companies_checked': 0,
                'files_removed': 0,
                'errors': []
            }
            
            companies = self.list_all_cached_companies()
            
            for company_info in companies:
                cleanup_stats['companies_checked'] += 1
                
                if company_info.get('age_hours', 0) > max_age_hours:
                    try:
                        company = company_info['company']
                        company_dir = self.base_path / company
                        
                        # Find all cache files for this company
                        cache_files = TimestampUtils.find_all_timestamped_files(
                            company_dir, f"{company}_jd_cache", "json"
                        )
                        
                        # Remove old cache files (keep the latest one)
                        for cache_file in cache_files[1:]:  # Skip the first (latest) file
                            cache_file.unlink()
                            cleanup_stats['files_removed'] += 1
                            logger.info(f"🗑️ [JD_CACHE_MANAGER] Removed old cache: {cache_file}")
                            
                    except Exception as e:
                        cleanup_stats['errors'].append(f"Error cleaning {company}: {str(e)}")
            
            logger.info(f"🧹 [JD_CACHE_MANAGER] Cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"❌ [JD_CACHE_MANAGER] Error during cache cleanup: {e}")
            return {'error': str(e)}


# Global instance
jd_cache_manager = JDCacheManager()
