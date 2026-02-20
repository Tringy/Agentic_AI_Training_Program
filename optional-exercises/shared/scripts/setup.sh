#!/bin/bash
# Environment setup script for AI Training exercises
# This script sets up Python virtual environment and installs dependencies

set -e  # Exit on error

echo "🚀 AI Training - Environment Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 not found"
    echo "   Install Python 3.10+ from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "❌ Error: Python 3.10+ required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION"
echo ""

# Check Node.js version (optional but recommended)
echo "Checking Node.js version (optional)..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js $NODE_VERSION"
else
    echo "⚠️  Node.js not found (optional for TypeScript exercises)"
fi
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists"
    read -p "Recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "✅ Virtual environment recreated"
    fi
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --quiet --upgrade pip
echo "✅ pip upgraded"
echo ""

# Install common dependencies
echo "Installing common dependencies..."
pip install --quiet \
    anthropic>=0.18.0 \
    openai>=1.12.0 \
    google-generativeai>=0.3.0 \
    fastapi>=0.109.0 \
    uvicorn>=0.27.0 \
    pydantic>=2.5.3 \
    python-dotenv>=1.0.0 \
    tiktoken>=0.5.2 \
    pytest>=7.4.0

echo "✅ Common dependencies installed"
echo ""

# Setup .env file
if [ -f ".env.example" ]; then
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo "✅ Created .env from .env.example"
        echo "⚠️  IMPORTANT: Edit .env and add your API keys"
        echo ""
    else
        echo "ℹ️  .env already exists (not overwriting)"
        echo ""
    fi
fi

# Check for API keys
echo "Checking API keys..."
if [ -f ".env" ]; then
    source .env

    KEYS_FOUND=0

    if [ ! -z "$ANTHROPIC_API_KEY" ]; then
        echo "✅ ANTHROPIC_API_KEY configured"
        KEYS_FOUND=$((KEYS_FOUND + 1))
    else
        echo "⚠️  ANTHROPIC_API_KEY not set"
    fi

    if [ ! -z "$OPENAI_API_KEY" ]; then
        echo "✅ OPENAI_API_KEY configured"
        KEYS_FOUND=$((KEYS_FOUND + 1))
    else
        echo "ℹ️  OPENAI_API_KEY not set (optional)"
    fi

    if [ ! -z "$GOOGLE_API_KEY" ]; then
        echo "✅ GOOGLE_API_KEY configured"
        KEYS_FOUND=$((KEYS_FOUND + 1))
    else
        echo "ℹ️  GOOGLE_API_KEY not set (optional)"
    fi

    if [ $KEYS_FOUND -eq 0 ]; then
        echo ""
        echo "⚠️  WARNING: No API keys found!"
        echo "   Edit .env and add at least one API key:"
        echo "   - ANTHROPIC_API_KEY (get from https://console.anthropic.com)"
        echo "   - GOOGLE_API_KEY (free, get from https://aistudio.google.com)"
        echo "   - OPENAI_API_KEY (get from https://platform.openai.com)"
    fi
else
    echo "⚠️  No .env file found"
    echo "   Create one with your API keys"
fi

echo ""
echo "=================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Configure API keys in .env file"
echo "3. Run an exercise: cd level-1-foundational/ex01-token-counter"
echo "4. Install exercise dependencies: pip install -r requirements.txt"
echo "5. Start coding!"
echo ""
