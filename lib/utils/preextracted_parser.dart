import 'dart:developer' as developer;

import '../models/preextracted_comparison.dart';

class PreextractedParser {
  static PreextractedComparisonResult parse(String text) {
    developer.log('[PreextractedParser] Parsing text length=${text.length}');
    developer.log('[PreextractedParser] Raw text: ${text.substring(0, text.length > 500 ? 500 : text.length)}...');

    final lines = text.split(RegExp(r'\r?\n'));

    OverallSummary overall = const OverallSummary(
      totalRequirements: 0,
      matched: 0,
      missing: 0,
      matchRatePercent: 0,
    );

    final List<CategorySummary> categories = [];
    final List<MatchedItem> matched = [];
    final List<MissingItem> missing = [];

    // Parse overall summary (supports both "Total JD Requirements:" and "Total Requirements:")
    int idx = 0;
    while (idx < lines.length) {
      final l = lines[idx].trim();
      if (l.startsWith('Total JD Requirements:') ||
          l.startsWith('Total Requirements:')) {
        final total = _numFrom(l);
        final m = _numFrom(_nextLine(lines, idx, startsWith: 'Matched:'));
        final miss = _numFrom(_nextLine(lines, idx, startsWith: 'Missing:'));
        final rate =
            _percentFrom(_nextLine(lines, idx, startsWith: 'Match Rate:'));
        overall = OverallSummary(
          totalRequirements: total,
          matched: m,
          missing: miss,
          matchRatePercent: rate,
        );
        developer.log(
            '[PreextractedParser] Overall: total=$total matched=$m missing=$miss rate=$rate');
        break;
      }
      idx++;
    }

    // Parse summary table (new format) or category breakdown (legacy)
    final summaryTableStart = lines.indexWhere(
        (l) => l.trim().toLowerCase().startsWith('📊 summary table'));
    if (summaryTableStart != -1) {
      // Skip header lines until we hit the table header row that starts with 'Category'
      int i = summaryTableStart + 1;
      while (i < lines.length &&
          !lines[i].trim().toLowerCase().startsWith('category')) {
        i++;
      }
      // The next lines should be data rows until a blank line or a new section
      for (i = i + 1; i < lines.length; i++) {
        final row = lines[i].trim();
        if (row.isEmpty) break;
        if (row.startsWith('🧠') ||
            row.startsWith('🔹') ||
            row.startsWith('✅') ||
            row.startsWith('❌')) break;
        final parsed = _parseSummaryTableRow(row);
        if (parsed != null) categories.add(parsed);
      }
      developer
          .log('[PreextractedParser] Summary table rows=${categories.length}');
    } else {
      // Legacy category breakdown format
      final sectionStart = lines.indexWhere(
          (l) => l.trim().toLowerCase().startsWith('📊 category breakdown'));
      if (sectionStart != -1) {
        for (int i = sectionStart + 1; i < lines.length; i++) {
          final l = lines[i].trim();
          if (l.isEmpty) continue;
          if (l.startsWith('✅') || l.startsWith('❌')) break;
          final parsed = _parseCategoryLine(l);
          if (parsed != null) categories.add(parsed);
        }
        developer
            .log('[PreextractedParser] Categories parsed=${categories.length}');
      }
    }

    // Parse matched items
    final matchedStart = lines.indexWhere(
        (l) => l.trim().toLowerCase().startsWith('✅ matched skills'));
    if (matchedStart != -1) {
      for (int i = matchedStart + 1; i < lines.length; i++) {
        final l = lines[i].trim();
        if (l.isEmpty) continue;
        if (l.startsWith('❌')) break;
        if (!l.startsWith('- JD:')) continue;
        final mi = _parseMatchedLine(l);
        if (mi != null) matched.add(mi);
      }
      developer.log('[PreextractedParser] Matched parsed=${matched.length}');
    }

    // Parse missing items
    final missingStart = lines.indexWhere(
        (l) => l.trim().toLowerCase().startsWith('❌ missing skills'));
    if (missingStart != -1) {
      for (int i = missingStart + 1; i < lines.length; i++) {
        final l = lines[i].trim();
        if (l.isEmpty) continue;
        if (!l.startsWith('- JD:')) break;
        final mi = _parseMissingLine(l);
        if (mi != null) missing.add(mi);
      }
      developer.log('[PreextractedParser] Missing parsed=${missing.length}');
    }

    return PreextractedComparisonResult(
      overall: overall,
      categories: categories,
      matched: matched,
      missing: missing,
      rawText: text,
    );
  }

  static String _nextLine(List<String> lines, int idx,
      {required String startsWith}) {
    final i = lines.indexWhere((l) => l.trim().startsWith(startsWith));
    return i == -1 ? '' : lines[i].trim();
  }

  static int _numFrom(String line) {
    // Handle both regular numbers and numbers in square brackets like [15]
    final m = RegExp(r'\[?(\d+(?:\.\d+)?)\]?').firstMatch(line);
    final result = m == null ? 0 : double.tryParse(m.group(1)!)?.round() ?? 0;
    developer.log('[PreextractedParser] _numFrom("$line") = $result');
    return result;
  }

