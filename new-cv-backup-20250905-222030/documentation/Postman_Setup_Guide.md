# CV Management API - Postman Setup Guide

This guide will help you set up and use Postman to test the CV Management API from the beginning.

## 📋 Prerequisites

1. **Postman**: Download and install [Postman](https://www.postman.com/downloads/)
2. **Server Running**: Ensure your CV Management API server is running on `http://localhost:8000`

## 🚀 Quick Start

### Step 1: Import the Collection

1. Open Postman
2. Click **"Import"** button (top left)
3. Choose **"Upload Files"** 
4. Select the file: `CV_Management_API_Postman_Collection.json`
5. Click **"Import"**

### Step 2: Verify Collection Import

You should see a new collection called **"CV Management API"** with three main folders:
- 🔍 **Health & Info** - Basic API information and health checks
- 🔐 **Authentication** - User login, profile management
- 🤖 **AI Services** - AI-powered CV analysis and job matching

## 📊 Collection Structure

### Variables
The collection includes these pre-configured variables:
- `base_url`: `http://localhost:8000` (API base URL)
- `access_token`: (auto-populated after login)
- `refresh_token`: (auto-populated after login)

## 🧪 Testing Workflow

### Phase 1: Health Checks (No Authentication Required)

Start by testing these endpoints to verify the API is working:

1. **Root - API Status**
   - **Method**: GET
   - **URL**: `{{base_url}}/`
   - **Expected**: Basic API information

2. **Health Check**
   - **Method**: GET
   - **URL**: `{{base_url}}/health`
   - **Expected**: `{"status": "healthy"}`

3. **Database Health Check**
   - **Method**: GET
   - **URL**: `{{base_url}}/health/database`
   - **Expected**: Database connection status

4. **API Info**
   - **Method**: GET
   - **URL**: `{{base_url}}/api/info`
   - **Expected**: Detailed API information and available endpoints

### Phase 2: Authentication Flow

#### 2.1 Login (Development Mode)

The API currently allows empty credentials for development:

1. **Open**: Authentication → Login
2. **Body** (JSON):
   ```json
   {
       "email": "",
       "password": ""
   }
   ```
3. **Send** the request
4. **Expected Response**:
   ```json
   {
       "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
       "refresh_token": "refresh_token_here",
       "token_type": "bearer",
       "expires_in": 3600,
       "user": {
           "id": "user_id",
           "email": "user@example.com",
           "name": "User Name",
           "created_at": "2025-01-01T00:00:00",
           "is_active": true
       }
   }
   ```

**Important**: The collection includes a **Post-response Script** that automatically saves the `access_token` and `refresh_token` to collection variables.

#### 2.2 Test Authenticated Endpoints

After successful login, test these endpoints:

1. **Get Profile**
   - Requires: Bearer token (auto-included)
   - Returns: Current user information

2. **Update Profile**
   - Method: PUT
   - Body: User profile updates
   - Requires: Authentication

### Phase 3: AI Services

#### 3.1 AI Health and Status

1. **AI Health Check** (No auth required)
   - Check AI service availability

2. **Get AI Status** (Requires auth)
   - Current AI configuration
   - Available providers

3. **Get Available Providers** (Requires auth)
   - List of AI providers (OpenAI, Anthropic, DeepSeek)

#### 3.2 AI Configuration

1. **Switch AI Provider**:
   ```json
   {
       "provider": "openai",
       "model": "gpt-3.5-turbo"
   }
   ```

2. **Switch AI Model**:
   ```json
   {
       "model": "gpt-4"
   }
   ```

#### 3.3 AI Operations

1. **Chat Completion**:
   ```json
   {
       "prompt": "Hello, how can you help me with my CV?",
       "system_prompt": "You are a helpful CV and career advisor.",
       "temperature": 0.7,
       "max_tokens": 150
   }
   ```

2. **Analyze CV**:
   ```json
   {
       "cv_text": "John Doe\nSoftware Engineer\n\nExperience:\n- 5 years in Python development\n- Flask and Django frameworks\n- Database design and optimization\n\nSkills:\n- Python, JavaScript, SQL\n- Git, Docker, AWS\n- Agile methodologies"
   }
   ```

3. **Compare CV with Job**:
   ```json
   {
       "cv_text": "Your CV content here...",
       "job_description": "Job requirements here..."
   }
   ```

## 🔧 Configuration Tips

### Authentication Setup

1. **Automatic Token Management**: The Login request includes a script that automatically saves tokens
2. **Collection Authorization**: The collection is configured with Bearer token authentication
3. **Individual Request Auth**: Each protected endpoint inherits collection auth but can be overridden

### Environment Variables

You can create environments for different setups:

1. **Development Environment**:
   - `base_url`: `http://localhost:8000`

2. **Production Environment**:
   - `base_url`: `https://your-production-api.com`

### Custom Headers

All requests include appropriate `Content-Type` headers where needed:
- `application/json` for POST/PUT requests with JSON bodies

## 🔍 Troubleshooting

### Common Issues

1. **Server Not Running**
   - Error: Connection refused
   - Solution: Start your server with `./start_server_quiet.sh`

2. **Authentication Failed**
   - Error: 401 Unauthorized
   - Solution: Run the Login request to get fresh tokens

3. **Invalid Token**
   - Error: Token expired or invalid
   - Solution: Use the Refresh Token endpoint or login again

4. **AI Service Unavailable**
   - Error: AI provider not available
   - Solution: Check AI Health endpoint and verify API keys

### Debug Steps

1. **Check Server Status**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Verify Database**:
   ```bash
   curl http://localhost:8000/health/database
   ```

3. **Check AI Services**:
   ```bash
   curl http://localhost:8000/api/ai/health
   ```

## 📈 Advanced Usage

### Scripting and Automation

1. **Pre-request Scripts**: Add custom headers or modify request data
2. **Post-response Scripts**: Extract and save response data
3. **Collection Runner**: Run the entire collection for automated testing

### Testing Scripts

Add test scripts to verify responses:

```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has required fields", function () {
    const response = pm.response.json();
    pm.expect(response).to.have.property('status');
});
```

## 📝 Example Test Sequence

Here's a recommended sequence for testing:

1. **Health Checks** (Verify server is running)
2. **Login** (Get authentication tokens)
3. **Get Profile** (Test authentication)
4. **AI Health Check** (Verify AI services)
5. **Get AI Status** (Check current configuration)
6. **Chat Completion** (Test basic AI functionality)
7. **Analyze CV** (Test CV analysis feature)
8. **Compare CV with Job** (Test job matching feature)

## 🆘 Support

If you encounter issues:

1. Check the server logs for error details
2. Verify all environment variables are set correctly
3. Ensure the database connection is working
4. Check AI service API keys are valid

## 🔗 API Documentation

- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (Alternative documentation)

---

**Happy Testing! 🚀**
