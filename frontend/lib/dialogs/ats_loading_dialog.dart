import 'package:flutter/material.dart';
import 'dart:async';

class ATSLoadingDialog extends StatefulWidget {
  final VoidCallback? onCancel;
  const ATSLoadingDialog({super.key, this.onCancel});

  @override
  State<ATSLoadingDialog> createState() => _ATSLoadingDialogState();
}

class _ATSLoadingDialogState extends State<ATSLoadingDialog>
    with TickerProviderStateMixin {
  late AnimationController _rotationController;
  late AnimationController _pulseController;
  late AnimationController _textController;

  int _currentStep = 0;
  Timer? _stepTimer;
  bool _isAtFinalStep = false;

  final List<Map<String, dynamic>> _steps = [
    {
      'icon': Icons.upload_file,
      'text': 'Reading CV content...',
      'color': Colors.blue,
      'duration': 2000,
    },
    {
      'icon': Icons.work_outline,
      'text': 'Analyzing job description...',
      'color': Colors.orange,
      'duration': 2500,
    },
    {
      'icon': Icons.psychology,
      'text': 'Extracting technical skills...',
      'color': Colors.purple,
      'duration': 3000,
    },
    {
      'icon': Icons.people_outline,
      'text': 'Identifying soft skills...',
      'color': Colors.green,
      'duration': 2000,
    },
    {
      'icon': Icons.domain,
      'text': 'Processing domain keywords...',
      'color': Colors.teal,
      'duration': 2500,
    },
    {
      'icon': Icons.compare_arrows,
      'text': 'Performing semantic matching...',
      'color': Colors.indigo,
      'duration': 3000,
    },
    {
      'icon': Icons.calculate,
      'text': 'Calculating compatibility scores...',
      'color': Colors.red,
      'duration': 2000,
    },
    {
      'icon': Icons.lightbulb_outline,
      'text': 'Generating improvement tips...',
      'color': Colors.amber,
      'duration': 1500,
    },
  ];

  @override
  void initState() {
    super.initState();

    _rotationController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat();

    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    )..repeat(reverse: true);

    _textController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );

    _startStepAnimation();
  }

  void _startStepAnimation() {
    _stepTimer = Timer.periodic(const Duration(milliseconds: 2800), (timer) {
      if (mounted && _currentStep < _steps.length - 1) {
        setState(() {
          _currentStep++;
        });
      } else if (mounted && _currentStep == _steps.length - 1) {
        setState(() {
          _isAtFinalStep = true;
        });
        // Stay at the last step, keep animating
      }
    });
  }

  @override
  void dispose() {
    _rotationController.dispose();
    _pulseController.dispose();
    _textController.dispose();
    _stepTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final step = _steps[_currentStep];
    final isFinal = _currentStep == _steps.length - 1;
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Stack(
        children: [
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                AnimatedBuilder(
                  animation: _rotationController,
                  builder: (context, child) {
                    // Fun loading icon for final step
                    if (isFinal && _isAtFinalStep) {
                      return Transform.rotate(
                        angle: _rotationController.value * 6.3,
                        child: Text(
                          '🛸', // Surprise emoji! You can swap for others if you like
                          style: const TextStyle(fontSize: 48),
                        ),
                      );
                    }
                    return Icon(
                      step['icon'] as IconData,
                      color: step['color'] as Color,
                      size: 48,
                    );
                  },
                ),
                const SizedBox(height: 16),
                Text(
                  step['text'] as String,
                  style: const TextStyle(
                      fontSize: 18, fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 12),
                if (isFinal && _isAtFinalStep)
                  Padding(
                    padding: const EdgeInsets.only(top: 8.0),
                    child: Text(
                      'Hang tight, almost there!',
                      style:
                          TextStyle(fontSize: 14, color: Colors.blue.shade400),
                    ),
                  ),
                const SizedBox(height: 8),
              ],
            ),
          ),
          // Close button in top right
          Positioned(
            top: 0,
            right: 0,
            child: IconButton(
              icon: const Icon(Icons.close, color: Colors.grey),
              tooltip: 'Cancel',
              onPressed: () {
                Navigator.of(context, rootNavigator: true).pop();
                if (widget.onCancel != null) widget.onCancel!();
              },
            ),
          ),
        ],
      ),
    );
  }

  String _getTipForStep(int step) {
    final tips = [
      'ATS systems scan for exact keyword matches first',
      'Job descriptions reveal company priorities and culture',
      'Technical skills are weighted higher in tech roles',
      'Soft skills show your ability to work in teams',
      'Domain knowledge demonstrates industry expertise',
      'AI matching considers context and synonyms',
      'Scores above 70% typically pass initial screening',
      'Tailored CVs can improve match rates by 40%+',
    ];
    return tips[step % tips.length];
  }
}
