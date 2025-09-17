# Multi-Provider AI Architecture - Deep Dive with Examples

## Overview

The CV-Magic-App implements a sophisticated multi-provider AI architecture that allows seamless switching between different AI providers (OpenAI, Anthropic, DeepSeek) while maintaining a consistent interface and experience. This architecture provides redundancy, cost optimization, and the ability to leverage the best features of each provider.

## Architecture Components

### 1. Base Provider Interface

The foundation of the multi-provider architecture is the `BaseAIProvider` abstract class that defines a common interface:

```python
# backend/app/ai/base_provider.py

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class AIResponse:
    """Standardized response format for all AI providers"""
    def __init__(
        self, 
        content: str, 
        model: str, 
        provider: str, 
        tokens_used: Optional[int] = None,
        cost: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.model = model
        self.provider = provider
        self.tokens_used = tokens_used
        self.cost = cost
        self.metadata = metadata or {}

class BaseAIProvider(ABC):
    """Abstract base class for all AI providers"""
    
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.provider_name = self._get_provider_name()
    
    @abstractmethod
    def _get_provider_name(self) -> str:
        """Return the name of this provider"""
        pass
    
    @abstractmethod
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """Generate a response from the AI model"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Return list of available models for this provider"""
        pass
```

### 2. Provider Implementations

#### OpenAI Provider Example

```python
# backend/app/ai/providers/openai_provider.py

import openai
from app.ai.base_provider import BaseAIProvider, AIResponse

class OpenAIProvider(BaseAIProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        super().__init__(api_key, model_name)
        self.client = openai.OpenAI(api_key=api_key)
    
    def _get_provider_name(self) -> str:
        return "openai"
    
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """Generate response using OpenAI"""
        
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add user prompt
        messages.append({"role": "user", "content": prompt})
        
        # Make API call
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract response data
        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        cost = self._calculate_cost(tokens_used)
        
        return AIResponse(
            content=content,
            model=self.model_name,
            provider=self.provider_name,
            tokens_used=tokens_used,
            cost=cost,
            metadata={
                "finish_reason": response.choices[0].finish_reason,
                "response_id": response.id
            }
        )
    
    def get_available_models(self) -> List[str]:
        return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
```

#### Anthropic Provider Example

```python
# backend/app/ai/providers/anthropic_provider.py

import anthropic
from app.ai.base_provider import BaseAIProvider, AIResponse

class AnthropicProvider(BaseAIProvider):
    """Anthropic (Claude) provider implementation"""
    
    def __init__(self, api_key: str, model_name: str = "claude-3-5-haiku-20241022"):
        super().__init__(api_key, model_name)
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def _get_provider_name(self) -> str:
        return "anthropic"
    
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """Generate response using Anthropic Claude"""
        
        # Prepare request parameters
        request_params = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens or 4000,  # Claude requires max_tokens
        }
        
        # Add system prompt if provided
        if system_prompt:
            request_params["system"] = system_prompt
        
        # Make API call
        response = self.client.messages.create(**request_params)
        
        # Extract response data
        content = response.content[0].text
        tokens_used = response.usage.input_tokens + response.usage.output_tokens
        cost = self._calculate_cost(tokens_used)
        
        return AIResponse(
            content=content,
            model=self.model_name,
            provider=self.provider_name,
            tokens_used=tokens_used,
            cost=cost,
            metadata={
                "stop_reason": response.stop_reason,
                "response_id": response.id
            }
        )
    
    def get_available_models(self) -> List[str]:
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229"
        ]
```

### 3. Central AI Service Manager

The `AIServiceManager` orchestrates all providers and provides a unified interface:

