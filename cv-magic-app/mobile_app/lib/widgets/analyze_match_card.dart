import 'package:flutter/material.dart';
import '../utils/text_formatter.dart';

/// Analyze Match Card - Displays CV-JD matching analysis
/// Shows AFTER Detailed Skills Display when analyze match data is ready
class AnalyzeMatchCard extends StatelessWidget {
  final String rawAnalysis;
  final String? companyName;

  const AnalyzeMatchCard({
    super.key,
    required this.rawAnalysis,
    this.companyName,
  });

  @override
  Widget build(BuildContext context) {
    // Check if we have valid analysis
    if (rawAnalysis.trim().isEmpty) {
      return _buildEmptyState();
    }

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      elevation: 4,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            colors: [
              Colors.deepOrange.shade50,
              Colors.deepOrange.shade100,
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Colors.deepOrange.shade700,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(
                      Icons.analytics,
                      color: Colors.white,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Analyze Match',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.deepOrange.shade900,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          'Recruiter-Style Assessment',
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.deepOrange.shade700,
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (companyName != null) ...[ 
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: Colors.deepOrange.shade300,
                          width: 2,
                        ),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.business,
                            size: 16,
                            color: Colors.deepOrange.shade700,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            companyName!,
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: Colors.deepOrange.shade800,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
              const SizedBox(height: 20),

              // Analysis Content
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: Colors.deepOrange.shade200,
                    width: 2,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.deepOrange.shade100,
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: _buildFormattedAnalysis(rawAnalysis),
              ),

              // Info footer
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.deepOrange.shade50.withOpacity(0.5),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: Colors.deepOrange.shade200,
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.info_outline,
                      size: 16,
                      color: Colors.deepOrange.shade700,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'This analysis simulates how a recruiter would evaluate your CV against the job requirements',
                        style: TextStyle(
                          fontSize: 11,
                          color: Colors.deepOrange.shade800,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFormattedAnalysis(String analysis) {
    // Use TextFormatter utility to format the analysis text
    final formatted = TextFormatter.formatAnalysisText(analysis);
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: formatted.map((block) {
        if (block.type == TextBlockType.heading) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 8.0, top: 12.0),
            child: Text(
              block.content,
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.bold,
                color: Colors.deepOrange.shade800,
              ),
            ),
          );
        } else if (block.type == TextBlockType.bullet) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 6.0, left: 12.0),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '• ',
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.deepOrange.shade700,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Expanded(
                  child: Text(
                    block.content,
                    style: TextStyle(
                      fontSize: 13,
                      color: Colors.grey.shade800,
                      height: 1.5,
                    ),
                  ),
                ),
              ],
            ),
          );
        } else {
          // Regular paragraph
          return Padding(
            padding: const EdgeInsets.only(bottom: 10.0),
            child: Text(
              block.content,
              style: TextStyle(
                fontSize: 13,
                color: Colors.grey.shade800,
                height: 1.6,
              ),
            ),
          );
        }
      }).toList(),
    );
  }

  Widget _buildEmptyState() {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Row(
              children: [
                Icon(Icons.analytics, color: Colors.grey.shade400),
                const SizedBox(width: 8),
                Text(
                  'Analyze Match',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey.shade600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'No analyze match results available',
              style: TextStyle(
                fontSize: 13,
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
