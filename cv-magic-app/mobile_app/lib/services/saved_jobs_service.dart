///
/// Saved Jobs Service
///
/// Service to load and manage saved jobs data from the backend
///

import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:path/path.dart' as path;

class SavedJobsService {
  static String get _savedJobsPath {
    // Try multiple possible paths
    final currentDir = Directory.current.path;
    debugPrint('Current directory: $currentDir');

    // Try multiple possible paths
    final paths = [
      // Path 1: Relative from current directory
      path.join(currentDir, '..', 'backend', 'saved_jobs', 'saved_jobs.json'),
      // Path 2: Absolute path
      '/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/saved_jobs/saved_jobs.json',
      // Path 3: From mobile_app directory
      path.join(currentDir, 'backend', 'saved_jobs', 'saved_jobs.json'),
      // Path 4: From project root
      path.join(
          currentDir, '..', '..', 'backend', 'saved_jobs', 'saved_jobs.json'),
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

  /// Load saved jobs from the JSON file
  static Future<List<Map<String, dynamic>>> loadSavedJobs() async {
    // For Flutter web, we need to use HTTP requests instead of direct file access
    if (kIsWeb) {
      return await _loadSavedJobsFromAPI();
    }

    try {
      final file = File(_savedJobsPath);
      debugPrint('🔍 [SAVED_JOBS] Looking for file at: $_savedJobsPath');
      
      if (await file.exists()) {
        try {
          final contents = await file.readAsString();
          debugPrint('✅ [SAVED_JOBS] Loaded from filesystem, length: ${contents.length}');
          return _parseJobsJson(contents);
        } catch (e) {
          debugPrint('⚠️ [SAVED_JOBS] Failed to read from filesystem: $e');
          // Continue to fallback
        }
      } else {
        debugPrint('ℹ️ [SAVED_JOBS] File not found at $_savedJobsPath');
      }

      // Fallback to bundled asset for mobile/simulator
      debugPrint('📎 [SAVED_JOBS] Attempting to load from assets...');
      try {
        final assetContents = await rootBundle.loadString('assets/saved_jobs.json');
        debugPrint('✅ [SAVED_JOBS] Loaded from assets, length: ${assetContents.length}');
        return _parseJobsJson(assetContents);
      } catch (e) {
        debugPrint('❌ [SAVED_JOBS] Failed to load from assets: $e');
        rethrow;
      }
    } on FormatException catch (e) {
      debugPrint('JSON format error: $e');
      rethrow;
    } on FlutterError catch (e) {
      debugPrint('Asset load error: $e');
      rethrow;
    } catch (e) {
      debugPrint('Error loading saved jobs: $e');
      throw Exception('Failed to load saved jobs: $e');
    }
  }

  static List<Map<String, dynamic>> _parseJobsJson(String contents) {
    if (contents.trim().isEmpty) {
      throw const FormatException('Saved jobs data is empty');
    }

    final data = json.decode(contents);

    if (data is! Map<String, dynamic>) {
      throw FormatException(
          'Invalid JSON structure: expected Map, got ${data.runtimeType}');
    }

    if (!data.containsKey('jobs')) {
      throw const FormatException('Missing "jobs" key in saved jobs data');
    }

    final jobs = data['jobs'];
    if (jobs is! List) {
      throw FormatException(
          'Invalid "jobs" structure: expected List, got ${jobs.runtimeType}');
    }

    return jobs.cast<Map<String, dynamic>>();
  }

  /// Load saved jobs from API (for Flutter web)
  static Future<List<Map<String, dynamic>>> _loadSavedJobsFromAPI() async {
    try {
      debugPrint('🌐 [SAVED_JOBS] Loading from API for web platform');

      // For now, return sample data since we don't have a backend API endpoint
      // In a real implementation, you would make an HTTP request to your backend
      return [
        {
          'company_name': 'Australia for UNHCR',
          'job_url':
              'https://www.ethicaljobs.com.au/members/australiaforunhcr/data-analyst',
          'job_title': 'Data Analyst',
          'location': 'Sydney, Australia',
          'phone_number': null,
          'email': null,
        }
      ];
    } catch (e) {
      debugPrint('Error loading saved jobs from API: $e');
      throw Exception('Failed to load saved jobs from API: $e');
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
