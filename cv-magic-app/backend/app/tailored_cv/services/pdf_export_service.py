import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle,
)
from reportlab.lib import colors

logger = logging.getLogger(__name__)


class ResumePDFGenerator:
    """Generate a PDF resume from structured data with perfect alignment."""

    def __init__(self, data: Dict[str, Any], page_margins: Optional[Dict[str, float]] = None) -> None:
        self.data = data
        self.styles = getSampleStyleSheet()

        # Page configuration
        self.page_width, self.page_height = A4
        self.margins = page_margins or {
            'top': 0.5,
            'bottom': 0.5,
            'left': 0.5,
            'right': 0.5,
        }

        # Alignment constants
        self.content_left_margin = 0.15 * inch
        self.bullet_indent = 18

        # Uniform spacing settings (in points)
        self.spacing = {
            'section_above': 16,
            'section_below': 4,
            'subsection_gap': 12,
            'bullet_gap': 3,
            'after_bullets': 8,
            'line_after_section': 6,
        }

        self._calculate_dimensions()
        self._setup_custom_styles()

    def _calculate_dimensions(self) -> None:
        self.text_width = self.page_width - (self.margins['left'] + self.margins['right']) * inch
        self.text_height = self.page_height - (self.margins['top'] + self.margins['bottom']) * inch
        self.date_column_width = 1.8 * inch
        self.title_column_width = self.text_width - self.date_column_width - self.content_left_margin
        self.two_column_widths = [self.title_column_width, self.date_column_width]

    def _usable_width(self) -> float:
        left = self.margins['left'] * inch
        right = self.margins['right'] * inch
        return self.page_width - left - right

    def _setup_custom_styles(self) -> None:
        style_names = [s.name for s in self.styles.byName.values()]

        # Name style
        if 'Name' not in style_names:
            self.styles.add(ParagraphStyle(
                name='Name',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=6,
                spaceBefore=0,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                leading=24
            ))

        # Contact info style
        if 'Contact' not in style_names:
            self.styles.add(ParagraphStyle(
                name='Contact',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#444444'),
                alignment=TA_CENTER,
                spaceAfter=4,
                leading=10
            ))

        # Section header
        if 'SectionHeader' not in style_names:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=self.spacing['section_below'],
                spaceBefore=0,
                fontName='Helvetica-Bold',
                alignment=TA_LEFT,
                leftIndent=self.content_left_margin,
                rightIndent=0,
                leading=14
            ))

        # Body text style
        if 'BodyText' not in style_names:
            self.styles.add(ParagraphStyle(
                name='BodyText',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#333333'),
                spaceAfter=6,
                alignment=TA_JUSTIFY,
                leftIndent=self.content_left_margin,
                rightIndent=0,
                leading=12
            ))

        # Bullet character style
        if 'BulletChar' not in style_names:
            self.styles.add(ParagraphStyle(
                name='BulletChar',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#333333'),
                alignment=TA_LEFT,
                leftIndent=0,
                rightIndent=0,
                leading=12
            ))

        # Job Title style
        if 'JobTitle' not in style_names:
            self.styles.add(ParagraphStyle(
                name='JobTitle',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#1a1a1a'),
                fontName='Helvetica-Bold',
                spaceAfter=0,
                alignment=TA_LEFT,
                leftIndent=0,
                rightIndent=0,
                leading=12
            ))

        # Date style - right aligned
        if 'DateRight' not in style_names:
            self.styles.add(ParagraphStyle(
                name='DateRight',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#555555'),
                fontName='Helvetica',
                alignment=TA_RIGHT,
                spaceAfter=0,
                leftIndent=0,
                rightIndent=0,
                leading=12
            ))

        # Company style
        if 'Company' not in style_names:
            self.styles.add(ParagraphStyle(
                name='Company',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#555555'),
                fontName='Helvetica-Oblique',
                spaceAfter=8,
                alignment=TA_LEFT,
                leftIndent=self.content_left_margin,
                rightIndent=0,
                leading=12
            ))

        # Degree style
        if 'Degree' not in style_names:
            self.styles.add(ParagraphStyle(
                name='Degree',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#1a1a1a'),
                fontName='Helvetica-Bold',
                spaceAfter=0,
                alignment=TA_LEFT,
                leftIndent=0,
                rightIndent=0,
                leading=12
            ))

        # Institution style
        if 'Institution' not in style_names:
            self.styles.add(ParagraphStyle(
                name='Institution',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#555555'),
                spaceAfter=12,
                alignment=TA_LEFT,
                leftIndent=self.content_left_margin,
                rightIndent=0,
                leading=12
            ))

    def _create_section_with_line(self, title: str):
        elements = []
        elements.append(Spacer(1, self.spacing['section_above']))
        elements.append(Paragraph(title, self.styles['SectionHeader']))
        
        line = HRFlowable(
            width=self._usable_width() - self.content_left_margin,
            thickness=0.5,
            color=colors.HexColor('#666666'),
            spaceBefore=2,
            spaceAfter=self.spacing['line_after_section'],
            hAlign='LEFT'
        )
        line._xoffset = self.content_left_margin
        elements.append(line)
        
        return elements

    def _make_bullet_row(self, text: str) -> Table:
        bullet_col = self.bullet_indent
        usable = self._usable_width() - self.content_left_margin
        text_col = usable - bullet_col
        
        bullet_par = Paragraph("•", self.styles['BulletChar'])
        text_par = Paragraph(text, self.styles['BodyText'])
        
        tbl = Table([[bullet_par, text_par]], colWidths=[bullet_col, text_col])
        tbl.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), self.content_left_margin),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        return tbl

    def _make_bullet_rows(self, texts: List[str]):
        out = []
        for i, text in enumerate(texts):
            out.append(self._make_bullet_row(text))
            if i < len(texts) - 1:
                out.append(Spacer(1, self.spacing['bullet_gap']))
        return out

    def _create_aligned_two_column(self, left_content: str, right_content: str, 
                                   left_style: str = 'JobTitle', right_style: str = 'DateRight'):
        left_para = Paragraph(left_content, self.styles[left_style])
        right_para = Paragraph(right_content, self.styles[right_style])
        
        table = Table(
            [[left_para, right_para]], 
            colWidths=self.two_column_widths,
            style=[
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), self.content_left_margin),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]
        )
        
        return table

    def _contact_elements(self):
        elements = []
        personal_info = self.data.get('personal_information', {})

        elements.append(Spacer(1, 0.05 * inch))

        # Name
        name = personal_info.get('name', 'N/A')
        elements.append(Paragraph(name, self.styles['Name']))

        # Contact Line 1
        contact_line1 = []
        if personal_info.get('location'):
            contact_line1.append(personal_info['location'])
        if personal_info.get('phone'):
            contact_line1.append(personal_info['phone'])
        if personal_info.get('email'):
            contact_line1.append(personal_info['email'])

        if contact_line1:
            elements.append(Paragraph(" | ".join(contact_line1), self.styles['Contact']))

        # Contact Line 2
        contact_line2 = []
        if personal_info.get('linkedin'):
            contact_line2.append(personal_info['linkedin'])
        if personal_info.get('github'):
            contact_line2.append(personal_info['github'])

        portfolio = personal_info.get('portfolio_links', {})
        if portfolio and portfolio.get('blogs'):
            contact_line2.append(portfolio['blogs'])
        if portfolio and portfolio.get('dashboard_portfolio'):
            contact_line2.append(portfolio['dashboard_portfolio'])

        if contact_line2:
            elements.append(Paragraph(" | ".join(contact_line2), self.styles['Contact']))

        return elements

    def _paragraph_block(self, text: str):
        return Paragraph(text, self.styles['BodyText'])

    def generate(self, filename: str) -> str:
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=self.margins['right'] * inch,
            leftMargin=self.margins['left'] * inch,
            topMargin=self.margins['top'] * inch,
            bottomMargin=self.margins['bottom'] * inch,
        )

        elements: List[Any] = []

        # Contact section
        elements.extend(self._contact_elements())

        # Career profile
        profile = self.data.get('career_profile', {})
        if isinstance(profile, dict) and profile.get('summary'):
            elements.extend(self._create_section_with_line('CAREER PROFILE'))
            elements.append(self._paragraph_block(profile['summary']))

        # Experience
        experience = self.data.get('experience', [])
        if isinstance(experience, list) and experience:
            elements.extend(self._create_section_with_line('PROFESSIONAL EXPERIENCE'))
            for i, exp in enumerate(experience):
                if not isinstance(exp, dict):
                    continue
                
                title = exp.get('title', 'N/A')
                duration = exp.get('duration', '')
                company = exp.get('company', '')
                location = exp.get('location', '')
                
                # Title and date
                if duration:
                    table = self._create_aligned_two_column(f"<b>{title}</b>", duration, 'JobTitle', 'DateRight')
                    elements.append(table)
                else:
                    elements.append(Paragraph(f"<b>{title}</b>", self.styles['BodyText']))
                
                # Company and location
                company_parts = []
                if company:
                    company_parts.append(company)
                if location:
                    company_parts.append(location)
                
                if company_parts:
                    elements.append(Paragraph(" | ".join(company_parts), self.styles['Company']))
                
                # Responsibilities
                if exp.get('responsibilities') and isinstance(exp['responsibilities'], list):
                    elements.extend(self._make_bullet_rows([str(x) for x in exp['responsibilities']]))
                    
                    if i < len(experience) - 1:
                        elements.append(Spacer(1, self.spacing['after_bullets']))
                elif i < len(experience) - 1:
                    elements.append(Spacer(1, self.spacing['subsection_gap']))

        # Education
        education = self.data.get('education', [])
        if isinstance(education, list) and education:
            elements.extend(self._create_section_with_line('EDUCATION'))
            for i, edu in enumerate(education):
                if not isinstance(edu, dict):
                    continue
                
                degree = edu.get('degree', 'N/A')
                institution = edu.get('institution', '')
                year = edu.get('year', '')
                location = edu.get('location', '')
                
                # Degree and year
                if year:
                    table = self._create_aligned_two_column(f"<b>{degree}</b>", year, 'Degree', 'DateRight')
                    elements.append(table)
                else:
                    elements.append(Paragraph(f"<b>{degree}</b>", self.styles['BodyText']))
                
                # Institution and location
                inst_parts = []
                if institution:
                    inst_parts.append(institution)
                if location and location not in institution:
                    inst_parts.append(location)
                
                if inst_parts:
                    elements.append(Paragraph(", ".join(inst_parts), self.styles['Institution']))
                
                if i < len(education) - 1:
                    elements.append(Spacer(1, 6))

        # Skills
        skills = self.data.get('skills', {})
        if skills and skills.get('technical_skills'):
            elements.extend(self._create_section_with_line('TECHNICAL SKILLS'))
            for skill in skills['technical_skills']:
                elements.extend(self._make_bullet_rows([skill]))

        # Projects
        projects = self.data.get('projects', [])
        if isinstance(projects, list) and projects:
            elements.extend(self._create_section_with_line('PROJECTS'))
            for i, proj in enumerate(projects):
                if not isinstance(proj, dict):
                    continue
                
                name = proj.get('name', 'N/A')
                date = proj.get('date', '')
                
                if date:
                    table = self._create_aligned_two_column(f"<b>{name}</b>", date, 'JobTitle', 'DateRight')
                    elements.append(table)
                else:
                    elements.append(Paragraph(f"<b>{name}</b>", self.styles['BodyText']))
                
                if proj.get('description'):
                    elements.append(Paragraph(proj['description'], self.styles['BodyText']))
                
                if proj.get('technologies'):
                    tech_text = f"Technologies: {', '.join(proj['technologies'])}"
                    elements.append(Paragraph(tech_text, self.styles['Company']))
                
                if i < len(projects) - 1:
                    elements.append(Spacer(1, self.spacing['subsection_gap']))

        # Certifications
        certifications = self.data.get('certifications', [])
        if isinstance(certifications, list) and certifications:
            elements.extend(self._create_section_with_line('CERTIFICATIONS'))
            for cert in certifications:
                if isinstance(cert, dict):
                    cert_name = cert.get('name', 'N/A')
                    issuer = cert.get('issuer', '')
                    date = cert.get('date', '')
                    
                    cert_text = f"{cert_name}"
                    if issuer:
                        cert_text += f" - {issuer}"
                    if date:
                        cert_text += f" ({date})"
                    
                    elements.extend(self._make_bullet_rows([cert_text]))
                else:
                    elements.extend(self._make_bullet_rows([str(cert)]))

        doc.build(elements)
        logger.info(f"✓ PDF generated with perfect alignment: {filename}")
        return filename


