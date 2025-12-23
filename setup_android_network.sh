#!/bin/bash
# Setup Android networking for backend connectivity
# Run this after connecting Android device via USB

echo "🔧 Setting up Android network for backend access..."
echo ""

# Check if adb is installed
if ! command -v adb &> /dev/null; then
    echo "❌ ADB not found. Please install Android SDK Platform Tools"
    echo "   Download: https://developer.android.com/studio/releases/platform-tools"
    exit 1
fi

echo "📱 Checking for connected devices..."
adb devices -l

echo ""
echo "🔌 Setting up port forwarding..."
# Forward port 8000 from device to host
adb reverse tcp:8000 tcp:8000

if [ $? -eq 0 ]; then
    echo "✅ Port forwarding configured: device port 8000 → host port 8000"
    echo "   Your Flutter app can now use 'localhost:8000' on physical devices!"
else
    echo "❌ Failed to setup port forwarding"
    echo "   Fallback: Use your Mac's IP address instead"
    echo "   Current IP: $(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')"
fi

echo ""
echo "🌐 Your network configuration:"
echo "   Mac IP: $(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')"
echo "   Backend Port: 8000"
echo ""
echo "📋 How to connect:"
echo "   Android Emulator: http://10.0.2.2:8000 (auto-configured ✅)"
echo "   Android Physical: http://localhost:8000 (if adb reverse setup ✅)"
echo "   iOS Simulator:    http://localhost:8000"
echo "   WiFi (Any):       http://$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}'):8000"
echo ""
echo "🚀 Ready to run your Flutter app!"
