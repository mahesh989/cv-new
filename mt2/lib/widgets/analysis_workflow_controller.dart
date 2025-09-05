import 'package:flutter/material.dart';
import '../services/api_service.dart' as api;
import '../services/enhanced_api_service.dart';
import '../services/skill_comparison_service.dart';
import '../services/keyword_cache_service.dart';
import '../services/enhanced_ats_service.dart';
import '../utils/notification_service.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class AnalysisWorkflowController with ChangeNotifier {
  final EnhancedApiService _apiService = EnhancedApiService();

  // Analysis states
  bool _isPreliminaryRunning = false;
  bool _isAIAnalysisRunning = false;
  bool _isSkillComparisonRunning = false;
  bool _isEnhancedATSRunning = false;
  bool _isAIRecommendationsRunning = false;
  Map<String, dynamic>? _preliminaryResults;
  String _aiAnalysisResult = '';
  Map<String, dynamic> _skillComparison = {};
  bool _hasSkillComparisonResults = false;
  Map<String, dynamic>? _enhancedATSResults;
  bool _hasEnhancedATSResults = false;
  String _aiRecommendationsResult = '';
  bool _hasAIRecommendations = false;

  // Getters
  bool get isPreliminaryRunning => _isPreliminaryRunning;
  bool get isAIAnalysisRunning => _isAIAnalysisRunning;
  bool get isSkillComparisonRunning => _isSkillComparisonRunning;
  bool get isEnhancedATSRunning => _isEnhancedATSRunning;
  bool get isAIRecommendationsRunning => _isAIRecommendationsRunning;
  Map<String, dynamic>? get preliminaryResults => _preliminaryResults;
  String get aiAnalysisResult => _aiAnalysisResult;
  Map<String, dynamic> get skillComparison => _skillComparison;
  bool get hasSkillComparisonResults => _hasSkillComparisonResults;
  Map<String, dynamic>? get enhancedATSResults => _enhancedATSResults;
  bool get hasEnhancedATSResults => _hasEnhancedATSResults;
  String get aiRecommendationsResult => _aiRecommendationsResult;
  bool get hasAIRecommendations => _hasAIRecommendations;

  // Main workflow method
  Future<void> executeFullAnalysis({
    required String cvFilename,
    required String jdText,
    required String currentPrompt,
  }) async {
    if (cvFilename.isEmpty || jdText.isEmpty) {
      NotificationService.showError('Please provide CV and JD text first');
      return;
    }

    try {
      // 1. Preliminary Analysis
      await _runPreliminaryAnalysis(cvFilename, jdText);

      // 2. AI Analysis
      await _runAIAnalysis(cvFilename, jdText, currentPrompt);

      // 3. Skill Comparison
      await _runSkillComparison(cvFilename, jdText);

      // 4. Enhanced ATS Score (automatic)
      await _runEnhancedATSScore(cvFilename, jdText);

      // 5. AI Recommendations (automatic)
      await _runAIRecommendations(cvFilename, jdText);

      NotificationService.showSuccess('Full analysis completed successfully!');
    } catch (e) {
      NotificationService.showError('Analysis workflow failed: $e');
      rethrow;
    }
  }

  // Individual analysis steps
  Future<void> _runPreliminaryAnalysis(String cvFilename, String jdText) async {
    _isPreliminaryRunning = true;
    notifyListeners();

    try {
      _preliminaryResults = await _apiService.preliminaryAnalysis(
        cvFilename: cvFilename,
        jdText: jdText,
      );

      // Cache results
      await KeywordCacheService.savePreliminaryAnalysis(
        cvFilename: cvFilename,
        jdText: jdText,
        results: _preliminaryResults!,
      );
    } finally {
      _isPreliminaryRunning = false;
      notifyListeners();
    }
  }

  Future<void> _runAIAnalysis(
      String cvFilename, String jdText, String prompt) async {
    _isAIAnalysisRunning = true;
    notifyListeners();

    try {
      final result = await _apiService.analyzeMatch(
        cvFilename: cvFilename,
        jdText: jdText,
        prompt: prompt,
      );

      _aiAnalysisResult = result.raw;

      // Cache results
      await KeywordCacheService.saveAIAnalysis(
        cvFilename: cvFilename,
        jdText: jdText,
        result: _aiAnalysisResult,
      );
    } finally {
      _isAIAnalysisRunning = false;
      notifyListeners();
    }
  }

  Future<void> _runSkillComparison(String cvFilename, String jdText) async {
    _isSkillComparisonRunning = true;
    notifyListeners();

    try {
      // Use skills from preliminary analysis or fallback to individual extraction
      final dynamic cvSkillsDynamic = _preliminaryResults?['cv_skills'];
      final dynamic jdSkillsDynamic = _preliminaryResults?['jd_skills'];

      // Proper type casting with fallbacks
      final Map<String, List<String>> cvSkills =
          _convertToSkillsMap(cvSkillsDynamic);
      final Map<String, List<String>> jdSkills =
          _convertToSkillsMap(jdSkillsDynamic);

      if (cvSkills.isEmpty || jdSkills.isEmpty) {
        throw Exception('No skills available for comparison');
      }

      _skillComparison = await SkillComparisonService.compareSkills(
        cvSkills: cvSkills,
        jdSkills: jdSkills,
        jdText: jdText,
      );

      _hasSkillComparisonResults = true;

      // Cache results
      await KeywordCacheService.saveComparisonResults(
        cvFilename: cvFilename,
        jdText: jdText,
        comparisonResults: _skillComparison,
      );
    } finally {
      _isSkillComparisonRunning = false;
      notifyListeners();
    }
  }

  // Enhanced ATS Score step
  Future<void> _runEnhancedATSScore(String cvFilename, String jdText) async {
    _isEnhancedATSRunning = true;
    notifyListeners();

    try {
      // Get CV and JD text from session
      final cvText = await _getCVTextFromSession();
      final jdTextFromParam = jdText; // Use the passed parameter

      // Build extracted keywords from preliminary results
      final extractedKeywords = {
        'cv_skills': _preliminaryResults?['cv_skills'] ?? {},
        'jd_skills': _preliminaryResults?['jd_skills'] ?? {},
        'cv_text': cvText,
        'jd_text': jdTextFromParam,
      };

      _enhancedATSResults = await EnhancedATSService.calculateEnhancedATSScore(
        cvText: cvText,
        jdText: jdTextFromParam,
        skillComparison: _skillComparison,
        extractedKeywords: extractedKeywords,
      );
      _hasEnhancedATSResults = true;

      // Cache results
      await KeywordCacheService.saveEnhancedATSResults(
        cvFilename: cvFilename,
        jdText: jdTextFromParam,
        enhancedATSResults: _enhancedATSResults!,
      );
    } finally {
      _isEnhancedATSRunning = false;
      notifyListeners();
    }
  }

  // AI Recommendations step
  Future<void> _runAIRecommendations(String cvFilename, String jdText) async {
    _isAIRecommendationsRunning = true;
    notifyListeners();

    try {
      debugPrint(
          '[AI_RECOMMENDATIONS] Starting AI Recommendations generation...');

      // Call the API to generate AI Recommendations using backend's default prompt
      final response = await http
          .post(
            Uri.parse(
                '${api.ApiService.baseUrl}/api/llm/generate-recommendations-from-analysis'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode({
              'cv_filename': cvFilename,
              'jd_text': jdText,
            }),
          )
          .timeout(const Duration(
              seconds: 90)); // 90 second timeout for AI generation

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final recommendations =
            data['recommendations'] ?? 'No recommendations generated';

        _aiRecommendationsResult = recommendations;
        _hasAIRecommendations = true;

        // Cache results
        await KeywordCacheService.saveAIRecommendations(
          cvFilename: cvFilename,
          jdText: jdText,
          result: recommendations,
        );

        debugPrint(
            '[AI_RECOMMENDATIONS] AI Recommendations completed successfully');
      } else {
        debugPrint('❌ [AI_RECOMMENDATIONS] API Error: ${response.statusCode}');
        debugPrint('❌ [AI_RECOMMENDATIONS] Response: ${response.body}');

        // Fallback: Try the alternative endpoint
        final fallbackResponse = await http.post(
          Uri.parse(
              '${api.ApiService.baseUrl}/api/llm/generate-recommendations'),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({
            'cv_filename': cvFilename,
            'jd_text': jdText,
          }),
        );

        if (fallbackResponse.statusCode == 200) {
          final fallbackData = json.decode(fallbackResponse.body);
          final fallbackRecommendations =
              fallbackData['recommendations'] ?? 'No recommendations generated';

          _aiRecommendationsResult = fallbackRecommendations;
          _hasAIRecommendations = true;

          // Cache results
          await KeywordCacheService.saveAIRecommendations(
            cvFilename: cvFilename,
            jdText: jdText,
            result: fallbackRecommendations,
          );
        } else {
          debugPrint(
              '❌ [AI_RECOMMENDATIONS] Fallback also failed: ${fallbackResponse.statusCode}');
          // Create a fallback recommendation based on available data
          _aiRecommendationsResult = _createFallbackRecommendations();
          _hasAIRecommendations = true;

          // Cache fallback results
          await KeywordCacheService.saveAIRecommendations(
            cvFilename: cvFilename,
            jdText: jdText,
            result: _aiRecommendationsResult,
          );
        }
      }
    } finally {
      _isAIRecommendationsRunning = false;
      notifyListeners();
    }
  }

  // Create fallback recommendations when API calls fail
  String _createFallbackRecommendations() {
    final buffer = StringBuffer();

    buffer.writeln('# CV Tailoring Strategy - Fallback Recommendations');
    buffer.writeln();
    buffer.writeln('## 🎯 STRATEGIC POSITIONING');
    buffer.writeln(
        'Based on the analysis completed, focus on highlighting your strongest matched skills and relevant experience.');
    buffer.writeln();
    buffer.writeln('## 🔧 TECHNICAL SKILLS STRATEGY');
    if (_preliminaryResults != null &&
        _preliminaryResults!['cv_skills'] != null) {
      final cvSkills =
          _preliminaryResults!['cv_skills'] as Map<String, dynamic>;
      buffer.writeln('### Emphasize Your Strongest Skills:');
      cvSkills.forEach((category, skills) {
        if (skills is List && skills.isNotEmpty) {
          buffer.writeln(
              '- **${category.replaceAll('_', ' ').toUpperCase()}**: ${skills.take(3).join(', ')}');
        }
      });
    }
    buffer.writeln();
    buffer.writeln('## 🎪 SOFT SKILLS ENHANCEMENT');
    buffer.writeln(
        'Focus on communication, teamwork, and problem-solving skills that are universally valued.');
    buffer.writeln();
    buffer.writeln('## 📈 ACHIEVEMENT TRANSFORMATION');
    buffer.writeln(
        'Quantify your achievements with specific metrics and business impact where possible.');
    buffer.writeln();
    buffer.writeln('## ⚠️ STRATEGIC WARNINGS');
    buffer.writeln('### Don\'t Oversell Missing Skills');
    buffer.writeln('- Only claim skills and experience you genuinely have');
    buffer.writeln(
        '- Focus on transferable skills rather than fabricating specific expertise');
    buffer.writeln();
    buffer.writeln('### Don\'t Undersell Your Strengths');
    buffer.writeln(
        '- Highlight your unique qualifications and distinctive background');
    buffer.writeln('- Emphasize relevant projects and accomplishments');
    buffer.writeln();
    buffer.writeln('## 🎯 SUCCESS PROBABILITY');
    buffer.writeln(
        'Focus on authentic positioning and leveraging your genuine strengths for the best chance of success.');

    return buffer.toString();
  }

  // Helper methods for getting CV and JD text
  Future<String> _getCVTextFromSession() async {
    try {
      // Use skills from preliminary results as a text representation
      final cvSkills = _preliminaryResults?['cv_skills'] ?? {};
      if (cvSkills is Map<String, dynamic>) {
        final cvSkillsText = cvSkills.entries
            .map((entry) =>
                '${entry.key.replaceAll('_', ' ').toUpperCase()}: ${(entry.value as List<dynamic>).join(', ')}')
            .join('\n\n');
        return cvSkillsText.isNotEmpty
            ? cvSkillsText
            : 'CV skills extracted successfully';
      }
      return 'CV data available for analysis';
    } catch (e) {
      debugPrint('Warning: Could not create CV text representation: $e');
      return 'CV data available for analysis';
    }
  }

  // Helper method for proper type conversion
  Map<String, List<String>> _convertToSkillsMap(dynamic skillsData) {
    if (skillsData == null) return {};

    try {
      if (skillsData is Map<String, dynamic>) {
        // Handle nested structure from preliminary analysis
        if (skillsData.containsKey('soft_skills') ||
            skillsData.containsKey('technical_skills') ||
            skillsData.containsKey('domain_keywords')) {
          // This is the nested structure from preliminary analysis
          return {
            'soft_skills': _extractSkillsList(skillsData['soft_skills']),
            'technical_skills':
                _extractSkillsList(skillsData['technical_skills']),
            'domain_keywords':
                _extractSkillsList(skillsData['domain_keywords']),
          };
        } else {
          // Handle flat structure
          return skillsData.map((key, value) {
            if (value is List<dynamic>) {
              return MapEntry(key, value.whereType<String>().toList());
            } else if (value is List<String>) {
              return MapEntry(key, value);
            } else {
              return MapEntry(key, <String>[]);
            }
          });
        }
      }
      return {};
    } catch (e) {
      debugPrint('Error converting skills map: $e');
      return {};
    }
  }

  // Extract skills list from dynamic data
  List<String> _extractSkillsList(dynamic skillsData) {
    if (skillsData == null) return [];
    if (skillsData is List) {
      return skillsData.map((item) => item.toString()).toList();
    }
    return [];
  }

  // Individual step execution
  Future<void> runSkillComparisonOnly({
    required String cvFilename,
    required String jdText,
    required Map<String, dynamic> cvSkillsDynamic,
    required Map<String, dynamic> jdSkillsDynamic,
  }) async {
    _isSkillComparisonRunning = true;
    notifyListeners();

    try {
      // Convert dynamic maps to properly typed maps
      final Map<String, List<String>> cvSkills =
          _convertToSkillsMap(cvSkillsDynamic);
      final Map<String, List<String>> jdSkills =
          _convertToSkillsMap(jdSkillsDynamic);

      _skillComparison = await SkillComparisonService.compareSkills(
        cvSkills: cvSkills,
        jdSkills: jdSkills,
        jdText: jdText,
      );

      _hasSkillComparisonResults = true;

      await KeywordCacheService.saveComparisonResults(
        cvFilename: cvFilename,
        jdText: jdText,
        comparisonResults: _skillComparison,
      );
    } finally {
      _isSkillComparisonRunning = false;
      notifyListeners();
    }
  }

  // Reset state
  void reset() {
    _isPreliminaryRunning = false;
    _isAIAnalysisRunning = false;
    _isSkillComparisonRunning = false;
    _isEnhancedATSRunning = false;
    _isAIRecommendationsRunning = false;
    _preliminaryResults = null;
    _aiAnalysisResult = '';
    _skillComparison = {};
    _hasSkillComparisonResults = false;
    _enhancedATSResults = null;
    _hasEnhancedATSResults = false;
    _aiRecommendationsResult = '';
    _hasAIRecommendations = false;
    notifyListeners();
  }

  // Load cached results
  Future<void> loadCachedResults(String cvFilename, String jdText) async {
    try {
      // Load preliminary analysis
      final preliminary =
          await KeywordCacheService.getPreliminaryAnalysis(cvFilename, jdText);
      if (preliminary != null) {
        _preliminaryResults = preliminary;
      }

      // Load AI analysis
      final aiAnalysis =
          await KeywordCacheService.getAIAnalysis(cvFilename, jdText);
      if (aiAnalysis != null) {
        _aiAnalysisResult = aiAnalysis;
      }

      // Load skill comparison
      final comparison = await KeywordCacheService.getComparisonResults(
        cvFilename: cvFilename,
        jdText: jdText,
      );
      if (comparison != null) {
        _skillComparison = comparison;
        _hasSkillComparisonResults = true;
      }

      // Load Enhanced ATS Score
      final enhancedATS = await KeywordCacheService.getEnhancedATSResults(
        cvFilename: cvFilename,
        jdText: jdText,
      );
      if (enhancedATS != null) {
        _enhancedATSResults = enhancedATS;
        _hasEnhancedATSResults = true;
      }

      // Load AI Recommendations
      final aiRecommendations = await KeywordCacheService.getAIRecommendations(
        cvFilename,
        jdText,
      );
      if (aiRecommendations != null) {
        _aiRecommendationsResult = aiRecommendations;
        _hasAIRecommendations = true;
      }

      notifyListeners();
    } catch (e) {
      debugPrint('Error loading cached results: $e');
    }
  }
}
