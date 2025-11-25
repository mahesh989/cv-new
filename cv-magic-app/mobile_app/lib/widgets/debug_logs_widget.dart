import 'package:flutter/material.dart';
import '../services/debug_logs_service.dart';
import 'dart:async';

class DebugLogsWidget extends StatefulWidget {
  final String? filterKeyword;
  final int lines;
  final bool autoRefresh;

  const DebugLogsWidget({
    Key? key,
    this.filterKeyword,
    this.lines = 200,
    this.autoRefresh = true,
  }) : super(key: key);

  @override
  State<DebugLogsWidget> createState() => _DebugLogsWidgetState();
}

class _DebugLogsWidgetState extends State<DebugLogsWidget> {
  List<Map<String, dynamic>> _logs = [];
  bool _isLoading = true;
  String? _error;
  Timer? _refreshTimer;
  StreamSubscription<Map<String, dynamic>>? _logSubscription;

  @override
  void initState() {
    super.initState();
    _loadLogs();
    if (widget.autoRefresh) {
      _startAutoRefresh();
    }
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    _logSubscription?.cancel();
    super.dispose();
  }

  void _loadLogs() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final result = await debugLogsService.getRecentLogs(
        lines: widget.lines,
        filterKeyword: widget.filterKeyword,
      );

      if (mounted) {
        setState(() {
          _isLoading = false;
          if (result['success'] == true) {
            _logs = List<Map<String, dynamic>>.from(result['logs'] ?? []);
            _error = null;
          } else {
            _error = result['error'] ?? 'Failed to load logs';
            _logs = [];
          }
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _error = 'Error: $e';
          _logs = [];
        });
      }
    }
  }

  void _startAutoRefresh() {
    _logSubscription = debugLogsService
        .pollLogs(
          lines: widget.lines,
          filterKeyword: widget.filterKeyword,
          interval: const Duration(seconds: 2),
        )
        .listen((result) {
      if (mounted) {
        setState(() {
          if (result['success'] == true) {
            _logs = List<Map<String, dynamic>>.from(result['logs'] ?? []);
            _error = null;
          } else {
            _error = result['error'];
          }
        });
      }
    });
  }

  String _getLogLevel(String message) {
    if (message.contains('❌') || message.contains('ERROR')) return 'error';
    if (message.contains('⚠️') || message.contains('WARNING')) return 'warning';
    if (message.contains('✅') || message.contains('SUCCESS')) return 'success';
    if (message.contains('🔍') || message.contains('INFO')) return 'info';
    return 'default';
  }

  Color _getLogColor(String level) {
    switch (level) {
      case 'error':
        return Colors.red.shade300;
      case 'warning':
        return Colors.orange.shade300;
      case 'success':
        return Colors.green.shade300;
      case 'info':
        return Colors.blue.shade300;
      default:
        return Colors.grey.shade300;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.black87,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey.shade900,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(8),
                topRight: Radius.circular(8),
              ),
            ),
            child: Row(
              children: [
                const Icon(Icons.terminal, color: Colors.white, size: 20),
                const SizedBox(width: 8),
                Text(
                  widget.filterKeyword != null
                      ? 'Debug Logs: ${widget.filterKeyword}'
                      : 'Debug Logs',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.refresh, color: Colors.white, size: 20),
                  onPressed: _loadLogs,
                  tooltip: 'Refresh logs',
                ),
                if (widget.autoRefresh)
                  Icon(
                    Icons.sync,
                    color: Colors.green.shade300,
                    size: 16,
                  ),
              ],
            ),
          ),
          // Logs content
          Expanded(
            child: _isLoading
                ? const Center(
                    child: CircularProgressIndicator(
                      color: Colors.white,
                    ),
                  )
                : _error != null
                    ? Center(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.error_outline,
                                  color: Colors.red.shade300, size: 48),
                              const SizedBox(height: 16),
                              Text(
                                _error!,
                                style: TextStyle(color: Colors.red.shade300),
                                textAlign: TextAlign.center,
                              ),
                              const SizedBox(height: 16),
                              ElevatedButton(
                                onPressed: _loadLogs,
                                child: const Text('Retry'),
                              ),
                            ],
                          ),
                        ),
                      )
                    : _logs.isEmpty
                        ? const Center(
                            child: Text(
                              'No logs found',
                              style: TextStyle(color: Colors.grey),
                            ),
                          )
                        : ListView.builder(
                            reverse: true, // Show newest first
                            itemCount: _logs.length,
                            itemBuilder: (context, index) {
                              final log = _logs[index];
                              final message = log['message'] as String? ?? '';
                              final level = _getLogLevel(message);
                              final color = _getLogColor(level);

                              return Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 12,
                                  vertical: 4,
                                ),
                                decoration: BoxDecoration(
                                  border: Border(
                                    left: BorderSide(
                                      color: color,
                                      width: 3,
                                    ),
                                  ),
                                ),
                                child: SelectableText(
                                  message,
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 11,
                                    fontFamily: 'monospace',
                                  ),
                                ),
                              );
                            },
                          ),
          ),
        ],
      ),
    );
  }
}

