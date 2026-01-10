#!/bin/bash

# Installation script for NLP to SQL Chat Application

echo "======================================================"
echo "NLP to SQL Chat Application - Installation Script"
echo "======================================================"
echo ""

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
    echo "✓ Python $PYTHON_VERSION found"
else
    echo "✗ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

echo ""
echo "Step 1: Installing Python dependencies..."
echo "----------------------------------------"
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

echo ""
echo "Step 2: Setting up environment file..."
echo "----------------------------------------"
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file from .env.example"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your OpenRouter API key!"
    echo "   Get your API key from: https://openrouter.ai/"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "Step 3: Creating required directories..."
echo "----------------------------------------"
mkdir -p database
mkdir -p data/processed
echo "✓ Directories created"

echo ""
echo "Step 4: Verifying setup..."
echo "----------------------------------------"
python3 test_setup.py

echo ""
echo "======================================================"
echo "Installation complete!"
echo "======================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OpenRouter API key"
echo "2. Place your CSV/Excel files in data/excel_files/"
echo "3. Run: streamlit run app.py"
echo ""
