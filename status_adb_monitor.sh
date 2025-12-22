#!/bin/bash

# Check ADB Monitor Status

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.adb_monitor.pid"
LOG_FILE="$SCRIPT_DIR/adb_monitor.log"

echo "📊 ADB Monitor Status"
echo "===================="

if [ -f "$PID_FILE" ]; then
    MONITOR_PID=$(cat "$PID_FILE")
    if ps -p $MONITOR_PID > /dev/null 2>&1; then
        echo "✅ Status: Running"
        echo "🆔 PID: $MONITOR_PID"
        echo "⏱️  Uptime: $(ps -o etime= -p $MONITOR_PID | tr -d ' ')"
        
        # Check device status
        ADB_PATH="$HOME/Library/Android/sdk/platform-tools/adb"
        DEVICE_COUNT=$($ADB_PATH devices | grep -v "List of devices" | grep "device$" | wc -l)
        
        if [ $DEVICE_COUNT -gt 0 ]; then
            echo "📱 Device: Connected"
            
            # Check port forwarding
            if $ADB_PATH reverse --list 2>/dev/null | grep -q "tcp:8000"; then
                echo "🔗 Port Forwarding: Active (8000 → 8000)"
            else
                echo "⚠️  Port Forwarding: Inactive"
            fi
        else
            echo "📱 Device: Not connected"
        fi
        
        echo ""
        echo "--- Recent Activity (last 5 lines) ---"
        tail -n 5 "$LOG_FILE" 2>/dev/null || echo "(no logs yet)"
        
    else
        echo "❌ Status: Not running (stale PID file)"
        rm "$PID_FILE"
    fi
else
    echo "❌ Status: Not running"
fi

echo ""
echo "Commands:"
echo "  Start:      sh start_adb_monitor.sh"
echo "  Stop:       sh stop_adb_monitor.sh"
echo "  View logs:  tail -f adb_monitor.log"
