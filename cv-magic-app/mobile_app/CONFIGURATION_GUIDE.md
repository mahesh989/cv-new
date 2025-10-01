# Environment Configuration Guide

## 🎯 Overview

Your Flutter app now uses environment-based configuration that automatically switches between development and production URLs.

## 🔧 How It Works

### **Environment Detection**
- **Development Mode** (`kDebugMode = true`): Uses `http://localhost:8000`
- **Production Mode** (`kDebugMode = false`): Uses your production URL

### **Configuration Files**

#### **1. Environment Config** (`lib/core/config/environment_config.dart`)
```dart
class EnvironmentConfig {
  static const String _developmentBaseUrl = 'http://localhost:8000';
  static const String _productionBaseUrl = 'https://your-production-url.com';
  
  static String get baseUrl {
    if (kDebugMode) {
      return _developmentBaseUrl;  // Development
    } else {
      return _productionBaseUrl;   // Production
    }
  }
}
```

#### **2. App Config** (`lib/core/config/app_config.dart`)
```dart
class AppConfig {
  static String get baseUrl => kDebugMode 
      ? 'http://localhost:8000'  // Development
      : 'https://your-production-url.com';  // Production
}
```

## 🚀 Usage

### **Development (Flutter Web)**
```bash
# This will automatically use localhost:8000
flutter run -d chrome
```

### **Production Build**
```bash
# This will automatically use your production URL
flutter build web --release
```

## 📝 Updated Files

All these files now use environment-based configuration:

✅ **Services:**
- `lib/services/api_service.dart`
- `lib/services/jd_analysis_service.dart`
- `lib/services/saved_jobs_service.dart`
- `lib/services/ai_model_service.dart`
- `lib/services/api_key_service.dart`

✅ **Screens:**
- `lib/screens/auth_screen.dart`
- `lib/screens/cv_magic_page.dart`
- `lib/screens/cv_generation_screen.dart`

✅ **Modules:**
- `lib/modules/cv/cv_preview_module.dart`

✅ **Widgets:**
- `lib/widgets/backend_error_popup.dart`

## 🔄 Migration Benefits

### **Before (Hardcoded)**
```dart
static const String baseUrl = 'http://localhost:8000';
```

### **After (Environment-Based)**
```dart
static String get baseUrl => EnvironmentConfig.baseUrl;
```

## 🎯 Next Steps

### **1. Update Production URL**
Edit `lib/core/config/environment_config.dart`:
```dart
static const String _productionBaseUrl = 'https://your-actual-production-url.com';
```

### **2. Test Both Environments**
```bash
# Test development
flutter run -d chrome

# Test production build
flutter build web --release
flutter run -d chrome --release
```

### **3. Deploy**
Your app will automatically use the correct URL based on the build mode!

## 🛠️ Customization

### **Add More Environment Variables**
```dart
class EnvironmentConfig {
  // URLs
  static String get baseUrl => kDebugMode ? _devUrl : _prodUrl;
  
  // API Keys
  static String get apiKey => kDebugMode ? _devKey : _prodKey;
  
  // Timeouts
  static Duration get timeout => kDebugMode 
      ? Duration(seconds: 30)  // Dev: longer timeout
      : Duration(seconds: 10); // Prod: shorter timeout
  
  // Logging
  static String get logLevel => kDebugMode ? 'DEBUG' : 'INFO';
}
```

## ✅ Verification

To verify everything is working:

1. **Check Development Mode:**
   ```dart
   print('Base URL: ${EnvironmentConfig.baseUrl}');
   // Should print: http://localhost:8000
   ```

2. **Check Production Mode:**
   ```dart
   print('Base URL: ${EnvironmentConfig.baseUrl}');
   // Should print: https://your-production-url.com
   ```

## 🎉 Result

Now you can:
- ✅ Use `flutter run -d chrome` for development
- ✅ Deploy to production without code changes
- ✅ Switch environments automatically
- ✅ Maintain clean, maintainable code
