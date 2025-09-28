import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../core/config/app_config.dart';

class NetworkUtils {
  /// Test if the backend is accessible
  static Future<bool> testBackendConnectivity() async {
    try {
      final response = await http.get(
        Uri.parse(AppConfig.baseUrl),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 5));

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  /// Get detailed connectivity info for debugging
  static Future<Map<String, dynamic>> getConnectivityInfo() async {
    final info = {
      'backend_url': AppConfig.baseUrl,
      'api_url': AppConfig.apiBaseUrl,
      'backend_accessible': false,
      'auth_endpoints_accessible': false,
      'error': null,
    };

    try {
      // Test backend root
      final rootResponse = await http
          .get(
            Uri.parse(AppConfig.baseUrl),
          )
          .timeout(const Duration(seconds: 5));

      info['backend_accessible'] = rootResponse.statusCode == 200;

      // Test auth endpoints
      final authResponse = await http
          .post(
            Uri.parse('${AppConfig.apiBaseUrl}/auth/login'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(
                {'invalid': 'data'}), // Will get 422 but proves endpoint exists
          )
          .timeout(const Duration(seconds: 5));

      info['auth_endpoints_accessible'] = authResponse.statusCode ==
          422; // Validation error means endpoint works
    } catch (e) {
      info['error'] = e.toString();
    }

    return info;
  }

  /// Show connectivity debug dialog
  static Future<void> showConnectivityDialog(BuildContext context) async {
    final info = await getConnectivityInfo();

    if (!context.mounted) return;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('🔍 Network Connectivity Debug'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('🌐 Backend URL: ${info['backend_url']}'),
              const SizedBox(height: 8),
              Text('📡 API URL: ${info['api_url']}'),
              const SizedBox(height: 8),
              Text(
                  '✅ Backend: ${info['backend_accessible'] ? 'Accessible' : 'Not Accessible'}'),
              const SizedBox(height: 8),
              Text(
                  '🔐 Auth Endpoints: ${info['auth_endpoints_accessible'] ? 'Working' : 'Not Working'}'),
              if (info['error'] != null) ...[
                const SizedBox(height: 8),
                Text('❌ Error: ${info['error']}'),
              ],
              const SizedBox(height: 16),
              const Text(
                '💡 Troubleshooting:\n'
                '• Ensure backend server is running\n'
                '• For Android Emulator: Use 10.0.2.2:8000\n'
                '• For iOS Simulator: Use localhost:8000\n'
                '• For Physical Device: Use your computer\'s IP',
                style: TextStyle(fontSize: 12),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}
