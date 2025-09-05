# Authentication System - Development Mode

## Overview

The authentication system has been set up to allow **empty credentials login** during development. This is a temporary measure to facilitate easy testing and development, and should be replaced with proper authentication before production deployment.

## How It Works

### Login with Empty Credentials

Users can login with empty email and password fields, or any credentials they want. The system will always authenticate successfully and return a valid JWT token.

**Example requests:**

```bash
# Login with empty credentials
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "", "password": ""}'

# Login with any credentials (also works)
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "anything@example.com", "password": "anypassword"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "unique-uuid",
    "email": "demo@cvapp.com",
    "name": "Demo User",
    "created_at": "2025-09-05T01:06:19.152326Z",
    "is_active": true
  }
}
```

### Protected Endpoints

Once you have a token, you can access protected endpoints by including it in the Authorization header:

```bash
curl -X GET "http://localhost:8000/api/auth/profile" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Available Endpoints

- **POST** `/api/auth/login` - Login with any credentials (returns JWT token)
- **GET** `/api/auth/profile` - Get user profile (requires authentication)
- **POST** `/api/auth/logout` - Logout (placeholder for now)
- **POST** `/api/auth/refresh` - Refresh token (placeholder for now)
- **PUT** `/api/auth/profile` - Update profile (placeholder for now)
- **POST** `/api/auth/register` - Register user (placeholder for now)

## Implementation Details

### Key Files Created/Modified:

1. **`app/models/auth.py`** - Authentication data models
2. **`app/core/auth.py`** - JWT token utilities and authentication logic
3. **`app/core/dependencies.py`** - FastAPI dependencies for protected routes
4. **`app/routes/auth.py`** - Authentication API endpoints

### Security Configuration

The JWT tokens are configured with:
- **Algorithm**: HS256
- **Access Token Expiry**: 60 minutes (configurable in `app/config.py`)
- **Refresh Token Expiry**: 7 days (configurable in `app/config.py`)
- **Secret Key**: Set in config (change in production!)

## Development Notes

⚠️ **IMPORTANT**: This setup is for development only. Before production:

1. Replace `authenticate_user()` function with proper credential verification
2. Implement proper user database storage and retrieval
3. Add password hashing and verification
4. Implement proper user registration
5. Add rate limiting for authentication endpoints
6. Update JWT secret key to a secure value
7. Consider implementing OAuth2 or other modern authentication flows

## Testing

The authentication system has been tested and verified to work correctly:
- ✅ Login with empty credentials returns valid JWT token
- ✅ Login with any credentials returns valid JWT token  
- ✅ Protected endpoints require valid JWT token
- ✅ Protected endpoints reject requests without tokens
- ✅ JWT tokens contain proper user information

## Next Steps

When ready to implement proper authentication:
1. Set up user database tables
2. Implement password hashing (bcrypt recommended)
3. Add proper email validation
4. Implement user registration with email verification
5. Add password reset functionality
6. Consider implementing session management
7. Add audit logging for security events
