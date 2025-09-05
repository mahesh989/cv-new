/// Comprehensive error handling and user experience enhancements
/// Provides consistent error handling, loading states, and user-friendly interactions

library error_handling;

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:async';
import 'dart:io';
import 'architecture.dart';

/// Global error handler for the application
class GlobalErrorHandler {
  static final GlobalErrorHandler _instance = GlobalErrorHandler._internal();
  factory GlobalErrorHandler() => _instance;
  GlobalErrorHandler._internal();

  /// Initialize global error handling
  static void initialize() {
    // Handle Flutter framework errors
    FlutterError.onError = (FlutterErrorDetails details) {
      Logger.error(
        'Flutter Error: ${details.exception}',
        details.exception,
        details.stack,
      );

      // In release mode, report to crash analytics
      if (kReleaseMode) {
        _reportError(details.exception, details.stack);
      }
    };

    // Handle platform dispatcher errors
    PlatformDispatcher.instance.onError = (error, stack) {
      Logger.error('Platform Error: $error', error, stack);
      if (kReleaseMode) {
        _reportError(error, stack);
      }
      return true;
    };
  }

  /// Report error to analytics service
  static Future<void> _reportError(dynamic error, StackTrace? stackTrace) async {
    try {
      // TODO: Integrate with your preferred crash reporting service
      // Examples: Firebase Crashlytics, Sentry, Bugsnag
      debugPrint('📊 Error reported to analytics: $error');
    } catch (e) {
      debugPrint('Failed to report error: $e');
    }
  }
}

/// Enhanced error types with user-friendly messages
enum ErrorType {
  network,
  validation,
  authentication,
  authorization,
  fileSystem,
  parsing,
  timeout,
  unknown,
}

class AppError {
  final ErrorType type;
  final String message;
  final String userMessage;
  final String? code;
  final dynamic originalError;
  final StackTrace? stackTrace;

  const AppError({
    required this.type,
    required this.message,
    required this.userMessage,
    this.code,
    this.originalError,
    this.stackTrace,
  });

  /// Create network error
  factory AppError.network(String message, {String? code}) {
    return AppError(
      type: ErrorType.network,
      message: message,
      userMessage: 'Connection problem. Please check your internet connection.',
      code: code,
    );
  }

  /// Create validation error
  factory AppError.validation(String message, {String? code}) {
    return AppError(
      type: ErrorType.validation,
      message: message,
      userMessage: 'Please check your input and try again.',
      code: code,
    );
  }

  /// Create authentication error
  factory AppError.authentication(String message, {String? code}) {
    return AppError(
      type: ErrorType.authentication,
      message: message,
      userMessage: 'Authentication failed. Please sign in again.',
      code: code,
    );
  }

  /// Create timeout error
  factory AppError.timeout(String message, {String? code}) {
    return AppError(
      type: ErrorType.timeout,
      message: message,
      userMessage: 'Operation timed out. Please try again.',
      code: code,
    );
  }

  /// Create file system error
  factory AppError.fileSystem(String message, {String? code}) {
    return AppError(
      type: ErrorType.fileSystem,
      message: message,
      userMessage: 'File operation failed. Please try again.',
      code: code,
    );
  }

  /// Create unknown error
  factory AppError.unknown(String message, {String? code, dynamic originalError}) {
    return AppError(
      type: ErrorType.unknown,
      message: message,
      userMessage: 'Something went wrong. Please try again.',
      code: code,
      originalError: originalError,
    );
  }

  /// Create error from exception
  factory AppError.fromException(dynamic exception) {
    if (exception is SocketException) {
      return AppError.network('Network error: ${exception.message}');
    } else if (exception is TimeoutException) {
      return AppError.timeout('Operation timed out: ${exception.message}');
    } else if (exception is FormatException) {
      return AppError.parsing('Data parsing error: ${exception.message}');
    } else if (exception is PlatformException) {
      return AppError(
        type: ErrorType.unknown,
        message: 'Platform error: ${exception.message}',
        userMessage: 'A system error occurred. Please try again.',
        code: exception.code,
      );
    } else {
      return AppError.unknown(
        'Unexpected error: ${exception.toString()}',
        originalError: exception,
      );
    }
  }

