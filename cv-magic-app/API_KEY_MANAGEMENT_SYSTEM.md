# API Key Management System

## Overview

The API Key Management System provides dynamic, user-configurable API key management for all AI providers (OpenAI, Anthropic/Claude, and DeepSeek). This system allows users to configure their own API keys through the frontend interface, eliminating the need for server-side environment variables.

## Architecture

### Backend Components

#### 1. API Key Manager (`app/services/api_key_manager.py`)
- **Purpose**: Centralized API key storage and validation
- **Features**:
  - Secure key storage with hashing
  - Provider-specific key management
  - Real-time validation
  - Session-based storage

#### 2. Enhanced AI Service (`app/services/enhanced_ai_service.py`)
- **Purpose**: AI service with built-in API key validation
- **Features**:
  - Pre-call API key validation
  - Provider-specific error messages
  - Dynamic key management integration

#### 3. API Routes (`app/routes/api_keys.py`)
- **Endpoints**:
  - `POST /api/api-keys/set` - Set API key for provider
  - `POST /api/api-keys/validate/{provider}` - Validate API key
  - `GET /api/api-keys/status` - Get all providers status
  - `DELETE /api/api-keys/{provider}` - Remove API key
  - `DELETE /api/api-keys/` - Clear all keys

### Frontend Components

#### 1. API Key Input Dialog (`lib/widgets/api_key_input_dialog.dart`)
- **Purpose**: User-friendly API key configuration
- **Features**:
  - Secure input with visibility toggle
  - Key confirmation
  - Real-time validation
  - Provider-specific styling

#### 2. Error Notification System (`lib/widgets/api_key_error_notification.dart`)
- **Purpose**: User notification for API key issues
- **Features**:
  - Contextual error messages
  - Quick configuration access
  - Dismissible notifications

#### 3. Enhanced AI Model Selector (`lib/widgets/ai_model_selector.dart`)
- **Purpose**: Model selection with API key validation
- **Features**:
  - API key status indicators
  - Automatic key validation
  - Provider management section

## User Flow

### 1. Model Selection Flow
```
User selects model → Check API key status → 
If missing: Show API key dialog → 
If valid: Proceed with AI call
```

### 2. API Key Configuration Flow
```
User clicks "Configure" → API key dialog opens → 
User enters key → Validation → 
Success: Save and proceed / Failure: Show error
```

### 3. Error Handling Flow
```
AI call fails → Check error type → 
If API key error: Show notification → 
User can configure key or dismiss
```

## Implementation Details

### Backend Integration

The system integrates with the existing AI configuration:

```python
# app/ai/ai_config.py
def get_api_key(self, provider: str) -> Optional[str]:
    # First try dynamic API key manager
    try:
        from app.services.api_key_manager import api_key_manager
        dynamic_key = api_key_manager.get_api_key(provider)
        if dynamic_key:
            return dynamic_key
    except Exception as e:
        logger.warning(f"Failed to get dynamic API key for {provider}: {e}")
    
    # Fallback to environment variables
    # ... existing env var logic
```

### Frontend Integration

The system enhances the existing AI model selector:

```dart
// lib/widgets/ai_model_selector.dart
Future<void> _changeModel(String modelId) async {
  final provider = _getProviderFromModel(modelId);
  
  // Check if API key is configured and valid
  if (!_hasValidAPIKey(provider)) {
    _showAPIKeyRequiredDialog(provider, modelId);
    return;
  }
  
  // Proceed with model change
  // ...
}
```

## Security Features

### 1. Key Storage
- Keys are stored in a local JSON file (`api_keys.json`)
- Keys are hashed for security
- Session-based storage (not persistent across server restarts)

### 2. Validation
- Real-time API key validation
- Provider-specific validation logic
- Error handling for invalid keys

### 3. Error Handling
- Graceful fallback to environment variables
- User-friendly error messages
- No key exposure in logs

## Usage Examples

### Setting an API Key (Backend)
```python
from app.services.api_key_manager import api_key_manager

# Set API key
success = api_key_manager.set_api_key('openai', 'sk-your-key-here')

# Validate key
is_valid, message = api_key_manager.validate_api_key('openai')
```

### Setting an API Key (Frontend)
```dart
final apiKeyService = APIKeyService();
final success = await apiKeyService.setAPIKey('openai', 'sk-your-key-here');
```

### AI Call with Validation
```python
from app.services.enhanced_ai_service import enhanced_ai_service

# This will automatically validate API keys before making the call
response = await enhanced_ai_service.generate_response_with_validation(
    prompt="Your prompt here",
    system_prompt="System prompt",
    temperature=0.7
)
```

## Error Messages

### API Key Required
```
"API key required for OpenAI. Please configure your API key for this provider."
```

### API Key Invalid
```
"API key for OpenAI is invalid or service unavailable."
```

### Validation Failed
```
"Failed to validate API key for OpenAI: [specific error]"
```

## Testing

Run the test script to verify the system:

```bash
cd cv-magic-app/backend
python test_api_key_management.py
```

## Configuration

### Environment Variables (Fallback)
The system still supports environment variables as fallback:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY` or `CLAUDE_API_KEY`
- `DEEPSEEK_API_KEY`

### Frontend Configuration
Update `lib/core/config/app_config.dart`:
```dart
class AppConfig {
  static const String baseUrl = 'http://localhost:8000';
  static String authToken = ''; // Set by auth service
}
```

## Benefits

1. **User Control**: Users can configure their own API keys
2. **Cost Management**: Users control their API usage and costs
3. **Flexibility**: Support for multiple providers
4. **Security**: Secure key storage and validation
5. **User Experience**: Intuitive interface with clear error messages
6. **Fallback Support**: Environment variables still work
7. **Modular Design**: Easy to extend for new providers

## Future Enhancements

1. **Persistent Storage**: Database-backed key storage
2. **Key Rotation**: Automatic key rotation support
3. **Usage Tracking**: API usage monitoring
4. **Multi-user Support**: User-specific key management
5. **Key Encryption**: Enhanced security with encryption
6. **Provider Analytics**: Usage analytics per provider

## Troubleshooting

### Common Issues

1. **API Key Not Saving**
   - Check authentication token
   - Verify backend is running
   - Check network connectivity

2. **Validation Failing**
   - Verify API key format
   - Check provider-specific requirements
   - Ensure network connectivity to provider

3. **Frontend Not Updating**
   - Check API key service configuration
   - Verify backend endpoints
   - Check authentication flow

### Debug Steps

1. Check backend logs for API key operations
2. Verify frontend API key service configuration
3. Test API endpoints directly
4. Check authentication token validity
5. Verify provider-specific API key formats

## Support

For issues or questions:
1. Check the test script output
2. Review backend logs
3. Verify API key formats
4. Test with environment variables as fallback
