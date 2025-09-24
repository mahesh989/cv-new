///
/// Job Tracking Screen
///
/// A modular, dynamic, structured, and reusable job tracking interface
/// that follows the existing design patterns and maintains consistency
/// with other tabs in the application.
///

import 'dart:convert';
import 'package:flutter/material.dart';
import '../services/saved_jobs_service.dart';
import '../widgets/job_tracking/saved_jobs_table_updated.dart';
import '../core/theme/app_theme.dart';

class JobTrackingScreen extends StatefulWidget {
  const JobTrackingScreen({super.key});

  @override
  State<JobTrackingScreen> createState() => _JobTrackingScreenState();
}

class _JobTrackingScreenState extends State<JobTrackingScreen>
    with AutomaticKeepAliveClientMixin {
  List<Map<String, dynamic>> _jobs = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _verifyAssets();
    _loadJobs();
  }

  Future<void> _verifyAssets() async {
    try {
      debugPrint('🔍 [JOB_TRACKING] Verifying assets...');
      final manifestContent = await DefaultAssetBundle.of(context).loadString('AssetManifest.json');
      final Map<String, dynamic> manifestMap = json.decode(manifestContent);
      
      if (manifestMap.containsKey('assets/saved_jobs.json')) {
        debugPrint('✅ [JOB_TRACKING] Found saved_jobs.json in asset manifest');
      } else {
        debugPrint('❌ [JOB_TRACKING] saved_jobs.json not found in asset manifest!');
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
      });
    } catch (e, stackTrace) {
      debugPrint('❌ [JOB_TRACKING] Error loading jobs: $e');
      debugPrint('📋 [JOB_TRACKING] Stack trace: $stackTrace');
      setState(() {
        _error = 'Failed to load saved jobs: $e';
        _isLoading = false;
      });
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
        SavedJobsTable(jobs: _jobs),
      ],
    );
  }

  Widget _buildHeader() {
    return Row(
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
        IconButton(
          onPressed: _loadJobs,
          icon: const Icon(Icons.refresh),
          tooltip: 'Reload',
        ),
      ],
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
