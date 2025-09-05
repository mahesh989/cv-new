import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../theme/app_theme.dart';
import '../../services/enhanced_ats_service.dart';

class EnhancedATSScoreWidget extends StatefulWidget {
  final Map<String, dynamic> atsResults;

  const EnhancedATSScoreWidget({
    Key? key,
    required this.atsResults,
  }) : super(key: key);

  @override
  State<EnhancedATSScoreWidget> createState() => _EnhancedATSScoreWidgetState();
}

class _EnhancedATSScoreWidgetState extends State<EnhancedATSScoreWidget>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _animation;

  // Expansion state for requirement bonus sections
  bool _isMatchedReqsExpanded = false;
  bool _isMissingReqsExpanded = false;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    _animation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final overallScore =
        widget.atsResults['overall_ats_score']?.toDouble() ?? 0.0;
    final scoreCategory = widget.atsResults['score_category'] ?? 'Unknown';

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(),
            const SizedBox(height: 20),
            _buildOverallScoreSection(overallScore, scoreCategory),
            const SizedBox(height: 24),
            _buildScoreBreakdown(),
          ],
        ),
      ),
    );
  }

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
                style: AppTheme.headingSmall.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.purple.shade700,
                ),
              ),
              Text(
                'AI-powered multi-dimensional scoring',
                style: AppTheme.bodySmall.copyWith(
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildOverallScoreSection(double score, String category) {
    final scoreColor = _getScoreColor(score);
    final scoreIcon = EnhancedATSService.getScoreIcon(score);

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
                AnimatedBuilder(
                  animation: _animation,
                  builder: (context, child) {
                    return SizedBox(
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
                          // Animated progress circle
                          SizedBox(
                            width: 120,
                            height: 120,
                            child: CircularProgressIndicator(
                              value: (score / 100) * _animation.value,
                              strokeWidth: 8,
                              backgroundColor: Colors.transparent,
                              valueColor:
                                  AlwaysStoppedAnimation<Color>(scoreColor),
                            ),
                          ),
                          // Score text in center
                          Positioned.fill(
                            child: Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Text(
                                    scoreIcon,
                                    style: const TextStyle(fontSize: 20),
                                  ),
                                  Text(
                                    '${(score * _animation.value).toInt()}',
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
                    );
                  },
                ),
                const SizedBox(height: 8),
                Text(
                  'Overall ATS Score',
                  style: AppTheme.bodyMedium.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 20),
          // Score Category and Details
          Expanded(
            flex: 3,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: scoreColor.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    category,
                    style: TextStyle(
                      color: scoreColor,
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                _buildScoreInsight(score),
                const SizedBox(height: 8),
                _buildBaseScoreSummary(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildScoreInsight(double score) {
    String insight;
    if (score >= 90) {
      insight = "Excellent! Your CV is highly optimized for ATS systems.";
    } else if (score >= 80) {
      insight =
          "Good score! Minor optimizations can boost your ATS performance.";
    } else if (score >= 70) {
      insight = "Fair score. Focus on key recommendations to improve.";
    } else if (score >= 60) {
      insight = "Needs improvement. Address critical gaps first.";
    } else {
      insight = "Significant optimization needed for ATS success.";
    }

    return Text(
      insight,
      style: AppTheme.bodySmall.copyWith(
        color: Colors.grey[700],
        fontStyle: FontStyle.italic,
      ),
    );
  }

  Widget _buildBaseScoreSummary() {
    final baseScores = widget.atsResults['base_scores'] ?? {};
    final categoryScores = baseScores['category_scores'] ?? {};

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Base Keyword Matching:',
          style: AppTheme.bodySmall.copyWith(
            fontWeight: FontWeight.w600,
            fontSize: 11,
          ),
        ),
        const SizedBox(height: 4),
        ...categoryScores.entries.map((entry) {
          final category = entry.key.toString().replaceAll('_', ' ');
          final score = entry.value?.toDouble() ?? 0.0;
          return Padding(
            padding: const EdgeInsets.only(bottom: 2),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  category,
                  style: AppTheme.bodySmall.copyWith(
                    fontSize: 10,
                    color: Colors.grey[600],
                  ),
                ),
                Text(
                  '${score.toInt()}%',
                  style: AppTheme.bodySmall.copyWith(
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    color: _getScoreColor(score),
                  ),
                ),
              ],
            ),
          );
        }).toList(),
      ],
    );
  }

  Widget _buildScoreBreakdown() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Overall Score Circle/Pie Chart
        _buildOverallScoreChart(),
        const SizedBox(height: 24),

        // Detailed Score Breakdown
        _buildDetailedScoreBreakdown(),
      ],
    );
  }

  Widget _buildOverallScoreChart() {
    final overallScore =
        widget.atsResults['overall_ats_score']?.toDouble() ?? 0.0;
    final scoreCategory = widget.atsResults['score_category'] ?? '';

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.blue.shade50, Colors.purple.shade50],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Row(
        children: [
          // Circular Score Display
          SizedBox(
            width: 120,
            height: 120,
            child: Stack(
              children: [
                // Background circle
                CircularProgressIndicator(
                  value: 1.0,
                  strokeWidth: 12,
                  backgroundColor: Colors.grey.shade200,
                  valueColor:
                      AlwaysStoppedAnimation<Color>(Colors.grey.shade200),
                ),
                // Progress circle
                AnimatedBuilder(
                  animation: _animation,
                  builder: (context, child) {
                    return CircularProgressIndicator(
                      value: (overallScore / 100) * _animation.value,
                      strokeWidth: 12,
                      backgroundColor: Colors.transparent,
                      valueColor: AlwaysStoppedAnimation<Color>(
                        _getScoreColor(overallScore),
                      ),
                    );
                  },
                ),
                // Score text in center
                Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        '${overallScore.toInt()}',
                        style: AppTheme.headingLarge.copyWith(
                          fontWeight: FontWeight.bold,
                          color: _getScoreColor(overallScore),
                          fontSize: 32,
                        ),
                      ),
                      Text(
                        '/100',
                        style: AppTheme.bodySmall.copyWith(
                          color: Colors.grey.shade600,
                          fontSize: 10,
                        ),
                      ),
                    ],
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
                  'Overall ATS Score',
                  style: AppTheme.headingMedium.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: _getScoreColor(overallScore).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: _getScoreColor(overallScore).withOpacity(0.3),
                    ),
                  ),
                  child: Text(
                    scoreCategory,
                    style: AppTheme.bodySmall.copyWith(
                      color: _getScoreColor(overallScore),
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailedScoreBreakdown() {
    final detailedBreakdown = widget.atsResults['detailed_breakdown'] ?? {};

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '📈 DETAILED SCORE BREAKDOWN',
          style: AppTheme.headingMedium.copyWith(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        const SizedBox(height: 8),
        const Divider(thickness: 2),
        const SizedBox(height: 16),

        // Individual skill comparison components (using existing CV-JD comparison data)
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
            isHighPriority: true, // Highest weight component
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

        // NEW: Requirement Bonus Component
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
                            style: AppTheme.bodyMedium.copyWith(
                              fontWeight: FontWeight.bold,
                              color: Colors.amber.shade800,
                            ),
                          ),
                          Text(
                            'Essential: +2/+3pts, Missing: -10%, Preferred: +1pt',
                            style: AppTheme.bodySmall.copyWith(
                              color: Colors.amber.shade700,
                              fontSize: 10,
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
                          style: AppTheme.bodyMedium.copyWith(
                            fontWeight: FontWeight.bold,
                            color: Colors.amber.shade800,
                            fontSize: 16,
                          ),
                        ),
                        Text(
                          'Enhanced Bonus',
                          style: AppTheme.bodySmall.copyWith(
                            color: Colors.amber.shade600,
                            fontSize: 10,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // Breakdown of matches
                Row(
                  children: [
                    Expanded(
                      child: _buildEnhancedBonusDetailCard(
                        '🔷 Essential',
                        detailedBreakdown['requirement_bonus']
                                ['critical_matches'] ??
                            0,
                        detailedBreakdown['requirement_bonus']
                                ['critical_total'] ??
                            0,
                        detailedBreakdown['requirement_bonus']
                                    ['essential_bonus']
                                ?.toDouble() ??
                            0.0,
                        detailedBreakdown['requirement_bonus']
                                ['critical_requirements'] ??
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
                                ['preferred_matches'] ??
                            0,
                        detailedBreakdown['requirement_bonus']
                                ['preferred_total'] ??
                            0,
                        detailedBreakdown['requirement_bonus']
                                    ['preferred_bonus']
                                ?.toDouble() ??
                            0.0,
                        detailedBreakdown['requirement_bonus']
                                ['preferred_requirements'] ??
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

        const SizedBox(height: 20),
        const Divider(),
        const SizedBox(height: 8),

        // Total calculation formula
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.green.shade50,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.green.shade200),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.calculate, color: Colors.green.shade700, size: 20),
                  const SizedBox(width: 8),
                  Text(
                    'Final ATS Score Calculation',
                    style: AppTheme.bodyMedium.copyWith(
                      color: Colors.green.shade800,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                'Technical×25% + Soft×10% + Domain×8% + Skills Relevance×12% + Experience×15% + Industry×10% + Seniority×8% + Tech Depth×3% + Enhanced Requirement Bonus',
                style: AppTheme.bodySmall.copyWith(
                  color: Colors.green.shade700,
                  fontWeight: FontWeight.w500,
                  fontSize: 11,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildStaticScoreBar(
    String label,
    String icon,
    double score,
    double weight,
    double contribution, {
    bool showSubcomponents = false,
    Map<String, dynamic> subcomponents = const {},
    bool isHighPriority = false,
    bool isPenalty = false,
  }) {
    final color = _getScoreColor(score);

    // Create ASCII-style progress bar
    final filledBars = (score / 5).round().clamp(0, 20);
    final emptyBars = 20 - filledBars;
    final progressBars = '█' * filledBars + '░' * emptyBars;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Main score bar
          Container(
            padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 12),
            decoration: BoxDecoration(
              color: isHighPriority
                  ? Colors.blue.shade50
                  : isPenalty
                      ? Colors.red.shade50
                      : Colors.grey.shade50,
              borderRadius: BorderRadius.circular(6),
              border: Border.all(
                color: isHighPriority
                    ? Colors.blue.shade300
                    : isPenalty
                        ? Colors.red.shade300
                        : Colors.grey.shade200,
                width: isHighPriority ? 2 : 1,
              ),
            ),
            child: Row(
              children: [
                // Label with icon
                SizedBox(
                  width: 180,
                  child: Row(
                    children: [
                      Text(icon, style: const TextStyle(fontSize: 16)),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              label.toUpperCase(),
                              style: AppTheme.bodySmall.copyWith(
                                fontWeight: isHighPriority
                                    ? FontWeight.bold
                                    : FontWeight.w600,
                                fontSize: isHighPriority ? 12 : 11,
                                color: isHighPriority
                                    ? Colors.blue.shade800
                                    : isPenalty
                                        ? Colors.red.shade700
                                        : Colors.grey.shade700,
                              ),
                            ),
                            if (isHighPriority)
                              Text(
                                'Highest Priority',
                                style: AppTheme.bodySmall.copyWith(
                                  fontSize: 9,
                                  color: Colors.blue.shade600,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),

                // ASCII Progress Bar
                Expanded(
                  flex: 2,
                  child: Text(
                    progressBars,
                    style: TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 11,
                      color: color,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
                const SizedBox(width: 16),

                // Score, weight, and contribution
                SizedBox(
                  width: 140,
                  child: Text(
                    '${score.toStringAsFixed(1)}/100 (${weight.toStringAsFixed(1)}%)',
                    style: AppTheme.bodySmall.copyWith(
                      fontWeight: FontWeight.w600,
                      color: color,
                      fontSize: 11,
                    ),
                    textAlign: TextAlign.right,
                  ),
                ),
                const SizedBox(width: 12),

                // Arrow and contribution
                Text(
                  '→ ${contribution.toStringAsFixed(1)}',
                  style: AppTheme.bodySmall.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.green.shade700,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),

          // Subcomponents (kept for backward compatibility but not used in new structure)
          if (showSubcomponents && subcomponents.isNotEmpty) ...[
            const SizedBox(height: 8),
            Padding(
              padding: const EdgeInsets.only(left: 20),
              child: Column(
                children: [
                  _buildSubcomponentBar(
                    '├─ Technical Skills',
                    subcomponents['technical_skills']?['score']?.toDouble() ??
                        0.0,
                    subcomponents['technical_skills']?['weight']?.toDouble() ??
                        50.0,
                  ),
                  _buildSubcomponentBar(
                    '├─ Domain Keywords',
                    subcomponents['domain_keywords']?['score']?.toDouble() ??
                        0.0,
                    subcomponents['domain_keywords']?['weight']?.toDouble() ??
                        30.0,
                  ),
                  _buildSubcomponentBar(
                    '└─ Soft Skills',
                    subcomponents['soft_skills']?['score']?.toDouble() ?? 0.0,
                    subcomponents['soft_skills']?['weight']?.toDouble() ?? 20.0,
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSubcomponentBar(String label, double score, double weight) {
    final color = _getScoreColor(score);
    final filledBars = (score / 10).round().clamp(0, 10);
    final emptyBars = 10 - filledBars;
    final miniProgressBars = '▓' * filledBars + '░' * emptyBars;

    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          SizedBox(
            width: 140,
            child: Text(
              label,
              style: AppTheme.bodySmall.copyWith(
                fontSize: 10,
                color: Colors.grey.shade600,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              miniProgressBars,
              style: TextStyle(
                fontFamily: 'monospace',
                fontSize: 10,
                color: color.withValues(alpha: 0.8),
                letterSpacing: 0.5,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Text(
            '${score.toStringAsFixed(1)}/100 (${weight.toStringAsFixed(1)}%)',
            style: AppTheme.bodySmall.copyWith(
              fontSize: 9,
              color: color,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRequirementBadge(String label, int count, String description,
      Color bgColor, Color textColor) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: textColor.withValues(alpha: 0.3)),
      ),
      child: Column(
        children: [
          Text(
            label,
            style: AppTheme.bodySmall.copyWith(
              fontWeight: FontWeight.w600,
              color: textColor,
              fontSize: 11,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            '$count',
            style: AppTheme.headingMedium.copyWith(
              fontWeight: FontWeight.bold,
              color: textColor,
              fontSize: 24,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            description,
            style: AppTheme.bodySmall.copyWith(
              color: textColor.withValues(alpha: 0.8),
              fontSize: 10,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildDetailedScoreBar(String label, String icon, double score,
      double weight, double contribution) {
    final color = _getScoreColor(score);
    final progressBars =
        '█' * (score / 5).round() + '░' * (20 - (score / 5).round());

    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(
        children: [
          // Header row with label and values
          Row(
            children: [
              // Icon and label
              SizedBox(
                width: 140,
                child: Row(
                  children: [
                    Text(icon, style: const TextStyle(fontSize: 16)),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        label,
                        style: AppTheme.bodyMedium.copyWith(
                          fontWeight: FontWeight.w600,
                          fontSize: 13,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              // Progress bars (visual representation)
              Expanded(
                flex: 3,
                child: Text(
                  progressBars,
                  style: TextStyle(
                    fontFamily: 'monospace',
                    fontSize: 12,
                    color: color,
                    letterSpacing: 0,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              // Score and weight
              SizedBox(
                width: 120,
                child: Text(
                  '${score.toStringAsFixed(1)}/100 (${weight.toStringAsFixed(1)}%)',
                  style: AppTheme.bodySmall.copyWith(
                    fontWeight: FontWeight.w600,
                    color: color,
                  ),
                  textAlign: TextAlign.right,
                ),
              ),
              const SizedBox(width: 8),
              // Arrow and contribution
              Text(
                '→ ${contribution.toStringAsFixed(1)}',
                style: AppTheme.bodySmall.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.green.shade700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          // Actual progress bar
          AnimatedBuilder(
            animation: _animation,
            builder: (context, child) {
              return Container(
                height: 6,
                width: double.infinity,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(3),
                  color: Colors.grey.shade200,
                ),
                child: FractionallySizedBox(
                  alignment: Alignment.centerLeft,
                  widthFactor: (score / 100) * _animation.value,
                  child: Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(3),
                      gradient: LinearGradient(
                        colors: [color.withOpacity(0.7), color],
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildScoreBar(String label, double score,
      {bool isMainComponent = false}) {
    final color = _getScoreColor(score);

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  label,
                  style: AppTheme.bodyMedium.copyWith(
                    fontWeight:
                        isMainComponent ? FontWeight.w600 : FontWeight.normal,
                    fontSize: isMainComponent ? 13 : 12,
                  ),
                ),
              ),
              Text(
                '${score.toInt()}${isMainComponent ? '/100' : ''}',
                style: AppTheme.bodyMedium.copyWith(
                  fontWeight: FontWeight.w600,
                  color: color,
                  fontSize: isMainComponent ? 13 : 12,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          AnimatedBuilder(
            animation: _animation,
            builder: (context, child) {
              return Container(
                height: isMainComponent ? 8 : 6,
                width: double.infinity,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(4),
                  color: Colors.grey[200],
                ),
                child: FractionallySizedBox(
                  alignment: Alignment.centerLeft,
                  widthFactor: (score / 100) * _animation.value,
                  child: Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(4),
                      color: color,
                    ),
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildEnhancementFactor(String label, double value) {
    final isPositive = value >= 0;
    final color = isPositive ? Colors.green : Colors.red;
    final icon = isPositive ? '↗️' : '↘️';

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Text(
              '$icon $label',
              style: AppTheme.bodySmall.copyWith(fontSize: 11),
            ),
          ),
          Text(
            '${isPositive ? '+' : ''}${value.toStringAsFixed(1)}',
            style: AppTheme.bodySmall.copyWith(
              fontWeight: FontWeight.w600,
              color: color,
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSkillsRelevanceAnalysis() {
    final detailedAnalysis = widget.atsResults['detailed_analysis'] ?? {};
    final skillsRelevance =
        EnhancedATSService.parseSkillsRelevance(detailedAnalysis);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Overall Skills Score:',
              style: AppTheme.bodySmall,
            ),
            Text(
              '${skillsRelevance['overall_skills_score']?.toInt() ?? 0}/100',
              style: AppTheme.bodySmall.copyWith(fontWeight: FontWeight.w600),
            ),
          ],
        ),
        const SizedBox(height: 8),
        if (skillsRelevance['strength_areas'] != null &&
            (skillsRelevance['strength_areas'] as List).isNotEmpty) ...[
          Text(
            '💪 Strength Areas:',
            style: AppTheme.bodySmall.copyWith(fontWeight: FontWeight.w600),
          ),
          Text(
            (skillsRelevance['strength_areas'] as List).join(', '),
            style: AppTheme.bodySmall.copyWith(color: Colors.green[700]),
          ),
        ],
        if (skillsRelevance['improvement_areas'] != null &&
            (skillsRelevance['improvement_areas'] as List).isNotEmpty) ...[
          const SizedBox(height: 4),
          Text(
            '📈 Improvement Areas:',
            style: AppTheme.bodySmall.copyWith(fontWeight: FontWeight.w600),
          ),
          Text(
            (skillsRelevance['improvement_areas'] as List).join(', '),
            style: AppTheme.bodySmall.copyWith(color: Colors.orange[700]),
          ),
        ],
      ],
    );
  }

  Widget _buildMissingSkillsAnalysis() {
    final detailedAnalysis = widget.atsResults['detailed_analysis'] ?? {};
    final missingSkillsImpact =
        EnhancedATSService.parseMissingSkillsImpact(detailedAnalysis);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Impact Score:',
              style: AppTheme.bodySmall,
            ),
            Text(
              '${missingSkillsImpact['overall_impact_score']?.toInt() ?? 0}/100',
              style: AppTheme.bodySmall.copyWith(fontWeight: FontWeight.w600),
            ),
          ],
        ),
        const SizedBox(height: 8),
        if (missingSkillsImpact['critical_gaps'] != null &&
            (missingSkillsImpact['critical_gaps'] as List).isNotEmpty) ...[
          Text(
            '🔴 Critical Gaps:',
            style: AppTheme.bodySmall.copyWith(fontWeight: FontWeight.w600),
          ),
          Text(
            (missingSkillsImpact['critical_gaps'] as List).join(', '),
            style: AppTheme.bodySmall.copyWith(color: Colors.red[700]),
          ),
        ],
        if (missingSkillsImpact['minor_gaps'] != null &&
            (missingSkillsImpact['minor_gaps'] as List).isNotEmpty) ...[
          const SizedBox(height: 4),
          Text(
            '🟡 Minor Gaps:',
            style: AppTheme.bodySmall.copyWith(fontWeight: FontWeight.w600),
          ),
          Text(
            (missingSkillsImpact['minor_gaps'] as List).join(', '),
            style: AppTheme.bodySmall.copyWith(color: Colors.orange[600]),
          ),
        ],
      ],
    );
  }

  Widget _buildAchievementMapping() {
    final achievementsMapped = List<Map<String, dynamic>>.from(
        widget.atsResults['achievements_mapped'] ?? []);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '🏆 Achievement → Requirement Mapping',
          style: AppTheme.headingMedium.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        if (achievementsMapped.isEmpty)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              children: [
                Icon(Icons.insights, size: 48, color: Colors.grey[400]),
                const SizedBox(height: 8),
                Text(
                  'Achievement mapping analysis in progress...',
                  style: AppTheme.bodyMedium.copyWith(color: Colors.grey[600]),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 4),
                Text(
                  'This feature maps your CV achievements to specific JD requirements using AI analysis.',
                  style: AppTheme.bodySmall.copyWith(color: Colors.grey[500]),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          )
        else
          ...achievementsMapped.map((achievement) {
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
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.green.shade600,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          achievement['relevance'] ?? 'High',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'CV Achievement',
                          style: AppTheme.bodySmall.copyWith(
                            fontWeight: FontWeight.w600,
                            color: Colors.green[700],
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    achievement['achievement'] ?? '',
                    style: AppTheme.bodyMedium,
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(Icons.arrow_forward,
                          size: 16, color: Colors.grey[600]),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Maps to: ${achievement['maps_to'] ?? 'JD requirement'}',
                          style: AppTheme.bodySmall.copyWith(
                            color: Colors.grey[700],
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            );
          }).toList(),
      ],
    );
  }

  Widget _buildBonusDetailCard(String label, int matches, int total,
      double points, Color bgColor, Color textColor) {
    final percentage = total > 0 ? (matches / total * 100).round() : 0;

    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: textColor.withValues(alpha: 0.3)),
      ),
      child: Column(
        children: [
          Text(
            label,
            style: AppTheme.bodySmall.copyWith(
              fontWeight: FontWeight.w600,
              color: textColor,
              fontSize: 10,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 4),
          Text(
            '$matches/$total',
            style: AppTheme.bodyMedium.copyWith(
              fontWeight: FontWeight.bold,
              color: textColor,
              fontSize: 14,
            ),
          ),
          Text(
            '$percentage%',
            style: AppTheme.bodySmall.copyWith(
              color: textColor.withValues(alpha: 0.8),
              fontSize: 10,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            '+${points.toStringAsFixed(1)} pts',
            style: AppTheme.bodySmall.copyWith(
              color: textColor,
              fontWeight: FontWeight.w600,
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEnhancedBonusDetailCard(
      String label,
      int matches,
      int total,
      double points,
      List<dynamic> requirements,
      Color bgColor,
      Color textColor) {
    final percentage = total > 0 ? (matches / total * 100).round() : 0;

    // Filter matched and missing requirements
    final matchedReqs =
        requirements.where((req) => req['matched'] == true).toList();
    final missingReqs =
        requirements.where((req) => req['matched'] == false).toList();

    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: textColor.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with label and stats
          Center(
            child: Column(
              children: [
                Text(
                  label,
                  style: AppTheme.bodySmall.copyWith(
                    fontWeight: FontWeight.w600,
                    color: textColor,
                    fontSize: 10,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 4),
                Text(
                  '$matches/$total',
                  style: AppTheme.bodyMedium.copyWith(
                    fontWeight: FontWeight.bold,
                    color: textColor,
                    fontSize: 14,
                  ),
                ),
                Text(
                  '$percentage% • ${points >= 0 ? '+' : ''}${points.toStringAsFixed(1)} pts',
                  style: AppTheme.bodySmall.copyWith(
                    color: textColor.withValues(alpha: 0.8),
                    fontSize: 9,
                  ),
                ),
              ],
            ),
          ),

          if (requirements.isNotEmpty) ...[
            const SizedBox(height: 8),
            Container(
              height: 1,
              color: textColor.withValues(alpha: 0.2),
            ),
            const SizedBox(height: 6),

            // Matched requirements with hover
            if (matchedReqs.isNotEmpty) ...[
              Row(
                children: [
                  Icon(Icons.check_circle, color: Colors.green, size: 12),
                  const SizedBox(width: 6),
                  Text(
                    'Found (${matchedReqs.length}):',
                    style: AppTheme.bodySmall.copyWith(
                      fontWeight: FontWeight.w600,
                      color: textColor,
                      fontSize: 10,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: matchedReqs.take(3).map<Widget>((req) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Tooltip(
                      message: req['jd_proof_text'] ??
                          req['cv_evidence'] ??
                          'Found in CV',
                      decoration: BoxDecoration(
                        color: Colors.grey[800],
                        borderRadius: BorderRadius.circular(6),
                      ),
                      textStyle:
                          const TextStyle(color: Colors.white, fontSize: 12),
                      waitDuration: const Duration(milliseconds: 500),
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 6),
                        decoration: BoxDecoration(
                          color: Colors.green.shade100,
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(
                              color: Colors.green.shade300, width: 0.5),
                        ),
                        child: Text(
                          req['requirement'] ?? '',
                          style: AppTheme.bodySmall.copyWith(
                            color: Colors.green.shade700,
                            fontSize: 11,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
              if (matchedReqs.length > 3) ...[
                const SizedBox(height: 4),
                InkWell(
                  onTap: () {
                    setState(() {
                      _isMatchedReqsExpanded = !_isMatchedReqsExpanded;
                    });
                  },
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        _isMatchedReqsExpanded
                            ? Icons.expand_less
                            : Icons.expand_more,
                        color: textColor.withValues(alpha: 0.6),
                        size: 14,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        _isMatchedReqsExpanded
                            ? 'Show less'
                            : 'Show ${matchedReqs.length - 3} more',
                        style: AppTheme.bodySmall.copyWith(
                          color: textColor.withValues(alpha: 0.6),
                          fontSize: 9,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ],
                  ),
                ),
                if (_isMatchedReqsExpanded) ...[
                  const SizedBox(height: 6),
                  ...matchedReqs.skip(3).map<Widget>((req) {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Tooltip(
                        message: req['jd_proof_text'] ??
                            req['cv_evidence'] ??
                            'Found in CV',
                        decoration: BoxDecoration(
                          color: Colors.grey[800],
                          borderRadius: BorderRadius.circular(6),
                        ),
                        textStyle:
                            const TextStyle(color: Colors.white, fontSize: 12),
                        waitDuration: const Duration(milliseconds: 500),
                        child: Container(
                          width: double.infinity,
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 6),
                          decoration: BoxDecoration(
                            color: Colors.green.shade100,
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(
                                color: Colors.green.shade300, width: 0.5),
                          ),
                          child: Text(
                            req['requirement'] ?? '',
                            style: AppTheme.bodySmall.copyWith(
                              color: Colors.green.shade700,
                              fontSize: 11,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ],
              ],
            ],

            // Missing requirements
            if (missingReqs.isNotEmpty) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.cancel, color: Colors.red.shade400, size: 12),
                  const SizedBox(width: 6),
                  Text(
                    'Missing (${missingReqs.length}):',
                    style: AppTheme.bodySmall.copyWith(
                      fontWeight: FontWeight.w600,
                      color: textColor,
                      fontSize: 10,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: missingReqs.take(2).map<Widget>((req) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.red.shade50,
                        borderRadius: BorderRadius.circular(6),
                        border:
                            Border.all(color: Colors.red.shade200, width: 0.5),
                      ),
                      child: Text(
                        req['requirement'] ?? '',
                        style: AppTheme.bodySmall.copyWith(
                          color: Colors.red.shade600,
                          fontSize: 11,
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
              if (missingReqs.length > 2) ...[
                const SizedBox(height: 4),
                InkWell(
                  onTap: () {
                    setState(() {
                      _isMissingReqsExpanded = !_isMissingReqsExpanded;
                    });
                  },
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        _isMissingReqsExpanded
                            ? Icons.expand_less
                            : Icons.expand_more,
                        color: textColor.withValues(alpha: 0.6),
                        size: 14,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        _isMissingReqsExpanded
                            ? 'Show less'
                            : 'Show ${missingReqs.length - 2} more',
                        style: AppTheme.bodySmall.copyWith(
                          color: textColor.withValues(alpha: 0.6),
                          fontSize: 9,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ],
                  ),
                ),
                if (_isMissingReqsExpanded) ...[
                  const SizedBox(height: 6),
                  ...missingReqs.skip(2).map<Widget>((req) {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 6),
                        decoration: BoxDecoration(
                          color: Colors.red.shade50,
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(
                              color: Colors.red.shade200, width: 0.5),
                        ),
                        child: Text(
                          req['requirement'] ?? '',
                          style: AppTheme.bodySmall.copyWith(
                            color: Colors.red.shade600,
                            fontSize: 11,
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ],
              ],
            ],
          ],
        ],
      ),
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 90) return Colors.green;
    if (score >= 80) return Colors.lightGreen;
    if (score >= 70) return Colors.orange;
    if (score >= 60) return Colors.deepOrange;
    return Colors.red;
  }
}
