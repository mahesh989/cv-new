///
/// Job Tracking Screen
///
/// A modular, dynamic, structured, and reusable job tracking interface
/// that follows the existing design patterns and maintains consistency
/// with other tabs in the application.
///

import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/saved_jobs_service.dart';
import '../widgets/job_tracking/saved_jobs_table_final.dart';
import '../core/theme/app_theme.dart';

class JobTrackingScreen extends StatefulWidget {
  final VoidCallback? onRefreshRequested;

  const JobTrackingScreen({super.key, this.onRefreshRequested});

  @override
  State<JobTrackingScreen> createState() => JobTrackingScreenState();
}

class JobTrackingScreenState extends State<JobTrackingScreen>
    with AutomaticKeepAliveClientMixin {
  List<Map<String, dynamic>> _jobs = [];
  bool _isLoading = true;
  String? _error;
  bool _showAppliedJobs = false; // Toggle for showing applied jobs only
  final Map<String, bool> _appliedStatus =
      {}; // Track applied status for each job
  bool _hasCachedData = false; // Track if we have cached data to show

  /// Public method to trigger refresh from external sources
  void refreshJobs() {
    debugPrint('🔄 [JOB_TRACKING] External refresh triggered');
    _loadJobs();
  }

  @override
  void initState() {
    super.initState();
    _verifyAssets();
    _loadJobs();
    _loadAppliedStatus();
  }

  Future<void> _verifyAssets() async {
    try {
      debugPrint('🔍 [JOB_TRACKING] Verifying assets...');
      final manifestContent =
          await DefaultAssetBundle.of(context).loadString('AssetManifest.json');
      final Map<String, dynamic> manifestMap = json.decode(manifestContent);

      if (manifestMap.containsKey('assets/saved_jobs.json')) {
        debugPrint('✅ [JOB_TRACKING] Found saved_jobs.json in asset manifest');
      } else {
        debugPrint(
            '❌ [JOB_TRACKING] saved_jobs.json not found in asset manifest!');
      }
    } catch (e) {
      debugPrint('⚠️ [JOB_TRACKING] Error verifying assets: $e');
    }
  }

  Future<void> _loadJobs() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      debugPrint('🔄 [JOB_TRACKING] Loading saved jobs...');
      final jobs = await SavedJobsService.loadSavedJobs();
      debugPrint('✅ [JOB_TRACKING] Successfully loaded ${jobs.length} jobs');
      setState(() {
        _jobs = jobs;
        _isLoading = false;
        _hasCachedData = jobs.isNotEmpty;
      });
      // Load applied status after jobs are loaded
      await _loadAppliedStatus();
    } catch (e, stackTrace) {
      debugPrint('❌ [JOB_TRACKING] Error loading jobs: $e');
      debugPrint('📋 [JOB_TRACKING] Stack trace: $stackTrace');

      // If we have cached data, show it instead of error
      if (_hasCachedData && _jobs.isNotEmpty) {
        debugPrint('📋 [JOB_TRACKING] Showing cached data due to API error');
        setState(() {
          _isLoading = false;
          _error = null; // Don't show error if we have cached data
        });
      } else {
        setState(() {
          _error = 'Failed to load saved jobs: $e';
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _loadAppliedStatus() async {
    try {
      debugPrint(
          '🔄 [JOB_TRACKING] Loading applied status from SharedPreferences...');
      final prefs = await SharedPreferences.getInstance();

      // Load applied status for each job
      for (var job in _jobs) {
        final key = _getJobKey(job);
        final isApplied = prefs.getBool('applied_$key') ?? false;
        _appliedStatus[key] = isApplied;
        debugPrint(
            '📋 [JOB_TRACKING] Job ${job['company_name']}: applied = $isApplied');
      }

      debugPrint(
          '✅ [JOB_TRACKING] Loaded applied status for ${_appliedStatus.length} jobs');

      // Trigger UI update if we're showing applied jobs
      if (_showAppliedJobs) {
        setState(() {
          // This will trigger a rebuild to show updated applied jobs
        });
      }
    } catch (e) {
      debugPrint('❌ [JOB_TRACKING] Error loading applied status: $e');
    }
  }

  @override
  bool get wantKeepAlive => true;

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return Scaffold(
      backgroundColor: AppTheme.neutralGray50,
      body: SafeArea(
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          child: _buildContent(),
        ),
      ),
    );
  }

  Widget _buildContent() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 16),
          _buildErrorCard(_error!),
        ],
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildHeader(),
        const SizedBox(height: 16),
        _buildTableContent(),
      ],
    );
  }

  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(
              Icons.work_outline,
              color: AppTheme.primaryTeal,
            ),
            const SizedBox(width: 8),
            Text(
              'Saved Jobs',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray800,
                  ),
            ),
            // Show indicator when using cached data
            if (_hasCachedData && _jobs.isNotEmpty) ...[
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.orange.withOpacity(0.3)),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.cached,
                      size: 12,
                      color: Colors.orange.shade700,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      'Cached',
                      style: TextStyle(
                        fontSize: 10,
                        color: Colors.orange.shade700,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ],
            const Spacer(),
            IconButton(
              onPressed: _loadJobs,
              icon: const Icon(Icons.refresh),
              tooltip: 'Reload',
            ),
          ],
        ),
        const SizedBox(height: 12),
        // Toggle buttons for All Jobs vs Applied Jobs
        Row(
          children: [
            _buildToggleButton(
              label: 'All Jobs',
              isSelected: !_showAppliedJobs,
              onTap: () => setState(() => _showAppliedJobs = false),
              icon: Icons.list_alt,
            ),
            const SizedBox(width: 12),
            _buildToggleButton(
              label: 'Applied Jobs',
              isSelected: _showAppliedJobs,
              onTap: () => setState(() => _showAppliedJobs = true),
              icon: Icons.check_circle_outline,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildToggleButton({
    required String label,
    required bool isSelected,
    required VoidCallback onTap,
    required IconData icon,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? AppTheme.primaryTeal : Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? AppTheme.primaryTeal : AppTheme.neutralGray300,
            width: 1,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 16,
              color: isSelected ? Colors.white : AppTheme.neutralGray600,
            ),
            const SizedBox(width: 6),
            Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: isSelected ? Colors.white : AppTheme.neutralGray700,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTableContent() {
    if (_showAppliedJobs) {
      // Show only applied jobs
      final appliedJobs = _getAppliedJobs();
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Applied Jobs (${appliedJobs.length})',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppTheme.neutralGray800,
                ),
          ),
          const SizedBox(height: 12),
          if (appliedJobs.isEmpty)
            _buildEmptyAppliedJobsState()
          else
            SavedJobsTable(
              jobs: appliedJobs,
              onAppliedStatusChanged: _onAppliedStatusChanged,
            ),
        ],
      );
    } else {
      // Show all jobs
      return SavedJobsTable(
        jobs: _jobs,
        onAppliedStatusChanged: _onAppliedStatusChanged,
      );
    }
  }

  List<Map<String, dynamic>> _getAppliedJobs() {
    // Filter jobs where the applied status is true
    return _jobs.where((job) {
      final key = _getJobKey(job);
      return _appliedStatus[key] ?? false;
    }).toList();
  }

  String _getJobKey(Map<String, dynamic> job) {
    return '${job['company_name']}_${job['job_url']}';
  }

  void _onAppliedStatusChanged(Map<String, dynamic> job, bool isApplied) {
    final key = _getJobKey(job);
    setState(() {
      _appliedStatus[key] = isApplied;
    });
    debugPrint(
        '🔄 [JOB_TRACKING] Applied status changed for ${job['company_name']}: $isApplied');
  }

  Widget _buildEmptyAppliedJobsState() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppTheme.neutralGray50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.neutralGray200),
      ),
      child: Column(
        children: [
          Icon(
            Icons.check_circle_outline,
            size: 48,
            color: AppTheme.neutralGray400,
          ),
          const SizedBox(height: 12),
          Text(
            'No Applied Jobs Yet',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppTheme.neutralGray600,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Toggle "Already Applied?" to ON for jobs you\'ve applied to',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppTheme.neutralGray500,
                ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildErrorCard(String error) {
    return Card(
      color: Colors.red.withValues(alpha: 0.08),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Icon(Icons.error_outline, color: Colors.red),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Could not load saved jobs',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: Colors.red,
                          fontWeight: FontWeight.w600,
                        ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    error,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.red[700],
                        ),
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton.icon(
                    onPressed: _loadJobs,
                    icon: const Icon(Icons.refresh),
                    label: const Text('Try again'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primaryTeal,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}
