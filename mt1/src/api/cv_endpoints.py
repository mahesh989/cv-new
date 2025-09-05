"""
CV-related API endpoints
Extracted from main.py for better organization
"""

import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse
from datetime import datetime
from docx import Document
import PyPDF2
import pdfplumber

from ..cv_parser import extract_text_from_pdf, extract_text_from_docx

router = APIRouter(prefix="/api/cv", tags=["cv"])

# Constants
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
TAILORED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "tailored_cvs"))

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TAILORED_DIR, exist_ok=True)


@router.get("/list")
def list_cvs():
    """List all uploaded CVs"""
    try:
        return {"uploaded_cvs": os.listdir(UPLOAD_DIR)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing CVs: {str(e)}")


@router.post("/upload")
async def upload_cv(cv: UploadFile = File(...)):
    """Upload a CV file"""
    if not cv.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Validate file type
    allowed_extensions = {'.pdf', '.docx'}
    file_extension = os.path.splitext(cv.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        path = os.path.join(UPLOAD_DIR, cv.filename)
        with open(path, "wb") as buffer:
            shutil.copyfileobj(cv.file, buffer)
        
        # Log upload info
        print("=" * 80)
        print("🔍 DEBUG: CV UPLOAD INFO")
        print("=" * 80)
        print(f"CV Filename: {cv.filename}")
        print(f"CV File Path: {path}")
        print(f"CV File Size: {os.path.getsize(path)} bytes")
        print(f"CV Content Type: {cv.content_type}")
        print("=" * 80)
        
        return {"message": "CV uploaded successfully", "filename": cv.filename}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading CV: {str(e)}")


@router.get("/content/{filename}")
def get_cv_content(filename: str):
    """Get CV content for preview - works for both uploaded and tailored CVs"""
    # First try uploaded CVs directory
    uploaded_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(uploaded_path):
        return _extract_cv_content(uploaded_path, filename, "uploaded")
    
    # Then try tailored CVs directory
    tailored_path = os.path.join(TAILORED_DIR, filename)
    if os.path.exists(tailored_path):
        return _extract_cv_content(tailored_path, filename, "tailored")
    
    raise HTTPException(status_code=404, detail="CV file not found")


@router.get("/preview/{filename}")
def get_cv_preview(filename: str):
    """Get CV preview as plain text"""
    path = os.path.join(TAILORED_DIR, filename)
    print(f"🔍 Preview requested for: {path}")
    
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        if filename.lower().endswith('.pdf'):
            return _extract_pdf_text(path)
        else:
            return _extract_docx_text(path)
    except Exception as e:
        print(f"❌ Error reading file: {path} - {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {str(e)}")


@router.get("/download/{filename}")
def download_cv(filename: str):
    """Download a CV file"""
    path = os.path.join(TAILORED_DIR, filename)
    print(f"📥 Download requested for: {path}")
    
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        raise HTTPException(status_code=404, detail="CV file not found")
    
    print(f"✅ File found, size: {os.path.getsize(path)} bytes")
    
    # Determine media type
    media_type = _get_media_type(filename)
    
    return FileResponse(
        path,
        filename=filename,
        media_type=media_type
    )


# Helper functions
def _extract_cv_content(file_path: str, filename: str, source: str) -> str:
    """Extract content from CV file"""
    try:
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            content = extract_text_from_pdf(file_path)
        elif ext == ".docx":
            content = extract_text_from_docx(file_path)
        else:
            # Try reading as text file for other formats
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # Debug logging
        print("=" * 80)
        print(f"🔍 DEBUG: CV TEXT CONTENT ({source.upper()})")
        print("=" * 80)
        print(f"CV Filename: {filename}")
        print(f"CV Text Length: {len(content)} characters")
        print("CV Text Content:")
        print("-" * 40)
        print(content[:1000] + "..." if len(content) > 1000 else content)
        print("-" * 40)
        print("=" * 80)
        
        print(f"✅ Read {source} CV: {filename} ({len(content)} chars)")
        return content
        
    except Exception as e:
        print(f"❌ Error reading {source} CV {filename}: {str(e)}")
        raise


def _extract_pdf_text(path: str) -> str:
    """Extract text from PDF file"""
    try:
        with open(path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            print(f"✅ Successfully read PDF file: {path}")
            return text
    except Exception as e:
        # Fallback to pdfplumber
        try:
            with pdfplumber.open(path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                print(f"✅ Successfully read PDF file with pdfplumber: {path}")
                return text
        except Exception as e2:
            print(f"❌ Error reading PDF file: {path}")
            print(f"Error details: {str(e2)}")
            raise Exception(f"Failed to extract PDF text: {str(e2)}")


def _extract_docx_text(path: str) -> str:
    """Extract text from DOCX file"""
    try:
        doc = Document(path)
        print(f"✅ Successfully read DOCX file: {path}")
        return "\n\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"❌ Error reading DOCX file: {path}")
        print(f"Error details: {str(e)}")
        raise Exception(f"Failed to extract DOCX text: {str(e)}")


def _get_media_type(filename: str) -> str:
    """Get media type based on file extension"""
    if filename.lower().endswith('.pdf'):
        return 'application/pdf'
    elif filename.lower().endswith('.docx'):
        return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    else:
        return 'application/octet-stream'
