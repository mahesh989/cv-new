# CV Application API Endpoints Documentation

## Overview
This document outlines all the API endpoints for the new CV management application. The API is built with FastAPI and follows RESTful principles.

## Base URL
```
http://localhost:8000
```

## Authentication
The API uses JWT (JSON Web Token) based authentication. Protected endpoints require the `Authorization` header:
```
Authorization: Bearer <jwt_token>
```

---

## 🔐 Authentication Endpoints

### Register User
**POST** `/auth/register`

Register a new user account.

**Request Body:**
```json
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
  "user_id": "string"
}
```

**Status Codes:**
- `201`: User created successfully
- `400`: Validation error or user already exists

---

### Login
**POST** `/auth/login`

Login with credentials to receive JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "string",
    "username": "string",
    "email": "string",
    "full_name": "string"
  }
}
```

**Status Codes:**
- `200`: Login successful
- `401`: Invalid credentials

---

### Refresh Token
**POST** `/auth/refresh`

Refresh the JWT token.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### Logout
**POST** `/auth/logout`

Logout and invalidate token.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

---

## 👤 User Profile Endpoints

### Get User Profile
**GET** `/user/profile`

Get current user's profile information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

### Update User Profile
**PUT** `/user/profile`

Update user profile information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "email": "string",
  "full_name": "string"
}
```

**Response:**
```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": "string",
    "username": "string",
    "email": "string",
    "full_name": "string"
  }
}
```

---

### Change Password
**POST** `/user/change-password`

Change user password.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

---

## 📄 CV Management Endpoints

### Upload CV
**POST** `/cv/upload`

Upload a new CV file.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Request Body:**
```
cv_file: File (PDF, DOCX)
title: string (optional)
description: string (optional)
```

**Response:**
```json
{
  "message": "CV uploaded successfully",
  "cv_id": "string",
  "filename": "string",
  "file_size": 123456,
  "file_type": "application/pdf"
}
```

---

### List User CVs
**GET** `/cv/list`

Get list of user's uploaded CVs.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `page`: int (default: 1)
- `limit`: int (default: 10)

**Response:**
```json
{
  "cvs": [
    {
      "id": "string",
      "filename": "string",
      "title": "string",
      "description": "string",
      "file_size": 123456,
      "file_type": "application/pdf",
      "uploaded_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 10
}
```

---

### Get CV Details
**GET** `/cv/{cv_id}`

Get details of a specific CV.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "id": "string",
  "filename": "string",
  "title": "string",
  "description": "string",
  "file_size": 123456,
  "file_type": "application/pdf",
  "uploaded_at": "2024-01-01T00:00:00Z",
  "download_url": "string"
}
```

---

### Download CV
**GET** `/cv/{cv_id}/download`

Download CV file.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
Binary file download with appropriate headers.

---

### Update CV Info
**PUT** `/cv/{cv_id}`

Update CV information (title, description).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "title": "string",
  "description": "string"
}
```

**Response:**
```json
{
  "message": "CV updated successfully",
  "cv": {
    "id": "string",
    "filename": "string",
    "title": "string",
    "description": "string"
  }
}
```

---

### Delete CV
**DELETE** `/cv/{cv_id}`

Delete a CV file.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "message": "CV deleted successfully"
}
```

---

## 🎯 Job Application Endpoints

### Save Job Application
**POST** `/jobs/applications`

Save a new job application.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "job_title": "string",
  "company": "string",
  "job_url": "string",
  "job_description": "string",
  "cv_id": "string",
  "application_date": "2024-01-01",
  "status": "applied|pending|interview|rejected|accepted",
  "notes": "string"
}
```

**Response:**
```json
{
  "message": "Job application saved successfully",
  "application_id": "string"
}
```

---

### List Job Applications
**GET** `/jobs/applications`

Get list of user's job applications.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `page`: int (default: 1)
- `limit`: int (default: 10)
- `status`: string (filter by status)

**Response:**
```json
{
  "applications": [
    {
      "id": "string",
      "job_title": "string",
      "company": "string",
      "job_url": "string",
      "status": "applied",
      "application_date": "2024-01-01",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "limit": 10
}
```

---

### Get Job Application Details
**GET** `/jobs/applications/{application_id}`

Get details of a specific job application.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "id": "string",
  "job_title": "string",
  "company": "string",
  "job_url": "string",
  "job_description": "string",
  "cv_id": "string",
  "application_date": "2024-01-01",
  "status": "applied",
  "notes": "string",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

### Update Job Application
**PUT** `/jobs/applications/{application_id}`

Update job application information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "status": "interview",
  "notes": "Got a call for interview"
}
```

**Response:**
```json
{
  "message": "Job application updated successfully"
}
```

---

### Delete Job Application
**DELETE** `/jobs/applications/{application_id}`

Delete a job application.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "message": "Job application deleted successfully"
}
```

---

## 🔍 Analysis Endpoints

### Analyze CV
**POST** `/analysis/cv-analysis`

Analyze CV content and extract skills.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "cv_id": "string"
}
```

**Response:**
```json
{
  "cv_id": "string",
  "analysis": {
    "technical_skills": ["Python", "JavaScript", "React"],
    "soft_skills": ["Communication", "Leadership"],
    "domain_keywords": ["Software Development", "API Design"],
    "experience_years": 5,
    "education": "Bachelor's in Computer Science"
  },
  "analyzed_at": "2024-01-01T00:00:00Z"
}
```

---

### Compare CV with Job
**POST** `/analysis/compare`

Compare CV skills with job requirements.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "cv_id": "string",
  "job_description": "string"
}
```

**Response:**
```json
{
  "cv_id": "string",
  "match_score": 85,
  "matched_skills": ["Python", "JavaScript"],
  "missing_skills": ["Docker", "Kubernetes"],
  "recommendations": [
    "Consider adding Docker experience to your CV",
    "Highlight your JavaScript framework experience"
  ],
  "compared_at": "2024-01-01T00:00:00Z"
}
```

---

## 🏥 Health Check Endpoints

### Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

---

### Database Health
**GET** `/health/database`

Check database connectivity.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Validation error message",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

API endpoints are rate-limited:
- Authentication endpoints: 5 requests per minute
- Upload endpoints: 10 requests per hour
- General endpoints: 100 requests per minute

## CORS Policy

The API allows cross-origin requests from:
- `http://localhost:3000` (development frontend)
- Production frontend domain (to be configured)

## File Upload Limits

- Maximum file size: 10MB
- Supported formats: PDF, DOCX
- Maximum files per user: 50

## Security Features

- JWT token expiration: 1 hour
- Password hashing: bcrypt
- SQL injection prevention: SQLAlchemy ORM
- Input validation: Pydantic models
- File type validation: MIME type checking
