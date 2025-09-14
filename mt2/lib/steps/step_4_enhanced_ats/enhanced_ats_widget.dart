import 'package:flutter/material.dart';
import '../base/analysis_step_widget.dart';
import 'enhanced_ats_controller.dart';

/// Widget for displaying Step 4: Enhanced ATS Score results
class EnhancedATSWidget extends AnalysisStepWidget {
  const EnhancedATSWidget({
    super.key,
    required EnhancedATSController controller,
    super.showHeader = true,
    super.showProgress = true,
    super.showErrors = true,
  }) : super(controller: controller);

  @override
  Widget buildStepContent(BuildContext context) {
    final atsController = controller as EnhancedATSController;
    final atsResults = atsController.result?.data ?? {};

    // Debug logging
    debugPrint('🔍 [ENHANCED_ATS_WIDGET] Building widget...');
    debugPrint('   Overall Score: ${atsController.overallScore}');
    debugPrint('   Score Category: ${atsController.scoreCategory}');
    debugPrint(
        '   Detailed Breakdown: ${atsController.detailedBreakdown != null ? 'Available' : 'Not Available'}');
    debugPrint('   ATS Results Keys: ${atsResults.keys.toList()}');
    debugPrint('   Is Showing Countdown: ${atsController.isShowingCountdown}');
    debugPrint('   Countdown Seconds: ${atsController.countdownSeconds}');
    debugPrint('   Is Processing: ${atsController.isProcessing}');

    return Container(
      decoration: BoxDecoration(
        color: Colors.indigo[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.indigo[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          _buildHeader(),
          const SizedBox(height: 20),

          // Countdown Display (10-second rule)
          if (atsController.isShowingCountdown) ...[
            _buildCountdownDisplay(atsController),
            const SizedBox(height: 20),
          ],
          
          // Processing Animation
          if (atsController.isProcessing && !atsController.isShowingCountdown) ...[
            _buildProcessingAnimation(),
            const SizedBox(height: 20),
          ],

          // Overall Score Section
          if (atsController.overallScore != null && !atsController.isShowingCountdown && !atsController.isProcessing) ...[
            _buildOverallScoreSection(atsController),
            const SizedBox(height: 24),
          ],

          // Score Breakdown Section
          if (atsResults.isNotEmpty && !atsController.isShowingCountdown && !atsController.isProcessing) ...[
            _buildScoreBreakdown(atsResults),
          ],
        ],
      ),
    );
  }

  /// Build header section
  Widget _buildHeader() {
    return Row(
      children: [
        Icon(
          Icons.analytics_outlined,
          size: 28,
          color: Colors.purple.shade600,
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Enhanced ATS Score Analysis',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.purple.shade700,
                ),
              ),
              Text(
                'AI-powered multi-dimensional scoring',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  /// Build the overall score section
  Widget _buildOverallScoreSection(EnhancedATSController controller) {
    final overallScore = controller.overallScore ?? 0.0;
    final scoreCategory = controller.scoreCategory ?? 'Unknown';
    final scoreColor = _getScoreColor(overallScore);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [scoreColor.withOpacity(0.1), scoreColor.withOpacity(0.05)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: scoreColor.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          // Circular Score Display
          Expanded(
            flex: 2,
            child: Column(
              children: [
                SizedBox(
                  width: 120,
                  height: 120,
                  child: Stack(
                    children: [
                      // Background circle
                      SizedBox(
                        width: 120,
                        height: 120,
                        child: CircularProgressIndicator(
                          value: 1.0,
                          strokeWidth: 8,
                          backgroundColor: Colors.grey[200],
                          valueColor: AlwaysStoppedAnimation<Color>(
                            Colors.grey[200]!,
                          ),
                        ),
                      ),
                      // Progress circle
                      SizedBox(
                        width: 120,
                        height: 120,
                        child: CircularProgressIndicator(
                          value: overallScore / 100,
                          strokeWidth: 8,
                          backgroundColor: Colors.transparent,
                          valueColor: AlwaysStoppedAnimation<Color>(scoreColor),
                        ),
                      ),
                      // Score text in center
                      Positioned.fill(
                        child: Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                _getScoreIcon(overallScore),
                                style: const TextStyle(fontSize: 20),
                              ),
                              Text(
                                '${overallScore.toInt()}',
                                style: TextStyle(
                                  fontSize: 28,
                                  fontWeight: FontWeight.bold,
                                  color: scoreColor,
                                ),
                              ),
                              Text(
                                '/100',
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.grey[600],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Overall ATS Score',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 20),
          // Score info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Score Category',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: scoreColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: scoreColor.withOpacity(0.3)),
                  ),
                  child: Text(
                    scoreCategory,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: scoreColor,
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  'This score represents how well your CV matches the job requirements based on multiple factors including skills, experience, and industry alignment.',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Build score breakdown section
  Widget _buildScoreBreakdown(Map<String, dynamic> atsResults) {
    final detailedBreakdown = atsResults['detailed_breakdown'] ??
        atsResults['detailed_analysis'] ??
        {};

    // Debug logging
    debugPrint('🔍 [SCORE_BREAKDOWN] Building score breakdown...');
    debugPrint(
        '   Detailed breakdown keys: ${detailedBreakdown.keys.toList()}');
    debugPrint('   ATS Results keys: ${atsResults.keys.toList()}');

    // Debug requirement bonus data
    if (detailedBreakdown.containsKey('requirement_bonus')) {
      final reqBonus = detailedBreakdown['requirement_bonus'];
      debugPrint(
          '🔍 [SCORE_BREAKDOWN] Requirement bonus keys: ${reqBonus.keys.toList()}');
      debugPrint(
          '🔍 [SCORE_BREAKDOWN] Critical matches: ${reqBonus['critical_matches']}');
      debugPrint(
          '🔍 [SCORE_BREAKDOWN] Critical total: ${reqBonus['critical_total']}');
      debugPrint(
          '🔍 [SCORE_BREAKDOWN] Preferred matches: ${reqBonus['preferred_matches']}');
      debugPrint(
          '🔍 [SCORE_BREAKDOWN] Preferred total: ${reqBonus['preferred_total']}');
    } else {
      debugPrint(
          '❌ [SCORE_BREAKDOWN] No requirement_bonus found in detailed breakdown');
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '📈 DETAILED SCORE BREAKDOWN',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Colors.indigo[700],
          ),
        ),
        const SizedBox(height: 8),
        const Divider(thickness: 2),
        const SizedBox(height: 16),

        // Individual skill comparison components
        if (detailedBreakdown['technical_skills_match'] != null)
          _buildStaticScoreBar(
            'Technical Skills Match',
            '⚙️',
            detailedBreakdown['technical_skills_match']['score']?.toDouble() ??
                0.0,
            detailedBreakdown['technical_skills_match']['weight']?.toDouble() ??
                25.0,
            detailedBreakdown['technical_skills_match']['contribution']
                    ?.toDouble() ??
                0.0,
            isHighPriority: true,
          ),

        if (detailedBreakdown['soft_skills_match'] != null)
          _buildStaticScoreBar(
            'Soft Skills Match',
            '🤝',
            detailedBreakdown['soft_skills_match']['score']?.toDouble() ?? 0.0,
            detailedBreakdown['soft_skills_match']['weight']?.toDouble() ??
                10.0,
            detailedBreakdown['soft_skills_match']['contribution']
                    ?.toDouble() ??
                0.0,
          ),

        if (detailedBreakdown['domain_keywords_match'] != null)
          _buildStaticScoreBar(
            'Domain Keywords Match',
            '🏭',
            detailedBreakdown['domain_keywords_match']['score']?.toDouble() ??
                0.0,
            detailedBreakdown['domain_keywords_match']['weight']?.toDouble() ??
                8.0,
            detailedBreakdown['domain_keywords_match']['contribution']
                    ?.toDouble() ??
                0.0,
          ),

        if (detailedBreakdown['skills_relevance'] != null)
          _buildStaticScoreBar(
            'Skills Relevance',
            '🛠️',
            detailedBreakdown['skills_relevance']['score']?.toDouble() ?? 0.0,
            detailedBreakdown['skills_relevance']['weight']?.toDouble() ?? 12.0,
            detailedBreakdown['skills_relevance']['contribution']?.toDouble() ??
                0.0,
          ),

        if (detailedBreakdown['experience_alignment'] != null)
          _buildStaticScoreBar(
            'Experience Alignment',
            '👤',
            detailedBreakdown['experience_alignment']['score']?.toDouble() ??
                0.0,
            detailedBreakdown['experience_alignment']['weight']?.toDouble() ??
                15.0,
            detailedBreakdown['experience_alignment']['contribution']
                    ?.toDouble() ??
                0.0,
          ),

        if (detailedBreakdown['industry_fit'] != null)
          _buildStaticScoreBar(
            'Industry Fit',
            '🏢',
            detailedBreakdown['industry_fit']['score']?.toDouble() ?? 0.0,
            detailedBreakdown['industry_fit']['weight']?.toDouble() ?? 10.0,
            detailedBreakdown['industry_fit']['contribution']?.toDouble() ??
                0.0,
          ),

        if (detailedBreakdown['role_seniority'] != null)
          _buildStaticScoreBar(
            'Role Seniority',
            '🎯',
            detailedBreakdown['role_seniority']['score']?.toDouble() ?? 0.0,
            detailedBreakdown['role_seniority']['weight']?.toDouble() ?? 8.0,
            detailedBreakdown['role_seniority']['contribution']?.toDouble() ??
                0.0,
          ),

        if (detailedBreakdown['technical_depth'] != null)
          _buildStaticScoreBar(
            'Technical Depth',
            '🔧',
            detailedBreakdown['technical_depth']['score']?.toDouble() ?? 0.0,
            detailedBreakdown['technical_depth']['weight']?.toDouble() ?? 3.0,
            detailedBreakdown['technical_depth']['contribution']?.toDouble() ??
                0.0,
          ),

        const SizedBox(height: 12),

        // Requirement Bonus Component
        if (detailedBreakdown['requirement_bonus'] != null)
          Container(
            margin: const EdgeInsets.only(top: 16),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.amber.shade50, Colors.orange.shade50],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.amber.shade200),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: Colors.amber.shade100,
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: const Text('🎁', style: TextStyle(fontSize: 16)),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Enhanced Requirement Bonus',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                              color: Colors.amber.shade800,
                            ),
                          ),
                          Text(
                            'Essential: +2/+3pts, Missing: -10%, Preferred: +1pt',
                            style: TextStyle(
                              fontSize: 10,
                              color: Colors.amber.shade700,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          '${(detailedBreakdown['requirement_bonus']['score']?.toDouble() ?? 0.0).toStringAsFixed(1)} pts',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.amber.shade800,
                          ),
                        ),
                        Text(
                          'Bonus',
                          style: TextStyle(
                            fontSize: 10,
                            color: Colors.amber.shade600,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),

                // Detailed breakdown
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: _buildEnhancedBonusDetailCard(
                        '🔷 Essential',
                        detailedBreakdown['requirement_bonus']
                                ?['critical_matches'] ??
                            0,
                        detailedBreakdown['requirement_bonus']
                                ?['critical_total'] ??
                            0,
                        detailedBreakdown['requirement_bonus']
                                    ?['essential_bonus']
                                ?.toDouble() ??
                            0.0,
                        detailedBreakdown['requirement_bonus']
                                ?['critical_requirements'] ??
                            [],
                        Colors.blue.shade100,
                        Colors.blue.shade700,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _buildEnhancedBonusDetailCard(
                        '🟡 Preferred',
                        detailedBreakdown['requirement_bonus']
                                ?['preferred_matches'] ??
                            0,
                        detailedBreakdown['requirement_bonus']
                                ?['preferred_total'] ??
                            0,
                        detailedBreakdown['requirement_bonus']
                                    ?['preferred_bonus']
                                ?.toDouble() ??
                            0.0,
                        detailedBreakdown['requirement_bonus']
                                ?['preferred_requirements'] ??
                            [],
                        Colors.yellow.shade100,
                        Colors.yellow.shade700,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
      ],
    );
  }

  /// Build static score bar for individual components
  Widget _buildStaticScoreBar(
    String label,
    String icon,
    double score,
    double weight,
    double contribution, {
    bool isHighPriority = false,
  }) {
    final scoreColor = _getScoreColor(score);
    final percentage = (score / 100) * 100;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isHighPriority ? Colors.blue.shade50 : Colors.grey.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isHighPriority ? Colors.blue.shade200 : Colors.grey.shade300,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(icon, style: const TextStyle(fontSize: 16)),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  label,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: isHighPriority
                        ? Colors.blue.shade700
                        : Colors.grey.shade700,
                  ),
                ),
              ),
              Text(
                '${score.toStringAsFixed(1)}/100',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: scoreColor,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: LinearProgressIndicator(
                  value: score / 100,
                  backgroundColor: Colors.grey.shade200,
                  valueColor: AlwaysStoppedAnimation<Color>(scoreColor),
                ),
              ),
              const SizedBox(width: 12),
              Text(
                '${percentage.toStringAsFixed(0)}%',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                  color: scoreColor,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Weight: ${weight.toStringAsFixed(1)}%',
                style: TextStyle(
                  fontSize: 11,
                  color: Colors.grey.shade600,
                ),
              ),
              Text(
                'Contribution: ${contribution.toStringAsFixed(1)} pts',
                style: TextStyle(
                  fontSize: 11,
                  color: Colors.grey.shade600,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// Get score color based on score value
  Color _getScoreColor(double score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.orange;
    if (score >= 40) return Colors.yellow.shade700;
    return Colors.red;
  }

  /// Get score icon based on score value
  String _getScoreIcon(double score) {
    if (score >= 80) return '🏆';
    if (score >= 60) return '👍';
    if (score >= 40) return '⚠️';
    return '❌';
  }

  /// Build enhanced bonus detail card
  Widget _buildEnhancedBonusDetailCard(
    String label,
    int matches,
    int total,
    double points,
    List<dynamic> requirements,
    Color bgColor,
    Color textColor,
  ) {
    final percentage = total > 0 ? (matches / total * 100).round() : 0;

    // Filter matched and missing requirements
    final matchedReqs =
        requirements.where((req) => req['matched'] == true).toList();
    final missingReqs =
        requirements.where((req) => req['matched'] == false).toList();

    return _EnhancedBonusDetailCard(
      label: label,
      matches: matches,
      total: total,
      points: points,
      matchedReqs: matchedReqs,
      missingReqs: missingReqs,
      bgColor: bgColor,
      textColor: textColor,
    );
  }
  
  /// Build countdown display (10-second rule) - consistent style
  Widget _buildCountdownDisplay(EnhancedATSController controller) {
    // Get the appropriate message based on countdown time
    String getMessage() {
      if (controller.countdownSeconds >= 8) {
        return 'Generating enhanced ATS analysis...';
      } else if (controller.countdownSeconds >= 5) {
        return 'Analyzing ATS compatibility...';
      } else if (controller.countdownSeconds >= 2) {
        return 'Calculating comprehensive score...';
      } else {
        return 'Finalizing ATS results...';
      }
    }
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.orange.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.orange.shade200),
      ),
      child: Row(
        children: [
          // Consistent circular progress indicator
          SizedBox(
            width: 24,
            height: 24,
            child: CircularProgressIndicator(
              strokeWidth: 3,
              valueColor: AlwaysStoppedAnimation<Color>(Colors.orange.shade600),
            ),
          ),
          const SizedBox(width: 16),
          // Status message with consistent styling
          Expanded(
            child: Text(
              getMessage(),
              style: TextStyle(
                fontSize: 16,
                color: Colors.orange.shade700,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  /// Build processing animation - consistent style
  Widget _buildProcessingAnimation() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Row(
        children: [
          // Consistent circular progress indicator
          SizedBox(
            width: 24,
            height: 24,
            child: CircularProgressIndicator(
              strokeWidth: 3,
              valueColor: AlwaysStoppedAnimation<Color>(Colors.blue.shade600),
            ),
          ),
          const SizedBox(width: 16),
          // Processing message with consistent styling
          Expanded(
            child: Text(
              'Generating comprehensive ATS report...',
              style: TextStyle(
                fontSize: 16,
                color: Colors.blue.shade700,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Expandable enhanced bonus detail card
class _EnhancedBonusDetailCard extends StatefulWidget {
  final String label;
  final int matches;
  final int total;
  final double points;
  final List<dynamic> matchedReqs;
  final List<dynamic> missingReqs;
  final Color bgColor;
  final Color textColor;

  const _EnhancedBonusDetailCard({
    required this.label,
    required this.matches,
    required this.total,
    required this.points,
    required this.matchedReqs,
    required this.missingReqs,
    required this.bgColor,
    required this.textColor,
  });

  @override
  State<_EnhancedBonusDetailCard> createState() =>
      _EnhancedBonusDetailCardState();
}

class _EnhancedBonusDetailCardState extends State<_EnhancedBonusDetailCard> {
  bool _isMatchedExpanded = false;
  bool _isMissingExpanded = false;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: widget.bgColor,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: widget.textColor.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with label and stats
          Center(
            child: Column(
              children: [
                Text(
                  widget.label,
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    color: widget.textColor,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 4),
                Text(
                  '${widget.matches}/${widget.total}',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: widget.textColor,
                  ),
                ),
                Text(
                  '${widget.total > 0 ? (widget.matches / widget.total * 100).round() : 0}% • ${widget.points >= 0 ? '+' : ''}${widget.points.toStringAsFixed(1)} pts',
                  style: TextStyle(
                    fontSize: 9,
                    color: widget.textColor.withOpacity(0.8),
                  ),
                ),
              ],
            ),
          ),

          if (widget.matchedReqs.isNotEmpty ||
              widget.missingReqs.isNotEmpty) ...[
            const SizedBox(height: 8),
            Container(
              height: 1,
              color: widget.textColor.withOpacity(0.2),
            ),
            const SizedBox(height: 6),

            // Matched requirements
            if (widget.matchedReqs.isNotEmpty) ...[
              _buildExpandableSection(
                'Found (${widget.matchedReqs.length}):',
                Icons.check_circle,
                Colors.green,
                widget.matchedReqs,
                _isMatchedExpanded,
                (value) => setState(() => _isMatchedExpanded = value),
              ),
            ],

            // Missing requirements
            if (widget.missingReqs.isNotEmpty) ...[
              const SizedBox(height: 8),
              _buildExpandableSection(
                'Missing (${widget.missingReqs.length}):',
                Icons.cancel,
                Colors.red,
                widget.missingReqs,
                _isMissingExpanded,
                (value) => setState(() => _isMissingExpanded = value),
              ),
            ],
          ],
        ],
      ),
    );
  }

  /// Build expandable section for requirements
  Widget _buildExpandableSection(
    String title,
    IconData icon,
    Color iconColor,
    List<dynamic> requirements,
    bool isExpanded,
    Function(bool) onToggle,
  ) {
    return InkWell(
      onTap: () => onToggle(!isExpanded),
      borderRadius: BorderRadius.circular(4),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 2, horizontal: 4),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(4),
          color: isExpanded
              ? widget.textColor.withOpacity(0.05)
              : Colors.transparent,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with toggle button
            Row(
              children: [
                Icon(icon, color: iconColor, size: 12),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    title,
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      color: widget.textColor,
                    ),
                  ),
                ),
                Icon(
                  isExpanded ? Icons.expand_less : Icons.expand_more,
                  size: 16,
                  color: widget.textColor.withOpacity(0.6),
                ),
              ],
            ),

            // Expandable content
            if (isExpanded) ...[
              const SizedBox(height: 6),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: requirements.map<Widget>((req) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Text(
                      '• ${req['requirement'] ?? req['skill'] ?? 'Unknown'}',
                      style: TextStyle(
                        fontSize: 9,
                        color: widget.textColor.withOpacity(0.8),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ] else if (requirements.length > 3) ...[
              // Show first 3 items when collapsed
              const SizedBox(height: 6),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: requirements.take(3).map<Widget>((req) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Text(
                      '• ${req['requirement'] ?? req['skill'] ?? 'Unknown'}',
                      style: TextStyle(
                        fontSize: 9,
                        color: widget.textColor.withOpacity(0.8),
                      ),
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 4),
              Text(
                '... and ${requirements.length - 3} more (tap to expand)',
                style: TextStyle(
                  fontSize: 8,
                  color: widget.textColor.withOpacity(0.6),
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
