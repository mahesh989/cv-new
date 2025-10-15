import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../core/config/app_config.dart';

class AuthService {
  static const String _baseUrl = AppConfig.baseUrl;
  static const String _refreshTokenKey = 'refresh_token';
  static const String _authTokenKey = 'auth_token';
  static const String _tokenExpiryKey = 'token_expiry';
  static const String _userEmailKey = 'user_email';
  static const String _userNameKey = 'user_name';
  static const String _isLoggedInKey = 'is_logged_in';

  /// Get authentication token from SharedPreferences
  static Future<String?> getAuthToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(_authTokenKey);
    } catch (e) {
      print('Error getting auth token: $e');
      return null;
    }
  }

  /// Get refresh token from SharedPreferences
  static Future<String?> getRefreshToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(_refreshTokenKey);
    } catch (e) {
      print('Error getting refresh token: $e');
      return null;
    }
  }

  /// Check if token is expired
  static Future<bool> isTokenExpired() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final expiryString = prefs.getString(_tokenExpiryKey);

      if (expiryString == null) return true;

      final expiry = DateTime.parse(expiryString);
      final now = DateTime.now();

      // Consider token expired if it expires within the next 5 minutes
      return now.isAfter(expiry.subtract(const Duration(minutes: 5)));
    } catch (e) {
      print('Error checking token expiry: $e');
      return true;
    }
  }

  /// Refresh access token using refresh token
  static Future<String?> refreshAccessToken() async {
    try {
      final refreshToken = await getRefreshToken();
      if (refreshToken == null) {
        print('No refresh token available');
        return null;
      }

      final response = await http.post(
        Uri.parse('$_baseUrl/api/auth/refresh-token'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'refresh_token': refreshToken,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final newAccessToken = data['access_token'];
        final newRefreshToken = data['refresh_token'];
        final expiresIn = data['expires_in']; // in seconds

        // Save new tokens
        await _saveTokens(
          accessToken: newAccessToken,
          refreshToken: newRefreshToken,
          expiresIn: expiresIn,
        );

        print('✅ Token refreshed successfully');
        return newAccessToken;
      } else {
        print('❌ Token refresh failed: ${response.statusCode}');
        print('Response: ${response.body}');
        return null;
      }
    } catch (e) {
      print('❌ Error refreshing token: $e');
      return null;
    }
  }

  /// Get valid authentication token (refresh if needed)
  static Future<String?> getValidAuthToken() async {
    try {
      // Check if current token is still valid
      if (!await isTokenExpired()) {
        return await getAuthToken();
      }

      print('🔄 Token expired, attempting to refresh...');

      // Try to refresh the token
      final newToken = await refreshAccessToken();
      if (newToken != null) {
        return newToken;
      }

      // If refresh failed, user needs to login again
      print('❌ Token refresh failed, user needs to login again');
      await clearAuthData();
      return null;
    } catch (e) {
      print('❌ Error getting valid auth token: $e');
      return null;
    }
  }

  /// Save authentication tokens and user data
  static Future<void> _saveTokens({
    required String accessToken,
    required String refreshToken,
    required int expiresIn,
  }) async {
    try {
      final prefs = await SharedPreferences.getInstance();

      // Calculate expiry time
      final expiry = DateTime.now().add(Duration(seconds: expiresIn));

      await prefs.setString(_authTokenKey, accessToken);
      await prefs.setString(_refreshTokenKey, refreshToken);
      await prefs.setString(_tokenExpiryKey, expiry.toIso8601String());
      await prefs.setBool(_isLoggedInKey, true);

      print('✅ Tokens saved successfully');
    } catch (e) {
      print('❌ Error saving tokens: $e');
    }
  }

  /// Save user data after login
  static Future<void> saveUserData({
    required String email,
    required String name,
    required String accessToken,
    required String refreshToken,
    required int expiresIn,
  }) async {
    try {
      final prefs = await SharedPreferences.getInstance();

      // Calculate expiry time
      final expiry = DateTime.now().add(Duration(seconds: expiresIn));

      await prefs.setString(_userEmailKey, email);
      await prefs.setString(_userNameKey, name);
      await prefs.setString(_authTokenKey, accessToken);
      await prefs.setString(_refreshTokenKey, refreshToken);
      await prefs.setString(_tokenExpiryKey, expiry.toIso8601String());
      await prefs.setBool(_isLoggedInKey, true);

      print('✅ User data saved successfully');
    } catch (e) {
      print('❌ Error saving user data: $e');
    }
  }

  /// Clear all authentication data
  static Future<void> clearAuthData() async {
    try {
      final prefs = await SharedPreferences.getInstance();

      await prefs.remove(_authTokenKey);
      await prefs.remove(_refreshTokenKey);
      await prefs.remove(_tokenExpiryKey);
      await prefs.remove(_userEmailKey);
      await prefs.remove(_userNameKey);
      await prefs.setBool(_isLoggedInKey, false);

      print('✅ Auth data cleared successfully');
    } catch (e) {
      print('❌ Error clearing auth data: $e');
    }
  }

  /// Check if user is logged in
  static Future<bool> isLoggedIn() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final isLoggedIn = prefs.getBool(_isLoggedInKey) ?? false;

      if (!isLoggedIn) return false;

      // Check if token is still valid
      return !await isTokenExpired();
    } catch (e) {
      print('❌ Error checking login status: $e');
      return false;
    }
  }

  /// Get user email
  static Future<String?> getUserEmail() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(_userEmailKey);
    } catch (e) {
      print('❌ Error getting user email: $e');
      return null;
    }
  }

  /// Get user name
  static Future<String?> getUserName() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(_userNameKey);
    } catch (e) {
      print('❌ Error getting user name: $e');
      return null;
    }
  }

  /// Make authenticated HTTP request with automatic token refresh
  static Future<http.Response> makeAuthenticatedRequest({
    required String method,
    required String endpoint,
    Map<String, String>? headers,
    Object? body,
  }) async {
    try {
      // Get valid token (refresh if needed)
      final token = await getValidAuthToken();
      if (token == null) {
        throw Exception('Authentication required. Please log in.');
      }

      // Prepare headers
      final requestHeaders = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
        ...?headers,
      };

      // Make request
      final url = Uri.parse('$_baseUrl$endpoint');
      http.Response response;

      switch (method.toUpperCase()) {
        case 'GET':
          response = await http.get(url, headers: requestHeaders);
          break;
        case 'POST':
          response = await http.post(
            url,
            headers: requestHeaders,
            body: body,
          );
          break;
        case 'PUT':
          response = await http.put(
            url,
            headers: requestHeaders,
            body: body,
          );
          break;
        case 'DELETE':
          response = await http.delete(url, headers: requestHeaders);
          break;
        default:
          throw Exception('Unsupported HTTP method: $method');
      }

      // If token expired during request, try to refresh and retry once
      if (response.statusCode == 401) {
        final responseBody = response.body;
        if (responseBody.contains('Token has expired') ||
            responseBody.contains('expired')) {
          print('🔄 Token expired during request, refreshing...');
          final newToken = await refreshAccessToken();

          if (newToken != null) {
            // Retry request with new token
            requestHeaders['Authorization'] = 'Bearer $newToken';

            switch (method.toUpperCase()) {
              case 'GET':
                response = await http.get(url, headers: requestHeaders);
                break;
              case 'POST':
                response = await http.post(
                  url,
                  headers: requestHeaders,
                  body: body,
                );
                break;
              case 'PUT':
                response = await http.put(
                  url,
                  headers: requestHeaders,
                  body: body,
                );
                break;
              case 'DELETE':
                response = await http.delete(url, headers: requestHeaders);
                break;
            }
          }
        }
      }

      return response;
    } catch (e) {
      print('❌ Error making authenticated request: $e');
      rethrow;
    }
  }
}
