#!/bin/bash
# Quick Start Script for AR Feature Testing
# This script starts both backend services required for AR measurements

echo "🚀 Starting GanithaMithura AR Feature Services..."
echo ""

# Check if we're in the right directory
if [ ! -d "measurement-service" ] || [ ! -d "unit-rag-service" ]; then
    echo "❌ Error: Please run this script from the ganithamithura root directory"
    exit 1
fi

# Function to check if port is in use
check_port() {
    lsof -ti :$1 > /dev/null 2>&1
    return $?
}

# Kill existing processes on ports 8000 and 8001
echo "🧹 Cleaning up existing services..."
if check_port 8000; then
    echo "   Stopping service on port 8000..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null
fi
if check_port 8001; then
    echo "   Stopping service on port 8001..."
    lsof -ti :8001 | xargs kill -9 2>/dev/null
fi

echo ""
echo "📦 Installing dependencies..."

# Setup measurement-service
echo "   Setting up measurement-service..."
cd measurement-service
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
deactivate
cd ..

# Setup unit-rag-service (assuming it's already set up)
echo "   Checking unit-rag-service..."
cd unit-rag-service
if [ ! -d "venv" ]; then
    echo "   ⚠️  unit-rag-service venv not found. Please set it up manually."
else
    echo "   ✅ unit-rag-service ready"
fi
cd ..

echo ""
echo "🎬 Starting services..."
echo ""

# Start measurement-service in background
echo "   Starting measurement-service on port 8001..."
cd measurement-service
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8001 > ../logs/measurement-service.log 2>&1 &
MEASUREMENT_PID=$!
deactivate
cd ..

# Wait a moment for first service to start
sleep 2

# Start unit-rag-service in background
echo "   Starting unit-rag-service on port 8000..."
cd unit-rag-service
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../logs/rag-service.log 2>&1 &
RAG_PID=$!
deactivate
cd ..

# Wait for services to start
echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check if services are running
echo ""
echo "🔍 Checking service health..."

measurement_status=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/health 2>/dev/null)
rag_status=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health 2>/dev/null)

if [ "$measurement_status" = "200" ]; then
    echo "   ✅ measurement-service: Running on port 8001"
else
    echo "   ❌ measurement-service: Not responding (check logs/measurement-service.log)"
fi

if [ "$rag_status" = "200" ]; then
    echo "   ✅ unit-rag-service: Running on port 8000"
else
    echo "   ❌ unit-rag-service: Not responding (check logs/rag-service.log)"
fi

echo ""
echo "📝 Service URLs:"
echo "   measurement-service: http://127.0.0.1:8001"
echo "   unit-rag-service:    http://127.0.0.1:8000"
echo ""
echo "📊 View logs:"
echo "   tail -f logs/measurement-service.log"
echo "   tail -f logs/rag-service.log"
echo ""
echo "🛑 To stop services:"
echo "   lsof -ti :8000 | xargs kill -9"
echo "   lsof -ti :8001 | xargs kill -9"
echo ""
echo "🎉 Setup complete! You can now run the Flutter app."
echo ""
