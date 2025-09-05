import 'package:flutter/material.dart';
import '../../services/api_service.dart' as api;
import '../../services/ats_service.dart' as ats;
import '../../theme/app_theme.dart';

class ATSResultWidget extends StatelessWidget {
  final ats.ATSResult atsResult;

  const ATSResultWidget({
    super.key,
    required this.atsResult,
  });

  @override
  Widget build(BuildContext context) {
    // Debug print all received skills
    debugPrint(
        '🟦 [ATSResultWidget] Matched Technical Skills: ${atsResult.matchedHardSkills}');
    debugPrint(
        '🟦 [ATSResultWidget] Matched Soft Skills: ${atsResult.matchedSoftSkills}');
    debugPrint(
        '🟦 [ATSResultWidget] Matched Domain Keywords: ${atsResult.matchedDomainKeywords}');
    debugPrint(
        '🟥 [ATSResultWidget] Missing Technical Skills: ${atsResult.missedHardSkills}');
    debugPrint(
        '🟥 [ATSResultWidget] Missing Soft Skills: ${atsResult.missedSoftSkills}');
    debugPrint(
        '🟥 [ATSResultWidget] Missing Domain Keywords: ${atsResult.missedDomainKeywords}');
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('📊 Overall Score: ${atsResult.overallScore}/100',
            style:
                AppTheme.headingSmall.copyWith(color: AppTheme.primaryCosmic)),
        const SizedBox(height: 12),
        Text('✅ Keyword Match: ${atsResult.keywordMatch}%',
            style: AppTheme.bodyMedium),
        Text('✅ Skills Match: ${atsResult.skillsMatch}%',
            style: AppTheme.bodyMedium),
        const SizedBox(height: 16),
        if (atsResult.matchedHardSkills.isNotEmpty) ...[
          Text('🟩 Matched Technical Skills:',
              style: AppTheme.bodyLarge.copyWith(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          _buildChipWrap(atsResult.matchedHardSkills, Colors.blue.shade100),
          const SizedBox(height: 12),
        ],
        if (atsResult.matchedSoftSkills.isNotEmpty) ...[
          Text('🟩 Matched Soft Skills:',
              style: AppTheme.bodyLarge.copyWith(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          _buildChipWrap(atsResult.matchedSoftSkills, Colors.purple.shade100),
          const SizedBox(height: 12),
        ],
        if (atsResult.matchedDomainKeywords.isNotEmpty) ...[
          Text('🟩 Matched Domain Keywords:',
              style: AppTheme.bodyLarge.copyWith(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          _buildChipWrap(
              atsResult.matchedDomainKeywords, Colors.orange.shade100),
          const SizedBox(height: 12),
        ],
        if (atsResult.missedHardSkills.isNotEmpty) ...[
          Text('🟥 Missing Technical Skills:',
              style: AppTheme.bodyLarge.copyWith(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          _buildChipWrap(atsResult.missedHardSkills, Colors.blue.shade100),
          const SizedBox(height: 12),
        ],
        if (atsResult.missedSoftSkills.isNotEmpty) ...[
          Text('🟥 Missing Soft Skills:',
              style: AppTheme.bodyLarge.copyWith(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          _buildChipWrap(atsResult.missedSoftSkills, Colors.purple.shade100),
          const SizedBox(height: 12),
        ],
        if (atsResult.missedDomainKeywords.isNotEmpty) ...[
          Text('🟥 Missing Domain Keywords:',
              style: AppTheme.bodyLarge.copyWith(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          _buildChipWrap(
              atsResult.missedDomainKeywords, Colors.orange.shade100),
          const SizedBox(height: 12),
        ],
        if (atsResult.tips.isNotEmpty) ...[
          const SizedBox(height: 16),
          Text('💡 Improvement Tips:',
              style: AppTheme.bodyLarge.copyWith(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppTheme.primaryTeal.withOpacity(0.05),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: AppTheme.primaryTeal.withOpacity(0.2),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: atsResult.tips
                  .map((tip) => Padding(
                        padding: const EdgeInsets.only(bottom: 6),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '• ',
                              style: AppTheme.bodySmall.copyWith(
                                color: AppTheme.primaryTeal,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Expanded(
                              child: Text(
                                tip,
                                style: AppTheme.bodySmall.copyWith(
                                  color: AppTheme.neutralGray700,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ))
                  .toList(),
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildChipWrap(List<String> items, Color color) => items.isEmpty
      ? Text('None found.', style: AppTheme.bodySmall)
      : Wrap(
          spacing: 6,
          runSpacing: 6,
          children: items
              .map((e) => Chip(
                    label: Text(e, style: AppTheme.bodySmall),
                    backgroundColor: color,
                  ))
              .toList(),
        );
}
