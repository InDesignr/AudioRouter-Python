#!/bin/bash
# Launcher script for Audio Router application

# Always use the project directory
PROJECT_DIR="/Users/madisonhofer/Projects/20250310-Audiorouter-Python"
cd "$PROJECT_DIR"

# Check if all dependencies are installed
if [ ! -d "venv312" ]; then
  echo "Python 3.12 virtual environment not found. Creating one..."
  python3.12 -m venv venv312
  source venv312/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
else
  # Activate the virtual environment
  source venv312/bin/activate
fi

# Display a notification that the app is starting
osascript -e 'display notification "Audio Router is starting..." with title "Audio Router"'

# Run the application
python main.py

# Keep the terminal window open in case of errors (uncomment if needed)
#read -p "Press Enter to close this window..." -n1 -s
