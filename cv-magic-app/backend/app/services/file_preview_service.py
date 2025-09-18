"""
File Preview Service

Handles file content extraction and preview functionality for any text file.
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class FilePreviewService:
    """Service for handling file preview and content extraction"""
    
    @staticmethod
    def extract_file_content(file_path: Path) -> Dict[str, Any]:
        """Extract content from a text file with metadata"""
        try:
            if not file_path.exists():
                return {
                    'success': False,
                    'error': f'File not found: {file_path}',
                    'text': '',
                    'metadata': {}
                }
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Get file metadata
            stat = file_path.stat()
            
            return {
                'success': True,
                'text': content,
                'metadata': {
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                    'created': stat.st_ctime,
                    'type': file_path.suffix[1:] if file_path.suffix else 'txt',
                    'filename': file_path.name,
                    'path': str(file_path.absolute())
                },
                'line_count': len(content.splitlines()),
                'char_count': len(content)
            }
            
        except Exception as e:
            logger.error(f"Error extracting file content from {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'metadata': {}
            }
    
    @staticmethod
    def get_file_preview(file_path: Path, max_length: int = 500) -> Dict[str, Any]:
        """Get a preview of file content with customizable length"""
        try:
            result = FilePreviewService.extract_file_content(file_path)
            
            if not result['success']:
                return result
            
            full_text = result['text']
            preview = full_text[:max_length] + ('...' if len(full_text) > max_length else '')
            
            return {
                'success': True,
                'preview': preview,
                'metadata': result['metadata'],
                'full_length': len(full_text),
                'preview_length': len(preview),
                'is_truncated': len(full_text) > max_length
            }
            
        except Exception as e:
            logger.error(f"Error generating file preview for {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'preview': '',
                'metadata': {}
            }
    
    @staticmethod
    def list_text_files(directory: Path, recursive: bool = False) -> Dict[str, Any]:
        """List all text files in a directory"""
        try:
            if not directory.exists():
                return {
                    'success': False,
                    'error': f'Directory not found: {directory}',
                    'files': []
                }
            
            # Get all files with common text extensions
            text_extensions = {'.txt', '.md', '.json', '.py', '.dart', '.yaml', '.log'}
            
            if recursive:
                files = [f for f in directory.rglob('*') if f.is_file() and f.suffix.lower() in text_extensions]
            else:
                files = [f for f in directory.iterdir() if f.is_file() and f.suffix.lower() in text_extensions]
            
            file_list = []
            for file in files:
                stat = file.stat()
                file_list.append({
                    'filename': file.name,
                    'path': str(file.absolute()),
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                    'type': file.suffix[1:] if file.suffix else 'txt'
                })
            
            return {
                'success': True,
                'files': file_list,
                'total_count': len(file_list),
                'directory': str(directory.absolute())
            }
            
        except Exception as e:
            logger.error(f"Error listing text files in {directory}: {e}")
            return {
                'success': False,
                'error': str(e),
                'files': []
            }

# Global instance
file_preview_service = FilePreviewService()