  /// Create parsing error
  factory AppError.parsing(String message, {String? code}) {
    return AppError(
      type: ErrorType.parsing,
      message: message,
      userMessage: 'Data processing error. Please try again.',
      code: code,
    );
  }

  @override
  String toString() => message;
}

/// Loading state management with different types
enum LoadingType {
  initial,
  refresh,
  loadMore,
  submit,
  upload,
  process,
}

class LoadingState {
  final bool isLoading;
  final LoadingType type;
  final String message;
  final double? progress;

  const LoadingState({
    required this.isLoading,
    this.type = LoadingType.initial,
    this.message = 'Loading...',
    this.progress,
  });

  /// Create initial loading state
  factory LoadingState.initial([String message = 'Loading...']) {
    return LoadingState(
      isLoading: true,
      type: LoadingType.initial,
      message: message,
    );
  }

  /// Create refresh loading state
  factory LoadingState.refresh([String message = 'Refreshing...']) {
    return LoadingState(
      isLoading: true,
      type: LoadingType.refresh,
      message: message,
    );
  }

  /// Create submit loading state
  factory LoadingState.submit([String message = 'Submitting...']) {
    return LoadingState(
      isLoading: true,
      type: LoadingType.submit,
      message: message,
    );
  }

  /// Create upload loading state with progress
  factory LoadingState.upload(double progress, [String message = 'Uploading...']) {
    return LoadingState(
      isLoading: true,
      type: LoadingType.upload,
      message: message,
      progress: progress,
    );
  }

  /// Create process loading state
  factory LoadingState.process(String message, {double? progress}) {
    return LoadingState(
      isLoading: true,
      type: LoadingType.process,
      message: message,
      progress: progress,
    );
  }

  /// Create idle state (not loading)
  factory LoadingState.idle() {
    return const LoadingState(
      isLoading: false,
      message: '',
    );
  }
}

/// Enhanced loading widget with different styles
class LoadingWidget extends StatelessWidget {
  final LoadingState state;
  final bool showMessage;
  final Color? color;
  final double size;

  const LoadingWidget({
    super.key,
    required this.state,
    this.showMessage = true,
    this.color,
    this.size = 40.0,
  });

  @override
  Widget build(BuildContext context) {
    if (!state.isLoading) {
      return const SizedBox.shrink();
    }

    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (state.progress != null) ...[
            SizedBox(
              width: size * 2,
              height: size * 2,
              child: CircularProgressIndicator(
                value: state.progress,
                strokeWidth: 4,
                color: color ?? Theme.of(context).primaryColor,
              ),
            ),
            if (state.progress! > 0) ...[
              const SizedBox(height: 8),
              Text(
                '${(state.progress! * 100).toInt()}%',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ] else ...[
            SizedBox(
              width: size,
              height: size,
              child: CircularProgressIndicator(
                strokeWidth: 3,
                color: color ?? Theme.of(context).primaryColor,
              ),
            ),
          ],
          if (showMessage && state.message.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text(
              state.message,
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
          ],
        ],
      ),
    );
  }
}

/// Enhanced error display widget
class ErrorWidget extends StatelessWidget {
  final AppError error;
  final VoidCallback? onRetry;
  final bool showDetails;
  final String? customMessage;