def _map_tailored_json_to_generator_schema(data: Dict[str, Any]) -> Dict[str, Any]:
    """Map tailored CV JSON to the generator schema."""
    mapped = {}
    
    # Personal information
    if 'personal_information' in data:
        mapped['personal_information'] = data['personal_information']
    
    # Career profile
    if 'career_profile' in data:
        mapped['career_profile'] = data['career_profile']
    
    # Education
    if 'education' in data:
        mapped['education'] = data['education']
    
    # Experience - clean up duplicates in company/location
    if 'experience' in data:
        experiences = []
        for exp in data['experience']:
            if not isinstance(exp, dict):
                continue
            
            cleaned_exp = exp.copy()
            
            # Clean company/location duplication
            company = exp.get('company', '')
            location = exp.get('location', '')
            if company and location and location in company:
                cleaned_exp['location'] = ''
            
            # Build duration if missing
            if not cleaned_exp.get('duration'):
                start = exp.get('start_date', '')
                end = exp.get('end_date', 'Present')
                if start:
                    cleaned_exp['duration'] = f"{start} - {end}"
            
            experiences.append(cleaned_exp)
        mapped['experience'] = experiences
    
    # Skills - flatten categories
    if 'skills' in data:
        skills_data = data['skills']
        if isinstance(skills_data, dict):
            technical = []
            for category, items in skills_data.items():
                if isinstance(items, list) and items:
                    technical.append(f"{category}: {', '.join(map(str, items))}")
            mapped['skills'] = {'technical_skills': technical}
        elif isinstance(skills_data, list):
            # Convert dict entries into labeled strings if needed
            technical = []
            for item in skills_data:
                if isinstance(item, dict):
                    cat = item.get('category')
                    items = item.get('skills')
                    if cat and isinstance(items, list):
                        technical.append(f"{cat}: {', '.join(map(str, items))}")
                    else:
                        technical.append(str(item))
                else:
                    technical.append(str(item))
            mapped['skills'] = {'technical_skills': technical}
    
    # Ensure personal_information exists even if missing in source
    if 'personal_information' not in mapped:
        mapped['personal_information'] = {
            'name': (data.get('contact') or {}).get('name', 'Candidate'),
            'phone': (data.get('contact') or {}).get('phone'),
            'email': (data.get('contact') or {}).get('email'),
            'linkedin': (data.get('contact') or {}).get('linkedin'),
            'location': (data.get('contact') or {}).get('location'),
        }
    
    # Projects
    if 'projects' in data:
        mapped['projects'] = data['projects']
    
    # Certifications
    if 'certifications' in data:
        mapped['certifications'] = data['certifications']
    
    return mapped


def build_resume_data_from_files(json_path: Optional[Path], _txt_path: Optional[Path]) -> Dict[str, Any]:
    """Load tailored JSON and map to generator schema."""
    if not json_path or not json_path.exists() or json_path.stat().st_size == 0:
        raise FileNotFoundError("Tailored JSON CV not found or empty. Export requires JSON.")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    
    return _map_tailored_json_to_generator_schema(raw)


def export_tailored_cv_pdf(user_email: str, company: str, export_dir: Path) -> Path:
    """Export the latest tailored CV as PDF (using the adapter that preserves JSON)."""
    from app.unified_latest_file_selector import get_selector_for_user
    from app.tailored_cv.services.tailored_cv_adapter import load_tailored_cv_and_convert

    selector = get_selector_for_user(user_email)
    cv_context = selector.get_latest_tailored_cv_only(company)

    # Convert tailored JSON → generator schema using the adapter
    pdf_data = load_tailored_cv_and_convert(str(cv_context.json_path))

    export_dir.mkdir(parents=True, exist_ok=True)
    out_path = export_dir / f"{company}_tailored_resume.pdf"

    ResumePDFGenerator(pdf_data).generate(str(out_path))

    return out_path