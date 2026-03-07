#!/bin/sh
# Install script for Marco file explorer
# Run via: curl -sSL https://raw.githubusercontent.com/falktimon/marco/main/install.sh | sh

set -e

REPO_URL="https://raw.githubusercontent.com/falktimon/marco/main"
PREFIX="${PREFIX:-/usr/local}"
BINDIR="$PREFIX/bin"

echo "Installing Marco file explorer..."

# Detect if we need sudo
SUDO=""
if [ ! -w "$BINDIR" ]; then
    SUDO="sudo"
fi

# Download marco.py
echo "Downloading marco.py..."
$SUDO mkdir -p "$BINDIR"
if command -v curl > /dev/null 2>&1; then
    $SUDO curl -sSL "$REPO_URL/marco.py" -o "$BINDIR/marco"
elif command -v wget > /dev/null 2>&1; then
    $SUDO wget -q "$REPO_URL/marco.py" -O "$BINDIR/marco"
else
    echo "Error: curl or wget required" >&2
    exit 1
fi

# Make executable
$SUDO chmod +x "$BINDIR/marco"

# Create example config directory
CONFIG_DIR="$HOME/.config/marco"
mkdir -p "$CONFIG_DIR"

# Download example config if it doesn't exist
if [ ! -f "$CONFIG_DIR/marco.toml" ]; then
    echo "Downloading example config..."
    if command -v curl > /dev/null 2>&1; then
        curl -sSL "$REPO_URL/marco.toml.example" -o "$CONFIG_DIR/marco.toml.example"
    elif command -v wget > /dev/null 2>&1; then
        wget -q "$REPO_URL/marco.toml.example" -O "$CONFIG_DIR/marco.toml.example"
    fi
fi

echo ""
echo "Installation complete!"
echo "marco installed to: $BINDIR/marco"
echo ""
echo "Usage: marco"
echo ""
echo "To customize, edit: $CONFIG_DIR/marco.toml"
echo "Example config: $CONFIG_DIR/marco.toml.example"