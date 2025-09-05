#!/bin/bash

# CV Management API Backend Startup Script
echo "Starting CV Management API Backend Server..."

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "Error: app/main.py not found. Please run this script from the backend directory."
    exit 1
fi

# Kill any existing server on port 8000
echo "Checking for existing server on port 8000..."
EXISTING_PID=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$EXISTING_PID" ]; then
    echo "Found existing server with PID: $EXISTING_PID"
    echo "Killing existing server..."
    kill -9 $EXISTING_PID 2>/dev/null
    sleep 2
    echo "Existing server killed."
else
    echo "No existing server found on port 8000."
fi

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "No virtual environment found. Using system Python."
fi

# Check if requirements are installed
echo "Checking dependencies..."
python -c "import fastapi" 2>/dev/null || {
    echo "FastAPI not found. Installing requirements..."
    pip install -r requirements.txt
}

# Start the server
echo "Starting FastAPI server on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Alternative Docs: http://localhost:8000/redoc"
echo "Press Ctrl+C to stop the server"
echo "=========================================="
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --reload-dir app
