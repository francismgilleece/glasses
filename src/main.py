#!/usr/bin/env python3
"""
Wearable Companion Device - Main Controller
Entry point for the modular wearable companion device.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src directory to path for imports
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from display.display_controller import DisplayController
from config.settings_manager import SettingsManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WearableDevice:
    """Main controller for the wearable companion device."""
    
    def __init__(self):
        self.settings = SettingsManager()
        self.display = None
        self.running = False
    
    async def initialize(self):
        """Initialize all device components."""
        logger.info("Initializing wearable device...")
        
        try:
            # Initialize display
            self.display = DisplayController(self.settings.get_display_config())
            await self.display.initialize()
            logger.info("Display initialized successfully")
            
            # Show startup message
            await self.display.show_text("Wearable Device\nStarting...", duration=2)
            
        except Exception as e:
            logger.error(f"Failed to initialize device: {e}")
            raise
    
    async def run(self):
        """Main device event loop."""
        self.running = True
        logger.info("Starting main event loop...")
        
        try:
            while self.running:
                # Simple demo: cycle through different display modes
                await self.display.show_text("Hello World!", duration=3)
                await self.display.show_time(duration=3)
                await self.display.show_text("Ready for\nintegration", duration=3)
                
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutdown requested")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Clean shutdown of all components."""
        logger.info("Shutting down device...")
        self.running = False
        
        if self.display:
            await self.display.clear()
            await self.display.shutdown()
        
        logger.info("Device shutdown complete")


async def main():
    """Main entry point."""
    device = WearableDevice()
    
    try:
        await device.initialize()
        await device.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 