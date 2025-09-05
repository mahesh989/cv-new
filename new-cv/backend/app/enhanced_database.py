"""
Enhanced database and storage management for CV Agent
"""
import os
import json
import uuid
import sqlite3
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import shutil

from .models.enhanced import (
    CVUploadResponse, CVInfo, JDExtractionResponse, ProcessingStatus, FileType,
    JDInfo, AnalysisResponse, AnalysisInfo, JDSource, AnalysisType
)

class DatabaseManager:
    """Enhanced database manager with SQLite backend and file storage"""
    
    def __init__(self, db_path: str = "cv_agent.db", upload_dir: str = "uploads"):
        self.db_path = db_path
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.upload_dir / "cvs").mkdir(exist_ok=True)
        (self.upload_dir / "temp").mkdir(exist_ok=True)
        
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # CVs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cvs (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    title TEXT,
                    description TEXT,
                    file_size INTEGER NOT NULL,
                    file_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    upload_date TEXT NOT NULL,
                    processing_status TEXT NOT NULL DEFAULT 'pending',
                    text_content TEXT,
                    text_length INTEGER,
                    file_hash TEXT,
                    metadata TEXT
                )
            """)
            
            # Job descriptions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_descriptions (
                    id TEXT PRIMARY KEY,
                    source_url TEXT,
                    source_type TEXT NOT NULL,
                    extracted_text TEXT NOT NULL,
                    extraction_date TEXT NOT NULL,
                    processing_status TEXT NOT NULL DEFAULT 'completed',
                    text_length INTEGER NOT NULL,
                    text_hash TEXT,
                    metadata TEXT
                )
            """)
            
            # Analysis results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id TEXT PRIMARY KEY,
                    cv_id TEXT NOT NULL,
                    jd_id TEXT,
                    analysis_result TEXT NOT NULL,
                    ai_model_used TEXT NOT NULL,
                    processing_time REAL NOT NULL,
                    analysis_date TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (cv_id) REFERENCES cvs (id),
                    FOREIGN KEY (jd_id) REFERENCES job_descriptions (id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cvs_upload_date ON cvs(upload_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cvs_status ON cvs(processing_status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_jds_extraction_date ON job_descriptions(extraction_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_cv_id ON analysis_results(cv_id)")
            
            conn.commit()
    
    def _generate_id(self) -> str:
        """Generate unique ID"""
        return str(uuid.uuid4())
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _calculate_text_hash(self, text: str) -> str:
        """Calculate MD5 hash of text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    # CV Management Methods
    
    def save_cv(self, filename: str, file_content: bytes, title: Optional[str] = None, 
                description: Optional[str] = None) -> CVUploadResponse:
        """Save CV file and create database record"""
        cv_id = self._generate_id()
        file_extension = Path(filename).suffix.lower().lstrip('.')
        
        # Determine file type
        if file_extension == 'pdf':
            file_type = FileType.PDF
        elif file_extension == 'docx':
            file_type = FileType.DOCX
        else:
            file_type = FileType.TXT
        
        # Save file
        safe_filename = f"{cv_id}_{filename}"
        file_path = self.upload_dir / "cvs" / safe_filename
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        file_size = len(file_content)
        file_hash = self._calculate_file_hash(file_path)
        upload_date = datetime.utcnow().isoformat()
        
        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cvs (id, filename, title, description, file_size, file_type, 
                               file_path, upload_date, processing_status, file_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cv_id, filename, title, description, file_size, file_type.value,
                  str(file_path), upload_date, ProcessingStatus.PENDING.value, file_hash))
            conn.commit()
        
        return CVUploadResponse(
            id=cv_id,
            filename=filename,
            title=title,
            description=description,
            file_size=file_size,
            file_type=file_type,
            upload_date=datetime.fromisoformat(upload_date),
            processing_status=ProcessingStatus.PENDING
        )
    
    def get_cv(self, cv_id: str) -> Optional[CVInfo]:
        """Get CV information by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, filename, title, description, file_size, file_type,
                       upload_date, processing_status, text_length
                FROM cvs WHERE id = ?
            """, (cv_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return CVInfo(
                id=row[0],
                filename=row[1],
                title=row[2],
                description=row[3],
                file_size=row[4],
                file_type=FileType(row[5]),
                upload_date=datetime.fromisoformat(row[6]),
                processing_status=ProcessingStatus(row[7]),
                text_length=row[8]
            )
    
    def list_cvs(self, page: int = 1, limit: int = 10) -> List[CVInfo]:
        """List CVs with pagination"""
        offset = (page - 1) * limit
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, filename, title, description, file_size, file_type,
                       upload_date, processing_status, text_length
                FROM cvs 
                ORDER BY upload_date DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            rows = cursor.fetchall()
            return [CVInfo(
                id=row[0],
                filename=row[1],
                title=row[2],
                description=row[3],
                file_size=row[4],
                file_type=FileType(row[5]),
                upload_date=datetime.fromisoformat(row[6]),
                processing_status=ProcessingStatus(row[7]),
                text_length=row[8]
            ) for row in rows]
    
    def count_cvs(self) -> int:
        """Get total CV count"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cvs")
            return cursor.fetchone()[0]
    
    def update_cv_content(self, cv_id: str, text_content: str):
        """Update CV with extracted text content"""
        text_length = len(text_content)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE cvs 
                SET text_content = ?, text_length = ?, processing_status = ?
                WHERE id = ?
            """, (text_content, text_length, ProcessingStatus.COMPLETED.value, cv_id))
            conn.commit()
    
    def get_cv_content(self, cv_id: str) -> Optional[str]:
        """Get CV text content"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT text_content FROM cvs WHERE id = ?", (cv_id,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def get_cv_file_path(self, cv_id: str) -> Optional[Path]:
        """Get CV file path"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM cvs WHERE id = ?", (cv_id,))
            row = cursor.fetchone()
            return Path(row[0]) if row else None
    
    def delete_cv(self, cv_id: str) -> bool:
        """Delete CV and associated file"""
        file_path = self.get_cv_file_path(cv_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cvs WHERE id = ?", (cv_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
        
        # Delete file if it exists
        if file_path and file_path.exists():
            file_path.unlink()
        
        return deleted
    
    # Job Description Management Methods
    
    def save_job_description(self, text: str, source_url: Optional[str] = None) -> JDExtractionResponse:
        """Save job description"""
        jd_id = self._generate_id()
        source_type = "url" if source_url else "text"
        text_hash = self._calculate_text_hash(text)
        text_length = len(text)
        extraction_date = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO job_descriptions (id, source_url, source_type, extracted_text,
                                             extraction_date, processing_status, text_length, text_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (jd_id, source_url, source_type, text, extraction_date,
                  ProcessingStatus.COMPLETED.value, text_length, text_hash))
            conn.commit()
        
        return JDExtractionResponse(
            id=jd_id,
            source_url=source_url,
            source_type=source_type,
            extracted_text=text,
            extraction_date=datetime.fromisoformat(extraction_date),
            processing_status=ProcessingStatus.COMPLETED,
            text_length=text_length
        )
    
    def get_job_description(self, jd_id: str) -> Optional[JDExtractionResponse]:
        """Get job description by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, source_url, source_type, extracted_text, extraction_date,
                       processing_status, text_length
                FROM job_descriptions WHERE id = ?
            """, (jd_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return JDExtractionResponse(
                id=row[0],
                source_url=row[1],
                source_type=row[2],
                extracted_text=row[3],
                extraction_date=datetime.fromisoformat(row[4]),
                processing_status=ProcessingStatus(row[5]),
                text_length=row[6]
            )
    
    def check_duplicate_jd(self, text: str) -> Optional[str]:
        """Check if job description already exists (by text hash)"""
        text_hash = self._calculate_text_hash(text)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM job_descriptions WHERE text_hash = ?", (text_hash,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    # Analysis Management Methods
    
    def save_analysis_result(self, cv_id: str, analysis_result: str, ai_model: str, 
                           processing_time: float, jd_id: Optional[str] = None) -> str:
        """Save analysis result"""
        analysis_id = self._generate_id()
        analysis_date = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analysis_results (id, cv_id, jd_id, analysis_result,
                                            ai_model_used, processing_time, analysis_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (analysis_id, cv_id, jd_id, analysis_result, ai_model, processing_time, analysis_date))
            conn.commit()
        
        return analysis_id
    
    def get_analysis_results(self, cv_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get analysis results for a CV"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, jd_id, analysis_result, ai_model_used, processing_time, analysis_date
                FROM analysis_results 
                WHERE cv_id = ?
                ORDER BY analysis_date DESC
                LIMIT ?
            """, (cv_id, limit))
            
            rows = cursor.fetchall()
            return [{
                "id": row[0],
                "jd_id": row[1],
                "analysis_result": row[2],
                "ai_model_used": row[3],
                "processing_time": row[4],
                "analysis_date": datetime.fromisoformat(row[5])
            } for row in rows]
    
    # Utility Methods
    
    def cleanup_temp_files(self, older_than_hours: int = 24):
        """Clean up temporary files older than specified hours"""
        import time
        
        temp_dir = self.upload_dir / "temp"
        current_time = time.time()
        cutoff_time = current_time - (older_than_hours * 3600)
        
        for file_path in temp_dir.iterdir():
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        cv_count = self.count_cvs()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM job_descriptions")
            jd_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM analysis_results")
            analysis_count = cursor.fetchone()[0]
        
        # Calculate total storage usage
        total_size = 0
        cv_dir = self.upload_dir / "cvs"
        if cv_dir.exists():
            total_size = sum(f.stat().st_size for f in cv_dir.rglob('*') if f.is_file())
        
        return {
            "cv_count": cv_count,
            "job_description_count": jd_count,
            "analysis_count": analysis_count,
            "total_storage_bytes": total_size,
            "total_storage_mb": round(total_size / (1024 * 1024), 2)
        }


# Global database instance
enhanced_db = DatabaseManager()