```python
# backend/app/ai/ai_service.py

class AIServiceManager:
    """Centralized AI service manager"""
    
    def __init__(self):
        self.config = ai_config
        self._providers: Dict[str, BaseAIProvider] = {}
        self._provider_classes = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "deepseek": DeepSeekProvider
        }
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available providers based on API keys"""
        for provider_name, provider_class in self._provider_classes.items():
            api_key = self.config.get_api_key(provider_name)
            if api_key:
                try:
                    available_models = self.config.get_available_models(provider_name)
                    if available_models:
                        default_model = available_models[0]
                        provider_instance = provider_class(api_key, default_model)
                        if provider_instance.is_available():
                            self._providers[provider_name] = provider_instance
                            logger.info(f"✅ Initialized {provider_name} provider")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize {provider_name}: {e}")
    
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        provider_name: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Generate response using current or specified provider"""
        
        # Determine which provider to use
        if provider_name:
            provider = self.get_provider(provider_name)
            if not provider:
                raise Exception(f"Provider {provider_name} not available")
        else:
            provider = self.get_current_provider()
            if not provider:
                raise Exception("No available AI provider")
        
        # Generate response
        return await provider.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
```

## Real-World Examples

### Example 1: CV Analysis with Provider Fallback

```python
# Example showing automatic provider fallback

async def analyze_cv_with_fallback(cv_text: str):
    """Analyze CV with automatic provider fallback"""
    
    system_prompt = """
    You are an expert CV analyzer. Extract:
    1. Technical skills
    2. Years of experience  
    3. Key achievements
    """
    
    # Primary attempt with Claude (best for analysis)
    try:
        response = await ai_service.generate_response(
            prompt=f"Analyze this CV: {cv_text}",
            system_prompt=system_prompt,
            provider_name="anthropic"
        )
        logger.info(f"✅ CV analyzed using Claude: {response.cost:.4f}$")
        return response
        
    except Exception as e:
        logger.warning(f"Claude failed: {e}, trying OpenAI...")
        
        # Fallback to OpenAI
        try:
            response = await ai_service.generate_response(
                prompt=f"Analyze this CV: {cv_text}",
                system_prompt=system_prompt,
                provider_name="openai"
            )
            logger.info(f"✅ CV analyzed using OpenAI: {response.cost:.4f}$")
            return response
            
        except Exception as e2:
            logger.warning(f"OpenAI failed: {e2}, trying DeepSeek...")
            
            # Final fallback to DeepSeek (most cost-effective)
            response = await ai_service.generate_response(
                prompt=f"Analyze this CV: {cv_text}",
                system_prompt=system_prompt,
                provider_name="deepseek"
            )
            logger.info(f"✅ CV analyzed using DeepSeek: {response.cost:.4f}$")
            return response
```

### Example 2: Smart Model Selection Based on Task

```python
# Example showing intelligent model selection

class SmartModelSelector:
    """Selects optimal model based on task characteristics"""
    
    @staticmethod
    def select_optimal_provider(task_type: str, text_length: int, budget_priority: str):
        """Select best provider/model combination"""
        
        if task_type == "code_analysis":
            return {
                "provider": "deepseek",
                "model": "deepseek-coder",
                "reason": "Specialized for code analysis"
            }
        
        elif task_type == "complex_reasoning":
            if budget_priority == "performance":
                return {
                    "provider": "anthropic", 
                    "model": "claude-3-5-sonnet-20241022",
                    "reason": "Best reasoning capabilities"
                }
            else:
                return {
                    "provider": "deepseek",
                    "model": "deepseek-reasoner", 
                    "reason": "Good reasoning at low cost"
                }
        
        elif task_type == "cv_analysis":
            if text_length > 5000:  # Large CV
                return {
                    "provider": "anthropic",
                    "model": "claude-3-5-haiku-20241022",
                    "reason": "Large context window, fast processing"
                }
            else:  # Standard CV
                return {
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "reason": "Cost-effective for standard analysis"
                }
        
        elif task_type == "bulk_processing":
            return {
                "provider": "deepseek",
                "model": "deepseek-chat",
                "reason": "Most cost-effective for bulk operations"
            }
        
        # Default fallback
        return {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "reason": "Reliable general-purpose model"
        }

# Usage example
async def analyze_cv_intelligently(cv_text: str, budget_priority: str = "balanced"):
    """Analyze CV using intelligently selected model"""
    
    # Select optimal provider
    selection = SmartModelSelector.select_optimal_provider(
        task_type="cv_analysis",
        text_length=len(cv_text),
        budget_priority=budget_priority
    )
    
    logger.info(f"Selected {selection['provider']}/{selection['model']}: {selection['reason']}")
    
    # Switch to selected model
    success = ai_service.switch_provider(selection['provider'], selection['model'])
    if not success:
        logger.warning(f"Failed to switch to {selection['provider']}, using current provider")
    
    # Perform analysis
    response = await ai_service.analyze_cv_content(cv_text)
    
    return {
        "analysis": response.content,
        "model_used": f"{response.provider}/{response.model}",
        "cost": response.cost,
        "tokens": response.tokens_used,
        "selection_reason": selection['reason']
    }
```

