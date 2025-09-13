import 'package:flutter/material.dart';
import 'widgets/ats_score_widget_with_pie_chart.dart';

/// Demo page to showcase the ATS Score Analysis with Pie Chart
class ATSPieChartDemo extends StatelessWidget {
  const ATSPieChartDemo({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ATS Score Analysis - Pie Chart Demo'),
        backgroundColor: Colors.orange[800],
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Demo with good scores
            ATSScoreWithPieChartWidget(
              finalATSScore: 69.1,
              categoryStatus: 'Moderate fit',
              recommendation: 'Consider if other factors are strong',
              skillsRelevanceScore: 84.0,
              experienceAlignmentScore: 70.0,
              hasComponentAnalysis: true,
            ),
            
            // Demo with excellent scores
            ATSScoreWithPieChartWidget(
              finalATSScore: 92.5,
              categoryStatus: 'Excellent fit',
              recommendation: 'Strong candidate profile',
              skillsRelevanceScore: 95.0,
              experienceAlignmentScore: 88.0,
              hasComponentAnalysis: true,
            ),
            
            // Demo with lower scores
            ATSScoreWithPieChartWidget(
              finalATSScore: 45.2,
              categoryStatus: 'Needs improvement',
              recommendation: 'Focus on skill alignment and experience relevance',
              skillsRelevanceScore: 52.0,
              experienceAlignmentScore: 38.0,
              hasComponentAnalysis: false,
            ),
          ],
        ),
      ),
    );
  }
}

/// Main function for standalone demo
void main() {
  runApp(MaterialApp(
    title: 'ATS Pie Chart Demo',
    theme: ThemeData(
      primarySwatch: Colors.orange,
      fontFamily: 'GoogleFonts', // This would need google_fonts package
    ),
    home: const ATSPieChartDemo(),
    debugShowCheckedModeBanner: false,
  ));
}