#!/bin/bash

echo "🚀 CV AGENT SYSTEM - STARTUP SCRIPT"
echo "=================================="
echo "🤖 Now using Claude Sonnet 4 (latest model)"
echo

# Navigate to backend directory
cd "$(dirname "$0")"
echo "📍 Current directory: $(pwd)"

# Check if required files exist
if [ ! -f "src/main.py" ]; then
    echo "❌ Error: main.py not found. Please run from backend directory."
    exit 1
fi

# Kill any existing servers on port 8000
echo "🔪 Stopping any existing servers on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 2

# Check for API keys
echo "🔑 Checking API keys..."
if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: No AI API keys found in environment"
    echo "   Please set ANTHROPIC_API_KEY or OPENAI_API_KEY"
    echo "   Example: export ANTHROPIC_API_KEY='your-key-here'"
fi

# Start the server
echo "🚀 Starting CV Agent Backend Server..."
echo "📡 Server will be available at: http://127.0.0.1:8000"
echo "📚 API Documentation: http://127.0.0.1:8000/docs"
echo "⚡ Using Claude Sonnet 4 for improved performance"
echo
echo "Press Ctrl+C to stop the server"
echo

# Start with Python
python -c "
import uvicorn
from src.main import app
print('✅ CV Agent Backend Server starting with Claude Sonnet 4...')
print('🌟 Enhanced JD skill extraction now active!')
uvicorn.run(app, host='127.0.0.1', port=8000, reload=True)
" 