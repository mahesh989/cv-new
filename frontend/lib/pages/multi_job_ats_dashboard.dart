import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../theme/app_theme.dart';
import '../services/job_database.dart';
import '../widgets/uniform_top_nav_bar.dart';
import '../utils/ats_helpers.dart';

// 🎯 STUNNING Multi-Job ATS Dashboard with Premium UI
class MultiJobATSDashboard extends StatefulWidget {
  const MultiJobATSDashboard({Key? key}) : super(key: key);

  @override
  State<MultiJobATSDashboard> createState() => _MultiJobATSDashboardState();

  /// Static method to add ATS result data for multi-job tracking using SQLite
  static Future<void> addATSResult({
    required String jobUrl,
    required String jobTitle,
    required String company,
    required int atsScore,
    required List<String> matchedSkills,
    required List<String> missedSkills,
    String? matchRate,
  }) async {
    try {
      // Create a more consistent job identifier
      String jobIdentifier = jobUrl;
      if (jobUrl.startsWith('manual_') || jobUrl.isEmpty) {
        final normalizedTitle = jobTitle.toLowerCase().replaceAll(
              RegExp(r'[^a-z0-9]'),
              '',
            );
        final normalizedCompany = company.toLowerCase().replaceAll(
              RegExp(r'[^a-z0-9]'),
              '',
            );
        jobIdentifier = '${normalizedCompany}_${normalizedTitle}';
      }

      // Use the new SQLite database
      final db = JobDatabase();
      await db.saveJobResult(
        jobId: jobIdentifier,
        jobTitle: jobTitle,
        company: company,
        jdText: '', // JD text not stored in this simplified version
        testDate: DateTime.now(),
        atsScore: atsScore,
        cvName: 'Current CV',
        matchedSkills: matchedSkills,
        missedSkills: missedSkills,
        metadata: {'matchRate': matchRate ?? '', 'originalJobUrl': jobUrl},
        status: atsScore >= 70 ? 'completed' : 'needs_improvement',
      );

      debugPrint(
        '✅ ATS result saved to SQLite database: $jobTitle at $company',
      );
    } catch (e) {
      debugPrint('❌ Error saving ATS result to database: $e');
    }
  }
}

// Data Models for Professional ATS Tracking
class ATSJobResult {
  final String jobId;
  final String jobTitle;
  final String company;
  final String jdText;
  final DateTime testDate;
  final int atsScore;
  final String cvName;
  final List<String> matchedSkills;
  final List<String> missedSkills;
  final Map<String, dynamic> metadata;
  final String status;

  ATSJobResult({
    required this.jobId,
    required this.jobTitle,
    required this.company,
    required this.jdText,
    required this.testDate,
    required this.atsScore,
    required this.cvName,
    required this.matchedSkills,
    required this.missedSkills,
    required this.metadata,
    required this.status,
  });

  Color get scoreColor {
    if (atsScore >= 80) return AppTheme.successGreen;
    if (atsScore >= 60) return AppTheme.warningOrange;
    return AppTheme.errorRed;
  }

  String get scoreGrade {
    if (atsScore >= 90) return 'A+';
    if (atsScore >= 80) return 'A';
    if (atsScore >= 70) return 'B';
    if (atsScore >= 60) return 'C';
    return 'D';
  }

  Map<String, dynamic> toJson() => {
        'jobId': jobId,
        'jobTitle': jobTitle,
        'company': company,
        'jdText': jdText,
        'testDate': testDate.toIso8601String(),
        'atsScore': atsScore,
        'cvName': cvName,
        'matchedSkills': matchedSkills,
        'missedSkills': missedSkills,
        'metadata': metadata,
        'status': status,
      };

  factory ATSJobResult.fromJson(Map<String, dynamic> json) => ATSJobResult(
        jobId: json['jobId'],
        jobTitle: json['jobTitle'],
        company: json['company'],
        jdText: json['jdText'],
        testDate: DateTime.parse(json['testDate']),
        atsScore: json['atsScore'],
        cvName: json['cvName'],
        matchedSkills: List<String>.from(json['matchedSkills']),
        missedSkills: List<String>.from(json['missedSkills']),
        metadata: json['metadata'],
        status: json['status'],
      );
}

