import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/config/app_config.dart';
import 'auth_service.dart';

class DebugLogsService {
  static final DebugLogsService _instance = DebugLogsService._internal();
  factory DebugLogsService() => _instance;
  DebugLogsService._internal();

  final String baseUrl = AppConfig.baseUrl;

  /// Get recent backend logs
  Future<Map<String, dynamic>> getRecentLogs({
    int lines = 100,
    String? filterKeyword,
  }) async {
    try {
      final token = await AuthService.getValidAuthToken();
      if (token == null) {
        return {
          'success': false,
          'error': 'Not authenticated',
          'logs': [],
        };
      }

      final uri =
          Uri.parse('$baseUrl/api/debug/logs/recent').replace(queryParameters: {
        'lines': lines.toString(),
        if (filterKeyword != null) 'filter_keyword': filterKeyword,
      });

      final response = await http.get(
        uri,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch logs: ${response.statusCode}',
          'logs': [],
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Error fetching logs: $e',
        'logs': [],
      };
    }
  }

  /// Get JD processing specific logs
  Future<Map<String, dynamic>> getJDProcessingLogs({int lines = 200}) async {
    return getRecentLogs(lines: lines, filterKeyword: 'JD_PROCESSING');
  }

  /// Poll logs at regular intervals
  Stream<Map<String, dynamic>> pollLogs({
    int lines = 100,
    String? filterKeyword,
    Duration interval = const Duration(seconds: 2),
  }) async* {
    while (true) {
      try {
        final result = await getRecentLogs(
          lines: lines,
          filterKeyword: filterKeyword,
        );
        yield result;
        await Future.delayed(interval);
      } catch (e) {
        yield {
          'success': false,
          'error': 'Error polling logs: $e',
          'logs': [],
        };
        await Future.delayed(interval);
      }
    }
  }
}

final debugLogsService = DebugLogsService();
