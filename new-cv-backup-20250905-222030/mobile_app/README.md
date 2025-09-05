# CV Agent Mobile App 🚀

A modern Flutter mobile application for AI-powered resume optimization with beautiful UI and model selection functionality.

## 🌟 Features

### ✨ Authentication System
- **Modern UI Design**: Beautiful gradient-based authentication screens inspired by mt2
- **Tab-based Auth**: Sign In and Sign Up tabs with smooth animations
- **Demo Mode**: Instant login without credentials for easy testing
- **Google Sign-In**: Simulated Google authentication flow
- **Responsive Design**: Adapts to different screen sizes and keyboard states

### 🤖 AI Model Selection
- **Dynamic Model Configuration**: Select from multiple AI models (GPT, Claude, DeepSeek)
- **Persistent Selection**: Your chosen model is saved and persists across app sessions
- **Beautiful UI**: Expandable model selector with rich visual design
- **Model Information**: Detailed info about each model including speed, cost, and capabilities
- **Recommended Models**: Highlighted recommended models for better user guidance

### 🎨 Modern UI/UX
- **Cosmic Theme**: Beautiful gradient-based design system with custom colors
- **Smooth Animations**: Fade and slide animations throughout the app
- **Material Design 3**: Latest Material Design principles
- **Custom Widgets**: Reusable gradient buttons, cards, and components
- **Inter Font**: Professional typography using Google Fonts
- **Loading States**: Beautiful loading animations with SpinKit

### 🏠 Home Screen
- **Tabbed Navigation**: Home, CV Magic, Jobs, and Settings tabs
- **Welcome Experience**: Personalized greeting with user name
- **Quick Actions**: Grid of action buttons for main features
- **Recent Activity**: Track user's recent actions (placeholder for future)
- **Expandable AppBar**: Beautiful gradient header with user menu

## 🏗️ Architecture

### 📁 Project Structure
```
lib/
├── core/
│   └── theme/
│       └── app_theme.dart          # Comprehensive theme system
├── models/
│   └── ai_model.dart               # AI model data structures
├── services/
│   └── ai_model_service.dart       # AI model state management
├── screens/
│   ├── auth_screen.dart            # Authentication UI
│   └── home_screen.dart            # Main home interface
├── widgets/
│   └── ai_model_selector.dart      # Model selection component
└── main.dart                       # App entry point
```

### 🔧 Dependencies
- **provider**: State management for AI model selection
- **shared_preferences**: Persistent storage for user preferences
- **google_fonts**: Professional typography (Inter font)
- **flutter_spinkit**: Beautiful loading animations
- **animations**: Enhanced animation transitions
- **http & dio**: Network requests (for future API integration)

## 🚀 Getting Started

### Prerequisites
- Flutter SDK (latest stable version)
- Dart SDK
- iOS Simulator / Android Emulator or physical device

### Installation

1. **Navigate to the project directory**:
   ```bash
   cd /Users/mahesh/Documents/Github/mahesh/new-cv/mobile_app
   ```

2. **Install dependencies**:
   ```bash
   flutter pub get
   ```

3. **Run the app**:
   ```bash
   flutter run
   ```

## 🎯 Usage

### Authentication
1. **Demo Mode**: Simply tap "Sign In" without entering credentials
2. **Custom Login**: Enter email/password or leave empty for demo
3. **Google Sign-In**: Use the Google button for simulated OAuth flow

### AI Model Selection
1. **Access**: Navigate to the Home tab after login
2. **Expand**: Tap on the "🤖 AI Model Configuration" card to expand
3. **Select**: Choose from dropdown or tap recommended model cards
4. **Persist**: Your selection automatically saves and persists

### Navigation
- **Home**: AI model selection and quick actions
- **CV Magic**: Future CV generation features
- **Jobs**: Future job browsing functionality  
- **Settings**: Future app configuration

## 🛠️ Technical Features

### State Management
- **Provider Pattern**: Centralized state management for AI model selection
- **Singleton Service**: AIModelService manages model state globally
- **Persistence**: SharedPreferences for storing user selections

### UI/UX Features  
- **Responsive Design**: Adapts to different screen sizes
- **Smooth Animations**: Fade and slide transitions
- **Loading States**: Proper loading indicators
- **Error Handling**: Graceful error states and user feedback

### Code Quality
- **Clean Architecture**: Separation of concerns across layers  
- **Reusable Components**: Custom theme and widget system
- **Type Safety**: Strong typing with custom model classes
- **Documentation**: Comprehensive code comments

## 🎨 Design System

### Colors
- **Primary Teal**: `#14B8A6` - Main brand color
- **Primary Cosmic**: `#6366F1` - Accent color
- **Neutral Grays**: Complete gray scale palette
- **Gradients**: Beautiful cosmic-inspired gradients

### Typography
- **Inter Font**: Professional, readable font family
- **Hierarchical Scale**: Display, Heading, Body, and Label styles
- **Consistent Spacing**: Proper line heights and margins

## 🔮 Future Enhancements

- **CV Upload**: File picker for existing resumes
- **CV Generation**: AI-powered resume creation
- **Job Integration**: Real job browsing and matching
- **ATS Analysis**: Resume compatibility scoring
- **User Profiles**: Complete user management
- **API Integration**: Backend connectivity for real AI processing

## 🤝 Inspired By

This app draws inspiration from the mt1 and mt2 projects, incorporating:
- Authentication flow design from mt2
- AI model configuration approach
- Modern Flutter best practices
- Clean architecture patterns

## 📱 Key Features

The app features:
- Beautiful loading screen with gradient background
- Modern authentication with tab-based design
- Rich home screen with AI model selector
- Smooth animations and transitions
- Professional typography and spacing
- Persistent model selection across sessions

---

**Built with ❤️ using Flutter** • Ready for further development and API integration
