#!/bin/bash
# Quick Start Script for RAG Starter Template

echo "RAG Starter - Quick Start"
echo "========================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Step 1: Creating .env file from template..."
    cp .env.example .env
    echo "  Created .env file. Please edit it and add your OPENAI_API_KEY"
    echo ""
    echo "  Get your API key from: https://platform.openai.com/api-keys"
    echo ""
    read -p "Press enter after you've added your API key to .env..."
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Step 2: Creating virtual environment..."
    python3 -m venv venv
    echo "  Virtual environment created"
fi

# Activate venv
echo ""
echo "Step 3: Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Step 4: Installing dependencies..."
pip install -q -r requirements.txt
echo "  Dependencies installed"

# Start server
echo ""
echo "Step 5: Starting RAG server..."
echo ""
echo "Server will be available at: http://localhost:8000"
echo "API docs available at: http://localhost:8000/docs"
echo ""
echo "To test the API, run in another terminal:"
echo "  python example_usage.py"
echo ""

python main.py
