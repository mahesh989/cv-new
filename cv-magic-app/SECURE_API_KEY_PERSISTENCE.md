# Secure User-Specific API Key Persistence System

## Overview

This document describes the implementation of a secure, user-specific API key persistence system that allows users to save their API keys without having to re-enter them every time they log in. The system uses encryption and database storage to ensure security while providing a seamless user experience.

## Problem Solved

**Before**: API keys were stored globally in a JSON file, shared across all users, and lost when the server restarted.

**After**: Each user has their own encrypted API keys stored in the database, persisting across sessions and server restarts.

## Security Features

### 1. User-Specific Encryption
- Each user's API keys are encrypted using a user-specific encryption key
- The encryption key is derived from the user ID and a server secret
- Keys are encrypted using Fernet (symmetric encryption) from the `cryptography` library

### 2. Database Storage
- API keys are stored in a dedicated `user_api_keys` table
- Each user can have multiple API keys (one per provider)
- Keys are never stored in plain text

### 3. Validation and Monitoring
- API keys are validated when set and periodically checked
- Validation status is tracked in the database
- Failed validations are logged for monitoring

## Architecture

### Database Schema

```sql
CREATE TABLE user_api_keys (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,  -- String to avoid UUID/INT type mismatches
    provider VARCHAR(50) NOT NULL,
    encrypted_key TEXT NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    is_valid BOOLEAN DEFAULT FALSE,
    last_validated TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, provider)
);
```

**Note**: The `user_id` column uses `VARCHAR(64)` instead of a foreign key to avoid type mismatch issues between UUID and Integer types in existing deployments.

### Key Components

#### 1. UserAPIKey Model (`app/models/user_api_keys.py`)
- Handles encryption/decryption of API keys
- Manages validation status
- Provides secure key storage and retrieval

#### 2. UserAPIKeyManager Service (`app/services/user_api_key_manager.py`)
- Manages user-specific API key operations
- Handles database interactions
- Provides validation and status checking

#### 3. Updated API Routes (`app/routes/api_keys.py`)
- Modified to use user-specific storage
- Maintains backward compatibility with initial setup
- Provides secure endpoints for authenticated users

#### 4. Enhanced AI Configuration (`app/ai/ai_config.py`)
- Updated to support user-specific API key retrieval
- Falls back to global keys for backward compatibility

## API Endpoints

### Authenticated Endpoints (User-Specific)

- `POST /api/api-keys/set` - Set API key for authenticated user
- `POST /api/api-keys/validate/{provider}` - Validate user's API key
- `GET /api/api-keys/status` - Get user's API key status
- `DELETE /api/api-keys/{provider}` - Remove user's API key
- `DELETE /api/api-keys/` - Clear all user's API keys

### Initial Setup Endpoints (Global)

- `POST /api/api-keys/set-initial` - Set API key for initial setup
- `GET /api/api-keys/status-initial` - Get global API key status

## Frontend Integration

### API Key Service Updates
The frontend `APIKeyService` has been updated to:
- Automatically use authenticated endpoints when user is logged in
- Fall back to initial setup endpoints for first-time configuration
- Handle user-specific API key persistence seamlessly

### User Experience
1. **First Time**: User sets up API keys using initial setup endpoints
2. **After Login**: API keys are automatically loaded from user-specific storage
3. **Key Management**: Users can update, validate, or remove their keys
4. **Persistence**: Keys persist across sessions and server restarts

## Security Considerations

### 1. Encryption Key Management
- Encryption keys are derived from user ID + server secret
- Server secret should be set via environment variable
- Keys are never stored in plain text

### 2. Access Control
- API keys are only accessible to the user who owns them
- Database queries are filtered by user ID
- No cross-user access is possible

### 3. Key Validation
- API keys are validated when set
- Validation status is tracked and updated
- Invalid keys are marked and can be re-validated

### 4. Audit Trail
- All API key operations are logged
- Creation, updates, and deletions are tracked
- Validation attempts are recorded

## Environment Configuration

### Required Environment Variables

```bash
# API Key Encryption Secret (REQUIRED for production)
API_KEY_ENCRYPTION_SECRET=your-secure-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/cv_magic

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440
```

### Installation Steps

1. **Install Dependencies**
   ```bash
   pip install cryptography==41.0.7
   ```

2. **Run Database Migration**
   ```bash
   alembic upgrade head
   ```

3. **Set Environment Variables**
   ```bash
   export API_KEY_ENCRYPTION_SECRET="your-secure-secret-key"
   ```

4. **Restart Application**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

## Migration from Global to User-Specific

### Backward Compatibility
- The system maintains backward compatibility with the global API key system
- Initial setup endpoints still work for first-time configuration
- Existing global keys continue to work until users set their own keys

### Migration Strategy
1. Deploy the new system alongside the existing one
2. Users will automatically get user-specific storage when they log in
3. Global keys remain available as fallback
4. Gradually migrate users to user-specific keys

## Benefits

### 1. Security
- **Encrypted Storage**: API keys are encrypted using user-specific keys
- **User Isolation**: Each user's keys are completely isolated
- **No Plain Text**: Keys are never stored in plain text

### 2. Persistence
- **Database Storage**: Keys persist across server restarts
- **Session Independence**: Keys are available across all user sessions
- **Reliability**: No more lost API keys

### 3. User Experience
- **Seamless Login**: Users don't need to re-enter API keys
- **Key Management**: Users can easily manage their keys
- **Validation**: Automatic key validation and status tracking

### 4. Scalability
- **Multi-User Support**: Each user has their own keys
- **Provider Flexibility**: Support for multiple AI providers
- **Extensible**: Easy to add new providers

## Monitoring and Maintenance

### 1. Key Validation Monitoring
- Monitor validation success/failure rates
- Alert on repeated validation failures
- Track key usage patterns

### 2. Security Monitoring
- Monitor for unusual access patterns
- Log all API key operations
- Regular security audits

### 3. Database Maintenance
- Regular cleanup of invalid keys
- Monitor database size and performance
- Backup and recovery procedures

## Troubleshooting

### Common Issues

1. **Encryption Errors**
   - Check `API_KEY_ENCRYPTION_SECRET` environment variable
   - Ensure consistent secret across deployments

2. **Database Connection Issues**
   - Verify database connectivity
   - Check migration status
   - Validate user permissions

3. **Key Validation Failures**
   - Check API key format
   - Verify provider-specific requirements
   - Test network connectivity

### Debug Steps

1. Check application logs for encryption/decryption errors
2. Verify database table creation and data
3. Test API endpoints with valid authentication
4. Validate environment variable configuration

## Future Enhancements

### 1. Advanced Security
- Key rotation support
- Hardware security module (HSM) integration
- Multi-factor authentication for key access

### 2. Usage Analytics
- API usage tracking per user
- Cost monitoring and alerts
- Usage pattern analysis

### 3. Key Management Features
- Bulk key operations
- Key sharing between users (with permissions)
- Key expiration and renewal

### 4. Integration Improvements
- OAuth integration for provider keys
- Automatic key refresh
- Provider-specific key formats

## Conclusion

The secure user-specific API key persistence system provides a robust, secure, and user-friendly solution for managing API keys in a multi-user environment. It ensures that users don't need to re-enter their API keys while maintaining the highest security standards through encryption and proper access controls.

The system is designed to be backward compatible, scalable, and maintainable, providing a solid foundation for future enhancements and growth.
