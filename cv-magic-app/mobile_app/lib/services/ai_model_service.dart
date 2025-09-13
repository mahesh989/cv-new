import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/ai_model.dart';

class AIModelService extends ChangeNotifier {
  static final AIModelService _instance = AIModelService._internal();
  factory AIModelService() => _instance;
  AIModelService._internal();

  static const String _selectedModelKey = 'selected_ai_model';

  AIModel _currentModel = AIModelsConfig.getDefaultModel();
  bool _isInitialized = false;

  // Getters
  AIModel get currentModel => _currentModel;
  String get currentModelId => _currentModel.id;
  bool get isInitialized => _isInitialized;

  // Initialize service and load saved model
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      final prefs = await SharedPreferences.getInstance();
      final savedModelId = prefs.getString(_selectedModelKey);

      if (savedModelId != null) {
        final savedModel = AIModelsConfig.getModel(savedModelId);
        if (savedModel != null) {
          _currentModel = savedModel;
          debugPrint('🤖 Loaded saved AI model: ${_currentModel.name}');
        } else {
          debugPrint(
              '⚠️ Saved model not found, using default: ${_currentModel.name}');
        }
      } else {
        debugPrint(
            '🤖 No saved model found, using default: ${_currentModel.name}');
      }
    } catch (e) {
      debugPrint('❌ Error initializing AI model service: $e');
    }

    _isInitialized = true;
    notifyListeners();
  }

  // Change the current model
  Future<void> changeModel(String modelId) async {
    if (modelId == _currentModel.id) return;

    final newModel = AIModelsConfig.getModel(modelId);
    if (newModel == null) {
      debugPrint('❌ Model not found: $modelId');
      return;
    }

    try {
      // Save to SharedPreferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_selectedModelKey, modelId);

      // Update current model
      _currentModel = newModel;
      debugPrint('✅ Changed AI model to: ${_currentModel.name}');

      // Sync with backend
      await _syncModelWithBackend(modelId);

      notifyListeners();
    } catch (e) {
      debugPrint('❌ Error changing AI model: $e');
    }
  }

  // Reset to default model
  Future<void> resetToDefault() async {
    await changeModel(AIModelsConfig.defaultModelId);
  }

  // Get all available models
  List<AIModel> getAllModels() {
    return AIModelsConfig.getAllModels();
  }

  // Get recommended models
  List<AIModel> getRecommendedModels() {
    return AIModelsConfig.getRecommendedModels();
  }

  // Get models by provider
  List<AIModel> getModelsByProvider(String provider) {
    return AIModelsConfig.getModelsByProvider(provider);
  }

  // Get models by capability
  List<AIModel> getModelsByCapability(String capability) {
    return AIModelsConfig.getModelsByCapability(capability);
  }

  // Get current model info as map (for API calls)
  Map<String, dynamic> getCurrentModelInfo() {
    return {
      'id': _currentModel.id,
      'name': _currentModel.name,
      'provider': _currentModel.provider,
    };
  }

  // Check if model is current
  bool isCurrentModel(String modelId) {
    return _currentModel.id == modelId;
  }

  // Get model performance info
  String getModelPerformanceInfo() {
    return '${_currentModel.speed} Speed • ${_currentModel.cost} Cost';
  }

  // Get model capabilities as string
  String getModelCapabilities() {
    return _currentModel.capabilities.join(', ');
  }

  // Clear saved model preference
  Future<void> clearSavedModel() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_selectedModelKey);
      debugPrint('🧹 Cleared saved AI model preference');
    } catch (e) {
      debugPrint('❌ Error clearing saved AI model: $e');
    }
  }

  // Map frontend model ID to backend API model name
  String _getBackendModelName(String modelId) {
    switch (modelId) {
      case 'gpt-4o':
        return 'gpt-4o';
      case 'gpt-4o-mini':
        return 'gpt-4o-mini';
      case 'gpt-3.5-turbo':
        return 'gpt-3.5-turbo';
      case 'claude-3.5-sonnet':
        return 'claude-3-5-sonnet-20241022';
      case 'claude-3-haiku':
        return 'claude-3-haiku-20240307';
      case 'deepseek-chat':
        return 'deepseek-chat';
      case 'deepseek-coder':
        return 'deepseek-coder';
      case 'deepseek-reasoner':
        return 'deepseek-reasoner';
      case 'gpt-5-nano':
        return 'gpt-5-nano';
      default:
        return modelId; // fallback to original ID
    }
  }

  // Sync model selection with backend
  Future<void> _syncModelWithBackend(String modelId) async {
    try {
      // Get authentication token
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');

      final headers = {
        'Content-Type': 'application/json',
      };

      // Add authorization header if token exists
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }

      // Get the actual model info to extract provider and model name
      final model = AIModelsConfig.getModel(modelId);
      if (model == null) {
        debugPrint('❌ Model not found for backend sync: $modelId');
        return;
      }

      // Map frontend model ID to backend API model name
      String provider = model.provider.toLowerCase();
      String apiModelName = _getBackendModelName(modelId);

      debugPrint('🔄 Syncing model: $modelId -> $provider/$apiModelName');

      final response = await http.post(
        Uri.parse('http://localhost:8000/api/ai/switch-model'),
        headers: headers,
        body: jsonEncode({
          'model': apiModelName,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        debugPrint('✅ Backend model synced: ${data['message']}');
      } else {
        debugPrint(
            '⚠️ Failed to sync model with backend: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('❌ Error syncing model with backend: $e');
    }
  }

  // Get current model status from backend
  Future<Map<String, dynamic>?> getBackendStatus() async {
    try {
      // Get authentication token
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');

      final headers = {
        'Content-Type': 'application/json',
      };

      // Add authorization header if token exists
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }

      final response = await http.get(
        Uri.parse('http://localhost:8000/api/ai/status'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        debugPrint('⚠️ Failed to get backend status: ${response.statusCode}');
        return null;
      }
    } catch (e) {
      debugPrint('❌ Error getting backend status: $e');
      return null;
    }
  }

  // Initialize and sync with backend on startup
  Future<void> initializeWithBackend() async {
    await initialize();

    // Try to sync with backend, but don't fail if not authenticated
    try {
      await _syncModelWithBackend(_currentModel.id);
      debugPrint('✅ AI model synced with backend');
    } catch (e) {
      debugPrint(
          '⚠️ Could not sync AI model with backend (likely not authenticated): $e');
    }

    // Try to get backend status, but don't fail if not authenticated
    try {
      final status = await getBackendStatus();
      if (status != null) {
        debugPrint('🔄 Backend status: $status');
      }
    } catch (e) {
      debugPrint(
          '⚠️ Could not get backend status (likely not authenticated): $e');
    }
  }

  // Sync with backend after authentication
  Future<void> syncAfterAuth() async {
    try {
      await _syncModelWithBackend(_currentModel.id);
      debugPrint('✅ AI model synced with backend after authentication');
    } catch (e) {
      debugPrint(
          '❌ Failed to sync AI model with backend after authentication: $e');
    }
  }
}

// Global instance for easy access
final aiModelService = AIModelService();
