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

from .audio.engine import AudioEngine
from .audio.devices import DeviceManager
from .gui.settings_window import SettingsWindow
from .utils.settings import Settings

logger = logging.getLogger(__name__)

# Define a main entry point function for better packaging and distribution
def main():
    """Main entry point for the application when run as a module"""
    from sys import argv
    app = AudioRouterApp(argv)
    return app.exec()

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
        
        # Start audio processing
        self.start_audio()
        
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
            
        self.tray_icon.setToolTip("Audio Router")
        
        # Create the tray menu
        tray_menu = QMenu()
        
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
    
    def start_audio(self):
        """Start the audio processing engine"""
        try:
            self.audio_engine.start()
            logger.info("Audio engine started successfully")
        except Exception as e:
            logger.error(f"Failed to start audio engine: {e}")
            # Show error in system tray
            self.tray_icon.showMessage(
                "Audio Router Error",
                f"Failed to start audio engine: {str(e)}",
                QSystemTrayIcon.MessageIcon.Warning
            )
    
    def quit_app(self):
        """Quit the application"""
        logger.info("Shutting down application")
        self.audio_engine.stop()
        self.settings.save()
        self.tray_icon.setVisible(False)
        self.quit()
