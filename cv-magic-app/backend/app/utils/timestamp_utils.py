"""
Timestamp Utility for File Naming

Provides consistent timestamp formatting for all file naming throughout the backend.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import re

logger = logging.getLogger(__name__)


class TimestampUtils:
    """Utility class for handling timestamped filenames"""
    
    @staticmethod
    def get_timestamp() -> str:
        """
        Get current timestamp in the format used for file naming
        
        Returns:
            Timestamp string in format: YYYYMMDD_HHMMSS
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @staticmethod
    def create_timestamped_filename(base_name: str, extension: str = "json", timestamp: Optional[str] = None) -> str:
        """
        Create a timestamped filename
        
        Args:
            base_name: Base filename without extension
            extension: File extension (without dot)
            timestamp: Optional timestamp, if not provided uses current time
            
        Returns:
            Timestamped filename: base_name_YYYYMMDD_HHMMSS.extension
        """
        if timestamp is None:
            timestamp = TimestampUtils.get_timestamp()
        
        return f"{base_name}_{timestamp}.{extension}"
    
    @staticmethod
    def extract_timestamp_from_filename(filename: str) -> Optional[str]:
        """
        Extract timestamp from a timestamped filename
        
        Args:
            filename: Filename that may contain timestamp
            
        Returns:
            Timestamp string if found, None otherwise
        """
        # Pattern to match timestamp: YYYYMMDD_HHMMSS
        pattern = r'_(\d{8}_\d{6})(?:\.[^.]+)?$'
        match = re.search(pattern, filename)
        return match.group(1) if match else None
    
    @staticmethod
    def is_timestamped_filename(filename: str) -> bool:
        """
        Check if filename contains a timestamp
        
        Args:
            filename: Filename to check
            
        Returns:
            True if filename contains timestamp, False otherwise
        """
        return TimestampUtils.extract_timestamp_from_filename(filename) is not None
    
    @staticmethod
    def get_base_name_from_timestamped(filename: str) -> str:
        """
        Get base name from timestamped filename
        
        Args:
            filename: Timestamped filename
            
        Returns:
            Base name without timestamp and extension
        """
        # Remove extension first
        name_without_ext = Path(filename).stem
        
        # Remove timestamp pattern
        pattern = r'_\d{8}_\d{6}$'
        base_name = re.sub(pattern, '', name_without_ext)
        
        return base_name
    
    @staticmethod
    def find_latest_timestamped_file(directory: Path, base_name: str, extension: str = "json") -> Optional[Path]:
        """
        Find the latest timestamped file in a directory
        
        Args:
            directory: Directory to search in
            base_name: Base filename to look for
            extension: File extension
            
        Returns:
            Path to latest file or None if no files found
        """
        if not directory.exists():
            return None
        
        # Pattern to match: base_name_YYYYMMDD_HHMMSS.extension
        pattern = f".*{base_name}.*_\d{{8}}_\d{{6}}\.{extension}"
        logger.debug(f"🔍 [TIMESTAMP_UTILS] Using pattern: {pattern}")
        
        matching_files = []
        for file_path in directory.glob(f"{base_name}_*.{extension}"):
            if re.match(pattern, file_path.name):
                matching_files.append(file_path)
        
        if not matching_files:
            return None
        
        # Sort by timestamp in filename (newest first)
        matching_files.sort(key=lambda x: TimestampUtils.extract_timestamp_from_filename(x.name), reverse=True)
        
        return matching_files[0]
    
    @staticmethod
    def find_all_timestamped_files(directory: Path, base_name: str, extension: str = "json") -> List[Path]:
        """
        Find all timestamped files matching the pattern
        
        Args:
            directory: Directory to search in
            base_name: Base filename to look for
            extension: File extension
            
        Returns:
            List of paths sorted by timestamp (newest first)
        """
        if not directory.exists():
            return []
        
        # Pattern to match: base_name_YYYYMMDD_HHMMSS.extension
        pattern = f"{base_name}_\\d{{8}}_\\d{{6}}\\.{extension}"
        
        matching_files = []
        for file_path in directory.glob(f"{base_name}_*.{extension}"):
            if re.match(pattern, file_path.name):
                matching_files.append(file_path)
        
        # Sort by timestamp in filename (newest first)
        matching_files.sort(key=lambda x: TimestampUtils.extract_timestamp_from_filename(x.name), reverse=True)
        
        return matching_files
    
    @staticmethod
    def get_file_info(file_path: Path) -> Dict[str, Any]:
        """
        Get information about a timestamped file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        filename = file_path.name
        timestamp = TimestampUtils.extract_timestamp_from_filename(filename)
        base_name = TimestampUtils.get_base_name_from_timestamped(filename)
        
        info = {
            'path': file_path,
            'filename': filename,
            'base_name': base_name,
            'extension': file_path.suffix[1:] if file_path.suffix else '',
            'is_timestamped': timestamp is not None,
            'timestamp': timestamp,
            'exists': file_path.exists()
        }
        
        if file_path.exists():
            stat = file_path.stat()
            info.update({
                'size': stat.st_size,
                'modified_time': stat.st_mtime,
                'created_time': stat.st_ctime
            })
        
        return info


# Convenience functions for common operations
def get_timestamp() -> str:
    """Get current timestamp string"""
    return TimestampUtils.get_timestamp()


def create_timestamped_filename(base_name: str, extension: str = "json") -> str:
    """Create timestamped filename"""
    return TimestampUtils.create_timestamped_filename(base_name, extension)


def find_latest_file(directory: Path, base_name: str, extension: str = "json") -> Optional[Path]:
    """Find latest timestamped file"""
    return TimestampUtils.find_latest_timestamped_file(directory, base_name, extension)


def find_all_files(directory: Path, base_name: str, extension: str = "json") -> List[Path]:
    """Find all timestamped files"""
    return TimestampUtils.find_all_timestamped_files(directory, base_name, extension)
