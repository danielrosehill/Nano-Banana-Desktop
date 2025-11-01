#!/bin/bash
# Setup script for Nano Banana Desktop virtual environment

set -e

echo "======================================"
echo "Nano Banana Desktop - Setup Script"
echo "======================================"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed."
    echo "Please install uv first: https://github.com/astral-sh/uv"
    exit 1
fi

# Navigate to code directory
cd "$(dirname "$0")/code"

echo "Creating virtual environment..."
uv venv .venv

echo ""
echo "Installing dependencies..."
source .venv/bin/activate
uv pip install -e ".[dev]"

echo ""
echo "======================================"
echo "Setup complete!"
echo "======================================"
echo ""
echo "To activate the virtual environment, run:"
echo "  source code/.venv/bin/activate"
echo ""
echo "Or use the run.sh script to start the application."
