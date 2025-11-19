# API Key Configuration Issue - Analysis and Fix

## Problem Description

When a new user signs up and logs in for the first time, they see an API key already configured in the home tab, even though they haven't configured any API keys. This appears to be using another user's API key configuration.

## Root Cause Analysis

The issue had **two main causes**:

### 1. Global State Sharing
The `ai_config` object maintains `_current_provider` and `_current_model` as instance variables that are **shared across all users**:
- When User A configures an API key, global state is set
- When User B (new user) logs in, these global values persist from User A's session
- Missing initialization in status endpoint returned stale provider information

### 2. **Orphaned API Keys from User ID Reuse** (PRIMARY ISSUE)
**This was the actual root cause:**
- When users are deleted, their API keys remain in the database (no CASCADE DELETE)
- When new users register, they can get the same user ID (auto-increment reuse)
- New users inherit API keys from deleted users with the same ID
- Example: User ID 3 (jasmine@gmail.com) created today but has API key from 2025-10-25

**Evidence from logs:**
- User jasmine@gmail.com (ID: 3) created on 2025-11-19
- But has API key created on 2025-10-25 (before user existed!)
- Multiple orphaned API keys found for deleted users (IDs 4, 5, 7, 8, 9, 10)

## Solution Implemented

### 1. Clean Up Orphaned API Keys During Registration

**File**: `cv-magic-app/backend/app/routes/auth.py`

Added cleanup logic in `register()` endpoint to:
- Remove any orphaned API keys for the new user ID
- Prevents new users from inheriting API keys from deleted users with the same ID

### 2. Validate API Key Ownership During Retrieval

**File**: `cv-magic-app/backend/app/services/user_api_key_manager.py`

Added safety check in `get_api_key()` method to:
- Verify API key was created **after** the user account was created
- If API key is older than user account, it's orphaned - remove it automatically
- Prevents returning API keys from previous users with the same ID

### 3. Clear Global State for Users Without API Keys

**File**: `cv-magic-app/backend/app/ai/ai_service.py`

Modified `initialize_for_user()` method to:
- Clear `ai_config._current_provider` and `ai_config._current_model` when a user has no API keys configured
- Clear the global state if the user's saved provider is not available (no API key for that provider)

```python
# Clear global provider/model state if user has no API keys configured
# This prevents new users from seeing another user's provider configuration
if not self._providers:
    logger.info(f"🧹 [AI_SERVICE] User {user_email} has no API keys - clearing global provider/model state")
    self.config._current_provider = None
    self.config._current_model = None
```

### 4. Initialize Service Before Status Check

**File**: `cv-magic-app/backend/app/routes/ai.py`

Modified `/api/ai/status` endpoint to:
- Initialize the AI service for the current user before returning status
- This ensures the provider state is correctly set for the current user

```python
# Initialize AI service for this user to ensure correct provider state
# This prevents new users from seeing another user's provider configuration
ai_service.initialize_for_user(current_user)
```

## How It Works Now

1. **New User Login**: When a new user logs in for the first time:
   - `initialize_for_user()` is called
   - No providers are initialized (user has no API keys)
   - Global `_current_provider` and `_current_model` are cleared to `None`
   - Status endpoints return empty provider list

2. **User with API Keys**: When a user with API keys logs in:
   - `initialize_for_user()` is called
   - Providers are initialized based on user's API keys
   - If user's saved provider is not available, global state is cleared
   - Status endpoints return correct provider information

3. **Status Endpoint**: The `/api/ai/status` endpoint now:
   - Always initializes the service for the current user first
   - Returns status based on the current user's actual API key configuration
   - Never returns stale provider information from other users

## Testing Recommendations

1. **New User Flow**:
   - Create a new user account
   - Log in for the first time
   - Verify that no API keys are shown as configured in the home tab
   - Verify that the API key status endpoint returns `has_api_keys: false`

2. **Existing User Flow**:
   - Log in as an existing user with API keys
   - Verify that their configured API keys are shown correctly
   - Verify that the correct provider/model is selected

3. **Multi-User Scenario**:
   - Log in as User A (with API keys)
   - Log out
   - Log in as User B (new user, no API keys)
   - Verify User B does not see User A's API key configuration

## Files Modified

1. `cv-magic-app/backend/app/routes/auth.py` - Added orphaned API key cleanup during registration
2. `cv-magic-app/backend/app/services/user_api_key_manager.py` - Added validation to prevent returning orphaned API keys
3. `cv-magic-app/backend/app/ai/ai_service.py` - Added logic to clear global state for users without API keys
4. `cv-magic-app/backend/app/routes/ai.py` - Added user initialization before status check

## Notes

- The fix maintains backward compatibility - existing users with API keys will continue to work as before
- The global state clearing only happens when a user has no API keys, preventing any disruption to normal operations
- All provider initialization is still user-specific (using user-specific API keys from the database)
- **Orphaned API keys are automatically cleaned up** when:
  - A new user registers with a reused user ID
  - An API key is retrieved that was created before the user account
- **Future Improvement**: Consider adding a CASCADE DELETE foreign key constraint to automatically delete API keys when users are deleted

