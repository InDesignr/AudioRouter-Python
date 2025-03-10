# MacOS Audio Router

A low-latency macOS application that routes audio from BlackHole virtual audio driver to user-selected output devices. Optimized for voice applications with minimal latency.

## Features

- Route audio from BlackHole to any output device
- Simple and intuitive UI for device selection
- Minimal latency for voice communication
- System tray presence for easy access
- **One-click start/stop routing** with automatic system audio switching
- Automatic reconnection if devices disconnect
- Save and load routing presets
- Graceful handling of device hot-plugging

## Requirements

- macOS 10.14 or higher
- [BlackHole](https://github.com/ExistentialAudio/BlackHole) virtual audio driver installed
- Python 3.9+
- SwitchAudioSource command-line tool (auto-installed via Homebrew if missing)

## Installation

1. Install the BlackHole virtual audio driver from [https://github.com/ExistentialAudio/BlackHole](https://github.com/ExistentialAudio/BlackHole)
2. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python main.py
   ```
5. For desktop shortcut access:
   ```
   # The desktop shortcut is already created at ~/Desktop/"Audio Router.command"
   # Simply double-click this icon to launch the application
   # It will automatically check for dependencies and start the app
   ```

## Configuration

The application settings are stored in `~/.audiorouter/config.json`. You can manually edit this file or use the application UI to modify settings.

## Usage

The application runs in the system tray. To use the router:

1. **Start Routing**: Right-click the system tray icon and select "Start Routing"
   - This will set your system output to the BlackHole device and route that audio to your selected output device
   - Your previous output device is remembered for when you stop routing

2. **Stop Routing**: Right-click the system tray icon and select "Stop Routing"
   - This will restore your system output to the previous device and stop the audio routing

3. **Settings**: Access routing settings by right-clicking the system tray icon and selecting "Settings"
   - Set your preferred output device for routing
   - Configure buffer size and sample rate for optimal latency

The application status is shown in the system tray tooltip (Running/Stopped).

## Development

This project is developed with VS Code. To set up the development environment:

1. Clone the repository
2. Open the folder in VS Code
3. Create a virtual environment and install dependencies
4. Use the integrated terminal and debugger for testing

## License

MIT License
