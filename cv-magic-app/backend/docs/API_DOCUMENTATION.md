# CV Management API Documentation

## Overview

The CV Management API is a comprehensive, production-ready system for managing CVs, user authentication, file storage, and advanced features. This API supports multiple user types, advanced security, monitoring, and optimization features.

## Table of Contents

1. [Authentication](#authentication)
2. [User Management](#user-management)
3. [File Management](#file-management)
4. [Advanced Features](#advanced-features)
5. [Security](#security)
6. [Monitoring](#monitoring)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)

## Authentication

### User Registration
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "full_name": "string",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### User Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "is_admin": false,
    "is_verified": true
  }
}
```

### Admin Login
```http
POST /api/auth/admin/login
Content-Type: application/json

{
  "email": "string",
  "password": "string"
}
```

### Email Verification
```http
GET /api/auth/verification-status
Authorization: Bearer <token>
```

```http
POST /api/auth/send-verification
Authorization: Bearer <token>
```

```http
POST /api/auth/verify-email
Content-Type: application/json

{
  "token": "string"
}
```

### Password Reset
```http
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "string"
}
```

```http
POST /api/auth/reset-password
Content-Type: application/json

{
  "token": "string",
  "new_password": "string"
}
```

## User Management

### Get User Profile
```http
GET /api/auth/me
Authorization: Bearer <token>
```

### Update User Profile
```http
PUT /api/auth/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "string",
  "email": "string"
}
```

### User Settings
```http
GET /api/user/settings
Authorization: Bearer <token>
```

```http
PUT /api/user/settings
Authorization: Bearer <token>
Content-Type: application/json

{
  "preferred_ai_model": "string",
  "analysis_preferences": {},
  "notification_settings": {},
  "ui_preferences": {}
}
```

### API Key Management
```http
GET /api/user/api-keys
Authorization: Bearer <token>
```

```http
POST /api/user/api-keys
Authorization: Bearer <token>
Content-Type: application/json

{
  "provider": "string",
  "api_key": "string"
}
```

## File Management

### Upload CV
```http
POST /api/user/cv/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <file>
title: "string"
description: "string"
```

### List CVs
```http
GET /api/user/cv/list
Authorization: Bearer <token>
```

### Get CV Details
```http
GET /api/user/cv/{cv_id}
Authorization: Bearer <token>
```

### Download CV
```http
GET /api/user/cv/{cv_id}/download
Authorization: Bearer <token>
```

### Delete CV
```http
DELETE /api/user/cv/{cv_id}
Authorization: Bearer <token>
```

### CV Statistics
```http
GET /api/user/cv/stats
Authorization: Bearer <token>
```

### Save Tailored CV
```http
POST /api/user/cv/{cv_id}/tailored
Authorization: Bearer <token>
Content-Type: multipart/form-data

tailored_content: "string"
filename: "string"
```

## Advanced Features

### Bulk Operations

#### Bulk Upload
```http
POST /api/advanced/bulk-upload
Authorization: Bearer <token>
Content-Type: application/json

{
  "files": [
    {
      "filename": "string",
      "size": 1024,
      "type": "pdf"
    }
  ]
}
```

#### Bulk Delete
```http
POST /api/advanced/bulk-delete
Authorization: Bearer <token>
Content-Type: application/json

{
  "file_ids": ["string"]
}
```

#### Bulk Export
```http
POST /api/advanced/bulk-export
Authorization: Bearer <token>
Content-Type: application/json

{
  "data_types": ["profile", "files", "activity", "settings"]
}
```

### Search Functionality
```http
POST /api/advanced/search
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "string",
  "file_types": ["pdf", "docx"],
  "date_range": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }
}
```

### User Statistics
```http
GET /api/advanced/statistics
Authorization: Bearer <token>
```

### Batch Processing
```http
POST /api/advanced/batch-process
Authorization: Bearer <token>
Content-Type: application/json

