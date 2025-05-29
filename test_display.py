#!/usr/bin/env python3
"""
Test script for the display controller.
Can be run on any system to test the display functionality in simulation mode.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from display.display_controller import DisplayController
from config.settings_manager import SettingsManager


async def test_display():
    """Test the display controller functionality."""
    print("Testing Wearable Device Display Controller")
    print("=" * 50)
    
    # Initialize settings manager
    settings = SettingsManager()
    print(f"✓ Settings loaded")
    
    # Initialize display controller
    display = DisplayController(settings.get_display_config())
    await display.initialize()
    print(f"✓ Display initialized")
    
    # Test basic text display
    print("\n1. Testing basic text display...")
    await display.show_text("Hello World!", duration=2)
    await asyncio.sleep(2.5)
    
    # Test multi-line text
    print("2. Testing multi-line text...")
    await display.show_text("Wearable\nCompanion\nDevice", duration=2)
    await asyncio.sleep(2.5)
    
    # Test time display
    print("3. Testing time display...")
    await display.show_time(duration=2)
    await asyncio.sleep(2.5)
    
    # Test notification
    print("4. Testing notification...")
    await display.show_notification("Test Alert", "This is a test notification", duration=2)
    await asyncio.sleep(2.5)
    
    # Test status display
    print("5. Testing status display...")
    await display.show_status("System Ready", "All modules loaded", duration=2)
    await asyncio.sleep(2.5)
    
    # Test progress bar
    print("6. Testing progress bar...")
    for i in range(11):
        progress = i / 10.0
        await display.show_progress_bar(progress, "Loading", duration=0.3)
        await asyncio.sleep(0.3)
    
    # Test brightness adjustment
    print("7. Testing brightness adjustment...")
    await display.set_brightness(128)
    await display.show_text("50% Brightness", duration=1)
    await asyncio.sleep(1.5)
    
    await display.set_brightness(255)
    await display.show_text("100% Brightness", duration=1)
    await asyncio.sleep(1.5)
    
    # Final message
    await display.show_text("Test Complete!", duration=2)
    await asyncio.sleep(2.5)
    
    # Shutdown
    await display.shutdown()
    print("\n✓ Display test completed successfully!")
    print("\nThe display controller is ready for hardware integration.")


if __name__ == "__main__":
    try:
        asyncio.run(test_display())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed: {e}")
        sys.exit(1) 