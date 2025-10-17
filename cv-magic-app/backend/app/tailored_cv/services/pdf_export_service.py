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
    """Generate a PDF resume from structured or lightly-structured data."""

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

        if 'Name' not in style_names:
            self.styles.add(ParagraphStyle(
                name='Name', parent=self.styles['Heading1'], fontSize=24,
                textColor=colors.HexColor('#1a1a1a'), spaceAfter=6, spaceBefore=0,
                alignment=TA_CENTER, fontName='Helvetica-Bold', leading=24
            ))

        if 'Contact' not in style_names:
            self.styles.add(ParagraphStyle(
                name='Contact', parent=self.styles['Normal'], fontSize=10,
                textColor=colors.HexColor('#444444'), alignment=TA_CENTER,
                spaceAfter=4, leading=10
            ))

        if 'SectionHeader' not in style_names:
            self.styles.add(ParagraphStyle(
                name='SectionHeader', parent=self.styles['Heading2'], fontSize=14,
                textColor=colors.HexColor('#1a1a1a'), spaceAfter=6, spaceBefore=0,
                fontName='Helvetica-Bold', alignment=TA_LEFT, leftIndent=self.content_left_margin,
                rightIndent=0, leading=14
            ))

        if 'BodyText' not in style_names:
            self.styles.add(ParagraphStyle(
                name='BodyText', parent=self.styles['Normal'], fontSize=11,
                textColor=colors.HexColor('#333333'), spaceAfter=6, alignment=TA_JUSTIFY,
                leftIndent=0, rightIndent=0, leading=12
            ))

        if 'BulletChar' not in style_names:
            self.styles.add(ParagraphStyle(
                name='BulletChar', parent=self.styles['Normal'], fontSize=11,
                textColor=colors.HexColor('#333333'), alignment=TA_LEFT,
                leftIndent=0, rightIndent=0, leading=12
            ))

        if 'JobTitle' not in style_names:
            self.styles.add(ParagraphStyle(
                name='JobTitle', parent=self.styles['Normal'], fontSize=11,
                textColor=colors.HexColor('#1a1a1a'), fontName='Helvetica-Bold',
                spaceAfter=0, alignment=TA_LEFT, leftIndent=0, rightIndent=0, leading=12
            ))

        if 'DateRight' not in style_names:
            self.styles.add(ParagraphStyle(
                name='DateRight', parent=self.styles['Normal'], fontSize=11,
                textColor=colors.HexColor('#555555'), fontName='Helvetica',
                alignment=TA_RIGHT, spaceAfter=0, leftIndent=0, rightIndent=0, leading=12
            ))

        if 'Company' not in style_names:
            self.styles.add(ParagraphStyle(
                name='Company', parent=self.styles['Normal'], fontSize=11,
                textColor=colors.HexColor('#555555'), fontName='Helvetica-Oblique',
                spaceAfter=8, alignment=TA_LEFT, leftIndent=self.content_left_margin,
                rightIndent=0, leading=12
            ))

        if 'Degree' not in style_names:
            self.styles.add(ParagraphStyle(
                name='Degree', parent=self.styles['Normal'], fontSize=11,
                textColor=colors.HexColor('#1a1a1a'), fontName='Helvetica-Bold',
                spaceAfter=0, alignment=TA_LEFT, leftIndent=0, rightIndent=0, leading=12
            ))

        if 'Institution' not in style_names:
            self.styles.add(ParagraphStyle(
                name='Institution', parent=self.styles['Normal'], fontSize=11,
                textColor=colors.HexColor('#555555'), spaceAfter=12, alignment=TA_LEFT,
                leftIndent=self.content_left_margin, rightIndent=0, leading=12
            ))

    def _create_section_with_line(self, title: str):
        elements = [Spacer(1, 16), Paragraph(title, self.styles['SectionHeader'])]
        line = HRFlowable(
            width=self._usable_width() - self.content_left_margin,
            thickness=0.5,
            color=colors.HexColor('#666666'),
            spaceBefore=2,
            spaceAfter=6,
            hAlign='LEFT',
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
        out: List[Any] = []
        for i, text in enumerate(texts):
            out.append(self._make_bullet_row(text))
            if i < len(texts) - 1:
                out.append(Spacer(1, 3))
        return out

    def _contact_elements(self) -> List[Any]:
        personal = self.data.get('personal_information', {})
        if not isinstance(personal, dict):
            return []
        out: List[Any] = [Spacer(1, 0.05 * inch)]
        name = personal.get('name') or personal.get('full_name')
        if name:
            out.append(Paragraph(str(name), self.styles['Name']))
        line1 = []
        for key in ['location', 'phone', 'email']:
            val = personal.get(key)
            if val:
                line1.append(str(val))
        if line1:
            out.append(Paragraph(" | ".join(line1), self.styles['Contact']))
        line2 = []
        for key in ['linkedin', 'github', 'portfolio']:
            val = personal.get(key)
            if val:
                line2.append(str(val))
        if line2:
            out.append(Paragraph(" | ".join(line2), self.styles['Contact']))
        return out

    def _paragraph_block(self, text: str):
        table = Table(
            [[Paragraph(text, self.styles['BodyText'])]],
            colWidths=[self._usable_width() - self.content_left_margin],
            style=[
                ('LEFTPADDING', (0, 0), (-1, -1), self.content_left_margin),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ],
        )
        return table

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

        elements.extend(self._contact_elements())

        # Career profile
        profile = self.data.get('career_profile', {})
        if isinstance(profile, dict) and profile.get('summary'):
            elements.extend(self._create_section_with_line('CAREER PROFILE'))
            elements.append(self._paragraph_block(profile['summary']))

        # Experience (structured)
        experience = self.data.get('experience', [])
        if isinstance(experience, list) and experience:
            elements.extend(self._create_section_with_line('PROFESSIONAL EXPERIENCE'))
            for exp in experience:
                if not isinstance(exp, dict):
                    continue
                title = exp.get('title', 'N/A')
                duration = exp.get('duration', '')
                company = exp.get('company', '')
                location = exp.get('location', '')
                hdr = Paragraph(f"<b>{title}</b>", self.styles['JobTitle'])
                date = Paragraph(duration or '', self.styles['DateRight'])
                tbl = Table([[hdr, date]], colWidths=self.two_column_widths, style=[
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), self.content_left_margin),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ])
                elements.append(tbl)
                comps = [c for c in [company, location] if c]
                if comps:
                    elements.append(Paragraph(" | ".join(comps), self.styles['Company']))
                if isinstance(exp.get('responsibilities'), list):
                    elements.extend(self._make_bullet_rows([str(x) for x in exp['responsibilities']]))

        # Education (structured)
        education = self.data.get('education', [])
        if isinstance(education, list) and education:
            elements.extend(self._create_section_with_line('EDUCATION'))
            for edu in education:
                if not isinstance(edu, dict):
                    continue
                degree = Paragraph(f"<b>{edu.get('degree','')}</b>", self.styles['Degree'])
                year = Paragraph(edu.get('year',''), self.styles['DateRight'])
                tbl = Table([[degree, year]], colWidths=self.two_column_widths, style=[
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), self.content_left_margin),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ])
                elements.append(tbl)
                inst_parts = [p for p in [edu.get('institution'), edu.get('location')] if p]
                if inst_parts:
                    elements.append(Paragraph(", ".join(inst_parts), self.styles['Institution']))

        # Skills (structured)
        skills = self.data.get('skills', {})
        tech_skills = None
        if isinstance(skills, dict):
            tech_skills = skills.get('technical_skills')
        if isinstance(tech_skills, list) and tech_skills:
            elements.extend(self._create_section_with_line('TECHNICAL SKILLS'))
            for s in tech_skills:
                elements.extend(self._make_bullet_rows([str(s)]))

        doc.build(elements)
        return filename


