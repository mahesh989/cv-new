import 'package:flutter/material.dart';
import '../models/skills_analysis_model.dart';
import 'analyze_match_widget.dart';

/// Test widget to isolate analyze match display issues
class TestAnalyzeMatchWidget extends StatelessWidget {
  const TestAnalyzeMatchWidget({super.key});

  @override
  Widget build(BuildContext context) {
    // Create dummy analyze match data
    final dummyAnalyzeMatch = AnalyzeMatchResult(
      rawAnalysis: '''**EXPERIENCED RECRUITER ASSESSMENT:**

**DECISION:** 🟢 STRONG PURSUE

**MARKET REALITY CHECK:**
- **What they actually need:** Strong analytical skills, experience with data mining and BI tools
- **Flexibility indicators:** Experience in a similar role, willingness to learn and adapt
- **Hard blockers identified:** None apparent
- **Hiring urgency signals:** Not specified, but the nature of the organization suggests a need for timely support

**INTELLIGENT OBSERVATIONS:**
- **Hidden strengths:** PhD in Physics showcases strong analytical abilities, experience in Python programming aligns well with data analysis requirements
- **Smart connections:** Proficiency in SQL and data visualization tools like Tableau and Power BI are directly relevant
- **Growth potential:** Demonstrated ability to learn and adapt in various roles, potential to excel in data-driven decision-making environments

**REALISTIC ODDS:** 60-70% chance of getting an interview if CV tailored well

**IF PURSUING - STRATEGIC PRIORITIES:**
1. **[Priority 1]**: Highlight experience with data mining and BI tools, showcase projects involving analytics and business-critical insights
2. **[Priority 2]**: Emphasize strong analytical and problem-solving skills, tie back to the impact on business decisions
3. **[Priority 3]**: Address any gaps in direct marketing campaign experience, showcase understanding of donor-centric strategies

**HONEST BOTTOM LINE:** With a strong foundation in data analysis and relevant technical skills, tailoring the CV to emphasize direct relevance to the role can make this candidate a strong contender for the position. It's worth the effort to pursue this opportunity.''',
      companyName: 'Australia_for_UNHCR',
      filePath: '/test/path.txt',
    );

    return Scaffold(
      appBar: AppBar(
        title: const Text('Test Analyze Match'),
        backgroundColor: Colors.orange.shade600,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Test loading state
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: Text(
                'Loading State Test:',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            AnalyzeMatchWidget(
              analyzeMatch: null,
              isLoading: true,
            ),

            const SizedBox(height: 20),

            // Test content state
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: Text(
                'Content State Test:',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            AnalyzeMatchWidget(
              analyzeMatch: dummyAnalyzeMatch,
              isLoading: false,
            ),

            const SizedBox(height: 20),

            // Test empty state
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: Text(
                'Empty State Test:',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            AnalyzeMatchWidget(
              analyzeMatch: AnalyzeMatchResult(
                rawAnalysis: '',
                companyName: 'Test Company',
              ),
              isLoading: false,
            ),

            const SizedBox(height: 20),

            // Test error state
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: Text(
                'Error State Test:',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            AnalyzeMatchWidget(
              analyzeMatch: AnalyzeMatchResult(
                rawAnalysis: '',
                companyName: 'Test Company',
                error: 'Test error message',
              ),
              isLoading: false,
            ),
          ],
        ),
      ),
    );
  }
}
