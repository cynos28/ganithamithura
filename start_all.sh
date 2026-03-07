#!/bin/bash
# A simple script to start the Symbol API, Auth API, and Ngrok tunnels all at once

# Set terminal color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==============================================${NC}"
echo -e "${YELLOW}🚀 Starting Ganitha Mithura Backend Environment${NC}"
echo -e "${BLUE}==============================================${NC}"

# Navigate to the ganithamithura parent directory
cd "$(dirname "$0")"

# Start the Auth Service on port 8001
echo -e "${GREEN}1. Starting Auth Service (Port 8001)...${NC}"
cd auth_service
source .venv/bin/activate 2>/dev/null || echo "No .venv found in auth_service, using global python."
uvicorn main:app --reload --host 0.0.0.0 --port 8001 &
AUTH_PID=$!
cd ..

# Wait 1 second to ensure ports don't clash
sleep 1

# Start the Symbol Service on port 8000
echo -e "${GREEN}2. Starting Symbol Service (Port 8000)...${NC}"
cd symbol-service
source venv/bin/activate 2>/dev/null || echo "No venv found in symbol-service, using global python."
uvicorn src.server:app --reload --host 0.0.0.0 --port 8000 &
SYMBOL_PID=$!
cd ..

# Wait a couple seconds to make sure Uvicorn instances are running
sleep 3

# Start the Ngrok python script to Tunnel & Update the cloud JSON file
echo -e "${GREEN}3. Starting Ngrok Tunnels and updating Cloud JSON...${NC}"
source symbol-service/venv/bin/activate && python start_tunnels.py

# Function to gracefully kill the web servers when the user hits Ctrl+C
function cleanup() {
    echo -e "\n${RED}Shutting down everything...${NC}"
    kill $AUTH_PID
    kill $SYMBOL_PID
    echo -e "${GREEN}Goodbye!${NC}"
    exit 0
}

# Trap the SIGINT signal (Ctrl+C) and call cleanup
trap cleanup SIGINT

# Wait forever while all background processes run
wait