  const ErrorWidget({
    super.key,
    required this.error,
    this.onRetry,
    this.showDetails = false,
    this.customMessage,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              _getErrorIcon(),
              size: 64,
              color: _getErrorColor(context),
            ),
            const SizedBox(height: 16),
            Text(
              customMessage ?? error.userMessage,
              style: Theme.of(context).textTheme.titleMedium,
              textAlign: TextAlign.center,
            ),
            if (showDetails && kDebugMode) ...[
              const SizedBox(height: 8),
              Text(
                error.message,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey[600],
                ),
                textAlign: TextAlign.center,
              ),
            ],
            if (error.code != null) ...[
              const SizedBox(height: 8),
              Text(
                'Error Code: ${error.code}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey[600],
                ),
              ),
            ],
            if (onRetry != null) ...[
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: const Text('Try Again'),
              ),
            ],
          ],
        ),
      ),
    );
  }

  IconData _getErrorIcon() {
    switch (error.type) {
      case ErrorType.network:
        return Icons.wifi_off;
      case ErrorType.validation:
        return Icons.warning;
      case ErrorType.authentication:
        return Icons.lock;
      case ErrorType.authorization:
        return Icons.security;
      case ErrorType.fileSystem:
        return Icons.folder_off;
      case ErrorType.parsing:
        return Icons.error;
      case ErrorType.timeout:
        return Icons.timer_off;
      case ErrorType.unknown:
        return Icons.error_outline;
    }
  }

  Color _getErrorColor(BuildContext context) {
    switch (error.type) {
      case ErrorType.network:
        return Colors.orange;
      case ErrorType.validation:
        return Colors.amber;
      case ErrorType.authentication:
      case ErrorType.authorization:
        return Colors.red;
      case ErrorType.timeout:
        return Colors.blue;
      default:
        return Theme.of(context).colorScheme.error;
    }
  }
}

/// Empty state widget for when no data is available
class EmptyStateWidget extends StatelessWidget {
  final IconData icon;
  final String title;
  final String message;
  final VoidCallback? onAction;
  final String? actionLabel;

  const EmptyStateWidget({
    super.key,
    required this.icon,
    required this.title,
    required this.message,
    this.onAction,
    this.actionLabel,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 64,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              title,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                color: Colors.grey[700],
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              message,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
            if (onAction != null && actionLabel != null) ...[
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: onAction,
                icon: const Icon(Icons.add),
                label: Text(actionLabel!),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// Offline indicator widget
class OfflineIndicator extends StatelessWidget {
  final bool isOnline;

  const OfflineIndicator({super.key, required this.isOnline});

  @override
  Widget build(BuildContext context) {
    if (isOnline) return const SizedBox.shrink();

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      color: Colors.red[600],
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.wifi_off,
            color: Colors.white,
            size: 16,
          ),
          const SizedBox(width: 8),
          Text(
            'No internet connection',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }
}

/// Snackbar helper for consistent messaging
class SnackBarHelper {
  static void showSuccess(BuildContext context, String message) {
    _showSnackBar(context, message, Colors.green, Icons.check_circle);
  }

  static void showError(BuildContext context, String message) {
    _showSnackBar(context, message, Colors.red, Icons.error);
  }

  static void showWarning(BuildContext context, String message) {
    _showSnackBar(context, message, Colors.orange, Icons.warning);
  }

  static void showInfo(BuildContext context, String message) {
    _showSnackBar(context, message, Colors.blue, Icons.info);
  }

  static void _showSnackBar(
    BuildContext context,
    String message,
    Color color,
    IconData icon,
  ) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(icon, color: Colors.white),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                message,
                style: const TextStyle(color: Colors.white),
              ),
            ),
          ],
        ),
        backgroundColor: color,
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        action: SnackBarAction(
          label: 'Dismiss',
          textColor: Colors.white,
          onPressed: () {
            ScaffoldMessenger.of(context).hideCurrentSnackBar();
          },
        ),
      ),
    );
  }
}

