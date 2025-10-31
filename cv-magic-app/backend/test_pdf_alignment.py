#!/usr/bin/env python3
"""
Test script to diagnose PDF alignment issues
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle,
)
from reportlab.lib import colors

# Create a test PDF
filename = '/tmp/alignment_test.pdf'
doc = SimpleDocTemplate(
    filename,
    pagesize=A4,
    rightMargin=0.5 * inch,
    leftMargin=0.5 * inch,
    topMargin=0.5 * inch,
    bottomMargin=0.5 * inch,
)

styles = getSampleStyleSheet()

# Create custom styles with NO leftIndent
styles.add(ParagraphStyle(
    name='SectionHeader',
    parent=styles['Normal'],
    fontSize=14,
    fontName='Helvetica-Bold',
    leftIndent=0,
    rightIndent=0,
))

styles.add(ParagraphStyle(
    name='TableParagraph',
    parent=styles['Normal'],
    fontSize=11,
    leftIndent=0,
    rightIndent=0,
    alignment=TA_JUSTIFY,
))

# Calculate dimensions
page_width = A4[0]
left_margin = 0.5 * inch
right_margin = 0.5 * inch
usable_width = page_width - left_margin - right_margin

print(f"Page width: {page_width}")
print(f"Left margin: {left_margin}")
print(f"Right margin: {right_margin}")
print(f"Usable width: {usable_width}")
print(f"SectionHeader leftIndent: {styles['SectionHeader'].leftIndent}")
print(f"TableParagraph leftIndent: {styles['TableParagraph'].leftIndent}")
print(f"Normal leftIndent: {styles['Normal'].leftIndent}")

elements = []

# Test 1: Section header (direct paragraph)
elements.append(Paragraph("SECTION HEADER (Direct)", styles['SectionHeader']))

# Test 2: Horizontal line (direct HRFlowable)
elements.append(HRFlowable(
    width=usable_width,
    thickness=0.5,
    color=colors.black,
    spaceBefore=2,
    spaceAfter=6,
))

# Test 3: Content in table with LEFTPADDING=0
para = Paragraph("Content wrapped in table with LEFTPADDING=0 (Should align with section header and line)", styles['TableParagraph'])
tbl = Table([[para]], colWidths=[usable_width])
tbl.setStyle(TableStyle([
    ('LEFTPADDING', (0, 0), (0, 0), 0),
    ('RIGHTPADDING', (0, 0), (0, 0), 0),
    ('TOPPADDING', (0, 0), (0, 0), 0),
    ('BOTTOMPADDING', (0, 0), (0, 0), 0),
]))
elements.append(tbl)

elements.append(Spacer(1, 20))

# Test 4: Direct paragraph (no table)
elements.append(Paragraph("Direct paragraph with NO table wrapper (Should also align)", styles['TableParagraph']))

elements.append(Spacer(1, 20))

# Test 5: Paragraph with leftIndent=10 for comparison
styles.add(ParagraphStyle(
    name='Indented10',
    parent=styles['Normal'],
    fontSize=11,
    leftIndent=10,
    rightIndent=0,
))
elements.append(Paragraph("This paragraph has leftIndent=10 for comparison", styles['Indented10']))

# Build PDF
doc.build(elements)

print(f"\nTest PDF created: {filename}")
print("Transfer this file from the VPS to check alignment visually.")

