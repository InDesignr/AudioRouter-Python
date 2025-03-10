"""
Audio Router App - Main application class
"""

import logging
import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from enum import Enum

from .audio.engine import AudioEngine
from .audio.devices import DeviceManager
from .gui.settings_window import SettingsWindow
from .utils.settings import Settings
from .utils import system_audio

logger = logging.getLogger(__name__)

# Define a main entry point function for better packaging and distribution
def main():
    """Main entry point for the application when run as a module"""
    from sys import argv
    app = AudioRouterApp(argv)
    return app.exec()

# Routing state enum
class RoutingState(Enum):
    STOPPED = 0
    RUNNING = 1

class AudioRouterApp(QApplication):
    """Main application class for Audio Router"""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)
        self.setApplicationName("Audio Router")
        
        # Initialize settings
        self.settings = Settings()
        
        # Initialize the device manager
        self.device_manager = DeviceManager()
        
        # Initialize audio engine
        self.audio_engine = AudioEngine(self.device_manager, self.settings)
        
        # Check for audio switch tool
        self.audio_switch_available = system_audio.check_audio_switch_tool()
        if not self.audio_switch_available:
            logger.warning("SwitchAudioSource tool not available. System audio switching disabled.")
            # Try to install it
            if system_audio.install_audio_switch_tool():
                self.audio_switch_available = True
                logger.info("SwitchAudioSource tool installed successfully.")
        
        # Routing state
        self.routing_state = RoutingState.STOPPED
        self.previous_output_device = None
        
        # Create the system tray icon
        self.init_tray()
        
        # Create the settings window
        self.settings_window = SettingsWindow(
            self.device_manager, 
            self.audio_engine,
            self.settings
        )
        
        # Setup device hot-plugging detection timer
        self.device_check_timer = QTimer(self)
        self.device_check_timer.setInterval(2000)  # Check every 2 seconds
        self.device_check_timer.timeout.connect(self.check_devices)
        self.device_check_timer.start()
        
        # Application is initialized but not routing yet
        logger.info("Application initialized successfully")
    
    def init_tray(self):
        """Initialize the system tray icon and menu"""
        # Create the icon path
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icon.png")
        
        # Set the icon if it exists
        if os.path.exists(icon_path):
            logger.info(f"Loading icon from {icon_path}")
            icon = QIcon(icon_path)
            self.tray_icon = QSystemTrayIcon(icon, self)
        else:
            logger.warning(f"Icon not found at {icon_path}, using default")
            self.tray_icon = QSystemTrayIcon(self)
            
        self.tray_icon.setToolTip("Audio Router (Stopped)")
        
        # Create the tray menu
        tray_menu = QMenu()
        
        # Add start/stop routing action
        self.toggle_routing_action = QAction("Start Routing", self)
        self.toggle_routing_action.triggered.connect(self.toggle_routing)
        tray_menu.addAction(self.toggle_routing_action)
        
        # Add menu actions
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tray_menu.addAction(settings_action)
        
        reload_action = QAction("Reload Devices", self)
        reload_action.triggered.connect(self.reload_devices)
        tray_menu.addAction(reload_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        
        # Set the menu and show the icon
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setVisible(True)
    
    def show_settings(self):
        """Show the settings window"""
        self.settings_window.show()
        self.settings_window.activateWindow()
        self.settings_window.raise_()
    
    def reload_devices(self):
        """Reload audio devices"""
        logger.info("Manually reloading audio devices")
        self.device_manager.refresh_devices()
        self.settings_window.update_device_lists()
        self.audio_engine.reconnect_devices()
    
    def check_devices(self):
        """Check for device changes periodically"""
        if self.device_manager.check_device_changes():
            logger.info("Device changes detected, updating...")
            self.settings_window.update_device_lists()
            self.audio_engine.reconnect_devices()
    
    def toggle_routing(self):
        """Toggle audio routing on and off"""
        if self.routing_state == RoutingState.STOPPED:
            self.start_routing()
        else:
            self.stop_routing()
    
    def start_routing(self):
        """Start audio routing and change system output"""
        try:
            # First, store the current output device if we can
            if self.audio_switch_available:
                device_id, device_name = system_audio.get_current_output_device()
                if device_name:
                    self.previous_output_device = device_name
                    logger.info(f"Saved previous output device: {device_name}")
            
            # Find the BlackHole device to set as system output
            blackhole_device = self.device_manager.get_default_blackhole_device()
            if not blackhole_device:
                raise ValueError("BlackHole device not found")
            
            # Set system output to BlackHole if possible
            if self.audio_switch_available and blackhole_device:
                success = system_audio.set_output_device(blackhole_device['name'])
                if success:
                    logger.info(f"Set system output to {blackhole_device['name']}")
                else:
                    logger.warning("Failed to set system output to BlackHole device")
            
            # Start the audio engine
            self.audio_engine.start()
            
            # Update state and UI
            self.routing_state = RoutingState.RUNNING
            self.toggle_routing_action.setText("Stop Routing")
            self.tray_icon.setToolTip("Audio Router (Running)")
            
            # Notify user
            self.tray_icon.showMessage(
                "Audio Router",
                "Audio routing started",
                QSystemTrayIcon.MessageIcon.Information
            )
            
            logger.info("Audio routing started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start audio routing: {e}")
            # Show error in system tray
            self.tray_icon.showMessage(
                "Audio Router Error",
                f"Failed to start audio routing: {str(e)}",
                QSystemTrayIcon.MessageIcon.Warning
            )
    
    def stop_routing(self):
        """Stop audio routing and restore previous output"""
        try:
            # Stop the audio engine
            self.audio_engine.stop()
            
            # Restore previous output device if we have one
            if self.audio_switch_available and self.previous_output_device:
                success = system_audio.set_output_device(self.previous_output_device)
                if success:
                    logger.info(f"Restored system output to {self.previous_output_device}")
                else:
                    logger.warning(f"Failed to restore system output to {self.previous_output_device}")
            
            # Update state and UI
            self.routing_state = RoutingState.STOPPED
            self.toggle_routing_action.setText("Start Routing")
            self.tray_icon.setToolTip("Audio Router (Stopped)")
            
            # Notify user
            self.tray_icon.showMessage(
                "Audio Router",
                "Audio routing stopped",
                QSystemTrayIcon.MessageIcon.Information
            )
            
            logger.info("Audio routing stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping audio routing: {e}")
            self.tray_icon.showMessage(
                "Audio Router Error",
                f"Error stopping audio routing: {str(e)}",
                QSystemTrayIcon.MessageIcon.Warning
            )
    
    def quit_app(self):
        """Quit the application"""
        logger.info("Shutting down application")
        
        # Stop routing if it's currently active
        if self.routing_state == RoutingState.RUNNING:
            self.stop_routing()
        
        # Save settings and quit
        self.settings.save()
        self.tray_icon.setVisible(False)
        self.quit()
