#!/usr/bin/env python3
"""
File Integrity Checker
Ensures ATS tests always read the latest CV files and prevents accuracy issues
"""

import os
import hashlib
import logging
from datetime import datetime
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)

class FileIntegrityChecker:
    """
    Ensures file integrity and version control for CV testing accuracy
    """
    
    def __init__(self, uploads_dir: str = "uploads", tailored_dir: str = "tailored_cvs"):
        self.uploads_dir = uploads_dir
        self.tailored_dir = tailored_dir
        self.file_cache = {}  # filename -> {hash, timestamp, content_preview}
        
    def get_file_hash(self, file_path: str) -> Optional[str]:
        """
        Get SHA256 hash of file for integrity checking
        """
        try:
            if not os.path.exists(file_path):
                return None
                
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.error(f"❌ [INTEGRITY] Failed to hash file {file_path}: {e}")
            return None
    
    def get_file_metadata(self, file_path: str) -> Dict:
        """
        Get comprehensive file metadata
        """
        try:
            if not os.path.exists(file_path):
                return {"exists": False}
            
            stat = os.stat(file_path)
            file_hash = self.get_file_hash(file_path)
            
            # Get content preview for debugging
            content_preview = ""
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content_preview = f.read(500)  # First 500 chars
            except:
                content_preview = "Binary file or read error"
            
            return {
                "exists": True,
                "size": stat.st_size,
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "hash": file_hash,
                "content_preview": content_preview,
                "full_path": file_path
            }
        except Exception as e:
            logger.error(f"❌ [INTEGRITY] Failed to get metadata for {file_path}: {e}")
            return {"exists": False, "error": str(e)}
    
    def verify_cv_file_integrity(self, filename: str, cv_type: str = 'tailored') -> Dict:
        """
        Verify CV file integrity and return detailed status
        """
        if cv_type == 'tailored':
            file_path = os.path.join(self.tailored_dir, filename)
        else:
            file_path = os.path.join(self.uploads_dir, filename)
        
        metadata = self.get_file_metadata(file_path)
        
        # Check if file was recently modified (within last hour)
        recently_modified = False
        if metadata["exists"]:
            try:
                mod_time = datetime.fromisoformat(metadata["modified_time"])
                time_diff = datetime.now() - mod_time
                recently_modified = time_diff.total_seconds() < 3600  # 1 hour
            except:
                pass
        
        # Check cache for changes
        cache_key = f"{cv_type}_{filename}"
        file_changed = True
        if cache_key in self.file_cache:
            old_hash = self.file_cache[cache_key].get("hash")
            file_changed = old_hash != metadata.get("hash")
        
        # Update cache
        if metadata["exists"]:
            self.file_cache[cache_key] = {
                "hash": metadata["hash"],
                "timestamp": datetime.now().isoformat(),
                "content_preview": metadata["content_preview"]
            }
        
        integrity_status = {
            "filename": filename,
            "cv_type": cv_type,
            "file_exists": metadata["exists"],
            "file_path": file_path,
            "recently_modified": recently_modified,
            "file_changed_since_last_check": file_changed,
            "metadata": metadata,
            "integrity_score": self._calculate_integrity_score(metadata, recently_modified, file_changed)
        }
        
        # Log integrity status
        if metadata["exists"]:
            logger.info(f"✅ [INTEGRITY] {filename} ({cv_type}): Size={metadata['size']}B, Hash={metadata['hash'][:8]}...")
            if recently_modified:
                logger.info(f"🔄 [INTEGRITY] File was recently modified: {metadata['modified_time']}")
            if file_changed:
                logger.info(f"🔄 [INTEGRITY] File content changed since last check")
        else:
            logger.error(f"❌ [INTEGRITY] File not found: {file_path}")
        
        return integrity_status
    
    def _calculate_integrity_score(self, metadata: Dict, recently_modified: bool, file_changed: bool) -> int:
        """
        Calculate integrity score (0-100)
        """
        if not metadata["exists"]:
            return 0
        
        score = 100
        
        # Penalize if file doesn't exist
        if not metadata["exists"]:
            score = 0
        
        # Bonus for recent modification (suggests fresh content)
        if recently_modified:
            score = min(100, score + 10)
        
        # Check file size (empty files are suspicious)
        file_size = metadata.get("size", 0)
        if file_size < 100:  # Less than 100 bytes
            score -= 30
        elif file_size > 1000000:  # More than 1MB (unusually large for CV)
            score -= 10
        
        return max(0, score)
    
    def validate_cv_content_against_keywords(self, cv_content: str, expected_keywords: list) -> Dict:
        """
        Validate that CV content actually contains expected keywords
        """
        cv_lower = cv_content.lower()
        
        found_keywords = []
        missing_keywords = []
        
        for keyword in expected_keywords:
            if keyword.lower() in cv_lower:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        accuracy_percentage = (len(found_keywords) / len(expected_keywords) * 100) if expected_keywords else 100
        
        validation_result = {
            "total_keywords": len(expected_keywords),
            "found_keywords": found_keywords,
            "missing_keywords": missing_keywords,
            "accuracy_percentage": round(accuracy_percentage, 1),
            "content_length": len(cv_content),
            "validation_passed": len(missing_keywords) == 0
        }
        
        logger.info(f"🔍 [CONTENT-VALIDATION] Keywords: {len(found_keywords)}/{len(expected_keywords)} found ({accuracy_percentage:.1f}%)")
        if missing_keywords:
            logger.warning(f"⚠️ [CONTENT-VALIDATION] Missing keywords: {missing_keywords}")
        
        return validation_result
    
    def ensure_file_freshness(self, filename: str, cv_type: str = 'tailored', max_age_minutes: int = 60) -> bool:
        """
        Ensure file is fresh (modified within specified time)
        """
        metadata = self.get_file_metadata(
            os.path.join(self.tailored_dir if cv_type == 'tailored' else self.uploads_dir, filename)
        )
        
        if not metadata["exists"]:
            return False
        
        try:
            mod_time = datetime.fromisoformat(metadata["modified_time"])
            age_minutes = (datetime.now() - mod_time).total_seconds() / 60
            is_fresh = age_minutes <= max_age_minutes
            
            if is_fresh:
                logger.info(f"✅ [FRESHNESS] {filename} is fresh ({age_minutes:.1f} minutes old)")
            else:
                logger.warning(f"⚠️ [FRESHNESS] {filename} is stale ({age_minutes:.1f} minutes old)")
            
            return is_fresh
        except:
            return False
    
    def debug_file_system_state(self) -> Dict:
        """
        Debug file system state for troubleshooting
        """
        debug_info = {
            "uploads_dir": {
                "path": self.uploads_dir,
                "exists": os.path.exists(self.uploads_dir),
                "files": []
            },
            "tailored_dir": {
                "path": self.tailored_dir,
                "exists": os.path.exists(self.tailored_dir),
                "files": []
            },
            "cache_size": len(self.file_cache),
            "timestamp": datetime.now().isoformat()
        }
        
        # List files in uploads directory
        if os.path.exists(self.uploads_dir):
            try:
                for file in os.listdir(self.uploads_dir):
                    file_path = os.path.join(self.uploads_dir, file)
                    if os.path.isfile(file_path):
                        debug_info["uploads_dir"]["files"].append({
                            "name": file,
                            "size": os.path.getsize(file_path),
                            "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                        })
            except Exception as e:
                debug_info["uploads_dir"]["error"] = str(e)
        
        # List files in tailored directory
        if os.path.exists(self.tailored_dir):
            try:
                for file in os.listdir(self.tailored_dir):
                    file_path = os.path.join(self.tailored_dir, file)
                    if os.path.isfile(file_path):
                        debug_info["tailored_dir"]["files"].append({
                            "name": file,
                            "size": os.path.getsize(file_path),
                            "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                        })
            except Exception as e:
                debug_info["tailored_dir"]["error"] = str(e)
        
        logger.info(f"🔧 [DEBUG] File system state: {len(debug_info['uploads_dir']['files'])} uploads, {len(debug_info['tailored_dir']['files'])} tailored")
        
        return debug_info


# Initialize global instance
file_integrity_checker = FileIntegrityChecker() 