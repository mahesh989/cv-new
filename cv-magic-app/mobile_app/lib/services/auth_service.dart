import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../core/config/app_config.dart';

/// Central authentication service.
///
/// All sign-in / sign-out calls go through here. It wraps Firebase Auth,
/// syncs with the backend on first sign-in, and caches the user email in
/// SharedPreferences so the rest of the app can read it synchronously.
class AuthService {
  AuthService._();
  static final AuthService instance = AuthService._();

  final FirebaseAuth _auth = FirebaseAuth.instance;
  final GoogleSignIn _googleSignIn = GoogleSignIn(
    scopes: ['email', 'profile'],
  );

  // ── Current user helpers ──────────────────────────────────────────────────

  User? get currentUser => _auth.currentUser;
  bool get isSignedIn => currentUser != null;

  Stream<User?> get authStateChanges => _auth.authStateChanges();

  /// Returns a fresh Firebase ID token for the current user.
  /// Pass this in every backend request as `Authorization: Bearer <token>`.
  Future<String?> getIdToken({bool forceRefresh = false}) async {
    final user = currentUser;
    if (user == null) return null;
    return user.getIdToken(forceRefresh);
  }

  // ── Sign-in methods ───────────────────────────────────────────────────────

  /// Email + password sign-in (existing account).
  Future<UserCredential> signInWithEmail(String email, String password) async {
    final cred = await _auth.signInWithEmailAndPassword(
      email: email.trim(),
      password: password,
    );
    await _postSignIn(cred.user);
    return cred;
  }

  /// Email + password registration (new account).
  Future<UserCredential> registerWithEmail(
    String email,
    String password,
    String displayName,
  ) async {
    final cred = await _auth.createUserWithEmailAndPassword(
      email: email.trim(),
      password: password,
    );
    // Set display name in Firebase
    await cred.user?.updateDisplayName(displayName.trim());
    await cred.user?.reload();
    await _postSignIn(cred.user);
    return cred;
  }

  /// Google Sign-In (OAuth pop-up / native sheet).
  Future<UserCredential?> signInWithGoogle() async {
    final googleUser = await _googleSignIn.signIn();
    if (googleUser == null) return null; // user cancelled

    final googleAuth = await googleUser.authentication;
    final credential = GoogleAuthProvider.credential(
      accessToken: googleAuth.accessToken,
      idToken: googleAuth.idToken,
    );

    final userCred = await _auth.signInWithCredential(credential);
    await _postSignIn(userCred.user);
    return userCred;
  }

  // ── Sign-out ──────────────────────────────────────────────────────────────

  Future<void> signOut() async {
    await Future.wait([
      _auth.signOut(),
      _googleSignIn.signOut(),
    ]);
    await _clearLocalSession();
  }

  // ── Password reset ────────────────────────────────────────────────────────

  Future<void> sendPasswordResetEmail(String email) async {
    await _auth.sendPasswordResetEmail(email: email.trim());
  }

  // ── Backend sync ──────────────────────────────────────────────────────────

  /// Called after every successful Firebase sign-in.
  ///
  /// 1. Caches user info locally.
  /// 2. Calls the backend `/api/auth/firebase/sync` to auto-provision the
  ///    user record on first sign-in.
  Future<void> _postSignIn(User? user) async {
    if (user == null) return;

    // Cache locally
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('is_logged_in', true);
    await prefs.setString('user_email', user.email ?? '');
    await prefs.setString('user_name', user.displayName ?? user.email?.split('@').first ?? 'User');

    // Sync with backend (best-effort — don't block the UI on failure)
    try {
      final token = await getIdToken();
      if (token == null) return;

      final response = await http.post(
        Uri.parse('${AppConfig.baseUrl}/api/auth/firebase/sync'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        debugPrint('✅ [AUTH] Backend sync successful for ${user.email}');
      } else {
        debugPrint('⚠️ [AUTH] Backend sync returned ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('⚠️ [AUTH] Backend sync failed (non-fatal): $e');
    }
  }

  Future<void> _clearLocalSession() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('is_logged_in');
    await prefs.remove('user_email');
    await prefs.remove('user_name');
    await prefs.remove('auth_token'); // clear any legacy JWT token
  }
}

// Convenience top-level import alias
final authService = AuthService.instance;
