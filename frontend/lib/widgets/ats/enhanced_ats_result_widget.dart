import 'package:flutter/material.dart';
import '../../theme/app_theme.dart';

class EnhancedATSResultWidget extends StatelessWidget {
  final Map<String, dynamic> skillComparison;

  const EnhancedATSResultWidget({
    super.key,
    required this.skillComparison,
  });

  @override
  Widget build(BuildContext context) {
    final matchSummary = skillComparison['match_summary'] ?? {};
    final isEnhanced = matchSummary['enhanced_analysis'] == true;
    final enhancedReasoning = skillComparison['enhanced_reasoning'] ?? {};

    debugPrint('🧠 [EnhancedATS] Building enhanced result widget');
    debugPrint('🧠 [EnhancedATS] Enhanced analysis: $isEnhanced');
    debugPrint('🧠 [EnhancedATS] Match summary: $matchSummary');

    return Card(
      elevation: 8,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              AppTheme.primaryCosmic.withOpacity(0.05),
              AppTheme.primaryTeal.withOpacity(0.05),
            ],
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with AI badge
            Row(
              children: [
                Icon(
                  isEnhanced ? Icons.psychology : Icons.analytics,
                  color: AppTheme.primaryCosmic,
                  size: 28,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isEnhanced
                            ? '🤖 AI-POWERED SKILLS ANALYSIS'
                            : '📊 SKILLS COMPARISON RESULTS',
                        style: AppTheme.headingSmall.copyWith(
                          color: AppTheme.primaryCosmic,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      if (isEnhanced)
                        Text(
                          'Enhanced semantic matching with detailed reasoning',
                          style: AppTheme.bodySmall.copyWith(
                            color: AppTheme.primaryTeal,
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                    ],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 20),

            // Overall Summary
            _buildOverallSummary(matchSummary),

            const SizedBox(height: 24),

            // Summary Table (Python-inspired)
            _buildSummaryTable(),

            const SizedBox(height: 24),

            // Category breakdown
            if (isEnhanced && enhancedReasoning.isNotEmpty) ...[
              _buildEnhancedAnalysis(enhancedReasoning),
            ] else ...[
              _buildStandardAnalysis(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildOverallSummary(Map<String, dynamic> summary) {
    final totalMatched = summary['total_matched'] ?? 0;
    final totalMissing = summary['total_missing'] ?? 0;
    final totalRequirements =
        summary['total_requirements'] ?? (totalMatched + totalMissing);
    final matchPercentage = summary['match_percentage'] ?? 0.0;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.primaryCosmic.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: AppTheme.primaryCosmic.withOpacity(0.2),
        ),
      ),
      child: Column(
        children: [
          Text(
            '🎯 OVERALL SUMMARY',
            style: AppTheme.bodyLarge.copyWith(
              fontWeight: FontWeight.bold,
              color: AppTheme.primaryCosmic,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildSummaryItem(
                  'Total Requirements', totalRequirements.toString()),
              _buildSummaryItem('Matched', totalMatched.toString()),
              _buildSummaryItem('Missing', totalMissing.toString()),
              _buildSummaryItem(
                  'Match Rate', '${matchPercentage.toStringAsFixed(1)}%'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: AppTheme.headingSmall.copyWith(
            color: AppTheme.primaryCosmic,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: AppTheme.bodySmall.copyWith(
            color: AppTheme.neutralGray600,
          ),
        ),
      ],
    );
  }

  Widget _buildEnhancedAnalysis(Map<String, dynamic> enhancedReasoning) {
    final categories = {
      'technical_skills': '🔧 Technical Skills',
      'soft_skills': '🤝 Soft Skills',
      'domain_keywords': '🎯 Domain Keywords'
    };

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '🧠 DETAILED AI ANALYSIS',
          style: AppTheme.bodyLarge.copyWith(
            fontWeight: FontWeight.bold,
            color: AppTheme.primaryCosmic,
          ),
        ),
        const SizedBox(height: 16),
        ...categories.entries.map((entry) {
          final category = entry.key;
          final categoryName = entry.value;
          final categoryReasoning =
              enhancedReasoning[category] as List<dynamic>? ?? [];

          if (categoryReasoning.isEmpty) return const SizedBox.shrink();

          return _buildCategoryAnalysis(categoryName, categoryReasoning);
        }).toList(),
      ],
    );
  }

  Widget _buildCategoryAnalysis(String categoryName, List<dynamic> reasoning) {
    final matched =
        reasoning.where((item) => item['type'] == 'matched').toList();
    final missing =
        reasoning.where((item) => item['type'] == 'missing').toList();

    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.neutralGray200),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Category header
          Text(
            categoryName.toUpperCase(),
            style: AppTheme.bodyLarge.copyWith(
              fontWeight: FontWeight.bold,
              color: AppTheme.primaryCosmic,
            ),
          ),
          const Divider(height: 20),

          // Matched skills with reasoning
          if (matched.isNotEmpty) ...[
            Text(
              '✅ MATCHED JD REQUIREMENTS (${matched.length} items):',
              style: AppTheme.bodyMedium.copyWith(
                fontWeight: FontWeight.w600,
                color: Colors.green.shade700,
              ),
            ),
            const SizedBox(height: 8),
            ...matched.asMap().entries.map((entry) {
              final index = entry.key;
              final item = entry.value;
              return _buildMatchedItem(index + 1, item);
            }).toList(),
            const SizedBox(height: 16),
          ],

          // Missing skills with reasoning
          if (missing.isNotEmpty) ...[
            Text(
              '❌ MISSING FROM CV (${missing.length} items):',
              style: AppTheme.bodyMedium.copyWith(
                fontWeight: FontWeight.w600,
                color: Colors.red.shade700,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              '(JD requirements NOT covered by your CV)',
              style: AppTheme.bodySmall.copyWith(
                color: Colors.red.shade600,
                fontStyle: FontStyle.italic,
              ),
            ),
            const SizedBox(height: 8),
            ...missing.asMap().entries.map((entry) {
              final index = entry.key;
              final item = entry.value;
              return _buildMissingItem(index + 1, item);
            }).toList(),
          ],
        ],
      ),
    );
  }

  Widget _buildMatchedItem(int index, Map<String, dynamic> item) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.green.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '$index. JD Required: \'${item['skill']}\'',
            style: AppTheme.bodyMedium.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            '→ Found in CV: \'${item['cv_equivalent']}\'',
            style: AppTheme.bodyMedium.copyWith(
              color: Colors.green.shade700,
            ),
          ),
          const SizedBox(height: 6),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '💡 ',
                style: AppTheme.bodySmall,
              ),
              Expanded(
                child: Text(
                  item['reasoning'] ?? 'AI semantic match',
                  style: AppTheme.bodySmall.copyWith(
                    color: AppTheme.neutralGray600,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMissingItem(int index, Map<String, dynamic> item) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '$index. JD Requires: \'${item['skill']}\'',
            style: AppTheme.bodyMedium.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 6),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '💡 ',
                style: AppTheme.bodySmall,
              ),
              Expanded(
                child: Text(
                  item['reasoning'] ?? 'Not found in CV',
                  style: AppTheme.bodySmall.copyWith(
                    color: AppTheme.neutralGray600,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStandardAnalysis() {
    // Fallback to standard display if no enhanced reasoning
    return Text(
      'Standard skill comparison (no detailed reasoning available)',
      style: AppTheme.bodyMedium.copyWith(
        color: AppTheme.neutralGray600,
        fontStyle: FontStyle.italic,
      ),
    );
  }

  Widget _buildSummaryTable() {
    final matched = skillComparison['matched'] ?? {};
    final missing = skillComparison['missing'] ?? {};
    final matchSummary = skillComparison['match_summary'] ?? {};

    // Calculate table data similar to Python's get_summary_dataframe
    final tableData = <Map<String, dynamic>>[];

    final categories = {
      'technical_skills': 'Technical Skills',
      'soft_skills': 'Soft Skills',
      'domain_keywords': 'Domain Keywords'
    };

    for (final entry in categories.entries) {
      final category = entry.key;
      final categoryName = entry.value;

      final matchedList = matched[category] as List<dynamic>? ?? [];
      final missingList = missing[category] as List<dynamic>? ?? [];

      final matchedCount = matchedList.length;
      final missingCount = missingList.length;
      final totalJD = matchedCount + missingCount;
      final matchRate = totalJD > 0 ? (matchedCount / totalJD * 100) : 0.0;

      // Get CV total from match summary categories (Python-inspired)
      final categories = matchSummary['categories'] ?? {};
      final categoryKey = category == 'technical_skills'
          ? 'technical'
          : category == 'soft_skills'
              ? 'soft'
              : 'domain';
      final categoryData = categories[categoryKey] ?? {};
      final cvTotal = categoryData['cv_total'] ?? matchedCount;

      tableData.add({
        'category': categoryName,
        'cvTotal': cvTotal,
        'jdTotal': totalJD,
        'matched': matchedCount,
        'missing': missingCount,
        'matchRate': matchRate,
      });
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.neutralGray200),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '📊 SUMMARY TABLE',
            style: AppTheme.bodyLarge.copyWith(
              fontWeight: FontWeight.bold,
              color: AppTheme.primaryCosmic,
            ),
          ),
          const SizedBox(height: 16),

          // Table Header
          Container(
            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
            decoration: BoxDecoration(
              color: AppTheme.primaryCosmic.withOpacity(0.1),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(8),
                topRight: Radius.circular(8),
              ),
            ),
            child: Row(
              children: [
                Expanded(flex: 3, child: _buildTableHeaderCell('Category')),
                Expanded(flex: 2, child: _buildTableHeaderCell('CV Total')),
                Expanded(flex: 2, child: _buildTableHeaderCell('JD Total')),
                Expanded(flex: 2, child: _buildTableHeaderCell('Matched')),
                Expanded(flex: 2, child: _buildTableHeaderCell('Missing')),
                Expanded(
                    flex: 2, child: _buildTableHeaderCell('Match Rate (%)')),
              ],
            ),
          ),

          // Table Rows
          ...tableData.asMap().entries.map((entry) {
            final index = entry.key;
            final row = entry.value;

            return Container(
              padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
              decoration: BoxDecoration(
                color: index % 2 == 0 ? Colors.grey.shade50 : Colors.white,
                border: Border(
                  bottom: BorderSide(
                    color: AppTheme.neutralGray200,
                    width: 0.5,
                  ),
                ),
              ),
              child: Row(
                children: [
                  Expanded(
                      flex: 3,
                      child:
                          _buildTableCell(row['category'], isCategory: true)),
                  Expanded(
                      flex: 2,
                      child: _buildTableCell(row['cvTotal'].toString())),
                  Expanded(
                      flex: 2,
                      child: _buildTableCell(row['jdTotal'].toString())),
                  Expanded(
                      flex: 2,
                      child: _buildTableCell(row['matched'].toString(),
                          color: Colors.green.shade700)),
                  Expanded(
                      flex: 2,
                      child: _buildTableCell(row['missing'].toString(),
                          color: row['missing'] > 0
                              ? Colors.red.shade700
                              : AppTheme.neutralGray600)),
                  Expanded(
                      flex: 2,
                      child: _buildTableCell(
                          '${row['matchRate'].toStringAsFixed(1)}%',
                          color: _getMatchRateColor(row['matchRate']))),
                ],
              ),
            );
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildTableHeaderCell(String text) {
    return Text(
      text,
      style: AppTheme.bodySmall.copyWith(
        fontWeight: FontWeight.bold,
        color: AppTheme.primaryCosmic,
      ),
      textAlign: TextAlign.center,
    );
  }

  Widget _buildTableCell(String text, {Color? color, bool isCategory = false}) {
    return Text(
      text,
      style: AppTheme.bodySmall.copyWith(
        color: color ?? AppTheme.neutralGray700,
        fontWeight: isCategory ? FontWeight.w600 : FontWeight.normal,
      ),
      textAlign: isCategory ? TextAlign.left : TextAlign.center,
    );
  }

  Color _getMatchRateColor(double matchRate) {
    if (matchRate >= 90) return Colors.green.shade700;
    if (matchRate >= 70) return Colors.orange.shade700;
    return Colors.red.shade700;
  }
}
