"""
Job Queue System for handling long-running operations that can survive tab switches
"""
import asyncio
import json
import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional, Callable
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor, Future
import logging
from dataclasses import dataclass, asdict
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Job:
    id: str
    job_type: str
    status: JobStatus
    data: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['started_at'] = self.started_at.isoformat() if self.started_at else None
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data

class JobQueue:
    """Thread-safe job queue system for long-running operations"""
    
    def __init__(self, max_workers: int = 4, persistence_file: str = "job_queue.json"):
        self.jobs: Dict[str, Job] = {}
        self.job_handlers: Dict[str, Callable] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running_futures: Dict[str, Future] = {}
        self.persistence_file = Path(persistence_file)
        self.lock = threading.RLock()
        
        # Load persisted jobs
        self._load_jobs()
        
        # Start cleanup task
        self._start_cleanup_task()
        
        logger.info(f"JobQueue initialized with {max_workers} workers")
    
    def register_handler(self, job_type: str, handler: Callable):
        """Register a handler function for a specific job type"""
        self.job_handlers[job_type] = handler
        logger.info(f"Registered handler for job type: {job_type}")
    
    def submit_job(self, job_type: str, job_data: Dict[str, Any]) -> str:
        """Submit a new job to the queue"""
        job_id = str(uuid4())
        
        job = Job(
            id=job_id,
            job_type=job_type,
            status=JobStatus.PENDING,
            data=job_data
        )
        
        with self.lock:
            self.jobs[job_id] = job
            self._persist_jobs()
        
        # Submit to thread pool
        if job_type in self.job_handlers:
            future = self.executor.submit(self._execute_job, job_id)
            self.running_futures[job_id] = future
        else:
            self._mark_job_failed(job_id, f"No handler registered for job type: {job_type}")
        
        logger.info(f"Submitted job {job_id} of type {job_type}")
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a job"""
        with self.lock:
            job = self.jobs.get(job_id)
            return job.to_dict() if job else None
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or running job"""
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                return False
            
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                return False
            
            # Cancel the future if it's running
            future = self.running_futures.get(job_id)
            if future:
                future.cancel()
                self.running_futures.pop(job_id, None)
            
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now()
            self._persist_jobs()
            
            logger.info(f"Cancelled job {job_id}")
            return True
    
    def _execute_job(self, job_id: str):
        """Execute a job in the background"""
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                return
            
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now()
            self._persist_jobs()
        
        logger.info(f"Starting execution of job {job_id}")
        
        try:
            handler = self.job_handlers[job.job_type]
            result = handler(job.data, lambda p: self._update_job_progress(job_id, p))
            
            with self.lock:
                job.status = JobStatus.COMPLETED
                job.result = result
                job.completed_at = datetime.now()
                job.progress = 100.0
                self._persist_jobs()
            
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {str(e)}")
            self._mark_job_failed(job_id, str(e))
        
        finally:
            self.running_futures.pop(job_id, None)
    
    def _update_job_progress(self, job_id: str, progress: float):
        """Update job progress"""
        with self.lock:
            job = self.jobs.get(job_id)
            if job:
                job.progress = min(100.0, max(0.0, progress))
                self._persist_jobs()
    
    def _mark_job_failed(self, job_id: str, error: str):
        """Mark a job as failed"""
        with self.lock:
            job = self.jobs.get(job_id)
            if job:
                job.status = JobStatus.FAILED
                job.error = error
                job.completed_at = datetime.now()
                self._persist_jobs()
    
    def _persist_jobs(self):
        """Persist jobs to file"""
        try:
            # Only persist recent jobs (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            recent_jobs = {
                job_id: job for job_id, job in self.jobs.items()
                if job.created_at >= cutoff_time
            }
            
            serializable_jobs = {
                job_id: job.to_dict() for job_id, job in recent_jobs.items()
            }
            
            with open(self.persistence_file, 'w') as f:
                json.dump(serializable_jobs, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist jobs: {e}")
    
    def _load_jobs(self):
        """Load jobs from file"""
        try:
            if self.persistence_file.exists():
                with open(self.persistence_file, 'r') as f:
                    data = json.load(f)
                
                for job_id, job_data in data.items():
                    job = Job(
                        id=job_data['id'],
                        job_type=job_data['job_type'],
                        status=JobStatus(job_data['status']),
                        data=job_data['data'],
                        result=job_data.get('result'),
                        error=job_data.get('error'),
                        created_at=datetime.fromisoformat(job_data['created_at']) if job_data.get('created_at') else None,
                        started_at=datetime.fromisoformat(job_data['started_at']) if job_data.get('started_at') else None,
                        completed_at=datetime.fromisoformat(job_data['completed_at']) if job_data.get('completed_at') else None,
                        progress=job_data.get('progress', 0.0)
                    )
                    self.jobs[job_id] = job
                
                logger.info(f"Loaded {len(self.jobs)} jobs from persistence")
        except Exception as e:
            logger.error(f"Failed to load jobs: {e}")
    
    def _start_cleanup_task(self):
        """Start background task to clean up old jobs"""
        def cleanup():
            while True:
                try:
                    cutoff_time = datetime.now() - timedelta(hours=24)
                    with self.lock:
                        old_job_ids = [
                            job_id for job_id, job in self.jobs.items()
                            if job.created_at < cutoff_time and 
                            job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
                        ]
                        
                        for job_id in old_job_ids:
                            self.jobs.pop(job_id, None)
                            self.running_futures.pop(job_id, None)
                        
                        if old_job_ids:
                            self._persist_jobs()
                            logger.info(f"Cleaned up {len(old_job_ids)} old jobs")
                    
                    # Sleep for 1 hour
                    time.sleep(3600)
                except Exception as e:
                    logger.error(f"Error in cleanup task: {e}")
                    time.sleep(60)  # Sleep for 1 minute on error
        
        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self.lock:
            stats = {
                'total_jobs': len(self.jobs),
                'pending': len([j for j in self.jobs.values() if j.status == JobStatus.PENDING]),
                'running': len([j for j in self.jobs.values() if j.status == JobStatus.RUNNING]),
                'completed': len([j for j in self.jobs.values() if j.status == JobStatus.COMPLETED]),
                'failed': len([j for j in self.jobs.values() if j.status == JobStatus.FAILED]),
                'cancelled': len([j for j in self.jobs.values() if j.status == JobStatus.CANCELLED]),
            }
        return stats
    
    def shutdown(self):
        """Shutdown the job queue"""
        logger.info("Shutting down job queue")
        self.executor.shutdown(wait=True)

# Global job queue instance
job_queue = JobQueue()

# Job handler functions
def analyze_match_handler(data: Dict[str, Any], progress_callback: Callable[[float], None]) -> Dict[str, Any]:
    """Handler for analyze_match jobs"""
    from .ai_matcher import analyze_match_fit
    from .cv_parser import extract_text_from_pdf, extract_text_from_docx
    import os
    
    progress_callback(10.0)
    
    cv_filename = data['cv_filename']
    jd_text = data['jd_text']
    prompt = data.get('prompt', '')
    
    # Extract CV text
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
    cv_path = os.path.join(upload_dir, cv_filename)
    
    if not os.path.exists(cv_path):
        raise Exception(f"CV file not found: {cv_filename}")
    
    progress_callback(20.0)
    
    ext = os.path.splitext(cv_filename)[1].lower()
    if ext == ".pdf":
        cv_text = extract_text_from_pdf(cv_path)
    elif ext == ".docx":
        cv_text = extract_text_from_docx(cv_path)
    else:
        raise Exception("Unsupported CV format")
    
    progress_callback(40.0)
    
    # Run analysis
    company_name = "Background_Job_Analysis"
    result = analyze_match_fit(cv_text, jd_text, company_name)
    
    progress_callback(100.0)
    
    return result

def ats_test_handler(data: Dict[str, Any], progress_callback: Callable[[float], None]) -> Dict[str, Any]:
    """Handler for ATS test jobs"""
    from .ats_enhanced_scorer import enhanced_ats_test
    
    progress_callback(10.0)
    
    cv_filename = data['cv_filename']
    jd_text = data['jd_text']
    prompt = data.get('prompt', '')
    cv_type = data.get('cv_type', 'pdf')
    
    progress_callback(30.0)
    
    # Run ATS test
    result = enhanced_ats_test(
        cv_filename=cv_filename,
        jd_text=jd_text,
        prompt=prompt,
        cv_type=cv_type
    )
    
    progress_callback(100.0)
    
    return result

def preliminary_analysis_handler(data: Dict[str, Any], progress_callback: Callable[[float], None]) -> Dict[str, Any]:
    """Handler for preliminary analysis jobs"""
    from .ats_rules_engine import extract_skills_unified
    
    progress_callback(20.0)
    
    cv_filename = data['cv_filename']
    jd_text = data['jd_text']
    
    # Extract CV skills
    cv_skills = extract_skills_unified(mode="cv", cv_filename=cv_filename)
    progress_callback(50.0)
    
    # Extract JD skills
    jd_skills = extract_skills_unified(mode="jd", jd_text=jd_text)
    progress_callback(80.0)
    
    result = {
        'cv_analysis': cv_skills,
        'jd_analysis': jd_skills,
        'status': 'completed'
    }
    
    progress_callback(100.0)
    
    return result

# Register handlers
job_queue.register_handler('analyze_match', analyze_match_handler)
job_queue.register_handler('ats_test', ats_test_handler)
job_queue.register_handler('preliminary_analysis', preliminary_analysis_handler)
