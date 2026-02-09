#!/bin/bash

# Hybrid Location Detection Demo - Startup Script
# Starts both backend and frontend servers

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "🌍 Hybrid Location Detection Demo"
echo "================================"
echo ""

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 8000 already in use. Killing existing process..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Check if port 8001 is already in use
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 8001 already in use. Killing existing process..."
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo "🚀 Starting Backend (FastAPI) on port 8000..."
cd "$BACKEND_DIR"
python main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "   ✓ Backend PID: $BACKEND_PID"

echo "📱 Starting Frontend on port 8001..."
cd "$FRONTEND_DIR"
python -m http.server 8001 > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   ✓ Frontend PID: $FRONTEND_PID"

sleep 2

echo ""
echo "✅ Servers Started!"
echo ""
echo "🌐 Frontend: http://localhost:8001"
echo "🔌 Backend API: http://localhost:8000"
echo "📊 Location Data: $BACKEND_DIR/location_output.json"
echo ""
echo "📖 To test on mobile:"
echo "   1. Find your Mac IP: ifconfig | grep inet"
echo "   2. Visit: http://<YOUR_MAC_IP>:8001"
echo ""
echo "🛑 To stop, press CTRL+C"
echo ""

# Wait for both processes
wait
