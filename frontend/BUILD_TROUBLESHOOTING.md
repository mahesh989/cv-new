# 🔧 Build Troubleshooting Guide

## 🚨 Common Android Build Issues

### Issue 1: Import Timeout Errors
**Symptoms:**
```
Error when reading 'lib/screens/my_prompts_page.dart': Operation timed out
```

**Solutions:**
```bash
# Clean and rebuild
flutter clean
flutter pub get
flutter run -d [DEVICE_ID]

# If still failing, skip dependency validation
flutter run -d [DEVICE_ID] --android-skip-build-dependency-validation
```

### Issue 2: Gradle Version Warnings
**Symptoms:**
```
Flutter support for your project's Android Gradle Plugin version (7.3.0) will soon be dropped
```

**Quick Fix:**
```bash
# Skip validation (temporary solution)
flutter run -d [DEVICE_ID] --android-skip-build-dependency-validation
```

**Permanent Fix:**
Update `android/build.gradle`:
```gradle
dependencies {
    classpath 'com.android.tools.build:gradle:7.4.2'
    classpath "org.jetbrains.kotlin:kotlin-gradle-plugin:1.8.10"
}
```

### Issue 3: NDK/CMake Installation
**Symptoms:**
```
NDK at /path/to/ndk did not have a source.properties file
```

**Solution:**
- Let Flutter install required components automatically
- This is normal for first-time builds
- Wait for installation to complete

## 🎯 Quick Commands

### Your Device (Moto G84 5G)
```bash
# Standard build
flutter run -d ZT322MHK2C

# Skip dependency validation
flutter run -d ZT322MHK2C --android-skip-build-dependency-validation

# Profile mode for performance testing
flutter run -d ZT322MHK2C --profile
```

### Development Workflow
```bash
# Clean start
flutter clean && flutter pub get

# Check devices
flutter devices

# Hot reload (press 'r' in terminal)
# Hot restart (press 'R' in terminal)
```

## 🔍 Debug Steps

### Step 1: Check Environment
```bash
flutter doctor -v
```

### Step 2: Verify Device Connection
```bash
flutter devices
adb devices
```

### Step 3: Clean Build
```bash
flutter clean
flutter pub get
```

### Step 4: Build with Verbose Output
```bash
flutter run -d [DEVICE_ID] -v
```

## 📱 Testing Alternatives

### If Android Build Fails
1. **Chrome Mobile Simulation**:
   ```bash
   flutter run -d chrome
   # Open DevTools (F12) → Mobile icon 📱
   ```

2. **iOS Simulator** (if available):
   ```bash
   flutter run -d ios
   ```

### Mobile Testing in Chrome
1. Open DevTools (F12)
2. Click mobile device icon
3. Select device: iPhone 12 Pro, Pixel 5, etc.
4. Test touch interactions
5. Verify responsive design

## ⚡ Performance Tips

### Faster Builds
- Use `flutter run --hot` for development
- Keep device connected and unlocked
- Close unnecessary apps on development machine

### Memory Management
- Close other IDEs/heavy applications
- Ensure sufficient disk space (>5GB)
- Use SSD if possible for faster I/O

## 🎯 Success Indicators

### Build Success
- ✅ "BUILD SUCCESSFUL" message
- ✅ App appears on device
- ✅ Hot reload works (press 'r')

### App Health
- ✅ Smooth animations
- ✅ Responsive navigation
- ✅ No crash on startup
- ✅ All features accessible

## 🆘 Emergency Fixes

### If All Else Fails
```bash
# Nuclear option - complete reset
rm -rf build/
rm -rf .dart_tool/
flutter clean
flutter pub get
flutter run -d [DEVICE_ID] --android-skip-build-dependency-validation
```

### Alternative Testing
- Use web version in Chrome mobile mode
- Test on iOS simulator if available
- Use Android emulator instead of physical device

## 📞 Getting Help

### Flutter Resources
- [Flutter Documentation](https://docs.flutter.dev/)
- [Flutter GitHub Issues](https://github.com/flutter/flutter/issues)
- [Stack Overflow Flutter Tag](https://stackoverflow.com/questions/tagged/flutter)

### Debugging Tools
- Flutter Inspector
- DevTools Performance Tab
- Chrome DevTools for web debugging 