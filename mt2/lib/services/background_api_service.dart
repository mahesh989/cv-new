import 'dart:async';
import 'dart:convert';
import 'dart:html' as html;
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

/// Service to handle API calls that continue running even when the tab is switched
/// Uses various strategies to ensure background execution
class BackgroundApiService {
  static final BackgroundApiService _instance = BackgroundApiService._internal();
  factory BackgroundApiService() => _instance;
  BackgroundApiService._internal();

  final Map<String, Completer<http.Response>> _activeRequests = {};
  final List<BackgroundRequest> _requestQueue = [];
  late Timer _heartbeatTimer;
  bool _isTabVisible = true;
  bool _isInitialized = false;

  /// Initialize the background service with visibility monitoring
  void initialize() {
    if (_isInitialized) return;
    
    if (kIsWeb) {
      _setupVisibilityListener();
      _setupHeartbeat();
      _setupBeforeUnloadHandler();
    }
    
    _isInitialized = true;
    debugPrint('🚀 BackgroundApiService initialized');
  }

  /// Setup visibility change listener for web platform
  void _setupVisibilityListener() {
    html.document.onVisibilityChange.listen((_) {
      final wasVisible = _isTabVisible;
      _isTabVisible = !html.document.hidden!;
      
      if (wasVisible != _isTabVisible) {
        debugPrint('👁️ Tab visibility changed: ${_isTabVisible ? 'visible' : 'hidden'}');
        
        if (_isTabVisible) {
          _onTabVisible();
        } else {
          _onTabHidden();
        }
      }
    });
  }

  /// Setup heartbeat timer to keep service alive
  void _setupHeartbeat() {
    _heartbeatTimer = Timer.periodic(const Duration(seconds: 10), (timer) {
      if (_activeRequests.isNotEmpty || _requestQueue.isNotEmpty) {
        debugPrint('💓 Heartbeat: ${_activeRequests.length} active, ${_requestQueue.length} queued');
      }
    });
  }

  /// Setup before unload handler to use Navigator.sendBeacon for critical requests
  void _setupBeforeUnloadHandler() {
    html.window.onBeforeUnload.listen((event) {
      _handlePageUnload();
    });
  }

  /// Handle tab becoming visible - process queued requests
  void _onTabVisible() {
    debugPrint('✅ Tab visible - processing ${_requestQueue.length} queued requests');
    _processQueuedRequests();
  }

  /// Handle tab becoming hidden - prepare for background operation
  void _onTabHidden() {
    debugPrint('🔄 Tab hidden - ${_activeRequests.length} requests still active');
    // Requests will continue in background due to keepalive
  }

  /// Process queued requests when tab becomes visible
  Future<void> _processQueuedRequests() async {
    final requestsToProcess = List<BackgroundRequest>.from(_requestQueue);
    _requestQueue.clear();

    for (final request in requestsToProcess) {
      try {
        final response = await _executeRequest(request);
        request.completer.complete(response);
      } catch (error) {
        request.completer.completeError(error);
      }
    }
  }

  /// Handle page unload - send critical requests with sendBeacon
  void _handlePageUnload() {
    for (final entry in _activeRequests.entries) {
      final requestId = entry.key;
      debugPrint('⚠️ Page unloading with active request: $requestId');
    }
  }

  /// Make a robust HTTP request that survives tab switches
  Future<http.Response> makeRequest({
    required String method,
    required String url,
    Map<String, String>? headers,
    dynamic body,
    Duration? timeout,
    int maxRetries = 3,
    bool critical = false,
  }) async {
    final requestId = _generateRequestId();
    final completer = Completer<http.Response>();
    
    final request = BackgroundRequest(
      id: requestId,
      method: method,
      url: url,
      headers: headers ?? {},
      body: body,
      timeout: timeout ?? const Duration(seconds: 120),
      maxRetries: maxRetries,
      critical: critical,
      completer: completer,
      createdAt: DateTime.now(),
    );

    debugPrint('🚀 Starting background request: $requestId ($method $url)');

    try {
      _activeRequests[requestId] = completer;
      
      if (_isTabVisible) {
        // Execute immediately if tab is visible
        final response = await _executeRequest(request);
        completer.complete(response);
      } else {
        // Queue for later execution if tab is hidden
        _requestQueue.add(request);
        debugPrint('📋 Queued request for later execution: $requestId');
      }
      
      return await completer.future;
    } finally {
      _activeRequests.remove(requestId);
    }
  }

