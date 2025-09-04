/// Comprehensive security and data protection for Flutter app
/// Provides input validation, secure storage, encryption, and security best practices

library security;

import 'dart:async';
import 'dart:convert';
import 'dart:math';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:crypto/crypto.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'architecture.dart';

/// Input validation utilities
class InputValidator {
  /// Email validation
  static bool isValidEmail(String email) {
    if (email.isEmpty) return false;
    
    final emailRegex = RegExp(
      r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    );
    
    return emailRegex.hasMatch(email);
  }

  /// Password strength validation
  static PasswordStrength validatePassword(String password) {
    if (password.isEmpty) {
      return PasswordStrength.empty;
    }
    
    if (password.length < 8) {
      return PasswordStrength.tooShort;
    }
    
    bool hasUppercase = password.contains(RegExp(r'[A-Z]'));
    bool hasLowercase = password.contains(RegExp(r'[a-z]'));
    bool hasDigits = password.contains(RegExp(r'[0-9]'));
    bool hasSpecialCharacters = password.contains(RegExp(r'[!@#$%^&*(),.?":{}|<>]'));
    
    int strength = 0;
    if (hasUppercase) strength++;
    if (hasLowercase) strength++;
    if (hasDigits) strength++;
    if (hasSpecialCharacters) strength++;
    if (password.length >= 12) strength++;
    
    switch (strength) {
      case 0:
      case 1:
        return PasswordStrength.weak;
      case 2:
      case 3:
        return PasswordStrength.medium;
      case 4:
      case 5:
        return PasswordStrength.strong;
      default:
        return PasswordStrength.weak;
    }
  }

  /// File name validation (prevent directory traversal)
  static bool isValidFileName(String fileName) {
    if (fileName.isEmpty) return false;
    
    // Check for directory traversal attempts
    if (fileName.contains('..') || 
        fileName.contains('/') || 
        fileName.contains('\\') ||
        fileName.contains(':')) {
      return false;
    }
    
    // Check for reserved characters
    final invalidChars = RegExp(r'[<>:"/\\|?*]');
    if (invalidChars.hasMatch(fileName)) {
      return false;
    }
    
    // Check for reserved Windows filenames
    final reservedNames = [
      'CON', 'PRN', 'AUX', 'NUL',
      'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
      'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
    ];
    
    final baseNameUpper = fileName.split('.').first.toUpperCase();
    if (reservedNames.contains(baseNameUpper)) {
      return false;
    }
    
    return true;
  }

  /// URL validation
  static bool isValidUrl(String url) {
    if (url.isEmpty) return false;
    
    try {
      final uri = Uri.parse(url);
      return uri.hasAbsolutePath && (uri.scheme == 'http' || uri.scheme == 'https');
    } catch (e) {
      return false;
    }
  }

  /// Sanitize text input (prevent XSS-like attacks)
  static String sanitizeText(String input) {
    return input
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#x27;')
        .replaceAll('&', '&amp;');
  }

  /// Validate file size
  static bool isValidFileSize(int bytes, {int maxSizeMB = 10}) {
    final maxBytes = maxSizeMB * 1024 * 1024;
    return bytes <= maxBytes;
  }

  /// Validate file type
  static bool isValidFileType(String fileName, List<String> allowedExtensions) {
    if (fileName.isEmpty) return false;
    
    final extension = fileName.toLowerCase().split('.').last;
    return allowedExtensions.contains(extension);
  }
}

/// Password strength enum
enum PasswordStrength {
  empty,
  tooShort,
  weak,
  medium,
  strong,
}

/// Extension for password strength
extension PasswordStrengthExtension on PasswordStrength {
  String get description {
    switch (this) {
      case PasswordStrength.empty:
        return 'Password is required';
      case PasswordStrength.tooShort:
        return 'Password must be at least 8 characters';
      case PasswordStrength.weak:
        return 'Weak password';
      case PasswordStrength.medium:
        return 'Medium strength password';
      case PasswordStrength.strong:
        return 'Strong password';
    }
  }

  Color get color {
    switch (this) {
      case PasswordStrength.empty:
      case PasswordStrength.tooShort:
        return Colors.grey;
      case PasswordStrength.weak:
        return Colors.red;
      case PasswordStrength.medium:
        return Colors.orange;
      case PasswordStrength.strong:
        return Colors.green;
    }
  }

  double get strength {
    switch (this) {
      case PasswordStrength.empty:
      case PasswordStrength.tooShort:
        return 0.0;
      case PasswordStrength.weak:
        return 0.3;
      case PasswordStrength.medium:
        return 0.6;
      case PasswordStrength.strong:
        return 1.0;
    }
  }
}

/// Secure storage manager with encryption
class SecureStorage {
  static final SecureStorage _instance = SecureStorage._internal();
  factory SecureStorage() => _instance;
  SecureStorage._internal();

