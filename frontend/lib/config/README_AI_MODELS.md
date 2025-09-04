# AI Model Configuration System

This system provides a centralized way to manage AI models throughout the app. All model definitions are in one place, making it easy to add, remove, or modify models.

## 📁 File Structure

```
lib/
├── config/
│   ├── ai_models_config.dart    # Model definitions and configuration
│   └── README_AI_MODELS.md      # This documentation
├── services/
│   └── ai_model_service.dart    # Service to manage model selection
├── utils/
│   └── ai_model_utils.dart      # Utility functions for easy access
└── widgets/
    └── ai_model_selector.dart   # UI widget for model selection
```

## 🚀 Quick Start

### 1. Get Current Model
```dart
import '../utils/ai_model_utils.dart';

// Get current model ID
String modelId = AIModelUtils.getCurrentModelId();

// Get current model object
AIModel model = AIModelUtils.getCurrentModel();

// Get model name
String modelName = AIModelUtils.getCurrentModelName();
```

### 2. Use in API Calls
```dart
import '../utils/ai_model_utils.dart';

// Create API request with current model
Map<String, dynamic> request = AIModelUtils.createAPIRequest(
  prompt: "Your prompt here",
  additionalParams: {'temperature': 0.7},
);

// The request will include:
// {
//   "prompt": "Your prompt here",
//   "model": "claude-sonnet-4-20250514",
//   "provider": "Anthropic",
//   "temperature": 0.7
// }
```

### 3. Display Model Info in UI
```dart
import '../utils/ai_model_utils.dart';

// Get model info for display
Map<String, dynamic> modelInfo = AIModelUtils.getCurrentModelForDisplay();

// Display in widget
Text('Using: ${modelInfo['name']} (${modelInfo['provider']})');
```

## 📋 Available Models

| Model ID | Name | Provider | Speed | Cost | Best For |
|----------|------|----------|-------|------|----------|
| `claude-sonnet-4-20250514` | Claude Sonnet 4 | Anthropic | Fast | High | Complex analysis |
| `claude-3-5-sonnet-20241022` | Claude 3.5 Sonnet | Anthropic | Medium | Medium | Balanced tasks |
| `claude-3-sonnet-20240229` | Claude 3 Sonnet | Anthropic | Medium | Low | Cost-effective analysis |
| `claude-3-haiku-20240307` | Claude Haiku | Anthropic | Very Fast | Very Low | Quick responses |
| `gpt-4` | GPT-4 | OpenAI | Medium | High | High-quality responses |
| `gpt-3.5-turbo` | GPT-3.5 Turbo | OpenAI | Fast | Low | Fast and affordable |

## 🔧 Adding New Models

To add a new model, edit `lib/config/ai_models_config.dart`:

```dart
// Add to the availableModels map
'your-new-model-id': AIModel(
  id: 'your-new-model-id',
  name: 'Your New Model',
  provider: 'Your Provider',
  description: 'Description of your model',
  speed: 'Fast',
  cost: 'Medium',
  color: AppTheme.primaryTeal,
  icon: Icons.auto_awesome_rounded,
),
```

## 🎯 Usage Examples

### Check Model Capabilities
```dart
// Check if current model supports analysis
if (AIModelUtils.supportsFeature('analysis')) {
  // Enable analysis features
}

// Check if it's a fast processing model
if (AIModelUtils.supportsFeature('fast_processing')) {
  // Enable quick response features
}
```

### Provider-Specific Logic
```dart
// Check if using Anthropic model
if (AIModelUtils.isCurrentModelAnthropic()) {
  // Use Anthropic-specific API endpoints
}

// Check if using OpenAI model
if (AIModelUtils.isCurrentModelOpenAI()) {
  // Use OpenAI-specific API endpoints
}
```

### Service Usage
```dart
import '../services/ai_model_service.dart';

final aiModelService = AIModelService();

// Change model
await aiModelService.changeModel('claude-3-haiku-20240307');

// Get all available models
List<AIModel> allModels = aiModelService.getAllModels();

// Reset to default
await aiModelService.resetToDefault();
```

## 🔄 Model Selection Flow

1. **User selects model** in `AIModelSelector` widget
2. **Service updates** the selection and saves to preferences
3. **Backend is notified** of the model change
4. **All app components** can access the current model via `AIModelUtils`

## 💡 Best Practices

1. **Always use `AIModelUtils`** instead of accessing the service directly
2. **Check model capabilities** before enabling features
3. **Use provider-specific logic** when needed
4. **Add new models** only in the config file
5. **Test model changes** thoroughly before deployment

## 🐛 Troubleshooting

### Model not found error
- Check if the model ID exists in `ai_models_config.dart`
- Verify the model ID is correctly spelled

### Service not initialized
- Make sure to call `AIModelService().initialize()` in your app startup
- Check if SharedPreferences is working correctly

### Backend notification failed
- The service will continue working even if backend notification fails
- Check your network connection and backend endpoint
