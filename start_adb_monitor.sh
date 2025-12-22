#!/bin/bash

# Start ADB Monitor in Background

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="$SCRIPT_DIR/adb_monitor.sh"
PID_FILE="$SCRIPT_DIR/.adb_monitor.pid"
LOG_FILE="$SCRIPT_DIR/adb_monitor.log"

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "⚠️  ADB Monitor is already running (PID: $OLD_PID)"
        echo "   To stop it, run: sh stop_adb_monitor.sh"
        exit 1
    else
        # Stale PID file, remove it
        rm "$PID_FILE"
    fi
fi

# Start monitor in background
echo "🚀 Starting ADB Port Forwarding Monitor..."
nohup "$MONITOR_SCRIPT" > "$LOG_FILE" 2>&1 &
MONITOR_PID=$!

# Save PID
echo $MONITOR_PID > "$PID_FILE"

echo "✅ ADB Monitor started (PID: $MONITOR_PID)"
echo "📝 Logs: $LOG_FILE"
echo ""
echo "Commands:"
echo "  View logs:  tail -f adb_monitor.log"
echo "  Stop:       sh stop_adb_monitor.sh"
echo "  Status:     sh status_adb_monitor.sh"

# Show initial logs
sleep 2
echo ""
echo "--- Recent Activity ---"
tail -n 10 "$LOG_FILE"
