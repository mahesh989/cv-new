import 'package:flutter/material.dart';
import '../models/preextracted_comparison.dart';
import 'preextracted_parser.dart';

/// Utility class for formatting text with markdown-style formatting
class TextFormatter {
  /// Creates a formatted TextSpan from markdown-style text
  static TextSpan formatText({
    required String text,
    MaterialColor? baseColor,
    double baseFontSize = 13,
    Color? baseTextColor,
    bool isAnalyzeMatch = false,
  }) {
    final lines = text.split('\n');
    final List<TextSpan> spans = [];
    final defaultTextColor = baseTextColor ?? Colors.grey.shade700;
    final defaultBaseColor = baseColor ?? Colors.blue;

    for (final line in lines) {
      if (line.trim().isEmpty) {
        spans.add(const TextSpan(text: '\n'));
        continue;
      }

      // Debug logging
      debugPrint('🔍 [TEXT_FORMATTER] Processing line: "$line"');

      // Handle decision indicators with emojis (for analyze match)
      if (isAnalyzeMatch && _isDecisionIndicator(line)) {
        debugPrint('🔍 [TEXT_FORMATTER] Detected decision indicator');
        // Parse bold text within decision indicators
        final decisionSpan =
            _parseBoldText(line, baseFontSize + 2, _getDecisionColor(line));
        // Override the color for all spans in the decision indicator
        final List<TextSpan> coloredSpans = [];
        if (decisionSpan.children != null) {
          for (final child in decisionSpan.children!) {
            if (child is TextSpan) {
              coloredSpans.add(TextSpan(
                text: child.text,
                style: (child.style ?? TextStyle()).copyWith(
                  fontSize: baseFontSize + 2,
                  fontWeight: FontWeight.bold,
                  color: _getDecisionColor(line),
                ),
              ));
            }
          }
        }
        spans.add(TextSpan(children: coloredSpans));
      }
      // Handle main headers (##) - including those with bold text
      else if (line.startsWith('## ')) {
        debugPrint('🔍 [TEXT_FORMATTER] Detected main header');
        final headerText = line.substring(3);
        spans.add(_parseBoldText(headerText, baseFontSize + 3,
            isAnalyzeMatch ? Colors.black87 : defaultBaseColor.shade700));
        spans.add(const TextSpan(text: '\n'));
      }
      // Handle sub headers (###) - including those with bold text
      else if (line.startsWith('### ')) {
        debugPrint('🔍 [TEXT_FORMATTER] Detected sub header');
        final headerText = line.substring(4);
        spans.add(_parseBoldText(headerText, baseFontSize + 1,
            isAnalyzeMatch ? Colors.grey.shade800 : defaultBaseColor.shade600));
      }
      // Handle numbered lists - including those with bold text
      else if (RegExp(r'^\d+\.\s').hasMatch(line)) {
        debugPrint('🔍 [TEXT_FORMATTER] Detected numbered list');

        // Extract the number and content
        final match = RegExp(r'^(\d+\.\s)(.*)').firstMatch(line);
        if (match != null) {
          final numberPart = match.group(1) ?? '';
          final contentPart = match.group(2) ?? '';

          // Check if content contains bold text
          if (contentPart.contains('**')) {
            // Parse bold text within numbered list item
            final List<TextSpan> listSpans = [];
            listSpans.add(TextSpan(
              text: numberPart,
              style: TextStyle(
                fontSize: baseFontSize,
                color: defaultTextColor,
              ),
            ));

            // Parse the content for bold formatting
            final contentSpan =
                _parseBoldText(contentPart, baseFontSize, defaultTextColor);
            if (contentSpan.children != null) {
              for (final child in contentSpan.children!) {
                if (child is TextSpan) {
                  listSpans.add(child);
                }
              }
            }

            spans.add(TextSpan(children: listSpans));
          } else {
            // Regular numbered list item without bold text
            spans.add(TextSpan(
              text: '$line\n',
              style: TextStyle(
                fontSize: baseFontSize,
                color: defaultTextColor,
                height: 1.5,
              ),
            ));
          }
        } else {
          // Fallback for malformed numbered lists
          spans.add(TextSpan(
            text: '$line\n',
            style: TextStyle(
              fontSize: baseFontSize,
              color: defaultTextColor,
              height: 1.5,
            ),
          ));
        }
      }
      // Handle bullet points (- and *) - including those with bold text
      else if (line.startsWith('- ') || line.startsWith('*   ')) {
        debugPrint('🔍 [TEXT_FORMATTER] Detected bullet point');
        String bulletContent;
        if (line.startsWith('- ')) {
          bulletContent = line.substring(2);
        } else {
          // Handle *   format (with spaces)
          bulletContent = line.substring(4);
        }

        // Check if bullet content contains bold text
        if (bulletContent.contains('**')) {
          // Parse bold text within bullet point
          final List<TextSpan> bulletSpans = [];
          bulletSpans.add(TextSpan(
            text: '• ',
            style: TextStyle(
              fontSize: baseFontSize,
              color: defaultTextColor,
            ),
          ));

          // Parse the content after the bullet for bold formatting
          final contentSpan =
              _parseBoldText(bulletContent, baseFontSize, defaultTextColor);
          if (contentSpan.children != null) {
            for (final child in contentSpan.children!) {
              if (child is TextSpan) {
                bulletSpans.add(child);
              }
            }
          }

          spans.add(TextSpan(children: bulletSpans));
        } else {
          // Regular bullet point without bold text
          spans.add(TextSpan(
            text: '• $bulletContent\n',
            style: TextStyle(
              fontSize: baseFontSize,
              color: defaultTextColor,
              height: 1.5,
            ),
          ));
        }
      }
      // Handle probability indicators (for analyze match)
      else if (isAnalyzeMatch && line.contains('%')) {
        debugPrint('🔍 [TEXT_FORMATTER] Detected probability indicator');
        // Parse bold text within probability indicators
        final probabilitySpan =
            _parseBoldText(line, baseFontSize, Colors.blue.shade700);
        // Override the color for all spans in the probability indicator
        final List<TextSpan> coloredSpans = [];
        if (probabilitySpan.children != null) {
          for (final child in probabilitySpan.children!) {
            if (child is TextSpan) {
              coloredSpans.add(TextSpan(
                text: child.text,
                style: (child.style ?? TextStyle()).copyWith(
                  fontSize: baseFontSize,
                  fontWeight: FontWeight.w600,
                  color: Colors.blue.shade700,
                ),
              ));
            }
          }
        }
        spans.add(TextSpan(children: coloredSpans));
      }
      // Handle bold text (**text**) - this should come after other checks
      else if (line.contains('**')) {
        debugPrint('🔍 [TEXT_FORMATTER] Detected bold text');
        spans.add(_parseBoldText(line, baseFontSize, defaultTextColor));
      }
      // Regular text
      else {
        debugPrint('🔍 [TEXT_FORMATTER] Processing as regular text');
        spans.add(TextSpan(
          text: '$line\n',
          style: TextStyle(
            fontSize: baseFontSize,
            color: defaultTextColor,
            height: 1.4,
          ),
        ));
      }
    }

    return TextSpan(children: spans);
  }

