# AI CV Agent - New Architecture

## 🚀 **Next-Generation CV Optimization Platform**

A complete rewrite of the AI CV Agent with modern architecture, dynamic AI model switching, and comprehensive documentation.

## 🏗️ **Project Structure**

```
new-cv/
├── README.md                    # This file
├── REFACTOR_PLAN.md            # Detailed refactoring plan
├── 
├── backend/                    # FastAPI Backend
│   ├── app/                   # Main application
│   ├── data/                  # Data storage
│   ├── tests/                 # Test suite
│   ├── scripts/               # Utility scripts
│   ├── .env.example          # Environment template
│   └── requirements.txt      # Dependencies
├── 
├── frontend/                   # Frontend Application
│   ├── src/                   # Source code
│   └── public/                # Static assets
├── 
├── documentation/              # Complete Documentation
│   ├── api/                   # API documentation
│   ├── ai/                    # AI system docs
│   ├── deployment/            # Deployment guides
│   └── development/           # Dev guides
└── 
└── shared/                     # Shared Resources
    ├── types/                 # Type definitions
    ├── constants/             # Constants
    └── utils/                 # Utilities
```

## ✨ **Key Features**

### 🤖 **Dynamic AI System**
- **Multiple Providers**: OpenAI, Claude, DeepSeek
- **Runtime Switching**: Change models without restarting
- **Unified Interface**: Same API for all providers
- **Cost Tracking**: Automatic token and cost calculation
- **Smart Fallbacks**: Automatic provider selection

### 🏗️ **Modern Architecture**
- **Clean Code**: Well-organized, maintainable structure
- **Separation of Concerns**: Clear module boundaries
- **Scalable Design**: Easy to extend and modify
- **Comprehensive Testing**: Full test coverage
- **Professional Documentation**: Complete guides and examples

### 🔧 **Developer Experience**
- **Easy Setup**: Simple installation and configuration
- **Hot Reload**: Instant feedback during development  
- **Type Safety**: Full type hints and validation
- **Error Handling**: Robust error management
- **Logging**: Comprehensive logging system

## 🚀 **Quick Start**

### 1. **Setup Backend**
```bash
cd backend
cp .env.example .env
# Edit .env with your API keys
pip install -r requirements.txt
./start_server.sh
```

### 2. **Setup Frontend** 
```bash
cd frontend
# Frontend setup instructions coming soon
```

### 3. **Documentation**
```bash
cd documentation
# Read the comprehensive guides
```

## 📚 **Documentation**

- **[API Documentation](./documentation/api/README.md)** - Complete API reference
- **[AI System Guide](./documentation/ai/README.md)** - AI service documentation  
- **[Development Guide](./documentation/development/README.md)** - Setup and development
- **[Deployment Guide](./documentation/deployment/README.md)** - Production deployment

## 🎯 **Core Advantages**

| Feature | Old System | New System |
|---------|------------|------------|
| **AI Models** | Single provider | Multiple providers with switching |
| **Architecture** | Monolithic | Modular, service-based |
| **Configuration** | Hardcoded | Environment-based, dynamic |
| **Documentation** | Scattered | Centralized, comprehensive |
| **Testing** | Limited | Full test coverage |
| **Maintenance** | Difficult | Easy, well-organized |

## 🛠️ **Technologies**

### **Backend**
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - Database ORM
- **Pydantic** - Data validation
- **SQLite** - Database
- **OpenAI/Anthropic/DeepSeek** - AI providers

### **Frontend**
- **React/Flutter** - TBD based on requirements
- **TypeScript** - Type-safe JavaScript
- **Modern UI Library** - TBD

### **DevOps**
- **Docker** - Containerization
- **pytest** - Testing framework
- **GitHub Actions** - CI/CD (planned)

## 🔄 **Migration from Old System**

1. **Backup Data**: Export existing data
2. **Setup New System**: Follow quick start guide
3. **Import Data**: Use migration scripts
4. **Test Functionality**: Verify all features work
5. **Go Live**: Switch to new system

## 🤝 **Contributing**

1. Read [Development Guide](./documentation/development/setup.md)
2. Follow the architecture patterns
3. Add tests for new features
4. Update documentation
5. Submit pull request

## 📈 **Roadmap**

- ✅ **Phase 1**: Core architecture and AI system
- 🔄 **Phase 2**: Complete API implementation  
- ⏳ **Phase 3**: Frontend development
- ⏳ **Phase 4**: Advanced features
- ⏳ **Phase 5**: Production deployment

## 🆘 **Support**

- **Documentation**: Check the `documentation/` folder
- **Issues**: Create GitHub issues for bugs
- **Features**: Submit feature requests
- **Questions**: Check existing documentation first

---

**Built with ❤️ for better CV optimization**
