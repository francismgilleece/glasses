#!/usr/bin/env python3
"""
Device Test Script - OLED Display on Raspberry Pi
Optimized for testing the actual hardware on Raspberry Pi Zero 2W.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from display.display_controller import DisplayController
from config.settings_manager import SettingsManager


async def hardware_test():
    """Test display functionality on actual hardware."""
    print("🔧 Raspberry Pi OLED Display Test")
    print("=" * 50)
    
    # Initialize settings with device-specific config
    settings = SettingsManager()
    
    # Override with hardware-specific settings if needed
    display_config = settings.get_display_config()
    print(f"📊 Display config: {display_config}")
    
    try:
        # Initialize display controller
        print("\n🔌 Initializing OLED display...")
        display = DisplayController(display_config)
        await display.initialize()
        print("✅ Display initialized successfully!")
        
        # Test 1: Basic connectivity
        print("\n1️⃣ Testing basic connectivity...")
        await display.clear()
        await display.show_text("Hardware Test\nStarting...", duration=2)
        await asyncio.sleep(2.5)
        
        # Test 2: Text rendering
        print("2️⃣ Testing text rendering...")
        await display.show_text("Hello Pi Zero!", font_size="large", duration=2)
        await asyncio.sleep(2.5)
        
        # Test 3: Multi-line text
        print("3️⃣ Testing multi-line text...")
        await display.show_text("Line 1\nLine 2\nLine 3", font_size="small", duration=2)
        await asyncio.sleep(2.5)
        
        # Test 4: Time display
        print("4️⃣ Testing time display...")
        await display.show_time(duration=3)
        await asyncio.sleep(3.5)
        
        # Test 5: Brightness levels
        print("5️⃣ Testing brightness control...")
        for brightness in [64, 128, 255, 128]:
            await display.set_brightness(brightness)
            await display.show_text(f"Brightness\n{brightness}", duration=1.5)
            await asyncio.sleep(2)
        
        # Test 6: Progress bar
        print("6️⃣ Testing progress bar...")
        for i in range(11):
            progress = i / 10.0
            await display.show_progress_bar(progress, "Hardware Test", duration=0.5)
            await asyncio.sleep(0.5)
        
        # Test 7: Notification
        print("7️⃣ Testing notification...")
        await display.show_notification("Test Complete", "All tests passed!", duration=3)
        await asyncio.sleep(3.5)
        
        # Test 8: Rapid updates
        print("8️⃣ Testing rapid updates...")
        for i in range(5):
            await display.show_text(f"Update {i+1}", duration=0.5)
            await asyncio.sleep(0.7)
        
        # Final success message
        await display.show_text("🎉 SUCCESS!\nDisplay working", duration=3)
        await asyncio.sleep(3.5)
        
        print("\n✅ All hardware tests passed!")
        print("🎯 Display is ready for integration")
        
    except Exception as e:
        print(f"\n❌ Hardware test failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   - Check physical connections")
        print("   - Verify SPI is enabled: sudo raspi-config")
        print("   - Check SPI devices: ls -la /dev/spi*")
        print("   - Verify GPIO pins are connected correctly")
        print("   - Check permissions: sudo usermod -a -G gpio $USER")
        print("   - Ensure display is compatible with SSD1306")
        
        # Try to show error on display if partially working
        try:
            if 'display' in locals():
                await display.show_text("Hardware\nError", duration=2)
        except:
            pass
        
        raise
    
    finally:
        # Clean shutdown
        try:
            if 'display' in locals():
                await display.clear()
                await display.shutdown()
                print("🔌 Display shutdown complete")
        except Exception as e:
            print(f"⚠️  Shutdown warning: {e}")


async def quick_test():
    """Quick test to verify basic functionality."""
    print("⚡ Quick Display Test")
    print("=" * 30)
    
    try:
        settings = SettingsManager()
        display = DisplayController(settings.get_display_config())
        
        await display.initialize()
        await display.show_text("Quick Test\nOK", duration=2)
        await asyncio.sleep(2.5)
        await display.clear()
        await display.shutdown()
        
        print("✅ Quick test passed!")
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        raise


def check_system():
    """Check system requirements before running tests."""
    print("🔍 System Check")
    print("=" * 20)
    
    # Check if running on Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'Raspberry Pi' in cpuinfo:
                print("✅ Running on Raspberry Pi")
            else:
                print("⚠️  Not detected as Raspberry Pi")
    except:
        print("⚠️  Could not read CPU info")
    
    # Check for SPI
    spi_devices = ['/dev/spidev0.0', '/dev/spidev0.1', '/dev/spidev1.0', '/dev/spidev1.1']
    spi_found = any(Path(dev).exists() for dev in spi_devices)
    if spi_found:
        found_devices = [dev for dev in spi_devices if Path(dev).exists()]
        print(f"✅ SPI interface available: {', '.join(found_devices)}")
    else:
        print("❌ SPI not enabled - run 'sudo raspi-config'")
    
    # Check GPIO access
    gpio_path = Path('/dev/gpiomem')
    if gpio_path.exists():
        print("✅ GPIO access available")
    else:
        print("❌ GPIO access not available")
    
    # Check if SPI is enabled in config
    try:
        with open('/boot/config.txt', 'r') as f:
            config_content = f.read()
            if 'dtparam=spi=on' in config_content:
                print("✅ SPI enabled in /boot/config.txt")
            else:
                print("❌ SPI not enabled in /boot/config.txt")
    except:
        print("⚠️  Could not read /boot/config.txt")
    
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test OLED display on Raspberry Pi')
    parser.add_argument('--quick', action='store_true', help='Run quick test only')
    parser.add_argument('--check', action='store_true', help='Check system requirements only')
    args = parser.parse_args()
    
    try:
        if args.check:
            check_system()
        elif args.quick:
            asyncio.run(quick_test())
        else:
            check_system()
            asyncio.run(hardware_test())
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1) 