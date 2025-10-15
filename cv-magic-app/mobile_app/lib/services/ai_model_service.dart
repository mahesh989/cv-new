import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/ai_model.dart';
import 'auth_service.dart';

class AIModelService extends ChangeNotifier {
  static final AIModelService _instance = AIModelService._internal();
  factory AIModelService() => _instance;
  AIModelService._internal();

  static const String _selectedModelKey = 'selected_ai_model';

  AIModel? _currentModel = AIModelsConfig.getDefaultModel();
  bool _isInitialized = false;

  // Getters
  AIModel? get currentModel => _currentModel;
  String? get currentModelId => _currentModel?.id;
  bool get isInitialized => _isInitialized;

  // Check if model is selected
  bool get hasModelSelected => _currentModel != null;

  // Initialize service and load saved model
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      final prefs = await SharedPreferences.getInstance();
      final isLoggedIn = prefs.getBool('is_logged_in') ?? false;

      if (isLoggedIn) {
        // User is logged in, fetch configuration from backend
        debugPrint(
            '🔐 User is logged in, fetching AI configuration from backend');
        await _fetchUserConfigurationFromBackend();
        
        // If no model was found in backend, check local storage and sync it
        if (_currentModel == null) {
          final savedModelId = prefs.getString(_selectedModelKey);
          if (savedModelId != null) {
            final savedModel = AIModelsConfig.getModel(savedModelId);
            if (savedModel != null) {
              debugPrint('🔄 No backend model found, syncing local model: ${savedModel.name}');
              _currentModel = savedModel;
              // Sync this model to the backend
              await _syncModelWithBackend(savedModelId);
            }
          }
        }
      } else {
        // User is not logged in, load from local storage (for offline mode)
        final savedModelId = prefs.getString(_selectedModelKey);

        if (savedModelId != null) {
          final savedModel = AIModelsConfig.getModel(savedModelId);
          if (savedModel != null) {
            // Check if user has API keys configured before setting model
            final hasApiKeys = await _checkApiKeyAvailability();
            if (hasApiKeys) {
              _currentModel = savedModel;
              debugPrint('🤖 Loaded saved AI model: ${_currentModel!.name}');
            } else {
              debugPrint(
                  '⚠️ Saved model found but no API keys configured, clearing model selection');
              _currentModel = null;
              // Clear the saved model since no API keys are available
              await prefs.remove(_selectedModelKey);
            }
          } else {
            debugPrint('⚠️ Saved model not found, no default model available');
            _currentModel = null;
          }
        } else {
          debugPrint('🤖 No saved model found, no default model available');
          _currentModel = null;
        }
      }
    } catch (e) {
      debugPrint('❌ Error initializing AI model service: $e');
      _currentModel = null;
    }

    _isInitialized = true;
    notifyListeners();
  }

  // Check if user has any API keys configured
  Future<bool> _checkApiKeyAvailability() async {
    try {
      // Try to get backend status to check if any API keys are configured
      final status = await getBackendStatus();
      if (status != null && status['has_api_keys'] == true) {
        return true;
      }
      return false;
    } catch (e) {
      debugPrint('⚠️ Could not check API key availability: $e');
      return false;
    }
  }

  // Change the current model
  Future<void> changeModel(String modelId) async {
    if (modelId == _currentModel?.id) return;

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
      debugPrint('✅ Changed AI model to: ${_currentModel!.name}');

      // Sync with backend
      await _syncModelWithBackend(modelId);

      notifyListeners();
    } catch (e) {
      debugPrint('❌ Error changing AI model: $e');
    }
  }

  // Clear model selection (no default model available)
  Future<void> clearSelection() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_selectedModelKey);

      _currentModel = null;
      debugPrint('🗑️ Cleared AI model selection');

      notifyListeners();
    } catch (e) {
      debugPrint('❌ Error clearing AI model selection: $e');
    }
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
  Map<String, dynamic>? getCurrentModelInfo() {
    if (_currentModel == null) return null;
    return {
      'id': _currentModel!.id,
      'name': _currentModel!.name,
      'provider': _currentModel!.provider,
    };
  }

  // Check if model is current
  bool isCurrentModel(String modelId) {
    return _currentModel?.id == modelId;
  }

  // Get model performance info
  String? getModelPerformanceInfo() {
    if (_currentModel == null) return null;
    return '${_currentModel!.speed} Speed • ${_currentModel!.cost} Cost';
  }

  // Get model capabilities as string
  String? getModelCapabilities() {
    if (_currentModel == null) return null;
    return _currentModel!.capabilities.join(', ');
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
        return 'claude-3-5-haiku-20241022';
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
      // Get authentication token using AuthService
      final token = await AuthService.getValidAuthToken();

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
        Uri.parse('https://cvagent.duckdns.org/api/ai/switch-model'),
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
      // Get authentication token using AuthService
      final token = await AuthService.getValidAuthToken();

      final headers = {
        'Content-Type': 'application/json',
      };

      // Add authorization header if token exists
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }

      // Get API key status to check if user has configured any API keys
      final response = await http.get(
        Uri.parse('https://cvagent.duckdns.org/api/api-keys/status'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else if (response.statusCode == 403) {
        debugPrint(
            '🔐 API key status requires authentication (403) - this is normal when not logged in');
        return null;
      } else {
        debugPrint('⚠️ Failed to get API key status: ${response.statusCode}');
        return null;
      }
    } catch (e) {
      debugPrint('❌ Error getting API key status: $e');
      return null;
    }
  }

  // Initialize and sync with backend on startup
  Future<void> initializeWithBackend() async {
    await initialize();

    // Try to sync with backend, but don't fail if not authenticated
    if (_currentModel != null) {
      try {
        await _syncModelWithBackend(_currentModel!.id);
        debugPrint('✅ AI model synced with backend');
      } catch (e) {
        debugPrint(
            '⚠️ Could not sync AI model with backend (likely not authenticated): $e');
      }
    } else {
      debugPrint('⚠️ No AI model selected, skipping backend sync');
    }

    // Try to get backend status, but don't fail if not authenticated
    try {
      final status = await getBackendStatus();
      if (status != null) {
        debugPrint('🔄 Backend status: $status');
      } else {
        debugPrint('🔐 Backend status unavailable (authentication required)');
        // Show user-friendly notification
        _showAuthRequiredNotification();
      }
    } catch (e) {
      debugPrint(
          '⚠️ Could not get backend status (likely not authenticated): $e');
      _showAuthRequiredNotification();
    }
  }

  // Show user-friendly notification about authentication requirement
  void _showAuthRequiredNotification() {
    // This will be called from the UI context, so we'll use a callback
    if (_onAuthRequired != null) {
      _onAuthRequired!();
    }
  }

  // Callback for when authentication is required
  Function()? _onAuthRequired;

  // Set callback for authentication required notifications
  void setAuthRequiredCallback(Function() callback) {
    _onAuthRequired = callback;
  }

  // Sync with backend after authentication
  Future<void> syncAfterAuth() async {
    // First, try to fetch user's saved configuration from backend
    await _fetchUserConfigurationFromBackend();

    if (_currentModel == null) {
      debugPrint('⚠️ No AI model selected, skipping post-auth sync');
      return;
    }

    try {
      await _syncModelWithBackend(_currentModel!.id);
      debugPrint('✅ AI model synced with backend after authentication');
    } catch (e) {
      debugPrint(
          '❌ Failed to sync AI model with backend after authentication: $e');
    }
  }

  // Fetch user's AI configuration from backend
  Future<void> _fetchUserConfigurationFromBackend() async {
    try {
      // Get authentication token using AuthService
      final token = await AuthService.getValidAuthToken();

      if (token == null) {
        debugPrint(
            '🔐 No auth token available for fetching user configuration');
        return;
      }

      final prefs = await SharedPreferences.getInstance();
      final headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      };

      // Get user's current model preference from backend
      final response = await http.get(
        Uri.parse('https://cvagent.duckdns.org/api/ai/current-model'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final currentModel = data['current_model'];
        final provider = data['current_provider'];
        
        debugPrint('🔍 Backend response: $data');

        if (currentModel && provider) {
          // Map backend model name to frontend model ID
          final frontendModelId = _getFrontendModelId(provider, currentModel);
          debugPrint('🔍 Mapped backend model to frontend ID: $frontendModelId');
          if (frontendModelId != null) {
            final model = AIModelsConfig.getModel(frontendModelId);
            if (model != null) {
              _currentModel = model;
              // Save to local preferences
              await prefs.setString(_selectedModelKey, frontendModelId);
              debugPrint(
                  '✅ Restored user AI configuration from backend: $provider/$currentModel');
              notifyListeners();
            } else {
              debugPrint('❌ Frontend model not found for ID: $frontendModelId');
            }
          } else {
            debugPrint('❌ Could not map backend model to frontend ID');
          }
        } else {
          debugPrint('🔍 No AI configuration found for user in backend (currentModel: $currentModel, provider: $provider)');
        }
      } else if (response.statusCode == 404) {
        debugPrint('🔍 No AI model configured for user in backend (404)');
      } else {
        debugPrint(
            '⚠️ Failed to fetch user AI configuration: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      debugPrint('❌ Error fetching user AI configuration from backend: $e');
    }
  }

  // Map backend model name to frontend model ID
  String? _getFrontendModelId(String provider, String backendModel) {
    switch (provider.toLowerCase()) {
      case 'openai':
        switch (backendModel) {
          case 'gpt-4o':
            return 'gpt-4o';
          case 'gpt-4o-mini':
            return 'gpt-4o-mini';
          case 'gpt-3.5-turbo':
            return 'gpt-3.5-turbo';
          case 'gpt-5-nano':
            return 'gpt-5-nano';
        }
        break;
      case 'anthropic':
        switch (backendModel) {
          case 'claude-3-5-sonnet-20241022':
            return 'claude-3.5-sonnet';
          case 'claude-3-5-haiku-20241022':
            return 'claude-3-haiku';
        }
        break;
      case 'deepseek':
        switch (backendModel) {
          case 'deepseek-chat':
            return 'deepseek-chat';
          case 'deepseek-coder':
            return 'deepseek-coder';
          case 'deepseek-reasoner':
            return 'deepseek-reasoner';
        }
        break;
    }
    return null;
  }
}

// Global instance for easy access
final aiModelService = AIModelService();
