import '../services/ai_model_service.dart';
import '../config/ai_models_config.dart';

/// Utility class for easy access to AI model information throughout the app
class AIModelUtils {
  static final AIModelService _service = AIModelService();

  /// Get the currently selected AI model ID
  static String getCurrentModelId() {
    return _service.currentModelId;
  }

  /// Get the currently selected AI model object
  static AIModel getCurrentModel() {
    return _service.currentModel;
  }

  /// Get the currently selected AI model name
  static String getCurrentModelName() {
    return _service.currentModel.name;
  }

  /// Get the currently selected AI model provider
  static String getCurrentModelProvider() {
    return _service.currentModel.provider;
  }

  /// Check if the current model is from Anthropic
  static bool isCurrentModelAnthropic() {
    return _service.currentModel.provider == 'Anthropic';
  }

  /// Check if the current model is from OpenAI
  static bool isCurrentModelOpenAI() {
    return _service.currentModel.provider == 'OpenAI';
  }

  /// Check if the current model is from DeepSeek
  static bool isCurrentModelDeepSeek() {
    return _service.currentModel.provider == 'DeepSeek';
  }

  /// Get model info for API calls
  static Map<String, dynamic> getCurrentModelForAPI() {
    return {
      'model': _service.currentModelId,
      'provider': _service.currentModel.provider,
      'name': _service.currentModel.name,
    };
  }

  /// Get model info for display purposes
  static Map<String, dynamic> getCurrentModelForDisplay() {
    return {
      'id': _service.currentModelId,
      'name': _service.currentModel.name,
      'provider': _service.currentModel.provider,
      'description': _service.currentModel.description,
      'speed': _service.currentModel.speed,
      'cost': _service.currentModel.cost,
    };
  }

  /// Example: How to use in API calls
  static Map<String, dynamic> createAPIRequest({
    required String prompt,
    Map<String, dynamic>? additionalParams,
  }) {
    final modelInfo = getCurrentModelForAPI();

    return {
      'prompt': prompt,
      'model': modelInfo['model'],
      'provider': modelInfo['provider'],
      ...?additionalParams,
    };
  }

  /// Example: How to get model info for UI display
  static String getModelDisplayText() {
    final model = getCurrentModel();
    return '${model.name} (${model.provider}) - ${model.speed} • ${model.cost}';
  }

  /// Example: How to check if model supports specific features
  static bool supportsFeature(String feature) {
    final model = getCurrentModel();

    switch (feature) {
      case 'analysis':
        return model.provider == 'Anthropic' || 
               model.id == 'gpt-4' || 
               model.provider == 'DeepSeek';
      case 'fast_processing':
        return model.id == 'claude-3-haiku-20240307' ||
               model.id == 'gpt-3.5-turbo' ||
               model.provider == 'DeepSeek';
      case 'high_quality':
        return model.id == 'claude-sonnet-4-20250514' || 
               model.id == 'gpt-4' ||
               model.id == 'deepseek-reasoner';
      case 'coding':
        return model.id == 'deepseek-coder' ||
               model.provider == 'DeepSeek';
      case 'reasoning':
        return model.id == 'deepseek-reasoner' ||
               model.provider == 'Anthropic';
      default:
        return true;
    }
  }
}

/// Example usage in other parts of the app:
/// 
/// ```dart
/// // In an API service
/// class APIService {
///   Future<void> makeAIRequest(String prompt) async {
///     final request = AIModelUtils.createAPIRequest(
///       prompt: prompt,
///       additionalParams: {'temperature': 0.7},
///     );
///     
///     // Use request['model'] and request['provider'] in your API call
///     final response = await http.post(
///       Uri.parse('your-api-endpoint'),
///       body: json.encode(request),
///     );
///   }
/// }
/// 
/// // In a UI widget
/// class SomeWidget extends StatelessWidget {
///   @override
///   Widget build(BuildContext context) {
///     final modelInfo = AIModelUtils.getCurrentModelForDisplay();
///     
///     return Text('Using: ${modelInfo['name']}');
///   }
/// }
/// 
/// // Check model capabilities
/// if (AIModelUtils.supportsFeature('analysis')) {
///   // Enable analysis features
/// }
/// ```
