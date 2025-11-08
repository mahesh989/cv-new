I'll examine the PDF export service to provide you with all the formatting details.

[1 tool called]

## 📄 **Complete PDF Formatting Specifications**

Here's a comprehensive breakdown of all PDF formatting details used in the CV generation:

---

## 🎨 **1. Page Configuration**

### **Page Size & Margins**
```python
Page Size: A4 (210mm × 297mm or 595.27 × 841.89 points)

Margins:
├── Top:    0.5 inches (36 points)
├── Bottom: 0.5 inches (36 points)
├── Left:   0.5 inches (36 points)
└── Right:  0.5 inches (36 points)

Usable Width: 523.27 points (7.27 inches)
Usable Height: 769.89 points (10.69 inches)
```

---

## 🔤 **2. Fonts & Typography**

### **Font Families**
- **Helvetica** (Regular)
- **Helvetica-Bold**
- **Helvetica-Oblique** (Italic)

### **Font Sizes by Element**

| Element | Font Size | Font Family | Weight |
|---------|-----------|-------------|--------|
| **Name** | 24pt | Helvetica-Bold | Bold |
| **Contact Info** | 10pt | Helvetica | Regular |
| **Section Headers** | 14pt | Helvetica-Bold | Bold |
| **Body Text** | 11pt | Helvetica | Regular |
| **Job Title** | 11pt | Helvetica-Bold | Bold |
| **Date (Right)** | 11pt | Helvetica | Regular |
| **Company** | 11pt | Helvetica-Oblique | Italic |
| **Degree** | 11pt | Helvetica-Bold | Bold |
| **Institution** | 11pt | Helvetica | Regular |
| **Bullet Text** | 11pt | Helvetica | Regular |
| **Skill Category** | 11pt | Helvetica-Bold | Bold |
| **Skill Item** | 11pt | Helvetica | Regular |

---

## 🎨 **3. Colors**

### **Text Colors (HEX)**
```python
Name:            #1a1a1a  (Very Dark Gray)
Section Headers: #1a1a1a  (Very Dark Gray)
Job Title:       #1a1a1a  (Very Dark Gray)
Degree:          #1a1a1a  (Very Dark Gray)
Skill Category:  #1a1a1a  (Very Dark Gray)

Contact Info:    #444444  (Medium Gray)

Body Text:       #333333  (Dark Gray)
Bullet Text:     #333333  (Dark Gray)
Skill Item:      #333333  (Dark Gray)

Date:            #555555  (Light Gray)
Company:         #555555  (Light Gray)

Hyperlinks:      blue     (Standard Blue)
```

### **Line Colors**
```python
Section Divider: #666666  (Medium Gray)
Line Thickness:  0.5 points
```

---

## 📐 **4. Spacing & Leading**

### **Vertical Spacing (in points)**

```python
spacing = {
    'section_above':      16pt   # Space before section header
    'section_below':      4pt    # Space after section header
    'subsection_gap':     12pt   # Gap between subsections
    'bullet_gap':         3pt    # Gap between bullet points
    'after_bullets':      8pt    # Space after bullet list
    'line_after_section': 6pt    # Space after section divider line
    'contact_name_gap':   -30pt  # Special: pulls contact closer to name
    'education_gap':      3pt    # Gap between education entries
}
```

### **Line Spacing (Leading)**

| Element | Leading |
|---------|---------|
| Name | 24pt |
| Contact | 10pt |
| Section Headers | 14pt |
| Body Text | 12pt |
| All other text | 12pt |

---

## 📍 **5. Alignment & Indentation**

### **Text Alignment**

```python
Name:            CENTER
Contact Info:    CENTER
Section Headers: LEFT
Body Text:       JUSTIFY
Job Title:       LEFT
Date:            RIGHT
Company:         LEFT
Institution:     LEFT
Bullet Text:     JUSTIFY
Skill Category:  LEFT
Skill Item:      LEFT
```

### **Indentation**

```python
Content Left Margin:  0pt    # Align to page edge
Bullet Indent:        18pt   # Bullet character position
Section Indent:       0pt    # No additional indent
Text Indent:          0pt    # No paragraph indent
```

### **Column Layout (Two-Column Sections)**

```python
Title Column Width:  ~4.72 inches (340.27pt)
Date Column Width:   1.8 inches (129.6pt)
Total:               6.52 inches (469.87pt)
```

---

## 🎯 **6. Section-Specific Formatting**

### **CAREER HIGHLIGHTS Section**

```python
Header: "CAREER HIGHLIGHTS" (static)
Font: Helvetica-Bold, 14pt, #1a1a1a
Divider Line: 0.5pt, #666666

Content Structure:
├── Value Statement
│   ├── Font: Helvetica, 11pt, #333333
│   ├── Alignment: JUSTIFY
│   └── Spacing: 3pt after
│
├── Bullet Points (3 items)
│   ├── Bullet: "•" (18pt indent)
│   ├── Font: Helvetica, 11pt, #333333
│   ├── Alignment: JUSTIFY
│   └── Spacing: 3pt between bullets
│
└── Skills Line
    ├── Font: Helvetica, 11pt, #333333
    ├── Alignment: JUSTIFY
    └── Spacing: 3pt after value statement
```

### **PROFESSIONAL EXPERIENCE Section**

```python
Header: "PROFESSIONAL EXPERIENCE"
Font: Helvetica-Bold, 14pt, #1a1a1a

Entry Format:
├── Job Title (Left) | Date (Right)
│   ├── Title Font: Helvetica-Bold, 11pt, #1a1a1a
│   └── Date Font: Helvetica, 11pt, #555555
│
├── Company | Location
│   ├── Font: Helvetica-Oblique, 11pt, #555555
│   └── Spacing: 8pt after
│
└── Responsibilities (Bullets)
    ├── Bullet: "•" (18pt indent)
    ├── Font: Helvetica, 11pt, #333333
    └── Spacing: 3pt between, 8pt after list
```

