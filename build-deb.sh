#!/bin/bash

# Build .deb package for Nano Banana Desktop
# Creates a Debian package for Ubuntu installation

set -e

echo "🍌 Nano Banana Desktop - Debian Package Builder"
echo "================================================"
echo ""

# Configuration
APP_NAME="nano-banana-desktop"
VERSION="1.0.0"
ARCH="amd64"
MAINTAINER="Daniel Rosehill <public@danielrosehill.com>"
DESCRIPTION="Desktop image editing utility using Google's Gemini Flash 2.5 Images"
HOMEPAGE="https://github.com/danielrosehill/Nano-Banana-Desktop"

# Check if we're in the right directory
if [ ! -d "code" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Create build directory structure
BUILD_DIR="build-deb"
PKG_DIR="${BUILD_DIR}/${APP_NAME}_${VERSION}_${ARCH}"

echo "📁 Creating package directory structure..."
rm -rf "${BUILD_DIR}"
mkdir -p "${PKG_DIR}/DEBIAN"
mkdir -p "${PKG_DIR}/opt/${APP_NAME}"
mkdir -p "${PKG_DIR}/usr/share/applications"
mkdir -p "${PKG_DIR}/usr/share/pixmaps"
mkdir -p "${PKG_DIR}/usr/bin"

# Copy application files
echo "📦 Copying application files..."
cp -r code/nano_banana "${PKG_DIR}/opt/${APP_NAME}/"
cp -r code/prompts "${PKG_DIR}/opt/${APP_NAME}/"
cp code/pyproject.toml "${PKG_DIR}/opt/${APP_NAME}/"

# Create launcher script
echo "🔧 Creating launcher script..."
cat > "${PKG_DIR}/opt/${APP_NAME}/nano-banana-launcher.sh" << 'LAUNCHER_EOF'
#!/bin/bash
# Launcher script for Nano Banana Desktop

APP_DIR="/opt/nano-banana-desktop"
VENV_DIR="$HOME/.local/share/nano-banana-desktop/venv"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "First-time setup: Creating virtual environment..."
    mkdir -p "$HOME/.local/share/nano-banana-desktop"
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"

    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install google-genai pillow pyside6 keyring

    echo "Setup complete!"
fi

# Activate virtual environment and run
source "$VENV_DIR/bin/activate"
cd "$APP_DIR"
python3 -m nano_banana
LAUNCHER_EOF

chmod +x "${PKG_DIR}/opt/${APP_NAME}/nano-banana-launcher.sh"

# Create symlink in /usr/bin
echo "🔗 Creating executable symlink..."
ln -s "/opt/${APP_NAME}/nano-banana-launcher.sh" "${PKG_DIR}/usr/bin/${APP_NAME}"

# Create desktop entry
echo "🖥️  Creating desktop entry..."
cat > "${PKG_DIR}/usr/share/applications/${APP_NAME}.desktop" << DESKTOP_EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Nano Banana Desktop
Comment=AI-powered image editing using Google Gemini
Exec=/usr/bin/nano-banana-desktop
Icon=nano-banana-desktop
Terminal=false
Categories=Graphics;Photography;ImageProcessing;
Keywords=image;edit;ai;gemini;transformation;
DESKTOP_EOF

# Create a simple icon placeholder (you can replace with actual icon)
echo "🎨 Creating icon placeholder..."
cat > "${PKG_DIR}/usr/share/pixmaps/${APP_NAME}.svg" << 'SVG_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <rect width="64" height="64" rx="8" fill="#FFD700"/>
  <text x="32" y="42" font-size="40" text-anchor="middle" fill="#333">🍌</text>
</svg>
SVG_EOF

# Create control file
echo "📝 Creating control file..."
cat > "${PKG_DIR}/DEBIAN/control" << CONTROL_EOF
Package: ${APP_NAME}
Version: ${VERSION}
Section: graphics
Priority: optional
Architecture: ${ARCH}
Depends: python3 (>= 3.10), python3-venv, python3-pip
Maintainer: ${MAINTAINER}
Homepage: ${HOMEPAGE}
Description: ${DESCRIPTION}
 A desktop image editing utility for Linux that leverages Google's
 Gemini Flash 2.5 Images (Nano Banana) for AI-powered image transformations.
 .
 Features:
  - Tab-based interface for managing multiple images
  - AI-powered image editing using Gemini's image-to-image capabilities
  - Prewritten prompt templates for common edits
  - Custom prompt support
  - Version control with automatic backup
CONTROL_EOF

# Create postinst script (runs after installation)
echo "📝 Creating postinst script..."
cat > "${PKG_DIR}/DEBIAN/postinst" << 'POSTINST_EOF'
#!/bin/bash
set -e

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database -q
fi

echo ""
echo "✅ Nano Banana Desktop installed successfully!"
echo ""
echo "To run the application:"
echo "  1. From terminal: nano-banana-desktop"
echo "  2. From application menu: Search for 'Nano Banana Desktop'"
echo ""
echo "⚠️  Note: You will need a Google Gemini API key to use this application."
echo ""

exit 0
POSTINST_EOF

chmod +x "${PKG_DIR}/DEBIAN/postinst"

# Create prerm script (runs before removal)
echo "📝 Creating prerm script..."
cat > "${PKG_DIR}/DEBIAN/prerm" << 'PRERM_EOF'
#!/bin/bash
set -e

echo "Removing Nano Banana Desktop..."

exit 0
PRERM_EOF

chmod +x "${PKG_DIR}/DEBIAN/prerm"

# Create postrm script (runs after removal)
echo "📝 Creating postrm script..."
cat > "${PKG_DIR}/DEBIAN/postrm" << 'POSTRM_EOF'
#!/bin/bash
set -e

# Clean up user data if desired
if [ "$1" = "purge" ]; then
    echo "Purging user data..."
    rm -rf "$HOME/.local/share/nano-banana-desktop"
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database -q
fi

exit 0
POSTRM_EOF

chmod +x "${PKG_DIR}/DEBIAN/postrm"

# Calculate installed size
echo "📊 Calculating package size..."
INSTALLED_SIZE=$(du -sk "${PKG_DIR}" | cut -f1)
echo "Installed-Size: ${INSTALLED_SIZE}" >> "${PKG_DIR}/DEBIAN/control"

# Build the package
echo "🔨 Building .deb package..."
dpkg-deb --build --root-owner-group "${PKG_DIR}"

# Move to dist directory
echo "📦 Moving package to dist directory..."
mkdir -p dist
mv "${PKG_DIR}.deb" "dist/${APP_NAME}_${VERSION}_${ARCH}.deb"

# Cleanup
echo "🧹 Cleaning up build artifacts..."
rm -rf "${BUILD_DIR}"

echo ""
echo "✅ Package built successfully!"
echo ""
echo "Package: dist/${APP_NAME}_${VERSION}_${ARCH}.deb"
echo "Size: $(du -h "dist/${APP_NAME}_${VERSION}_${ARCH}.deb" | cut -f1)"
echo ""
echo "To install:"
echo "  sudo dpkg -i dist/${APP_NAME}_${VERSION}_${ARCH}.deb"
echo "  sudo apt-get install -f  # Install dependencies if needed"
echo ""
echo "To test with lintian (optional):"
echo "  lintian dist/${APP_NAME}_${VERSION}_${ARCH}.deb"
echo ""
