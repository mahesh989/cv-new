import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'package:crypto/crypto.dart';

class KeywordCacheService {
  static const String _cachePrefix = 'keyword_cache_';
  static const Duration _cacheExpiry = Duration(days: 7); // Cache for 7 days

  // Generate cache key based on CV filename + JD text hash
  static String _generateCacheKey(String cvFilename, String jdText) {
    final jdHash = md5.convert(utf8.encode(jdText.trim())).toString();
    return '${_cachePrefix}${cvFilename}_${jdHash}';
  }

  // Generate individual cache keys for CV and JD
  static String _generateCVCacheKey(String cvFilename) {
    return '${_cachePrefix}cv_${cvFilename}';
  }

  static String _generateJDCacheKey(String jdText) {
    final jdHash = md5.convert(utf8.encode(jdText.trim())).toString();
    return '${_cachePrefix}jd_${jdHash}';
  }

  // Cache structure for keywords
  static Map<String, dynamic> _createKeywordStructure({
    required List<String> technicalSkills,
    required List<String> softSkills,
    required List<String> domainKeywords,
  }) {
    return {
      'technical_skills': technicalSkills,
      'soft_skills': softSkills,
      'domain_keywords': domainKeywords,
      'timestamp': DateTime.now().toIso8601String(),
    };
  }

  // Save CV keywords to cache
  static Future<void> saveCVKeywords({
    required String cvFilename,
    required List<String> technicalSkills,
    required List<String> softSkills,
    required List<String> domainKeywords,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generateCVCacheKey(cvFilename);
    final data = _createKeywordStructure(
      technicalSkills: technicalSkills,
      softSkills: softSkills,
      domainKeywords: domainKeywords,
    );

    await prefs.setString(cacheKey, json.encode(data));
    print('🔄 [CACHE] Saved CV keywords for: $cvFilename');
  }

  // Save JD keywords to cache
  static Future<void> saveJDKeywords({
    required String jdText,
    required List<String> technicalSkills,
    required List<String> softSkills,
    required List<String> domainKeywords,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generateJDCacheKey(jdText);
    final data = _createKeywordStructure(
      technicalSkills: technicalSkills,
      softSkills: softSkills,
      domainKeywords: domainKeywords,
    );

    await prefs.setString(cacheKey, json.encode(data));
    print('🔄 [CACHE] Saved JD keywords for: ${jdText.substring(0, 50)}...');
  }

  // Get CV keywords from cache
  static Future<Map<String, dynamic>?> getCVKeywords(String cvFilename) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generateCVCacheKey(cvFilename);
    final cachedData = prefs.getString(cacheKey);

    if (cachedData == null) {
      print('📂 [CACHE] No cached CV keywords found for: $cvFilename');
      return null;
    }

    try {
      final data = json.decode(cachedData) as Map<String, dynamic>;

      // Check if cache is expired
      final timestamp = DateTime.parse(data['timestamp']);
      if (DateTime.now().difference(timestamp) > _cacheExpiry) {
        print('⏰ [CACHE] CV keywords cache expired for: $cvFilename');
        await prefs.remove(cacheKey);
        return null;
      }

      print('✅ [CACHE] Retrieved CV keywords for: $cvFilename');
      return {
        'technical_skills': List<String>.from(data['technical_skills'] ?? []),
        'soft_skills': List<String>.from(data['soft_skills'] ?? []),
        'domain_keywords': List<String>.from(data['domain_keywords'] ?? []),
      };
    } catch (e) {
      print('❌ [CACHE] Error parsing CV keywords cache: $e');
      await prefs.remove(cacheKey);
      return null;
    }
  }

  // Get JD keywords from cache
  static Future<Map<String, dynamic>?> getJDKeywords(String jdText) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generateJDCacheKey(jdText);
    final cachedData = prefs.getString(cacheKey);

    if (cachedData == null) {
      print('📂 [CACHE] No cached JD keywords found');
      return null;
    }

    try {
      final data = json.decode(cachedData) as Map<String, dynamic>;

      // Check if cache is expired
      final timestamp = DateTime.parse(data['timestamp']);
      if (DateTime.now().difference(timestamp) > _cacheExpiry) {
        print('⏰ [CACHE] JD keywords cache expired');
        await prefs.remove(cacheKey);
        return null;
      }

      print('✅ [CACHE] Retrieved JD keywords');
      return {
        'technical_skills': List<String>.from(data['technical_skills'] ?? []),
        'soft_skills': List<String>.from(data['soft_skills'] ?? []),
        'domain_keywords': List<String>.from(data['domain_keywords'] ?? []),
      };
    } catch (e) {
      print('❌ [CACHE] Error parsing JD keywords cache: $e');
      await prefs.remove(cacheKey);
      return null;
    }
  }

