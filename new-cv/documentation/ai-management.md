# Centralized AI Management System

## Overview

The CV application now includes a **centralized AI management system** that provides seamless integration with multiple AI providers (OpenAI, Anthropic Claude, DeepSeek). The system allows dynamic switching between providers and models, unified API interface, and specialized CV analysis capabilities.

## 🏗️ Architecture

### Core Components

1. **AI Configuration Manager** (`app/ai/ai_config.py`)
   - Manages API keys and provider configurations
   - Handles model selection and switching
   - Provides cost and performance information

2. **Base Provider Interface** (`app/ai/base_provider.py`)
   - Abstract interface that all providers must implement
   - Standardized `AIResponse` format
   - Consistent API across all providers

3. **Provider Implementations** (`app/ai/providers/`)
   - `OpenAIProvider` - OpenAI GPT models
   - `AnthropicProvider` - Anthropic Claude models
   - `DeepSeekProvider` - DeepSeek models

4. **AI Service Manager** (`app/ai/ai_service.py`)
   - Centralized service for all AI operations
   - Provider switching and management
   - Specialized CV analysis methods

5. **API Endpoints** (`app/routes/ai.py`)
   - RESTful API for AI operations
   - Authentication-protected endpoints
   - Comprehensive error handling

## 📡 API Endpoints

### Base URL
```
http://localhost:8000/api/ai
```

### Available Endpoints

#### 🔍 Status & Information
- **GET** `/health` - AI service health check (no auth required)
- **GET** `/status` - Complete AI system status
- **GET** `/providers` - Available providers list
- **GET** `/models` - Available models by provider
- **GET** `/current` - Current provider/model configuration

#### ⚙️ Configuration Management
- **POST** `/switch-provider` - Switch to different provider
- **POST** `/switch-model` - Switch model within current provider

#### 🤖 AI Operations
- **POST** `/chat` - General AI chat completion
- **POST** `/analyze-cv` - CV content analysis
- **POST** `/compare-cv-job` - CV vs job description comparison

## 🚀 Usage Examples

### 1. Check AI System Status

```bash
# Get authentication token
ACCESS_TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "", "password": ""}' | jq -r '.access_token')

# Check AI status
curl -X GET "http://localhost:8000/api/ai/status" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

**Response:**
```json
{
  "current_status": {
    "current_provider": "openai",
    "current_model": "gpt-4o-mini",
    "provider_available": true,
    "total_providers": 3,
    "available_providers": ["openai", "anthropic", "deepseek"]
  },
  "providers": {
    "openai": {
      "provider": "openai",
      "available": true,
      "api_key_configured": true,
      "current_model": "gpt-4o-mini",
      "is_current": true
    }
  },
  "available_models": {
    "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
  }
}
```

### 2. Switch AI Provider

```bash
curl -X POST "http://localhost:8000/api/ai/switch-provider" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"provider": "anthropic", "model": "claude-3-5-haiku-20241022"}' | jq
```

### 3. Analyze CV Content

```bash
curl -X POST "http://localhost:8000/api/ai/analyze-cv" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "John Doe\nSoftware Engineer\n5 years Python, React, AWS...",
    "provider": "openai"
  }' | jq
```

**Response:**
```json
{
  "analysis": "{\"technical_skills\": [\"Python\", \"React\", \"AWS\"], \"soft_skills\": [\"Leadership\"], \"experience_years\": 5}",
  "model_used": "gpt-4o-mini",
  "provider_used": "openai",
  "tokens_used": 150,
  "cost": 0.0023,
  "analyzed_at": "2025-01-01T00:00:00Z"
}
```

### 4. Compare CV with Job

```bash
curl -X POST "http://localhost:8000/api/ai/compare-cv-job" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "John Doe - Python Developer...",
    "job_description": "We need a senior Python developer with React experience..."
  }' | jq
