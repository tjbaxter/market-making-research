#!/bin/bash
# Installation script for market-making-research

echo "🚀 Market-Making Research - Installation Script"
echo "================================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Install package in development mode
echo "🔨 Installing package in development mode..."
pip install -e .

echo ""
echo "✅ Installation complete!"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests:"
echo "  pytest"
echo ""
echo "To run the example simulation:"
echo "  python examples/basic_simulation.py"
echo ""

