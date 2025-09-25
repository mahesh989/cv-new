///
/// Job Tracking Screen
///
/// A modular, dynamic, structured, and reusable job tracking interface
/// that follows the existing design patterns and maintains consistency
/// with other tabs in the application.
///

import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
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
  bool _isLoading =
      false; // Start with false, only set to true when actually loading
  String? _error;
  bool _showAppliedJobs = false; // Toggle for showing applied jobs only
  final Map<String, bool> _appliedStatus =
      {}; // Track applied status for each job
  bool _hasCachedData = false; // Track if we have cached data to show
  DateTime? _lastLoadTime; // Track when we last loaded data

  /// Public method to trigger refresh from external sources
  void refreshJobs() {
    debugPrint('🔄 [JOB_TRACKING] External refresh triggered');

    // If we're already loading, skip
    if (_isLoading) {
      debugPrint('⏸️ [JOB_TRACKING] Already loading, skipping refresh');
      return;
    }

    // If we have existing data, always show it immediately and refresh silently
    if (_jobs.isNotEmpty) {
      debugPrint(
          '📋 [JOB_TRACKING] Showing existing data (${_jobs.length} jobs) and refreshing silently');
      // Show existing data immediately, just make sure applied status is loaded
      _loadAppliedStatus();

      // Check if we need to refresh based on age
      if (_lastLoadTime != null) {
        final timeSinceLastLoad = DateTime.now().difference(_lastLoadTime!);
        if (timeSinceLastLoad.inSeconds < 30) {
          debugPrint(
              '📋 [JOB_TRACKING] Data is recent (${timeSinceLastLoad.inSeconds}s ago), no refresh needed');
          return;
        }
      }

      // Data is older than 30s or no timestamp, refresh silently in background
      debugPrint('🔄 [JOB_TRACKING] Refreshing data silently in background...');
      _silentRefresh();
    } else {
      // No existing data, do a full load with loading indicator
      debugPrint('🔄 [JOB_TRACKING] No existing data, loading jobs...');
      _loadJobs();
    }
  }

  @override
  void initState() {
    super.initState();
    _verifyAssets();
    _preloadAppliedStatus(); // Preload applied status before loading jobs
    _loadJobs();
  }

  /// Get the backup file path for applied statuses
  Future<File> _getBackupFile() async {
    final directory = await getApplicationDocumentsDirectory();
    return File('${directory.path}/applied_statuses.json');
  }

  /// Save applied statuses to backup file
  Future<void> _saveToBackupFile() async {
    try {
      final file = await _getBackupFile();
      final data = jsonEncode(_appliedStatus);
      await file.writeAsString(data);
      debugPrint(
          '💾 [JOB_TRACKING] Saved applied statuses to backup file: ${_appliedStatus.length} items');
    } catch (e) {
      debugPrint('❌ [JOB_TRACKING] Error saving to backup file: $e');
    }
  }

  /// Load applied statuses from backup file
  Future<void> _loadFromBackupFile() async {
    try {
      final file = await _getBackupFile();
      if (await file.exists()) {
        final data = await file.readAsString();
        final Map<String, dynamic> decoded = jsonDecode(data);
        _appliedStatus.clear();
        decoded.forEach((key, value) {
          _appliedStatus[key] = value as bool;
        });
        debugPrint(
            '📂 [JOB_TRACKING] Loaded applied statuses from backup file: ${_appliedStatus.length} items');
      } else {
        debugPrint('📂 [JOB_TRACKING] No backup file found');
      }
    } catch (e) {
      debugPrint('❌ [JOB_TRACKING] Error loading from backup file: $e');
    }
  }

  /// Preload applied status from SharedPreferences and backup file
  Future<void> _preloadAppliedStatus() async {
    try {
      debugPrint('🚀 [JOB_TRACKING] Preloading applied status on app start...');

      // First, try to load from backup file
      await _loadFromBackupFile();

      final prefs = await SharedPreferences.getInstance();

      // List all keys for debugging
      final allPrefsKeys = prefs.getKeys().toList();
      debugPrint('🔍 [JOB_TRACKING] All SharedPreferences keys: $allPrefsKeys');

      final allKeys =
          prefs.getKeys().where((key) => key.startsWith('applied_')).toList();
      debugPrint(
          '📚 [JOB_TRACKING] Found ${allKeys.length} saved applied statuses in SharedPreferences');

      // If SharedPreferences has data, it takes priority and we sync to backup
      if (allKeys.isNotEmpty) {
        debugPrint(
            '📋 [JOB_TRACKING] Using SharedPreferences data as primary source');
        _appliedStatus.clear(); // Clear backup data
        for (final key in allKeys) {
          if (key.startsWith('applied_')) {
            final jobKey =
                key.substring('applied_'.length); // Remove 'applied_' prefix
            final value = prefs.getBool(key) ?? false;
            _appliedStatus[jobKey] = value;
            debugPrint(
                '💾 [JOB_TRACKING] Pre-populated applied status: $jobKey = $value');
          }
        }
        // Save current state to backup file
        await _saveToBackupFile();
      } else if (_appliedStatus.isNotEmpty) {
        debugPrint(
            '🔄 [JOB_TRACKING] SharedPreferences empty, using backup file data');
        debugPrint(
            '📋 [JOB_TRACKING] Restoring ${_appliedStatus.length} applied statuses from backup');
        // Restore from backup to SharedPreferences
        for (final entry in _appliedStatus.entries) {
          final prefKey = 'applied_${entry.key}';
          await prefs.setBool(prefKey, entry.value);
          debugPrint(
              '🔄 [JOB_TRACKING] Restored to SharedPreferences: $prefKey = ${entry.value}');
        }
      } else {
        debugPrint(
            '⚠️ [JOB_TRACKING] No applied statuses found in SharedPreferences or backup file');
      }
    } catch (e) {
      debugPrint('❌ [JOB_TRACKING] Error preloading applied status: $e');
    }
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
        _hasCachedData = false; // Reset cached flag since we got fresh data
        _lastLoadTime = DateTime.now(); // Track when we loaded data
      });
      // Load applied status after jobs are loaded
      await _loadAppliedStatus();
    } catch (e, stackTrace) {
      debugPrint('❌ [JOB_TRACKING] Error loading jobs: $e');
      debugPrint('📋 [JOB_TRACKING] Stack trace: $stackTrace');

      // If we have cached data from previous successful loads, show it instead of error
      if (_jobs.isNotEmpty) {
        debugPrint(
            '📋 [JOB_TRACKING] Showing cached data due to API error (${_jobs.length} jobs)');
        setState(() {
          _isLoading = false;
          _error = null; // Don't show error if we have cached data
          _hasCachedData = true; // Mark that we're showing cached data
        });
        // Still load applied status for cached data
        await _loadAppliedStatus();
      } else {
        debugPrint('❌ [JOB_TRACKING] No cached data available, showing error');
        setState(() {
          _error = 'Failed to load saved jobs: $e';
          _isLoading = false;
          _hasCachedData = false;
        });
      }
    }
  }

  /// Silent refresh - updates data in background without showing loading spinner
  Future<void> _silentRefresh() async {
    try {
      debugPrint('🔄 [JOB_TRACKING] Silent refresh in progress...');
      final jobs = await SavedJobsService.loadSavedJobs();
      debugPrint(
          '✅ [JOB_TRACKING] Silent refresh successful - ${jobs.length} jobs');
      setState(() {
        _jobs = jobs;
        _hasCachedData = false; // Reset cached flag since we got fresh data
        _lastLoadTime = DateTime.now(); // Track when we loaded data
        _error = null; // Clear any previous errors
      });
      // Load applied status after jobs are loaded
      await _loadAppliedStatus();
    } catch (e) {
      debugPrint('❌ [JOB_TRACKING] Silent refresh failed: $e');
      // Don't update UI state on error - keep existing data visible
      // Silently fail and keep using cached data
    }
  }

  Future<void> _loadAppliedStatus() async {
    try {
      debugPrint(
          '🔄 [JOB_TRACKING] Loading applied status from SharedPreferences...');
      debugPrint(
          '📊 [JOB_TRACKING] Total jobs to load status for: ${_jobs.length}');

      final prefs = await SharedPreferences.getInstance();

      // Clear existing applied status to start fresh
      _appliedStatus.clear();

      // Get all keys from SharedPreferences to debug
      final allKeys =
          prefs.getKeys().where((key) => key.startsWith('applied_')).toList();
      debugPrint(
          '🔍 [JOB_TRACKING] Found ${allKeys.length} saved applied statuses in SharedPreferences');

      // Load applied status for each job
      int loadedCount = 0;
      for (var job in _jobs) {
        final key = _getJobKey(job);
        final prefKey = 'applied_$key';
        final isApplied = prefs.getBool(prefKey) ?? false;
        _appliedStatus[key] = isApplied;

        if (isApplied) {
          loadedCount++;
          debugPrint(
              '✅ [JOB_TRACKING] Job ${job['company_name']}: applied = true (key: $prefKey)');
        } else {
          debugPrint(
              '📋 [JOB_TRACKING] Job ${job['company_name']}: applied = false (key: $prefKey)');
        }
      }

      debugPrint(
          '✅ [JOB_TRACKING] Loaded applied status for ${_appliedStatus.length} jobs ($loadedCount applied)');

      // Always trigger UI update to ensure applied status is reflected
      setState(() {
        // This will trigger a rebuild to show updated applied jobs
      });
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
            const Spacer(),
            // Debug button to clear all applied statuses (only visible in debug mode)
            if (kDebugMode) ...[
              IconButton(
                onPressed: () async {
                  debugPrint(
                      '🧹 [JOB_TRACKING] Debug: Clearing all applied statuses');
                  final prefs = await SharedPreferences.getInstance();
                  final allKeys = prefs
                      .getKeys()
                      .where((key) => key.startsWith('applied_'))
                      .toList();
                  for (final key in allKeys) {
                    await prefs.remove(key);
                  }
                  _appliedStatus.clear();
                  setState(() {});
                  debugPrint(
                      '✅ [JOB_TRACKING] Debug: Cleared ${allKeys.length} applied statuses');
                },
                icon: const Icon(Icons.delete_sweep),
                tooltip: 'Clear All Applied Status (Debug)',
              ),
            ],
            IconButton(
              onPressed: () {
                debugPrint('🔄 [JOB_TRACKING] Manual refresh triggered');
                // If we have data, use silent refresh, otherwise full load
                if (_jobs.isNotEmpty) {
                  _silentRefresh();
                } else {
                  _loadJobs();
                }
              },
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
    // Create a more robust key using multiple fields and normalize them
    final companyName =
        (job['company_name'] ?? '').toString().trim().toLowerCase();
    final jobUrl = (job['job_url'] ?? '').toString().trim();
    final jobTitle = (job['job_title'] ?? '').toString().trim().toLowerCase();

    // Use a combination of fields to create a unique, stable key
    final key = '${companyName}_${jobTitle}_${jobUrl.hashCode}';
    debugPrint(
        '🔑 [JOB_TRACKING] Generated key for ${job['company_name']}: $key');
    return key;
  }

  void _onAppliedStatusChanged(Map<String, dynamic> job, bool isApplied) async {
    debugPrint(
        '📞 [JOB_TRACKING] Callback received for ${job['company_name']}: $isApplied');

    final key = _getJobKey(job);
    final prefKey = 'applied_$key';

    debugPrint('🔑 [JOB_TRACKING] Generated key in callback: $key');

    // Update in-memory state immediately
    setState(() {
      _appliedStatus[key] = isApplied;
    });

    // Save to SharedPreferences with verification
    try {
      final prefs = await SharedPreferences.getInstance();

      // Save the value
      final saveSuccess = await prefs.setBool(prefKey, isApplied);

      // Verify it was saved correctly
      final savedValue = prefs.getBool(prefKey);

      if (saveSuccess && savedValue == isApplied) {
        debugPrint(
            '✅ [JOB_TRACKING] Saved and verified applied status for ${job['company_name']}: $isApplied (key: $prefKey)');
      } else {
        debugPrint(
            '❌ [JOB_TRACKING] Failed to save or verify applied status for ${job['company_name']}: expected $isApplied, got $savedValue');
      }

      // Debug: Show all saved applied statuses
      final allKeys =
          prefs.getKeys().where((k) => k.startsWith('applied_')).toList();
      debugPrint(
          '📊 [JOB_TRACKING] Total saved applied statuses: ${allKeys.length}');

      // Also save to backup file for persistence
      await _saveToBackupFile();
    } catch (e) {
      debugPrint('❌ [JOB_TRACKING] Error saving applied status: $e');
      // Revert in-memory state if save failed
      setState(() {
        _appliedStatus[key] = !isApplied;
      });
    }

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
