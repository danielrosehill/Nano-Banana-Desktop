#!/bin/bash

# Update script for Nano Banana Desktop
# Downloads and installs the latest .deb package

set -e

echo "🍌 Nano Banana Desktop - Update Script"
echo "======================================="
echo ""

# Configuration
APP_NAME="nano-banana-desktop"
GITHUB_REPO="danielrosehill/Nano-Banana-Desktop"
DEB_PATTERN="${APP_NAME}_*_amd64.deb"

# Function to check if package is installed
is_installed() {
    dpkg -l | grep -q "^ii  ${APP_NAME}"
}

# Function to get installed version
get_installed_version() {
    dpkg -l | grep "^ii  ${APP_NAME}" | awk '{print $3}' || echo "none"
}

# Check if app is currently installed
if is_installed; then
    CURRENT_VERSION=$(get_installed_version)
    echo "📦 Current version: ${CURRENT_VERSION}"
else
    echo "⚠️  Nano Banana Desktop is not currently installed"
    echo "This script will perform a fresh installation"
fi

echo ""
echo "🔍 Checking for updates..."

# Check if a local .deb file was provided
if [ $# -eq 1 ] && [ -f "$1" ]; then
    DEB_FILE="$1"
    echo "📥 Using local package: ${DEB_FILE}"
else
    # Download from GitHub releases
    echo "📡 Fetching latest release from GitHub..."

    # Check if gh CLI is available
    if command -v gh &> /dev/null; then
        # Use gh CLI to get latest release
        LATEST_URL=$(gh release view --repo "${GITHUB_REPO}" --json assets --jq '.assets[] | select(.name | endswith("_amd64.deb")) | .url')

        if [ -z "$LATEST_URL" ]; then
            echo "❌ No .deb package found in latest release"
            exit 1
        fi

        echo "📥 Downloading latest package..."
        DEB_FILE="/tmp/${APP_NAME}_latest.deb"
        gh release download --repo "${GITHUB_REPO}" --pattern "*_amd64.deb" --output "${DEB_FILE}"
    else
        echo "⚠️  GitHub CLI (gh) not found"
        echo ""
        echo "Please either:"
        echo "  1. Install gh: sudo apt install gh"
        echo "  2. Manually download the .deb from:"
        echo "     https://github.com/${GITHUB_REPO}/releases"
        echo "  3. Run this script with the .deb file as an argument:"
        echo "     ./update-deb.sh path/to/package.deb"
        exit 1
    fi
fi

# Extract version from .deb filename
NEW_VERSION=$(dpkg-deb -f "${DEB_FILE}" Version)
echo ""
echo "📦 New version: ${NEW_VERSION}"

# Compare versions if already installed
if is_installed; then
    if [ "${CURRENT_VERSION}" = "${NEW_VERSION}" ]; then
        echo ""
        echo "✅ You already have the latest version installed!"
        read -p "Do you want to reinstall? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Update cancelled"
            exit 0
        fi
    fi
fi

echo ""
echo "🔧 Installing package..."
echo ""

# Install the package
sudo dpkg -i "${DEB_FILE}"

# Fix dependencies if needed
if [ $? -ne 0 ]; then
    echo ""
    echo "🔧 Fixing dependencies..."
    sudo apt-get install -f -y
fi

# Verify installation
if is_installed; then
    INSTALLED_VERSION=$(get_installed_version)
    echo ""
    echo "✅ Successfully installed Nano Banana Desktop v${INSTALLED_VERSION}"
    echo ""
    echo "To run the application:"
    echo "  - From terminal: nano-banana-desktop"
    echo "  - From application menu: Search for 'Nano Banana Desktop'"
    echo ""
else
    echo ""
    echo "❌ Installation failed"
    exit 1
fi

# Cleanup temporary file if we downloaded it
if [ "${DEB_FILE}" = "/tmp/${APP_NAME}_latest.deb" ]; then
    rm -f "${DEB_FILE}"
fi

echo "🎉 Update complete!"
