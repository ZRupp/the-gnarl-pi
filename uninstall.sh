#!/bin/bash
# The Gnarl Pi Uninstallation Script
# Run with: sudo ./uninstall.sh

set -e

echo "========================================"
echo "  The Gnarl Pi - Uninstall Script"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: Please run as root (sudo ./uninstall.sh)"
    exit 1
fi

# Uninstall Python package
echo "[1/3] Uninstalling Python package..."
pip3 uninstall -y the-gnarl-pi || echo "Package not installed via pip"

# Remove systemd service if exists
echo "[2/3] Removing systemd services..."
if [ -f /etc/systemd/system/cpu-governor.service ]; then
    systemctl disable cpu-governor.service || true
    rm -f /etc/systemd/system/cpu-governor.service
    systemctl daemon-reload
fi

# Ask about config removal
echo "[3/3] Configuration cleanup..."
if [ -d /etc/gnarl ]; then
    read -p "Remove configuration directory /etc/gnarl? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf /etc/gnarl
        echo "Configuration removed"
    else
        echo "Configuration kept at /etc/gnarl"
    fi
fi

echo ""
echo "========================================"
echo "  Uninstallation Complete"
echo "========================================"
echo ""
echo "Note: System packages (JACK, I2C tools, etc.) were not removed."
echo "To remove them manually:"
echo "  sudo apt-get remove jackd2 i2c-tools"
echo ""
