#!/bin/bash

# Persistent ADB Port Forwarding Monitor
# Automatically maintains port forwarding when device connects/reconnects

ADB_PATH="$HOME/Library/Android/sdk/platform-tools/adb"
PORT=8000
CHECK_INTERVAL=5  # Check every 5 seconds

echo "🔄 Starting ADB Port Forwarding Monitor..."
echo "📱 Monitoring for device on port $PORT"
echo "⏱️  Check interval: ${CHECK_INTERVAL}s"
echo ""
echo "Press Ctrl+C to stop"
echo "----------------------------------------"

# Function to setup port forwarding
setup_forwarding() {
    $ADB_PATH reverse tcp:$PORT tcp:$PORT 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ $(date '+%H:%M:%S') - Port forwarding active: Device localhost:$PORT → Computer localhost:$PORT"
        return 0
    else
        return 1
    fi
}

# Function to check if device is connected
is_device_connected() {
    device_count=$($ADB_PATH devices | grep -v "List of devices" | grep "device$" | wc -l)
    [ $device_count -gt 0 ]
}

# Function to check if forwarding is active
is_forwarding_active() {
    $ADB_PATH reverse --list 2>/dev/null | grep -q "tcp:$PORT"
}

# Main monitoring loop
previous_state="disconnected"

while true; do
    if is_device_connected; then
        # Device is connected
        if [ "$previous_state" = "disconnected" ]; then
            echo "📱 $(date '+%H:%M:%S') - Device detected!"
            previous_state="connected"
        fi
        
        # Check if forwarding is active, if not, set it up
        if ! is_forwarding_active; then
            echo "🔧 $(date '+%H:%M:%S') - Setting up port forwarding..."
            setup_forwarding
        fi
    else
        # Device is not connected
        if [ "$previous_state" = "connected" ]; then
            echo "⚠️  $(date '+%H:%M:%S') - Device disconnected, waiting for reconnection..."
            previous_state="disconnected"
        fi
    fi
    
    sleep $CHECK_INTERVAL
done
