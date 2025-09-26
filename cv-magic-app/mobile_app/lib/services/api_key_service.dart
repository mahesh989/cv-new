import 'package:http/http.dart' as http;
import 'dart:convert';
import '../core/config/app_config.dart';

class APIKeyService {
  static const String _baseUrl = AppConfig.baseUrl;

  /// Set API key for a specific provider
  Future<bool> setAPIKey(String provider, String apiKey) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/api/api-keys/set'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization':
              'Bearer ${AppConfig.authToken}', // You'll need to get this from your auth service
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
      final response = await http.post(
        Uri.parse('$_baseUrl/api/api-keys/validate/$provider'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AppConfig.authToken}',
        },
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
      final response = await http.get(
        Uri.parse('$_baseUrl/api/api-keys/status'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AppConfig.authToken}',
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
      final response = await http.delete(
        Uri.parse('$_baseUrl/api/api-keys/$provider'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AppConfig.authToken}',
        },
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
      final response = await http.delete(
        Uri.parse('$_baseUrl/api/api-keys/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AppConfig.authToken}',
        },
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
