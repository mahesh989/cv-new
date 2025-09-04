/// Core architecture patterns and foundation classes for the Flutter app
/// This provides a structured foundation for building maintainable Flutter applications

library architecture;

import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

/// Base class for all business logic controllers
/// Provides consistent lifecycle management and error handling
abstract class BaseController extends ChangeNotifier {
  bool _isDisposed = false;
  bool _isLoading = false;
  String? _error;

  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasError => _error != null;
  bool get isDisposed => _isDisposed;

  /// Set loading state and notify listeners
  @protected
  void setLoading(bool loading) {
    if (_isDisposed) return;
    _isLoading = loading;
    notifyListeners();
  }

  /// Set error state and notify listeners
  @protected
  void setError(String? error) {
    if (_isDisposed) return;
    _error = error;
    notifyListeners();
  }

  /// Clear error state
  void clearError() {
    setError(null);
  }

  /// Execute async operation with automatic loading and error handling
  @protected
  Future<T> executeAsync<T>(
    Future<T> Function() operation, {
    bool showLoading = true,
    String? errorMessage,
  }) async {
    try {
      if (showLoading) setLoading(true);
      clearError();
      
      final result = await operation();
      return result;
    } catch (e, stackTrace) {
      debugPrint('❌ Controller Error: $e');
      debugPrint('Stack trace: $stackTrace');
      
      setError(errorMessage ?? e.toString());
      rethrow;
    } finally {
      if (showLoading) setLoading(false);
    }
  }

  @override
  void dispose() {
    _isDisposed = true;
    super.dispose();
  }
}

/// Result wrapper for operations that can succeed or fail
class Result<T> {
  final T? data;
  final String? error;
  final bool isSuccess;

  const Result.success(this.data)
      : error = null,
        isSuccess = true;

  const Result.failure(this.error)
      : data = null,
        isSuccess = false;

  bool get isFailure => !isSuccess;

  /// Transform successful result with a mapper function
  Result<R> map<R>(R Function(T data) mapper) {
    if (isSuccess && data != null) {
      try {
        return Result.success(mapper(data!));
      } catch (e) {
        return Result.failure(e.toString());
      }
    }
    return Result.failure(error);
  }

  /// Handle both success and failure cases
  R fold<R>(
    R Function(String error) onFailure,
    R Function(T data) onSuccess,
  ) {
    if (isSuccess && data != null) {
      return onSuccess(data!);
    } else {
      return onFailure(error ?? 'Unknown error');
    }
  }
}

/// Base class for all data models with validation
abstract class BaseModel {
  /// Validate the model instance
  List<String> validate() => [];

  /// Check if model is valid
  bool get isValid => validate().isEmpty;

  /// Convert to JSON representation
  Map<String, dynamic> toJson();

  /// Create copy with modified fields
  BaseModel copyWith();
}

/// Repository pattern interface for data access
abstract class BaseRepository {
  /// Execute operation with error handling
  @protected
  Future<Result<T>> safeExecute<T>(Future<T> Function() operation) async {
    try {
      final result = await operation();
      return Result.success(result);
    } catch (e) {
      debugPrint('❌ Repository Error: $e');
      return Result.failure(e.toString());
    }
  }
}

/// Use case pattern for business logic
abstract class UseCase<TInput, TOutput> {
  Future<Result<TOutput>> execute(TInput input);
}

/// Simple dependency injection container
class ServiceLocator {
  static final ServiceLocator _instance = ServiceLocator._internal();
  factory ServiceLocator() => _instance;
  ServiceLocator._internal();

  final Map<Type, dynamic> _services = {};
  final Map<Type, dynamic Function()> _factories = {};

  /// Register a singleton service
  void registerSingleton<T>(T service) {
    _services[T] = service;
  }

  /// Register a factory for creating services
  void registerFactory<T>(T Function() factory) {
    _factories[T] = factory;
  }

  /// Get a service instance
  T get<T>() {
    // Check for singleton first
    if (_services.containsKey(T)) {
      return _services[T] as T;
    }

    // Check for factory
    if (_factories.containsKey(T)) {
      return _factories[T]!() as T;
    }

    throw Exception('Service of type $T not registered');
  }

  /// Check if service is registered
  bool isRegistered<T>() {
    return _services.containsKey(T) || _factories.containsKey(T);
  }

  /// Clear all services (useful for testing)
  void clear() {
    _services.clear();
    _factories.clear();
  }
}

// Global service locator instance
final serviceLocator = ServiceLocator();

/// Mixin for widgets that need loading and error states
mixin LoadingStateMixin<T extends StatefulWidget> on State<T> {
  bool _isLoading = false;
  String? _error;

  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasError => _error != null;

  void setLoading(bool loading) {
    if (mounted) {
      setState(() {
        _isLoading = loading;
      });
    }
  }

  void setError(String? error) {
    if (mounted) {
      setState(() {
        _error = error;
      });
    }
  }

  void clearError() => setError(null);

  /// Execute async operation with loading and error handling
  Future<T?> executeWithLoading<T>(
    Future<T> Function() operation, {
    String? errorMessage,
  }) async {
    try {
      setLoading(true);
      clearError();
      
      final result = await operation();
      return result;
    } catch (e) {
      setError(errorMessage ?? e.toString());
      return null;
    } finally {
      setLoading(false);
    }
  }

  /// Build loading widget
  Widget buildLoadingWidget() {
    return const Center(
      child: CircularProgressIndicator(),
    );
  }

  /// Build error widget
  Widget buildErrorWidget({VoidCallback? onRetry}) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.error_outline,
            size: 48,
            color: Theme.of(context).colorScheme.error,
          ),
          const SizedBox(height: 16),
          Text(
            error ?? 'An error occurred',
            style: Theme.of(context).textTheme.bodyLarge,
            textAlign: TextAlign.center,
          ),
          if (onRetry != null) ...[
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: onRetry,
              child: const Text('Retry'),
            ),
          ],
        ],
      ),
    );
  }
}

