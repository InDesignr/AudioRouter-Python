# MacOS Audio Router

A low-latency macOS application that routes audio from BlackHole virtual audio driver to user-selected output devices. Optimized for voice applications with minimal latency.

## Features

- Route audio from BlackHole to any output device
- Simple and intuitive UI for device selection
- Minimal latency for voice communication
- System tray presence for easy access
- Automatic reconnection if devices disconnect
- Save and load routing presets
- Graceful handling of device hot-plugging

## Requirements

- macOS 10.14 or higher
- [BlackHole](https://github.com/ExistentialAudio/BlackHole) virtual audio driver installed
- Python 3.9+

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

## Configuration

The application settings are stored in `~/.audiorouter/config.json`. You can manually edit this file or use the application UI to modify settings.

## Development

This project is developed with VS Code. To set up the development environment:

1. Clone the repository
2. Open the folder in VS Code
3. Create a virtual environment and install dependencies
4. Use the integrated terminal and debugger for testing

## License

MIT License
