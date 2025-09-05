"""
CV Processing Utilities - Pure Functions Only
=============================================

This module contains pure utility functions for CV parsing and processing.
These functions are extracted from main.py and designed to be:
- Pure functions (no global state modification)
- Deterministic for the same inputs
- Side-effect free (except logging)
- Easily testable
"""

import re
from typing import List, Dict, Any


def parse_cv_content_debug(raw_content: str) -> List[Dict[str, Any]]:
    """
    Debug version of CV parsing logic
    Extracts structured sections from raw CV content
    """
    sections = []
    lines = raw_content.split('\n')
    
    current_section = ''
    current_content = []
    
    # Major CV section headers (standalone, all caps)
    section_headers = [
        'EDUCATION',
        'EXPERIENCE',
        'WORK EXPERIENCE',
        'EMPLOYMENT HISTORY',
        'PROJECTS',
        'SKILLS',
        'TECHNICAL SKILLS',
        'CERTIFICATIONS',
        'AWARDS',
        'PUBLICATIONS',
        'VOLUNTEER',
        'INTERESTS',
        'REFERENCES'
    ]

    for i, line in enumerate(lines):
        trimmed_line = line.strip()
        if trimmed_line == '':
            continue

        # Check if this is a major section header (standalone, all caps)
        is_header = False
        matched_header = ''
        
        # Only treat as header if it's a standalone line in all caps
        if trimmed_line == trimmed_line.upper() and len(trimmed_line) > 2:
            for header in section_headers:
                if trimmed_line == header.upper():
                    is_header = True
                    matched_header = header
                    break

        if is_header:
            # Save previous section if exists
            if current_section and current_content:
                sections.append({
                    'section_title': current_section,
                    'content': process_section_content_debug(current_content, current_section),
                })
            
            current_section = matched_header if matched_header else trimmed_line
            current_content = []
        else:
            # Handle contact information and personal info
            if not sections and not current_section:
                if ('@' in trimmed_line or 
                    '|' in trimmed_line or
                    'Phone' in trimmed_line or
                    'LinkedIn' in trimmed_line or
                    'GitHub' in trimmed_line or
                    'Blogs' in trimmed_line or
                    'Portfolio' in trimmed_line):
                    if not current_content:
                        current_section = 'CONTACT INFORMATION'
                elif i < 5 and not current_content:
                    current_section = 'PERSONAL INFORMATION'
            
            # Handle career profile section (special case)
            if trimmed_line.upper() == 'CAREER PROFILE':
                if current_section and current_content:
                    sections.append({
                        'section_title': current_section,
                        'content': process_section_content_debug(current_content, current_section),
                    })
                current_section = 'CAREER PROFILE'
                current_content = []
            else:
                current_content.append(trimmed_line)

    # Add the last section
    if current_section and current_content:
        sections.append({
            'section_title': current_section,
            'content': process_section_content_debug(current_content, current_section),
        })

    # If no sections were found, create a general content section
    if not sections:
        sections.append({
            'section_title': 'CV Content',
            'content': process_section_content_debug([line for line in lines if line.strip()]),
        })

    return sections


