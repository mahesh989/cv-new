"""
Pipeline Deduplicator Service

Prevents multiple pipeline runs for the same company within a time window.
"""

import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import hashlib

logger = logging.getLogger(__name__)


class PipelineDeduplicator:
    """Service to prevent duplicate pipeline runs"""
    
    def __init__(self):
        self.base_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
        self.dedup_window_minutes = 5  # Prevent duplicates within 5 minutes
    
    def _get_session_hash(self, company: str, cv_content: str, jd_content: str) -> str:
        """Generate unique hash for this analysis session"""
        content = f"{company}:{cv_content[:500]}:{jd_content[:500]}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _get_pipeline_state_file(self, company: str) -> Path:
        """Get the pipeline state file path"""
        company_dir = self.base_dir / company
        return company_dir / "pipeline_state.json"
    
    def should_run_pipeline(self, company: str, cv_content: str, jd_content: str) -> Dict[str, Any]:
        """
        Check if pipeline should run based on deduplication rules
        
        Returns:
            Dict with 'should_run' boolean and 'reason' string
        """
        try:
            session_hash = self._get_session_hash(company, cv_content, jd_content)
            state_file = self._get_pipeline_state_file(company)
            
            if not state_file.exists():
                return {
                    "should_run": True, 
                    "reason": "No previous pipeline state found",
                    "session_hash": session_hash
                }
            
            # Read existing state
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            last_run_time = datetime.fromisoformat(state.get("last_run_time", "2000-01-01T00:00:00"))
            last_session_hash = state.get("session_hash", "")
            last_status = state.get("status", "unknown")
            
            time_since_last_run = datetime.now() - last_run_time
            
            # Same session within dedup window - skip
            if (session_hash == last_session_hash and 
                time_since_last_run < timedelta(minutes=self.dedup_window_minutes) and
                last_status == "completed"):
                return {
                    "should_run": False,
                    "reason": f"Same analysis completed {time_since_last_run.total_seconds():.0f}s ago",
                    "session_hash": session_hash,
                    "last_run_time": last_run_time.isoformat()
                }
            
            # Different content or sufficient time passed - run
            return {
                "should_run": True,
                "reason": "Different content or sufficient time elapsed",
                "session_hash": session_hash
            }
            
        except Exception as e:
            logger.error(f"Error checking pipeline deduplication: {e}")
            return {"should_run": True, "reason": f"Error checking state: {e}"}
    
    def mark_pipeline_started(self, company: str, session_hash: str) -> bool:
        """Mark pipeline as started"""
        try:
            state_file = self._get_pipeline_state_file(company)
            state_file.parent.mkdir(parents=True, exist_ok=True)
            
            state = {
                "session_hash": session_hash,
                "last_run_time": datetime.now().isoformat(),
                "status": "running",
                "steps_completed": []
            }
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            
            logger.info(f"[DEDUP] Marked pipeline started for {company}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking pipeline started: {e}")
            return False
    
    def mark_pipeline_completed(self, company: str, session_hash: str, steps_completed: list) -> bool:
        """Mark pipeline as completed"""
        try:
            state_file = self._get_pipeline_state_file(company)
            
            state = {
                "session_hash": session_hash,
                "last_run_time": datetime.now().isoformat(),
                "status": "completed",
                "steps_completed": steps_completed,
                "completion_time": datetime.now().isoformat()
            }
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            
            logger.info(f"[DEDUP] Marked pipeline completed for {company}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking pipeline completed: {e}")
            return False
    
    def mark_pipeline_failed(self, company: str, session_hash: str, error: str) -> bool:
        """Mark pipeline as failed"""
        try:
            state_file = self._get_pipeline_state_file(company)
            
            state = {
                "session_hash": session_hash,
                "last_run_time": datetime.now().isoformat(),
                "status": "failed",
                "error": error,
                "failure_time": datetime.now().isoformat()
            }
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            
            logger.warning(f"[DEDUP] Marked pipeline failed for {company}: {error}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking pipeline failed: {e}")
            return False


# Global instance
pipeline_deduplicator = PipelineDeduplicator()