#!/bin/bash

# Test Runner Script for Environment Configuration
# This script runs all tests to verify the environment configuration

echo "🧪 Running Environment Configuration Tests..."
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Test 1: Run Dart configuration test
echo -e "\n${BLUE}Test 1: Dart Configuration Test${NC}"
dart test_config.dart
print_status $? "Dart configuration test"

# Test 2: Run Flutter unit tests
echo -e "\n${BLUE}Test 2: Flutter Unit Tests${NC}"
flutter test test/environment_config_test.dart
print_status $? "Flutter unit tests"

# Test 3: Run Flutter widget tests
echo -e "\n${BLUE}Test 3: Flutter Widget Tests${NC}"
flutter test test/widgets/config_test_widget.dart
print_status $? "Flutter widget tests"

# Test 4: Check for compilation errors
echo -e "\n${BLUE}Test 4: Compilation Check${NC}"
flutter analyze lib/core/config/
print_status $? "Compilation check"

# Test 5: Test Flutter web compilation
echo -e "\n${BLUE}Test 5: Flutter Web Compilation Test${NC}"
flutter build web --no-sound-null-safety --dart-define=FLUTTER_WEB_USE_SKIA=true
print_status $? "Flutter web compilation"

# Summary
echo -e "\n${YELLOW}=============================================="
echo -e "Test Summary"
echo -e "==============================================${NC}"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Your environment configuration is working correctly.${NC}"
    echo -e "\n${BLUE}Next steps:${NC}"
    echo -e "1. Start your backend: ${YELLOW}cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload${NC}"
    echo -e "2. Run Flutter web: ${YELLOW}flutter run -d chrome${NC}"
    echo -e "3. Your app will automatically use localhost:8000 in development mode"
else
    echo -e "${RED}❌ Some tests failed. Please check the output above.${NC}"
    exit 1
fi
