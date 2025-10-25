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
      // Handle new LITMUS_TEST_PROMPT format fields
      else if (isAnalyzeMatch && _isLitmusField(line)) {
        debugPrint('🔍 [TEXT_FORMATTER] Detected LITMUS field');
        
        // Format the field name to remove underscores
        String formattedLine = line;
        if (line.contains('CRITICAL_MISSING:')) {
          formattedLine = line.replaceFirst('CRITICAL_MISSING:', _formatFieldName('CRITICAL_MISSING'));
        } else if (line.contains('IMPLICIT_LIKELY:')) {
          formattedLine = line.replaceFirst('IMPLICIT_LIKELY:', _formatFieldName('IMPLICIT_LIKELY'));
        } else if (line.contains('LEARNABLE_GAPS:')) {
          formattedLine = line.replaceFirst('LEARNABLE_GAPS:', _formatFieldName('LEARNABLE_GAPS'));
        } else if (line.contains('BLOCKER_FOUND:')) {
          formattedLine = line.replaceFirst('BLOCKER_FOUND:', _formatFieldName('BLOCKER_FOUND'));
        }
        
        spans.add(TextSpan(
          text: '$formattedLine\n',
          style: TextStyle(
            fontSize: baseFontSize,
            fontWeight: FontWeight.w600,
            color: _getLitmusFieldColor(line),
            height: 1.4,
          ),
        ));
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
    // New LITMUS_TEST_PROMPT format
    if (line.contains('DECISION: PROCEED') ||
        line.contains('DECISION: MAYBE') ||
        line.contains('DECISION: DONT_PROCEED')) {
      return true;
    }
    
    // Legacy format
    return line.contains('🟢 STRONG PURSUE') ||
        line.contains('🟡 STRATEGIC PURSUE') ||
        line.contains('🟠 CALCULATED RISK') ||
        line.contains('🔴 REALISTIC REJECT');
  }

  /// Gets color for decision indicators
  static Color _getDecisionColor(String line) {
    // New LITMUS_TEST_PROMPT format with beautiful colors
    if (line.contains('DECISION: PROCEED')) {
      return const Color(0xFF10B981); // Emerald green
    } else if (line.contains('DECISION: MAYBE')) {
      return const Color(0xFFF59E0B); // Amber
    } else if (line.contains('DECISION: DONT_PROCEED')) {
      return const Color(0xFFEF4444); // Red
    }
    
    // Legacy format support
    if (line.contains('🟢')) return const Color(0xFF10B981); // Emerald green
    if (line.contains('🟡')) return const Color(0xFFF59E0B); // Amber
    if (line.contains('🟠')) return const Color(0xFFEA580C); // Orange
    if (line.contains('🔴')) return const Color(0xFFEF4444); // Red
    return const Color(0xFF3B82F6); // Blue
  }

  /// Checks if a line contains LITMUS_TEST_PROMPT fields
  static bool _isLitmusField(String line) {
    return line.contains('CONFIDENCE:') ||
        line.contains('MATCH_SCORE:') ||
        line.contains('PRIMARY_REASON:') ||
        line.contains('CRITICAL_MISSING:') ||
        line.contains('IMPLICIT_LIKELY:') ||
        line.contains('LEARNABLE_GAPS:') ||
        line.contains('STRENGTHS:') ||
        line.contains('BLOCKER_FOUND:');
  }

  /// Formats field names by converting underscores to spaces and capitalizing properly
  static String _formatFieldName(String fieldName) {
    // Remove the colon if present
    String name = fieldName.replaceAll(':', '');
    
    // Convert underscores to spaces
    name = name.replaceAll('_', ' ');
    
    // Capitalize each word
    List<String> words = name.split(' ');
    words = words.map((word) => 
      word.isNotEmpty ? word[0].toUpperCase() + word.substring(1).toLowerCase() 
      : word
    ).toList();
    
    return words.join(' ') + ':';
  }

  /// Gets color for LITMUS_TEST_PROMPT fields
  static Color _getLitmusFieldColor(String line) {
    if (line.contains('CONFIDENCE:') || line.contains('MATCH_SCORE:')) {
      return const Color(0xFF8B5CF6); // Purple for scores
    } else if (line.contains('PRIMARY_REASON:')) {
      return const Color(0xFF1F2937); // Dark gray for main reason
    } else if (line.contains('CRITICAL_MISSING:') || line.contains('BLOCKER_FOUND:')) {
      return const Color(0xFFEF4444); // Red for blockers
    } else if (line.contains('IMPLICIT_LIKELY:') || line.contains('LEARNABLE_GAPS:')) {
      return const Color(0xFF10B981); // Green for opportunities
    } else if (line.contains('STRENGTHS:')) {
      return const Color(0xFF059669); // Darker green for strengths
    }
    return const Color(0xFF6B7280); // Default gray
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

class SkillsAnalysisAdapters {
  static PreextractedComparisonResult parsePreextractedRaw(String raw) {
    // ignore: avoid_print
    print('[SkillsAnalysisAdapters] parsePreextractedRaw length=${raw.length}');
    return PreextractedParser.parse(raw);
  }
}
