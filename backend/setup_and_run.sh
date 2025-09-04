#!/bin/bash

echo "🚀 Setting up CV Agent Backend..."

# Navigate to backend directory
cd /Users/mahesh/Documents/GitHub/backend

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip and install build tools
echo "⬆️ Upgrading pip and build tools..."
pip install --upgrade pip wheel setuptools

# Install dependencies
echo "📚 Installing dependencies..."
pip install fastapi==0.100.0 "uvicorn[standard]==0.21.0" python-dotenv python-multipart pydantic
pip install pdfplumber python-docx beautifulsoup4 httpx requests
pip install openai sentence-transformers==3.0.1 scikit-learn==1.4.0 flashtext==2.7
pip install pyquery==2.0.1 cssselect==1.3.0 pyppeteer==2.0.0 pyee==11.1.1 fake-useragent==2.2.0 parse==1.20.2 w3lib==2.3.1
pip install spacy==3.7.6

# Download spaCy English model
echo "🌍 Downloading spaCy English model..."
python -m spacy download en_core_web_sm

# Create required directories
echo "📁 Creating required directories..."
mkdir -p tailored_cvs

# Kill any existing process on port 8000
echo "🔪 Killing existing processes on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start the server
echo "🚀 Starting FastAPI server on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 