def process_section_content_debug(content: List[str], section_title: str = None) -> List[Dict[str, Any]]:
    """
    Debug version of content processing with lookahead for job titles in EXPERIENCE section
    """
    processed_content = []
    i = 0
    while i < len(content):
        trimmed_line = content[i].strip()
        if trimmed_line == '':
            i += 1
            continue

        # Check if line contains bullet points
        if (trimmed_line.startswith('•') or
            trimmed_line.startswith('*') or
            trimmed_line.startswith('-') or
            trimmed_line.startswith('▪') or
            trimmed_line.startswith('▫') or
            re.match(r'^\d+\.', trimmed_line)):
            # Extract bullet content
            bullet_content = trimmed_line
            if trimmed_line.startswith('•'):
                bullet_content = trimmed_line[1:].strip()
            elif trimmed_line.startswith('*'):
                bullet_content = trimmed_line[1:].strip()
            elif trimmed_line.startswith('-'):
                bullet_content = trimmed_line[1:].strip()
            elif trimmed_line.startswith('▪'):
                bullet_content = trimmed_line[1:].strip()
            elif trimmed_line.startswith('▫'):
                bullet_content = trimmed_line[1:].strip()
            elif re.match(r'^\d+\.', trimmed_line):
                bullet_content = re.sub(r'^\d+\.\s*', '', trimmed_line)
            processed_content.append({
                'type': 'bullet',
                'text': bullet_content,
            })
            i += 1
            continue

        # Check if this is a job title/position line (contains date range)
        is_job_title = False
        if (re.search(r'\d{4}\s*[-–—]\s*(Present|\d{4})', trimmed_line) or
            re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', trimmed_line)):
            is_job_title = True

        # Improved: If in EXPERIENCE section, treat as job title if next line is a date
        if (section_title is not None and 'EXPERIENCE' in section_title.upper()) and not is_job_title:
            if i + 1 < len(content):
                next_line = content[i + 1].strip()
                if (re.search(r'\d{4}\s*[-–—]\s*(Present|\d{4})', next_line) or
                    re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', next_line)):
                    is_job_title = True
        if is_job_title:
            processed_content.append({
                'type': 'job_title',
                'text': trimmed_line,
            })
            i += 1
            continue

        # Education institution
        if (',' in trimmed_line and 
            ('University' in trimmed_line or 
             'College' in trimmed_line or
             'School' in trimmed_line)):
            processed_content.append({
                'type': 'education',
                'text': trimmed_line,
            })
            i += 1
            continue

        # Regular text line
        processed_content.append({
            'type': 'text',
            'text': trimmed_line,
        })
        i += 1
    return processed_content


def is_date_pattern(text: str) -> bool:
    """
    Check if text contains date patterns commonly found in CVs
    """
    date_patterns = [
        r'\d{4}\s*[-–—]\s*(Present|\d{4})',  # 2020 - Present, 2018-2020
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',  # Jan 2020
        r'\d{1,2}/\d{4}',  # 01/2020
        r'\d{4}'  # Just year
    ]
    
    for pattern in date_patterns:
        if re.search(pattern, text):
            return True
    return False


def is_bullet_point(text: str) -> bool:
    """
    Check if text starts with common bullet point markers
    """
    text = text.strip()
    bullet_markers = ['•', '*', '-', '▪', '▫']
    
    for marker in bullet_markers:
        if text.startswith(marker):
            return True
    
    # Check for numbered lists
    if re.match(r'^\d+\.', text):
        return True
        
    return False


def extract_bullet_content(text: str) -> str:
    """
    Extract content from bullet point line, removing the bullet marker
    """
    text = text.strip()
    
    if text.startswith('•'):
        return text[1:].strip()
    elif text.startswith('*'):
        return text[1:].strip()
    elif text.startswith('-'):
        return text[1:].strip()
    elif text.startswith('▪'):
        return text[1:].strip()
    elif text.startswith('▫'):
        return text[1:].strip()
    elif re.match(r'^\d+\.', text):
        return re.sub(r'^\d+\.\s*', '', text)
    
    return text


def is_section_header(text: str, known_headers: List[str]) -> tuple:
    """
    Check if text is a section header
    Returns (is_header: bool, matched_header: str)
    """
    text = text.strip()
    
    # Only treat as header if it's a standalone line in all caps
    if text == text.upper() and len(text) > 2:
        for header in known_headers:
            if text == header.upper():
                return True, header
    
    return False, ""


def is_contact_info_line(text: str) -> bool:
    """
    Check if line contains contact information
    """
    contact_indicators = [
        '@',  # Email
        '|',  # Separator in contact lines
        'Phone',
        'LinkedIn',
        'GitHub',
        'Blogs',
        'Portfolio',
        'Email',
        '+',  # Phone numbers
        'www.',
        'http'
    ]
    
    for indicator in contact_indicators:
        if indicator in text:
            return True
    
    return False


def is_education_line(text: str) -> bool:
    """
    Check if line contains education information
    """
    education_keywords = ['University', 'College', 'School', 'Institute', 'Academy']
    
    # Must contain comma and education keyword
    if ',' in text:
        for keyword in education_keywords:
            if keyword in text:
                return True
    
    return False
