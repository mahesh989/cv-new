/// Enhanced state management system for the Flutter app
/// Provides consistent state handling, persistence, and reactive updates

library state_management;

import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'architecture.dart';

/// Global application state management
class AppStateManager extends BaseController {
  static final AppStateManager _instance = AppStateManager._internal();
  factory AppStateManager() => _instance;
  AppStateManager._internal();

  // Core app state
  bool _isInitialized = false;
  bool _isOnline = true;
  String? _selectedCvFilename;
  String? _currentJobDescription;
  Map<String, dynamic> _cache = {};
  List<String> _recentFiles = [];

  // Getters
  bool get isInitialized => _isInitialized;
  bool get isOnline => _isOnline;
  String? get selectedCvFilename => _selectedCvFilename;
  String? get currentJobDescription => _currentJobDescription;
  Map<String, dynamic> get cache => Map.unmodifiable(_cache);
  List<String> get recentFiles => List.unmodifiable(_recentFiles);

  /// Initialize the app state
  Future<void> initialize() async {
    await executeAsync(() async {
      await _loadFromStorage();
      _isInitialized = true;
      Logger.info('✅ App state initialized');
    });
  }

  /// Set online/offline status
  void setOnlineStatus(bool online) {
    _isOnline = online;
    Logger.info('🌐 Network status: ${online ? 'Online' : 'Offline'}');
    notifyListeners();
  }

  /// Set selected CV filename
  void setSelectedCv(String? filename) {
    if (_selectedCvFilename != filename) {
      _selectedCvFilename = filename;
      if (filename != null) {
        _addToRecentFiles(filename);
      }
      _saveToStorage();
      notifyListeners();
    }
  }

  /// Set current job description
  void setJobDescription(String? description) {
    if (_currentJobDescription != description) {
      _currentJobDescription = description;
      _saveToStorage();
      notifyListeners();
    }
  }

  /// Add to cache with expiration
  void addToCache(String key, dynamic value, {Duration? expiration}) {
    final now = DateTime.now();
    _cache[key] = {
      'value': value,
      'created': now.millisecondsSinceEpoch,
      'expires': expiration != null 
          ? now.add(expiration).millisecondsSinceEpoch 
          : null,
    };
    _saveToStorage();
  }

  /// Get from cache
  T? getFromCache<T>(String key) {
    final cached = _cache[key];
    if (cached == null) return null;

    final expires = cached['expires'];
    if (expires != null && DateTime.now().millisecondsSinceEpoch > expires) {
      _cache.remove(key);
      _saveToStorage();
      return null;
    }

    return cached['value'] as T?;
  }

  /// Clear cache
  void clearCache() {
    _cache.clear();
    _saveToStorage();
    notifyListeners();
  }

  /// Add file to recent files list
  void _addToRecentFiles(String filename) {
    _recentFiles.remove(filename); // Remove if already exists
    _recentFiles.insert(0, filename); // Add to beginning
    if (_recentFiles.length > 10) {
      _recentFiles = _recentFiles.take(10).toList(); // Keep only 10 recent files
    }
  }

  /// Load state from persistent storage
  Future<void> _loadFromStorage() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      _selectedCvFilename = prefs.getString('selected_cv');
      _currentJobDescription = prefs.getString('current_jd');
      
      final recentFilesJson = prefs.getString('recent_files');
      if (recentFilesJson != null) {
        _recentFiles = List<String>.from(jsonDecode(recentFilesJson));
      }

      final cacheJson = prefs.getString('app_cache');
      if (cacheJson != null) {
        _cache = Map<String, dynamic>.from(jsonDecode(cacheJson));
        _cleanExpiredCache();
      }

      Logger.info('📁 App state loaded from storage');
    } catch (e) {
      Logger.error('Failed to load app state', e);
    }
  }

  /// Save state to persistent storage
  Future<void> _saveToStorage() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      if (_selectedCvFilename != null) {
        await prefs.setString('selected_cv', _selectedCvFilename!);
      } else {
        await prefs.remove('selected_cv');
      }

      if (_currentJobDescription != null) {
        await prefs.setString('current_jd', _currentJobDescription!);
      } else {
        await prefs.remove('current_jd');
      }

      await prefs.setString('recent_files', jsonEncode(_recentFiles));
      await prefs.setString('app_cache', jsonEncode(_cache));

    } catch (e) {
      Logger.error('Failed to save app state', e);
    }
  }

  /// Clean expired cache entries
  void _cleanExpiredCache() {
    final now = DateTime.now().millisecondsSinceEpoch;
    final keysToRemove = <String>[];

    for (final entry in _cache.entries) {
      final expires = entry.value['expires'];
      if (expires != null && now > expires) {
        keysToRemove.add(entry.key);
      }
    }

    for (final key in keysToRemove) {
      _cache.remove(key);
    }
  }

  /// Reset all state
  Future<void> reset() async {
    _selectedCvFilename = null;
    _currentJobDescription = null;
    _recentFiles.clear();
    _cache.clear();
    
    await _saveToStorage();
    notifyListeners();
    
    Logger.info('🔄 App state reset');
  }
}

