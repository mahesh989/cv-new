# CV Management API

A comprehensive backend API for CV management and job application tracking built with FastAPI.

## Features

- 🔐 **JWT-based Authentication** - Secure user registration, login, and token management
- 📄 **CV Management** - Upload, store, and manage CV files (PDF, DOCX)
- 🎯 **Job Application Tracking** - Track job applications and their status
- 🔍 **CV Analysis** - AI-powered CV analysis and skill extraction
- 📊 **Job Matching** - Compare CV skills with job requirements
- 🏥 **Health Monitoring** - Built-in health checks and monitoring
- 🛡️ **Security** - Password hashing, token blacklisting, input validation

## Technology Stack

- **FastAPI** - Modern, fast web framework for APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Primary database
- **JWT** - Authentication and authorization
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server

## Project Structure

```
new-cv/back/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── auth/                # Authentication utilities
│   │   ├── __init__.py
│   │   └── jwt_handler.py   # JWT token handling
│   ├── config/              # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py      # Application settings
│   ├── database/            # Database setup and utilities
│   │   ├── __init__.py
│   │   └── database.py      # Database connection and setup
│   ├── middleware/          # Custom middleware
│   │   ├── __init__.py
│   │   └── auth.py          # Authentication middleware
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── user.py          # User and session models
│   │   └── cv.py            # CV and job application models
│   ├── routes/              # API routes
│   │   ├── __init__.py
│   │   └── auth.py          # Authentication endpoints
│   └── utils/               # Utility functions
├── tests/                   # Test files
├── uploads/                 # File upload directory
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── API_ENDPOINTS.md        # API documentation
└── README.md               # This file
```

## Setup Instructions

### 1. Clone the Repository
```bash
cd new-cv/back
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env file with your configuration
```

### 5. Set Up Database
Make sure you have PostgreSQL installed and running, then create a database:
```sql
CREATE DATABASE cv_app;
```

Update your `.env` file with the correct database credentials.

### 6. Run the Application
```bash
# Development mode with auto-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or directly with Python
python app/main.py
```

The API will be available at `http://localhost:8000`

### 7. View API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

### Required Variables
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT tokens (use a strong, random key)

### Optional Variables
- `DEBUG` - Enable debug mode (default: False)
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `REDIS_URL` - Redis connection for caching (optional)
- `OPENAI_API_KEY` - OpenAI API key for CV analysis
- `CLAUDE_API_KEY` - Claude API key for CV analysis

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

### Health Checks
- `GET /health` - Basic health check
- `GET /health/database` - Database health check

### System
- `GET /` - API information
- `GET /api/info` - Detailed API information

## Database Models

### User Model
- User authentication and profile information
- Password hashing with bcrypt
- Session management for JWT tokens

### CV Model
- CV file storage and metadata
- Analysis results storage
- File validation and size limits

### Job Application Model
- Job application tracking
- Application status management
- Job matching results

## Security Features

- **Password Hashing** - bcrypt for secure password storage
- **JWT Authentication** - Stateless authentication with token blacklisting
- **Input Validation** - Pydantic models for request validation
- **CORS Protection** - Configurable CORS settings
- **Rate Limiting** - API rate limiting (planned)
- **File Validation** - MIME type and size validation for uploads

## Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Format code
black app/

# Sort imports
isort app/

# Lint code
flake8 app/
```

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "Migration description"

# Apply migration
alembic upgrade head
```

## Production Deployment

### Using Docker (Recommended)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Configuration
- Set `DEBUG=False` for production
- Use a strong, unique `JWT_SECRET_KEY`
- Configure production database settings
- Set up proper logging and monitoring

## Future Enhancements

- [ ] CV analysis with AI/ML models
- [ ] Advanced job matching algorithms
- [ ] Email notifications
- [ ] File format conversion
- [ ] Advanced reporting and analytics
- [ ] Role-based access control
- [ ] API rate limiting
- [ ] Comprehensive test coverage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For questions or support, please open an issue on GitHub or contact the development team.
