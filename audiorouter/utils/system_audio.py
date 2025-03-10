"""
System Audio Utilities - Functions for interacting with macOS audio system
"""

import logging
import subprocess
import re
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)

def get_current_output_device() -> Tuple[Optional[str], Optional[str]]:
    """
    Get the current system audio output device
    
    Returns:
        Tuple containing (device_id, device_name) or (None, None) on error
    """
    try:
        cmd = ["SwitchAudioSource", "-c"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            device_name = result.stdout.strip()
            
            # Get the device ID
            id_cmd = ["SwitchAudioSource", "-f", "json"]
            id_result = subprocess.run(id_cmd, capture_output=True, text=True)
            
            if id_result.returncode == 0:
                # Parse the JSON output to find the device ID
                import json
                devices = json.loads(id_result.stdout)
                
                for device in devices:
                    if device.get('name') == device_name:
                        return (device.get('id'), device_name)
            
            # Fallback to just the name if we couldn't get the ID
            return (None, device_name)
        
        logger.error(f"Error getting current output device: {result.stderr}")
        return (None, None)
    
    except Exception as e:
        logger.error(f"Exception getting current output device: {e}")
        return (None, None)

def set_output_device(device_name: str) -> bool:
    """
    Set the system audio output device
    
    Args:
        device_name: Name of the device to set as output
        
    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = ["SwitchAudioSource", "-s", device_name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"System audio output set to: {device_name}")
            return True
        
        logger.error(f"Error setting output device: {result.stderr}")
        return False
    
    except Exception as e:
        logger.error(f"Exception setting output device: {e}")
        return False

def check_audio_switch_tool() -> bool:
    """
    Check if the SwitchAudioSource tool is installed
    
    Returns:
        True if installed, False otherwise
    """
    try:
        cmd = ["which", "SwitchAudioSource"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            return True
        
        logger.warning("SwitchAudioSource not found. Install with: brew install switchaudio-osx")
        return False
    
    except Exception as e:
        logger.error(f"Exception checking for SwitchAudioSource: {e}")
        return False

def install_audio_switch_tool() -> bool:
    """
    Attempt to install SwitchAudioSource using Homebrew
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # First check if Homebrew is installed
        cmd = ["which", "brew"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error("Homebrew not found. Cannot install SwitchAudioSource automatically.")
            return False
        
        # Install SwitchAudioSource
        cmd = ["brew", "install", "switchaudio-osx"]
        logger.info("Installing SwitchAudioSource...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("SwitchAudioSource installed successfully")
            return True
        
        logger.error(f"Error installing SwitchAudioSource: {result.stderr}")
        return False
    
    except Exception as e:
        logger.error(f"Exception installing SwitchAudioSource: {e}")
        return False
