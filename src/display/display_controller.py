"""
Display Controller - Core OLED Display Management
Handles communication with the 128x64px transparent OLED display.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Tuple
from pathlib import Path

try:
    from luma.core.interface.serial import i2c, spi
    from luma.core.render import canvas
    from luma.oled.device import ssd1306
    from PIL import Image, ImageDraw, ImageFont
    import RPi.GPIO as GPIO
except ImportError as e:
    # For development on non-Pi systems
    logging.warning(f"Hardware libraries not available: {e}")
    ssd1306 = None
    GPIO = None

logger = logging.getLogger(__name__)


class DisplayController:
    """Controls the OLED display with async support and multiple display modes."""
    
    def __init__(self, config: dict):
        self.config = config
        self.device = None
        self.width = 128
        self.height = 64
        self.font_small = None
        self.font_medium = None
        self.font_large = None
        self.current_task = None
        
        # Display state
        self.brightness = config.get('brightness', 255)
        self.rotation = config.get('rotation', 0)
        self.interface_type = config.get('interface', 'i2c')  # 'i2c' or 'spi'
        
    async def initialize(self):
        """Initialize the OLED display and load fonts."""
        logger.info("Initializing OLED display...")
        
        try:
            # Initialize interface based on configuration
            if self.interface_type == 'i2c':
                i2c_port = self.config.get('i2c_port', 1)
                i2c_address = int(self.config.get('i2c_address', '0x3C'), 16)
                serial = i2c(port=i2c_port, address=i2c_address)
                logger.info(f"I2C interface: port={i2c_port}, address=0x{i2c_address:02X}")
                
            elif self.interface_type == 'spi':
                spi_device = self.config.get('spi_device', 0)
                spi_port = self.config.get('spi_port', 0)
                dc_pin = self.config.get('spi_dc_pin', 24)
                rst_pin = self.config.get('spi_rst_pin', 25)
                cs_pin = self.config.get('spi_cs_pin', 8)
                
                serial = spi(device=spi_device, port=spi_port, 
                           gpio_DC=dc_pin, gpio_RST=rst_pin, gpio_CS=cs_pin)
                logger.info(f"SPI interface: device={spi_device}, port={spi_port}, DC={dc_pin}, RST={rst_pin}, CS={cs_pin}")
                
            else:
                raise ValueError(f"Unsupported interface: {self.interface_type}")
            
            # Initialize the OLED device
            self.device = ssd1306(serial, width=self.width, height=self.height, rotate=self.rotation)
            
            # Set brightness
            self.device.contrast(self.brightness)
            
            # Load fonts
            await self._load_fonts()
            
            # Clear display
            await self.clear()
            
            logger.info(f"Display initialized: {self.width}x{self.height}, interface: {self.interface_type}")
            
        except Exception as e:
            if ssd1306 is None:
                logger.warning("Running in development mode - display simulation enabled")
                await self._setup_simulation_mode()
            else:
                logger.error(f"Failed to initialize display: {e}")
                raise
    
    async def _setup_simulation_mode(self):
        """Setup simulation mode for development without hardware."""
        logger.info("Setting up display simulation mode")
        self.device = None  # Will be handled by simulation methods
        
        # Create mock fonts
        class MockFont:
            def getbbox(self, text):
                return (0, 0, len(text) * 6, 10)
        
        self.font_small = MockFont()
        self.font_medium = MockFont()
        self.font_large = MockFont()
    
    async def _load_fonts(self):
        """Load fonts for different text sizes."""
        try:
            # Try to load system fonts, fall back to PIL defaults
            fonts_dir = Path("/usr/share/fonts/truetype/dejavu")
            if fonts_dir.exists():
                font_path = fonts_dir / "DejaVuSans.ttf"
                self.font_small = ImageFont.truetype(str(font_path), 10)
                self.font_medium = ImageFont.truetype(str(font_path), 12)
                self.font_large = ImageFont.truetype(str(font_path), 16)
            else:
                # Use PIL default fonts
                self.font_small = ImageFont.load_default()
                self.font_medium = ImageFont.load_default()
                self.font_large = ImageFont.load_default()
                
            logger.info("Fonts loaded successfully")
            
        except Exception as e:
            logger.warning(f"Font loading failed, using defaults: {e}")
            # Fallback to default font
            default_font = ImageFont.load_default()
            self.font_small = default_font
            self.font_medium = default_font
            self.font_large = default_font
    
    async def clear(self):
        """Clear the display."""
        if self.device:
            with canvas(self.device) as draw:
                draw.rectangle(self.device.bounding_box, outline=0, fill=0)
        else:
            logger.info("[SIM] Display cleared")
    
    async def show_text(self, text: str, font_size: str = "medium", 
                       position: Tuple[int, int] = None, duration: float = None,
                       center: bool = True):
        """
        Display text on the OLED screen.
        
        Args:
            text: Text to display (supports \n for line breaks)
            font_size: "small", "medium", or "large"
            position: (x, y) position, None for center
            duration: How long to show text (seconds), None for permanent
            center: Whether to center the text
        """
        # Cancel any current display task
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
        
        if duration:
            self.current_task = asyncio.create_task(
                self._show_text_with_duration(text, font_size, position, duration, center)
            )
        else:
            await self._render_text(text, font_size, position, center)
    
    async def _show_text_with_duration(self, text: str, font_size: str, 
                                     position: Tuple[int, int], duration: float, center: bool):
        """Show text for a specific duration."""
        await self._render_text(text, font_size, position, center)
        await asyncio.sleep(duration)
        await self.clear()
    
    async def _render_text(self, text: str, font_size: str, 
                          position: Tuple[int, int], center: bool):
        """Render text to the display."""
        # Select font
        font_map = {
            "small": self.font_small,
            "medium": self.font_medium,
            "large": self.font_large
        }
        font = font_map.get(font_size, self.font_medium)
        
        if self.device:
            with canvas(self.device) as draw:
                self._draw_text(draw, text, font, position, center)
        else:
            # Simulation mode
            logger.info(f"[SIM] Display text ({font_size}): {repr(text)}")
    
    def _draw_text(self, draw, text: str, font, position: Tuple[int, int], center: bool):
        """Helper to draw text with proper positioning."""
        lines = text.split('\n')
        
        if center and position is None:
            # Calculate center position for multi-line text
            total_height = len(lines) * 15  # Approximate line height
            start_y = (self.height - total_height) // 2
            
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                y = start_y + (i * 15)
                draw.text((x, y), line, font=font, fill=255)
        else:
            # Use specified position or top-left
            x, y = position if position else (0, 0)
            for i, line in enumerate(lines):
                draw.text((x, y + i * 15), line, font=font, fill=255)
    
    async def show_time(self, format_12h: bool = True, duration: float = None):
        """Display current time."""
        now = datetime.now()
        if format_12h:
            time_str = now.strftime("%I:%M %p")
        else:
            time_str = now.strftime("%H:%M")
        
        date_str = now.strftime("%m/%d/%Y")
        display_text = f"{time_str}\n{date_str}"
        
        await self.show_text(display_text, font_size="medium", duration=duration)
    
    async def show_status(self, status: str, details: str = None, duration: float = 3):
        """Show system status information."""
        if details:
            text = f"{status}\n{details}"
        else:
            text = status
        
        await self.show_text(text, font_size="small", duration=duration)
    
    async def show_notification(self, title: str, message: str, duration: float = 5):
        """Display a notification with title and message."""
        text = f"{title}\n{message}"
        await self.show_text(text, font_size="small", duration=duration)
    
    async def set_brightness(self, brightness: int):
        """Set display brightness (0-255)."""
        self.brightness = max(0, min(255, brightness))
        if self.device:
            self.device.contrast(self.brightness)
        logger.info(f"Display brightness set to {self.brightness}")
    
    async def show_progress_bar(self, progress: float, label: str = "Progress", duration: float = None):
        """
        Show a progress bar.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            label: Label to show above progress bar
            duration: How long to show (None for permanent)
        """
        if self.device:
            with canvas(self.device) as draw:
                # Draw label
                draw.text((10, 10), label, font=self.font_small, fill=255)
                
                # Draw progress bar outline
                bar_x, bar_y = 10, 30
                bar_width, bar_height = 108, 10
                draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], 
                             outline=255, fill=0)
                
                # Draw progress fill
                fill_width = int(bar_width * progress)
                if fill_width > 0:
                    draw.rectangle([bar_x, bar_y, bar_x + fill_width, bar_y + bar_height], 
                                 outline=255, fill=255)
                
                # Draw percentage
                pct_text = f"{int(progress * 100)}%"
                bbox = draw.textbbox((0, 0), pct_text, font=self.font_small)
                text_width = bbox[2] - bbox[0]
                text_x = (self.width - text_width) // 2
                draw.text((text_x, 45), pct_text, font=self.font_small, fill=255)
        else:
            logger.info(f"[SIM] Progress bar: {label} - {int(progress * 100)}%")
        
        if duration:
            await asyncio.sleep(duration)
            await self.clear()
    
    async def shutdown(self):
        """Clean shutdown of the display."""
        logger.info("Shutting down display...")
        
        # Cancel any running tasks
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
        
        await self.clear()
        
        # Cleanup GPIO if available
        if GPIO:
            GPIO.cleanup()
        
        logger.info("Display shutdown complete") 