  late SharedPreferences _prefs;
  late String _encryptionKey;
  bool _isInitialized = false;

  /// Initialize secure storage
  Future<void> initialize() async {
    if (_isInitialized) return;
    
    _prefs = await SharedPreferences.getInstance();
    _encryptionKey = await _getOrCreateEncryptionKey();
    _isInitialized = true;
    
    Logger.info('🔐 Secure storage initialized');
  }

  /// Store encrypted data
  Future<void> store(String key, String value) async {
    await _ensureInitialized();
    
    final encryptedValue = _encrypt(value);
    await _prefs.setString('secure_$key', encryptedValue);
  }

  /// Retrieve and decrypt data
  Future<String?> retrieve(String key) async {
    await _ensureInitialized();
    
    final encryptedValue = _prefs.getString('secure_$key');
    if (encryptedValue == null) return null;
    
    try {
      return _decrypt(encryptedValue);
    } catch (e) {
      Logger.error('Failed to decrypt value for key: $key', e);
      return null;
    }
  }

  /// Remove stored data
  Future<void> remove(String key) async {
    await _ensureInitialized();
    await _prefs.remove('secure_$key');
  }

  /// Clear all secure storage
  Future<void> clear() async {
    await _ensureInitialized();
    
    final keys = _prefs.getKeys().where((k) => k.startsWith('secure_'));
    for (final key in keys) {
      await _prefs.remove(key);
    }
  }

  Future<void> _ensureInitialized() async {
    if (!_isInitialized) {
      await initialize();
    }
  }

  /// Get or create encryption key
  Future<String> _getOrCreateEncryptionKey() async {
    String? key = _prefs.getString('encryption_key');
    
    if (key == null) {
      key = _generateRandomKey();
      await _prefs.setString('encryption_key', key);
    }
    
    return key;
  }

  /// Generate random encryption key
  String _generateRandomKey() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    final random = Random.secure();
    
    return String.fromCharCodes(
      Iterable.generate(32, (_) => chars.codeUnitAt(random.nextInt(chars.length))),
    );
  }

  /// Simple XOR encryption (for demo - use proper encryption in production)
  String _encrypt(String text) {
    final textBytes = utf8.encode(text);
    final keyBytes = utf8.encode(_encryptionKey);
    final encrypted = <int>[];
    
    for (int i = 0; i < textBytes.length; i++) {
      encrypted.add(textBytes[i] ^ keyBytes[i % keyBytes.length]);
    }
    
    return base64.encode(encrypted);
  }

  /// Simple XOR decryption
  String _decrypt(String encryptedText) {
    final encryptedBytes = base64.decode(encryptedText);
    final keyBytes = utf8.encode(_encryptionKey);
    final decrypted = <int>[];
    
    for (int i = 0; i < encryptedBytes.length; i++) {
      decrypted.add(encryptedBytes[i] ^ keyBytes[i % keyBytes.length]);
    }
    
    return utf8.decode(decrypted);
  }
}

/// Biometric authentication helper
class BiometricAuth {
  static final BiometricAuth _instance = BiometricAuth._internal();
  factory BiometricAuth() => _instance;
  BiometricAuth._internal();

  /// Check if biometric authentication is available
  Future<bool> isAvailable() async {
    try {
      // TODO: Implement actual biometric check
      // You can use packages like local_auth for real biometric authentication
      return false; // Simulated - not available
    } catch (e) {
      Logger.error('Error checking biometric availability', e);
      return false;
    }
  }

  /// Authenticate with biometrics
  Future<bool> authenticate({
    required String reason,
    bool biometricOnly = true,
  }) async {
    try {
      // TODO: Implement actual biometric authentication
      // Example with local_auth package:
      // final isAvailable = await isAvailable();
      // if (!isAvailable) return false;
      // 
      // return await _localAuth.authenticate(
      //   localizedReason: reason,
      //   options: AuthenticationOptions(
      //     biometricOnly: biometricOnly,
      //     stickyAuth: true,
      //   ),
      // );
      
      return false; // Simulated - always fails for demo
    } catch (e) {
      Logger.error('Biometric authentication failed', e);
      return false;
    }
  }
}

/// Session security manager
class SessionSecurity {
  static final SessionSecurity _instance = SessionSecurity._internal();
  factory SessionSecurity() => _instance;
  SessionSecurity._internal();

  DateTime? _sessionStart;
  DateTime? _lastActivity;
  final Duration _sessionTimeout = const Duration(minutes: 30);
  final Duration _inactivityTimeout = const Duration(minutes: 15);

  /// Start a new session
  void startSession() {
    _sessionStart = DateTime.now();
    _lastActivity = DateTime.now();
    Logger.info('🔐 Session started');
  }

  /// Update last activity timestamp
  void updateActivity() {
    _lastActivity = DateTime.now();
  }

