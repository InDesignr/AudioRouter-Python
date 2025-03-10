#!/bin/bash
# Launcher script for Audio Router application
# This script activates the virtual environment and runs the application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the project directory
cd "$SCRIPT_DIR"

# Check if all dependencies are installed
if [ ! -d "venv" ]; then
  echo "Virtual environment not found. Creating one..."
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
else
  # Activate the virtual environment
  source venv/bin/activate
fi

# Display a notification that the app is starting
osascript -e 'display notification "Audio Router is starting..." with title "Audio Router"'

# Run the application
python main.py

# Keep the terminal window open in case of errors (uncomment if needed)
#read -p "Press Enter to close this window..." -n1 -s
