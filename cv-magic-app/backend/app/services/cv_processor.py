"""
Simple CV processor service for basic text extraction
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CVProcessor:
    """Simple CV processor for basic text extraction"""
    
    def extract_text_from_file(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from a CV file"""
        try:
            if file_path.suffix.lower() == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_path.suffix.lower() == '.docx':
                return self._extract_from_docx(file_path)
            elif file_path.suffix.lower() == '.txt':
                return self._extract_from_txt(file_path)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported file type: {file_path.suffix}',
                    'text': '',
                    'word_count': 0
                }
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'word_count': 0
            }
    
    def _extract_from_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from PDF file"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                return {
                    'success': True,
                    'text': text.strip(),
                    'word_count': len(text.split()),
                    'file_type': 'pdf'
                }
        except ImportError:
            return {
                'success': False,
                'error': 'PyPDF2 not available',
                'text': '',
                'word_count': 0
            }
    
    def _extract_from_docx(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from DOCX file"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return {
                'success': True,
                'text': text.strip(),
                'word_count': len(text.split()),
                'file_type': 'docx'
            }
        except ImportError:
            return {
                'success': False,
                'error': 'python-docx not available',
                'text': '',
                'word_count': 0
            }
    
    def _extract_from_txt(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            return {
                'success': True,
                'text': text.strip(),
                'word_count': len(text.split()),
                'file_type': 'txt'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'word_count': 0
            }
    
    def get_text_preview(self, text: str, max_length: int = 200) -> str:
        """Get a preview of the text"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    def extract_basic_info(self, text: str) -> Dict[str, Any]:
        """Extract basic information from CV text"""
        lines = text.split('\n')
        
        # Simple extraction - look for common patterns
        email = ""
        phone = ""
        name = ""
        
        for line in lines:
            line = line.strip()
            if '@' in line and not email:
                email = line
            elif any(char.isdigit() for char in line) and len(line) > 8 and not phone:
                phone = line
            elif len(line) > 2 and len(line) < 50 and not name and not any(char in line for char in ['@', 'http', 'www']):
                name = line
                break
        
        return {
            'name': name,
            'email': email,
            'phone': phone,
            'word_count': len(text.split()),
            'line_count': len(lines)
        }


# Global instance
cv_processor = CVProcessor()
