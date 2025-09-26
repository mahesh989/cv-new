import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';

class AIModel {
  final String id;
  final String name;
  final String provider;
  final String description;
  final String speed;
  final String cost;
  final Color color;
  final IconData icon;
  final bool isRecommended;
  final List<String> capabilities;

  const AIModel({
    required this.id,
    required this.name,
    required this.provider,
    required this.description,
    required this.speed,
    required this.cost,
    required this.color,
    required this.icon,
    this.isRecommended = false,
    this.capabilities = const [],
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'provider': provider,
      'description': description,
      'speed': speed,
      'cost': cost,
      'isRecommended': isRecommended,
      'capabilities': capabilities,
    };
  }

  factory AIModel.fromJson(Map<String, dynamic> json) {
    return AIModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      provider: json['provider'] ?? '',
      description: json['description'] ?? '',
      speed: json['speed'] ?? '',
      cost: json['cost'] ?? '',
      color: AppTheme.primaryTeal, // Default color
      icon: Icons.smart_toy_rounded, // Default icon
      isRecommended: json['isRecommended'] ?? false,
      capabilities: List<String>.from(json['capabilities'] ?? []),
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is AIModel && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

class AIModelsConfig {
  static const Map<String, AIModel> availableModels = {
    'gpt-4o': AIModel(
      id: 'gpt-4o',
      name: 'GPT-4o',
      provider: 'OpenAI',
      description: 'Most capable GPT model with vision',
      speed: 'Fast',
      cost: 'High',
      color: AppTheme.primaryCosmic,
      icon: Icons.auto_awesome_rounded,
      isRecommended: true,
      capabilities: ['Text', 'Vision', 'Code', 'Analysis'],
    ),
    'gpt-4o-mini': AIModel(
      id: 'gpt-4o-mini',
      name: 'GPT-4o Mini',
      provider: 'OpenAI',
      description: 'Faster and cost-effective GPT model',
      speed: 'Very Fast',
      cost: 'Medium',
      color: AppTheme.primaryNeon,
      icon: Icons.flash_on_rounded,
      capabilities: ['Text', 'Code', 'Analysis'],
    ),
    'gpt-3.5-turbo': AIModel(
      id: 'gpt-3.5-turbo',
      name: 'GPT-3.5 Turbo',
      provider: 'OpenAI',
      description: 'Fast and reliable for most tasks',
      speed: 'Very Fast',
      cost: 'Low',
      color: AppTheme.primaryEmerald,
      icon: Icons.speed_rounded,
      capabilities: ['Text', 'Code'],
    ),
    'claude-3.5-sonnet': AIModel(
      id: 'claude-3.5-sonnet',
      name: 'Claude 3.5 Sonnet',
      provider: 'Anthropic',
      description: 'Advanced reasoning and analysis',
      speed: 'Fast',
      cost: 'High',
      color: AppTheme.primaryAurora,
      icon: Icons.psychology_alt_rounded,
      isRecommended: true,
      capabilities: ['Text', 'Code', 'Analysis', 'Reasoning'],
    ),
    'claude-3-haiku': AIModel(
      id: 'claude-3-haiku',
      name: 'Claude 3 Haiku',
      provider: 'Anthropic',
      description: 'Fast and efficient for quick tasks',
      speed: 'Very Fast',
      cost: 'Low',
      color: AppTheme.primaryTeal,
      icon: Icons.flash_on_rounded,
      capabilities: ['Text', 'Quick Analysis'],
    ),
    'deepseek-chat': AIModel(
      id: 'deepseek-chat',
      name: 'DeepSeek Chat',
      provider: 'DeepSeek',
      description: 'Advanced reasoning and coding',
      speed: 'Fast',
      cost: 'Very Low',
      color: AppTheme.primaryEmerald,
      icon: Icons.code_rounded,
      isRecommended: true,
      capabilities: ['Text', 'Code', 'Reasoning'],
    ),
    'deepseek-coder': AIModel(
      id: 'deepseek-coder',
      name: 'DeepSeek Coder',
      provider: 'DeepSeek',
      description: 'Specialized for coding tasks',
      speed: 'Fast',
      cost: 'Very Low',
      color: AppTheme.primaryCosmic,
      icon: Icons.terminal_rounded,
      capabilities: ['Code', 'Programming'],
    ),
    'deepseek-reasoner': AIModel(
      id: 'deepseek-reasoner',
      name: 'DeepSeek Reasoner',
      provider: 'DeepSeek',
      description: 'Advanced reasoning and analysis',
      speed: 'Medium',
      cost: 'Low',
      color: AppTheme.primaryAurora,
      icon: Icons.psychology_alt_rounded,
      capabilities: ['Reasoning', 'Analysis', 'Problem Solving'],
    ),
    'gpt-5-nano': AIModel(
      id: 'gpt-5-nano',
      name: 'GPT-5 Nano',
      provider: 'OpenAI',
      description: 'Latest nano model with flexible service tier',
      speed: 'Very Fast',
      cost: 'Very Low',
      color: AppTheme.primaryNeon,
      icon: Icons.bolt_rounded,
      isRecommended: true,
      capabilities: ['Text', 'Code', 'Analysis', 'Fast Processing', 'Flexible'],
    ),
  };

  // Default model
  static const String defaultModelId = 'gpt-4o-mini';

  // Get model by ID
  static AIModel? getModel(String id) {
    return availableModels[id];
  }

  // Get all model IDs
  static List<String> getAllModelIds() {
    return availableModels.keys.toList();
  }

  // Get all models
  static List<AIModel> getAllModels() {
    return availableModels.values.toList();
  }

  // Get recommended models
  static List<AIModel> getRecommendedModels() {
    return availableModels.values
        .where((model) => model.isRecommended)
        .toList();
  }

  // Get models by provider
  static List<AIModel> getModelsByProvider(String provider) {
    return availableModels.values
        .where((model) => model.provider == provider)
        .toList();
  }

  // Get models by capability
  static List<AIModel> getModelsByCapability(String capability) {
    return availableModels.values
        .where((model) => model.capabilities.contains(capability))
        .toList();
  }

  // Check if model exists
  static bool modelExists(String id) {
    return availableModels.containsKey(id);
  }

  // Get all providers
  static List<String> getAllProviders() {
    return availableModels.values
        .map((model) => model.provider)
        .toSet()
        .toList();
  }

  // Get default model - returns null to force user selection
  static AIModel? getDefaultModel() {
    // No default model - user must select provider and configure API key first
    return null;
  }
}
