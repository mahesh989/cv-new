// Test to demonstrate the new direct display approach for AI Recommendations
// This shows how your backend data will now be displayed exactly like Analyze Match

import 'package:flutter/material.dart';
import 'lib/utils/text_formatter.dart';

void main() {
  runApp(TestApp());
}

class TestApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Recommendations Direct Display Test',
      theme: ThemeData(primarySwatch: Colors.amber),
      home: TestScreen(),
    );
  }
}

class TestScreen extends StatelessWidget {
  // Your actual backend data - now displayed with full fidelity
  final String sampleRecommendation = '''# 🎯 CV Tailoring Strategy Report for Nine_Entertainment

## 📊 Executive Summary
- **Current ATS Score:** 61.737500000000004/100 (⚠️ Moderate fit)
- **Key Strengths:** 
  - Technical Depth (90.0/100)
  - Core Competency (82.5%)
  - Learning Agility (85.0%)
  - Skills Relevance (85.0%)
- **Critical Gaps:**
  - Domain Keywords Match (0.0%)
  - Soft Skills Match (25.0%)
  - Technical Skills Match (43.0%)
- **Success Probability:** Moderate, with potential for improvement through targeted keyword integration and experience reframing.

## 🔍 Priority Gap Analysis
**Immediate Action Required (Low Scores):**
- Domain Keywords Match: 0.0%
- Soft Skills Match: 25.0%

**Optimization Opportunities (Medium Scores):**
- Technical Skills Match: 43.0%
- Experience/Seniority: 73.0%
- Company Fit: 61.25%

**Strength Amplification (High Scores):**
- Technical Depth: 90.0%
- Core Competency: 82.5%
- Learning Agility: 85.0%

## 🛠️ Keyword Integration Strategy
**Critical Missing Keywords (0% domain match):**
- **Business Intelligence:** Highlight any projects involving insights delivery or BI tools.
  - **Injection Point:** Use in project descriptions or achievements related to data insights and decision-making processes.

**Technical Skills Enhancement (43.0% current match):**
- **Data Engineering, Data Modelling, ETL:** Emphasize relevant coursework or projects from academic background.
  - **Injection Point:** Include in the skills section and relevant project experiences where you have applied these concepts.

**Soft Skills Optimization (25.0% current match):**
- **Proactive, Results-Driven:** Document instances where you have anticipated project needs or driven results.
  - **Injection Point:** Use these terms in descriptions of team projects or initiatives you led.

## 🎪 Experience Reframing Strategy
**Industry Transition Focus (70.0/100 current fit):**
- **Reframe Analytical Experience:** Highlight data analysis projects as foundational to data engineering roles.
  - **Integration:** Emphasize how these projects have driven business insights and supported decision-making.

**Seniority Positioning (75.0/100 current match):**
- **Highlight Leadership:** Document any mentoring or leadership roles in academic or professional settings.
  - **Integration:** Use specific examples of leading team projects or initiatives.

**Technical Depth Showcase (90.0/100 current score):**
- **Complexity Indicators:** Detail any complex data scenarios or challenges tackled.
  - **Integration:** Use in project summaries to demonstrate problem-solving and technical acumen.

## 📈 ATS Score Improvement Roadmap
**Target Score:** Aim for a score of 75/100 or above.

**High-Impact Changes (Expected +10-15 points):**
1. **Domain Keyword Integration:** Focus on incorporating business intelligence and data analytics terms.
2. **Technical Skills Enhancement:** Explicitly include data engineering and modeling terms in the CV.

**Medium-Impact Changes (Expected +5-10 points):**
1. **Soft Skills Evidence:** Provide clear examples of proactive and results-driven actions.
2. **Experience Reframing:** Reframe technical experiences to align with industry expectations.

**Fine-Tuning (Expected +2-5 points):**
1. **Polish Language:** Ensure all technical terms and experiences are clearly articulated and match job description terminology.
2. **Structured Layout:** Ensure CV format is ATS-friendly with clear headings and bullet points.

---

**Strategic Note:** This analysis is based on comprehensive data including actual ATS calculations, component analysis, and strategic assessment. Focus on evidence-based improvements that maximize authenticity while optimizing for ATS performance and interview success.''';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Direct Display Approach'),
        backgroundColor: Colors.amber.shade600,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Show the approach comparison
            _buildComparisonHeader(),
            SizedBox(height: 20),
            
            // Show how AI Recommendations now displays (like Analyze Match)
            _buildRecommendationDisplay(),
          ],
        ),
      ),
    );
  }

  Widget _buildComparisonHeader() {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Implementation Approach: Direct Display',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 8),
          Text(
            '✅ SAME AS ANALYZE MATCH: Full content preservation\n'
            '✅ NO PARSING: Direct display of backend markdown\n'
            '✅ RICH FORMATTING: Uses existing TextFormatter system\n'
            '✅ CONSISTENT UX: Same approach across both systems',
            style: TextStyle(fontSize: 14),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationDisplay() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.amber.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.amber.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header (matches the real implementation)
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
            child: Row(
              children: [
                Icon(
                  Icons.lightbulb_outline,
                  color: Colors.amber.shade700,
                  size: 24,
                ),
                const SizedBox(width: 8),
                Text(
                  '💡 AI RECOMMENDATIONS',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.amber.shade700,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 4),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Text(
              'Personalized suggestions to improve your ATS score',
              style: TextStyle(
                fontSize: 14,
                color: Colors.amber.shade600,
                fontStyle: FontStyle.italic,
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Direct content display (like Analyze Match)
          Container(
            width: double.infinity,
            margin: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.amber.shade200),
            ),
            child: RecommendationFormattedText(
              text: sampleRecommendation,
            ),
          ),
        ],
      ),
    );
  }
}