"""
Base Input Module - Abstract Interface for Data Sources
Provides a consistent interface for all input modules.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class InputData:
    """Container for data from input sources."""
    
    def __init__(self, source: str, data_type: str, content: Any, 
                 timestamp: Optional[datetime] = None, priority: int = 5,
                 expires_at: Optional[datetime] = None):
        self.source = source
        self.data_type = data_type  # 'text', 'notification', 'status', 'time', etc.
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.priority = priority  # 1-10, lower = higher priority
        self.expires_at = expires_at
        self.id = f"{source}_{data_type}_{int(self.timestamp.timestamp())}"
    
    def is_expired(self) -> bool:
        """Check if this data has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'source': self.source,
            'data_type': self.data_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }


class BaseInput(ABC):
    """Abstract base class for all input modules."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.enabled = config.get('enabled', True)
        self.update_interval = config.get('update_interval', 60)  # seconds
        self.running = False
        self.last_update = None
        self.error_count = 0
        self.max_errors = config.get('max_errors', 5)
        
        # Data cache
        self.current_data: List[InputData] = []
        self.data_listeners = []
    
    async def initialize(self):
        """Initialize the input module."""
        logger.info(f"Initializing input module: {self.name}")
        try:
            await self._initialize()
            logger.info(f"Input module {self.name} initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize {self.name}: {e}")
            raise
    
    @abstractmethod
    async def _initialize(self):
        """Module-specific initialization. Override in subclasses."""
        pass
    
    async def start(self):
        """Start the input module data collection."""
        if not self.enabled:
            logger.info(f"Input module {self.name} is disabled")
            return
        
        logger.info(f"Starting input module: {self.name}")
        self.running = True
        
        # Start the update loop
        asyncio.create_task(self._update_loop())
    
    async def stop(self):
        """Stop the input module."""
        logger.info(f"Stopping input module: {self.name}")
        self.running = False
        await self._cleanup()
    
    async def _update_loop(self):
        """Main update loop for the input module."""
        while self.running:
            try:
                # Check if it's time for an update
                if self._should_update():
                    await self._fetch_data()
                    self.last_update = datetime.now()
                    self.error_count = 0  # Reset error count on successful update
                
                # Clean expired data
                self._clean_expired_data()
                
                # Wait before next update
                await asyncio.sleep(min(self.update_interval, 10))
                
            except Exception as e:
                self.error_count += 1
                logger.error(f"Error in {self.name} update loop: {e}")
                
                if self.error_count >= self.max_errors:
                    logger.error(f"Max errors reached for {self.name}, stopping")
                    self.running = False
                    break
                
                # Wait longer after errors
                await asyncio.sleep(30)
    
    def _should_update(self) -> bool:
        """Check if it's time for an update."""
        if self.last_update is None:
            return True
        
        time_since_update = datetime.now() - self.last_update
        return time_since_update.total_seconds() >= self.update_interval
    
    @abstractmethod
    async def _fetch_data(self):
        """Fetch data from the input source. Override in subclasses."""
        pass
    
    async def _cleanup(self):
        """Clean up resources. Override in subclasses if needed."""
        pass
    
    def _clean_expired_data(self):
        """Remove expired data from cache."""
        self.current_data = [data for data in self.current_data if not data.is_expired()]
    
    def add_data(self, data: InputData):
        """Add new data to the module."""
        # Remove old data of the same type from the same source
        self.current_data = [d for d in self.current_data 
                           if not (d.source == data.source and d.data_type == data.data_type)]
        
        # Add new data
        self.current_data.append(data)
        
        # Notify listeners
        self._notify_listeners(data)
    
    def get_current_data(self, data_type: Optional[str] = None) -> List[InputData]:
        """Get current data, optionally filtered by type."""
        if data_type:
            return [data for data in self.current_data if data.data_type == data_type]
        return self.current_data.copy()
    
    def get_latest_data(self, data_type: str) -> Optional[InputData]:
        """Get the most recent data of a specific type."""
        filtered_data = self.get_current_data(data_type)
        if not filtered_data:
            return None
        
        return max(filtered_data, key=lambda x: x.timestamp)
    
    def add_data_listener(self, callback):
        """Add a callback function to be notified of new data."""
        self.data_listeners.append(callback)
    
    def _notify_listeners(self, data: InputData):
        """Notify all listeners of new data."""
        for callback in self.data_listeners:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(data))
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Error notifying listener in {self.name}: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get module status information."""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'running': self.running,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'error_count': self.error_count,
            'data_count': len(self.current_data),
            'update_interval': self.update_interval
        } 