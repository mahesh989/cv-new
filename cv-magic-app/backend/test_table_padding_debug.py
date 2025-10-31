#!/usr/bin/env python3
"""
Debug script to understand ReportLab table padding behavior
"""
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate

styles = getSampleStyleSheet()

# Create test document
doc = SimpleDocTemplate('/tmp/padding_test.pdf', pagesize=A4,
                       leftMargin=0.5*inch, rightMargin=0.5*inch,
                       topMargin=0.5*inch, bottomMargin=0.5*inch)

page_width = A4[0]
left_margin = 0.5 * inch
right_margin = 0.5 * inch
usable_width = page_width - left_margin - right_margin

elements = []

# Test 1: Paragraph WITHOUT table (baseline)
p1 = Paragraph("1. Direct paragraph (NO table) - BASELINE", styles['Normal'])
elements.append(p1)

# Test 2: Paragraph in table WITH default padding (no TableStyle)
p2 = Paragraph("2. Paragraph in table with DEFAULT padding (should be indented ~6pts)", styles['Normal'])
t2 = Table([[p2]], colWidths=[usable_width])
elements.append(t2)

# Test 3: Paragraph in table WITH TableStyle LEFTPADDING=0
p3 = Paragraph("3. Paragraph in table with LEFTPADDING=0 (should match baseline)", styles['Normal'])
t3 = Table([[p3]], colWidths=[usable_width])
t3.setStyle(TableStyle([
    ('LEFTPADDING', (0, 0), (0, 0), 0),
    ('RIGHTPADDING', (0, 0), (0, 0), 0),
    ('TOPPADDING', (0, 0), (0, 0), 0),
    ('BOTTOMPADDING', (0, 0), (0, 0), 0),
]))
elements.append(t3)

# Test 4: Paragraph in table WITH style parameter (not setStyle)
p4 = Paragraph("4. Paragraph in table with style= parameter LEFTPADDING=0", styles['Normal'])
t4 = Table([[p4]], colWidths=[usable_width], style=[
    ('LEFTPADDING', (0, 0), (0, 0), 0),
    ('RIGHTPADDING', (0, 0), (0, 0), 0),
    ('TOPPADDING', (0, 0), (0, 0), 0),
    ('BOTTOMPADDING', (0, 0), (0, 0), 0),
])
elements.append(t4)

# Test 5: Check if (-1, -1) range works differently
p5 = Paragraph("5. Paragraph in table with LEFTPADDING=0 using (-1,-1) range", styles['Normal'])
t5 = Table([[p5]], colWidths=[usable_width])
t5.setStyle(TableStyle([
    ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ('TOPPADDING', (0, 0), (-1, -1), 0),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
]))
elements.append(t5)

doc.build(elements)
print("Padding test PDF created: /tmp/padding_test.pdf")
print("Check if tests 3, 4, 5 align with test 1 (baseline)")
print("If test 2 is indented but others align, TableStyle is working correctly")
print("If ALL tests 2-5 are indented, there's a deeper issue")

