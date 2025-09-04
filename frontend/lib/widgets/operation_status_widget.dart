import 'package:flutter/material.dart';
import '../state/session_state.dart';

class OperationStatusWidget extends StatefulWidget {
  final VoidCallback? onCancel;
  final Function(String operationType)? onOperationComplete;

  const OperationStatusWidget({
    super.key,
    this.onCancel,
    this.onOperationComplete,
  });

  @override
  State<OperationStatusWidget> createState() => _OperationStatusWidgetState();
}

class _OperationStatusWidgetState extends State<OperationStatusWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat(reverse: true);

    _pulseAnimation = Tween<double>(
      begin: 0.8,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!SessionState.isOperationInProgress) {
      return const SizedBox.shrink();
    }

    // Check if operation has expired
    if (SessionState.isOperationExpired()) {
      return _buildExpiredOperationCard();
    }

    return _buildActiveOperationCard();
  }

  Widget _buildActiveOperationCard() {
    final operationType = SessionState.currentOperationType ?? 'Unknown';
    final context = SessionState.operationContext ?? '';
    final duration = SessionState.getOperationDuration();

    final operationInfo = _getOperationInfo(operationType);

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            operationInfo['color'].withOpacity(0.1),
            operationInfo['color'].withOpacity(0.05),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: operationInfo['color'].withOpacity(0.3),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: operationInfo['color'].withOpacity(0.2),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            children: [
              AnimatedBuilder(
                animation: _pulseAnimation,
                builder: (context, child) {
                  return Transform.scale(
                    scale: _pulseAnimation.value,
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: operationInfo['color'].withOpacity(0.2),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Icon(
                        operationInfo['icon'],
                        color: operationInfo['color'],
                        size: 24,
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      operationInfo['title'],
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      operationInfo['subtitle'],
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[600],
                      ),
                    ),
                    if (context.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        context,
                        style: TextStyle(
                          fontSize: 12,
                          color: operationInfo['color'],
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    duration,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[500],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 8),
                  if (widget.onCancel != null)
                    TextButton(
                      onPressed: () {
                        SessionState.completeOperation();
                        widget.onCancel?.call();
                        setState(() {});
                      },
                      style: TextButton.styleFrom(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 4,
                        ),
                      ),
                      child: const Text(
                        'Cancel',
                        style: TextStyle(fontSize: 12),
                      ),
                    ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          LinearProgressIndicator(
            backgroundColor: Colors.grey[200],
            valueColor: AlwaysStoppedAnimation<Color>(operationInfo['color']),
          ),
          const SizedBox(height: 12),
          Text(
            "Operation in progress... You can switch tabs and come back to check progress.",
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
              fontStyle: FontStyle.italic,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildExpiredOperationCard() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.orange.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.orange.withOpacity(0.3),
          width: 2,
        ),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.timer_off,
                  color: Colors.orange,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Operation Timed Out',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'The ${SessionState.currentOperationType ?? "operation"} seems to have taken too long.',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
              ElevatedButton(
                onPressed: () {
                  SessionState.completeOperation();
                  setState(() {});
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange,
                  foregroundColor: Colors.white,
                ),
                child: const Text('Clear'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Map<String, dynamic> _getOperationInfo(String operationType) {
    switch (operationType) {
      case 'cv_generation':
        return {
          'icon': Icons.auto_awesome,
          'color': Colors.blue,
          'title': 'Generating CV',
          'subtitle': 'Creating your tailored CV...',
        };
      case 'ats_testing':
        return {
          'icon': Icons.analytics,
          'color': Colors.green,
          'title': 'Running ATS Test',
          'subtitle': 'Analyzing CV compatibility...',
        };
      case 'cv_improvement':
        return {
          'icon': Icons.trending_up,
          'color': Colors.purple,
          'title': 'Improving CV',
          'subtitle': 'Applying enhancements...',
        };
      default:
        return {
          'icon': Icons.hourglass_empty,
          'color': Colors.grey,
          'title': 'Processing',
          'subtitle': 'Working on your request...',
        };
    }
  }
}
