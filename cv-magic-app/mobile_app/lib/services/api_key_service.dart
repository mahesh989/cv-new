import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/config/app_config.dart';
import '../core/config/environment_config.dart';

class APIKeyService {
  static String get _baseUrl => EnvironmentConfig.baseUrl;

  /// Get authentication token from SharedPreferences
  Future<String?> _getAuthToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString('auth_token');
    } catch (e) {
      print('Error getting auth token: $e');
      return null;
    }
  }

  /// Set API key for a specific provider
  Future<bool> setAPIKey(String provider, String apiKey) async {
    try {
      // Use set-initial endpoint for first-time setup (no auth required)
      final response = await http.post(
        Uri.parse('$_baseUrl/api/api-keys/set-initial'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'provider': provider,
          'api_key': apiKey,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['success'] == true && data['is_valid'] == true;
      }

      return false;
    } catch (e) {
      print('Error setting API key: $e');
      return false;
    }
  }

  /// Validate API key for a specific provider
  Future<bool> validateAPIKey(String provider) async {
    try {
      final authToken = await _getAuthToken();
      final headers = <String, String>{
        'Content-Type': 'application/json',
      };

      if (authToken != null && authToken.isNotEmpty) {
        headers['Authorization'] = 'Bearer $authToken';
      }

      final response = await http.post(
        Uri.parse('$_baseUrl/api/api-keys/validate/$provider'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['success'] == true && data['is_valid'] == true;
      }

      return false;
    } catch (e) {
      print('Error validating API key: $e');
      return false;
    }
  }

  /// Get status of all providers
  Future<Map<String, dynamic>> getProvidersStatus() async {
    try {
      final authToken = await _getAuthToken();

      // Try authenticated endpoint first if token is available
      if (authToken != null && authToken.isNotEmpty) {
        final response = await http.get(
          Uri.parse('$_baseUrl/api/api-keys/status'),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $authToken',
          },
        );

        if (response.statusCode == 200) {
          final data = jsonDecode(response.body);
          return data['providers'] ?? {};
        }
      }

      // Fallback to unauthenticated endpoint for initial setup
      final response = await http.get(
        Uri.parse('$_baseUrl/api/api-keys/status-initial'),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['providers'] ?? {};
      }

      return {};
    } catch (e) {
      print('Error getting providers status: $e');
      return {};
    }
  }

  /// Remove API key for a specific provider
  Future<bool> removeAPIKey(String provider) async {
    try {
      final authToken = await _getAuthToken();
      final headers = <String, String>{
        'Content-Type': 'application/json',
      };

      if (authToken != null && authToken.isNotEmpty) {
        headers['Authorization'] = 'Bearer $authToken';
      }

      final response = await http.delete(
        Uri.parse('$_baseUrl/api/api-keys/$provider'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['success'] == true;
      }

      return false;
    } catch (e) {
      print('Error removing API key: $e');
      return false;
    }
  }

  /// Clear all API keys
  Future<bool> clearAllAPIKeys() async {
    try {
      final authToken = await _getAuthToken();
      final headers = <String, String>{
        'Content-Type': 'application/json',
      };

      if (authToken != null && authToken.isNotEmpty) {
        headers['Authorization'] = 'Bearer $authToken';
      }

      final response = await http.delete(
        Uri.parse('$_baseUrl/api/api-keys/'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['success'] == true;
      }

      return false;
    } catch (e) {
      print('Error clearing all API keys: $e');
      return false;
    }
  }
}
