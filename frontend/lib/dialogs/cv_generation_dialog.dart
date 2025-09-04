import 'package:flutter/material.dart';
import 'dart:async';
import 'dart:math' as math;
import '../theme/app_theme.dart';

enum CVGenerationType {
  initial,
  regeneration,
  atsRegeneration,
  atsImprovement,
}

class CVGenerationDialog extends StatefulWidget {
  final CVGenerationType type;
  final String? additionalContext;

  const CVGenerationDialog({
    super.key,
    required this.type,
    this.additionalContext,
  });

  @override
  State<CVGenerationDialog> createState() => _CVGenerationDialogState();
}

class _CVGenerationDialogState extends State<CVGenerationDialog>
    with TickerProviderStateMixin {
  late AnimationController _mainController;
  late AnimationController _particleController;
  late AnimationController _textController;
  late AnimationController _breathingController;

  int _currentStep = 0;
  Timer? _stepTimer;
  List<Particle> _particles = [];

  @override
  void initState() {
    super.initState();

    _mainController = AnimationController(
      duration: AppTheme.slowAnimation,
      vsync: this,
    )..repeat();

    _particleController = AnimationController(
      duration: const Duration(seconds: 4),
      vsync: this,
    )..repeat();

    _textController = AnimationController(
      duration: AppTheme.normalAnimation,
      vsync: this,
    );

    _breathingController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat(reverse: true);

    _initializeParticles();
    _startStepAnimation();
  }

  void _initializeParticles() {
    final random = math.Random();
    _particles = List.generate(15, (index) {
      return Particle(
        x: random.nextDouble(),
        y: random.nextDouble(),
        speed: 0.5 + random.nextDouble() * 0.5,
        size: 2 + random.nextDouble() * 4,
        color: _getParticleColor(index),
      );
    });
  }

  Color _getParticleColor(int index) {
    final colors = [
      AppTheme.primaryCosmic.withOpacity(0.6),
      AppTheme.primaryAurora.withOpacity(0.6),
      AppTheme.primaryNeon.withOpacity(0.6),
      AppTheme.primaryElectric.withOpacity(0.6),
      AppTheme.successGreen.withOpacity(0.6),
      AppTheme.warningOrange.withOpacity(0.6),
    ];
    return colors[index % colors.length];
  }

  List<Map<String, dynamic>> get _steps {
    switch (widget.type) {
      case CVGenerationType.initial:
        return [
          {
            'icon': Icons.upload_file,
            'text': 'Analyzing your CV structure...',
            'color': AppTheme.primaryCosmic,
            'emoji': '📄',
          },
          {
            'icon': Icons.work_outline,
            'text': 'Understanding job requirements...',
            'color': AppTheme.warningOrange,
            'emoji': '🎯',
          },
          {
            'icon': Icons.psychology,
            'text': 'AI is thinking creatively...',
            'color': AppTheme.primaryAurora,
            'emoji': '🧠',
          },
          {
            'icon': Icons.auto_fix_high,
            'text': 'Tailoring your experience...',
            'color': AppTheme.successGreen,
            'emoji': '✨',
          },
          {
            'icon': Icons.format_paint,
            'text': 'Optimizing keywords...',
            'color': AppTheme.primaryNeon,
            'emoji': '🎨',
          },
          {
            'icon': Icons.rocket_launch,
            'text': 'Finalizing your perfect CV...',
            'color': AppTheme.errorRed,
            'emoji': '🚀',
          },
        ];

      case CVGenerationType.regeneration:
        return [
          {
            'icon': Icons.refresh,
            'text': 'Loading previous version...',
            'color': AppTheme.primaryElectric,
            'emoji': '🔄',
          },
          {
            'icon': Icons.edit_note,
            'text': 'Applying your feedback...',
            'color': AppTheme.warningOrange,
            'emoji': '📝',
          },
          {
            'icon': Icons.psychology,
            'text': 'AI is reimagining content...',
            'color': AppTheme.primaryAurora,
            'emoji': '💭',
          },
          {
            'icon': Icons.tune,
            'text': 'Fine-tuning improvements...',
            'color': AppTheme.successGreen,
            'emoji': '⚙️',
          },
          {
            'icon': Icons.star,
            'text': 'Adding that special touch...',
            'color': AppTheme.warningOrange,
            'emoji': '⭐',
          },
        ];

      case CVGenerationType.atsRegeneration:
        return [
          {
            'icon': Icons.document_scanner,
            'text': 'Scanning CV structure...',
            'color': AppTheme.primaryCosmic,
            'emoji': '📄',
          },
          {
            'icon': Icons.search,
            'text': 'Identifying job keywords...',
            'color': AppTheme.warningOrange,
            'emoji': '🎯',
          },
          {
            'icon': Icons.compare,
            'text': 'Performing semantic matching...',
            'color': AppTheme.primaryAurora,
            'emoji': '⚖️',
          },
          {
            'icon': Icons.calculate,
            'text': 'Computing ATS scores...',
            'color': AppTheme.successGreen,
            'emoji': '📈',
          },
          {
            'icon': Icons.assignment,
            'text': 'Compiling ATS report...',
            'color': AppTheme.primaryNeon,
            'emoji': '📋',
          },
        ];

      case CVGenerationType.atsImprovement:
        return [
          {
            'icon': Icons.analytics,
            'text': 'Analyzing ATS feedback...',
            'color': AppTheme.primaryCosmic,
            'emoji': '📊',
          },
          {
            'icon': Icons.lightbulb,
            'text': 'Processing your instructions...',
            'color': AppTheme.warningOrange,
            'emoji': '💡',
          },
          {
            'icon': Icons.auto_fix_high,
            'text': 'Enhancing CV content...',
            'color': AppTheme.primaryAurora,
            'emoji': '✨',
          },
          {
            'icon': Icons.trending_up,
            'text': 'Optimizing ATS compatibility...',
            'color': AppTheme.successGreen,
            'emoji': '📈',
          },
          {
            'icon': Icons.check_circle,
            'text': 'Finalizing improved CV...',
            'color': AppTheme.primaryNeon,
            'emoji': '✅',
          },
        ];
    }
  }

  void _startStepAnimation() {
    _stepTimer = Timer.periodic(const Duration(milliseconds: 3000), (timer) {
      if (mounted && _currentStep < _steps.length - 1) {
        setState(() {
          _currentStep++;
        });
        _textController.reset();
        _textController.forward();
      }
    });
  }

  @override
  void dispose() {
    _mainController.dispose();
    _particleController.dispose();
    _textController.dispose();
    _breathingController.dispose();
    _stepTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final currentStepData = _steps[_currentStep];

    bool isATS = widget.type == CVGenerationType.atsRegeneration;

    return Dialog(
      backgroundColor: Colors.transparent,
      child: AppTheme.createCard(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Animated particles background or custom ATS animation
            SizedBox(
              height: 120,
              child: isATS
                  ? Center(
                      child: TweenAnimationBuilder<double>(
                        duration: const Duration(milliseconds: 1500),
                        tween: Tween(begin: 0.0, end: 1.0),
                        builder: (context, value, child) {
                          return Transform.rotate(
                            angle: value * 2 * math.pi,
                            child: Container(
                              width: 80,
                              height: 80,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                gradient: SweepGradient(
                                  colors: [
                                    AppTheme.primaryCosmic,
                                    AppTheme.primaryNeon,
                                    AppTheme.warningOrange,
                                    AppTheme.primaryCosmic,
                                  ],
                                  stops: const [0.0, 0.3, 0.7, 1.0],
                                ),
                              ),
                              child: Center(
                                child: Container(
                                  width: 50,
                                  height: 50,
                                  decoration: const BoxDecoration(
                                    color: Colors.white,
                                    shape: BoxShape.circle,
                                  ),
                                  child: Icon(
                                    Icons.analytics,
                                    color: AppTheme.primaryCosmic,
                                    size: 32,
                                  ),
                                ),
                              ),
                            ),
                          );
                        },
                        onEnd: () {
                          // Restart the animation for continuous effect
                          Future.delayed(const Duration(milliseconds: 100), () {
                            if (mounted) setState(() {});
                          });
                        },
                      ),
                    )
                  : Stack(
                      children: [
                        // Particles
                        AnimatedBuilder(
                          animation: _particleController,
                          builder: (context, child) {
                            return CustomPaint(
                              size: const Size(double.infinity, 120),
                              painter: ParticlePainter(
                                  _particles, _particleController.value),
                            );
                          },
                        ),
                        // Main animated icon
                        Center(
                          child: AnimatedBuilder(
                            animation: _mainController,
                            builder: (context, child) {
                              return Transform.rotate(
                                angle: _mainController.value * 2 * math.pi,
                                child: AnimatedBuilder(
                                  animation: _breathingController,
                                  builder: (context, child) {
                                    return Transform.scale(
                                      scale: 1.0 +
                                          (_breathingController.value * 0.3),
                                      child: Container(
                                        width: 80,
                                        height: 80,
                                        decoration: BoxDecoration(
                                          gradient: RadialGradient(
                                            colors: [
                                              currentStepData['color']
                                                  .withOpacity(0.2),
                                              currentStepData['color']
                                                  .withOpacity(0.1),
                                              Colors.transparent,
                                            ],
                                          ),
                                          shape: BoxShape.circle,
                                          border: Border.all(
                                            color: currentStepData['color'],
                                            width: 3,
                                          ),
                                        ),
                                        child: Stack(
                                          alignment: Alignment.center,
                                          children: [
                                            Icon(
                                              Icons.auto_fix_high,
                                              size: 35,
                                              color: currentStepData['color'],
                                            ),
                                            Positioned(
                                              top: 5,
                                              right: 5,
                                              child: Text(
                                                currentStepData['emoji'],
                                                style: const TextStyle(
                                                    fontSize: 16),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    );
                                  },
                                ),
                              );
                            },
                          ),
                        ),
                      ],
                    ),
            ),

            const SizedBox(height: 16),

            // Title with type-specific text
            Text(
              _getTitleForType(),
              style: AppTheme.headingMedium.copyWith(
                color: currentStepData['color'],
              ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 16),

            // Current step with enhanced animation
            isATS
                ? TweenAnimationBuilder<double>(
                    duration: const Duration(milliseconds: 1000),
                    tween: Tween(begin: 0.8, end: 1.0),
                    builder: (context, value, child) {
                      return Transform.scale(
                        scale: value,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 12),
                          decoration: BoxDecoration(
                            color: currentStepData['color'].withOpacity(0.1),
                            borderRadius: AppTheme.inputRadius,
                            border: Border.all(
                              color: currentStepData['color'].withOpacity(0.3),
                            ),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                currentStepData['emoji'],
                                style: const TextStyle(fontSize: 20),
                              ),
                              const SizedBox(width: 12),
                              Flexible(
                                child: Text(
                                  currentStepData['text'],
                                  style: AppTheme.bodyLarge.copyWith(
                                    color: currentStepData['color'],
                                    fontWeight: FontWeight.w600,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                    onEnd: () {
                      // Restart the pulse animation
                      Future.delayed(const Duration(milliseconds: 100), () {
                        if (mounted) setState(() {});
                      });
                    },
                  )
                : AnimatedBuilder(
                    animation: _textController,
                    builder: (context, child) {
                      return Opacity(
                        opacity: _textController.value,
                        child: Transform.translate(
                          offset: Offset(0, 15 * (1 - _textController.value)),
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 16, vertical: 12),
                            decoration: BoxDecoration(
                              color: currentStepData['color'].withOpacity(0.1),
                              borderRadius: AppTheme.inputRadius,
                              border: Border.all(
                                color:
                                    currentStepData['color'].withOpacity(0.3),
                              ),
                            ),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(
                                  currentStepData['emoji'],
                                  style: const TextStyle(fontSize: 20),
                                ),
                                const SizedBox(width: 12),
                                Flexible(
                                  child: Text(
                                    currentStepData['text'],
                                    style: AppTheme.bodyLarge.copyWith(
                                      color: currentStepData['color'],
                                      fontWeight: FontWeight.w600,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  ),

            const SizedBox(height: 20),

            // Enhanced progress indicator
            Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(10),
                boxShadow: [
                  BoxShadow(
                    color: currentStepData['color'].withOpacity(0.3),
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: LinearProgressIndicator(
                  value: (_currentStep + 1) / _steps.length,
                  backgroundColor: AppTheme.neutralGray200,
                  valueColor:
                      AlwaysStoppedAnimation<Color>(currentStepData['color']),
                  minHeight: 8,
                ),
              ),
            ),

            const SizedBox(height: 8),

            Text(
              'Step ${_currentStep + 1} of ${_steps.length}',
              style: AppTheme.bodySmall.copyWith(
                fontWeight: FontWeight.w500,
              ),
            ),

            const SizedBox(height: 16),

            // Context-aware tip
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    AppTheme.primaryCosmic.withOpacity(0.05),
                    AppTheme.primaryAurora.withOpacity(0.05),
                  ],
                ),
                borderRadius: AppTheme.inputRadius,
                border:
                    Border.all(color: AppTheme.primaryCosmic.withOpacity(0.2)),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.lightbulb,
                    color: AppTheme.warningOrange,
                    size: 18,
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      _getTipForType(),
                      style: AppTheme.bodySmall.copyWith(
                        color: AppTheme.primaryCosmic,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getTitleForType() {
    switch (widget.type) {
      case CVGenerationType.initial:
        return '🎨 Crafting Your Tailored CV';
      case CVGenerationType.regeneration:
        return '🔄 Regenerating Your CV';
      case CVGenerationType.atsRegeneration:
        return '🚀 ATS-Optimizing Your CV';
      case CVGenerationType.atsImprovement:
        return '✨ Enhancing Your CV';
    }
  }

  String _getTipForType() {
    switch (widget.type) {
      case CVGenerationType.initial:
        return 'AI is analyzing 1000+ successful CVs to create your perfect match!';
      case CVGenerationType.regeneration:
        return 'Each regeneration makes your CV 15% more targeted to the role!';
      case CVGenerationType.atsRegeneration:
        return 'ATS-optimized CVs have 3x higher chance of reaching human recruiters!';
      case CVGenerationType.atsImprovement:
        return 'Incorporating ATS insights to boost your CV\'s performance!';
    }
  }
}

class Particle {
  double x;
  double y;
  final double speed;
  final double size;
  final Color color;

  Particle({
    required this.x,
    required this.y,
    required this.speed,
    required this.size,
    required this.color,
  });
}

class ParticlePainter extends CustomPainter {
  final List<Particle> particles;
  final double animationValue;

  ParticlePainter(this.particles, this.animationValue);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint();

    for (final particle in particles) {
      // Update particle position
      particle.y = (particle.y + particle.speed * 0.01) % 1.0;
      particle.x = (particle.x +
              math.sin(animationValue * 2 * math.pi + particle.y * 10) *
                  0.002) %
          1.0;

      paint.color = particle.color.withOpacity(0.6);
      canvas.drawCircle(
        Offset(particle.x * size.width, particle.y * size.height),
        particle.size,
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