/// Analysis state management for CV analysis operations
class AnalysisStateManager extends BaseController {
  static final AnalysisStateManager _instance = AnalysisStateManager._internal();
  factory AnalysisStateManager() => _instance;
  AnalysisStateManager._internal();

  // Analysis state
  bool _isAnalyzing = false;
  String? _currentAnalysisId;
  Map<String, dynamic>? _lastAnalysisResult;
  List<Map<String, dynamic>> _analysisHistory = [];
  double _analysisProgress = 0.0;
  String _analysisStatus = '';

  // Getters
  bool get isAnalyzing => _isAnalyzing;
  String? get currentAnalysisId => _currentAnalysisId;
  Map<String, dynamic>? get lastAnalysisResult => _lastAnalysisResult;
  List<Map<String, dynamic>> get analysisHistory => List.unmodifiable(_analysisHistory);
  double get analysisProgress => _analysisProgress;
  String get analysisStatus => _analysisStatus;

  /// Start analysis operation
  void startAnalysis(String analysisId) {
    _isAnalyzing = true;
    _currentAnalysisId = analysisId;
    _analysisProgress = 0.0;
    _analysisStatus = 'Starting analysis...';
    notifyListeners();
    Logger.info('🔍 Started analysis: $analysisId');
  }

  /// Update analysis progress
  void updateProgress(double progress, String status) {
    _analysisProgress = progress.clamp(0.0, 1.0);
    _analysisStatus = status;
    notifyListeners();
  }

  /// Complete analysis operation
  void completeAnalysis(Map<String, dynamic> result) {
    _isAnalyzing = false;
    _analysisProgress = 1.0;
    _analysisStatus = 'Analysis complete';
    _lastAnalysisResult = result;
    
    // Add to history
    _analysisHistory.insert(0, {
      'id': _currentAnalysisId,
      'result': result,
      'timestamp': DateTime.now().millisecondsSinceEpoch,
    });
    
    // Keep only last 20 analyses
    if (_analysisHistory.length > 20) {
      _analysisHistory = _analysisHistory.take(20).toList();
    }
    
    _currentAnalysisId = null;
    notifyListeners();
    
    Logger.info('✅ Analysis completed successfully');
    _saveAnalysisHistory();
  }

  /// Handle analysis error
  void handleAnalysisError(String error) {
    _isAnalyzing = false;
    _analysisProgress = 0.0;
    _analysisStatus = 'Analysis failed';
    _currentAnalysisId = null;
    
    setError(error);
    notifyListeners();
    
    Logger.error('❌ Analysis failed', error);
  }

  /// Cancel current analysis
  void cancelAnalysis() {
    _isAnalyzing = false;
    _analysisProgress = 0.0;
    _analysisStatus = 'Analysis cancelled';
    _currentAnalysisId = null;
    
    notifyListeners();
    Logger.info('⏹️ Analysis cancelled');
  }

  /// Get analysis by ID from history
  Map<String, dynamic>? getAnalysisById(String id) {
    try {
      return _analysisHistory.firstWhere((analysis) => analysis['id'] == id);
    } catch (e) {
      return null;
    }
  }

  /// Clear analysis history
  void clearHistory() {
    _analysisHistory.clear();
    notifyListeners();
    _saveAnalysisHistory();
  }

  /// Save analysis history to storage
  Future<void> _saveAnalysisHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('analysis_history', jsonEncode(_analysisHistory));
    } catch (e) {
      Logger.error('Failed to save analysis history', e);
    }
  }

  /// Load analysis history from storage
  Future<void> loadAnalysisHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final historyJson = prefs.getString('analysis_history');
      
      if (historyJson != null) {
        _analysisHistory = List<Map<String, dynamic>>.from(jsonDecode(historyJson));
        notifyListeners();
        Logger.info('📚 Analysis history loaded');
      }
    } catch (e) {
      Logger.error('Failed to load analysis history', e);
    }
  }
}

/// UI state management for interface state
class UIStateManager extends BaseController {
  static final UIStateManager _instance = UIStateManager._internal();
  factory UIStateManager() => _instance;
  UIStateManager._internal();

  // UI state
  int _currentTabIndex = 0;
  bool _isDarkMode = false;
  bool _isCompactMode = false;
  String _currentTheme = 'default';
  Map<String, bool> _expandedSections = {};
  List<String> _recentSearches = [];

  // Getters
  int get currentTabIndex => _currentTabIndex;
  bool get isDarkMode => _isDarkMode;
  bool get isCompactMode => _isCompactMode;
  String get currentTheme => _currentTheme;
  Map<String, bool> get expandedSections => Map.unmodifiable(_expandedSections);
  List<String> get recentSearches => List.unmodifiable(_recentSearches);

  /// Set current tab index
  void setTabIndex(int index) {
    if (_currentTabIndex != index) {
      _currentTabIndex = index;
      notifyListeners();
      _saveUIState();
    }
  }