{
  "file_ids": ["string"],
  "operation": "string",
  "parameters": {}
}
```

## Optimized API

### Optimized User Files
```http
GET /api/optimized/user/files?page=1&page_size=20&file_type=pdf
Authorization: Bearer <token>
```

### Optimized User Analytics
```http
GET /api/optimized/user/analytics
Authorization: Bearer <token>
```

### Global Search
```http
GET /api/optimized/search/global?query=string&page=1&page_size=20
Authorization: Bearer <token>
```

### Performance Health
```http
GET /api/optimized/performance/health
Authorization: Bearer <token>
```

## Security

### Security Statistics
```http
GET /api/security/security-stats
Authorization: Bearer <admin_token>
```

### Audit Logs
```http
GET /api/security/audit-logs?user_id=1&activity_type=authentication&limit=100&offset=0
Authorization: Bearer <admin_token>
```

### Security Events
```http
GET /api/security/security-events?severity=high&limit=100
Authorization: Bearer <admin_token>
```

### User Sessions
```http
GET /api/security/user-sessions/{user_id}
Authorization: Bearer <admin_token>
```

### Invalidate User Sessions
```http
POST /api/security/invalidate-user-sessions/{user_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "reason": "string"
}
```

### Audit Report
```http
GET /api/security/audit-report?days=30
Authorization: Bearer <admin_token>
```

## Monitoring

### Health Check
```http
GET /monitoring/health
```

### Detailed Health Check
```http
GET /api/monitoring/health/detailed
Authorization: Bearer <admin_token>
```

### Metrics
```http
GET /api/monitoring/metrics
Authorization: Bearer <admin_token>
```

### Metrics History
```http
GET /api/monitoring/metrics/history?hours=24
Authorization: Bearer <admin_token>
```

### Application Status
```http
GET /api/monitoring/status
```

### Alerts
```http
GET /api/monitoring/alerts
Authorization: Bearer <admin_token>
```

### Manual Metrics Collection
```http
POST /api/monitoring/metrics/collect
Authorization: Bearer <admin_token>
```

## Cache Management

### Cache Statistics
```http
GET /api/advanced/cache/stats
Authorization: Bearer <admin_token>
```

### Clear Cache
```http
POST /api/advanced/cache/clear?pattern=*
Authorization: Bearer <admin_token>
```

### Cache Warming
```http
POST /api/optimized/cache/warm
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "cache_keys": ["string"]
}
```

## Performance Monitoring

### Performance Metrics
```http
GET /api/advanced/performance/metrics
Authorization: Bearer <admin_token>
```

### Optimization Recommendations
```http
GET /api/advanced/performance/recommendations
Authorization: Bearer <admin_token>
```

### Clear Performance Metrics
```http
POST /api/advanced/performance/clear-metrics
Authorization: Bearer <admin_token>
```

### Optimization Status
```http
GET /api/optimized/optimization/status
Authorization: Bearer <admin_token>
```

## Error Handling

### Standard Error Response
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common Error Codes
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Validation Error
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

## Rate Limiting

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Rate Limits by Endpoint
- Login: 5 requests/minute
- Registration: 3 requests/minute
- Password Reset: 3 requests/5 minutes
- File Upload: 10 requests/minute
- Analysis: 20 requests/minute
- Admin: 50 requests/minute

## Authentication

### Bearer Token
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### Token Expiration
- Access Token: 1 hour (production), 8 hours (development)
- Refresh Token: 7 days

## Response Formats

### Success Response
```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "data": {}
}
```

### Paginated Response
```json
{
  "status": "success",
  "data": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

### Cached Response
```json
{
  "status": "success",
  "source": "cache",
  "data": {}
}
```

## Webhooks

### Security Events
```http
POST /webhooks/security-events
Content-Type: application/json

{
  "event_type": "string",
  "severity": "string",
  "user_id": 1,
  "ip_address": "string",
  "timestamp": "2024-01-01T00:00:00Z",
  "details": {}
}
```

## SDK Examples

### Python
```python
import requests

# Authentication
response = requests.post("http://localhost:8000/api/auth/login", json={
    "email": "user@example.com",
    "password": "password123"
})
token = response.json()["access_token"]

# Make authenticated requests
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/api/user/cv/list", headers=headers)
```

### JavaScript
```javascript
// Authentication
const response = await fetch("http://localhost:8000/api/auth/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
        email: "user@example.com",
        password: "password123"
    })
});
const {access_token} = await response.json();

// Make authenticated requests
const cvResponse = await fetch("http://localhost:8000/api/user/cv/list", {
    headers: {"Authorization": `Bearer ${access_token}`}
});
```

## Production Deployment

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://host:6379/0

# Security
JWT_SECRET_KEY=your-secret-key
RATE_LIMIT_ENABLED=true

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Monitoring
MONITORING_ENABLED=true
LOG_LEVEL=INFO
```

### Docker Deployment
```bash
# Build and run
docker-compose -f docker-compose.prod.yml up -d

# Health check
curl http://localhost:8000/monitoring/health
```

### Health Checks
- Basic: `GET /monitoring/health`
- Detailed: `GET /api/monitoring/health/detailed` (admin)

## Support

For support and questions:
- Email: support@cvapp.com
- Documentation: https://docs.cvapp.com
- API Status: https://status.cvapp.com
