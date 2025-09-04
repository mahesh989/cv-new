import 'package:flutter/material.dart';
import '../services/session_updater.dart';
import '../state/session_state.dart';
import '../theme/app_theme.dart';

class JobInput extends StatefulWidget {
  final TextEditingController jdController;
  final TextEditingController jdUrlController;
  final VoidCallback onExtract;

  const JobInput({
    super.key,
    required this.jdController,
    required this.jdUrlController,
    required this.onExtract,
  });

  @override
  State<JobInput> createState() => _JobInputState();
}

class _JobInputState extends State<JobInput> with TickerProviderStateMixin {
  bool _hasJDText = false;
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;
  bool _isExtracting = false;

  @override
  void initState() {
    super.initState();

    // Initialize animations
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    _pulseAnimation = Tween<double>(
      begin: 1.0,
      end: 1.05,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));

    // Restore both JD text and URL from SessionState during tab switching
    widget.jdController.text = SessionState.jdText ?? '';
    widget.jdUrlController.text = SessionState.jdUrl ?? '';
    _hasJDText = widget.jdController.text.trim().isNotEmpty;

    print(
        '🔄 [JobInput] Restored from SessionState: JD=${widget.jdController.text.length} chars, URL=${widget.jdUrlController.text}');

    // Listen to text changes to update button state
    widget.jdController.addListener(_onJDTextChanged);
    // Listen to URL changes to update SessionState
    widget.jdUrlController.addListener(_onUrlChanged);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    widget.jdController.removeListener(_onJDTextChanged);
    widget.jdUrlController.removeListener(_onUrlChanged);
    super.dispose();
  }

  void _onJDTextChanged() {
    final hasText = widget.jdController.text.trim().isNotEmpty;
    if (hasText != _hasJDText) {
      setState(() {
        _hasJDText = hasText;
      });

      // Pulse animation when text is added
      if (hasText) {
        _pulseController.forward().then((_) => _pulseController.reverse());
      }
    }
  }

  void _onUrlChanged() {
    // Update SessionState when URL changes (for tab switching persistence)
    SessionState.jdUrl = widget.jdUrlController.text;
  }

  @override
  Widget build(BuildContext context) {
    return AppTheme.createCard(
      padding: const EdgeInsets.all(28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionHeader(
            icon: Icons.link_rounded,
            title: '🔗 Job Description URL',
            subtitle: 'Paste the job posting link for automatic extraction',
            gradient: AppTheme.oceanGradient,
          ),
          const SizedBox(height: 16),
          _buildUrlInputSection(),
          const SizedBox(height: 32),
          _buildSectionHeader(
            icon: Icons.description_rounded,
            title: '📝 Job Description Text',
            subtitle: 'Or paste the job description directly',
            gradient: AppTheme.cosmicGradient,
          ),
          const SizedBox(height: 16),
          _buildTextInputSection(),
        ],
      ),
    );
  }

  Widget _buildSectionHeader({
    required IconData icon,
    required String title,
    required String subtitle,
    required LinearGradient gradient,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: gradient,
        borderRadius: AppTheme.buttonRadius,
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryCosmic.withOpacity(0.2),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final isNarrow = constraints.maxWidth < 400;

          if (isNarrow) {
            // Mobile layout - vertical stacking
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        icon,
                        color: Colors.white,
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        title,
                        style: AppTheme.headingSmall.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.w800,
                          fontSize: 16,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  subtitle,
                  style: AppTheme.bodyMedium.copyWith(
                    color: Colors.white.withOpacity(0.9),
                    fontSize: 13,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            );
          } else {
            // Desktop layout - horizontal
            return Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    icon,
                    color: Colors.white,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: AppTheme.headingSmall.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.w800,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        style: AppTheme.bodyMedium.copyWith(
                          color: Colors.white.withOpacity(0.9),
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
              ],
            );
          }
        },
      ),
    );
  }

  Widget _buildUrlInputSection() {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isNarrow = constraints.maxWidth < 500;

        if (isNarrow) {
          // Mobile layout - vertical stacking
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                decoration: BoxDecoration(
                  borderRadius: AppTheme.inputRadius,
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.primaryNeon.withOpacity(0.1),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: TextField(
                  controller: widget.jdUrlController,
                  decoration: AppTheme.getInputDecoration(
                    hintText: '🌐 https://example.com/job-description',
                    prefixIcon: Icon(
                      Icons.link_rounded,
                      color: AppTheme.primaryNeon,
                      size: 20,
                    ),
                  ),
                  style: AppTheme.bodyMedium.copyWith(fontSize: 14),
                ),
              ),
              const SizedBox(height: 12),
              _buildExtractButton(),
            ],
          );
        } else {
          // Desktop layout - horizontal
          return Row(
            children: [
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    borderRadius: AppTheme.inputRadius,
                    boxShadow: [
                      BoxShadow(
                        color: AppTheme.primaryNeon.withOpacity(0.1),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: TextField(
                    controller: widget.jdUrlController,
                    decoration: AppTheme.getInputDecoration(
                      hintText: '🌐 https://example.com/job-description',
                      prefixIcon: Icon(
                        Icons.link_rounded,
                        color: AppTheme.primaryNeon,
                        size: 22,
                      ),
                    ),
                    style: AppTheme.bodyMedium,
                  ),
                ),
              ),
              const SizedBox(width: 16),
              _buildExtractButton(),
            ],
          );
        }
      },
    );
  }

  Widget _buildExtractButton() {
    return AnimatedContainer(
      duration: AppTheme.fastAnimation,
      child: ElevatedButton.icon(
        onPressed: _isExtracting
            ? null
            : () async {
                setState(() => _isExtracting = true);

                widget.onExtract();
                // Update job description and URL in memory only (not persisted)
                SessionUpdater.updateJobDescription(
                  widget.jdController.text,
                  url: widget.jdUrlController.text.trim().isNotEmpty
                      ? widget.jdUrlController.text.trim()
                      : null,
                );

                // Simulate extraction delay for better UX
                await Future.delayed(const Duration(milliseconds: 500));
                if (mounted) setState(() => _isExtracting = false);
              },
        icon: const Icon(Icons.auto_fix_high_rounded, size: 20),
        label: const Text('Extract'),
        style: ElevatedButton.styleFrom(
          backgroundColor: AppTheme.primaryNeon,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: AppTheme.buttonRadius,
          ),
          elevation: 6,
          shadowColor: AppTheme.primaryNeon.withOpacity(0.4),
        ),
      ),
    );
  }

  Widget _buildTextInputSection() {
    return AnimatedBuilder(
      animation: _pulseAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: _hasJDText ? _pulseAnimation.value : 1.0,
          child: Container(
            decoration: BoxDecoration(
              borderRadius: AppTheme.inputRadius,
              boxShadow: _hasJDText
                  ? AppTheme.glowShadow
                  : [
                      BoxShadow(
                        color: AppTheme.primaryCosmic.withOpacity(0.1),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
            ),
            child: TextField(
              controller: widget.jdController,
              maxLines: 8,
              onChanged: (value) => SessionUpdater.updateJobDescription(value,
                  url: widget.jdUrlController.text.trim().isNotEmpty
                      ? widget.jdUrlController.text.trim()
                      : null),
              decoration: AppTheme.getInputDecoration(
                hintText:
                    '✨ Paste the full job description here...\n\n🎯 Include requirements, responsibilities, and qualifications for best results!',
                prefixIcon: const Padding(
                  padding: EdgeInsets.only(top: 12, left: 12),
                  child: Icon(
                    Icons.description_rounded,
                    color: AppTheme.primaryCosmic,
                    size: 22,
                  ),
                ),
              ).copyWith(
                contentPadding: const EdgeInsets.all(20),
              ),
              style: AppTheme.bodyMedium,
            ),
          ),
        );
      },
    );
  }
}
