#!/bin/bash

echo "🚀 Testing Mobile Formatting on Android Device..."
echo ""

# Check if device is connected
if flutter devices | grep -q "ZT322MHK2C"; then
    echo "✅ Moto G84 5G detected"
    echo ""
    
    echo "🔧 Building for Android with optimizations..."
    flutter run -d ZT322MHK2C --android-skip-build-dependency-validation --hot
else
    echo "❌ Android device not detected. Please ensure:"
    echo "   1. USB debugging is enabled"
    echo "   2. Device is connected via USB"
    echo "   3. Run 'flutter devices' to check"
    echo ""
    
    echo "💡 Alternative: Test in Chrome mobile view"
    echo "   1. Run: flutter run -d chrome"
    echo "   2. Press F12 in Chrome"
    echo "   3. Click mobile device icon"
    echo "   4. Select a mobile device model"
fi 