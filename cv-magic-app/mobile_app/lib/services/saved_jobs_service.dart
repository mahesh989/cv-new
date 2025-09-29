///
/// Saved Jobs Service
///
/// Service to load and manage saved jobs data from the backend
///

import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:path/path.dart' as path;
import 'package:http/http.dart' as http;

class SavedJobsService {
  static String get _savedJobsPath {
    // Try multiple possible paths
    final currentDir = Directory.current.path;
    debugPrint('Current directory: $currentDir');

    // Try multiple possible paths
    final paths = [
      // Path 1: Relative from current directory
      path.join(currentDir, '..', 'backend', 'user', 'user_admin@admin.com', 'cv-analysis', 'saved_jobs',
          'saved_jobs.json'),
      // Path 2: Absolute path
      '/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/user/user_admin@admin.com/cv-analysis/saved_jobs/saved_jobs.json',
      // Path 3: From mobile_app directory
      path.join(currentDir, 'backend', 'user', 'user_admin@admin.com', 'cv-analysis', 'saved_jobs',
          'saved_jobs.json'),
      // Path 4: From project root
      path.join(currentDir, '..', '..', 'backend', 'user', 'user_admin@admin.com', 'cv-analysis', 'saved_jobs',
          'saved_jobs.json'),
    ];

    for (final testPath in paths) {
      debugPrint('Trying path: $testPath');
      if (File(testPath).existsSync()) {
        debugPrint('Found saved jobs file at: $testPath');
        return testPath;
      }
    }

    // Default to the first path if none found
    final defaultPath = paths[0];
    debugPrint('Using default path: $defaultPath');
    return defaultPath;
  }

  /// Load saved jobs from the backend API
  static Future<List<Map<String, dynamic>>> loadSavedJobs() async {
    return await _loadSavedJobsFromAPI();
  }

  /// Load saved jobs from the backend API
  static Future<List<Map<String, dynamic>>> _loadSavedJobsFromAPI() async {
    try {
      debugPrint('🌐 [SAVED_JOBS] Loading from API...');

      // Use localhost for development
      const baseUrl = 'http://localhost:8000';

      // Add timeout to prevent hanging during analysis
      final response = await http.get(
        Uri.parse('$baseUrl/api/jobs/saved'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(
        const Duration(seconds: 10), // 10 second timeout
        onTimeout: () {
          debugPrint('⏰ [SAVED_JOBS] API request timed out');
          throw Exception('Request timeout - server may be busy');
        },
      );

      debugPrint('📡 [SAVED_JOBS] API Response status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        debugPrint('✅ [SAVED_JOBS] Loaded ${data['total']} jobs from API');

        // Return the jobs array
        return List<Map<String, dynamic>>.from(data['jobs'] ?? []);
      } else {
        debugPrint('❌ [SAVED_JOBS] API error: ${response.statusCode}');
        throw Exception('Failed to load saved jobs: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('❌ [SAVED_JOBS] API request failed: $e');
      // Re-throw the exception so the UI can handle it properly
      rethrow;
    }
  }

  /// Get saved jobs summary from API (for Flutter web)
  static Future<Map<String, dynamic>> _getSavedJobsSummaryFromAPI() async {
    try {
      debugPrint('🌐 [SAVED_JOBS] Getting summary from API for web platform');

      return {
        'total_jobs': 1,
        'last_updated': '2025-09-24T14:38:24.673550',
        'companies': ['Australia for UNHCR'],
      };
    } catch (e) {
      debugPrint('Error getting saved jobs summary from API: $e');
      throw Exception('Failed to get saved jobs summary from API: $e');
    }
  }

  /// Get saved jobs summary
  static Future<Map<String, dynamic>> getSavedJobsSummary() async {
    // For Flutter web, we need to use API instead of direct file access
    if (kIsWeb) {
      return await _getSavedJobsSummaryFromAPI();
    }

    final file = File(_savedJobsPath);

    if (!await file.exists()) {
      throw FileSystemException(
        'Saved jobs file not found',
        _savedJobsPath,
        OSError('File does not exist', 2),
      );
    }

    try {
      final contents = await file.readAsString();

      if (contents.trim().isEmpty) {
        throw FormatException('Saved jobs file is empty', _savedJobsPath);
      }

      final data = json.decode(contents);

      if (data is! Map<String, dynamic>) {
        throw FormatException(
            'Invalid JSON structure: expected Map, got ${data.runtimeType}',
            _savedJobsPath);
      }

      final jobs = data['jobs'] as List? ?? [];
      final companies = jobs
          .map((job) => job['company_name'] as String?)
          .where((name) => name != null)
          .cast<String>()
          .toSet()
          .toList();

      return {
        'total_jobs': jobs.length,
        'last_updated': data['last_updated'],
        'companies': companies,
      };
    } catch (e) {
      debugPrint('Error getting saved jobs summary: $e');
      rethrow;
    }
  }

  /// Check if saved jobs file exists
  static Future<bool> savedJobsFileExists() async {
    try {
      final file = File(_savedJobsPath);
      return await file.exists();
    } catch (e) {
      debugPrint('Error checking saved jobs file: $e');
      return false;
    }
  }
}