```

### 5. General AI Chat

```bash
curl -X POST "http://localhost:8000/api/ai/chat" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain machine learning in simple terms",
    "system_prompt": "You are a helpful AI assistant",
    "temperature": 0.7,
    "max_tokens": 500
  }' | jq
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Configuration  
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# DeepSeek Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Default AI Settings
DEFAULT_AI_PROVIDER=openai
DEFAULT_AI_MODEL=gpt-4o-mini
```

### Provider Configuration

The system automatically detects available providers based on configured API keys:

- **OpenAI**: Requires `OPENAI_API_KEY`
- **Anthropic**: Requires `ANTHROPIC_API_KEY`  
- **DeepSeek**: Requires `DEEPSEEK_API_KEY`

## 📊 Supported Models

### OpenAI Models
- `gpt-4o` - Most advanced GPT-4 model
- `gpt-4o-mini` - Cost-effective GPT-4 variant (recommended)
- `gpt-4-turbo` - High-performance with large context
- `gpt-3.5-turbo` - Fast and economical

### Anthropic (Claude) Models
- `claude-3-5-sonnet-20241022` - Most intelligent Claude model
- `claude-3-5-haiku-20241022` - Fastest for everyday tasks (recommended)
- `claude-3-opus-20240229` - Most powerful for complex tasks

### DeepSeek Models
- `deepseek-chat` - General-purpose chat model (recommended)
- `deepseek-coder` - Specialized for coding tasks
- `deepseek-reasoner` - Advanced reasoning capabilities

## 💰 Cost Management

The system tracks token usage and calculates costs:

- **Automatic cost calculation** for all providers
- **Token usage tracking** for optimization
- **Model pricing information** built-in
- **Cost-effective model recommendations**

## 🔒 Security Features

- **JWT Authentication** required for all endpoints (except health check)
- **API key protection** via environment variables
- **Input validation** on all requests
- **Rate limiting** (configured in FastAPI settings)
- **Error handling** with proper HTTP status codes

## 🚦 Provider Status

The system provides real-time provider status:

- **Available**: Provider initialized and ready
- **Configured**: API key configured but provider not available
- **Failed**: Initialization failed (check API key/connectivity)
- **Missing**: No API key configured

## 🔄 Dynamic Switching

### Runtime Provider Switching
- Switch between providers without restarting
- Automatic fallback to available providers
- Model switching within providers
- Configuration persistence

### Smart Defaults
- Automatic provider selection based on API keys
- Cost-optimized model selection
- Fallback provider chain

## 🎯 CV Analysis Features

### CV Content Analysis
- **Technical skills extraction**
- **Soft skills identification** 
- **Experience level estimation**
- **Education summary**
- **Key achievements extraction**
- **Professional summary generation**

### Job Matching
- **Match score calculation** (0-100)
- **Skill gap analysis**
- **Recommendation generation**
- **Strength highlighting**
- **Application optimization tips**

## 📈 Performance Optimization

### Model Selection Guidelines

**For CV Analysis:**
- **Light analysis**: `gpt-4o-mini` or `claude-3-5-haiku-20241022`
- **Detailed analysis**: `gpt-4o` or `claude-3-5-sonnet-20241022`
- **Code-heavy CVs**: `deepseek-coder`

**For Job Matching:**
- **Quick matching**: `gpt-4o-mini` or `deepseek-chat`
- **Detailed comparison**: `claude-3-5-sonnet-20241022`
- **Technical roles**: `deepseek-reasoner`

## 🐛 Troubleshooting

### Common Issues

1. **"No available AI provider"**
   - Check API keys in `.env` file
   - Verify internet connectivity
   - Check provider status via `/status` endpoint

2. **"Provider failed to initialize"**
   - Verify API key validity
   - Check API key permissions
   - Test with provider health endpoints

3. **High costs**
   - Switch to more cost-effective models
   - Reduce `max_tokens` parameter
   - Use appropriate models for task complexity

### Health Checks

```bash
# Check overall health
curl "http://localhost:8000/api/ai/health"

# Check detailed status  
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/ai/status"
```

## 🔮 Future Enhancements

### Planned Features
- **Model performance metrics**
- **Usage analytics and reporting**
- **Custom model fine-tuning**
- **Batch processing capabilities**
- **Advanced caching mechanisms**
- **Multi-language support**

### Integration Possibilities
- **Vector databases** for semantic search
- **Image analysis** for CV photo processing
- **Speech-to-text** for video CV analysis
- **Custom training** on domain-specific data

---

## 🎉 Success! 

Your centralized AI management system is now **fully operational** with:

✅ **3 AI providers implemented** (OpenAI, Anthropic, DeepSeek)  
✅ **Dynamic provider switching**  
✅ **Unified API interface**  
✅ **CV analysis capabilities**  
✅ **Job matching functionality**  
✅ **Cost tracking and optimization**  
✅ **Comprehensive API endpoints**  
✅ **Authentication and security**  

**Ready for production use!** 🚀
