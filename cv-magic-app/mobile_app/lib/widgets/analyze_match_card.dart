import 'package:flutter/material.dart';

/// Analyze Match Card - Displays CV-JD matching analysis in table format
/// Shows CV vs JD keyword comparison with match status
class AnalyzeMatchCard extends StatelessWidget {
  final Map<String, dynamic> matchData;
  final String? companyName;

  const AnalyzeMatchCard({
    super.key,
    required this.matchData,
    this.companyName,
  });

  @override
  Widget build(BuildContext context) {
    // Check if we have valid match data
    if (matchData.isEmpty) {
      return _buildEmptyState();
    }

    // Extract data
    final matchedRequired = List<String>.from(matchData['matched_required_keywords'] ?? []);
    final matchedPreferred = List<String>.from(matchData['matched_preferred_keywords'] ?? []);
    final missedRequired = List<String>.from(matchData['missed_required_keywords'] ?? []);
    final missedPreferred = List<String>.from(matchData['missed_preferred_keywords'] ?? []);
    final matchCounts = matchData['match_counts'] as Map<String, dynamic>? ?? {};
    
    final totalRequired = matchCounts['total_required_keywords'] ?? 0;
    final totalPreferred = matchCounts['total_preferred_keywords'] ?? 0;
    final matchedRequiredCount = matchCounts['matched_required_count'] ?? 0;
    final matchedPreferredCount = matchCounts['matched_preferred_count'] ?? 0;
    
    // Calculate percentages
    final requiredPercent = totalRequired > 0 ? (matchedRequiredCount / totalRequired * 100).round() : 0;
    final preferredPercent = totalPreferred > 0 ? (matchedPreferredCount / totalPreferred * 100).round() : 0;

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

              // Match Statistics
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.deepOrange.shade200, width: 2),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildStatColumn('Required', matchedRequiredCount, totalRequired, requiredPercent, Colors.red),
                    _buildStatColumn('Preferred', matchedPreferredCount, totalPreferred, preferredPercent, Colors.orange),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Keyword Matching Tables
              _buildMatchingTable('Required Keywords', matchedRequired, missedRequired, Colors.red),
              const SizedBox(height: 12),
              _buildMatchingTable('Preferred Keywords', matchedPreferred, missedPreferred, Colors.orange),

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

  Widget _buildStatColumn(String label, int matched, int total, int percent, MaterialColor color) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: color.shade800,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          '$matched / $total',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: color.shade700,
          ),
        ),
        const SizedBox(height: 4),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
          decoration: BoxDecoration(
            color: color.shade100,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            '$percent%',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: color.shade900,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMatchingTable(String title, List<String> matched, List<String> missed, MaterialColor color) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.shade200, width: 2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Table Header
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.shade100,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(10),
                topRight: Radius.circular(10),
              ),
            ),
            child: Text(
              title,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: color.shade900,
              ),
            ),
          ),
          
          // Table Content
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Matched Keywords Row
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 100,
                      child: Row(
                        children: [
                          Icon(Icons.check_circle, color: Colors.green.shade600, size: 18),
                          const SizedBox(width: 4),
                          Text(
                            'Matched',
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                              color: Colors.green.shade800,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: matched.isEmpty
                          ? Text('None', style: TextStyle(fontSize: 12, color: Colors.grey.shade600))
                          : Wrap(
                              spacing: 6,
                              runSpacing: 6,
                              children: matched.map((keyword) => Chip(
                                label: Text(keyword, style: const TextStyle(fontSize: 11)),
                                backgroundColor: Colors.green.shade100,
                                padding: const EdgeInsets.all(4),
                                materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                              )).toList(),
                            ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                
                // Missed Keywords Row
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 100,
                      child: Row(
                        children: [
                          Icon(Icons.cancel, color: Colors.red.shade600, size: 18),
                          const SizedBox(width: 4),
                          Text(
                            'Missed',
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                              color: Colors.red.shade800,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: missed.isEmpty
                          ? Text('None', style: TextStyle(fontSize: 12, color: Colors.grey.shade600))
                          : Wrap(
                              spacing: 6,
                              runSpacing: 6,
                              children: missed.map((keyword) => Chip(
                                label: Text(keyword, style: const TextStyle(fontSize: 11)),
                                backgroundColor: Colors.red.shade100,
                                padding: const EdgeInsets.all(4),
                                materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                              )).toList(),
                            ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
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
