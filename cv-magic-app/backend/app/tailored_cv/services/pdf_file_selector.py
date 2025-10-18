"""
PDF File Selector for Company-Specific Tailored CV PDFs

This module provides utilities to find and select the latest PDF file
for a specific company from the user's PDF storage directory.
"""

import logging
from pathlib import Path
from typing import Optional
from app.utils.user_path_utils import get_user_base_path

logger = logging.getLogger(__name__)


def get_latest_company_pdf(user_email: str, company: str) -> Optional[Path]:
    """
    Get the latest PDF file for a specific company from the user's PDF directory.
    
    Args:
        user_email: User's email address
        company: Company name (e.g., "Australia_for_UNHCR", "Google")
        
    Returns:
        Path to the latest PDF file for the company, or None if not found
    """
    try:
        # Get user's base path
        user_base = get_user_base_path(user_email)
        pdf_dir = user_base / "cvs" / "pdf_cvs"
        
        if not pdf_dir.exists():
            logger.warning(f"📁 PDF directory does not exist: {pdf_dir}")
            return None
        
        # Find all PDF files for this specific company
        # Pattern: {company}_tailored_resume_*.pdf
        pdf_pattern = f"{company}_tailored_resume_*.pdf"
        pdf_files = list(pdf_dir.glob(pdf_pattern))
        
        if not pdf_files:
            logger.warning(f"📄 No PDF files found for company '{company}' in {pdf_dir}")
            return None
        
        # Sort by modification time (newest first)
        pdf_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        latest_pdf = pdf_files[0]
        
        logger.info(f"✅ Found latest PDF for '{company}': {latest_pdf.name}")
        return latest_pdf
        
    except Exception as e:
        logger.error(f"❌ Failed to get latest PDF for company '{company}': {e}")
        return None


def get_company_pdf_info(user_email: str, company: str) -> Optional[dict]:
    """
    Get information about the latest PDF file for a specific company.
    
    Args:
        user_email: User's email address
        company: Company name
        
    Returns:
        Dictionary with PDF file information, or None if not found
    """
    try:
        pdf_path = get_latest_company_pdf(user_email, company)
        
        if not pdf_path or not pdf_path.exists():
            return None
        
        stat = pdf_path.stat()
        
        return {
            "path": pdf_path,
            "filename": pdf_path.name,
            "size": stat.st_size,
            "last_modified": stat.st_mtime,
            "company": company,
            "exists": True
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get PDF info for company '{company}': {e}")
        return None


def list_company_pdfs(user_email: str, company: str) -> list:
    """
    List all PDF files for a specific company, sorted by modification time.
    
    Args:
        user_email: User's email address
        company: Company name
        
    Returns:
        List of PDF file paths, sorted by modification time (newest first)
    """
    try:
        user_base = get_user_base_path(user_email)
        pdf_dir = user_base / "cvs" / "pdf_cvs"
        
        if not pdf_dir.exists():
            return []
        
        # Find all PDF files for this specific company
        pdf_pattern = f"{company}_tailored_resume_*.pdf"
        pdf_files = list(pdf_dir.glob(pdf_pattern))
        
        # Sort by modification time (newest first)
        pdf_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        return pdf_files
        
    except Exception as e:
        logger.error(f"❌ Failed to list PDFs for company '{company}': {e}")
        return []
