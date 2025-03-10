"""
Device Manager - Handles detection and management of audio devices
"""

import logging
import sounddevice as sd
import pyaudio
import soundcard as sc
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class DeviceManager:
    """Manages audio devices for the Audio Router application"""
    
    def __init__(self):
        """Initialize the device manager"""
        self.py_audio = pyaudio.PyAudio()
        self.input_devices = []
        self.output_devices = []
        self.blackhole_devices = []
        self.last_device_hash = ""
        self.refresh_devices()
        logger.info("Device manager initialized")
    
    def refresh_devices(self) -> None:
        """Refresh the list of available audio devices"""
        try:
            # Clear current device lists
            self.input_devices = []
            self.output_devices = []
            self.blackhole_devices = []
            
            # Get devices using SoundDevice
            sd_devices = sd.query_devices()
            
            # Get devices using SoundCard
            sc_inputs = sc.all_microphones()
            sc_outputs = sc.all_speakers()
            
            # Get devices using PyAudio
            for i in range(self.py_audio.get_device_count()):
                device_info = self.py_audio.get_device_info_by_index(i)
                
                # Parse device info
                device = {
                    'index': i,
                    'name': device_info['name'],
                    'max_input_channels': device_info['maxInputChannels'],
                    'max_output_channels': device_info['maxOutputChannels'],
                    'default_sample_rate': device_info['defaultSampleRate'],
                    'host_api': device_info['hostApi']
                }
                
                # Check if it's a BlackHole device
                if "BlackHole" in device['name']:
                    self.blackhole_devices.append(device)
                
                # Add to input or output lists
                if device['max_input_channels'] > 0:
                    self.input_devices.append(device)
                
                if device['max_output_channels'] > 0:
                    self.output_devices.append(device)
            
            # Generate a hash to detect changes
            self.last_device_hash = self._generate_device_hash()
            
            logger.info(f"Found {len(self.input_devices)} input devices, "
                       f"{len(self.output_devices)} output devices, "
                       f"{len(self.blackhole_devices)} BlackHole devices")
            
        except Exception as e:
            logger.error(f"Error refreshing audio devices: {e}")
    
    def check_device_changes(self) -> bool:
        """Check if audio devices have changed"""
        current_hash = self._generate_device_hash()
        if current_hash != self.last_device_hash:
            logger.info("Audio device changes detected")
            self.refresh_devices()
            return True
        return False
    
    def _generate_device_hash(self) -> str:
        """Generate a hash string representing the current device state"""
        device_str = ""
        for device in self.input_devices:
            device_str += f"{device['name']}:{device['index']};"
        for device in self.output_devices:
            device_str += f"{device['name']}:{device['index']};"
        return device_str
    
    def get_default_blackhole_device(self) -> Optional[Dict]:
        """Get the default BlackHole device, or None if not found"""
        if self.blackhole_devices:
            return self.blackhole_devices[0]
        logger.warning("No BlackHole devices found")
        return None
    
    def get_default_output_device(self) -> Optional[Dict]:
        """Get the default output device, or None if not found"""
        if self.output_devices:
            # Find the system default output device
            for device in self.output_devices:
                # Skip BlackHole devices
                if "BlackHole" not in device['name']:
                    return device
            # If all outputs are BlackHole devices, return the first one
            return self.output_devices[0]
        logger.warning("No output devices found")
        return None
    
    def get_device_by_name(self, name: str, output: bool = True) -> Optional[Dict]:
        """Get device by name"""
        devices = self.output_devices if output else self.input_devices
        for device in devices:
            if device['name'] == name:
                return device
        return None
    
    def get_device_by_index(self, index: int) -> Optional[Dict]:
        """Get device by index"""
        try:
            device_info = self.py_audio.get_device_info_by_index(index)
            return {
                'index': index,
                'name': device_info['name'],
                'max_input_channels': device_info['maxInputChannels'],
                'max_output_channels': device_info['maxOutputChannels'],
                'default_sample_rate': device_info['defaultSampleRate'],
                'host_api': device_info['hostApi']
            }
        except Exception as e:
            logger.error(f"Error getting device by index {index}: {e}")
            return None
    
    def get_sample_rate_for_device(self, device_index: int) -> int:
        """Get the default sample rate for a device"""
        try:
            device_info = self.py_audio.get_device_info_by_index(device_index)
            return int(device_info['defaultSampleRate'])
        except Exception as e:
            logger.error(f"Error getting sample rate for device {device_index}: {e}")
            return 44100  # Default to CD quality as fallback
    
    def cleanup(self) -> None:
        """Clean up PyAudio resources"""
        self.py_audio.terminate()
