#!/bin/bash
# Setup ADB port forwarding for physical device

echo "📱 Setting up ADB port forwarding..."
~/Library/Android/sdk/platform-tools/adb reverse tcp:8000 tcp:8000

if [ $? -eq 0 ]; then
    echo "✅ Port forwarding active: Device can now access localhost:8000"
else
    echo "❌ Failed to set up port forwarding. Make sure:"
    echo "   1. Device is connected via USB"
    echo "   2. USB debugging is enabled"
    echo "   3. Run: ~/Library/Android/sdk/platform-tools/adb devices"
fi
