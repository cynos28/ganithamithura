#!/bin/bash

# GanithaMithura AR Measurement System - Startup Script
# This script starts all required services for the AR measurement app

set -e  # Exit on error

echo "🚀 Starting GanithaMithura AR Measurement System..."
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="/Users/shehandulmina/Downloads/Research/GM/ganithamithura"
VENV_PATH="$PROJECT_ROOT/.venv/bin/activate"

# Check if virtual environment exists
if [ ! -f "$VENV_PATH" ]; then
    echo -e "${RED}❌ Virtual environment not found at $VENV_PATH${NC}"
    echo "Please create it first: python -m venv .venv"
    exit 1
fi

# Function to start a service in a new terminal tab
start_service() {
    local service_name=$1
    local service_path=$2
    local port=$3
    local extra_env=$4
    
    echo -e "${BLUE}📦 Starting $service_name on port $port...${NC}"
    
    # macOS: Open new terminal tab
    if [[ "$OSTYPE" == "darwin"* ]]; then
        osascript -e "
            tell application \"Terminal\"
                activate
                do script \"cd $service_path && source $VENV_PATH && $extra_env PYTHONPATH=$service_path python -m app.main\"
            end tell
        " > /dev/null 2>&1
    else
        # Linux: Use gnome-terminal or xterm
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal --tab --title="$service_name" -- bash -c "cd $service_path && source $VENV_PATH && $extra_env PYTHONPATH=$service_path python -m app.main; exec bash"
        else
            echo -e "${YELLOW}⚠️  Cannot open new terminal. Please start manually:${NC}"
            echo "  cd $service_path"
            echo "  source $VENV_PATH"
            echo "  $extra_env PYTHONPATH=$service_path python -m app.main"
        fi
    fi
    
    sleep 2
}

# 1. Start Measurement Service (Port 8001)
echo ""
echo -e "${GREEN}Step 1: Starting Measurement Service${NC}"
start_service "Measurement Service" "$PROJECT_ROOT/measurement-service" "8001" ""

# 2. Start Unit RAG Service (Port 8000)
echo ""
echo -e "${GREEN}Step 2: Starting RAG Service${NC}"

# Get OpenAI API key from .env
OPENAI_KEY=""
if [ -f "$PROJECT_ROOT/unit-rag-service/.env" ]; then
    OPENAI_KEY=$(grep "OPENAI_API_KEY=" "$PROJECT_ROOT/unit-rag-service/.env" | cut -d'=' -f2)
fi

if [ -z "$OPENAI_KEY" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY not found in unit-rag-service/.env${NC}"
    echo "Please add it to the .env file"
    exit 1
fi

start_service "RAG Service" "$PROJECT_ROOT/unit-rag-service" "8000" "OPENAI_API_KEY=$OPENAI_KEY"

# 3. Setup ADB reverse for physical devices
echo ""
echo -e "${GREEN}Step 3: Setting up ADB port forwarding${NC}"

if command -v adb &> /dev/null; then
    ADB_PATH="adb"
elif [ -f "$HOME/Library/Android/sdk/platform-tools/adb" ]; then
    ADB_PATH="$HOME/Library/Android/sdk/platform-tools/adb"
else
    echo -e "${YELLOW}⚠️  ADB not found. Skipping port forwarding.${NC}"
    echo "   For physical devices, run manually:"
    echo "   adb reverse tcp:8001 tcp:8001"
    echo "   adb reverse tcp:8000 tcp:8000"
    ADB_PATH=""
fi

if [ -n "$ADB_PATH" ]; then
    if $ADB_PATH devices | grep -q "device$"; then
        echo -e "${BLUE}📱 Setting up port forwarding for connected device...${NC}"
        $ADB_PATH reverse tcp:8001 tcp:8001
        $ADB_PATH reverse tcp:8000 tcp:8000
        echo -e "${GREEN}✅ Port forwarding configured: 8001, 8000${NC}"
    else
        echo -e "${YELLOW}⚠️  No Android device connected${NC}"
        echo "   Connect device and run:"
        echo "   $ADB_PATH reverse tcp:8001 tcp:8001"
        echo "   $ADB_PATH reverse tcp:8000 tcp:8000"
    fi
fi

# 4. Wait for services to start
echo ""
echo -e "${BLUE}⏳ Waiting for services to start (10 seconds)...${NC}"
sleep 10

# 5. Check if services are running
echo ""
echo -e "${GREEN}Step 4: Verifying services${NC}"

check_service() {
    local service_name=$1
    local port=$2
    
    if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name is running on port $port${NC}"
        return 0
    else
        echo -e "${RED}❌ $service_name is not responding on port $port${NC}"
        return 1
    fi
}

MEASUREMENT_OK=0
RAG_OK=0

check_service "Measurement Service" "8001" && MEASUREMENT_OK=1 || MEASUREMENT_OK=0
check_service "RAG Service" "8000" && RAG_OK=1 || RAG_OK=0

# 6. Print status and next steps
echo ""
echo "=================================================="
echo -e "${GREEN}🎉 Startup Complete!${NC}"
echo "=================================================="
echo ""

if [ $MEASUREMENT_OK -eq 1 ] && [ $RAG_OK -eq 1 ]; then
    echo -e "${GREEN}All services are running successfully!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Open the Flutter app:"
    echo "   cd $PROJECT_ROOT/ganithamithura"
    echo "   flutter run"
    echo ""
    echo "2. Test the AR measurement flow:"
    echo "   - Select 'Length' measurement"
    echo "   - Point camera at an object (desk, chair, etc.)"
    echo "   - Tap to measure"
    echo "   - Confirm detected object or select manually"
    echo "   - Answer personalized question!"
    echo ""
    echo -e "${BLUE}Service URLs:${NC}"
    echo "   Measurement: http://localhost:8001/docs"
    echo "   RAG: http://localhost:8000/docs"
    echo ""
else
    echo -e "${YELLOW}⚠️  Some services failed to start${NC}"
    echo "Please check the terminal tabs for error messages"
    echo ""
    echo "Manual startup commands:"
    echo ""
    echo "Measurement Service:"
    echo "  cd $PROJECT_ROOT/measurement-service"
    echo "  source $VENV_PATH"
    echo "  PYTHONPATH=\$PWD python -m app.main"
    echo ""
    echo "RAG Service:"
    echo "  cd $PROJECT_ROOT/unit-rag-service"
    echo "  source $VENV_PATH"
    echo "  OPENAI_API_KEY=your-key PYTHONPATH=\$PWD python -m app.main"
    echo ""
fi

echo -e "${BLUE}To stop services:${NC}"
echo "  lsof -ti :8001 | xargs kill -9"
echo "  lsof -ti :8000 | xargs kill -9"
echo ""
