# LLM Skill Extraction Accuracy Analysis

## Job Description: BI Engineer/Data Analyst - Nine Entertainment

### 🔍 EXTRACTED BY LLM:

**Technical Skills (12 extracted):**
1. SQL ✓
2. Power BI ✓
3. Tableau ✓
4. Data Modelling ✓
5. Data Warehousing ✓
6. ETL ✓
7. Snowflake ✓
8. Version Control ✓
9. Role-based Access Controls ✓
10. Data Quality Assurance ✓
11. Data Visualization ✓
12. Self-service Reporting ✓

**Soft Skills (5 extracted):**
1. Communication ✓
2. Detail-oriented ✓
3. Collaboration ✓
4. Problem-solving ✓
5. Adaptability ✓

**Domain Keywords (9 extracted):**
1. Business Intelligence ✓
2. Data Aggregation ✓
3. Data Integrity ✓
4. Data Quality ✓
5. Reporting ✓
6. Insights Delivery ✓
7. Data Operations ✓
8. Data Pipelines ✓
9. Business Decision-Making ✓

---

### ❌ MISSED BY LLM:

**Technical Skills Missed:**
1. **Documentation** - "best practices for BI development including version control, documentation..."
2. **Performance Optimization** - "performance optimisation" (explicitly mentioned)
3. **Dimensional Modeling** - "dimensional modelling" (specific type of data modeling)
4. **Advanced SQL** - The JD specifically says "Write advanced SQL queries" not just SQL
5. **Data Loading** - "Experience with data loading, transformation..."
6. **RAG (Retrieval-Augmented Generation)** - "Experience with next-generation architectures such as Vector Databases and RAG"
7. **Vector Databases** - Mentioned as nice-to-have but still a technical skill

**Soft Skills Missed:**
1. **Proactive mindset** - "A proactive, detail-oriented mindset"
2. **Stakeholder Management** - "Work closely with analysts, product teams, and business leaders"
3. **Translation Skills** - "translate business needs into technical data solutions"
4. **Teaching/Mentoring** - Implied by "self-service reporting capabilities, empowering business users"

**Domain Keywords Missed:**
1. **Automotive Industry** - "Drive is Nine's brand appealing to the automotive enthusiast"
2. **Media Organisation** - "Australia's largest media organisation"
3. **Governance Standards** - "ensuring data integrity and governance standards"
4. **Security Measures** - "security measures to safeguard sensitive data"
5. **Analytics Needs** - "support reporting and analytics needs"
6. **Actionable Insights** - "deliver clear, actionable insights"
7. **Visual Stories** - "Translate complex datasets into compelling visual stories"
8. **BI/Visualization Trends** - "Stay up to date with BI/visualisation trends"

---

### 📊 EXTRACTION ACCURACY ASSESSMENT:

**Technical Skills:** 
- **Accuracy: 63%** (12 out of 19 potential skills extracted)
- **Critical Misses:** Advanced SQL specificity, Performance Optimization, Documentation

**Soft Skills:**
- **Accuracy: 56%** (5 out of 9 potential skills extracted)
- **Critical Misses:** Proactive mindset, Stakeholder Management

**Domain Keywords:**
- **Accuracy: 53%** (9 out of 17 potential keywords extracted)
- **Critical Misses:** Industry context (Automotive, Media), Governance/Security concepts

---

### 🎯 KEY INSIGHTS:

1. **The LLM tends to extract high-level/generic skills** but misses:
   - Specific qualifiers (e.g., "Advanced" SQL vs just SQL)
   - Industry-specific context (Automotive, Media)
   - Nuanced soft skills (Proactive mindset, Translation skills)

2. **Nice-to-have skills are often ignored** even though they're still relevant:
   - RAG and Vector Databases were completely missed
   - These could be differentiators for candidates

3. **Compound concepts are simplified:**
   - "Version control, documentation, and performance optimisation" → Only extracted "Version Control"
   - "Data loading, transformation, and performance optimization" → Only extracted general ETL

4. **Context is lost:**
   - The job is specifically for an automotive media company, but this domain context wasn't captured
   - Security and governance aspects were underrepresented

---

### 💡 RECOMMENDATIONS FOR IMPROVEMENT:

1. **Enhance Prompt Engineering:**
   ```python
   # Add explicit instructions to capture:
   - Skill qualifiers (advanced, expert, basic, etc.)
   - Nice-to-have skills separately
   - Industry/domain context
   - All components of compound requirements
   ```

2. **Post-Processing Enhancement:**
   ```python
   # Add rules to:
   - Detect and preserve skill level indicators
   - Extract industry keywords from company description
   - Parse compound skill lists more carefully
   - Include "nice-to-have" skills with a flag
   ```

3. **Validation Layer:**
   ```python
   # Implement checks for:
   - Common missed patterns (e.g., "advanced X" → ensure "advanced" is captured)
   - Industry terms in company description that should be domain keywords
   - Security/governance terms that are often missed
   ```

4. **Structured Extraction:**
   - Consider using a more structured approach with predefined skill categories
   - Use regex patterns to catch specific skill patterns
   - Implement a two-pass extraction: first LLM, then rule-based enhancement

---

### 📈 IMPACT ON MATCHING:

The current extraction misses could lead to:
1. **False negatives** - Candidates with "advanced SQL" skills might not match properly
2. **Lost context** - Automotive industry experience wouldn't be recognized
3. **Incomplete assessment** - Security and governance skills wouldn't be evaluated
4. **Missed opportunities** - Candidates with RAG/Vector DB experience wouldn't get bonus points

**Overall Extraction Quality: C+ (60-65% accuracy)**

The extraction captures the main requirements but misses important nuances and context that could significantly impact match quality.