### Example 3: Parallel Processing with Multiple Providers

```python
# Example showing parallel processing across providers

import asyncio

async def parallel_cv_analysis(cv_text: str):
    """Run CV analysis on multiple providers in parallel for comparison"""
    
    system_prompt = "Analyze this CV and extract key skills and experience level."
    
    async def analyze_with_provider(provider_name: str):
        try:
            response = await ai_service.generate_response(
                prompt=f"CV to analyze: {cv_text}",
                system_prompt=system_prompt,
                provider_name=provider_name,
                temperature=0.3  # Lower temperature for consistency
            )
            return {
                "provider": provider_name,
                "model": response.model,
                "content": response.content,
                "cost": response.cost,
                "tokens": response.tokens_used,
                "success": True
            }
        except Exception as e:
            return {
                "provider": provider_name,
                "error": str(e),
                "success": False
            }
    
    # Get available providers
    available_providers = ai_service.get_available_providers()
    
    # Run analysis in parallel
    tasks = [analyze_with_provider(provider) for provider in available_providers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    successful_analyses = [r for r in results if isinstance(r, dict) and r.get('success')]
    failed_analyses = [r for r in results if isinstance(r, dict) and not r.get('success')]
    
    return {
        "successful_analyses": len(successful_analyses),
        "failed_analyses": len(failed_analyses),
        "results": successful_analyses,
        "failures": failed_analyses,
        "total_cost": sum(r.get('cost', 0) for r in successful_analyses),
        "consensus_analysis": _extract_consensus(successful_analyses)
    }

def _extract_consensus(analyses: list):
    """Extract consensus from multiple AI analyses"""
    if not analyses:
        return "No successful analyses"
    
    if len(analyses) == 1:
        return analyses[0]['content']
    
    # Simple approach: return the analysis from the most expensive/capable model
    # In practice, you might implement more sophisticated consensus logic
    most_expensive = max(analyses, key=lambda x: x.get('cost', 0))
    return {
        "primary_analysis": most_expensive['content'],
        "provider_consensus": f"Based on {len(analyses)} providers",
        "alternative_views": [a['content'][:200] + "..." for a in analyses if a != most_expensive]
    }
```

### Example 4: Cost-Aware Batch Processing

