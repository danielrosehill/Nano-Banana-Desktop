#!/bin/bash
# Run script for Nano Banana Desktop

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODE_DIR="$SCRIPT_DIR/code"

# Check if virtual environment exists
if [ ! -d "$CODE_DIR/.venv" ]; then
    echo "Error: Virtual environment not found."
    echo "Please run ./setup-venv.sh first to set up the environment."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$CODE_DIR/.venv/bin/activate"

# Navigate to code directory
cd "$CODE_DIR"

# Check if main module exists
if [ -f "nano_banana/__main__.py" ]; then
    echo "Starting Nano Banana Desktop..."
    python3 -m nano_banana "$@"
elif [ -f "nano_banana/main.py" ]; then
    echo "Starting Nano Banana Desktop..."
    python3 nano_banana/main.py "$@"
else
    echo "Note: Main application entry point not yet created."
    echo "Virtual environment is active. You can now develop the application."
    echo ""
    echo "Starting a shell in the virtual environment..."
    exec bash
fi
