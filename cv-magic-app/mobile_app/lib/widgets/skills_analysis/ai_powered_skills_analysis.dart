import 'package:flutter/material.dart';

import '../../models/preextracted_comparison.dart';

class AIPoweredSkillsAnalysis extends StatelessWidget {
  final PreextractedComparisonResult data;
  const AIPoweredSkillsAnalysis({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _header(),
        const SizedBox(height: 12),
        _overallSummary(context),
        const SizedBox(height: 12),
        _summaryTable(context),
      ],
    );
  }

  Widget _header() {
    return Text(
      '🤖 AI-POWERED SKILLS ANALYSIS',
      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
    );
  }

  Widget _overallSummary(BuildContext context) {
    final o = data.overall;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('🎯 OVERALL SUMMARY'),
        const Divider(),
        Text('Total Requirements: ${o.totalRequirements}'),
        Text('Matched: ${o.matched}'),
        Text('Missing: ${o.missing}'),
        Text('Match Rate: ${o.matchRatePercent.toStringAsFixed(1)}%'),
      ],
    );
  }

  Widget _summaryTable(BuildContext context) {
    final headerStyle = Theme.of(context)
        .textTheme
        .bodySmall
        ?.copyWith(fontWeight: FontWeight.w600);
    final rows = data.categories;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('📊 SUMMARY TABLE'),
        const Divider(),
        Container(
          decoration: BoxDecoration(
            border: Border.all(color: Theme.of(context).dividerColor),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Table(
            columnWidths: const {
              0: FlexColumnWidth(2),
              1: FlexColumnWidth(),
              2: FlexColumnWidth(),
              3: FlexColumnWidth(),
              4: FlexColumnWidth(),
              5: FlexColumnWidth(),
            },
            defaultVerticalAlignment: TableCellVerticalAlignment.middle,
            children: [
              TableRow(
                decoration: BoxDecoration(
                    color: Theme.of(context)
                        .colorScheme
                        .surfaceVariant
                        .withOpacity(0.4)),
                children: [
                  Padding(
                      padding: const EdgeInsets.all(8),
                      child: Text('Category', style: headerStyle)),
                  Padding(
                      padding: const EdgeInsets.all(8),
                      child: Text('CV Total', style: headerStyle)),
                  Padding(
                      padding: const EdgeInsets.all(8),
                      child: Text('JD Total', style: headerStyle)),
                  Padding(
                      padding: const EdgeInsets.all(8),
                      child: Text('Matched', style: headerStyle)),
                  Padding(
                      padding: const EdgeInsets.all(8),
                      child: Text('Missing', style: headerStyle)),
                  Padding(
                      padding: const EdgeInsets.all(8),
                      child: Text('Match Rate (%)', style: headerStyle)),
                ],
              ),
              for (final r in rows)
                TableRow(children: [
                  Padding(
                      padding: const EdgeInsets.all(8), child: Text(r.name)),
                  Padding(
                      padding: const EdgeInsets.all(8),
                      child: Text(r.cvTotal == 0 ? '-' : r.cvTotal.toString())),
                  Padding(
                      padding: const EdgeInsets.all(8),
                      child: Text(r.jdTotal.toString())),
                  Padding(
                      padding: const EdgeInsets.all(8),
                      child: Text(r.matched.toString())),
                  Padding(
                      padding: const EdgeInsets.all(8),
                      child: Text(r.missing.toString())),
                  Padding(
                      padding: const EdgeInsets.all(8),
                      child: Text(r.matchRatePercent.toStringAsFixed(1))),
                ]),
            ],
          ),
        ),
      ],
    );
  }

  // Detailed AI analysis (matched/missing lists) intentionally removed per requirements.
}