```python
# Example showing cost-aware batch processing

class CostAwareBatchProcessor:
    """Process multiple CVs with cost optimization"""
    
    def __init__(self, budget_limit: float):
        self.budget_limit = budget_limit
        self.current_cost = 0.0
        self.processed_count = 0
    
    async def process_cv_batch(self, cv_texts: List[str]) -> Dict:
        """Process batch of CVs with cost control"""
        
        results = []
        
        for i, cv_text in enumerate(cv_texts):
            # Check budget
            if self.current_cost >= self.budget_limit:
                logger.warning(f"Budget limit reached at CV {i}/{len(cv_texts)}")
                break
            
            # Select cost-effective provider for batch processing
            remaining_budget = self.budget_limit - self.current_cost
            remaining_cvs = len(cv_texts) - i
            budget_per_cv = remaining_budget / remaining_cvs
            
            # Choose provider based on budget per CV
            if budget_per_cv > 0.01:  # High budget per CV
                provider = "anthropic"
                model = "claude-3-5-haiku-20241022"
            elif budget_per_cv > 0.005:  # Medium budget
                provider = "openai" 
                model = "gpt-4o-mini"
            else:  # Low budget
                provider = "deepseek"
                model = "deepseek-chat"
            
            logger.info(f"Processing CV {i+1}/{len(cv_texts)} with {provider} (budget: ${budget_per_cv:.4f})")
            
            try:
                # Switch to cost-appropriate provider
                ai_service.switch_provider(provider, model)
                
                # Analyze CV
                response = await ai_service.analyze_cv_content(cv_text)
                
                self.current_cost += response.cost or 0
                self.processed_count += 1
                
                results.append({
                    "cv_index": i,
                    "analysis": response.content,
                    "provider": response.provider,
                    "model": response.model,
                    "cost": response.cost,
                    "tokens": response.tokens_used,
                    "success": True
                })
                
                logger.info(f"✅ CV {i+1} processed - Cost: ${response.cost:.4f}, Total: ${self.current_cost:.4f}")
                
            except Exception as e:
                logger.error(f"❌ Failed to process CV {i+1}: {e}")
                results.append({
                    "cv_index": i,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "total_processed": self.processed_count,
            "total_cost": self.current_cost,
            "budget_used_percent": (self.current_cost / self.budget_limit) * 100,
            "results": results,
            "cost_per_cv": self.current_cost / max(self.processed_count, 1)
        }
```

## Flutter Frontend Integration

### Example 5: Frontend Model Management

```dart
// mobile_app/lib/services/ai_model_service.dart

class AIModelService extends ChangeNotifier {
  
  // Change AI model with backend synchronization
  Future<void> changeModel(String modelId) async {
    final newModel = AIModelsConfig.getModel(modelId);
    if (newModel == null) return;

    try {
      // Save locally first
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('selected_ai_model', modelId);
      
      // Update UI immediately
      _currentModel = newModel;
      notifyListeners();
      
      // Sync with backend
      await _syncModelWithBackend(modelId);
      
    } catch (e) {
      debugPrint('❌ Error changing AI model: $e');
    }
  }
  
  // Backend synchronization
  Future<void> _syncModelWithBackend(String modelId) async {
    final model = AIModelsConfig.getModel(modelId);
    if (model == null) return;
    
    // Map frontend model ID to backend format
    String provider = model.provider.toLowerCase();
    String apiModelName = _getBackendModelName(modelId);
    
    final response = await http.post(
      Uri.parse('http://localhost:8000/api/skill-extraction/set-ai-model'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'provider': provider,
        'model': apiModelName,
      }),
    );
    
    if (response.statusCode == 200) {
      debugPrint('✅ Backend model synced: $provider/$apiModelName');
    }
  }
  
  // Get model recommendations based on current task
  List<AIModel> getRecommendedModelsForTask(String taskType) {
    switch (taskType) {
      case 'cv_analysis':
        return [
          AIModelsConfig.getModel('gpt-4o-mini')!,
          AIModelsConfig.getModel('claude-3-haiku')!,
        ];
      case 'job_matching':
        return [
          AIModelsConfig.getModel('claude-3.5-sonnet')!,
          AIModelsConfig.getModel('gpt-4o')!,
        ];
      case 'code_review':
        return [
          AIModelsConfig.getModel('deepseek-coder')!,
          AIModelsConfig.getModel('gpt-4o')!,
        ];
      default:
        return getRecommendedModels();
    }
  }
}
```