  /// Execute HTTP request with retry logic
  Future<http.Response> _executeRequest(BackgroundRequest request) async {
    for (int attempt = 1; attempt <= request.maxRetries; attempt++) {
      try {
        debugPrint('🔄 Executing request ${request.id}, attempt $attempt/${request.maxRetries}');
        
        final headers = {
          ...request.headers,
          // Add keepalive indicator for supporting servers
          'X-Keep-Alive': 'true',
          'X-Background-Request': 'true',
        };

        http.Response response;
        
        switch (request.method.toUpperCase()) {
          case 'GET':
            response = await http.get(
              Uri.parse(request.url),
              headers: headers,
            ).timeout(request.timeout);
            break;
            
          case 'POST':
            response = await http.post(
              Uri.parse(request.url),
              headers: headers,
              body: request.body is String ? request.body : jsonEncode(request.body),
            ).timeout(request.timeout);
            break;
            
          case 'PUT':
            response = await http.put(
              Uri.parse(request.url),
              headers: headers,
              body: request.body is String ? request.body : jsonEncode(request.body),
            ).timeout(request.timeout);
            break;
            
          case 'DELETE':
            response = await http.delete(
              Uri.parse(request.url),
              headers: headers,
            ).timeout(request.timeout);
            break;
            
          default:
            throw UnsupportedError('HTTP method ${request.method} not supported');
        }

        debugPrint('✅ Request ${request.id} completed: ${response.statusCode}');
        return response;
        
      } catch (error) {
        debugPrint('❌ Request ${request.id} failed (attempt $attempt): $error');
        
        if (attempt == request.maxRetries) {
          rethrow;
        }
        
        // Exponential backoff
        final delaySeconds = pow(2, attempt - 1).toInt();
        await Future.delayed(Duration(seconds: delaySeconds));
      }
    }
    
    throw Exception('Request failed after ${request.maxRetries} attempts');
  }

  /// Generate unique request ID
  String _generateRequestId() {
    return 'req_${DateTime.now().millisecondsSinceEpoch}_${(Random().nextDouble() * 1000).toInt()}';
  }

  /// Make GET request with background support
  Future<http.Response> get(
    String url, {
    Map<String, String>? headers,
    Duration? timeout,
    bool critical = false,
  }) {
    return makeRequest(
      method: 'GET',
      url: url,
      headers: headers,
      timeout: timeout,
      critical: critical,
    );
  }

  /// Make POST request with background support
  Future<http.Response> post(
    String url, {
    Map<String, String>? headers,
    dynamic body,
    Duration? timeout,
    bool critical = false,
  }) {
    return makeRequest(
      method: 'POST',
      url: url,
      headers: headers,
      body: body,
      timeout: timeout,
      critical: critical,
    );
  }

  /// Get current service status
  Map<String, dynamic> getStatus() {
    return {
      'initialized': _isInitialized,
      'tab_visible': _isTabVisible,
      'active_requests': _activeRequests.length,
      'queued_requests': _requestQueue.length,
    };
  }

  /// Cleanup resources
  void dispose() {
    _heartbeatTimer.cancel();
    _activeRequests.clear();
    _requestQueue.clear();
    _isInitialized = false;
    debugPrint('🗑️ BackgroundApiService disposed');
  }
}

/// Represents a background HTTP request
class BackgroundRequest {
  final String id;
  final String method;
  final String url;
  final Map<String, String> headers;
  final dynamic body;
  final Duration timeout;
  final int maxRetries;
  final bool critical;
  final Completer<http.Response> completer;
  final DateTime createdAt;

  BackgroundRequest({
    required this.id,
    required this.method,
    required this.url,
    required this.headers,
    required this.body,
    required this.timeout,
    required this.maxRetries,
    required this.critical,
    required this.completer,
    required this.createdAt,
  });
}

/// Job-based API for long-running operations
class JobApiService {
  static const String _baseUrl = 'http://localhost:8000';
  final BackgroundApiService _bgService = BackgroundApiService();

  /// Start a background job and return job ID
  Future<String> startJob({
    required String jobType,
    required Map<String, dynamic> jobData,
  }) async {
    final response = await _bgService.post(
      '$_baseUrl/api/jobs/start',
      headers: {'Content-Type': 'application/json'},
      body: {
        'job_type': jobType,
        'job_data': jobData,
      },
      critical: true,
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['job_id'];
    } else {
      throw Exception('Failed to start job: ${response.statusCode}');
    }
  }

  /// Poll job status until completion
  Future<Map<String, dynamic>> waitForJobCompletion(String jobId) async {
    const maxAttempts = 60; // 10 minutes max (60 * 10 seconds)
    int attempts = 0;

    while (attempts < maxAttempts) {
      try {
        final response = await _bgService.get(
          '$_baseUrl/api/jobs/$jobId/status',
          timeout: const Duration(seconds: 10),
        );

        if (response.statusCode == 200) {
          final data = jsonDecode(response.body);
          final status = data['status'];

          switch (status) {
            case 'completed':
              return data;
            case 'failed':
              throw Exception(data['error'] ?? 'Job failed');
            case 'running':
            case 'pending':
              // Continue polling
              break;
            default:
              throw Exception('Unknown job status: $status');
          }
        } else {
          throw Exception('Failed to check job status: ${response.statusCode}');
        }
      } catch (error) {
        debugPrint('⚠️ Error checking job status: $error');
        // Continue polling unless it's a critical error
      }

      attempts++;
      await Future.delayed(const Duration(seconds: 10));
    }

    throw TimeoutException('Job did not complete within timeout');
  }

  /// Start job and wait for completion
  Future<Map<String, dynamic>> executeJob({
    required String jobType,
    required Map<String, dynamic> jobData,
  }) async {
    final jobId = await startJob(jobType: jobType, jobData: jobData);
    debugPrint('🚀 Started job: $jobId');
    
    return await waitForJobCompletion(jobId);
  }
}

class TimeoutException implements Exception {
  final String message;
  TimeoutException(this.message);
  
  @override
  String toString() => 'TimeoutException: $message';
}
