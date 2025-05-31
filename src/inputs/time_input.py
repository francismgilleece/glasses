"""
Time Input Module - System Time and Date Information
A simple input module that provides current time and date information.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from .base_input import BaseInput, InputData

logger = logging.getLogger(__name__)


class TimeInput(BaseInput):
    """Input module that provides current time and date information."""
    
    def __init__(self, config: Dict[str, Any]):
        # Set default configuration
        default_config = {
            'enabled': True,
            'update_interval': 30,  # Update every 30 seconds
            'format_12h': True,     # Use 12-hour format
            'include_seconds': False,
            'include_date': True,
            'timezone': 'local'     # Could be extended to support other timezones
        }
        default_config.update(config)
        
        super().__init__("time_input", default_config)
        
        self.format_12h = self.config.get('format_12h', True)
        self.include_seconds = self.config.get('include_seconds', False)
        self.include_date = self.config.get('include_date', True)
    
    async def _initialize(self):
        """Initialize the time input module."""
        logger.info("Time input module initialized")
        # No special initialization needed for time module
    
    async def _fetch_data(self):
        """Fetch current time and date information."""
        now = datetime.now()
        
        # Generate time string
        if self.format_12h:
            if self.include_seconds:
                time_str = now.strftime("%I:%M:%S %p")
            else:
                time_str = now.strftime("%I:%M %p")
        else:
            if self.include_seconds:
                time_str = now.strftime("%H:%M:%S")
            else:
                time_str = now.strftime("%H:%M")
        
        # Add time data
        time_data = InputData(
            source=self.name,
            data_type="time",
            content={
                "time_str": time_str,
                "hour": now.hour,
                "minute": now.minute,
                "second": now.second,
                "timestamp": now.isoformat()
            },
            priority=3,  # Medium priority
            expires_at=now + timedelta(minutes=2)  # Expires in 2 minutes
        )
        self.add_data(time_data)
        
        # Add date data if enabled
        if self.include_date:
            date_str = now.strftime("%B %d, %Y")  # "January 01, 2024"
            short_date = now.strftime("%m/%d/%Y")  # "01/01/2024"
            weekday = now.strftime("%A")  # "Monday"
            
            date_data = InputData(
                source=self.name,
                data_type="date",
                content={
                    "date_str": date_str,
                    "short_date": short_date,
                    "weekday": weekday,
                    "day": now.day,
                    "month": now.month,
                    "year": now.year,
                    "timestamp": now.isoformat()
                },
                priority=4,  # Lower priority than time
                expires_at=now + timedelta(hours=1)  # Expires in 1 hour
            )
            self.add_data(date_data)
        
        # Add combined time/date display data
        if self.include_date:
            display_text = f"{time_str}\n{short_date}"
        else:
            display_text = time_str
        
        display_data = InputData(
            source=self.name,
            data_type="display_time",
            content={
                "display_text": display_text,
                "time_str": time_str,
                "date_str": short_date if self.include_date else None
            },
            priority=2,  # High priority for display
            expires_at=now + timedelta(minutes=1)  # Expires quickly for display
        )
        self.add_data(display_data)
        
        logger.debug(f"Time data updated: {time_str}")
    
    def get_current_time_string(self) -> str:
        """Get the current time as a formatted string."""
        latest_time = self.get_latest_data("time")
        if latest_time:
            return latest_time.content["time_str"]
        return "No time data"
    
    def get_current_date_string(self) -> str:
        """Get the current date as a formatted string."""
        latest_date = self.get_latest_data("date")
        if latest_date:
            return latest_date.content["date_str"]
        return "No date data"
    
    def get_display_text(self) -> str:
        """Get formatted text ready for display."""
        latest_display = self.get_latest_data("display_time")
        if latest_display:
            return latest_display.content["display_text"]
        return "No time available"
    
    async def _cleanup(self):
        """Clean up time module resources."""
        logger.info("Time input module cleaned up")


# Factory function for easy instantiation
def create_time_input(config: Dict[str, Any] = None) -> TimeInput:
    """Create a time input module with optional configuration."""
    if config is None:
        config = {}
    
    return TimeInput(config) 