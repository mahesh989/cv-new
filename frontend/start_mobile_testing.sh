#!/bin/bash

echo "🚀 CV Agent Mobile Testing Setup"
echo "================================"

# Function to show available options
show_options() {
    echo ""
    echo "Choose your testing environment:"
    echo "1. Chrome (Mobile Simulation) - Best for development"
    echo "2. iOS Simulator - Test on iOS"
    echo "3. Android Emulator - Test on Android"
    echo "4. Show all devices"
    echo "5. Exit"
    echo ""
}

# Function to start Chrome mobile simulation
start_chrome_mobile() {
    echo "🌐 Starting Chrome with mobile simulation..."
    echo "💡 Pro tip: Open Chrome DevTools (F12) and click the mobile device icon"
    echo "   to simulate different mobile devices"
    echo ""
    flutter run -d chrome
}

# Function to start iOS simulator
start_ios() {
    echo "📱 Starting iOS Simulator..."
    echo "Launching iOS simulator first..."
    flutter emulators --launch apple_ios_simulator
    echo "Waiting for simulator to start..."
    sleep 5
    echo "Running app on iOS..."
    flutter run -d ios
}

# Function to start Android emulator
start_android() {
    echo "🤖 Starting Android Emulator..."
    echo "Launching Android emulator first..."
    flutter emulators --launch Medium_Phone_API_36
    echo "Waiting for emulator to start..."
    sleep 10
    echo "Running app on Android..."
    flutter run -d android
}

# Function to show all devices
show_devices() {
    echo "📋 Available devices:"
    flutter devices
    echo ""
    echo "📋 Available emulators:"
    flutter emulators
}

# Main menu loop
while true; do
    show_options
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            start_chrome_mobile
            break
            ;;
        2)
            start_ios
            break
            ;;
        3)
            start_android
            break
            ;;
        4)
            show_devices
            ;;
        5)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please choose 1-5."
            ;;
    esac
done 