  /// Check if session is valid
  bool isSessionValid() {
    if (_sessionStart == null || _lastActivity == null) return false;
    
    final now = DateTime.now();
    
    // Check session timeout
    if (now.difference(_sessionStart!) > _sessionTimeout) {
      Logger.warning('Session expired due to timeout');
      return false;
    }
    
    // Check inactivity timeout
    if (now.difference(_lastActivity!) > _inactivityTimeout) {
      Logger.warning('Session expired due to inactivity');
      return false;
    }
    
    return true;
  }

  /// End current session
  void endSession() {
    _sessionStart = null;
    _lastActivity = null;
    Logger.info('🔐 Session ended');
  }

  /// Get session info
  Map<String, dynamic> getSessionInfo() {
    if (_sessionStart == null || _lastActivity == null) {
      return {'active': false};
    }
    
    final now = DateTime.now();
    return {
      'active': true,
      'started': _sessionStart!.toIso8601String(),
      'lastActivity': _lastActivity!.toIso8601String(),
      'duration': now.difference(_sessionStart!).inMinutes,
      'timeSinceActivity': now.difference(_lastActivity!).inMinutes,
      'timeUntilTimeout': _inactivityTimeout.inMinutes - 
                         now.difference(_lastActivity!).inMinutes,
    };
  }
}

/// Data anonymization utilities
class DataAnonymizer {
  /// Anonymize email address
  static String anonymizeEmail(String email) {
    if (!InputValidator.isValidEmail(email)) return email;
    
    final parts = email.split('@');
    final username = parts[0];
    final domain = parts[1];
    
    if (username.length <= 2) {
      return '${username.substring(0, 1)}***@$domain';
    }
    
    return '${username.substring(0, 2)}***@$domain';
  }

  /// Anonymize phone number
  static String anonymizePhone(String phone) {
    if (phone.length <= 4) return phone;
    
    return '***${phone.substring(phone.length - 4)}';
  }

  /// Generate hash for sensitive data
  static String hashSensitiveData(String data) {
    final bytes = utf8.encode(data);
    final digest = sha256.convert(bytes);
    return digest.toString();
  }

  /// Sanitize logs by removing sensitive information
  static String sanitizeLogData(String logData) {
    return logData
        .replaceAll(RegExp(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL]')
        .replaceAll(RegExp(r'\b\d{3}-?\d{3}-?\d{4}\b'), '[PHONE]')
        .replaceAll(RegExp(r'\b\d{16}\b'), '[CARD]')
        .replaceAll(RegExp(r'password["\s:=]+[^"\s,}]+', caseSensitive: false), 'password=[REDACTED]');
  }
}

/// Security monitoring and alerts
class SecurityMonitor {
  static final SecurityMonitor _instance = SecurityMonitor._internal();
  factory SecurityMonitor() => _instance;
  SecurityMonitor._internal();

  final List<SecurityEvent> _events = [];
  final StreamController<SecurityEvent> _eventController = StreamController.broadcast();

  Stream<SecurityEvent> get securityEvents => _eventController.stream;

  /// Log security event
  void logSecurityEvent({
    required SecurityEventType type,
    required String description,
    Map<String, dynamic>? metadata,
  }) {
    final event = SecurityEvent(
      type: type,
      description: description,
      timestamp: DateTime.now(),
      metadata: metadata ?? {},
    );

    _events.add(event);
    _eventController.add(event);

    // Keep only last 100 events
    if (_events.length > 100) {
      _events.removeAt(0);
    }

    Logger.warning('Security Event: ${type.name} - $description');

    // Check for security alerts
    _checkForSecurityAlerts(event);
  }

  /// Check for patterns that might indicate security issues
  void _checkForSecurityAlerts(SecurityEvent event) {
    switch (event.type) {
      case SecurityEventType.failedLogin:
        _checkFailedLoginAttempts();
        break;
      case SecurityEventType.suspiciousActivity:
        _alertSuspiciousActivity(event);
        break;
      case SecurityEventType.dataAccess:
        _checkUnauthorizedAccess(event);
        break;
      default:
        break;
    }
  }

  /// Check for multiple failed login attempts
  void _checkFailedLoginAttempts() {
    final recentFailures = _events
        .where((e) => 
          e.type == SecurityEventType.failedLogin &&
          DateTime.now().difference(e.timestamp).inMinutes < 10)
        .length;

    if (recentFailures >= 3) {
      Logger.error('🚨 Multiple failed login attempts detected: $recentFailures attempts');
      // TODO: Implement account lockout or additional security measures
    }
  }

  /// Alert for suspicious activity
  void _alertSuspiciousActivity(SecurityEvent event) {
    Logger.error('🚨 Suspicious activity detected: ${event.description}');
    // TODO: Implement additional security responses
  }

