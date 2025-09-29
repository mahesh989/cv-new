import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:path/path.dart' as path;

class JobsStateManager {
  static const String _backendJobsPath =
      'backend/user/user_admin_at_admin_com/cv-analysis/saved_jobs/saved_jobs.json';
  static const String _assetsJobsPath = 'assets/saved_jobs.json';

  static Future<void> saveNewJob({
    bool replace = false,
    required String companyName,
    required String jobTitle,
    required String jobUrl,
    required String location,
    String? phoneNumber,
    String? email,
  }) async {
    try {
      debugPrint('🔄 [JOBS_STATE] Saving new job: $companyName - $jobTitle');

      // Get current working directory
      final currentDir = Directory.current.path;
      debugPrint('📂 [JOBS_STATE] Working directory: $currentDir');

      // Build paths for both backend and assets files
      final backendPath = path.join(currentDir, _backendJobsPath);
      final assetsPath = path.join(currentDir, _assetsJobsPath);

      // Load existing data from backend file
      var jobsData = await _loadExistingJobs(backendPath);

      // Create new job entry
      final newJob = {
        'company_name': companyName,
        'job_title': jobTitle,
        'job_url': jobUrl,
        'location': location,
        'phone_number': phoneNumber,
        'email': email,
      };

      // Check if job already exists
      final jobs = jobsData['jobs'] as List;
      final existingJobIndex = jobs.indexWhere((job) =>
          (job['company_name'] == companyName && job['job_url'] == jobUrl) ||
          (job['company_name'] == companyName && job['job_title'] == jobTitle));

      if (existingJobIndex >= 0) {
        if (replace) {
          // Update existing job
          jobs[existingJobIndex] = newJob;
          debugPrint('✏️ [JOBS_STATE] Updated existing job: $companyName');
        } else {
          debugPrint(
              'ℹ️ [JOBS_STATE] Job already exists, skipping: $companyName');
          return;
        }
      } else {
        // Add new job
        jobs.add(newJob);
        debugPrint('➕ [JOBS_STATE] Added new job: $companyName');
      }

      // Update timestamp
      jobsData['last_updated'] = DateTime.now().toIso8601String();
      jobsData['total_jobs'] = jobs.length;

      // Convert to JSON string with proper formatting
      final jsonString = JsonEncoder.withIndent('  ').convert(jobsData);

      // Save to both locations
      await Future.wait([
        _writeJsonToFile(backendPath, jsonString),
        _writeJsonToFile(assetsPath, jsonString),
      ]);

      debugPrint('✅ [JOBS_STATE] Successfully saved job data');
    } catch (e, stackTrace) {
      debugPrint('❌ [JOBS_STATE] Error saving job: $e');
      debugPrint('📋 [JOBS_STATE] Stack trace: $stackTrace');
      rethrow;
    }
  }

  static Future<Map<String, dynamic>> _loadExistingJobs(String filePath) async {
    try {
      final file = File(filePath);
      if (!await file.exists()) {
        debugPrint('⚠️ [JOBS_STATE] Jobs file not found, creating new one');
        return {
          'jobs': [],
          'total_jobs': 0,
          'last_updated': DateTime.now().toIso8601String()
        };
      }

      final contents = await file.readAsString();
      final data = json.decode(contents);
      debugPrint('✅ [JOBS_STATE] Successfully loaded existing jobs');
      return data;
    } catch (e) {
      debugPrint('❌ [JOBS_STATE] Error loading existing jobs: $e');
      rethrow;
    }
  }

  static Future<void> _writeJsonToFile(
      String filePath, String jsonString) async {
    try {
      final file = File(filePath);
      await file.writeAsString('$jsonString\n');
      debugPrint('✅ [JOBS_STATE] Successfully wrote to $filePath');
    } catch (e) {
      debugPrint('❌ [JOBS_STATE] Error writing to $filePath: $e');
      rethrow;
    }
  }
}
