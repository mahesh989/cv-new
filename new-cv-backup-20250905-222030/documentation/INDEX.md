# CV Management System Documentation

Welcome to the CV Management System documentation. This folder contains all the documentation and configuration files for the project.

## 📁 Documentation Files

### API Documentation
- **`API_ENDPOINTS.md`** - Complete API endpoints documentation with detailed examples
- **`API_ENDPOINTS_QUICK_REFERENCE.txt`** - Quick reference table for testing endpoints

### Setup & Configuration
- **`requirements.txt`** - Python dependencies for the backend
- **`.env.example`** - Environment variables template
- **`README.md`** - Backend setup and usage guide

## 🚀 Quick Start Guide

### 1. Backend Setup
```bash
cd new-cv/back
cp ../documentation/.env.example .env
# Edit .env with your database credentials
pip install -r requirements.txt
./start_server.sh
```

### 2. API Testing
- **Health Check**: `http://localhost:8000/health`
- **API Docs**: `http://localhost:8000/docs`
- **Quick Reference**: See `API_ENDPOINTS_QUICK_REFERENCE.txt`

## 📋 Project Structure

```
new-cv/
├── documentation/          # 📚 This folder - All documentation
│   ├── API_ENDPOINTS.md
│   ├── API_ENDPOINTS_QUICK_REFERENCE.txt
│   ├── requirements.txt
│   ├── .env.example
│   ├── README.md
│   └── INDEX.md
├── back/                   # 🔧 Backend API
│   ├── app/
│   ├── start_server.sh
│   └── requirements.txt
└── front/                  # 🖼️ Frontend (to be developed)
```

## 🔗 Key Resources

| Resource | Location | Description |
|----------|----------|-------------|
| Backend Code | `../back/` | FastAPI backend application |
| API Testing | `API_ENDPOINTS_QUICK_REFERENCE.txt` | Quick testing guide |
| Dependencies | `requirements.txt` | Python packages needed |
| Configuration | `.env.example` | Environment setup template |
| Complete API Docs | `API_ENDPOINTS.md` | Detailed API documentation |

## 🎯 Next Steps

1. **Set up Backend**: Follow the backend README
2. **Test APIs**: Use the quick reference guide
3. **Develop Frontend**: Create React/Vue frontend in `../front/`
4. **Deploy**: Set up production deployment

## 📞 Support

For questions or issues:
1. Check the API documentation
2. Review the quick reference guide
3. Test endpoints using Swagger UI at `/docs`

---
*Last Updated: 2025-01-04*
