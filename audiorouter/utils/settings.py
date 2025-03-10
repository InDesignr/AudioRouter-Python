"""
Settings Module - Handles loading, saving, and managing application settings
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class Settings:
    """Handles application settings storage and retrieval"""
    
    def __init__(self, config_dir: str = None):
        """Initialize settings manager"""
        # Default config directory is ~/.audiorouter
        if config_dir is None:
            self.config_dir = Path.home() / ".audiorouter"
        else:
            self.config_dir = Path(config_dir)
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Config file for main settings
        self.config_file = self.config_dir / "config.json"
        
        # Presets directory
        self.presets_dir = self.config_dir / "presets"
        self.presets_dir.mkdir(exist_ok=True)
        
        # Default settings
        self.defaults = {
            "input_device": None,
            "output_device": None,
            "sample_rate": 48000,
            "buffer_size": 512,
            "channels": 2,
            "auto_reconnect": True,
            "start_minimized": False,
            "enable_notifications": True,
            "window_x": 100,
            "window_y": 100
        }
        
        # Current settings
        self.settings = self.defaults.copy()
        
        # Load settings from file
        self.load()
        
        logger.info("Settings initialized")
    
    def load(self) -> bool:
        """Load settings from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Update settings with loaded values
                    self.settings.update(loaded_settings)
                logger.info("Settings loaded from file")
                return True
            else:
                # Create default settings file
                self.save()
                logger.info("Default settings created")
                return True
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return False
    
    def save(self) -> bool:
        """Save settings to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.info("Settings saved to file")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value"""
        self.settings[key] = value
    
    def get_presets(self) -> List[str]:
        """Get a list of available presets"""
        try:
            presets = []
            for file in self.presets_dir.glob("*.json"):
                presets.append(file.stem)
            return sorted(presets)
        except Exception as e:
            logger.error(f"Error getting presets: {e}")
            return []
    
    def save_preset(self, name: str, preset: Dict[str, Any]) -> bool:
        """Save a preset to a file"""
        try:
            preset_file = self.presets_dir / f"{name}.json"
            with open(preset_file, 'w') as f:
                json.dump(preset, f, indent=2)
            logger.info(f"Preset '{name}' saved")
            return True
        except Exception as e:
            logger.error(f"Error saving preset '{name}': {e}")
            return False
    
    def load_preset(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a preset from a file"""
        try:
            preset_file = self.presets_dir / f"{name}.json"
            if preset_file.exists():
                with open(preset_file, 'r') as f:
                    preset = json.load(f)
                logger.info(f"Preset '{name}' loaded")
                return preset
            else:
                logger.warning(f"Preset '{name}' not found")
                return None
        except Exception as e:
            logger.error(f"Error loading preset '{name}': {e}")
            return None
    
    def delete_preset(self, name: str) -> bool:
        """Delete a preset file"""
        try:
            preset_file = self.presets_dir / f"{name}.json"
            if preset_file.exists():
                preset_file.unlink()
                logger.info(f"Preset '{name}' deleted")
                return True
            else:
                logger.warning(f"Preset '{name}' not found")
                return False
        except Exception as e:
            logger.error(f"Error deleting preset '{name}': {e}")
            return False
    
    def reset_to_defaults(self) -> None:
        """Reset settings to defaults"""
        self.settings = self.defaults.copy()
        self.save()