### **EDUCATION Section**

```python
Header: "EDUCATION"
Font: Helvetica-Bold, 14pt, #1a1a1a

Entry Format:
├── Degree (Left) | Year (Right)
│   ├── Degree Font: Helvetica-Bold, 11pt, #1a1a1a
│   └── Year Font: Helvetica, 11pt, #555555
│
├── Institution, Location
│   ├── Font: Helvetica, 11pt, #555555
│   └── Spacing: 12pt after
│
└── Entry Spacing: 3pt between entries
```

### **SKILLS Section**

```python
Header: "SKILLS"
Font: Helvetica-Bold, 14pt, #1a1a1a

Categorized Format:
└── Each Category:
    ├── Bullet: "•" (18pt indent)
    ├── Category Font: Helvetica-Bold, 11pt, #1a1a1a
    ├── Skills Font: Helvetica, 11pt, #333333
    └── Format: "Category: Skill1, Skill2, Skill3"
```

### **PROJECTS Section**

```python
Header: "PROJECTS"
Font: Helvetica-Bold, 14pt, #1a1a1a

Entry Format:
├── Project Name (Left) | Date/Duration (Right)
│   ├── Name Font: Helvetica-Bold, 11pt, #1a1a1a
│   └── Date Font: Helvetica, 11pt, #555555
│
├── Context (if available)
│   ├── Font: Helvetica-Oblique, 11pt, #555555
│   └── Example: "University Project"
│
├── Description/Bullets
│   ├── Bullet: "•" (18pt indent)
│   └── Font: Helvetica, 11pt, #333333
│
└── Technologies
    ├── Font: Helvetica-Oblique, 11pt, #555555
    └── Format: "Technologies: Python, React, Docker"
```

### **CERTIFICATIONS Section**

```python
Header: "CERTIFICATIONS"
Font: Helvetica-Bold, 14pt, #1a1a1a

Entry Format:
└── Each Certification:
    ├── Bullet: "•" (18pt indent)
    ├── Font: Helvetica, 11pt, #333333
    └── Format: "Cert Name - Issuer (Date)"
```

---

## 🔗 **7. Hyperlinks**

### **Link Formatting**

```python
Color: blue (Standard Blue)
Decoration: Underlined
Clickable: Yes

Supported Link Types:
├── Email: mailto:user@example.com
├── LinkedIn: https://linkedin.com/in/user
├── GitHub: https://github.com/user
├── Portfolio: https://portfolio.com
└── Website: https://website.com

Display Format:
├── Email: Shows full email address
└── Social Links: Shows label only (e.g., "LinkedIn")
```

---

## 📊 **8. Table Configuration**

### **All Content Uses Tables for Alignment**

```python
Table Padding (all cells):
├── Left Padding:   0pt (aligned to frame edge)
├── Right Padding:  0pt
├── Top Padding:    0pt
└── Bottom Padding: 0pt

Vertical Alignment: TOP
Horizontal Alignment: LEFT (content), RIGHT (dates)
```

---

## 📏 **9. Bullet Point Formatting**

### **Bullet Configuration**

```python
Bullet Character: "•" (Unicode U+2022)
Bullet Column Width: 18pt
Text Column Width: 505.27pt (remaining width)

Bullet Style:
├── Font: Helvetica, 11pt, #333333
├── Alignment: LEFT
└── Leading: 12pt

Text Style:
├── Font: Helvetica, 11pt, #333333
├── Alignment: JUSTIFY
├── Leading: 12pt
└── No additional indent (table handles positioning)

Spacing Between Bullets: 3pt
Spacing After Bullet List: 8pt
```

---

## 🎨 **10. Section Divider Line**

### **Horizontal Rule Specifications**

```python
Width: Full usable width (523.27pt)
Thickness: 0.5pt
Color: #666666 (Medium Gray)
Alignment: LEFT
Space Before: 2pt
Space After: 6pt
```

---

## 📦 **11. Contact Header Layout**

### **Special Formatting**

```python
Structure:
├── Name
│   ├── Font: Helvetica-Bold, 24pt, #1a1a1a
│   ├── Alignment: CENTER
│   ├── Leading: 24pt
│   └── Space After: 6pt
│
└── Contact Line (Single Line)
    ├── Font: Helvetica, 10pt, #444444
    ├── Alignment: CENTER
    ├── Leading: 10pt
    ├── Space After: 4pt
    └── Format: "Location | Phone | Email | LinkedIn | GitHub | Portfolio"

Negative Spacing: -30pt between name and contact
  (pulls contact info closer to name for compact header)
```

---

## ✨ **Summary of Key Design Principles**

1. **Consistency**: All content uses tables for perfect alignment
2. **Hierarchy**: Clear visual hierarchy using font size, weight, and color
3. **Spacing**: Consistent spacing throughout with defined gaps
4. **Readability**: 11pt body text with 12pt leading for optimal reading
5. **Professional**: Grayscale color scheme with minimal embellishments
6. **Compact**: Tight spacing (-30pt name gap) for efficient space usage
7. **Alignment**: All left-aligned content starts at exact same position
8. **Modern**: Clean sans-serif font (Helvetica) throughout

---

**Total Specification**: This PDF uses **13 custom paragraph styles**, **consistent 0.5-inch margins**, **grayscale colors**, and **precise spacing** to create a professional, ATS-friendly CV format. 🎯