  /// Checks if a line contains decision indicators
  static bool _isDecisionIndicator(String line) {
    return line.contains('🟢 STRONG PURSUE') ||
        line.contains('🟡 STRATEGIC PURSUE') ||
        line.contains('🟠 CALCULATED RISK') ||
        line.contains('🔴 REALISTIC REJECT');
  }

  /// Gets color for decision indicators
  static Color _getDecisionColor(String line) {
    if (line.contains('🟢')) return Colors.green.shade600;
    if (line.contains('🟡')) return Colors.orange.shade600;
    if (line.contains('🟠')) return Colors.deepOrange.shade600;
    if (line.contains('🔴')) return Colors.red.shade600;
    return Colors.blue.shade600;
  }

  /// Parses bold text within a line - completely rewritten approach
  static TextSpan _parseBoldText(
      String line, double fontSize, Color defaultColor) {
    final List<TextSpan> spans = [];

    debugPrint('🔍 [BOLD_PARSER] Parsing line: "$line"');

    // Convert the line to a list of characters for easier processing
    final chars = line.split('');
    final List<String> currentText = [];
    bool isBold = false;
    int i = 0;

    while (i < chars.length) {
      // Check for ** pattern
      if (i < chars.length - 1 && chars[i] == '*' && chars[i + 1] == '*') {
        // Add any accumulated text
        if (currentText.isNotEmpty) {
          spans.add(TextSpan(
            text: currentText.join(''),
            style: TextStyle(
              fontSize: fontSize,
              fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
              color: isBold ? Colors.grey.shade800 : defaultColor,
            ),
          ));
          currentText.clear();
        }

        // Toggle bold state
        isBold = !isBold;
        i += 2; // Skip both asterisks
      } else {
        // Regular character
        currentText.add(chars[i]);
        i++;
      }
    }

    // Add any remaining text
    if (currentText.isNotEmpty) {
      spans.add(TextSpan(
        text: currentText.join(''),
        style: TextStyle(
          fontSize: fontSize,
          fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
          color: isBold ? Colors.grey.shade800 : defaultColor,
        ),
      ));
    }

    spans.add(const TextSpan(text: '\n'));
    return TextSpan(children: spans);
  }
}

