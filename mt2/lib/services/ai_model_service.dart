import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../config/ai_models_config.dart';

class AIModelService {
  static const String _storageKey = 'ai_model_selected';

  // Singleton pattern
  static final AIModelService _instance = AIModelService._internal();
  factory AIModelService() => _instance;
  AIModelService._internal();

  // Current selected model
  String _currentModelId = AIModelsConfig.defaultModelId;

  // Get current model
  String get currentModelId => _currentModelId;

  // Get current model object
  AIModel get currentModel =>
      AIModelsConfig.getModel(_currentModelId) ??
      AIModelsConfig.getDefaultModel();

  // Initialize the service
  Future<void> initialize() async {
    await _loadSavedModel();
  }

  // Load saved model from preferences
  Future<void> _loadSavedModel() async {
    final prefs = await SharedPreferences.getInstance();
    final savedModel = prefs.getString(_storageKey);
    if (savedModel != null && AIModelsConfig.modelExists(savedModel)) {
      _currentModelId = savedModel;
    }
  }

  // Change the selected model
  Future<void> changeModel(String modelId) async {
    if (!AIModelsConfig.modelExists(modelId)) {
      throw ArgumentError('Model $modelId does not exist');
    }

    _currentModelId = modelId;

    // Save to preferences
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_storageKey, modelId);

    // Notify backend
    await _notifyBackendModelChange(modelId);
  }

  // Notify backend about model change
  Future<void> _notifyBackendModelChange(String modelId) async {
    try {
      print('🔄 [AI_MODEL_SERVICE] Changing app model to: $modelId');

      final response = await http.post(
        Uri.parse('http://localhost:8000/api/update-ai-model'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'task':
              'DEFAULT', // Use DEFAULT as the task since we're using one model for all tasks
          'model': modelId
        }),
      );

      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        print(
            '✅ [AI_MODEL_SERVICE] Successfully updated app model to: $modelId');
        print('📋 [AI_MODEL_SERVICE] Response: ${result['message']}');
      } else {
        print(
            '❌ [AI_MODEL_SERVICE] Failed to update model. Status: ${response.statusCode}');
        print('📋 [AI_MODEL_SERVICE] Response: ${response.body}');
      }
    } catch (e) {
      print('❌ [AI_MODEL_SERVICE] Failed to notify backend: $e');
      // Don't throw - this is not critical for the app to function
    }
  }

  // Get model by ID
  AIModel? getModel(String id) {
    return AIModelsConfig.getModel(id);
  }

  // Get all available models
  List<AIModel> getAllModels() {
    return AIModelsConfig.getAllModels();
  }

  // Get all model IDs
  List<String> getAllModelIds() {
    return AIModelsConfig.getAllModelIds();
  }

  // Check if model exists
  bool modelExists(String id) {
    return AIModelsConfig.modelExists(id);
  }

  // Get default model
  AIModel getDefaultModel() {
    return AIModelsConfig.getDefaultModel();
  }

  // Get default model ID
  String getDefaultModelId() {
    return AIModelsConfig.defaultModelId;
  }

  // Reset to default model
  Future<void> resetToDefault() async {
    await changeModel(AIModelsConfig.defaultModelId);
  }

  // Get model info as Map (for backward compatibility)
  Map<String, dynamic> getModelAsMap(String id) {
    return AIModelsConfig.getModelAsMap(id);
  }

  // Get current model as Map (for backward compatibility)
  Map<String, dynamic> getCurrentModelAsMap() {
    return currentModel.toMap();
  }
}
