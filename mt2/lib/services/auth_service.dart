// Stub implementation of AuthService to prevent Firebase compilation errors
// This should be replaced with proper Firebase implementation once Firebase is configured

import '../utils/notification_service.dart';

class AuthService {
  // Mock user for development
  static bool _isSignedIn = false;
  static String? _currentUserEmail;
  static String? _currentUserName;

  // Mock auth state changes stream
  static Stream<MockUser?> get authStateChanges => Stream.value(_isSignedIn
      ? MockUser(_currentUserEmail ?? '', _currentUserName ?? 'User')
      : null);

  // Current user
  static MockUser? get currentUser => _isSignedIn
      ? MockUser(_currentUserEmail ?? '', _currentUserName ?? 'User')
      : null;

  // Sign in with email and password
  static Future<MockUserCredential?> signInWithEmailAndPassword(
      String email, String password) async {
    try {
      // Mock sign in
      await Future.delayed(const Duration(milliseconds: 500));
      _isSignedIn = true;
      _currentUserEmail = email;
      _currentUserName = email.split('@')[0];

      return MockUserCredential(MockUser(email, _currentUserName!));
    } catch (e) {
      throw Exception('Mock sign in failed: $e');
    }
  }

  // Register with email and password
  static Future<MockUserCredential?> registerWithEmailAndPassword(
      String email, String password, String displayName) async {
    try {
      // Mock registration
      await Future.delayed(const Duration(milliseconds: 500));
      _isSignedIn = true;
      _currentUserEmail = email;
      _currentUserName = displayName;

      return MockUserCredential(MockUser(email, displayName));
    } catch (e) {
      throw Exception('Mock registration failed: $e');
    }
  }

  // Sign in with Google
  static Future<MockUserCredential?> signInWithGoogle() async {
    try {
      // Mock Google sign in
      await Future.delayed(const Duration(milliseconds: 500));
      _isSignedIn = true;
      _currentUserEmail = 'user@gmail.com';
      _currentUserName = 'Mock User';

      return MockUserCredential(
          MockUser(_currentUserEmail!, _currentUserName!));
    } catch (e) {
      throw Exception('Mock Google sign in failed: $e');
    }
  }

  // Sign out
  static Future<void> signOut() async {
    try {
      _isSignedIn = false;
      _currentUserEmail = null;
      _currentUserName = null;
    } catch (e) {
      throw Exception('Sign out failed: $e');
    }
  }

  // Reset password
  static Future<void> resetPassword(String email) async {
    try {
      await Future.delayed(const Duration(milliseconds: 500));
      // Mock password reset
    } catch (e) {
      throw Exception('Password reset failed: $e');
    }
  }

  // Get user data
  static Future<Map<String, dynamic>?> getUserData() async {
    try {
      if (!_isSignedIn) return null;

      return {
        'email': _currentUserEmail,
        'displayName': _currentUserName,
        'settings': {
          'notifications': true,
          'theme': 'light',
        },
        'subscription': {
          'plan': 'free',
        },
      };
    } catch (e) {
      print('Error getting user data: $e');
      return null;
    }
  }

  // Update user settings
  static Future<void> updateUserSettings(Map<String, dynamic> settings) async {
    try {
      if (!_isSignedIn) return;
      // Mock settings update
      await Future.delayed(const Duration(milliseconds: 300));
    } catch (e) {
      throw Exception('Failed to update settings: $e');
    }
  }

  // Save CV to user's library
  static Future<void> saveCVToLibrary(String cvName, String cvContent) async {
    try {
      if (!_isSignedIn) return;
      // Mock CV save
      await Future.delayed(const Duration(milliseconds: 300));
    } catch (e) {
      throw Exception('Failed to save CV: $e');
    }
  }

  // Save ATS result to user's history
  static Future<void> saveATSResult(Map<String, dynamic> atsResult) async {
    try {
      if (!_isSignedIn) return;
      // Mock ATS result save
      await Future.delayed(const Duration(milliseconds: 300));
    } catch (e) {
      throw Exception('Failed to save ATS result: $e');
    }
  }

  // Get user's CV library
  static Future<List<Map<String, dynamic>>> getUserCVs() async {
    try {
      if (!_isSignedIn) return [];
      // Mock CV list
      return [
        {
          'id': 'mock1',
          'name': 'My Resume.pdf',
          'createdAt': DateTime.now().subtract(const Duration(days: 1)),
        },
      ];
    } catch (e) {
      print('Error getting user CVs: $e');
      return [];
    }
  }

  // Get user's ATS results
  static Future<List<Map<String, dynamic>>> getUserATSResults() async {
    try {
      if (!_isSignedIn) return [];
      // Mock ATS results
      return [
        {
          'id': 'mock1',
          'score': 85,
          'createdAt': DateTime.now().subtract(const Duration(hours: 2)),
        },
      ];
    } catch (e) {
      print('Error getting ATS results: $e');
      return [];
    }
  }
}

// Mock classes to replace Firebase types
class MockUser {
  final String email;
  final String displayName;
  final String uid;

  MockUser(this.email, this.displayName) : uid = email.hashCode.toString();
}

class MockUserCredential {
  final MockUser user;

  MockUserCredential(this.user);
}
