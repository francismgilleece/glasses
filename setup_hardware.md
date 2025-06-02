# Hardware Setup Guide - OLED Display on Raspberry Pi Zero 2W

## OLED Display Connection

### SPI Connection (Recommended)
Connect your 128x64 OLED display to the Raspberry Pi using SPI:

```
OLED Display    ->    Raspberry Pi Zero 2W
VCC             ->    3.3V (Pin 1 or 17)
GND             ->    Ground (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
DIN (MOSI)      ->    GPIO 10 (MOSI) (Pin 19)
CLK (SCLK)      ->    GPIO 11 (SCLK) (Pin 23)
CS              ->    GPIO 8 (CE0) (Pin 24)
DC              ->    GPIO 24 (Pin 18)
RST             ->    GPIO 25 (Pin 22)
```

**Pin Layout Reference:**
```
                    3V3  (1) (2)  5V
       GPIO 2 (SDA)     (3) (4)  5V
       GPIO 3 (SCL)     (5) (6)  GND
                    GPIO 4  (7) (8)  GPIO 14
                   GND  (9)(10)  GPIO 15
                  GPIO 17 (11)(12) GPIO 18
                  GPIO 27 (13)(14) GND
                  GPIO 22 (15)(16) GPIO 23
                    3V3 (17)(18) GPIO 24  <- DC
    GPIO 10 (MOSI)     (19)(20) GND
                  GPIO 9 (21)(22) GPIO 25  <- RST
    GPIO 11 (SCLK)     (23)(24) GPIO 8   <- CS
                   GND (25)(26) GPIO 7
```

### I2C Connection (Alternative)
If your display only supports I2C:

```
OLED Display    ->    Raspberry Pi Zero 2W
VCC             ->    3.3V (Pin 1 or 17)
GND             ->    Ground (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
SDA             ->    GPIO 2 (SDA) (Pin 3)
SCL             ->    GPIO 3 (SCL) (Pin 5)
```

## Enable SPI/I2C on Raspberry Pi

### Enable SPI (Default)
```bash
sudo raspi-config
# Navigate to: Interfacing Options -> SPI -> Enable
# Or edit /boot/config.txt and add:
# dtparam=spi=on
```

### Enable I2C (If needed)
```bash
sudo raspi-config
# Navigate to: Interfacing Options -> I2C -> Enable
# Or edit /boot/config.txt and add:
# dtparam=i2c_arm=on
```

### Verify SPI Connection
```bash
# Check SPI devices are available
ls -la /dev/spi*

# Should show: /dev/spidev0.0 and /dev/spidev0.1
```

### Verify I2C Connection (if using I2C)
```bash
# Install i2c tools
sudo apt-get install i2c-tools

# Scan for I2C devices (should show 0x3C for most OLED displays)
sudo i2cdetect -y 1
```

## Python Dependencies
Make sure all required libraries are installed:

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade

# Install Python dependencies
pip3 install -r requirements.txt

# If you get permission errors, use:
sudo pip3 install -r requirements.txt
```

## Configuration

### SPI Configuration (Default)
The device is configured to use SPI by default. To change SPI pins, edit the configuration:

```yaml
# config/default_settings.yaml
display:
  interface: "spi"
  spi_device: 0
  spi_port: 0
  spi_dc_pin: 24
  spi_rst_pin: 25
  spi_cs_pin: 8
```

### I2C Configuration
To switch to I2C, update the configuration:

```yaml
# config/default_settings.yaml
display:
  interface: "i2c"
  i2c_port: 1
  i2c_address: "0x3C"
```

## Common OLED Display Models

### SSD1306 (Most Common)
- 128x64 pixels
- Supports both SPI and I2C
- I2C address: 0x3C (default) or 0x3D
- Fully supported by luma.oled library

### SH1106 (Alternative)
- 128x64 pixels
- Slightly different controller
- Also supported by luma.oled

## Troubleshooting

### SPI Display Not Working
1. Check physical connections (7 wires for SPI)
2. Verify SPI is enabled: `sudo raspi-config`
3. Check SPI devices exist: `ls -la /dev/spi*`
4. Verify GPIO pins are correct
5. Check power supply (3.3V, not 5V for most displays)
6. Ensure all ground connections are secure

### I2C Display Not Working
1. Check physical connections (4 wires for I2C)
2. Verify I2C is enabled: `sudo raspi-config`
3. Check I2C address: `sudo i2cdetect -y 1`
4. Try different I2C address (0x3D instead of 0x3C)
5. Check power supply (3.3V, not 5V for most displays)

### Permission Errors
```bash
# Add user to gpio group for SPI
sudo usermod -a -G gpio $USER

# Add user to i2c group for I2C
sudo usermod -a -G i2c $USER

# Reboot after adding to groups
sudo reboot
```

### GPIO Already in Use
```bash
# Check what's using GPIO
sudo fuser /dev/gpiomem

# Kill processes if needed
sudo pkill -f python
```

## Wiring Double-Check

### SPI Wiring Checklist
- [ ] VCC to 3.3V (Pin 1)
- [ ] GND to Ground (Pin 6)
- [ ] DIN to GPIO 10/MOSI (Pin 19)
- [ ] CLK to GPIO 11/SCLK (Pin 23)
- [ ] CS to GPIO 8/CE0 (Pin 24)
- [ ] DC to GPIO 24 (Pin 18)
- [ ] RST to GPIO 25 (Pin 22)

### I2C Wiring Checklist
- [ ] VCC to 3.3V (Pin 1)
- [ ] GND to Ground (Pin 6)
- [ ] SDA to GPIO 2 (Pin 3)
- [ ] SCL to GPIO 3 (Pin 5) 