  // Check if both CV and JD keywords are cached
  static Future<bool> areBothKeywordsCached(
      String cvFilename, String jdText) async {
    final cvKeywords = await getCVKeywords(cvFilename);
    final jdKeywords = await getJDKeywords(jdText);
    return cvKeywords != null && jdKeywords != null;
  }

  // Get both CV and JD keywords together
  static Future<Map<String, Map<String, dynamic>>?> getBothKeywords(
      String cvFilename, String jdText) async {
    final cvKeywords = await getCVKeywords(cvFilename);
    final jdKeywords = await getJDKeywords(jdText);

    if (cvKeywords != null && jdKeywords != null) {
      return {
        'cv_keywords': cvKeywords,
        'jd_keywords': jdKeywords,
      };
    }
    return null;
  }

  // Clear all keyword caches (including comparison results)
  static Future<void> clearAllCaches() async {
    final prefs = await SharedPreferences.getInstance();
    final keys = prefs.getKeys().where((key) => key.startsWith(_cachePrefix));

    for (final key in keys) {
      await prefs.remove(key);
    }

    print('🧹 [CACHE] Cleared all keyword caches and comparison results');
  }

  // Clear cache for specific CV
  static Future<void> clearCVCache(String cvFilename) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generateCVCacheKey(cvFilename);
    await prefs.remove(cacheKey);
    print('🧹 [CACHE] Cleared CV keywords cache for: $cvFilename');
  }

  // Clear cache for specific JD (by text)
  static Future<void> clearJDCache(String jdText) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generateJDCacheKey(jdText);
    await prefs.remove(cacheKey);
    print('🧹 [CACHE] Cleared JD keywords cache');
  }

  // ========== COMPARISON RESULTS CACHING ==========

  /// Saves skill comparison results to persistent cache
  static Future<void> saveComparisonResults({
    required String cvFilename,
    required String jdText,
    required Map<String, dynamic> comparisonResults,
  }) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final key = _generateComparisonCacheKey(cvFilename, jdText);
      final dataToSave = {
        'comparison_results': comparisonResults,
        'timestamp': DateTime.now().toIso8601String(),
        'cv_filename': cvFilename,
        'jd_hash': md5.convert(utf8.encode(jdText.trim())).toString(),
      };

      await prefs.setString(key, json.encode(dataToSave));
      print('💾 [CACHE] Saved comparison results for: $cvFilename');
    } catch (e) {
      print('❌ [CACHE] Error saving comparison results: $e');
    }
  }

  /// Retrieves skill comparison results from persistent cache
  static Future<Map<String, dynamic>?> getComparisonResults({
    required String cvFilename,
    required String jdText,
  }) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final key = _generateComparisonCacheKey(cvFilename, jdText);
      final cachedData = prefs.getString(key);

      if (cachedData != null) {
        final data = json.decode(cachedData);
        final timestamp = DateTime.parse(data['timestamp']);

        // Check if cache is still valid (7 days)
        if (DateTime.now().difference(timestamp).inDays <= 7) {
          print('✅ [CACHE] Retrieved comparison results for: $cvFilename');
          return data['comparison_results'];
        } else {
          // Remove expired cache
          await prefs.remove(key);
          print(
              '🗑️ [CACHE] Removed expired comparison cache for: $cvFilename');
        }
      }
      return null;
    } catch (e) {
      print('❌ [CACHE] Error retrieving comparison results: $e');
      return null;
    }
  }

  /// Generates cache key for comparison results
  static String _generateComparisonCacheKey(String cvFilename, String jdText) {
    final jdHash = md5.convert(utf8.encode(jdText.trim())).toString();
    return '${_cachePrefix}_comparison_${cvFilename}_$jdHash';
  }

  /// Checks if comparison results are cached for given CV and JD
  static Future<bool> areComparisonResultsCached({
    required String cvFilename,
    required String jdText,
  }) async {
    final results = await getComparisonResults(
      cvFilename: cvFilename,
      jdText: jdText,
    );
    return results != null;
  }

  /// Clears comparison results cache for specific CV and JD
  static Future<void> clearComparisonCache({
    required String cvFilename,
    required String jdText,
  }) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final key = _generateComparisonCacheKey(cvFilename, jdText);
      await prefs.remove(key);
      print('🧹 [CACHE] Cleared comparison cache for: $cvFilename');
    } catch (e) {
      print('❌ [CACHE] Error clearing comparison cache: $e');
    }
  }

  // ========== ENHANCED ATS RESULTS CACHING ==========

  /// Saves enhanced ATS score results to persistent cache
  static Future<void> saveEnhancedATSResults({
    required String cvFilename,
    required String jdText,
    required Map<String, dynamic> enhancedATSResults,
  }) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final key = _generateEnhancedATSCacheKey(cvFilename, jdText);
      final data = {
        'enhanced_ats_results': enhancedATSResults,
        'timestamp': DateTime.now().toIso8601String(),
      };
      await prefs.setString(key, jsonEncode(data));
      print('💾 [CACHE] Saved enhanced ATS results for: $cvFilename');
    } catch (e) {
      print('❌ [CACHE] Error saving enhanced ATS results: $e');
    }
  }

  /// Retrieves enhanced ATS score results from persistent cache
  static Future<Map<String, dynamic>?> getEnhancedATSResults({
    required String cvFilename,
    required String jdText,
  }) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final key = _generateEnhancedATSCacheKey(cvFilename, jdText);
      final cachedData = prefs.getString(key);

      if (cachedData != null) {
        final data = jsonDecode(cachedData);
        final timestamp = DateTime.parse(data['timestamp']);

        if (DateTime.now().difference(timestamp) < _cacheExpiry) {
          print('✅ [CACHE] Retrieved enhanced ATS results for: $cvFilename');
          return data['enhanced_ats_results'];
        } else {
          await prefs.remove(key);
          print(
              '🗑️ [CACHE] Removed expired enhanced ATS cache for: $cvFilename');
        }
      }
      return null;
    } catch (e) {
      print('❌ [CACHE] Error retrieving enhanced ATS results: $e');
      return null;
    }
  }

  /// Generates cache key for enhanced ATS results
  static String _generateEnhancedATSCacheKey(String cvFilename, String jdText) {
    final jdHash = md5.convert(utf8.encode(jdText.trim())).toString();
    return '${_cachePrefix}_enhanced_ats_${cvFilename}_$jdHash';
  }

  /// Checks if enhanced ATS results are cached for given CV and JD
  static Future<bool> areEnhancedATSResultsCached({
    required String cvFilename,
    required String jdText,
  }) async {
    final results = await getEnhancedATSResults(
      cvFilename: cvFilename,
      jdText: jdText,
    );
    return results != null;
  }

  /// Clears enhanced ATS results cache for specific CV and JD
  static Future<void> clearEnhancedATSCache({
    required String cvFilename,
    required String jdText,
  }) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final key = _generateEnhancedATSCacheKey(cvFilename, jdText);
      await prefs.remove(key);
      print('🧹 [CACHE] Cleared enhanced ATS cache for: $cvFilename');
    } catch (e) {
      print('❌ [CACHE] Error clearing enhanced ATS cache: $e');
    }
  }

  // Get cache statistics (updated to include comparison and enhanced ATS results)
  static Future<Map<String, int>> getCacheStats() async {
    final prefs = await SharedPreferences.getInstance();
    final keys = prefs.getKeys().where((key) => key.startsWith(_cachePrefix));

    int cvCaches = 0;
    int jdCaches = 0;
    int comparisonCaches = 0;
    int enhancedATSCaches = 0;

    for (final key in keys) {
      if (key.contains('_cv_')) {
        cvCaches++;
      } else if (key.contains('_jd_')) {
        jdCaches++;
      } else if (key.contains('_comparison_')) {
        comparisonCaches++;
      } else if (key.contains('_enhanced_ats_')) {
        enhancedATSCaches++;
      }
    }

    return {
      'cv_caches': cvCaches,
      'jd_caches': jdCaches,
      'comparison_caches': comparisonCaches,
      'enhanced_ats_caches': enhancedATSCaches,
      'total_caches': keys.length,
    };
  }

  // Clear all cache entries
  static Future<void> clearAllCache() async {
    final prefs = await SharedPreferences.getInstance();
    final keys = prefs.getKeys();

    for (String key in keys) {
      if (key.startsWith(_cachePrefix)) {
        await prefs.remove(key);
      }
    }
    print('🧹 [CACHE] Cleared all keyword cache entries');
  }

  // CV Content Caching Methods
  static String _generateCVContentCacheKey(String cvFilename) {
    return '${_cachePrefix}content_${cvFilename}';
  }

  // Save CV content to cache
  static Future<void> saveCVContent({
    required String cvFilename,
    required String content,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generateCVContentCacheKey(cvFilename);
    final data = {
      'content': content,
      'timestamp': DateTime.now().toIso8601String(),
    };

    await prefs.setString(cacheKey, json.encode(data));
    print(
        '🔄 [CACHE] Saved CV content for: $cvFilename (${content.length} chars)');
  }

  // Get CV content from cache
  static Future<String?> getCVContent(String cvFilename) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generateCVContentCacheKey(cvFilename);
    final cachedData = prefs.getString(cacheKey);

    if (cachedData == null) {
      print('📂 [CACHE] No cached CV content found for: $cvFilename');
      return null;
    }

    try {
      final data = json.decode(cachedData) as Map<String, dynamic>;

      // Check if cache is expired
      final timestamp = DateTime.parse(data['timestamp']);
      if (DateTime.now().difference(timestamp) > _cacheExpiry) {
        print('⏰ [CACHE] CV content cache expired for: $cvFilename');
        await prefs.remove(cacheKey);
        return null;
      }

      final content = data['content'] as String;
      print(
          '✅ [CACHE] Retrieved CV content for: $cvFilename (${content.length} chars)');
      return content;
    } catch (e) {
      print('❌ [CACHE] Error parsing CV content cache: $e');
      await prefs.remove(cacheKey);
      return null;
    }
  }

  // Clear CV content cache
  static Future<void> clearCVContentCache(String cvFilename) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generateCVContentCacheKey(cvFilename);
    await prefs.remove(cacheKey);
    print('🧹 [CACHE] Cleared CV content cache for: $cvFilename');
  }

  // Preliminary Analysis Caching Methods
  static String _generatePreliminaryAnalysisCacheKey(
      String cvFilename, String jdText) {
    return '${_cachePrefix}prelim_${cvFilename}_${jdText.hashCode}';
  }

  // Save Preliminary Analysis results to cache
  static Future<void> savePreliminaryAnalysis({
    required String cvFilename,
    required String jdText,
    required Map<String, dynamic> results,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generatePreliminaryAnalysisCacheKey(cvFilename, jdText);
    final data = {
      'results': results,
      'timestamp': DateTime.now().toIso8601String(),
    };

    await prefs.setString(cacheKey, json.encode(data));
    print(
        '🔄 [CACHE] Saved Preliminary Analysis for: $cvFilename + JD (${jdText.length} chars)');
  }

  // Get Preliminary Analysis results from cache
  static Future<Map<String, dynamic>?> getPreliminaryAnalysis(
      String cvFilename, String jdText) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generatePreliminaryAnalysisCacheKey(cvFilename, jdText);
    final cachedData = prefs.getString(cacheKey);

    if (cachedData == null) {
      print(
          '📂 [CACHE] No cached Preliminary Analysis found for: $cvFilename + JD (${jdText.length} chars)');
      return null;
    }

    try {
      final data = json.decode(cachedData) as Map<String, dynamic>;

      // Check if cache is expired
      final timestamp = DateTime.parse(data['timestamp']);
      if (DateTime.now().difference(timestamp) > _cacheExpiry) {
        print(
            '⏰ [CACHE] Preliminary Analysis cache expired for: $cvFilename + JD (${jdText.length} chars)');
        await prefs.remove(cacheKey);
        return null;
      }

      final results = data['results'] as Map<String, dynamic>;
      print(
          '✅ [CACHE] Retrieved Preliminary Analysis for: $cvFilename + JD (${jdText.length} chars)');
      return results;
    } catch (e) {
      print('❌ [CACHE] Error parsing Preliminary Analysis cache: $e');
      await prefs.remove(cacheKey);
      return null;
    }
  }

  // Clear Preliminary Analysis cache
  static Future<void> clearPreliminaryAnalysisCache(
      String cvFilename, String jdText) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generatePreliminaryAnalysisCacheKey(cvFilename, jdText);
    await prefs.remove(cacheKey);
    print(
        '🧹 [CACHE] Cleared Preliminary Analysis cache for: $cvFilename + JD (${jdText.length} chars)');
  }

  // AI Analysis Caching Methods
  static String _generateAIAnalysisCacheKey(String cvFilename, String jdText) {
    return '${_cachePrefix}ai_analysis_${cvFilename}_${jdText.hashCode}';
  }

  // Save AI Analysis results to cache
  static Future<void> saveAIAnalysis({
    required String cvFilename,
    required String jdText,
    required String result,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generateAIAnalysisCacheKey(cvFilename, jdText);
    final data = {
      'result': result,
      'timestamp': DateTime.now().toIso8601String(),
    };

    await prefs.setString(cacheKey, json.encode(data));
    print(
        '🔄 [CACHE] Saved AI Analysis for: $cvFilename + JD (${jdText.length} chars)');
  }

  // Get AI Analysis results from cache
  static Future<String?> getAIAnalysis(String cvFilename, String jdText) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generateAIAnalysisCacheKey(cvFilename, jdText);
    final cachedData = prefs.getString(cacheKey);

    if (cachedData == null) {
      print(
          '📂 [CACHE] No cached AI Analysis found for: $cvFilename + JD (${jdText.length} chars)');
      return null;
    }

    try {
      final data = json.decode(cachedData) as Map<String, dynamic>;

      // Check if cache is expired
      final timestamp = DateTime.parse(data['timestamp']);
      if (DateTime.now().difference(timestamp) > _cacheExpiry) {
        print(
            '⏰ [CACHE] AI Analysis cache expired for: $cvFilename + JD (${jdText.length} chars)');
        await prefs.remove(cacheKey);
        return null;
      }

      final result = data['result'] as String;
      print(
          '✅ [CACHE] Retrieved AI Analysis for: $cvFilename + JD (${jdText.length} chars)');
      return result;
    } catch (e) {
      print('❌ [CACHE] Error parsing AI Analysis cache: $e');
      await prefs.remove(cacheKey);
      return null;
    }
  }

  // Clear AI Analysis cache
  static Future<void> clearAIAnalysisCache(
      String cvFilename, String jdText) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generateAIAnalysisCacheKey(cvFilename, jdText);
    await prefs.remove(cacheKey);
    print(
        '🧹 [CACHE] Cleared AI Analysis cache for: $cvFilename + JD (${jdText.length} chars)');
  }

  // AI Recommendations Caching Methods
  static String _generateAIRecommendationsCacheKey(
      String cvFilename, String jdText) {
    return '${_cachePrefix}ai_recommendations_${cvFilename}_${jdText.hashCode}';
  }

  // Save AI Recommendations results to cache
  static Future<void> saveAIRecommendations({
    required String cvFilename,
    required String jdText,
    required String result,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generateAIRecommendationsCacheKey(cvFilename, jdText);
    final data = {
      'result': result,
      'timestamp': DateTime.now().toIso8601String(),
    };

    await prefs.setString(cacheKey, json.encode(data));
    print(
        '🔄 [CACHE] Saved AI Recommendations for: $cvFilename + JD (${jdText.length} chars)');
  }

  // Get AI Recommendations results from cache
  static Future<String?> getAIRecommendations(
      String cvFilename, String jdText) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generateAIRecommendationsCacheKey(cvFilename, jdText);
    final cachedData = prefs.getString(cacheKey);

    if (cachedData == null) {
      print(
          '📂 [CACHE] No cached AI Recommendations found for: $cvFilename + JD (${jdText.length} chars)');
      return null;
    }

    try {
      final data = json.decode(cachedData) as Map<String, dynamic>;

      // Check if cache is expired
      final timestamp = DateTime.parse(data['timestamp']);
      if (DateTime.now().difference(timestamp) > _cacheExpiry) {
        print(
            '⏰ [CACHE] AI Recommendations cache expired for: $cvFilename + JD (${jdText.length} chars)');
        await prefs.remove(cacheKey);
        return null;
      }

      final result = data['result'] as String;
      print(
          '✅ [CACHE] Retrieved AI Recommendations for: $cvFilename + JD (${jdText.length} chars)');
      return result;
    } catch (e) {
      print('❌ [CACHE] Error parsing AI Recommendations cache: $e');
      await prefs.remove(cacheKey);
      return null;
    }
  }

  // Clear AI Recommendations cache
  static Future<void> clearAIRecommendationsCache(
      String cvFilename, String jdText) async {
    final prefs = await SharedPreferences.getInstance();
    final cacheKey = _generateAIRecommendationsCacheKey(cvFilename, jdText);
    await prefs.remove(cacheKey);
    print(
        '🧹 [CACHE] Cleared AI Recommendations cache for: $cvFilename + JD (${jdText.length} chars)');
  }
}