/// Enhanced dialog helper
class DialogHelper {
  /// Show confirmation dialog
  static Future<bool> showConfirmation(
    BuildContext context, {
    required String title,
    required String message,
    String confirmText = 'Confirm',
    String cancelText = 'Cancel',
    Color? confirmColor,
  }) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: Text(cancelText),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: confirmColor != null
                ? ElevatedButton.styleFrom(backgroundColor: confirmColor)
                : null,
            child: Text(confirmText),
          ),
        ],
      ),
    );

    return result ?? false;
  }

  /// Show error dialog
  static Future<void> showError(
    BuildContext context,
    AppError error, {
    VoidCallback? onRetry,
  }) async {
    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.error, color: Colors.red),
            SizedBox(width: 8),
            Text('Error'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(error.userMessage),
            if (kDebugMode && error.message != error.userMessage) ...[
              const SizedBox(height: 8),
              Text(
                'Technical details: ${error.message}',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
          if (onRetry != null)
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                onRetry();
              },
              child: const Text('Retry'),
            ),
        ],
      ),
    );
  }

  /// Show loading dialog
  static void showLoading(
    BuildContext context, {
    String message = 'Loading...',
    bool dismissible = false,
  }) {
    showDialog(
      context: context,
      barrierDismissible: dismissible,
      builder: (context) => WillPopScope(
        onWillPop: () async => dismissible,
        child: AlertDialog(
          content: Row(
            children: [
              const CircularProgressIndicator(),
              const SizedBox(width: 20),
              Expanded(child: Text(message)),
            ],
          ),
        ),
      ),
    );
  }

  /// Hide loading dialog
  static void hideLoading(BuildContext context) {
    Navigator.of(context).pop();
  }
}

/// Retry mechanism for failed operations
class RetryMechanism {
  /// Execute operation with retry logic
  static Future<T> execute<T>(
    Future<T> Function() operation, {
    int maxRetries = 3,
    Duration delay = const Duration(seconds: 1),
    bool Function(dynamic error)? shouldRetry,
  }) async {
    int attempts = 0;
    
    while (attempts < maxRetries) {
      try {
        return await operation();
      } catch (e) {
        attempts++;
        
        // Check if we should retry this error
        if (shouldRetry != null && !shouldRetry(e)) {
          rethrow;
        }
        
        // If this was the last attempt, rethrow
        if (attempts >= maxRetries) {
          rethrow;
        }
        
        // Wait before retrying
        await Future.delayed(delay * attempts);
        Logger.warning('Retrying operation (attempt $attempts): $e');
      }
    }
    
    throw Exception('Max retries exceeded');
  }

  /// Determine if error should be retried
  static bool shouldRetryError(dynamic error) {
    if (error is SocketException) return true;
    if (error is TimeoutException) return true;
    if (error is HttpException) {
      // Retry on 5xx server errors
      return error.message.contains('5');
    }
    return false;
  }
}

/// Connection status monitor
class ConnectionMonitor {
  static final ConnectionMonitor _instance = ConnectionMonitor._internal();
  factory ConnectionMonitor() => _instance;
  ConnectionMonitor._internal();

  final StreamController<bool> _connectionController = StreamController<bool>.broadcast();
  bool _isOnline = true;

  Stream<bool> get onConnectionChanged => _connectionController.stream;
  bool get isOnline => _isOnline;

  /// Initialize connection monitoring
  void initialize() {
    // TODO: Implement actual network monitoring
    // You can use packages like connectivity_plus for real network monitoring
    _checkConnection();
  }

  /// Check current connection status
  Future<void> _checkConnection() async {
    try {
      // Simple connectivity check
      final result = await InternetAddress.lookup('google.com');
      final newStatus = result.isNotEmpty && result[0].rawAddress.isNotEmpty;
      
      if (newStatus != _isOnline) {
        _isOnline = newStatus;
        _connectionController.add(_isOnline);
        Logger.info('Connection status changed: ${_isOnline ? 'Online' : 'Offline'}');
      }
    } catch (e) {
      if (_isOnline) {
        _isOnline = false;
        _connectionController.add(_isOnline);
        Logger.info('Connection lost');
      }
    }
  }

  void dispose() {
    _connectionController.close();
  }
}
