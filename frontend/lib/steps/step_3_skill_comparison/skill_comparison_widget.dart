import 'package:flutter/material.dart';
import '../base/analysis_step_widget.dart';
import 'skill_comparison_controller.dart';

/// Widget for displaying Step 3: Skill Comparison results
class SkillComparisonWidget extends AnalysisStepWidget {
  const SkillComparisonWidget({
    super.key,
    required SkillComparisonController controller,
    super.showHeader = true,
    super.showProgress = true,
    super.showErrors = true,
  }) : super(controller: controller);

  @override
  Widget buildStepContent(BuildContext context) {
    final comparisonController = controller as SkillComparisonController;

    return Container(
      decoration: BoxDecoration(
        color: Colors.purple[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.purple[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // AI-Powered Skills Analysis Header
          _buildAnalysisHeader(),
          const SizedBox(height: 16),

          // Overall Summary Section
          _buildOverallSummary(comparisonController),
          const SizedBox(height: 16),

          // Summary Table Section
          _buildSummaryTable(comparisonController),
          const SizedBox(height: 16),

          // Detailed AI Analysis Section
          _buildDetailedAIAnalysis(comparisonController),
        ],
      ),
    );
  }

  /// Build AI-Powered Skills Analysis header
  Widget _buildAnalysisHeader() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.purple[100],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.purple[300]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.psychology, color: Colors.purple[700], size: 24),
              const SizedBox(width: 8),
              Text(
                '🤖 AI-POWERED SKILLS ANALYSIS',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.purple[700],
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Enhanced semantic matching with detailed reasoning',
            style: TextStyle(
              fontSize: 14,
              color: Colors.purple[600],
              fontStyle: FontStyle.italic,
            ),
          ),
        ],
      ),
    );
  }

  /// Build overall summary section
  Widget _buildOverallSummary(SkillComparisonController controller) {
    final matchPercentage = controller.matchPercentage ?? 0.0;
    final matchedTechnical = controller.matchedTechnicalSkills?.length ?? 0;
    final matchedSoft = controller.matchedSoftSkills?.length ?? 0;
    final matchedDomain = controller.matchedDomainKeywords?.length ?? 0;
    final missingTechnical = controller.missingTechnicalSkills?.length ?? 0;
    final missingSoft = controller.missingSoftSkills?.length ?? 0;
    final missingDomain = controller.missingDomainKeywords?.length ?? 0;

    final totalMatched = matchedTechnical + matchedSoft + matchedDomain;
    final totalMissing = missingTechnical + missingSoft + missingDomain;
    final totalRequirements = totalMatched + totalMissing;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.analytics, color: Colors.blue[700], size: 20),
              const SizedBox(width: 8),
              Text(
                '🎯 OVERALL SUMMARY',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.blue[700],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: Colors.blue[200]!),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Total Requirements: $totalRequirements',
                  style: const TextStyle(
                      fontSize: 14, fontWeight: FontWeight.w600),
                ),
                Text(
                  'Matched: $totalMatched',
                  style: const TextStyle(
                      fontSize: 14, fontWeight: FontWeight.w600),
                ),
                Text(
                  'Missing: $totalMissing',
                  style: const TextStyle(
                      fontSize: 14, fontWeight: FontWeight.w600),
                ),
                Text(
                  'Match Rate: ${_formatPercentage(matchPercentage)}%',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.green[700],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Build detailed AI analysis section
  Widget _buildDetailedAIAnalysis(SkillComparisonController controller) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.orange[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.orange[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.psychology, color: Colors.orange[700], size: 20),
              const SizedBox(width: 8),
              Text(
                '🧠 DETAILED AI ANALYSIS',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.orange[700],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Technical Skills Analysis
          if (controller.detailedMatchedTechnicalSkills != null ||
              controller.missingTechnicalSkills != null) ...[
            _buildCategoryAnalysis(
              '🔹 TECHNICAL SKILLS',
              controller.detailedMatchedTechnicalSkills ?? [],
              controller.missingTechnicalSkills ?? [],
              Colors.blue,
            ),
            const SizedBox(height: 16),
          ],

          // Soft Skills Analysis
          if (controller.detailedMatchedSoftSkills != null ||
              controller.missingSoftSkills != null) ...[
            _buildCategoryAnalysis(
              '🔹 SOFT SKILLS',
              controller.detailedMatchedSoftSkills ?? [],
              controller.missingSoftSkills ?? [],
              Colors.green,
            ),
            const SizedBox(height: 16),
          ],

          // Domain Keywords Analysis
          if (controller.detailedMatchedDomainKeywords != null ||
              controller.missingDomainKeywords != null) ...[
            _buildCategoryAnalysis(
              '🔹 DOMAIN KEYWORDS',
              controller.detailedMatchedDomainKeywords ?? [],
              controller.missingDomainKeywords ?? [],
              Colors.orange,
            ),
          ],
        ],
      ),
    );
  }

  /// Build category analysis
  Widget _buildCategoryAnalysis(
    String categoryTitle,
    List<Map<String, dynamic>> matchedSkills,
    List<String> missingSkills,
    MaterialColor color,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          categoryTitle,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: color[700],
          ),
        ),
        const SizedBox(height: 8),

        // Matched skills
        if (matchedSkills.isNotEmpty) ...[
          Text(
            '  ✅ MATCHED JD REQUIREMENTS (${matchedSkills.length} items):',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: Colors.green[700],
            ),
          ),
          const SizedBox(height: 4),
          ...matchedSkills.asMap().entries.map((entry) {
            final index = entry.key + 1;
            final skill = entry.value;
            return Padding(
              padding: const EdgeInsets.only(left: 16, bottom: 4),
              child: Text(
                '    $index. JD Required: \'${skill['jd_skill'] ?? skill['jd_requirement'] ?? ''}\'\n'
                '       → Found in CV: \'${skill['cv_skill'] ?? skill['cv_equivalent'] ?? ''}\'\n'
                '       💡 ${skill['reasoning'] ?? skill['explanation'] ?? ''}',
                style: const TextStyle(fontSize: 11, height: 1.3),
              ),
            );
          }).toList(),
          const SizedBox(height: 8),
        ],

        // Missing skills
        if (missingSkills.isNotEmpty) ...[
          Text(
            '  ❌ MISSING FROM CV (${missingSkills.length} items):',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: Colors.red[700],
            ),
          ),
          const SizedBox(height: 4),
          ...missingSkills.asMap().entries.map((entry) {
            final index = entry.key + 1;
            final skill = entry.value;
            return Padding(
              padding: const EdgeInsets.only(left: 16, bottom: 4),
              child: Text(
                '    $index. JD Requires: \'$skill\'\n'
                '       💡 No matching skill found in CV',
                style: const TextStyle(fontSize: 11, height: 1.3),
              ),
            );
          }).toList(),
        ],
      ],
    );
  }

  /// Build the match summary section
  Widget _buildMatchSummarySection(SkillComparisonController controller) {
    final matchPercentage = controller.matchPercentage ?? 0.0;
    final summary = controller.comparisonSummary ?? '';

    return buildResultContainer(
      title: '📊 Match Summary',
      color: Colors.green,
      icon: Icons.analytics,
      content: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Match percentage
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Overall Match',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: Colors.green[700],
                      ),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Text(
                          '${_formatPercentage(matchPercentage)}%',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Colors.green[700],
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: LinearProgressIndicator(
                            value: _normalizePercentage(matchPercentage),
                            backgroundColor: Colors.green[100],
                            valueColor: AlwaysStoppedAnimation<Color>(
                              Colors.green[700]!,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),

          // Summary text
          if (summary.isNotEmpty) ...[
            const SizedBox(height: 12),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.green[50],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.green[200]!),
              ),
              child: Text(
                summary,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.green[800],
                  height: 1.5,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  /// Build the matched skills section
  Widget _buildMatchedSkillsSection(SkillComparisonController controller) {
    return buildResultContainer(
      title: '✅ Matched Skills',
      color: Colors.green,
      icon: Icons.check_circle,
      content: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Matched Technical Skills
          if (controller.matchedTechnicalSkills != null &&
              controller.matchedTechnicalSkills!.isNotEmpty) ...[
            _buildSkillCategory(
              'Technical Skills',
              controller.matchedTechnicalSkills!,
              Colors.green,
            ),
            const SizedBox(height: 12),
          ],

          // Matched Soft Skills
          if (controller.matchedSoftSkills != null &&
              controller.matchedSoftSkills!.isNotEmpty) ...[
            _buildSkillCategory(
              'Soft Skills',
              controller.matchedSoftSkills!,
              Colors.green,
            ),
            const SizedBox(height: 12),
          ],

          // Matched Domain Keywords
          if (controller.matchedDomainKeywords != null &&
              controller.matchedDomainKeywords!.isNotEmpty) ...[
            _buildSkillCategory(
              'Domain Keywords',
              controller.matchedDomainKeywords!,
              Colors.green,
            ),
          ],
        ],
      ),
    );
  }

  /// Build the missing skills section
  Widget _buildMissingSkillsSection(SkillComparisonController controller) {
    return buildResultContainer(
      title: '❌ Missing Skills',
      color: Colors.orange,
      icon: Icons.warning,
      content: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Missing Technical Skills
          if (controller.missingTechnicalSkills != null &&
              controller.missingTechnicalSkills!.isNotEmpty) ...[
            _buildSkillCategory(
              'Technical Skills',
              controller.missingTechnicalSkills!,
              Colors.orange,
            ),
            const SizedBox(height: 12),
          ],

          // Missing Soft Skills
          if (controller.missingSoftSkills != null &&
              controller.missingSoftSkills!.isNotEmpty) ...[
            _buildSkillCategory(
              'Soft Skills',
              controller.missingSoftSkills!,
              Colors.orange,
            ),
            const SizedBox(height: 12),
          ],

          // Missing Domain Keywords
          if (controller.missingDomainKeywords != null &&
              controller.missingDomainKeywords!.isNotEmpty) ...[
            _buildSkillCategory(
              'Domain Keywords',
              controller.missingDomainKeywords!,
              Colors.orange,
            ),
          ],
        ],
      ),
    );
  }

  /// Build a skill category with skills list
  Widget _buildSkillCategory(String title, List<String> skills, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '$title (${skills.length})',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 4,
          children: skills.map((skill) {
            return Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: color.withOpacity(0.3)),
              ),
              child: Text(
                skill,
                style: TextStyle(
                  fontSize: 12,
                  color: color,
                  fontWeight: FontWeight.w500,
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  /// Format percentage correctly (handle both decimal and percentage values)
  String _formatPercentage(double? percentage) {
    if (percentage == null) return '0.0';

    // If the value is already a percentage (>= 1), return as is
    if (percentage >= 1.0) {
      return percentage.toStringAsFixed(1);
    }

    // If it's a decimal (0-1), convert to percentage
    return (percentage * 100).toStringAsFixed(1);
  }

  /// Normalize percentage to 0-1 range for progress bar
  double _normalizePercentage(double? percentage) {
    if (percentage == null) return 0.0;

    // If the value is already a percentage (>= 1), convert to decimal
    if (percentage >= 1.0) {
      return (percentage / 100).clamp(0.0, 1.0);
    }

    // If it's already a decimal (0-1), return as is
    return percentage.clamp(0.0, 1.0);
  }

  /// Build summary table section
  Widget _buildSummaryTable(SkillComparisonController controller) {
    return buildResultContainer(
      title: '📊 Summary Table',
      color: Colors.indigo,
      icon: Icons.table_chart,
      content: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Table header
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.indigo.shade50,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.indigo.shade200),
            ),
            child: Row(
              children: [
                Expanded(flex: 3, child: _buildTableHeader('Category')),
                Expanded(flex: 2, child: _buildTableHeader('CV Total')),
                Expanded(flex: 2, child: _buildTableHeader('JD Total')),
                Expanded(flex: 2, child: _buildTableHeader('Matched')),
                Expanded(flex: 2, child: _buildTableHeader('Missing')),
                Expanded(flex: 2, child: _buildTableHeader('Match Rate (%)')),
              ],
            ),
          ),
          const SizedBox(height: 8),

          // Technical Skills row
          _buildTableRow(
            'Technical Skills',
            controller.cvTechnicalSkills?.length ?? 0,
            controller.jdTechnicalSkills?.length ?? 0,
            controller.matchedTechnicalSkills?.length ?? 0,
            controller.missingTechnicalSkills?.length ?? 0,
            Colors.blue,
          ),

          // Soft Skills row
          _buildTableRow(
            'Soft Skills',
            controller.cvSoftSkills?.length ?? 0,
            controller.jdSoftSkills?.length ?? 0,
            controller.matchedSoftSkills?.length ?? 0,
            controller.missingSoftSkills?.length ?? 0,
            Colors.green,
          ),

          // Domain Keywords row
          _buildTableRow(
            'Domain Keywords',
            controller.domainKeywords?.length ?? 0,
            controller.jdDomainKeywords?.length ?? 0,
            controller.matchedDomainKeywords?.length ?? 0,
            controller.missingDomainKeywords?.length ?? 0,
            Colors.orange,
          ),
        ],
      ),
    );
  }

  /// Build table header
  Widget _buildTableHeader(String text) {
    return Text(
      text,
      style: const TextStyle(
        fontSize: 12,
        fontWeight: FontWeight.bold,
        color: Colors.indigo,
      ),
      textAlign: TextAlign.center,
    );
  }

  /// Build table row
  Widget _buildTableRow(
    String category,
    int cvTotal,
    int jdTotal,
    int matched,
    int missing,
    MaterialColor color,
  ) {
    final matchRate = jdTotal > 0 ? (matched / jdTotal * 100) : 0.0;

    return Container(
      margin: const EdgeInsets.only(bottom: 4),
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: color.shade50,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.shade200),
      ),
      child: Row(
        children: [
          Expanded(flex: 3, child: _buildTableCell(category, color)),
          Expanded(flex: 2, child: _buildTableCell(cvTotal.toString(), color)),
          Expanded(flex: 2, child: _buildTableCell(jdTotal.toString(), color)),
          Expanded(flex: 2, child: _buildTableCell(matched.toString(), color)),
          Expanded(flex: 2, child: _buildTableCell(missing.toString(), color)),
          Expanded(
              flex: 2,
              child: _buildTableCell('${matchRate.toStringAsFixed(1)}', color)),
        ],
      ),
    );
  }

  /// Build table cell
  Widget _buildTableCell(String text, MaterialColor color) {
    return Text(
      text,
      style: TextStyle(
        fontSize: 11,
        fontWeight: FontWeight.w500,
        color: color.shade700,
      ),
      textAlign: TextAlign.center,
    );
  }

  /// Build enhanced detailed analysis section
  Widget _buildEnhancedDetailedAnalysis(SkillComparisonController controller) {
    return buildResultContainer(
      title: '🧠 Detailed AI Analysis',
      color: Colors.purple,
      icon: Icons.psychology,
      content: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Enhanced semantic matching with detailed reasoning',
            style: TextStyle(
              fontSize: 12,
              color: Colors.purple[600],
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(height: 16),

          // Technical Skills Analysis
          if (controller.detailedMatchedTechnicalSkills != null ||
              controller.missingTechnicalSkills != null) ...[
            _buildCategoryDetailedAnalysis(
              '🔧 Technical Skills',
              controller.detailedMatchedTechnicalSkills ?? [],
              controller.missingTechnicalSkills ?? [],
              Colors.blue,
            ),
            const SizedBox(height: 16),
          ],

          // Soft Skills Analysis
          if (controller.detailedMatchedSoftSkills != null ||
              controller.missingSoftSkills != null) ...[
            _buildCategoryDetailedAnalysis(
              '🤝 Soft Skills',
              controller.detailedMatchedSoftSkills ?? [],
              controller.missingSoftSkills ?? [],
              Colors.green,
            ),
            const SizedBox(height: 16),
          ],

          // Domain Keywords Analysis
          if (controller.detailedMatchedDomainKeywords != null ||
              controller.missingDomainKeywords != null) ...[
            _buildCategoryDetailedAnalysis(
              '🎯 Domain Keywords',
              controller.detailedMatchedDomainKeywords ?? [],
              controller.missingDomainKeywords ?? [],
              Colors.orange,
            ),
          ],
        ],
      ),
    );
  }

  /// Build detailed analysis for a category
  Widget _buildCategoryDetailedAnalysis(
    String categoryName,
    List<Map<String, dynamic>> matchedSkills,
    List<String> missingSkills,
    MaterialColor color,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            categoryName.toUpperCase(),
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: color.shade700,
            ),
          ),
          const Divider(height: 16),

          // Matched skills with reasoning
          if (matchedSkills.isNotEmpty) ...[
            Text(
              '✅ MATCHED JD REQUIREMENTS (${matchedSkills.length} items):',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: Colors.green.shade700,
              ),
            ),
            const SizedBox(height: 8),
            ...matchedSkills.asMap().entries.map((entry) {
              final index = entry.key;
              final skill = entry.value;
              return _buildMatchedSkillItem(index + 1, skill, color);
            }).toList(),
            const SizedBox(height: 12),
          ],

          // Missing skills
          if (missingSkills.isNotEmpty) ...[
            Text(
              '❌ MISSING FROM CV (${missingSkills.length} items):',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: Colors.red.shade700,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              '(JD requirements NOT covered by your CV)',
              style: TextStyle(
                fontSize: 10,
                color: Colors.red.shade600,
                fontStyle: FontStyle.italic,
              ),
            ),
            const SizedBox(height: 8),
            ...missingSkills.asMap().entries.map((entry) {
              final index = entry.key;
              final skill = entry.value;
              return _buildMissingSkillItem(index + 1, skill, color);
            }).toList(),
          ],
        ],
      ),
    );
  }

  /// Build matched skill item with reasoning
  Widget _buildMatchedSkillItem(
      int index, Map<String, dynamic> skill, MaterialColor color) {
    final jdSkill = skill['jd_skill'] ?? skill['jd_requirement'] ?? '';
    final cvSkill = skill['cv_skill'] ?? skill['cv_equivalent'] ?? '';
    final reasoning =
        skill['match_reason'] ?? skill['reasoning'] ?? 'AI semantic match';

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: Colors.green.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '$index. JD Required: \'$jdSkill\'',
            style: const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            '→ Found in CV: \'$cvSkill\'',
            style: TextStyle(
              fontSize: 11,
              color: Colors.green.shade700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            '💡 $reasoning',
            style: TextStyle(
              fontSize: 10,
              color: Colors.green.shade600,
              fontStyle: FontStyle.italic,
            ),
          ),
        ],
      ),
    );
  }

  /// Build missing skill item
  Widget _buildMissingSkillItem(int index, String skill, MaterialColor color) {
    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '$index. JD Requires: \'$skill\'',
            style: const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            '💡 Not found in CV',
            style: TextStyle(
              fontSize: 10,
              color: Colors.red.shade600,
              fontStyle: FontStyle.italic,
            ),
          ),
        ],
      ),
    );
  }

  /// Build side-by-side comparison section
  Widget _buildSideBySideComparison(SkillComparisonController controller) {
    return buildResultContainer(
      title: '📊 Detailed Comparison',
      color: Colors.blue,
      icon: Icons.compare_arrows,
      content: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Matched Skills Column
              Expanded(
                child: _buildComparisonColumn(
                  '✅ Matched Skills',
                  {
                    'Technical Skills': controller.matchedTechnicalSkills ?? [],
                    'Soft Skills': controller.matchedSoftSkills ?? [],
                    'Domain Keywords': controller.matchedDomainKeywords ?? [],
                  },
                  Colors.green,
                ),
              ),
              const SizedBox(width: 16),
              // Missing Skills Column
              Expanded(
                child: _buildComparisonColumn(
                  '❌ Missing Skills',
                  {
                    'Technical Skills': controller.missingTechnicalSkills ?? [],
                    'Soft Skills': controller.missingSoftSkills ?? [],
                    'Domain Keywords': controller.missingDomainKeywords ?? [],
                  },
                  Colors.orange,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// Build comparison column
  Widget _buildComparisonColumn(
    String title,
    Map<String, List<String>> skills,
    MaterialColor baseColor,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: baseColor.shade50,
            borderRadius: BorderRadius.circular(6),
            border: Border.all(color: baseColor.shade200),
          ),
          child: Text(
            title,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: baseColor.shade700,
            ),
            textAlign: TextAlign.center,
          ),
        ),
        const SizedBox(height: 12),
        ...skills.entries.map((entry) {
          if (entry.value.isEmpty) return const SizedBox.shrink();
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '${entry.key} (${entry.value.length})',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: baseColor.shade700,
                ),
              ),
              const SizedBox(height: 6),
              Wrap(
                spacing: 4,
                runSpacing: 4,
                children: entry.value
                    .map((skill) => Chip(
                          label: Text(
                            skill,
                            style: const TextStyle(fontSize: 10),
                          ),
                          backgroundColor: baseColor.shade100,
                          side: BorderSide(color: baseColor.shade300),
                          padding: const EdgeInsets.symmetric(
                              horizontal: 6, vertical: 2),
                        ))
                    .toList(),
              ),
              const SizedBox(height: 8),
            ],
          );
        }).toList(),
      ],
    );
  }
}