  static double _percentFrom(String line) {
    // Handle both regular percentages and percentages in square brackets like [78.95%]
    final m = RegExp(r'\[?(\d+(?:\.\d+)?)%?\]?').firstMatch(line);
    final result = m == null ? 0.0 : double.tryParse(m.group(1)!) ?? 0.0;
    developer.log('[PreextractedParser] _percentFrom("$line") = $result');
    return result;
  }

  static CategorySummary? _parseCategoryLine(String line) {
    // Example: "Technical: 0/5 matched (0%)"
    final nameEnd = line.indexOf(':');
    if (nameEnd == -1) return null;
    final name = line.substring(0, nameEnd).trim();
    final m =
        RegExp(r'(\d+)\/(\d+) matched \((\d+(?:\.\d+)?)%\)').firstMatch(line);
    if (m == null) return null;
    final matched = int.tryParse(m.group(1) ?? '') ?? 0;
    final jdTotal = int.tryParse(m.group(2) ?? '') ?? 0;
    final rate = double.tryParse(m.group(3) ?? '') ?? 0.0;
    final missing = (jdTotal - matched).clamp(0, 1 << 31);
    return CategorySummary(
      name: name,
      cvTotal: 0,
      jdTotal: jdTotal,
      matched: matched,
      missing: missing,
      matchRatePercent: rate,
    );
  }

  static CategorySummary? _parseSummaryTableRow(String line) {
    // Expected columns: Category  CV Total  JD Total  Matched  Missing  Match Rate (%)
    // Use a permissive split on multiple spaces and filter empties
    final parts = line
        .split(RegExp(r'\s{2,}'))
        .map((e) => e.trim())
        .where((e) => e.isNotEmpty)
        .toList();
    if (parts.length < 6) {
      // Try fallback split on single spaces while keeping the first column as the rest until a number appears
      final tokens = line.split(RegExp(r'\s+'));
      int firstNumIdx = tokens.indexWhere((t) => RegExp(r'^-?\d').hasMatch(t));
      if (firstNumIdx == -1 || tokens.length - firstNumIdx < 5) return null;
      final name = tokens.sublist(0, firstNumIdx).join(' ').trim();
      final cvTotal = _intOrZero(tokens[firstNumIdx]);
      final jdTotal = _intOrZero(tokens[firstNumIdx + 1]);
      final matched = _intOrZero(tokens[firstNumIdx + 2]);
      final missing = _intOrZero(tokens[firstNumIdx + 3]);
      final rate = _doubleOrZero(tokens[firstNumIdx + 4]);
      return CategorySummary(
        name: name,
        cvTotal: cvTotal,
        jdTotal: jdTotal,
        matched: matched,
        missing: missing,
        matchRatePercent: rate,
      );
    }

    final name = parts[0];
    final cvTotal = _intOrZero(parts[1]);
    final jdTotal = _intOrZero(parts[2]);
    final matched = _intOrZero(parts[3]);
    final missing = _intOrZero(parts[4]);
    final rate = _doubleOrZero(parts[5]);
    return CategorySummary(
      name: name,
      cvTotal: cvTotal,
      jdTotal: jdTotal,
      matched: matched,
      missing: missing,
      matchRatePercent: rate,
    );
  }

  static int _intOrZero(String s) {
    if (s.trim() == '-') return 0;
    // Handle square brackets like [5]
    final cleaned = s.replaceAll('%', '').replaceAll('[', '').replaceAll(']', '');
    final result = int.tryParse(cleaned) ?? 0;
    developer.log('[PreextractedParser] _intOrZero("$s") = $result');
    return result;
  }

  static double _doubleOrZero(String s) {
    // Handle square brackets like [71.43%]
    final cleaned = s.replaceAll('%', '').replaceAll('[', '').replaceAll(']', '');
    final result = double.tryParse(cleaned) ?? 0.0;
    developer.log('[PreextractedParser] _doubleOrZero("$s") = $result');
    return result;
  }

  static MatchedItem? _parseMatchedLine(String line) {
    final jd = RegExp(r'- JD:\s*"([^"]+)"').firstMatch(line)?.group(1);
    final cv = RegExp(r'CV:\s*"([^"]+)"').firstMatch(line)?.group(1);
    final reason = RegExp(r'\|\s*💡\s*(.*)$').firstMatch(line)?.group(1) ?? '';
    if (jd == null || cv == null) return null;
    return MatchedItem(jdSkill: jd, cvSkill: cv, reasoning: reason.trim());
  }

  static MissingItem? _parseMissingLine(String line) {
    final jd = RegExp(r'- JD:\s*"([^"]+)"').firstMatch(line)?.group(1);
    final reason = RegExp(r'\|\s*💡\s*(.*)$').firstMatch(line)?.group(1) ?? '';
    if (jd == null) return null;
    return MissingItem(jdSkill: jd, reasoning: reason.trim());
  }
}
