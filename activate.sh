#!/bin/bash
# Activate the virtual environment for development

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODE_DIR="$SCRIPT_DIR/code"

if [ ! -d "$CODE_DIR/.venv" ]; then
    echo "Error: Virtual environment not found."
    echo "Please run ./setup-venv.sh first."
    exit 1
fi

echo "Activating virtual environment..."
echo "Run 'deactivate' to exit the virtual environment."
echo ""

cd "$CODE_DIR"
exec bash --init-file <(echo "source .venv/bin/activate; PS1='(nano-banana) \u@\h:\w\$ '")
