import 'package:flutter/material.dart';
import 'dart:async';
import '../theme/app_theme.dart';

class CVAnalysisDialog extends StatefulWidget {
  final VoidCallback? onCancel;
  const CVAnalysisDialog({super.key, this.onCancel});

  @override
  State<CVAnalysisDialog> createState() => _CVAnalysisDialogState();
}

class _CVAnalysisDialogState extends State<CVAnalysisDialog>
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
      'color': AppTheme.primaryCosmic,
      'emoji': '📄',
    },
    {
      'icon': Icons.work_outline,
      'text': 'Analyzing job requirements...',
      'color': AppTheme.warningOrange,
      'emoji': '🎯',
    },
    {
      'icon': Icons.psychology,
      'text': 'Extracting technical skills...',
      'color': AppTheme.primaryAurora,
      'emoji': '🧠',
    },
    {
      'icon': Icons.people_outline,
      'text': 'Identifying soft skills...',
      'color': AppTheme.successGreen,
      'emoji': '👥',
    },
    {
      'icon': Icons.domain,
      'text': 'Processing domain keywords...',
      'color': AppTheme.primaryNeon,
      'emoji': '🏢',
    },
    {
      'icon': Icons.compare_arrows,
      'text': 'Performing semantic matching...',
      'color': AppTheme.primaryElectric,
      'emoji': '🔄',
    },
    {
      'icon': Icons.calculate,
      'text': 'Calculating compatibility scores...',
      'color': AppTheme.errorRed,
      'emoji': '📊',
    },
    {
      'icon': Icons.lightbulb_outline,
      'text': 'Generating insights...',
      'color': AppTheme.accentGolden,
      'emoji': '💡',
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
    _textController.forward();
  }

  void _startStepAnimation() {
    _stepTimer = Timer.periodic(const Duration(milliseconds: 2800), (timer) {
      if (mounted && _currentStep < _steps.length - 1) {
        setState(() {
          _currentStep++;
        });
        _textController.reset();
        _textController.forward();
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

  String _getTipForStep(int step) {
    final tips = [
      "💡 Tip: Use keywords from the job description in your CV",
      "🎯 Tip: Quantify your achievements with numbers and metrics",
      "🚀 Tip: Tailor your skills section to match job requirements",
      "✨ Tip: Use action verbs to describe your experience",
      "📈 Tip: Include relevant certifications and training",
      "🔍 Tip: Use industry-specific terminology appropriately",
      "💪 Tip: Highlight transferable skills for career changes",
      "🎨 Tip: Keep formatting clean and ATS-friendly",
    ];
    return tips[step % tips.length];
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
                          '🦄', // Surprise emoji! You can swap for others if you like
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
                FadeTransition(
                  opacity: _textController,
                  child: Text(
                    step['text'] as String,
                    style: const TextStyle(
                        fontSize: 18, fontWeight: FontWeight.bold),
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 12),
                if (isFinal && _isAtFinalStep)
                  Padding(
                    padding: const EdgeInsets.only(top: 8.0),
                    child: Text(
                      'Hang tight, almost there!',
                      style: TextStyle(
                          fontSize: 14, color: Colors.purple.shade400),
                    ),
                  ),
                const SizedBox(height: 8),
                Text(
                  _getTipForStep(_currentStep),
                  style: const TextStyle(fontSize: 14, color: Colors.grey),
                  textAlign: TextAlign.center,
                ),
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

  Color _getParticleColor(int index) {
    final colors = [
      AppTheme.primaryCosmic.withValues(alpha: 0.6),
      AppTheme.primaryAurora.withValues(alpha: 0.6),
      AppTheme.primaryNeon.withValues(alpha: 0.6),
      AppTheme.primaryElectric.withValues(alpha: 0.6),
      AppTheme.successGreen.withValues(alpha: 0.6),
      AppTheme.warningOrange.withValues(alpha: 0.6),
      AppTheme.accentGolden.withValues(alpha: 0.6),
      AppTheme.errorRed.withValues(alpha: 0.6),
    ];
    return colors[index % colors.length];
  }
}
