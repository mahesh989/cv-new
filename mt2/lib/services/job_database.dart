import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class JobDatabase {
  // Use localhost for development, change to production URL when deploying
  static const String _baseUrl = 'http://localhost:8000';

  // Singleton pattern
  static final JobDatabase _instance = JobDatabase._internal();
  factory JobDatabase() => _instance;
  JobDatabase._internal();

  // Save job result using HTTP API (persistent across sessions)
  Future<void> saveJobResult({
    required String jobId,
    required String jobTitle,
    required String company,
    required String jdText,
    required DateTime testDate,
    required int atsScore,
    required String cvName,
    required List<String> matchedSkills,
    required List<String> missedSkills,
    required Map<String, dynamic> metadata,
    required String status,
  }) async {
    try {
      debugPrint(
          '💾 [HTTP_DATABASE] Starting saveJobResult for: $jobTitle at $company');

      final requestData = {
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

      debugPrint('💾 [HTTP_DATABASE] Sending data to backend...');

      final response = await http.post(
        Uri.parse('$_baseUrl/ats-dashboard/save-result/'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode(requestData),
      );

      if (response.statusCode == 200) {
        debugPrint(
            '💾 [HTTP_DATABASE] Job result saved successfully to backend');
      } else {
        debugPrint(
            '❌ [HTTP_DATABASE] Error saving job result: ${response.statusCode} - ${response.body}');
        throw Exception('Failed to save job result: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('❌ [HTTP_DATABASE] Error saving job result: $e');
      rethrow;
    }
  }

  // Get all job results from HTTP API
  Future<List<Map<String, dynamic>>> getAllJobResults() async {
    try {
      debugPrint('🔍 [HTTP_DATABASE] Fetching job results from backend...');

      final response = await http.get(
        Uri.parse('$_baseUrl/ats-dashboard/results/'),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        final jobs = data.cast<Map<String, dynamic>>();

        debugPrint(
            '📊 [HTTP_DATABASE] Loaded ${jobs.length} job results from backend');
        for (int i = 0; i < jobs.length && i < 3; i++) {
          debugPrint(
              '📊 [HTTP_DATABASE] Job $i: ${jobs[i]['jobTitle']} at ${jobs[i]['company']} (Score: ${jobs[i]['atsScore']})');
        }

        return jobs;
      } else {
        debugPrint(
            '❌ [HTTP_DATABASE] Error loading job results: ${response.statusCode} - ${response.body}');
        return [];
      }
    } catch (e) {
      debugPrint('❌ [HTTP_DATABASE] Error loading job results: $e');
      return [];
    }
  }

  // Clear all job results via HTTP API
  Future<void> clearAllJobResults() async {
    try {
      debugPrint('🗑️ [HTTP_DATABASE] Clearing all job results...');

      final response = await http.delete(
        Uri.parse('$_baseUrl/ats-dashboard/clear/'),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        debugPrint('🗑️ [HTTP_DATABASE] All job results cleared from backend');
      } else {
        debugPrint(
            '❌ [HTTP_DATABASE] Error clearing job results: ${response.statusCode} - ${response.body}');
        throw Exception('Failed to clear job results: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('❌ [HTTP_DATABASE] Error clearing job results: $e');
      rethrow;
    }
  }

  // Migrate data from old SharedPreferences format (now deprecated)
  Future<void> migrateFromSharedPreferences() async {
    // Migration no longer needed since we're using HTTP API
    debugPrint('👌 [HTTP_DATABASE] Migration not needed - using HTTP API');
  }

  // Get database statistics via HTTP API
  Future<Map<String, dynamic>> getStats() async {
    try {
      debugPrint('📊 [HTTP_DATABASE] Fetching statistics from backend...');

      final response = await http.get(
        Uri.parse('$_baseUrl/ats-dashboard/stats/'),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final stats = json.decode(response.body) as Map<String, dynamic>;
        debugPrint('📊 [HTTP_DATABASE] Stats: ${stats.toString()}');
        return stats;
      } else {
        debugPrint(
            '❌ [HTTP_DATABASE] Error getting stats: ${response.statusCode} - ${response.body}');
        return {
          'totalJobs': 0,
          'avgScore': 0,
          'topScore': 0,
          'storageType': 'HTTP API (Failed)',
        };
      }
    } catch (e) {
      debugPrint('❌ [HTTP_DATABASE] Error getting stats: $e');
      return {
        'totalJobs': 0,
        'avgScore': 0,
        'topScore': 0,
        'storageType': 'HTTP API (Error)',
      };
    }
  }
}
