#!/bin/bash
# Setup script for Wearable Companion Device on Raspberry Pi Zero 2W
# Configured for SPI OLED Display

echo "🔧 Setting up Wearable Companion Device on Raspberry Pi (SPI Display)"
echo "====================================================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    git \
    vim

# Enable SPI
echo "🔌 Enabling SPI interface..."
if ! grep -q "dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    echo "✅ SPI enabled in /boot/config.txt"
else
    echo "✅ SPI already enabled"
fi

# Add user to spi group (if exists)
echo "👤 Adding user to spi group..."
if getent group spi > /dev/null 2>&1; then
    sudo usermod -a -G spi $USER
    echo "✅ User added to spi group"
else
    echo "ℹ️  No spi group found (this is normal)"
fi

# Add user to gpio group for GPIO access
echo "👤 Adding user to gpio group..."
if getent group gpio > /dev/null 2>&1; then
    sudo usermod -a -G gpio $USER
    echo "✅ User added to gpio group"
else
    echo "ℹ️  No gpio group found"
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --user
    echo "✅ Python dependencies installed"
else
    echo "⚠️  requirements.txt not found, installing key packages..."
    pip3 install --user \
        luma.oled \
        pillow \
        pydantic \
        pyyaml \
        structlog \
        aiohttp \
        requests
fi

# Create service file (optional)
echo "🔧 Creating systemd service (optional)..."
cat > /tmp/wearable-device.service << 'EOF'
[Unit]
Description=Wearable Companion Device
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/glasses-main
ExecStart=/usr/bin/python3 /home/pi/glasses-main/src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "📝 Service file created at /tmp/wearable-device.service"
echo "   To install: sudo cp /tmp/wearable-device.service /etc/systemd/system/"
echo "   To enable: sudo systemctl enable wearable-device.service"

# Check SPI
echo "🔍 Checking SPI setup..."
if [ -e "/dev/spidev0.0" ]; then
    echo "✅ SPI device found: /dev/spidev0.0"
elif [ -e "/dev/spidev0.1" ]; then
    echo "✅ SPI device found: /dev/spidev0.1"
else
    echo "❌ No SPI devices found - reboot may be required"
fi

# Check GPIO access
if [ -e "/dev/gpiomem" ]; then
    echo "✅ GPIO access available"
else
    echo "❌ GPIO access not available"
fi

# Set executable permissions
echo "🔐 Setting executable permissions..."
chmod +x test_display_device.py
chmod +x test_time_input.py
[ -f "src/main.py" ] && chmod +x src/main.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 SPI OLED Display Wiring:"
echo "   OLED VCC  -> Pi 3.3V (Pin 1)"
echo "   OLED GND  -> Pi Ground (Pin 6)"
echo "   OLED DIN  -> Pi GPIO 10/MOSI (Pin 19)"
echo "   OLED CLK  -> Pi GPIO 11/SCLK (Pin 23)"
echo "   OLED CS   -> Pi GPIO 8/CE0 (Pin 24)"
echo "   OLED DC   -> Pi GPIO 24 (Pin 18)"
echo "   OLED RST  -> Pi GPIO 25 (Pin 22)"
echo ""
echo "📋 Next steps:"
echo "   1. Reboot the Pi: sudo reboot"
echo "   2. Connect your OLED display using SPI pins (see wiring above)"
echo "   3. Test with: python3 test_display_device.py --check"
echo "   4. Run full test: python3 test_display_device.py"
echo ""
echo "🔧 If you have issues:"
echo "   - Check SPI devices: ls -la /dev/spi*"
echo "   - Verify SPI enabled: sudo raspi-config"
echo "   - Check GPIO access: ls -la /dev/gpio*"
echo "   - Check logs: journalctl -u wearable-device.service"

# Prompt for reboot
echo ""
read -p "🔄 Reboot now to apply SPI changes? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Rebooting..."
    sudo reboot
fi 