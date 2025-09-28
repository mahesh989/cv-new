"""
JD Usage Tracker

This service tracks which job descriptions have been used before to ensure
that first-time JD usage always uses the original CV.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Set, Optional
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class JDUsageTracker:
    """
    Tracks JD usage history to determine if a JD has been used before
    """
    
    def __init__(self, base_path: str = "cv-analysis"):
        self.base_path = Path(base_path)
        self.usage_file = self.base_path / "jd_usage_history.json"
        self._usage_data = self._load_usage_data()
    
    def _load_usage_data(self) -> Dict[str, Dict]:
        """Load JD usage history from file"""
        if not self.usage_file.exists():
            return {
                "jd_usage": {},  # jd_hash -> usage_info
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
        
        try:
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"📊 [JD_TRACKER] Loaded JD usage history: {len(data.get('jd_usage', {}))} entries")
                return data
        except Exception as e:
            logger.error(f"❌ [JD_TRACKER] Error loading usage data: {e}")
            return {
                "jd_usage": {},
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
    
    def _save_usage_data(self):
        """Save JD usage history to file"""
        try:
            self.usage_data["last_updated"] = datetime.now().isoformat()
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 [JD_TRACKER] Saved JD usage history")
        except Exception as e:
            logger.error(f"❌ [JD_TRACKER] Error saving usage data: {e}")
    
    @property
    def usage_data(self) -> Dict[str, Dict]:
        """Get current usage data"""
        return self._usage_data
    
    def _generate_jd_hash(self, jd_url: str, jd_text: str = "") -> str:
        """
        Generate a unique hash for JD identification
        Uses URL as primary identifier, with text as fallback
        """
        # Use URL as primary identifier
        if jd_url and jd_url.strip():
            identifier = jd_url.strip()
        elif jd_text and jd_text.strip():
            # Use text content if no URL
            identifier = jd_text.strip()
        else:
            raise ValueError("Either jd_url or jd_text must be provided")
        
        # Generate hash
        return hashlib.md5(identifier.encode('utf-8')).hexdigest()
    
    def is_jd_first_time_usage(self, jd_url: str, jd_text: str = "") -> bool:
        """
        Check if this JD is being used for the first time
        
        Args:
            jd_url: Job description URL
            jd_text: Job description text (fallback if no URL)
            
        Returns:
            True if this is first-time usage, False if JD has been used before
        """
        try:
            jd_hash = self._generate_jd_hash(jd_url, jd_text)
            
            if jd_hash in self.usage_data.get("jd_usage", {}):
                usage_info = self.usage_data["jd_usage"][jd_hash]
                usage_count = usage_info.get("usage_count", 0)
                logger.info(f"🔍 [JD_TRACKER] JD hash {jd_hash[:8]}... found with {usage_count} previous uses")
                return usage_count == 0
            else:
                logger.info(f"🆕 [JD_TRACKER] JD hash {jd_hash[:8]}... not found - first time usage")
                return True
                
        except Exception as e:
            logger.error(f"❌ [JD_TRACKER] Error checking JD usage: {e}")
            # Default to first-time usage on error
            return True
    
    def record_jd_usage(self, jd_url: str, jd_text: str = "", company: str = "", job_title: str = ""):
        """
        Record that a JD has been used
        
        Args:
            jd_url: Job description URL
            jd_text: Job description text
            company: Company name
            job_title: Job title
        """
        try:
            jd_hash = self._generate_jd_hash(jd_url, jd_text)
            current_time = datetime.now().isoformat()
            
            if jd_hash not in self.usage_data["jd_usage"]:
                # First time recording this JD
                self.usage_data["jd_usage"][jd_hash] = {
                    "jd_url": jd_url,
                    "jd_text_preview": jd_text[:200] if jd_text else "",
                    "company": company,
                    "job_title": job_title,
                    "first_used": current_time,
                    "last_used": current_time,
                    "usage_count": 1,
                    "companies_used_with": [company] if company else []
                }
                logger.info(f"📝 [JD_TRACKER] Recorded first usage of JD hash {jd_hash[:8]}... for {company}")
            else:
                # Update existing record
                usage_info = self.usage_data["jd_usage"][jd_hash]
                usage_info["last_used"] = current_time
                usage_info["usage_count"] = usage_info.get("usage_count", 0) + 1
                
                # Add company to list if not already there
                if company and company not in usage_info.get("companies_used_with", []):
                    usage_info["companies_used_with"].append(company)
                
                logger.info(f"📝 [JD_TRACKER] Updated usage count for JD hash {jd_hash[:8]}... to {usage_info['usage_count']}")
            
            # Save the updated data
            self._save_usage_data()
            
        except Exception as e:
            logger.error(f"❌ [JD_TRACKER] Error recording JD usage: {e}")
    
    def get_jd_usage_info(self, jd_url: str, jd_text: str = "") -> Optional[Dict]:
        """
        Get usage information for a JD
        
        Args:
            jd_url: Job description URL
            jd_text: Job description text
            
        Returns:
            Usage information dict or None if not found
        """
        try:
            jd_hash = self._generate_jd_hash(jd_url, jd_text)
            return self.usage_data.get("jd_usage", {}).get(jd_hash)
        except Exception as e:
            logger.error(f"❌ [JD_TRACKER] Error getting JD usage info: {e}")
            return None
    
    def get_all_used_jds(self) -> Dict[str, Dict]:
        """Get all JDs that have been used before"""
        return self.usage_data.get("jd_usage", {})
    
    def clear_usage_history(self):
        """Clear all JD usage history (for testing/reset)"""
        self.usage_data["jd_usage"] = {}
        self._save_usage_data()
        logger.info("🗑️ [JD_TRACKER] Cleared JD usage history")


# Global singleton instance
jd_usage_tracker = JDUsageTracker()
