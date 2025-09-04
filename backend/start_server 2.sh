#!/bin/bash

# CV Agent Backend Startup Script
echo "Starting CV Agent Backend Server..."

# Check if we're in the right directory
if [ ! -f "src/main.py" ]; then
    echo "Error: src/main.py not found. Please run this script from the my_cv_agent_backend directory."
    exit 1
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

# Start the server
echo "Starting FastAPI server on http://localhost:8000"
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --reload-dir src 