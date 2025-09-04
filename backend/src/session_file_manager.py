import os
import json
from datetime import datetime
from typing import Optional, Tuple
import re

class SessionFileManager:
    """
    Manages unique file naming and session tracking for analysis results
    """
    
    def __init__(self, results_dir: str = "analysis_results"):
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        
    def generate_unique_filename(self, cv_filename: str, jd_text: str, session_id: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate a unique filename based on CV and JD combination
        
        Args:
            cv_filename: Name of the CV file
            jd_text: Job description text (first 50 chars for identification)
            session_id: Optional session identifier
            
        Returns:
            Tuple of (filename, full_filepath)
        """
        # Clean CV filename (remove extension and special chars)
        cv_clean = re.sub(r'[^\w\s-]', '', cv_filename)
        cv_clean = re.sub(r'[-\s]+', '_', cv_clean).strip('_')
        
        # Create JD identifier (first 50 chars, cleaned)
        jd_identifier = jd_text[:50].strip()
        jd_clean = re.sub(r'[^\w\s-]', '', jd_identifier)
        jd_clean = re.sub(r'[-\s]+', '_', jd_clean).strip('_')
        
        # Create base filename
        base_filename = f"{cv_clean}_vs_{jd_clean}_Complete_Analysis"
        
        # Add session ID if provided
        if session_id:
            base_filename = f"{base_filename}_{session_id}"
        
        # Check for existing files and add suffix if needed
        filename = f"{base_filename}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        counter = 1
        while os.path.exists(filepath):
            filename = f"{base_filename}_{counter}.json"
            filepath = os.path.join(self.results_dir, filename)
            counter += 1
            
        return filename, filepath
    
    def find_existing_session_file(self, cv_filename: str, jd_text: str) -> Optional[str]:
        """
        Find existing analysis file for the same CV and JD combination
        
        Args:
            cv_filename: Name of the CV file
            jd_text: Job description text
            
        Returns:
            Filepath if found, None otherwise
        """
        # Clean CV filename
        cv_clean = re.sub(r'[^\w\s-]', '', cv_filename)
        cv_clean = re.sub(r'[-\s]+', '_', cv_clean).strip('_')
        
        # Create JD identifier
        jd_identifier = jd_text[:50].strip()
        jd_clean = re.sub(r'[^\w\s-]', '', jd_identifier)
        jd_clean = re.sub(r'[-\s]+', '_', jd_clean).strip('_')
        
        # Look for existing files
        base_pattern = f"{cv_clean}_vs_{jd_clean}_Complete_Analysis"
        
        for filename in os.listdir(self.results_dir):
            if filename.startswith(base_pattern) and filename.endswith('.json'):
                filepath = os.path.join(self.results_dir, filename)
                return filepath
                
        return None
    
    def get_or_create_session_file(self, cv_filename: str, jd_text: str, session_id: Optional[str] = None) -> Tuple[str, str, bool]:
        """
        Get existing session file or create new one
        
        Args:
            cv_filename: Name of the CV file
            jd_text: Job description text
            session_id: Optional session identifier
            
        Returns:
            Tuple of (filename, filepath, is_new_file)
        """
        # First, try to find existing file
        existing_filepath = self.find_existing_session_file(cv_filename, jd_text)
        
        if existing_filepath:
            # Found existing file - return it
            filename = os.path.basename(existing_filepath)
            return filename, existing_filepath, False
        else:
            # Create new file
            filename, filepath = self.generate_unique_filename(cv_filename, jd_text, session_id)
            return filename, filepath, True
    
    def initialize_session_file(self, filepath: str, cv_filename: str, jd_text: str) -> None:
        """
        Initialize a new session file with basic structure
        
        Args:
            filepath: Path to the file to initialize
            cv_filename: Name of the CV file
            jd_text: Job description text
        """
        initial_data = {
            "session_metadata": {
                "cv_filename": cv_filename,
                "jd_text_preview": jd_text[:100] + "..." if len(jd_text) > 100 else jd_text,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "analysis_phase": "initialized"
            },
            "analysis_results": {
                "preliminary_analysis": {},
                "skill_comparison": {},
                "enhanced_ats_score": {},
                "ai_recommendations": {}
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)
    
    def update_session_file(self, filepath: str, phase: str, data: dict) -> None:
        """
        Update session file with new analysis data
        
        Args:
            filepath: Path to the session file
            phase: Analysis phase (preliminary_analysis, skill_comparison, etc.)
            data: Data to add/update
        """
        try:
            # Load existing data
            with open(filepath, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Update metadata
            session_data["session_metadata"]["last_updated"] = datetime.now().isoformat()
            session_data["session_metadata"]["analysis_phase"] = phase
            
            # Update analysis results
            if phase in session_data["analysis_results"]:
                session_data["analysis_results"][phase].update(data)
            else:
                session_data["analysis_results"][phase] = data
            
            # Write back to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error updating session file: {e}")
    
    def get_session_file_content(self, filepath: str) -> Optional[dict]:
        """
        Get the content of a session file
        
        Args:
            filepath: Path to the session file
            
        Returns:
            File content as dict, or None if error
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading session file: {e}")
            return None

# Global instance
session_file_manager = SessionFileManager() 