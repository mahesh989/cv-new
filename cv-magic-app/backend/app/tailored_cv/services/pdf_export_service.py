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
# HyperLink import removed - not needed for current implementation
from reportlab.lib import colors

logger = logging.getLogger(__name__)


class ResumePDFGenerator:
    """Generate a PDF resume from structured data with perfect alignment."""

    def __init__(self, data: Dict[str, Any] | str, page_margins: Optional[Dict[str, float]] = None) -> None:
        # Accept dict or JSON string; normalize to dict to avoid 'str'.get errors
        if isinstance(data, str):
            try:
                data = json.loads(data)
                logger.info("[PDF_EXPORT] generator received string; parsed into dict")
            except Exception:
                raise TypeError("ResumePDFGenerator expects a dict or JSON string that parses to a dict")
        self.data = data  # type: ignore[assignment]
        self.styles = getSampleStyleSheet()

        # Page configuration
        self.page_width, self.page_height = A4
        self.margins = page_margins or {
            'top': 0.5,
            'bottom': 0.5,
            'left': 0.5,
            'right': 0.5,
        }

        # Alignment constants - all values in points for consistency
        self.content_left_margin = 0.15 * inch
        self.bullet_indent = 18  # Points - consistent with ReportLab units
        self.section_indent = 0  # No additional indent for section headers
        self.text_indent = 0     # No indent for body text

        # Uniform spacing settings (in points)
        self.spacing = {
            'section_above': 16,
            'section_below': 4,
            'subsection_gap': 12,
            'bullet_gap': 3,
            'after_bullets': 8,
            'line_after_section': 6,
            'contact_name_gap': -30,  # Special case for contact name
            'education_gap': 3,       # Consistent education spacing
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

        # Bullet text style (for text inside bullet tables - NO leftIndent to avoid double indentation)
        if 'BulletText' not in style_names:
            self.styles.add(ParagraphStyle(
                name='BulletText',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#333333'),
                spaceAfter=6,
                alignment=TA_JUSTIFY,
                leftIndent=0,  # NO indent - table handles positioning
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

        # Skill Category style
        if 'SkillCategory' not in style_names:
            self.styles.add(ParagraphStyle(
                name='SkillCategory',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#1a1a1a'),
                fontName='Helvetica-Bold',
                spaceAfter=4,
                alignment=TA_LEFT,
                leftIndent=0,
                rightIndent=0,
                leading=12
            ))

        # Skill Item style
        if 'SkillItem' not in style_names:
            self.styles.add(ParagraphStyle(
                name='SkillItem',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#333333'),
                fontName='Helvetica',
                spaceAfter=0,
                alignment=TA_LEFT,
                leftIndent=0,
                rightIndent=0,
                leading=12
            ))

    def _create_section_with_line(self, title: str):
        """Create a uniform section header with consistent spacing and alignment"""
        elements = []
        elements.append(Spacer(1, self.spacing['section_above']))
        elements.append(Paragraph(title, self.styles['SectionHeader']))
        
        # Create horizontal line
        line = HRFlowable(
            width=self._usable_width() - self.content_left_margin,
            thickness=0.5,
            color=colors.HexColor('#666666'),
            spaceBefore=2,
            spaceAfter=self.spacing['line_after_section'],
            hAlign='LEFT'
        )
        
        # Wrap line in table for proper positioning (instead of unreliable _xoffset)
        line_table = Table([[line]], colWidths=[self._usable_width()])
        line_table.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (0, 0), self.content_left_margin),
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('TOPPADDING', (0, 0), (0, 0), 0),
            ('BOTTOMPADDING', (0, 0), (0, 0), 0),
        ]))
        elements.append(line_table)
        
        return elements

    def _create_empty_section_handler(self, section_name: str, content: list) -> bool:
        """Handle empty sections uniformly - return True if section should be skipped"""
        if not content or (isinstance(content, list) and len(content) == 0):
            logger.info(f"[PDF_EXPORT] Skipping empty section: {section_name}")
            return True
        return False

    def _make_bullet_row(self, text: str) -> Table:
        bullet_col = self.bullet_indent
        usable = self._usable_width() - self.content_left_margin
        text_col = usable - bullet_col
        
        bullet_par = Paragraph("•", self.styles['BulletChar'])
        text_par = Paragraph(text, self.styles['BulletText'])  # Use BulletText to avoid double indentation
        
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
        
        # Ensure personal_info is a dictionary
        if not isinstance(personal_info, dict):
            logger.warning("[PDF_EXPORT] personal_information is not a dict: %s", type(personal_info))
            personal_info = {}

        elements.append(Spacer(1, self.spacing['contact_name_gap']))  # Consistent contact name gap

        # Name - use original CV data if profile data is missing
        name = personal_info.get('name', 'N/A')
        if not name or name == 'N/A':
            # Fallback to original CV contact data if available
            contact_data = self.data.get('contact', {})
            name = contact_data.get('name', 'N/A')
        elements.append(Paragraph(name, self.styles['Name']))

        # Single contact line with all information
        contact_parts = []
        
        # Get all contact information
        location = personal_info.get('location', '')
        phone = personal_info.get('phone', '')
        email = personal_info.get('email', '')
        linkedin = personal_info.get('linkedin', '')
        github = personal_info.get('github', '')
        
        # Portfolio links
        portfolio = personal_info.get('portfolio_links', {})
        portfolio_url = portfolio.get('blogs', '') if portfolio else ''
        website_url = portfolio.get('website', '') if portfolio else ''
        
        # Fallback to original CV data if profile data is missing
        if not location or not phone or not email:
            contact_data = self.data.get('contact', {})
            if not location:
                location = contact_data.get('location', '')
            if not phone:
                phone = contact_data.get('phone', '')
            if not email:
                email = contact_data.get('email', '')
            if not linkedin:
                linkedin = contact_data.get('linkedin', '')
            if not github:
                github = contact_data.get('website', '')
            if not portfolio_url and not website_url:
                portfolio_url = contact_data.get('website', '')
                website_url = contact_data.get('website', '')
        
        # Build single contact line with clickable links
        contact_parts = []
        
        # Add basic contact info
        if location:
            contact_parts.append(location)
        if phone:
            contact_parts.append(phone)
        if email:
            contact_parts.append(f"<link href=\"mailto:{email}\" color=\"blue\"><u>{email}</u></link>")
        
        # Add clickable links (only labels, not URLs)
        if linkedin:
            contact_parts.append(f"<link href=\"{linkedin}\" color=\"blue\"><u>LinkedIn</u></link>")
        if github:
            logger.info(f"[PDF_EXPORT] Adding GitHub link: {github}")
            contact_parts.append(f"<link href=\"{github}\" color=\"blue\"><u>GitHub</u></link>")
        else:
            logger.warning(f"[PDF_EXPORT] No GitHub URL found. linkedin={linkedin}, github={github}")
        if portfolio_url:
            contact_parts.append(f"<link href=\"{portfolio_url}\" color=\"blue\"><u>Portfolio</u></link>")
        if website_url and website_url != portfolio_url:
            contact_parts.append(f"<link href=\"{website_url}\" color=\"blue\"><u>Website</u></link>")

        # Create single contact line with all information
        if contact_parts:
            contact_line = " | ".join(contact_parts)
            elements.append(Paragraph(contact_line, self.styles['Contact']))

        return elements

    def _paragraph_block(self, text: str):
        """Create a paragraph block with consistent left margin alignment"""
        para = Paragraph(text, self.styles['BodyText'])
        
        # Wrap in table for consistent positioning (leftIndent on BodyText may not work in all contexts)
        table = Table([[para]], colWidths=[self._usable_width()])
        table.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (0, 0), self.content_left_margin),
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('TOPPADDING', (0, 0), (0, 0), 0),
            ('BOTTOMPADDING', (0, 0), (0, 0), 0),
        ]))
        return table
    
    def _create_hyperlink(self, text: str, url: str):
        """Create a clickable hyperlink"""
        try:
            if not url or not url.strip():
                return Paragraph(text, self.styles['Contact'])
            
            # Ensure URL has protocol (don't modify mailto: URLs)
            if not url.startswith(('http://', 'https://', 'mailto:')):
                url = 'https://' + url
            
            # Create hyperlink with blue color and underline
            link_style = ParagraphStyle(
                'Hyperlink',
                parent=self.styles['Contact'],
                textColor=colors.blue,
                underline=True,
            )
            
            # Create clickable link using ReportLab's hyperlink functionality
            link_text = f'<link href="{url}" color="blue"><u>{text}</u></link>'
            return Paragraph(link_text, link_style)
        except Exception as e:
            logger.warning("[PDF_EXPORT] Failed to create hyperlink for %s: %s", text, e)
            # Fallback to regular text if hyperlink creation fails
            return Paragraph(text, self.styles['Contact'])

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
        try:
            elements.extend(self._contact_elements())
        except Exception as e:
            logger.error("[PDF_EXPORT] Error creating contact elements: %s", e)
            # Add fallback contact info
            elements.append(Paragraph("Contact Information", self.styles['Name']))
            elements.append(Paragraph("Please check your profile settings", self.styles['Contact']))

        # Profile Summary (NEW FRAMEWORK) - Priority
        profile_summary = self.data.get('profile_summary', '')
        if profile_summary:
            logger.info("[PDF_EXPORT] Adding profile summary section")
            elements.extend(self._create_section_with_line('PROFESSIONAL SUMMARY'))
            elements.append(self._paragraph_block(profile_summary))
            elements.append(Spacer(1, self.spacing['section_below']))
        else:
            # Career profile (legacy support) - Fallback
            profile = self.data.get('career_profile', {})
            if isinstance(profile, dict) and profile.get('summary'):
                logger.info("[PDF_EXPORT] Adding legacy career profile section")
                elements.extend(self._create_section_with_line('PROFESSIONAL SUMMARY'))
                elements.append(self._paragraph_block(profile['summary']))
                elements.append(Spacer(1, self.spacing['section_below']))

        # Experience
        experience = self.data.get('experience', [])
        if isinstance(experience, list) and experience and not self._create_empty_section_handler('EXPERIENCE', experience):
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
        if isinstance(education, list) and education and not self._create_empty_section_handler('EDUCATION', education):
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
                    elements.append(Spacer(1, self.spacing['education_gap']))  # Consistent education spacing

        # Skills
        skills = self.data.get('skills', [])  # Changed from {} to []
        if skills:
            elements.extend(self._create_section_with_line('SKILLS'))
            
            # Check if skills are categorized (skills is a list of SkillCategory objects)
            is_categorized = isinstance(skills, list) and skills and isinstance(skills[0], dict) and 'category' in skills[0]
            
            if is_categorized:
                # Categorized format: Display with proper bullet alignment
                for skill_category in skills:
                    if isinstance(skill_category, dict) and 'category' in skill_category and 'skills' in skill_category:
                        category_name = skill_category['category']
                        skills_list = skill_category['skills']
                        if isinstance(skills_list, list) and skills_list:
                            # Use bullet formatting for proper alignment
                            skills_text = ", ".join(skills_list)
                            elements.extend(self._make_bullet_rows([f"<b>{category_name}:</b> {skills_text}"]))
            elif isinstance(skills, dict) and skills.get('is_categorized'):
                # Handle mapped categorized format from _map_tailored_json_to_generator_schema
                for category, skills_list in skills.items():
                    if category != 'is_categorized' and isinstance(skills_list, list) and skills_list:
                        # Use bullet formatting for proper alignment
                        skills_text = ", ".join(skills_list)
                        elements.extend(self._make_bullet_rows([f"<b>{category}:</b> {skills_text}"]))
            else:
                # Simple format: Display with proper bullet alignment
                technical_skills = skills.get('technical_skills', [])
                if technical_skills:
                    skills_text = ", ".join(technical_skills)
                    elements.extend(self._make_bullet_rows([skills_text]))

        # Projects
        projects = self.data.get('projects', [])
        if isinstance(projects, list) and projects and not self._create_empty_section_handler('PROJECTS', projects):
            logger.info(f"[PDF_EXPORT] Processing {len(projects)} projects")
            elements.extend(self._create_section_with_line('PROJECTS'))
            for i, proj in enumerate(projects):
                if not isinstance(proj, dict):
                    logger.warning(f"[PDF_EXPORT] Project {i} is not a dict: {type(proj)}")
                    continue
                
                name = proj.get('name', 'N/A')
                date = proj.get('date', '')
                duration = proj.get('duration', '')
                context = proj.get('context', '')
                logger.info(f"[PDF_EXPORT] Project {i}: {name}")
                
                # Use duration if available, otherwise date, otherwise no alignment
                project_date = duration or date
                if project_date:
                    table = self._create_aligned_two_column(f"<b>{name}</b>", project_date, 'JobTitle', 'DateRight')
                    elements.append(table)
                else:
                    # Use JobTitle style for consistent alignment with experience section
                    elements.append(Paragraph(f"<b>{name}</b>", self.styles['JobTitle']))
                
                # Add context if available (like university project, individual project, etc.)
                if context:
                    elements.append(Paragraph(context, self.styles['Company']))
                
                # Handle bullets/descriptions
                bullets = proj.get('bullets', [])
                logger.info(f"[PDF_EXPORT] Project {i} bullets: {len(bullets)} items")
                if bullets:
                    # Process all bullets at once for consistent alignment
                    clean_bullets = [bullet.strip() for bullet in bullets if bullet.strip()]
                    if clean_bullets:
                        elements.extend(self._make_bullet_rows(clean_bullets))
                elif proj.get('description'):
                    logger.info(f"[PDF_EXPORT] Project {i} using description fallback")
                    elements.append(Paragraph(proj['description'], self.styles['BodyText']))
                
                if proj.get('technologies'):
                    tech_text = f"Technologies: {', '.join(proj['technologies'])}"
                    elements.append(Paragraph(tech_text, self.styles['Company']))
                
                if i < len(projects) - 1:
                    elements.append(Spacer(1, self.spacing['subsection_gap']))

        # Certifications
        certifications = self.data.get('certifications', [])
        if isinstance(certifications, list) and certifications and not self._create_empty_section_handler('CERTIFICATIONS', certifications):
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
    
    # Profile summary (NEW FRAMEWORK) - Priority
    if 'profile_summary' in data:
        mapped['profile_summary'] = data['profile_summary']
    
    # Career profile (legacy support) - Fallback
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
            
            # Clean company/location duplication - only if location is at the end of company name
            company = exp.get('company', '')
            location = exp.get('location', '')
            if company and location and company.endswith(f', {location}'):
                # Only remove location if it's clearly duplicated at the end with a comma
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
            # Handle categorized skills format properly
            mapped['skills'] = {'is_categorized': True}
            for item in skills_data:
                if isinstance(item, dict):
                    cat = item.get('category')
                    items = item.get('skills')
                    if cat and isinstance(items, list):
                        # Store each category separately for proper PDF rendering
                        mapped['skills'][cat] = items
                    else:
                        # Fallback for non-categorized items
                        if 'technical_skills' not in mapped['skills']:
                            mapped['skills']['technical_skills'] = []
                        mapped['skills']['technical_skills'].append(str(item))
                else:
                    # Fallback for non-dict items
                    if 'technical_skills' not in mapped['skills']:
                        mapped['skills']['technical_skills'] = []
                    mapped['skills']['technical_skills'].append(str(item))
    
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
    from app.services.profile_service import profile_service
    from datetime import datetime

    selector = get_selector_for_user(user_email)
    cv_context = selector.get_latest_tailored_cv_only(company)
    logger.info(
        "[PDF_EXPORT] user=%s company=%s json_path=%s txt_path=%s exists=%s",
        user_email,
        company,
        str(cv_context.json_path) if cv_context.json_path else None,
        str(cv_context.txt_path) if cv_context.txt_path else None,
        cv_context.exists,
    )

    # Convert tailored JSON → generator schema using the adapter
    if not cv_context.json_path or not cv_context.json_path.exists():
        raise FileNotFoundError(f"Tailored JSON not found for company '{company}'")
    pdf_data = load_tailored_cv_and_convert(str(cv_context.json_path))
    # Some historical files may contain a JSON string instead of an object
    if isinstance(pdf_data, str):
        try:
            pdf_data = json.loads(pdf_data)
            logger.info("[PDF_EXPORT] parsed stringified JSON into dict")
        except Exception:
            logger.error("[PDF_EXPORT] tailored JSON loaded as string and failed to parse")
            raise TypeError("Tailored CV data must be a JSON object, not a string")

    # Ensure pdf_data is a dictionary before proceeding
    if not isinstance(pdf_data, dict):
        logger.error("[PDF_EXPORT] pdf_data is not a dictionary after processing: %s", type(pdf_data))
        raise TypeError(f"Expected dictionary, got {type(pdf_data)}")

    # Normalize known sections that might be stringified unexpectedly
    try:
        if isinstance(pdf_data.get('experience'), str):
            pdf_data['experience'] = json.loads(pdf_data['experience'])
            logger.info("[PDF_EXPORT] normalized experience from string")
        if isinstance(pdf_data.get('education'), str):
            pdf_data['education'] = json.loads(pdf_data['education'])
            logger.info("[PDF_EXPORT] normalized education from string")
        skills = pdf_data.get('skills')
        if isinstance(skills, str):
            pdf_data['skills'] = json.loads(skills)
            logger.info("[PDF_EXPORT] normalized skills from string")
        projects = pdf_data.get('projects')
        if isinstance(projects, str):
            pdf_data['projects'] = json.loads(projects)
            logger.info("[PDF_EXPORT] normalized projects from string")
        certifications = pdf_data.get('certifications')
        if isinstance(certifications, str):
            pdf_data['certifications'] = json.loads(certifications)
            logger.info("[PDF_EXPORT] normalized certifications from string")
        personal = pdf_data.get('personal_information')
        if isinstance(personal, str):
            pdf_data['personal_information'] = json.loads(personal)
            logger.info("[PDF_EXPORT] normalized personal_information from string")
        cprof = pdf_data.get('career_profile')
        if isinstance(cprof, str):
            pdf_data['career_profile'] = json.loads(cprof)
            logger.info("[PDF_EXPORT] normalized career_profile from string")
    except Exception as e:
        logger.error("[PDF_EXPORT] normalization failed: %s", e)
        raise

    # Inject profile data into personal_information section
    try:
        profile_data = profile_service.get_profile_for_cv_generation(user_email)
        if profile_data:
            logger.info("[PDF_EXPORT] Injecting profile data for user: %s", user_email)
            
            # Create personal_information section from profile
            personal_info = {
                'name': profile_data.get('full_name', ''),
                'email': profile_data.get('email', ''),
                'phone': profile_data.get('phone', ''),
                'location': profile_data.get('location', ''),
                'linkedin': profile_data.get('linkedin_url', ''),
                'github': profile_data.get('github_url', ''),
                'portfolio_links': {
                    'blogs': profile_data.get('portfolio_url', ''),
                    'website': profile_data.get('website_url', '')
                }
            }
            
            # Update the PDF data with profile information
            pdf_data['personal_information'] = personal_info
            logger.info("[PDF_EXPORT] Successfully injected profile data")
        else:
            logger.warning("[PDF_EXPORT] No profile data found for user: %s", user_email)
    except Exception as e:
        logger.error("[PDF_EXPORT] Failed to inject profile data: %s", e)
        # Continue without profile data - don't fail the PDF generation

    export_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_company = company.replace(" ", "_")
    out_path = export_dir / f"{safe_company}_tailored_resume_{ts}.pdf"
    logger.info("[PDF_EXPORT] writing to %s", out_path)

    try:
        ResumePDFGenerator(pdf_data).generate(str(out_path))
    except Exception as e:
        logger.error("[PDF_EXPORT] generation failed: %s", e)
        raise

    return out_path