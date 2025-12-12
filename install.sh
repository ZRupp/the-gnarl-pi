#!/bin/bash
# The Gnarl Pi Installation Script
# Run with: sudo ./install.sh

set -e

echo "========================================"
echo "  The Gnarl Pi - Installation Script"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: Please run as root (sudo ./install.sh)"
    exit 1
fi

# Get the actual user (not root)
ACTUAL_USER="${SUDO_USER:-$USER}"
ACTUAL_HOME=$(getent passwd "$ACTUAL_USER" | cut -d: -f6)

echo "Installing for user: $ACTUAL_USER"
echo "Home directory: $ACTUAL_HOME"
echo ""

# Update package list
echo "[1/8] Updating package list..."
apt-get update

# Install system dependencies
echo "[2/8] Installing system dependencies..."
apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    libasound2-dev \
    libjack-dev \
    jackd2 \
    i2c-tools \
    git

# Optional: Install ZynAddSubFX
read -p "Install ZynAddSubFX synth engine? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing ZynAddSubFX..."
    apt-get install -y zynaddsubfx
fi

# Enable I2C and SPI
echo "[3/8] Enabling I2C and SPI interfaces..."
raspi-config nonint do_i2c 0
raspi-config nonint do_spi 0

# Add user to required groups
echo "[4/8] Adding user to gpio, i2c, spi, audio groups..."
usermod -a -G gpio,i2c,spi,audio "$ACTUAL_USER"

# Install Python package
echo "[5/8] Installing Python package..."
pip3 install -e .

# Create config directory
echo "[6/8] Setting up configuration..."
mkdir -p /etc/gnarl
if [ ! -f /etc/gnarl/config.yaml ]; then
    cp config/default.yaml /etc/gnarl/config.yaml
    echo "Created default config at /etc/gnarl/config.yaml"
else
    echo "Config already exists at /etc/gnarl/config.yaml (not overwriting)"
fi
chown -R "$ACTUAL_USER:$ACTUAL_USER" /etc/gnarl

# Configure JACK for low latency
echo "[7/8] Configuring JACK audio..."
mkdir -p "$ACTUAL_HOME/.config/jack"
cat > "$ACTUAL_HOME/.config/jack/jackdrc" << 'EOF'
/usr/bin/jackd -dalsa -dhw:1 -r48000 -p128 -n2 -Xseq
EOF
chown "$ACTUAL_USER:$ACTUAL_USER" "$ACTUAL_HOME/.config/jack/jackdrc"

# Set up real-time audio permissions
if ! grep -q "@audio.*rtprio" /etc/security/limits.conf; then
    echo "@audio - rtprio 95" >> /etc/security/limits.conf
    echo "@audio - memlock unlimited" >> /etc/security/limits.conf
fi

# Set CPU governor to performance
echo "[8/8] Setting CPU governor to performance..."
cat > /etc/systemd/system/cpu-governor.service << 'EOF'
[Unit]
Description=Set CPU governor to performance

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor'

[Install]
WantedBy=multi-user.target
EOF
systemctl enable cpu-governor.service

echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Reboot to apply group membership changes"
echo "2. Connect your hardware (see docs/HARDWARE.md)"
echo "3. Edit /etc/gnarl/config.yaml with your pin assignments"
echo "4. Find your LCD I2C address: i2cdetect -y 1"
echo "5. Test hardware: gnarl test-hardware"
echo "6. Run the synth: gnarl run"
echo ""
echo "IMPORTANT: You must reboot for changes to take effect!"
read -p "Reboot now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    reboot
fi
