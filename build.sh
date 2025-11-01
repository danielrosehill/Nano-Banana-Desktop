#!/bin/bash

# Build script for Nano Banana Desktop
# Creates a standalone Python executable using PyInstaller

set -e

echo "🍌 Nano Banana Desktop - Build Script"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -d "code" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Navigate to code directory
cd code

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    uv venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies including PyInstaller
echo "📦 Installing dependencies..."
uv pip install -e ".[dev]"
uv pip install pyinstaller

# Create build directory
echo "📁 Creating build directory..."
mkdir -p ../dist

# Run PyInstaller
echo "🔨 Building executable..."
pyinstaller \
    --name="nano-banana-desktop" \
    --onefile \
    --windowed \
    --add-data="prompts:prompts" \
    --hidden-import=PySide6.QtCore \
    --hidden-import=PySide6.QtGui \
    --hidden-import=PySide6.QtWidgets \
    --hidden-import=google.genai \
    --hidden-import=keyring \
    --hidden-import=PIL \
    nano_banana/main.py

# Move executable to dist directory
echo "📦 Moving executable to dist directory..."
if [ -f "dist/nano-banana-desktop" ]; then
    mv dist/nano-banana-desktop ../dist/
    echo "✅ Build successful!"
    echo ""
    echo "Executable created at: ./dist/nano-banana-desktop"
    echo ""
    echo "To run: ./dist/nano-banana-desktop"
else
    echo "❌ Build failed - executable not found"
    exit 1
fi

# Cleanup
echo "🧹 Cleaning up build artifacts..."
rm -rf build
rm -f nano-banana-desktop.spec

echo ""
echo "🎉 Build complete!"
