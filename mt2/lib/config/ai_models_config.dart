import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class AIModel {
  final String id;
  final String name;
  final String provider;
  final String description;
  final String speed;
  final String cost;
  final Color color;
  final IconData icon;

  const AIModel({
    required this.id,
    required this.name,
    required this.provider,
    required this.description,
    required this.speed,
    required this.cost,
    required this.color,
    required this.icon,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'provider': provider,
      'description': description,
      'speed': speed,
      'cost': cost,
      'color': color,
      'icon': icon,
    };
  }
}

class AIModelsConfig {
  // DeepSeek-only models configuration
  static const Map<String, AIModel> availableModels = {
    'deepseek-chat': AIModel(
      id: 'deepseek-chat',
      name: 'DeepSeek Chat',
      provider: 'DeepSeek',
      description: 'Advanced reasoning and coding - Default',
      speed: 'Fast',
      cost: 'Very Low',
      color: AppTheme.primaryTeal,
      icon: Icons.code_rounded,
    ),
    'deepseek-coder': AIModel(
      id: 'deepseek-coder',
      name: 'DeepSeek Coder',
      provider: 'DeepSeek',
      description: 'Specialized for coding tasks',
      speed: 'Fast',
      cost: 'Very Low',
      color: AppTheme.primaryEmerald,
      icon: Icons.terminal_rounded,
    ),
    'deepseek-reasoner': AIModel(
      id: 'deepseek-reasoner',
      name: 'DeepSeek Reasoner',
      provider: 'DeepSeek',
      description: 'Advanced reasoning and analysis',
      speed: 'Medium',
      cost: 'Low',
      color: AppTheme.primaryCosmic,
      icon: Icons.psychology_alt_rounded,
    ),
  };

  // Default model - using DeepSeek only
  static const String defaultModelId = 'deepseek-chat';

  // Get model by ID
  static AIModel? getModel(String id) {
    return availableModels[id];
  }

  // Get default model
  static AIModel getDefaultModel() {
    return availableModels[defaultModelId]!;
  }

  // Get all model IDs
  static List<String> getAllModelIds() {
    return availableModels.keys.toList();
  }

  // Get all models
  static List<AIModel> getAllModels() {
    return availableModels.values.toList();
  }

  // Check if model exists
  static bool modelExists(String id) {
    return availableModels.containsKey(id);
  }

  // Get model info as Map (for backward compatibility)
  static Map<String, dynamic> getModelAsMap(String id) {
    final model = getModel(id);
    if (model != null) {
      return model.toMap();
    }
    return getDefaultModel().toMap();
  }

  // Get all models as Map (for backward compatibility)
  static Map<String, Map<String, dynamic>> getAllModelsAsMap() {
    final Map<String, Map<String, dynamic>> result = {};
    for (final entry in availableModels.entries) {
      result[entry.key] = entry.value.toMap();
    }
    return result;
  }
}
