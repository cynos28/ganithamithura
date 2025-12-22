#!/bin/bash

# Stop ADB Monitor

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.adb_monitor.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  ADB Monitor is not running (no PID file found)"
    exit 1
fi

MONITOR_PID=$(cat "$PID_FILE")

if ps -p $MONITOR_PID > /dev/null 2>&1; then
    echo "🛑 Stopping ADB Monitor (PID: $MONITOR_PID)..."
    kill $MONITOR_PID
    rm "$PID_FILE"
    echo "✅ ADB Monitor stopped"
else
    echo "⚠️  Process $MONITOR_PID not found (already stopped?)"
    rm "$PID_FILE"
fi