### Example 6: Dynamic UI Based on Available Providers

```dart
// Flutter widget showing provider status and selection

class AIProviderSelector extends StatefulWidget {
  @override
  _AIProviderSelectorState createState() => _AIProviderSelectorState();
}

class _AIProviderSelectorState extends State<AIProviderSelector> {
  Map<String, dynamic>? backendStatus;
  
  @override
  void initState() {
    super.initState();
    _loadBackendStatus();
  }
  
  Future<void> _loadBackendStatus() async {
    try {
      final response = await http.get(
        Uri.parse('http://localhost:8000/api/ai/status')
      );
      
      if (response.statusCode == 200) {
        setState(() {
          backendStatus = jsonDecode(response.body);
        });
      }
    } catch (e) {
      debugPrint('Error loading backend status: $e');
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('AI Providers', style: Theme.of(context).textTheme.headline6),
            SizedBox(height: 12),
            
            if (backendStatus != null) ...[
              // Show current provider status
              _buildCurrentProviderStatus(),
              SizedBox(height: 16),
              
              // Show available providers
              _buildProviderList(),
              SizedBox(height: 16),
              
              // Show model performance stats
              _buildPerformanceStats(),
            ] else
              CircularProgressIndicator(),
          ],
        ),
      ),
    );
  }
  
  Widget _buildCurrentProviderStatus() {
    final currentStatus = backendStatus!['current_status'];
    
    return Container(
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.green.shade200),
      ),
      child: Row(
        children: [
          Icon(Icons.check_circle, color: Colors.green),
          SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Current: ${currentStatus['current_provider']}'),
                Text('Model: ${currentStatus['current_model']}'),
                Text('Providers available: ${currentStatus['total_providers']}'),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildProviderList() {
    final providers = backendStatus!['providers'];
    
    return Column(
      children: providers.entries.map<Widget>((entry) {
        final providerName = entry.key;
        final providerInfo = entry.value;
        final isAvailable = providerInfo['available'] == true;
        
        return ListTile(
          leading: Icon(
            isAvailable ? Icons.cloud_done : Icons.cloud_off,
            color: isAvailable ? Colors.green : Colors.red,
          ),
          title: Text(providerName.toUpperCase()),
          subtitle: Text(
            isAvailable 
              ? 'Available • ${providerInfo['current_model']}'
              : 'Not available • ${providerInfo['error'] ?? 'No API key'}'
          ),
          trailing: isAvailable 
            ? IconButton(
                icon: Icon(Icons.settings),
                onPressed: () => _showProviderSettings(providerName),
              )
            : null,
        );
      }).toList(),
    );
  }
  
  Widget _buildPerformanceStats() {
    // Show cost and performance statistics
    return Container(
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Performance Stats', style: TextStyle(fontWeight: FontWeight.bold)),
          SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Avg Response Time: 2.3s'),
              Text('Total Requests: 156'),
            ],
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Avg Cost per Request: \$0.003'),
              Text('Success Rate: 98.7%'),
            ],
          ),
        ],
      ),
    );
  }
}
```

## Benefits of Multi-Provider Architecture

### 1. **Redundancy and Reliability**
- Automatic fallback to alternative providers
- No single point of failure
- Service continuity during provider outages

### 2. **Cost Optimization**
- Use cost-effective models for simple tasks
- Reserve expensive models for complex analysis
- Dynamic budget allocation

### 3. **Performance Optimization**
- Leverage each provider's strengths
- Model specialization (coding, reasoning, analysis)
- Speed vs quality trade-offs

### 4. **Scalability**
- Distribute load across multiple providers
- Parallel processing capabilities
- Rate limit management

### 5. **Future-Proofing**
- Easy integration of new providers
- Model upgrade path
- Technology diversification

This multi-provider architecture ensures the CV-Magic-App remains flexible, cost-effective, and reliable while providing the best possible AI-powered features to users.
