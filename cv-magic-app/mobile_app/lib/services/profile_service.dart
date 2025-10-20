import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/profile_model.dart';
import 'api_service.dart';
import 'auth_service.dart';

class ProfileService {
  static const String _baseUrl = 'https://cvagent.duckdns.org';
  static const String _apiPrefix = '/api/profile';

  /// Get current user's profile
  static Future<ProfileResponse> getProfile() async {
    try {
      final token = await AuthService.getValidAuthToken();
      if (token == null) {
        throw Exception('Authentication required');
      }

      final response = await http.get(
        Uri.parse('$_baseUrl$_apiPrefix'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return ProfileResponse.fromJson(data);
      } else {
        final errorData = jsonDecode(response.body);
        throw Exception(errorData['detail'] ?? 'Failed to get profile');
      }
    } catch (e) {
      print('Error getting profile: $e');
      return ProfileResponse(
        success: false,
        message: 'Error getting profile: $e',
      );
    }
  }

  /// Create a new profile
  static Future<ProfileResponse> createProfile(UserProfile profile) async {
    try {
      final token = await AuthService.getValidAuthToken();
      if (token == null) {
        throw Exception('Authentication required');
      }

      final response = await http.post(
        Uri.parse('$_baseUrl$_apiPrefix'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode(profile.toJson()),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return ProfileResponse.fromJson(data);
      } else {
        final errorData = jsonDecode(response.body);
        throw Exception(errorData['detail'] ?? 'Failed to create profile');
      }
    } catch (e) {
      print('Error creating profile: $e');
      return ProfileResponse(
        success: false,
        message: 'Error creating profile: $e',
      );
    }
  }

  /// Update existing profile
  static Future<ProfileResponse> updateProfile(Map<String, dynamic> updates) async {
    try {
      final token = await AuthService.getValidAuthToken();
      if (token == null) {
        throw Exception('Authentication required');
      }

      final response = await http.put(
        Uri.parse('$_baseUrl$_apiPrefix'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode(updates),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return ProfileResponse.fromJson(data);
      } else {
        final errorData = jsonDecode(response.body);
        throw Exception(errorData['detail'] ?? 'Failed to update profile');
      }
    } catch (e) {
      print('Error updating profile: $e');
      return ProfileResponse(
        success: false,
        message: 'Error updating profile: $e',
      );
    }
  }

  /// Delete profile
  static Future<ProfileResponse> deleteProfile() async {
    try {
      final token = await AuthService.getValidAuthToken();
      if (token == null) {
        throw Exception('Authentication required');
      }

      final response = await http.delete(
        Uri.parse('$_baseUrl$_apiPrefix'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return ProfileResponse.fromJson(data);
      } else {
        final errorData = jsonDecode(response.body);
        throw Exception(errorData['detail'] ?? 'Failed to delete profile');
      }
    } catch (e) {
      print('Error deleting profile: $e');
      return ProfileResponse(
        success: false,
        message: 'Error deleting profile: $e',
      );
    }
  }

  /// Check if profile exists
  static Future<bool> profileExists() async {
    try {
      final token = await AuthService.getValidAuthToken();
      if (token == null) {
        return false;
      }

      final response = await http.get(
        Uri.parse('$_baseUrl$_apiPrefix/exists'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['exists'] ?? false;
      }
      return false;
    } catch (e) {
      print('Error checking profile existence: $e');
      return false;
    }
  }

  /// Validate profile for CV generation
  static Future<ProfileResponse> validateProfileForCV() async {
    try {
      final token = await AuthService.getValidAuthToken();
      if (token == null) {
        throw Exception('Authentication required');
      }

      final response = await http.get(
        Uri.parse('$_baseUrl$_apiPrefix/validate'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return ProfileResponse.fromJson(data);
      } else {
        final errorData = jsonDecode(response.body);
        throw Exception(errorData['detail'] ?? 'Failed to validate profile');
      }
    } catch (e) {
      print('Error validating profile: $e');
      return ProfileResponse(
        success: false,
        message: 'Error validating profile: $e',
      );
    }
  }

  /// Get profile data for CV generation
  static Future<Map<String, dynamic>?> getProfileForCVGeneration() async {
    try {
      final token = await AuthService.getValidAuthToken();
      if (token == null) {
        throw Exception('Authentication required');
      }

      final response = await http.get(
        Uri.parse('$_baseUrl$_apiPrefix/cv-data'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['cv_data'];
      } else {
        return null;
      }
    } catch (e) {
      print('Error getting profile for CV generation: $e');
      return null;
    }
  }
}
