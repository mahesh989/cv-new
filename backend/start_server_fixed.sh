#!/bin/bash

echo "🚀 Starting CV Agent Backend Server..."

# Kill any existing processes on port 8000
echo "🔧 Checking for existing server on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "No existing server found on port 8000."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "🐍 Using virtual environment."
    source venv/bin/activate
else
    echo "🐍 No virtual environment found. Using system Python."
fi

# Test imports before starting
echo "🔍 Testing imports..."
python -c "from src.main import app; print('✅ Imports successful')" || {
    echo "❌ Import test failed. Please check dependencies."
    exit 1
}

echo "🚀 Starting FastAPI server on http://localhost:8000"
echo "📝 Press CTRL+C to stop the server"
echo ""

# Start the server with proper error handling
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --reload-dir src 