/// Reusable widget for formatted text display
class FormattedTextWidget extends StatelessWidget {
  final String text;
  final MaterialColor? baseColor;
  final double fontSize;
  final Color? textColor;
  final bool isAnalyzeMatch;
  final double lineHeight;

  const FormattedTextWidget({
    super.key,
    required this.text,
    this.baseColor,
    this.fontSize = 13,
    this.textColor,
    this.isAnalyzeMatch = false,
    this.lineHeight = 1.4,
  });

  @override
  Widget build(BuildContext context) {
    return SelectableText.rich(
      TextFormatter.formatText(
        text: text,
        baseColor: baseColor,
        baseFontSize: fontSize,
        baseTextColor: textColor,
        isAnalyzeMatch: isAnalyzeMatch,
      ),
      style: TextStyle(
        fontSize: fontSize,
        color: textColor ?? Colors.grey.shade700,
        height: lineHeight,
      ),
    );
  }
}

/// Specialized widget for analyze match text formatting
class AnalyzeMatchFormattedText extends StatelessWidget {
  final String text;

  const AnalyzeMatchFormattedText({
    super.key,
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    return FormattedTextWidget(
      text: text,
      fontSize: 13,
      isAnalyzeMatch: true,
    );
  }
}

/// Specialized widget for skills analysis text formatting
class SkillsAnalysisFormattedText extends StatelessWidget {
  final String text;
  final MaterialColor baseColor;

  const SkillsAnalysisFormattedText({
    super.key,
    required this.text,
    required this.baseColor,
  });

  @override
  Widget build(BuildContext context) {
    return FormattedTextWidget(
      text: text,
      baseColor: baseColor,
      fontSize: 13,
      isAnalyzeMatch: false,
    );
  }
}

/// Specialized widget for AI recommendations text formatting
class RecommendationFormattedText extends StatelessWidget {
  final String text;

  const RecommendationFormattedText({
    super.key,
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    return FormattedTextWidget(
      text: text,
      fontSize: 14,
      isAnalyzeMatch: false, // Uses general markdown formatting
      lineHeight: 1.6,
    );
  }
}

class SkillsAnalysisAdapters {
  static PreextractedComparisonResult parsePreextractedRaw(String raw) {
    // ignore: avoid_print
    print('[SkillsAnalysisAdapters] parsePreextractedRaw length=${raw.length}');
    return PreextractedParser.parse(raw);
  }
}