/// Base page widget with common functionality
abstract class BasePage extends StatefulWidget {
  const BasePage({super.key});

  @override
  BasePageState createState();
}

abstract class BasePageState<T extends BasePage> extends State<T>
    with LoadingStateMixin {
  
  /// Page title for app bar
  String get pageTitle => '';

  /// Whether to show app bar
  bool get showAppBar => true;

  /// Custom app bar actions
  List<Widget> get appBarActions => [];

  /// Build the main content
  Widget buildContent(BuildContext context);

  /// Called when page is first loaded
  @protected
  void onPageLoad() {}

  /// Called when page is refreshed
  @protected
  Future<void> onRefresh() async {}

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      onPageLoad();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: showAppBar
          ? AppBar(
              title: Text(pageTitle),
              actions: appBarActions,
            )
          : null,
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (isLoading) {
      return buildLoadingWidget();
    }

    if (hasError) {
      return buildErrorWidget(
        onRetry: () async {
          clearError();
          await onRefresh();
        },
      );
    }

    return RefreshIndicator(
      onRefresh: onRefresh,
      child: buildContent(context),
    );
  }
}

/// Custom exception types for better error handling
class ValidationException implements Exception {
  final String message;
  final Map<String, String> fieldErrors;

  const ValidationException(this.message, [this.fieldErrors = const {}]);

  @override
  String toString() => message;
}

class NetworkException implements Exception {
  final String message;
  final int? statusCode;

  const NetworkException(this.message, [this.statusCode]);

  @override
  String toString() => message;
}

class CacheException implements Exception {
  final String message;

  const CacheException(this.message);

  @override
  String toString() => message;
}

/// Logging utility with different levels
enum LogLevel { debug, info, warning, error }

class Logger {
  static const String _prefix = '[CV_Agent]';

  static void debug(String message, [Object? error]) {
    if (kDebugMode) {
      debugPrint('$_prefix [DEBUG] $message');
      if (error != null) debugPrint('Error: $error');
    }
  }

  static void info(String message) {
    debugPrint('$_prefix [INFO] $message');
  }

  static void warning(String message, [Object? error]) {
    debugPrint('$_prefix [WARNING] $message');
    if (error != null) debugPrint('Error: $error');
  }

  static void error(String message, [Object? error, StackTrace? stackTrace]) {
    debugPrint('$_prefix [ERROR] $message');
    if (error != null) debugPrint('Error: $error');
    if (stackTrace != null && kDebugMode) {
      debugPrint('Stack trace: $stackTrace');
    }
  }
}

/// Performance monitoring utility
class PerformanceMonitor {
  static final Map<String, Stopwatch> _stopwatches = {};

  /// Start timing an operation
  static void startTiming(String operationName) {
    _stopwatches[operationName] = Stopwatch()..start();
  }

  /// Stop timing and log the result
  static Duration stopTiming(String operationName) {
    final stopwatch = _stopwatches.remove(operationName);
    if (stopwatch != null) {
      stopwatch.stop();
      final duration = stopwatch.elapsed;
      Logger.info('⏱️ $operationName took ${duration.inMilliseconds}ms');
      return duration;
    }
    return Duration.zero;
  }

  /// Execute operation with automatic timing
  static Future<T> time<T>(
    String operationName,
    Future<T> Function() operation,
  ) async {
    startTiming(operationName);
    try {
      final result = await operation();
      return result;
    } finally {
      stopTiming(operationName);
    }
  }
}

/// Extension methods for common operations
extension ContextExtensions on BuildContext {
  /// Show snack bar with consistent styling
  void showSnackBar(String message, {bool isError = false}) {
    ScaffoldMessenger.of(this).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError
            ? Theme.of(this).colorScheme.error
            : Theme.of(this).colorScheme.primary,
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    );
  }

  /// Show loading dialog
  void showLoadingDialog([String? message]) {
    showDialog(
      context: this,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        content: Row(
          children: [
            const CircularProgressIndicator(),
            const SizedBox(width: 16),
            Text(message ?? 'Loading...'),
          ],
        ),
      ),
    );
  }

  /// Hide loading dialog
  void hideLoadingDialog() {
    Navigator.of(this).pop();
  }
}

/// Utility for safe async operations
class AsyncUtils {
  /// Execute multiple async operations concurrently
  static Future<List<T>> concurrent<T>(List<Future<T>> futures) async {
    return await Future.wait(futures);
  }

  /// Execute async operation with timeout
  static Future<T> withTimeout<T>(
    Future<T> future,
    Duration timeout, {
    String? timeoutMessage,
  }) async {
    return await future.timeout(
      timeout,
      onTimeout: () => throw TimeoutException(
        timeoutMessage ?? 'Operation timed out',
        timeout,
      ),
    );
  }

  /// Retry an async operation with exponential backoff
  static Future<T> retry<T>(
    Future<T> Function() operation, {
    int maxRetries = 3,
    Duration baseDelay = const Duration(seconds: 1),
  }) async {
    int attempts = 0;
    while (true) {
      try {
        return await operation();
      } catch (e) {
        attempts++;
        if (attempts >= maxRetries) rethrow;
        
        final delay = Duration(
          milliseconds: (baseDelay.inMilliseconds * (1 << attempts)).toInt(),
        );
        
        Logger.warning('Retry attempt $attempts after ${delay.inMilliseconds}ms');
        await Future.delayed(delay);
      }
    }
  }
}