  /// Toggle dark mode
  void toggleDarkMode() {
    _isDarkMode = !_isDarkMode;
    notifyListeners();
    _saveUIState();
    Logger.info('🌙 Dark mode: ${_isDarkMode ? 'enabled' : 'disabled'}');
  }

  /// Toggle compact mode
  void toggleCompactMode() {
    _isCompactMode = !_isCompactMode;
    notifyListeners();
    _saveUIState();
    Logger.info('📱 Compact mode: ${_isCompactMode ? 'enabled' : 'disabled'}');
  }

  /// Set theme
  void setTheme(String theme) {
    if (_currentTheme != theme) {
      _currentTheme = theme;
      notifyListeners();
      _saveUIState();
      Logger.info('🎨 Theme changed to: $theme');
    }
  }

  /// Set section expanded state
  void setSectionExpanded(String sectionId, bool expanded) {
    _expandedSections[sectionId] = expanded;
    notifyListeners();
    _saveUIState();
  }

  /// Toggle section expanded state
  void toggleSection(String sectionId) {
    final currentState = _expandedSections[sectionId] ?? false;
    setSectionExpanded(sectionId, !currentState);
  }

  /// Add to recent searches
  void addRecentSearch(String search) {
    if (search.trim().isEmpty) return;
    
    _recentSearches.remove(search); // Remove if already exists
    _recentSearches.insert(0, search); // Add to beginning
    
    if (_recentSearches.length > 10) {
      _recentSearches = _recentSearches.take(10).toList();
    }
    
    notifyListeners();
    _saveUIState();
  }

  /// Clear recent searches
  void clearRecentSearches() {
    _recentSearches.clear();
    notifyListeners();
    _saveUIState();
  }

  /// Load UI state from storage
  Future<void> loadUIState() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      _currentTabIndex = prefs.getInt('current_tab') ?? 0;
      _isDarkMode = prefs.getBool('dark_mode') ?? false;
      _isCompactMode = prefs.getBool('compact_mode') ?? false;
      _currentTheme = prefs.getString('current_theme') ?? 'default';
      
      final expandedJson = prefs.getString('expanded_sections');
      if (expandedJson != null) {
        _expandedSections = Map<String, bool>.from(jsonDecode(expandedJson));
      }
      
      final searchesJson = prefs.getString('recent_searches');
      if (searchesJson != null) {
        _recentSearches = List<String>.from(jsonDecode(searchesJson));
      }
      
      notifyListeners();
      Logger.info('🎨 UI state loaded');
    } catch (e) {
      Logger.error('Failed to load UI state', e);
    }
  }

  /// Save UI state to storage
  Future<void> _saveUIState() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      await prefs.setInt('current_tab', _currentTabIndex);
      await prefs.setBool('dark_mode', _isDarkMode);
      await prefs.setBool('compact_mode', _isCompactMode);
      await prefs.setString('current_theme', _currentTheme);
      await prefs.setString('expanded_sections', jsonEncode(_expandedSections));
      await prefs.setString('recent_searches', jsonEncode(_recentSearches));
      
    } catch (e) {
      Logger.error('Failed to save UI state', e);
    }
  }
}

/// Global state managers instances
final appState = AppStateManager();
final analysisState = AnalysisStateManager();
final uiState = UIStateManager();

/// Initialize all state managers
Future<void> initializeStateManagement() async {
  Logger.info('🚀 Initializing state management...');
  
  await Future.wait([
    appState.initialize(),
    analysisState.loadAnalysisHistory(),
    uiState.loadUIState(),
  ]);
  
  Logger.info('✅ State management initialized successfully');
}

/// State management provider for widgets
class StateProvider extends InheritedWidget {
  final AppStateManager appState;
  final AnalysisStateManager analysisState;
  final UIStateManager uiState;

  const StateProvider({
    Key? key,
    required this.appState,
    required this.analysisState,
    required this.uiState,
    required Widget child,
  }) : super(key: key, child: child);

  static StateProvider? of(BuildContext context) {
    return context.dependOnInheritedWidgetOfExactType<StateProvider>();
  }

  @override
  bool updateShouldNotify(StateProvider oldWidget) {
    return appState != oldWidget.appState ||
           analysisState != oldWidget.analysisState ||
           uiState != oldWidget.uiState;
  }
}

/// Extension to easily access state managers from context
extension StateContext on BuildContext {
  AppStateManager get appState {
    final provider = StateProvider.of(this);
    assert(provider != null, 'StateProvider not found in widget tree');
    return provider!.appState;
  }

  AnalysisStateManager get analysisState {
    final provider = StateProvider.of(this);
    assert(provider != null, 'StateProvider not found in widget tree');
    return provider!.analysisState;
  }

  UIStateManager get uiState {
    final provider = StateProvider.of(this);
    assert(provider != null, 'StateProvider not found in widget tree');
    return provider!.uiState;
  }
}
