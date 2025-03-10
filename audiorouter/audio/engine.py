"""
Audio Engine - Handles audio routing and processing
"""

import logging
import threading
import time
import numpy as np
import pyaudio
import queue
from typing import Dict, Optional, List, Any

from .devices import DeviceManager
from ..utils.settings import Settings

logger = logging.getLogger(__name__)

class AudioEngine:
    """Audio processing engine for routing audio between devices"""
    
    def __init__(self, device_manager: DeviceManager, settings: Settings):
        """Initialize the audio engine"""
        self.device_manager = device_manager
        self.settings = settings
        self.py_audio = pyaudio.PyAudio()
        self.running = False
        self.stream_in = None
        self.stream_out = None
        self.audio_thread = None
        self.buffer_size = settings.get("buffer_size", 512)  # Smaller buffer size for low latency
        self.sample_rate = settings.get("sample_rate", 48000)  # Default to 48kHz
        self.channels = settings.get("channels", 2)  # Default to stereo
        self.input_device = None
        self.output_device = None
        self.audio_buffer = queue.Queue(maxsize=8)  # Small buffer queue for low latency
        
        logger.info("Audio engine initialized")
    
    def start(self) -> bool:
        """Start audio processing"""
        if self.running:
            logger.warning("Audio engine is already running")
            return False
        
        try:
            # Get devices from settings or defaults
            input_device_name = self.settings.get("input_device")
            output_device_name = self.settings.get("output_device")
            
            if input_device_name:
                self.input_device = self.device_manager.get_device_by_name(input_device_name, output=False)
            else:
                self.input_device = self.device_manager.get_default_blackhole_device()
            
            if output_device_name:
                self.output_device = self.device_manager.get_device_by_name(output_device_name)
            else:
                self.output_device = self.device_manager.get_default_output_device()
            
            # Check if we have valid devices
            if not self.input_device:
                raise ValueError("No BlackHole input device found. Please install BlackHole driver.")
            
            if not self.output_device:
                raise ValueError("No output device found.")
            
            # Get the optimum sample rate for the devices
            self.sample_rate = int(self.settings.get("sample_rate", 48000))
            
            # Start the audio streams
            self._start_streams()
            
            # Start the processing thread
            self.running = True
            self.audio_thread = threading.Thread(target=self._audio_processing_thread)
            self.audio_thread.daemon = True
            self.audio_thread.start()
            
            logger.info(f"Audio engine started: Routing from {self.input_device['name']} to {self.output_device['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start audio engine: {e}")
            self.stop()
            raise
    
    def stop(self) -> None:
        """Stop audio processing"""
        logger.info("Stopping audio engine")
        self.running = False
        
        # Wait for thread to finish
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(1.0)
        
        # Close streams
        self._close_streams()
    
    def reconnect_devices(self) -> bool:
        """Reconnect to audio devices (for device changes)"""
        logger.info("Reconnecting audio devices")
        was_running = self.running
        
        if was_running:
            self.stop()
        
        # Short delay to ensure everything is closed
        time.sleep(0.2)
        
        if was_running:
            try:
                return self.start()
            except Exception as e:
                logger.error(f"Failed to reconnect devices: {e}")
                return False
        
        return True
    
    def _start_streams(self) -> None:
        """Start the audio streams for input and output"""
        try:
            # Close existing streams if they exist
            self._close_streams()
            
            # Input stream callback
            def input_callback(in_data, frame_count, time_info, status):
                try:
                    if status:
                        logger.debug(f"Input stream status: {status}")
                    
                    # Add to buffer queue without blocking
                    try:
                        self.audio_buffer.put(in_data, block=False)
                    except queue.Full:
                        # If buffer is full, clear one item and add new data
                        try:
                            self.audio_buffer.get_nowait()
                            self.audio_buffer.put(in_data, block=False)
                        except:
                            pass
                            
                    return (None, pyaudio.paContinue)
                except Exception as e:
                    logger.error(f"Error in input callback: {e}")
                    return (None, pyaudio.paContinue)
            
            # Output stream callback
            def output_callback(in_data, frame_count, time_info, status):
                try:
                    if status:
                        logger.debug(f"Output stream status: {status}")
                    
                    # Get data from buffer queue or return silence if empty
                    try:
                        data = self.audio_buffer.get(block=False)
                        return (data, pyaudio.paContinue)
                    except queue.Empty:
                        # Return silence if no data is available
                        return (b'\x00' * (frame_count * self.channels * 2), pyaudio.paContinue)
                except Exception as e:
                    logger.error(f"Error in output callback: {e}")
                    # Return silence on error
                    return (b'\x00' * (frame_count * self.channels * 2), pyaudio.paContinue)
            
            # Open input stream
            self.stream_in = self.py_audio.open(
                rate=self.sample_rate,
                channels=self.channels,
                format=pyaudio.paInt16,
                input=True,
                output=False,
                input_device_index=self.input_device['index'],
                frames_per_buffer=self.buffer_size,
                stream_callback=input_callback
            )
            
            # Open output stream
            self.stream_out = self.py_audio.open(
                rate=self.sample_rate,
                channels=self.channels,
                format=pyaudio.paInt16,
                input=False,
                output=True,
                output_device_index=self.output_device['index'],
                frames_per_buffer=self.buffer_size,
                stream_callback=output_callback
            )
            
            logger.info(f"Audio streams started: {self.buffer_size} buffer size, {self.sample_rate}Hz, {self.channels} channels")
            
        except Exception as e:
            logger.error(f"Error starting audio streams: {e}")
            self._close_streams()
            raise
    
    def _close_streams(self) -> None:
        """Close audio streams"""
        # Close input stream
        if self.stream_in:
            try:
                self.stream_in.stop_stream()
                self.stream_in.close()
            except Exception as e:
                logger.error(f"Error closing input stream: {e}")
            finally:
                self.stream_in = None
        
        # Close output stream
        if self.stream_out:
            try:
                self.stream_out.stop_stream()
                self.stream_out.close()
            except Exception as e:
                logger.error(f"Error closing output stream: {e}")
            finally:
                self.stream_out = None
        
        # Clear the buffer
        while not self.audio_buffer.empty():
            try:
                self.audio_buffer.get_nowait()
            except queue.Empty:
                break
    
    def _audio_processing_thread(self) -> None:
        """Audio processing thread function"""
        logger.info("Audio processing thread started")
        
        while self.running:
            try:
                # The actual processing happens in the callbacks
                # This thread is just to keep the engine running
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in audio processing thread: {e}")
                time.sleep(0.5)  # Short delay before retry
        
        logger.info("Audio processing thread stopped")
    
    def set_input_device(self, device: Dict) -> bool:
        """Set the input device and reconnect"""
        logger.info(f"Setting input device to {device['name']}")
        self.input_device = device
        self.settings.set("input_device", device['name'])
        return self.reconnect_devices()
    
    def set_output_device(self, device: Dict) -> bool:
        """Set the output device and reconnect"""
        logger.info(f"Setting output device to {device['name']}")
        self.output_device = device
        self.settings.set("output_device", device['name'])
        return self.reconnect_devices()
    
    def set_buffer_size(self, buffer_size: int) -> bool:
        """Set the buffer size and reconnect"""
        logger.info(f"Setting buffer size to {buffer_size}")
        self.buffer_size = buffer_size
        self.settings.set("buffer_size", buffer_size)
        return self.reconnect_devices()
    
    def set_sample_rate(self, sample_rate: int) -> bool:
        """Set the sample rate and reconnect"""
        logger.info(f"Setting sample rate to {sample_rate}")
        self.sample_rate = sample_rate
        self.settings.set("sample_rate", sample_rate)
        return self.reconnect_devices()
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self.stop()
        if self.py_audio:
            self.py_audio.terminate()
