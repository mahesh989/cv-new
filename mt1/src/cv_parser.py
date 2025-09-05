# cv_parser.py

import logging
import pdfplumber
from docx import Document

# ────────────────────────────────────────────────────────
# Suppress pdfminer “CropBox missing” warnings
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfminer.pdfinterp").setLevel(logging.ERROR)
logging.getLogger("pdfminer.layout").setLevel(logging.ERROR)
# ────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts and returns all text from a PDF file.
    Suppresses any CropBox warnings by virtue of the logging settings above.
    """
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # page.extract_text() may return None
            txt = page.extract_text()
            if txt:
                pages_text.append(txt)
    # Join pages with a blank line to keep page breaks clear
    return "\n\n".join(pages_text)

def extract_text_from_docx(docx_path: str) -> str:
    """
    Extracts and returns all paragraph text from a .docx file.
    """
    doc = Document(docx_path)
    # Filter out any empty paragraphs
    paras = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paras)
