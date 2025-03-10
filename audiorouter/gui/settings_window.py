"""
Settings Window - GUI for adjusting audio routing settings
"""

import logging
import os
from typing import Dict, List, Optional, Callable

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QSlider, QGroupBox, QCheckBox, QSpinBox,
    QApplication, QMainWindow, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings, QSize

from ..audio.devices import DeviceManager
from ..audio.engine import AudioEngine
from ..utils.settings import Settings

logger = logging.getLogger(__name__)

class SettingsWindow(QMainWindow):
    """Settings window for the Audio Router application"""
    
    def __init__(self, device_manager: DeviceManager, audio_engine: AudioEngine, settings: Settings):
        """Initialize the settings window"""
        super().__init__()
        
        self.device_manager = device_manager
        self.audio_engine = audio_engine
        self.settings = settings
        
        self.setWindowTitle("Audio Router Settings")
        self.setMinimumSize(500, 400)
        
        # Set window position from settings or center on screen
        screen_geometry = QApplication.primaryScreen().geometry()
        window_size = self.size()
        
        x = self.settings.get("window_x", (screen_geometry.width() - window_size.width()) // 2)
        y = self.settings.get("window_y", (screen_geometry.height() - window_size.height()) // 2)
        
        self.move(x, y)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        
        # Create device selection group
        device_group = QGroupBox("Audio Devices")
        device_layout = QVBoxLayout(device_group)
        
        # Input device selection
        input_layout = QHBoxLayout()
        input_label = QLabel("Input Device (BlackHole):")
        self.input_combo = QComboBox()
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_combo)
        device_layout.addLayout(input_layout)
        
        # Output device selection
        output_layout = QHBoxLayout()
        output_label = QLabel("Output Device:")
        self.output_combo = QComboBox()
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_combo)
        device_layout.addLayout(output_layout)
        
        # Button to refresh devices
        refresh_button = QPushButton("Refresh Devices")
        refresh_button.clicked.connect(self.refresh_devices)
        device_layout.addWidget(refresh_button)
        
        main_layout.addWidget(device_group)
        
        # Create audio settings group
        audio_group = QGroupBox("Audio Settings")
        audio_layout = QVBoxLayout(audio_group)
        
        # Sample rate selection
        sample_layout = QHBoxLayout()
        sample_label = QLabel("Sample Rate:")
        self.sample_combo = QComboBox()
        sample_rates = ["44100", "48000", "96000"]
        self.sample_combo.addItems(sample_rates)
        self.sample_combo.setCurrentText(str(self.settings.get("sample_rate", 48000)))
        sample_layout.addWidget(sample_label)
        sample_layout.addWidget(self.sample_combo)
        audio_layout.addLayout(sample_layout)
        
        # Buffer size selection
        buffer_layout = QHBoxLayout()
        buffer_label = QLabel("Buffer Size:")
        self.buffer_spin = QSpinBox()
        self.buffer_spin.setRange(64, 4096)
        self.buffer_spin.setSingleStep(64)
        self.buffer_spin.setValue(self.settings.get("buffer_size", 512))
        buffer_layout.addWidget(buffer_label)
        buffer_layout.addWidget(self.buffer_spin)
        audio_layout.addLayout(buffer_layout)
        
        # Auto-reconnect checkbox
        self.auto_reconnect = QCheckBox("Auto-reconnect on device changes")
        self.auto_reconnect.setChecked(self.settings.get("auto_reconnect", True))
        audio_layout.addWidget(self.auto_reconnect)
        
        main_layout.addWidget(audio_group)
        
        # Create preset group
        preset_group = QGroupBox("Presets")
        preset_layout = QVBoxLayout(preset_group)
        
        # Preset selection
        preset_select_layout = QHBoxLayout()
        preset_label = QLabel("Load Preset:")
        self.preset_combo = QComboBox()
        preset_select_layout.addWidget(preset_label)
        preset_select_layout.addWidget(self.preset_combo)
        preset_layout.addLayout(preset_select_layout)
        
        # Preset buttons
        preset_buttons_layout = QHBoxLayout()
        save_preset_button = QPushButton("Save Current")
        save_preset_button.clicked.connect(self.save_preset)
        delete_preset_button = QPushButton("Delete")
        delete_preset_button.clicked.connect(self.delete_preset)
        preset_buttons_layout.addWidget(save_preset_button)
        preset_buttons_layout.addWidget(delete_preset_button)
        preset_layout.addLayout(preset_buttons_layout)
        
        main_layout.addWidget(preset_group)
        
        # Create status message
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
        
        # Apply and Close buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply Settings")
        self.apply_button.clicked.connect(self.apply_settings)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(close_button)
        main_layout.addLayout(button_layout)
        
        # Initialize UI
        self.update_device_lists()
        self.update_preset_list()
        
        # Connect signals
        self.input_combo.currentIndexChanged.connect(self.on_input_changed)
        self.output_combo.currentIndexChanged.connect(self.on_output_changed)
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        
        logger.info("Settings window initialized")
    
    def update_device_lists(self):
        """Update device selection dropdowns"""
        try:
            # Save current selections
            current_input = self.input_combo.currentText() if self.input_combo.count() > 0 else ""
            current_output = self.output_combo.currentText() if self.output_combo.count() > 0 else ""
            
            # Clear device lists
            self.input_combo.clear()
            self.output_combo.clear()
            
            # Add input devices
            for device in self.device_manager.input_devices:
                self.input_combo.addItem(device['name'])
            
            # Add output devices
            for device in self.device_manager.output_devices:
                self.output_combo.addItem(device['name'])
            
            # Restore previous selections or set defaults
            if current_input and self.input_combo.findText(current_input) >= 0:
                self.input_combo.setCurrentText(current_input)
            elif self.settings.get("input_device") and self.input_combo.findText(self.settings.get("input_device")) >= 0:
                self.input_combo.setCurrentText(self.settings.get("input_device"))
            else:
                # Find and select a BlackHole device
                for i in range(self.input_combo.count()):
                    if "BlackHole" in self.input_combo.itemText(i):
                        self.input_combo.setCurrentIndex(i)
                        break
            
            if current_output and self.output_combo.findText(current_output) >= 0:
                self.output_combo.setCurrentText(current_output)
            elif self.settings.get("output_device") and self.output_combo.findText(self.settings.get("output_device")) >= 0:
                self.output_combo.setCurrentText(self.settings.get("output_device"))
            
            logger.info("Device lists updated")
            
        except Exception as e:
            logger.error(f"Error updating device lists: {e}")
            self.status_label.setText(f"Error updating device lists: {str(e)}")
    
    def update_preset_list(self):
        """Update the preset selection dropdown"""
        try:
            # Save current selection
            current_preset = self.preset_combo.currentText() if self.preset_combo.count() > 0 else ""
            
            # Clear and update preset list
            self.preset_combo.clear()
            presets = self.settings.get_presets()
            
            if not presets:
                self.preset_combo.addItem("No presets saved")
                self.preset_combo.setEnabled(False)
                return
            
            self.preset_combo.setEnabled(True)
            for preset_name in presets:
                self.preset_combo.addItem(preset_name)
            
            # Restore previous selection if possible
            if current_preset and self.preset_combo.findText(current_preset) >= 0:
                self.preset_combo.setCurrentText(current_preset)
            
            logger.info("Preset list updated")
            
        except Exception as e:
            logger.error(f"Error updating preset list: {e}")
            self.status_label.setText(f"Error updating preset list: {str(e)}")
    
    def refresh_devices(self):
        """Refresh audio devices"""
        try:
            self.status_label.setText("Refreshing audio devices...")
            self.device_manager.refresh_devices()
            self.update_device_lists()
            self.status_label.setText("Audio devices refreshed")
            logger.info("Devices refreshed from settings window")
        except Exception as e:
            logger.error(f"Error refreshing devices: {e}")
            self.status_label.setText(f"Error refreshing devices: {str(e)}")
    
    def on_input_changed(self, index):
        """Handle input device selection change"""
        if index < 0:
            return
        
        device_name = self.input_combo.currentText()
        logger.info(f"Input device changed to: {device_name}")
    
    def on_output_changed(self, index):
        """Handle output device selection change"""
        if index < 0:
            return
        
        device_name = self.output_combo.currentText()
        logger.info(f"Output device changed to: {device_name}")
    
    def on_preset_changed(self, index):
        """Handle preset selection change"""
        if index < 0 or not self.preset_combo.isEnabled():
            return
        
        preset_name = self.preset_combo.currentText()
        if preset_name == "No presets saved":
            return
        
        logger.info(f"Preset selected: {preset_name}")
        
        # Ask user if they want to load the preset
        reply = QMessageBox.question(
            self, 
            "Load Preset", 
            f"Do you want to load the '{preset_name}' preset?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.status_label.setText(f"Loading preset: {preset_name}...")
                preset = self.settings.load_preset(preset_name)
                
                if preset:
                    # Update UI with preset values
                    if "input_device" in preset and self.input_combo.findText(preset["input_device"]) >= 0:
                        self.input_combo.setCurrentText(preset["input_device"])
                    
                    if "output_device" in preset and self.output_combo.findText(preset["output_device"]) >= 0:
                        self.output_combo.setCurrentText(preset["output_device"])
                    
                    if "sample_rate" in preset:
                        self.sample_combo.setCurrentText(str(preset["sample_rate"]))
                    
                    if "buffer_size" in preset:
                        self.buffer_spin.setValue(preset["buffer_size"])
                    
                    # Apply settings immediately
                    self.apply_settings()
                    
                    self.status_label.setText(f"Preset '{preset_name}' loaded")
                    logger.info(f"Preset '{preset_name}' loaded")
                else:
                    self.status_label.setText(f"Error: Preset '{preset_name}' not found")
                    logger.warning(f"Preset '{preset_name}' not found")
            except Exception as e:
                logger.error(f"Error loading preset: {e}")
                self.status_label.setText(f"Error loading preset: {str(e)}")
    
    def save_preset(self):
        """Save current settings as a preset"""
        # Get preset name from user
        from PyQt6.QtWidgets import QInputDialog
        preset_name, ok = QInputDialog.getText(
            self, 
            "Save Preset", 
            "Enter preset name:"
        )
        
        if ok and preset_name:
            try:
                # Create preset from current settings
                preset = {
                    "input_device": self.input_combo.currentText(),
                    "output_device": self.output_combo.currentText(),
                    "sample_rate": int(self.sample_combo.currentText()),
                    "buffer_size": self.buffer_spin.value(),
                    "auto_reconnect": self.auto_reconnect.isChecked()
                }
                
                # Save preset
                self.settings.save_preset(preset_name, preset)
                self.update_preset_list()
                self.status_label.setText(f"Preset '{preset_name}' saved")
                logger.info(f"Preset '{preset_name}' saved")
                
                # Select the new preset
                index = self.preset_combo.findText(preset_name)
                if index >= 0:
                    self.preset_combo.setCurrentIndex(index)
                
            except Exception as e:
                logger.error(f"Error saving preset: {e}")
                self.status_label.setText(f"Error saving preset: {str(e)}")
    
    def delete_preset(self):
        """Delete the selected preset"""
        if not self.preset_combo.isEnabled() or self.preset_combo.currentText() == "No presets saved":
            return
        
        preset_name = self.preset_combo.currentText()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Delete Preset", 
            f"Are you sure you want to delete the '{preset_name}' preset?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.settings.delete_preset(preset_name)
                self.update_preset_list()
                self.status_label.setText(f"Preset '{preset_name}' deleted")
                logger.info(f"Preset '{preset_name}' deleted")
            except Exception as e:
                logger.error(f"Error deleting preset: {e}")
                self.status_label.setText(f"Error deleting preset: {str(e)}")
    
    def apply_settings(self):
        """Apply the current settings"""
        try:
            self.status_label.setText("Applying settings...")
            
            # Get settings from UI
            input_device_name = self.input_combo.currentText()
            output_device_name = self.output_combo.currentText()
            sample_rate = int(self.sample_combo.currentText())
            buffer_size = self.buffer_spin.value()
            auto_reconnect = self.auto_reconnect.isChecked()
            
            # Update settings object
            self.settings.set("input_device", input_device_name)
            self.settings.set("output_device", output_device_name)
            self.settings.set("sample_rate", sample_rate)
            self.settings.set("buffer_size", buffer_size)
            self.settings.set("auto_reconnect", auto_reconnect)
            
            # Save settings
            self.settings.save()
            
            # Update audio engine
            input_device = self.device_manager.get_device_by_name(input_device_name, output=False)
            output_device = self.device_manager.get_device_by_name(output_device_name)
            
            if input_device and output_device:
                self.audio_engine.sample_rate = sample_rate
                self.audio_engine.buffer_size = buffer_size
                
                # Restart audio engine with new settings
                self.audio_engine.reconnect_devices()
                
                self.status_label.setText("Settings applied successfully")
                logger.info("Settings applied from UI")
            else:
                self.status_label.setText("Error: Invalid device selection")
                logger.warning("Invalid device selection when applying settings")
                
        except Exception as e:
            logger.error(f"Error applying settings: {e}")
            self.status_label.setText(f"Error applying settings: {str(e)}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window position
        self.settings.set("window_x", self.pos().x())
        self.settings.set("window_y", self.pos().y())
        self.settings.save()
        
        event.accept()