class _MultiJobATSDashboardState extends State<MultiJobATSDashboard>
    with TickerProviderStateMixin {
  List<ATSJobResult> _jobResults = [];
  bool _isLoading = true;
  late TabController _tabController;
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;
  String _sortBy = 'date';
  bool _sortAscending = false;

  // Cached Analytics (to prevent flickering from repeated calculations)
  double _cachedAverageScore = 0;
  ATSJobResult? _cachedTopJob;
  int _cachedTotalJobs = 0;
  int _cachedExcellentJobs = 0;
  int _cachedGoodJobs = 0;
  int _cachedNeedsImprovementJobs = 0;

  // Getters that use cached values (no recalculation on each build)
  double get _averageScore => _cachedAverageScore;
  ATSJobResult? get _topJob => _cachedTopJob;
  int get _totalJobs => _cachedTotalJobs;
  int get _excellentJobs => _cachedExcellentJobs;
  int get _goodJobs => _cachedGoodJobs;
  int get _needsImprovementJobs => _cachedNeedsImprovementJobs;

  // Method to update cached analytics (call only when data changes)
  void _updateCachedAnalytics() {
    _cachedTotalJobs = _jobResults.length;

    if (_jobResults.isEmpty) {
      _cachedAverageScore = 0;
      _cachedTopJob = null;
      _cachedExcellentJobs = 0;
      _cachedGoodJobs = 0;
      _cachedNeedsImprovementJobs = 0;
    } else {
      _cachedAverageScore =
          _jobResults.map((j) => j.atsScore).reduce((a, b) => a + b) /
              _jobResults.length;
      _cachedTopJob = _jobResults.reduce(
        (a, b) => a.atsScore > b.atsScore ? a : b,
      );
      _cachedExcellentJobs = _jobResults.where((j) => j.atsScore >= 80).length;
      _cachedGoodJobs =
          _jobResults.where((j) => j.atsScore >= 60 && j.atsScore < 80).length;
      _cachedNeedsImprovementJobs =
          _jobResults.where((j) => j.atsScore < 60).length;
    }
  }

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeOutBack),
    );
    _initializeDatabase();
  }

  Future<void> _initializeDatabase() async {
    // Initialize database and migrate data from SharedPreferences if needed
    final db = JobDatabase();
    await db.migrateFromSharedPreferences();
    await _loadJobResults();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _loadJobResults() async {
    setState(() => _isLoading = true);
    debugPrint('🔄 [DASHBOARD] Starting to load job results...');

    try {
      final db = JobDatabase();
      debugPrint('🔄 [DASHBOARD] Database instance created');

      final results = await db.getAllJobResults();
      debugPrint(
        '🔄 [DASHBOARD] Raw results from database: ${results.length} items',
      );

      if (results.isEmpty) {
        debugPrint('📭 [DASHBOARD] No results found in database');
      } else {
        debugPrint('📊 [DASHBOARD] First result sample: ${results.first}');
      }

      // Convert database results to ATSJobResult objects
      _jobResults = results.map((data) {
        debugPrint(
          '🔄 [DASHBOARD] Converting data: ${data['jobTitle']} at ${data['company']}',
        );
        return ATSJobResult(
          jobId: data['jobId'],
          jobTitle: data['jobTitle'],
          company: data['company'],
          jdText: data['jdText'],
          testDate: DateTime.parse(data['testDate']),
          atsScore: data['atsScore'],
          cvName: data['cvName'],
          matchedSkills: List<String>.from(data['matchedSkills']),
          missedSkills: List<String>.from(data['missedSkills']),
          metadata: data['metadata'],
          status: data['status'],
        );
      }).toList();

      _sortJobResults();
      _updateCachedAnalytics(); // Update cached analytics after loading data
      debugPrint(
        '✅ [DASHBOARD] Loaded ${_jobResults.length} job results from database',
      );

      if (_jobResults.isNotEmpty) {
        debugPrint(
          '✅ [DASHBOARD] Sample loaded job: ${_jobResults.first.jobTitle} at ${_jobResults.first.company}, Score: ${_jobResults.first.atsScore}',
        );
      }
    } catch (e) {
      debugPrint('❌ [DASHBOARD] Error loading job results from database: $e');
      debugPrint('❌ [DASHBOARD] Stack trace: ${StackTrace.current}');
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
        // Start the stunning entrance animation
        _animationController.forward();
      }
    }
  }

  void _sortJobResults() {
    switch (_sortBy) {
      case 'score':
        _jobResults.sort(
          (a, b) => _sortAscending
              ? a.atsScore.compareTo(b.atsScore)
              : b.atsScore.compareTo(a.atsScore),
        );
        break;
      case 'company':
        _jobResults.sort(
          (a, b) => _sortAscending
              ? a.company.compareTo(b.company)
              : b.company.compareTo(a.company),
        );
        break;
      case 'date':
      default:
        _jobResults.sort(
          (a, b) => _sortAscending
              ? a.testDate.compareTo(b.testDate)
              : b.testDate.compareTo(a.testDate),
        );
        break;
    }
    // Note: No need to update cached analytics here since sorting doesn't change the data values
  }

  Future<void> _showClearConfirmation() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: Row(
          children: [
            Icon(
              Icons.warning_amber_rounded,
              color: Colors.orange.shade600,
            ),
            const SizedBox(width: 8),
            const Text('Clear All Results?'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'This will permanently delete all ATS test results from your job dashboard.',
            ),
            const SizedBox(height: 12),
            Text(
              '${_jobResults.length} job results will be deleted.',
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            const Text(
              'This action cannot be undone.',
              style: TextStyle(
                color: Colors.red,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('Clear All'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await _clearAllResults();
    }
  }

  Future<void> _clearAllResults() async {
    try {
      setState(() => _isLoading = true);

      final resultsCount = _jobResults.length;

      // Clear all data from SQLite database
      final db = JobDatabase();
      await db.clearAllJobResults();

      // Clear the local list and update analytics
      setState(() {
        _jobResults.clear();
        _updateCachedAnalytics(); // Update cached analytics after clearing
      });

      debugPrint('✅ Cleared all $resultsCount job results from database');

      // Show success message
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('✅ All job results cleared successfully!'),
            backgroundColor: Colors.green,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        );
      }
    } catch (e) {
      debugPrint('❌ Error clearing job results: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Failed to clear results: $e'),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        backgroundColor: AppTheme.neutralGray50,
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.primaryCosmic.withOpacity(0.2),
                      blurRadius: 20,
                      offset: const Offset(0, 10),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    CircularProgressIndicator(
                      valueColor:
                          AlwaysStoppedAnimation<Color>(AppTheme.primaryCosmic),
                      strokeWidth: 3,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Loading Dashboard...',
                      style: AppTheme.bodyLarge.copyWith(
                        color: AppTheme.neutralGray600,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      body: FadeTransition(
        opacity: _fadeAnimation,
        child: SlideTransition(
          position: _slideAnimation,
          child: Column(
            children: [
              Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      AppTheme.primaryCosmic,
                      AppTheme.secondaryBlue,
                      AppTheme.primaryTeal,
                    ],
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.primaryCosmic.withOpacity(0.3),
                      blurRadius: 20,
                      offset: const Offset(0, 10),
                    ),
                  ],
                ),
                child: SafeArea(
                  bottom: false,
                  child: LayoutBuilder(
                    builder: (context, constraints) {
                      final isMobile = constraints.maxWidth < 600;
                      return Padding(
                        padding: EdgeInsets.symmetric(
                          horizontal: isMobile ? 16 : 24,
                          vertical: isMobile ? 12 : 20,
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.all(12),
                                  decoration: BoxDecoration(
                                    color: Colors.white.withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(16),
                                  ),
                                  child: Icon(
                                    Icons.dashboard_rounded,
                                    color: Colors.white,
                                    size: isMobile ? 24 : 28,
                                  ),
                                ),
                                const SizedBox(width: 16),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'Multi-Job ATS Dashboard',
                                        style: AppTheme.headingLarge.copyWith(
                                          color: Colors.white,
                                          fontSize: isMobile ? 20 : 28,
                                          fontWeight: FontWeight.bold,
                                          letterSpacing: -0.5,
                                        ),
                                        overflow: TextOverflow.ellipsis,
                                        maxLines: 1,
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        'Track your ATS performance across all applications',
                                        style: AppTheme.bodyMedium.copyWith(
                                          color: Colors.white.withOpacity(0.9),
                                          fontSize: isMobile ? 12 : 14,
                                        ),
                                        overflow: TextOverflow.ellipsis,
                                        maxLines: isMobile ? 2 : 1,
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 20),
                            _buildEnhancedTabBar(isMobile),
                          ],
                        ),
                      );
                    },
                  ),
                ),
              ),
              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildOverviewTab(),
                    _buildJobsListTab(),
                    _buildAnalyticsTab(),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: _buildFloatingActionButton(),
    );
  }

  Widget _buildEnhancedTabBar(bool isMobile) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.15),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.white.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: TabBar(
        controller: _tabController,
        labelColor: Colors.white,
        unselectedLabelColor: Colors.white.withOpacity(0.6),
        labelStyle: AppTheme.buttonMedium.copyWith(
          fontWeight: FontWeight.w600,
          fontSize: isMobile ? 12 : 14,
        ),
        unselectedLabelStyle: AppTheme.buttonMedium.copyWith(
          fontWeight: FontWeight.w500,
          fontSize: isMobile ? 12 : 14,
        ),
        indicator: BoxDecoration(
          color: Colors.white.withOpacity(0.25),
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        indicatorSize: TabBarIndicatorSize.tab,
        tabs: [
          Tab(
            icon: Icon(Icons.dashboard_rounded, size: isMobile ? 18 : 20),
            text: 'Overview',
            height: isMobile ? 48 : 56,
          ),
          Tab(
            icon: Icon(Icons.list_alt_rounded, size: isMobile ? 18 : 20),
            text: 'Jobs List',
            height: isMobile ? 48 : 56,
          ),
          Tab(
            icon: Icon(Icons.analytics_rounded, size: isMobile ? 18 : 20),
            text: 'Analytics',
            height: isMobile ? 48 : 56,
          ),
        ],
      ),
    );
  }

  Widget _buildFloatingActionButton() {
    return TweenAnimationBuilder<double>(
      duration: const Duration(milliseconds: 600),
      tween: Tween(begin: 0.0, end: 1.0),
      builder: (context, value, child) {
        return Transform.scale(
          scale: value,
          child: FloatingActionButton.extended(
            onPressed: () => Navigator.pop(context),
            backgroundColor: AppTheme.primaryCosmic,
            foregroundColor: Colors.white,
            icon: const Icon(Icons.arrow_back_rounded),
            label: Text(
              'Back to ATS',
              style: AppTheme.buttonMedium.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            elevation: 12,
            extendedPadding: const EdgeInsets.symmetric(horizontal: 20),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(28),
            ),
          ),
        );
      },
    );
  }

  Widget _buildCompactQuickStats() {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isMobile = constraints.maxWidth < 600;

        if (isMobile) {
          // Mobile: Stack in 2+1 layout for better readability
          return Column(
            children: [
              Row(
                children: [
                  Expanded(
                    child: _buildCompactStatCard(
                      'Total Jobs',
                      _totalJobs.toString(),
                      Icons.work_rounded,
                      AppTheme.primaryTeal,
                      isCompact: true,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _buildCompactStatCard(
                      'Avg Score',
                      '${_averageScore.round()}%',
                      Icons.analytics_rounded,
                      AppTheme.secondaryBlue,
                      isCompact: true,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              _buildCompactStatCard(
                'Top Score',
                _topJob != null ? '${_topJob!.atsScore}%' : '0%',
                Icons.star_rounded,
                AppTheme.primaryCosmic,
                isCompact: false,
              ),
            ],
          );
        } else {
          // Desktop: Keep horizontal layout
          return Row(
            children: [
              Expanded(
                child: _buildCompactStatCard(
                  'Total Jobs',
                  _totalJobs.toString(),
                  Icons.work_rounded,
                  AppTheme.primaryTeal,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildCompactStatCard(
                  'Avg Score',
                  '${_averageScore.round()}%',
                  Icons.analytics_rounded,
                  AppTheme.secondaryBlue,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildCompactStatCard(
                  'Top Score',
                  _topJob != null ? '${_topJob!.atsScore}%' : '0%',
                  Icons.star_rounded,
                  AppTheme.primaryCosmic,
                ),
              ),
            ],
          );
        }
      },
    );
  }

  Widget _buildCompactStatCard(
    String label,
    String value,
    IconData icon,
    Color color, {
    bool isCompact = false,
  }) {
    return Container(
      padding: EdgeInsets.all(isCompact ? 12 : 16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: AppTheme.cardRadius,
        border: Border.all(color: color.withOpacity(0.2), width: 1),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: isCompact ? 20 : 24),
          SizedBox(height: isCompact ? 6 : 8),
          Text(
            value,
            style: AppTheme.headingMedium.copyWith(
              color: color,
              fontSize: isCompact ? 16 : 18,
            ),
            overflow: TextOverflow.ellipsis,
            maxLines: 1,
          ),
          SizedBox(height: isCompact ? 2 : 4),
          Text(
            label,
            style: AppTheme.bodySmall.copyWith(
              color: AppTheme.neutralGray600,
              fontSize: isCompact ? 11 : 12,
            ),
            overflow: TextOverflow.ellipsis,
            maxLines: 1,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildQuickStats() {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            'Total Jobs',
            _totalJobs.toString(),
            Icons.work,
            Colors.white.withOpacity(0.15),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'Avg Score',
            '${_averageScore.round()}%',
            Icons.analytics,
            Colors.white.withOpacity(0.15),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'Top Score',
            _topJob != null ? '${_topJob!.atsScore}%' : '0%',
            Icons.star,
            Colors.white.withOpacity(0.15),
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard(
    String label,
    String value,
    IconData icon,
    Color bgColor,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: AppTheme.cardRadius,
        border: Border.all(color: Colors.white.withOpacity(0.2), width: 1),
      ),
      child: Column(
        children: [
          Icon(icon, color: Colors.white, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: AppTheme.headingMedium.copyWith(
              color: Colors.white,
              fontSize: 20,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: AppTheme.bodySmall.copyWith(
              color: Colors.white.withOpacity(0.8),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTabBar() {
    return Container(
      decoration: BoxDecoration(
        gradient: AppTheme.primaryGradient,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: TabBar(
        controller: _tabController,
        labelColor: Colors.white,
        unselectedLabelColor: Colors.white.withOpacity(0.7),
        labelStyle: AppTheme.buttonMedium.copyWith(fontWeight: FontWeight.w600),
        unselectedLabelStyle: AppTheme.buttonMedium.copyWith(
          fontWeight: FontWeight.w500,
        ),
        indicatorColor: Colors.white,
        indicatorWeight: 3,
        indicatorSize: TabBarIndicatorSize.tab,
        tabs: const [
          Tab(icon: Icon(Icons.dashboard_rounded), text: 'Overview'),
          Tab(icon: Icon(Icons.list_alt_rounded), text: 'Jobs List'),
          Tab(icon: Icon(Icons.analytics_rounded), text: 'Analytics'),
        ],
      ),
    );
  }

  Widget _buildOverviewTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 100),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildCompactQuickStats(),
          const SizedBox(height: 20),
          _buildPerformanceOverview(),
          const SizedBox(height: 20),
          _buildRecentJobs(),
          const SizedBox(height: 20),
          _buildQuickInsights(),
        ],
      ),
    );
  }

  Widget _buildPerformanceOverview() {
    return AppTheme.createCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.trending_up, color: AppTheme.primaryCosmic, size: 24),
              const SizedBox(width: 12),
              Text('Performance Overview', style: AppTheme.headingMedium),
            ],
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Expanded(
                child: _buildPerformanceCard(
                  'Excellent',
                  _excellentJobs,
                  AppTheme.successGreen,
                  '80%+',
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildPerformanceCard(
                  'Good',
                  _goodJobs,
                  AppTheme.warningOrange,
                  '60-79%',
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildPerformanceCard(
                  'Needs Work',
                  _needsImprovementJobs,
                  AppTheme.errorRed,
                  '<60%',
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPerformanceCard(
    String label,
    int count,
    Color color,
    String range,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: AppTheme.cardRadius,
        border: Border.all(color: color.withOpacity(0.2), width: 1),
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
            child: Text(
              count.toString(),
              style: AppTheme.headingSmall.copyWith(
                color: Colors.white,
                fontSize: 16,
              ),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: AppTheme.bodyMedium.copyWith(
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
          Text(range, style: AppTheme.bodySmall.copyWith(color: color)),
        ],
      ),
    );
  }

  Widget _buildRecentJobs() {
    final recentJobs = _jobResults.take(5).toList();

    return AppTheme.createCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.schedule_rounded,
                color: AppTheme.primaryCosmic,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text('Recent Jobs', style: AppTheme.headingMedium),
              const Spacer(),
              TextButton(
                onPressed: () => _tabController.animateTo(1),
                child: Text(
                  'View All',
                  style: AppTheme.bodyMedium.copyWith(
                    color: AppTheme.primaryCosmic,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (recentJobs.isEmpty)
            Center(
              child: Column(
                children: [
                  Icon(
                    Icons.work_off_rounded,
                    size: 48,
                    color: AppTheme.neutralGray400,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'No ATS tests yet',
                    style: AppTheme.bodyLarge.copyWith(
                      color: AppTheme.neutralGray500,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Run your first ATS test to see data here',
                    style: AppTheme.bodyMedium,
                  ),
                ],
              ),
            )
          else
            ...recentJobs.map((job) => _buildJobCard(job)),
        ],
      ),
    );
  }

  Widget _buildJobCard(ATSJobResult job) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.neutralGray50,
        borderRadius: AppTheme.cardRadius,
        border: Border.all(color: AppTheme.neutralGray200, width: 1),
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final isNarrow = constraints.maxWidth < 400;

          if (isNarrow) {
            // Mobile: Stack vertically to prevent overflow
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: job.scoreColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Center(
                        child: Text(
                          '${job.atsScore}%',
                          style: AppTheme.bodySmall.copyWith(
                            color: job.scoreColor,
                            fontWeight: FontWeight.bold,
                            fontSize: 11,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            job.jobTitle,
                            style: AppTheme.bodyMedium.copyWith(
                              fontWeight: FontWeight.w600,
                              fontSize: 14,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 2),
                          Text(
                            job.company,
                            style: AppTheme.bodySmall.copyWith(
                              fontSize: 12,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: job.scoreColor,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        job.scoreGrade,
                        style: AppTheme.bodySmall.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 10,
                        ),
                      ),
                    ),
                    Text(
                      DateFormat('MMM dd').format(job.testDate),
                      style: AppTheme.bodySmall.copyWith(fontSize: 11),
                    ),
                  ],
                ),
              ],
            );
          } else {
            // Desktop: Use horizontal layout with proper constraints
            return Row(
              children: [
                Container(
                  width: 50,
                  height: 50,
                  decoration: BoxDecoration(
                    color: job.scoreColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Center(
                    child: Text(
                      '${job.atsScore}%',
                      style: AppTheme.bodyMedium.copyWith(
                        color: job.scoreColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        job.jobTitle,
                        style: AppTheme.bodyLarge.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        job.company,
                        style: AppTheme.bodyMedium,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                // Constrain the right column to prevent overflow
                SizedBox(
                  width: 80, // Fixed width to prevent overflow
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 6, vertical: 3),
                        decoration: BoxDecoration(
                          color: job.scoreColor,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Text(
                          job.scoreGrade,
                          style: AppTheme.bodySmall.copyWith(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 11,
                          ),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        DateFormat('MMM dd').format(job.testDate),
                        style: AppTheme.bodySmall.copyWith(fontSize: 11),
                        overflow: TextOverflow.ellipsis,
                        maxLines: 1,
                      ),
                    ],
                  ),
                ),
              ],
            );
          }
        },
      ),
    );
  }

  Widget _buildQuickInsights() {
    if (_jobResults.isEmpty) return const SizedBox.shrink();

    final topSkills = <String, int>{};
    for (final job in _jobResults) {
      for (final skill in job.matchedSkills) {
        topSkills[skill] = (topSkills[skill] ?? 0) + 1;
      }
    }

    final sortedSkills = topSkills.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    return AppTheme.createCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.lightbulb_rounded,
                color: AppTheme.primaryCosmic,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text('Quick Insights', style: AppTheme.headingMedium),
            ],
          ),
          const SizedBox(height: 16),
          _buildInsightItem(
            'Average ATS Score',
            '${_averageScore.round()}%',
            _averageScore >= 70 ? Icons.trending_up : Icons.trending_down,
            _averageScore >= 70 ? AppTheme.successGreen : AppTheme.errorRed,
          ),
          const SizedBox(height: 12),
          _buildInsightItem(
            'Top Performing Skill',
            sortedSkills.isNotEmpty ? sortedSkills.first.key : 'None',
            Icons.star_rounded,
            AppTheme.warningOrange,
          ),
          const SizedBox(height: 12),
          _buildInsightItem(
            'Total Applications',
            _totalJobs.toString(),
            Icons.work_rounded,
            AppTheme.primaryCosmic,
          ),
        ],
      ),
    );
  }

  Widget _buildInsightItem(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: color, size: 20),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: AppTheme.bodyMedium),
              Text(
                value,
                style: AppTheme.bodyLarge.copyWith(
                  fontWeight: FontWeight.w600,
                  color: color,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildJobsListTab() {
    return Column(
      children: [
        _buildJobsHeader(),
        Expanded(
          child: _jobResults.isEmpty
              ? _buildEmptyState()
              : ListView.builder(
                  padding: const EdgeInsets.fromLTRB(20, 20, 20, 100),
                  itemCount: _jobResults.length,
                  itemBuilder: (context, index) =>
                      _buildDetailedJobCard(_jobResults[index]),
                ),
        ),
      ],
    );
  }

  Widget _buildJobsHeader() {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          Text('Sort by:', style: AppTheme.bodyMedium),
          const SizedBox(width: 12),
          _buildSortChip('Date', 'date'),
          const SizedBox(width: 8),
          _buildSortChip('Score', 'score'),
          const SizedBox(width: 8),
          _buildSortChip('Company', 'company'),
          const Spacer(),
          IconButton(
            onPressed: () {
              setState(() {
                _sortAscending = !_sortAscending;
              });
              _sortJobResults();
            },
            icon: Icon(
              _sortAscending ? Icons.arrow_upward : Icons.arrow_downward,
              color: AppTheme.primaryCosmic,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSortChip(String label, String sortType) {
    final isSelected = _sortBy == sortType;
    return GestureDetector(
      onTap: () {
        setState(() {
          _sortBy = sortType;
        });
        _sortJobResults();
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? AppTheme.primaryCosmic : AppTheme.neutralGray100,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          label,
          style: AppTheme.bodySmall.copyWith(
            color: isSelected ? Colors.white : AppTheme.neutralGray600,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }

  Widget _buildDetailedJobCard(ATSJobResult job) {
    return AppTheme.createCard(
      margin: const EdgeInsets.only(bottom: 16),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final isMobile = constraints.maxWidth < 600;

          if (isMobile) {
            // Mobile: Stack vertically for better space usage
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Job title and company
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      job.jobTitle,
                      style: AppTheme.headingSmall.copyWith(fontSize: 16),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      job.company,
                      style: AppTheme.bodyMedium.copyWith(
                        color: AppTheme.neutralGray600,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // Score badge - centered
                Center(
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 10,
                    ),
                    decoration: BoxDecoration(
                      color: job.scoreColor,
                      borderRadius: BorderRadius.circular(25),
                      boxShadow: [
                        BoxShadow(
                          color: job.scoreColor.withOpacity(0.3),
                          blurRadius: 8,
                          offset: const Offset(0, 3),
                        ),
                      ],
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          '${job.atsScore}%',
                          style: AppTheme.headingSmall.copyWith(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            job.scoreGrade,
                            style: AppTheme.bodySmall.copyWith(
                              color: Colors.white,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 12),

                // Skills and test date
                Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        Flexible(
                          child: _buildSkillChip(
                            '${job.matchedSkills.length} Matched',
                            AppTheme.successGreen,
                            isCompact: true,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Flexible(
                          child: _buildSkillChip(
                            '${job.missedSkills.length} Missed',
                            AppTheme.errorRed,
                            isCompact: true,
                          ),
                        ),
                      ],
                    ),
                    if (job.metadata['totalTests'] != null &&
                        job.metadata['totalTests'] > 1) ...[
                      const SizedBox(height: 8),
                      _buildSkillChip(
                        '${job.metadata['totalTests']} tests',
                        AppTheme.primaryCosmic,
                        isCompact: true,
                      ),
                    ],
                    const SizedBox(height: 8),
                    Text(
                      DateFormat('MMM dd, yyyy').format(job.testDate),
                      style: AppTheme.bodySmall.copyWith(
                        color: AppTheme.neutralGray500,
                      ),
                    ),
                  ],
                ),
              ],
            );
          } else {
            // Desktop: Keep horizontal layout
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            job.jobTitle,
                            style: AppTheme.headingSmall,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            job.company,
                            style: AppTheme.bodyMedium,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: job.scoreColor,
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color: job.scoreColor.withOpacity(0.3),
                            blurRadius: 8,
                            offset: const Offset(0, 3),
                          ),
                        ],
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            '${job.atsScore}%',
                            style: AppTheme.bodyLarge.copyWith(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            job.scoreGrade,
                            style: AppTheme.bodySmall.copyWith(
                              color: Colors.white,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    _buildSkillChip(
                      '${job.matchedSkills.length} Matched',
                      AppTheme.successGreen,
                    ),
                    const SizedBox(width: 8),
                    _buildSkillChip(
                      '${job.missedSkills.length} Missed',
                      AppTheme.errorRed,
                    ),
                    if (job.metadata['totalTests'] != null &&
                        job.metadata['totalTests'] > 1) ...[
                      const SizedBox(width: 8),
                      _buildSkillChip(
                        '${job.metadata['totalTests']} tests',
                        AppTheme.primaryCosmic,
                      ),
                    ],
                    const Spacer(),
                    Text(
                      DateFormat('MMM dd, yyyy').format(job.testDate),
                      style: AppTheme.bodySmall,
                    ),
                  ],
                ),
              ],
            );
          }
        },
      ),
    );
  }

  Widget _buildSkillChip(String label, Color color, {bool isCompact = false}) {
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: isCompact ? 6 : 8,
        vertical: isCompact ? 3 : 4,
      ),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3), width: 1),
      ),
      child: Text(
        label,
        style: AppTheme.bodySmall.copyWith(
          color: color,
          fontWeight: FontWeight.w600,
          fontSize: isCompact ? 10 : 12,
        ),
        overflow: TextOverflow.ellipsis,
        maxLines: 1,
        textAlign: TextAlign.center,
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 100),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppTheme.primaryCosmic.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.analytics_rounded,
                size: 48,
                color: AppTheme.primaryCosmic,
              ),
            ),
            const SizedBox(height: 16),
            Text('No ATS Data Yet', style: AppTheme.headingMedium),
            const SizedBox(height: 8),
            Text(
              'Run ATS tests on job descriptions to start tracking your performance across multiple applications.',
              style: AppTheme.bodyMedium,
              textAlign: TextAlign.center,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalyticsTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 100),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSkillsAnalysis(),
          const SizedBox(height: 20),
          _buildCompanyPerformance(),
          const SizedBox(height: 20),
          _buildTrendAnalysis(),
        ],
      ),
    );
  }

  Widget _buildSkillsAnalysis() {
    final allMatchedSkills = <String, int>{};
    final allMissedSkills = <String, int>{};

    for (final job in _jobResults) {
      for (final skill in job.matchedSkills) {
        allMatchedSkills[skill] = (allMatchedSkills[skill] ?? 0) + 1;
      }
      for (final skill in job.missedSkills) {
        allMissedSkills[skill] = (allMissedSkills[skill] ?? 0) + 1;
      }
    }

    final topMatched = allMatchedSkills.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    final topMissed = allMissedSkills.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    return AppTheme.createCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.psychology_rounded,
                color: AppTheme.primaryCosmic,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text('Skills Analysis', style: AppTheme.headingMedium),
            ],
          ),
          const SizedBox(height: 20),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Most Matched Skills',
                      style: AppTheme.bodyLarge.copyWith(
                        fontWeight: FontWeight.w600,
                        color: AppTheme.successGreen,
                      ),
                    ),
                    const SizedBox(height: 12),
                    ...topMatched.take(5).map(
                          (entry) => _buildSkillAnalysisItem(
                            entry.key,
                            entry.value,
                            AppTheme.successGreen,
                          ),
                        ),
                  ],
                ),
              ),
              const SizedBox(width: 20),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Most Missed Skills',
                      style: AppTheme.bodyLarge.copyWith(
                        fontWeight: FontWeight.w600,
                        color: AppTheme.errorRed,
                      ),
                    ),
                    const SizedBox(height: 12),
                    ...topMissed.take(5).map(
                          (entry) => _buildSkillAnalysisItem(
                            entry.key,
                            entry.value,
                            AppTheme.errorRed,
                          ),
                        ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSkillAnalysisItem(String skill, int count, Color color) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.05),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.2), width: 1),
      ),
      child: Row(
        children: [
          Expanded(
            child: Text(
              skill,
              style: AppTheme.bodyMedium.copyWith(fontWeight: FontWeight.w500),
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              '${count}x',
              style: AppTheme.bodySmall.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCompanyPerformance() {
    final companyScores = <String, List<int>>{};

    for (final job in _jobResults) {
      if (!companyScores.containsKey(job.company)) {
        companyScores[job.company] = [];
      }
      companyScores[job.company]!.add(job.atsScore);
    }

    final companyAverages = companyScores.entries.map((entry) {
      final average = entry.value.reduce((a, b) => a + b) / entry.value.length;
      return MapEntry(entry.key, average);
    }).toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    return AppTheme.createCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.business_rounded,
                color: AppTheme.primaryCosmic,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text('Company Performance', style: AppTheme.headingMedium),
            ],
          ),
          const SizedBox(height: 20),
          if (companyAverages.isEmpty)
            Center(
              child: Text(
                'No company data available',
                style: AppTheme.bodyMedium.copyWith(
                  color: AppTheme.neutralGray500,
                ),
              ),
            )
          else
            ...companyAverages.take(5).map(
                  (entry) => Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppTheme.neutralGray50,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: AppTheme.neutralGray200,
                        width: 1,
                      ),
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Text(
                            entry.key,
                            style: AppTheme.bodyLarge.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 6,
                          ),
                          decoration: BoxDecoration(
                            color: _getScoreColor(entry.value.round()),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            '${entry.value.toStringAsFixed(1)}%',
                            style: AppTheme.bodyMedium.copyWith(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
        ],
      ),
    );
  }

  Widget _buildTrendAnalysis() {
    return AppTheme.createCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.timeline_rounded,
                color: AppTheme.primaryCosmic,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text('Performance Trends', style: AppTheme.headingMedium),
            ],
          ),
          const SizedBox(height: 20),
          if (_jobResults.length < 2)
            Center(
              child: Text(
                'Need at least 2 job tests to show trends',
                style: AppTheme.bodyMedium.copyWith(
                  color: AppTheme.neutralGray500,
                ),
              ),
            )
          else
            Column(
              children: [
                _buildTrendItem(
                  'Improvement Rate',
                  _calculateImprovementRate(),
                  Icons.trending_up_rounded,
                ),
                const SizedBox(height: 16),
                _buildTrendItem(
                  'Consistency Score',
                  _calculateConsistencyScore(),
                  Icons.analytics_rounded,
                ),
                const SizedBox(height: 16),
                _buildTrendItem(
                  'Application Frequency',
                  '${(_jobResults.length / 30).toStringAsFixed(1)} per month',
                  Icons.schedule_rounded,
                ),
              ],
            ),
        ],
      ),
    );
  }

  String _calculateImprovementRate() {
    if (_jobResults.length < 2) return '0%';

    final sortedByDate = [..._jobResults]
      ..sort((a, b) => a.testDate.compareTo(b.testDate));
    final firstScore = sortedByDate.first.atsScore;
    final lastScore = sortedByDate.last.atsScore;
    final improvement = lastScore - firstScore;

    return improvement >= 0 ? '+${improvement}%' : '${improvement}%';
  }

  String _calculateConsistencyScore() {
    if (_jobResults.isEmpty) return '0%';

    final scores = _jobResults.map((j) => j.atsScore).toList();
    final mean = scores.reduce((a, b) => a + b) / scores.length;
    final variance =
        scores.map((s) => (s - mean) * (s - mean)).reduce((a, b) => a + b) /
            scores.length;
    final consistency = (100 - variance).clamp(0, 100);

    return '${consistency.round()}%';
  }

  Widget _buildTrendItem(String label, String value, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.primaryCosmic.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: AppTheme.primaryCosmic.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppTheme.primaryCosmic,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: Colors.white, size: 20),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              label,
              style: AppTheme.bodyLarge.copyWith(fontWeight: FontWeight.w600),
            ),
          ),
          Text(
            value,
            style: AppTheme.bodyLarge.copyWith(
              color: AppTheme.primaryCosmic,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Color _getScoreColor(int score) => ATSHelpers.getScoreColor(score);

  /// Clean up legacy data and migrate to new consistent identifier system
  // Legacy cleanup method removed - migration now handled by JobDatabase
}
