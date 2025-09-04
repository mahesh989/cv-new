#!/bin/bash

echo "📦 Installing CV Agent Backend Dependencies..."

# Navigate to backend directory
cd /Users/mahesh/Documents/GitHub/backend

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip and install build tools
echo "⬆️ Upgrading pip and build tools..."
pip install --upgrade pip wheel setuptools

# Install all dependencies from requirements.txt
echo "📚 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Download spaCy English model
echo "🌍 Downloading spaCy English model..."
python -m spacy download en_core_web_sm

# Create required directories
echo "📁 Creating required directories..."
mkdir -p tailored_cvs

echo "✅ All dependencies installed successfully!"
echo ""
echo "To start the server, run:"
echo "  source .venv/bin/activate"
echo "  python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Or use the setup script:"
echo "  ./setup_and_run.sh" 