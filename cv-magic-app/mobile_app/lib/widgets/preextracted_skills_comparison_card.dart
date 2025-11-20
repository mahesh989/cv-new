import 'package:flutter/material.dart';
import '../models/preextracted_comparison.dart';

/// Preextracted Skills Comparison Card - Displays CV-JD skills comparison in table format
/// Shows skills breakdown by category (Technical, Soft, Domain) with match statistics
class PreextractedSkillsComparisonCard extends StatelessWidget {
  final PreextractedComparisonResult data;
  final String? companyName;

  const PreextractedSkillsComparisonCard({
    super.key,
    required this.data,
    this.companyName,
  });

  @override
  Widget build(BuildContext context) {
    // Check if we have valid data
    if (data.categories.isEmpty) {
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
              Colors.blue.shade50,
              Colors.blue.shade100,
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
                      color: Colors.blue.shade700,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(
                      Icons.table_chart,
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
                          'Skills Comparison',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.blue.shade900,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          'CV vs JD Skills Analysis',
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.blue.shade700,
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
                          color: Colors.blue.shade300,
                          width: 2,
                        ),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.business,
                            size: 16,
                            color: Colors.blue.shade700,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            companyName!,
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: Colors.blue.shade800,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
              const SizedBox(height: 20),

              // Overall Summary Statistics
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.blue.shade200, width: 2),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildOverallStat(
                      'Total Requirements',
                      data.overall.totalRequirements,
                      Colors.blue,
                    ),
                    _buildOverallStat(
                      'Matched',
                      data.overall.matched,
                      Colors.green,
                    ),
                    _buildOverallStat(
                      'Missing',
                      data.overall.missing,
                      Colors.red,
                    ),
                    _buildOverallStat(
                      'Match Rate',
                      data.overall.matchRatePercent.round(),
                      Colors.orange,
                      isPercent: true,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Summary Table
              _buildComparisonTable(context),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildOverallStat(String label, int value, MaterialColor color, {bool isPercent = false}) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: color.shade800,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 6),
        Text(
          isPercent ? '$value%' : value.toString(),
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color.shade700,
          ),
        ),
      ],
    );
  }

  Widget _buildComparisonTable(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue.shade200, width: 2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Table Header
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.blue.shade100,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(10),
                topRight: Radius.circular(10),
              ),
            ),
            child: Text(
              '📊 Summary Table',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.blue.shade900,
              ),
            ),
          ),

          // Table Content
          Padding(
            padding: const EdgeInsets.all(12),
            child: Table(
              columnWidths: const {
                0: FlexColumnWidth(2.5), // Category
                1: FlexColumnWidth(1.2), // CV Total
                2: FlexColumnWidth(1.2), // JD Total
                3: FlexColumnWidth(1.2), // Matched
                4: FlexColumnWidth(1.2), // Missing
                5: FlexColumnWidth(1.5), // Match Rate
              },
              defaultVerticalAlignment: TableCellVerticalAlignment.middle,
              border: TableBorder(
                horizontalInside: BorderSide(
                  color: Colors.grey.shade300,
                  width: 1,
                ),
              ),
              children: [
                // Header Row
                TableRow(
                  decoration: BoxDecoration(
                    color: Colors.blue.shade50,
                  ),
                  children: [
                    _buildTableHeaderCell('Category'),
                    _buildTableHeaderCell('CV Total'),
                    _buildTableHeaderCell('JD Total'),
                    _buildTableHeaderCell('Matched'),
                    _buildTableHeaderCell('Missing'),
                    _buildTableHeaderCell('Match Rate (%)'),
                  ],
                ),
                // Data Rows
                for (final category in data.categories)
                  TableRow(
                    children: [
                      _buildTableCell(
                        category.name,
                        fontWeight: FontWeight.w600,
                        color: _getCategoryColor(category.name),
                      ),
                      _buildTableCell(category.cvTotal.toString()),
                      _buildTableCell(category.jdTotal.toString()),
                      _buildTableCell(
                        category.matched.toString(),
                        color: Colors.green.shade700,
                        fontWeight: FontWeight.w600,
                      ),
                      _buildTableCell(
                        category.missing.toString(),
                        color: Colors.red.shade700,
                        fontWeight: FontWeight.w600,
                      ),
                      _buildTableCell(
                        '${category.matchRatePercent.toStringAsFixed(1)}%',
                        color: _getMatchRateColor(category.matchRatePercent),
                        fontWeight: FontWeight.w600,
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

  Widget _buildTableHeaderCell(String text) {
    return Padding(
      padding: const EdgeInsets.all(10),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.bold,
          color: Colors.blue.shade900,
        ),
      ),
    );
  }

  Widget _buildTableCell(
    String text, {
    Color? color,
    FontWeight? fontWeight,
  }) {
    return Padding(
      padding: const EdgeInsets.all(10),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 12,
          color: color ?? Colors.grey.shade800,
          fontWeight: fontWeight ?? FontWeight.normal,
        ),
      ),
    );
  }

  Color _getCategoryColor(String categoryName) {
    final name = categoryName.toLowerCase();
    if (name.contains('technical')) {
      return Colors.purple.shade700;
    } else if (name.contains('soft')) {
      return Colors.orange.shade700;
    } else if (name.contains('domain')) {
      return Colors.teal.shade700;
    }
    return Colors.grey.shade800;
  }

  Color _getMatchRateColor(double matchRate) {
    if (matchRate >= 70) {
      return Colors.green.shade700;
    } else if (matchRate >= 40) {
      return Colors.orange.shade700;
    } else {
      return Colors.red.shade700;
    }
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
                Icon(Icons.table_chart, color: Colors.grey.shade400),
                const SizedBox(width: 8),
                Text(
                  'Skills Comparison',
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
              'No skills comparison data available',
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