  /// Check for unauthorized data access
  void _checkUnauthorizedAccess(SecurityEvent event) {
    // TODO: Implement data access monitoring
    Logger.info('Data access logged: ${event.description}');
  }

  /// Get recent security events
  List<SecurityEvent> getRecentEvents({Duration? within}) {
    final cutoff = within != null 
        ? DateTime.now().subtract(within)
        : DateTime.now().subtract(const Duration(hours: 24));

    return _events.where((e) => e.timestamp.isAfter(cutoff)).toList();
  }

  /// Clear security events
  void clearEvents() {
    _events.clear();
  }

  void dispose() {
    _eventController.close();
  }
}

/// Security event types
enum SecurityEventType {
  login,
  logout,
  failedLogin,
  dataAccess,
  dataModification,
  suspiciousActivity,
  sessionTimeout,
}

/// Security event model
class SecurityEvent {
  final SecurityEventType type;
  final String description;
  final DateTime timestamp;
  final Map<String, dynamic> metadata;

  SecurityEvent({
    required this.type,
    required this.description,
    required this.timestamp,
    required this.metadata,
  });

  Map<String, dynamic> toJson() => {
    'type': type.name,
    'description': description,
    'timestamp': timestamp.toIso8601String(),
    'metadata': metadata,
  };
}

/// Security widgets for user interface

/// Secure text field with validation
class SecureTextField extends StatefulWidget {
  final String label;
  final String? initialValue;
  final bool isPassword;
  final Function(String)? onChanged;
  final String? Function(String?)? validator;
  final bool enableStrengthIndicator;
  final List<String> allowedFileTypes;

  const SecureTextField({
    super.key,
    required this.label,
    this.initialValue,
    this.isPassword = false,
    this.onChanged,
    this.validator,
    this.enableStrengthIndicator = false,
    this.allowedFileTypes = const [],
  });

  @override
  State<SecureTextField> createState() => _SecureTextFieldState();
}

class _SecureTextFieldState extends State<SecureTextField> {
  late TextEditingController _controller;
  bool _isObscured = true;
  PasswordStrength _passwordStrength = PasswordStrength.empty;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.initialValue);
    if (widget.isPassword && widget.enableStrengthIndicator) {
      _controller.addListener(_checkPasswordStrength);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _checkPasswordStrength() {
    final strength = InputValidator.validatePassword(_controller.text);
    if (strength != _passwordStrength) {
      setState(() {
        _passwordStrength = strength;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextFormField(
          controller: _controller,
          obscureText: widget.isPassword && _isObscured,
          onChanged: (value) {
            widget.onChanged?.call(value);
            if (widget.isPassword && widget.enableStrengthIndicator) {
              _checkPasswordStrength();
            }
          },
          validator: widget.validator,
          decoration: InputDecoration(
            labelText: widget.label,
            suffixIcon: widget.isPassword
                ? IconButton(
                    icon: Icon(_isObscured ? Icons.visibility : Icons.visibility_off),
                    onPressed: () {
                      setState(() {
                        _isObscured = !_isObscured;
                      });
                    },
                  )
                : null,
          ),
        ),
        if (widget.isPassword && widget.enableStrengthIndicator) ...[
          const SizedBox(height: 8),
          LinearProgressIndicator(
            value: _passwordStrength.strength,
            backgroundColor: Colors.grey[300],
            valueColor: AlwaysStoppedAnimation<Color>(_passwordStrength.color),
          ),
          const SizedBox(height: 4),
          Text(
            _passwordStrength.description,
            style: TextStyle(
              color: _passwordStrength.color,
              fontSize: 12,
            ),
          ),
        ],
      ],
    );
  }
}

/// Security status widget
class SecurityStatusWidget extends StatelessWidget {
  final bool isSecure;
  final String? message;

  const SecurityStatusWidget({
    super.key,
    required this.isSecure,
    this.message,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          isSecure ? Icons.security : Icons.warning,
          color: isSecure ? Colors.green : Colors.orange,
          size: 16,
        ),
        const SizedBox(width: 4),
        Text(
          message ?? (isSecure ? 'Secure' : 'Insecure'),
          style: TextStyle(
            color: isSecure ? Colors.green : Colors.orange,
            fontSize: 12,
          ),
        ),
      ],
    );
  }
}

/// Global security instances
final secureStorage = SecureStorage();
final biometricAuth = BiometricAuth();
final sessionSecurity = SessionSecurity();
final securityMonitor = SecurityMonitor();

/// Initialize security features
Future<void> initializeSecurity() async {
  await secureStorage.initialize();
  sessionSecurity.startSession();
  
  // Log security initialization
  securityMonitor.logSecurityEvent(
    type: SecurityEventType.login,
    description: 'Application security initialized',
    metadata: {'timestamp': DateTime.now().toIso8601String()},
  );
  
  Logger.info('🔐 Security features initialized');
}
