#!/bin/bash

# Kill existing server on port 8000
EXISTING_PID=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$EXISTING_PID" ]; then
    kill -9 $EXISTING_PID 2>/dev/null
    sleep 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Install dependencies if needed (silently)
python -c "import fastapi" 2>/dev/null || pip install -r requirements.txt > /dev/null 2>&1

echo "Server starting at http://localhost:8000"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --reload-dir app
