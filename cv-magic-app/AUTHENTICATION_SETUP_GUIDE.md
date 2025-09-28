# 🔐 CV Agent Authentication Setup Guide

## 📋 Complete User Authentication Workflow

### 🎯 Development Mode Configuration (Current)

**Backend Configuration:**
```python
# cv-magic-app/backend/app/config.py
EMAIL_ENABLED: bool = False          # No real emails sent
DEVELOPMENT_MODE: bool = True        # Auto-verify users
EMAIL_MOCK_SUCCESS: bool = True      # Always succeeds
```

**Benefits:**
- ✅ **NO email verification required**
- ✅ **NO SMTP setup needed** 
- ✅ **Instant account activation**
- ✅ **Perfect for development/testing**

---

## 🚀 How Users Sign Up & Sign In

### 📝 STEP 1: Sign Up Process

1. **Open CV Agent app**
2. **Click "Sign Up" tab**
3. **Fill out form with valid data:**
   - **Full Name:** "John Doe" *(optional)*
   - **Username:** "johndoe123" *(3+ chars, alphanumeric + underscore)*
   - **Email:** "john.doe@example.com" *(valid format)*
   - **Password:** "password123" *(8+ chars, letters + numbers)*
4. **Click "Create Account"**
5. **✅ Account created and AUTO-VERIFIED**
6. **✅ Success message appears**
7. **✅ Form automatically switches to "Sign In" tab**

### 🔑 STEP 2: Sign In Process

1. **Enter same credentials:**
   - **Email:** "john.doe@example.com"
   - **Password:** "password123"
2. **Click "Sign In"**
3. **✅ Login successful immediately**
4. **✅ Full access to CV Agent features**

**Total Time:** ~30 seconds for complete signup + login

---

## 🧪 Validation Rules

### 📧 Email Validation
- **Required:** Must be provided
- **Format:** Valid email format (user@domain.com)
- **Length:** Must be less than 100 characters
- **Example:** `john.doe@example.com` ✅

### 👤 Username Validation
- **Required:** Must be provided
- **Length:** 3-50 characters
- **Characters:** Letters, numbers, underscore only (no spaces)
- **Unique:** Must not already exist
- **Example:** `johndoe123` ✅, `john doe` ❌

### 🔐 Password Validation
- **Required:** Must be provided
- **Length:** 8-128 characters
- **Complexity:** Must contain at least one letter AND one number
- **Example:** `password123` ✅, `password` ❌, `12345678` ❌

### 📝 Full Name Validation
- **Optional:** Can be left empty
- **Length:** If provided, 2-100 characters
- **Example:** `John Doe` ✅

---

## 🔧 Troubleshooting Network Issues

### 🌐 Platform-Specific Backend URLs

**Current Configuration:**
- **Default:** `http://localhost:8000`

**Alternative Configurations for Different Environments:**

```dart
// For Android Emulator:
static String get baseUrl => 'http://10.0.2.2:8000';

// For iOS Simulator:  
static String get baseUrl => 'http://localhost:8000'; // or 'http://127.0.0.1:8000'

// For Physical Devices:
static String get baseUrl => 'http://YOUR_COMPUTER_IP:8000'; // e.g., 'http://192.168.1.100:8000'

// For Web:
static String get baseUrl => 'http://localhost:8000';
```

### 🔍 Finding Your Computer's IP Address

**Mac/Linux:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Windows:**
```cmd
ipconfig | findstr "IPv4"
```

**Example Result:** `192.168.1.100` → Use `http://192.168.1.100:8000`

---

## 🛠️ Testing Backend Connectivity

### 📡 Built-in Connectivity Test
- **In Flutter app:** Click "Test Backend Connection" button
- **Shows:** Backend status, API endpoints, error details
- **Helps:** Diagnose network issues

### 🧪 Manual Backend Test
```bash
# Test if backend is running
curl http://localhost:8000

# Test auth endpoints
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"password123"}'
```

---

## ❌ Common Issues & Solutions

### 🔌 "Connection Refused" Error
**Cause:** Backend server not running
**Solution:** 
```bash
cd cv-magic-app/backend
python -m app.main
```

### ⏰ "Connection Timeout" Error  
**Cause:** Network connectivity issues
**Solutions:**
1. Check internet connection
2. Ensure backend is running on correct port
3. For mobile devices, use computer's IP instead of localhost

### 📱 Mobile Device Issues
**Cause:** `localhost` doesn't work on physical devices
**Solution:** Update `app_config.dart`:
```dart
static String get baseUrl => 'http://YOUR_COMPUTER_IP:8000';
```

### 🔄 "Auto-verification Not Working"
**Cause:** Wrong configuration
**Solution:** Ensure in `config.py`:
```python
EMAIL_ENABLED = False
DEVELOPMENT_MODE = True
```

---

## 🎉 Success Indicators

### ✅ Working Signup Flow
1. Form validation passes
2. Network request succeeds (Status 200)
3. Success message appears
4. Tab switches to "Sign In"
5. User data is saved

### ✅ Working Login Flow  
1. Form validation passes
2. Network request succeeds (Status 200)
3. JWT tokens received
4. User preferences saved
5. App navigates to main screen

---

## 📞 Support & Debugging

### 🔍 Debug Information Available
- **Console Logs:** Check Flutter console for detailed request/response info
- **Network Test:** Use built-in connectivity test button
- **Backend Logs:** Check FastAPI server logs for incoming requests

### 📧 Contact Information
- **Backend Status:** All endpoints tested and working ✅
- **Authentication System:** Fully functional ✅  
- **Development Mode:** Enabled and tested ✅

**The authentication system is working perfectly in development mode!** 🎯✨
