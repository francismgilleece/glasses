"""
Settings Manager - Configuration and User Preferences
Handles device settings, user preferences, and configuration management.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DisplayConfig(BaseModel):
    """Display configuration settings."""
    interface: str = Field(default="i2c", description="Interface type: i2c or spi")
    brightness: int = Field(default=255, ge=0, le=255, description="Display brightness (0-255)")
    rotation: int = Field(default=0, description="Display rotation in degrees")
    width: int = Field(default=128, description="Display width in pixels")
    height: int = Field(default=64, description="Display height in pixels")
    i2c_address: str = Field(default="0x3C", description="I2C address for display")
    i2c_port: int = Field(default=1, description="I2C port number")


class DeviceConfig(BaseModel):
    """Device hardware configuration."""
    device_name: str = Field(default="WearableCompanion", description="Device name")
    gpio_pins: Dict[str, int] = Field(default_factory=dict, description="GPIO pin assignments")
    power_management: Dict[str, Any] = Field(default_factory=dict, description="Power settings")


class UserPreferences(BaseModel):
    """User preference settings."""
    time_format_12h: bool = Field(default=True, description="Use 12-hour time format")
    default_brightness: int = Field(default=200, ge=0, le=255, description="Default display brightness")
    notification_duration: float = Field(default=5.0, description="Default notification display time")
    auto_dim_timeout: float = Field(default=30.0, description="Seconds before auto-dimming")
    sleep_timeout: float = Field(default=300.0, description="Seconds before sleep mode")


class SettingsManager:
    """Manages device configuration and user preferences."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        # Set default config directory
        if config_dir is None:
            # Use project root/config directory
            project_root = Path(__file__).parent.parent.parent
            config_dir = project_root / "config"
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration file paths
        self.device_config_path = self.config_dir / "device_config.yaml"
        self.user_prefs_path = self.config_dir / "user_preferences.yaml"
        self.default_settings_path = self.config_dir / "default_settings.yaml"
        
        # Load configurations
        self.display_config = DisplayConfig()
        self.device_config = DeviceConfig()
        self.user_preferences = UserPreferences()
        
        self._load_configurations()
    
    def _load_configurations(self):
        """Load all configuration files."""
        try:
            # Load default settings first
            self._load_default_settings()
            
            # Load device configuration
            self._load_device_config()
            
            # Load user preferences
            self._load_user_preferences()
            
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using default configuration")
            self._create_default_configs()
    
    def _load_default_settings(self):
        """Load default settings from file."""
        if self.default_settings_path.exists():
            try:
                with open(self.default_settings_path, 'r') as f:
                    defaults = yaml.safe_load(f)
                    
                if defaults:
                    # Update display config with defaults
                    if 'display' in defaults:
                        self.display_config = DisplayConfig(**defaults['display'])
                    
                    # Update device config with defaults
                    if 'device' in defaults:
                        self.device_config = DeviceConfig(**defaults['device'])
                    
                    # Update user preferences with defaults
                    if 'user_preferences' in defaults:
                        self.user_preferences = UserPreferences(**defaults['user_preferences'])
                        
            except Exception as e:
                logger.warning(f"Failed to load default settings: {e}")
    
    def _load_device_config(self):
        """Load device-specific configuration."""
        if self.device_config_path.exists():
            try:
                with open(self.device_config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                    
                if config_data:
                    self.device_config = DeviceConfig(**config_data)
                    
            except Exception as e:
                logger.warning(f"Failed to load device config: {e}")
    
    def _load_user_preferences(self):
        """Load user preferences."""
        if self.user_prefs_path.exists():
            try:
                with open(self.user_prefs_path, 'r') as f:
                    prefs_data = yaml.safe_load(f)
                    
                if prefs_data:
                    self.user_preferences = UserPreferences(**prefs_data)
                    
            except Exception as e:
                logger.warning(f"Failed to load user preferences: {e}")
    
    def _create_default_configs(self):
        """Create default configuration files."""
        try:
            # Create default settings file
            default_settings = {
                'display': self.display_config.model_dump(),
                'device': self.device_config.model_dump(),
                'user_preferences': self.user_preferences.model_dump()
            }
            
            with open(self.default_settings_path, 'w') as f:
                yaml.dump(default_settings, f, default_flow_style=False, indent=2)
            
            # Create device config file
            with open(self.device_config_path, 'w') as f:
                yaml.dump(self.device_config.model_dump(), f, default_flow_style=False, indent=2)
            
            # Create user preferences file
            with open(self.user_prefs_path, 'w') as f:
                yaml.dump(self.user_preferences.model_dump(), f, default_flow_style=False, indent=2)
            
            logger.info("Default configuration files created")
            
        except Exception as e:
            logger.error(f"Failed to create default configs: {e}")
    
    def get_display_config(self) -> Dict[str, Any]:
        """Get display configuration as dictionary."""
        return self.display_config.model_dump()
    
    def get_device_config(self) -> Dict[str, Any]:
        """Get device configuration as dictionary."""
        return self.device_config.model_dump()
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences as dictionary."""
        return self.user_preferences.model_dump()
    
    def update_display_config(self, **kwargs):
        """Update display configuration settings."""
        try:
            # Update the model with new values
            updated_data = {**self.display_config.model_dump(), **kwargs}
            self.display_config = DisplayConfig(**updated_data)
            
            # Save to file
            self._save_device_config()
            logger.info(f"Display config updated: {kwargs}")
            
        except Exception as e:
            logger.error(f"Failed to update display config: {e}")
            raise
    
    def update_user_preferences(self, **kwargs):
        """Update user preferences."""
        try:
            # Update the model with new values
            updated_data = {**self.user_preferences.model_dump(), **kwargs}
            self.user_preferences = UserPreferences(**updated_data)
            
            # Save to file
            self._save_user_preferences()
            logger.info(f"User preferences updated: {kwargs}")
            
        except Exception as e:
            logger.error(f"Failed to update user preferences: {e}")
            raise
    
    def _save_device_config(self):
        """Save device configuration to file."""
        try:
            with open(self.device_config_path, 'w') as f:
                yaml.dump(self.device_config.model_dump(), f, default_flow_style=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save device config: {e}")
            raise
    
    def _save_user_preferences(self):
        """Save user preferences to file."""
        try:
            with open(self.user_prefs_path, 'w') as f:
                yaml.dump(self.user_preferences.model_dump(), f, default_flow_style=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save user preferences: {e}")
            raise
    
    def get_setting(self, category: str, key: str, default=None):
        """Get a specific setting value."""
        try:
            if category == "display":
                return getattr(self.display_config, key, default)
            elif category == "device":
                return getattr(self.device_config, key, default)
            elif category == "user":
                return getattr(self.user_preferences, key, default)
            else:
                logger.warning(f"Unknown settings category: {category}")
                return default
        except AttributeError:
            logger.warning(f"Setting not found: {category}.{key}")
            return default
    
    def set_setting(self, category: str, key: str, value):
        """Set a specific setting value."""
        try:
            if category == "display":
                setattr(self.display_config, key, value)
                self._save_device_config()
            elif category == "device":
                setattr(self.device_config, key, value)
                self._save_device_config()
            elif category == "user":
                setattr(self.user_preferences, key, value)
                self._save_user_preferences()
            else:
                raise ValueError(f"Unknown settings category: {category}")
                
            logger.info(f"Setting updated: {category}.{key} = {value}")
            
        except Exception as e:
            logger.error(f"Failed to set setting {category}.{key}: {e}")
            raise
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        logger.info("Resetting all settings to defaults")
        
        self.display_config = DisplayConfig()
        self.device_config = DeviceConfig()
        self.user_preferences = UserPreferences()
        
        self._create_default_configs()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of all current configuration."""
        return {
            "display": self.display_config.model_dump(),
            "device": self.device_config.model_dump(),
            "user_preferences": self.user_preferences.model_dump(),
            "config_files": {
                "device_config": str(self.device_config_path),
                "user_preferences": str(self.user_prefs_path),
                "default_settings": str(self.default_settings_path)
            }
        } 