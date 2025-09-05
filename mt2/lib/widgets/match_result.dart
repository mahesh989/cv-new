import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class MatchResultWidget extends StatefulWidget {
  final String raw;
  final List<String> keywords;
  final List<String> keyPhrases;

  const MatchResultWidget({
    super.key,
    required this.raw,
    this.keywords = const [],
    this.keyPhrases = const [],
  });

  @override
  State<MatchResultWidget> createState() => _MatchResultWidgetState();
}

class _MatchResultWidgetState extends State<MatchResultWidget>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: AppTheme.normalAnimation,
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: AppTheme.smoothCurve,
    ));

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0.0, 0.3),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: AppTheme.smoothCurve,
    ));

    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  // Highlights markdown-style **bold** text
  TextSpan _highlightedText(String raw) {
    final boldRegExp = RegExp(r'\*\*(.*?)\*\*');
    final spans = <TextSpan>[];
    int lastIndex = 0;

    for (final match in boldRegExp.allMatches(raw)) {
      if (match.start > lastIndex) {
        spans.add(TextSpan(
          text: raw.substring(lastIndex, match.start),
          style: AppTheme.bodyMedium,
        ));
      }
      spans.add(TextSpan(
        text: match.group(1),
        style: AppTheme.bodyMedium.copyWith(
          fontWeight: FontWeight.w800,
          color: AppTheme.primaryCosmic,
        ),
      ));
      lastIndex = match.end;
    }

    if (lastIndex < raw.length) {
      spans.add(TextSpan(
        text: raw.substring(lastIndex),
        style: AppTheme.bodyMedium,
      ));
    }

    return TextSpan(children: spans);
  }

  @override
  Widget build(BuildContext context) {
    print('\n${'='*80}');
    print('📱 [UI_WIDGET] MATCH RESULT WIDGET - BUILD');
    print('='*80);
    print('📝 Raw text length: ${widget.raw.length}');
    print('🏷️ Keywords count: ${widget.keywords.length}');
    print('🔑 Key phrases count: ${widget.keyPhrases.length}');
    
    if (widget.raw.isNotEmpty) {
      print('\n📄 [UI_WIDGET] Raw analysis content preview (first 400 chars):');
      print('-'*60);
      print(widget.raw.length > 400 ? widget.raw.substring(0, 400) : widget.raw);
      print('-'*60);
      
      print('\n📊 [UI_WIDGET] Raw analysis full content (for UI output saving):');
      print('='*60);
      print('EXACT_UI_OUTPUT_START');
      print(widget.raw);
      print('EXACT_UI_OUTPUT_END');
      print('='*60);
    }
    
    if (widget.keywords.isNotEmpty) {
      print('\n🏷️ [UI_WIDGET] Keywords displayed: ${widget.keywords}');
    }
    
    if (widget.keyPhrases.isNotEmpty) {
      print('\n🔑 [UI_WIDGET] Key phrases displayed: ${widget.keyPhrases}');
    }
    
    // If nothing to show, return an empty SizedBox
    if (widget.raw.isEmpty &&
        widget.keywords.isEmpty &&
        widget.keyPhrases.isEmpty) {
      print('⚠️ [UI_WIDGET] Nothing to display - returning empty widget');
      print('='*80 + '\n');
      return const SizedBox.shrink();
    }
    
    print('✅ [UI_WIDGET] Building match result display widget');
    print('='*80 + '\n');
    
    return AnimatedBuilder(
      animation: _animationController,
      builder: (context, child) {
        return FadeTransition(
          opacity: _fadeAnimation,
          child: SlideTransition(
            position: _slideAnimation,
            child: AppTheme.createCard(
              padding: const EdgeInsets.all(28),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (widget.raw.isNotEmpty) _buildMatchResultSection(),
                  if (widget.keywords.isNotEmpty) ...[
                    if (widget.raw.isNotEmpty) const SizedBox(height: 32),
                    _buildKeywordsSection(),
                  ],
                  if (widget.keyPhrases.isNotEmpty) ...[
                    if (widget.raw.isNotEmpty || widget.keywords.isNotEmpty)
                      const SizedBox(height: 32),
                    _buildKeyPhrasesSection(),
                  ],
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildMatchResultSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader(
          icon: Icons.psychology_rounded,
          title: '🧠 Match Analysis',
          subtitle: 'AI-powered compatibility assessment',
          gradient: AppTheme.cosmicGradient,
        ),
        const SizedBox(height: 20),
        Container(
          width: double.infinity,
          constraints: const BoxConstraints(
            minHeight: 300, // Minimum height to ensure good visibility
          ),
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            borderRadius: AppTheme.inputRadius, // Match TextField
            boxShadow: [
              BoxShadow(
                color: AppTheme.primaryCosmic.withOpacity(0.1),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
            // Optional: add glow if you want to match the glowing state
            // If you want to match the glow only when content is present, you can add a condition
            // color: Colors.white, // (if TextField has a background color)
          ),
          child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            child: SelectableText.rich(
              _highlightedText(widget.raw),
              style: AppTheme.bodyMedium.copyWith(
                height: 1.6, // Better line spacing for readability
                fontSize: 15, // Slightly larger font for better readability
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildKeywordsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader(
          icon: Icons.local_offer_rounded,
          title: '📌 Keywords',
          subtitle: 'Key terms extracted from analysis',
          gradient: AppTheme.forestGradient,
        ),
        const SizedBox(height: 20),
        _buildChipGrid(widget.keywords, 'technical_skills'),
      ],
    );
  }

  Widget _buildKeyPhrasesSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader(
          icon: Icons.key_rounded,
          title: '🔑 Key Phrases',
          subtitle: 'Important phrases and concepts',
          gradient: AppTheme.royalGradient,
        ),
        const SizedBox(height: 20),
        _buildChipGrid(
          widget.keyPhrases.map((kp) {
            return kp.replaceFirst(RegExp(r'^\s*\d+\.\s*'), '');
          }).toList(),
          'soft_skills',
        ),
      ],
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

  Widget _buildChipGrid(List<String> items, String chipType) {
    final backgroundColor =
        AppTheme.chipColors[chipType] ?? AppTheme.neutralGray100;
    final textColor =
        AppTheme.chipTextColors[chipType] ?? AppTheme.neutralGray700;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: backgroundColor.withOpacity(0.3),
        borderRadius: AppTheme.cardRadius,
        border: Border.all(
          color: backgroundColor,
          width: 1.5,
        ),
      ),
      child: Wrap(
        spacing: 12,
        runSpacing: 12,
        children: items
            .map((item) => _buildStylishChip(item, backgroundColor, textColor))
            .toList(),
      ),
    );
  }

  Widget _buildStylishChip(
      String text, Color backgroundColor, Color textColor) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            backgroundColor,
            backgroundColor.withOpacity(0.8),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: AppTheme.pillRadius,
        boxShadow: [
          BoxShadow(
            color: backgroundColor.withOpacity(0.4),
            blurRadius: 6,
            offset: const Offset(0, 3),
          ),
        ],
        border: Border.all(
          color: backgroundColor.withOpacity(0.6),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(
              color: textColor,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 8),
          Text(
            text,
            style: AppTheme.bodyMedium.copyWith(
              color: textColor,
              fontWeight: FontWeight.w600,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }
}