def _parse_text_cv_to_minimal_structure(text: str) -> Dict[str, Any]:
    """Parse the saved plain text tailored CV into a minimal structure usable by the generator.
    This is intentionally simple and robust.
    """
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]

    # Heuristic: first non-empty line as name if it looks like a name
    name = lines[0] if lines else 'Candidate'

    bullets: List[str] = []
    for ln in lines:
        if ln.startswith('•'):
            bullets.append(ln[1:].strip())

    return {
        'personal_information': {
            'name': name,
        },
        'career_profile': {
            'summary': 'Tailored resume generated from latest CV content.'
        },
        'skills': {'technical_skills': bullets[:10]}  # best-effort
    }


def build_resume_data_from_files(json_path: Optional[Path], txt_path: Optional[Path]) -> Dict[str, Any]:
    """Load structured JSON if available; otherwise parse text."""
    if json_path and json_path.exists() and json_path.stat().st_size > 0:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception as e:
            logger.warning(f"Failed to read JSON CV at {json_path}: {e}")
    if txt_path and txt_path.exists():
        try:
            text = txt_path.read_text(encoding='utf-8')
            return _parse_text_cv_to_minimal_structure(text)
        except Exception as e:
            logger.warning(f"Failed to read TXT CV at {txt_path}: {e}")
    return {'personal_information': {'name': 'Candidate'}}


def export_tailored_cv_pdf(user_email: str, company: str, export_dir: Path) -> Path:
    """Generate a PDF of the latest tailored CV for a company and return the file path."""
    from app.unified_latest_file_selector import get_selector_for_user

    selector = get_selector_for_user(user_email)
    cv_context = selector.get_latest_tailored_cv_only(company)
    if not cv_context.exists:
        raise FileNotFoundError(f"No tailored CV found for company: {company}")

    data = build_resume_data_from_files(cv_context.json_path, cv_context.txt_path)

    export_dir.mkdir(parents=True, exist_ok=True)
    out_path = export_dir / f"{company}_tailored_resume.pdf"

    generator = ResumePDFGenerator(data)
    generator.generate(str(out_path))
    return out_path


