#!/bin/bash
# Script to create a desktop shortcut for Audio Router

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_PATH="$SCRIPT_DIR/launch_audiorouter.command"
ICON_PATH="$SCRIPT_DIR/audiorouter/resources/icon.png"
DESKTOP_PATH="$HOME/Desktop"
APP_NAME="Audio Router"

# Create the AppleScript application
echo "Creating AppleScript application..."
osascript > "$DESKTOP_PATH/$APP_NAME.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>applet</string>
    <key>CFBundleIconFile</key>
    <string>applet</string>
    <key>CFBundleIdentifier</key>
    <string>com.apple.ScriptEditor.id.AudioRouter</string>
    <key>CFBundleName</key>
    <string>Audio Router</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleSignature</key>
    <string>aplt</string>
</dict>
</plist>
EOF

mkdir -p "$DESKTOP_PATH/$APP_NAME.app/Contents/Resources"
mkdir -p "$DESKTOP_PATH/$APP_NAME.app/Contents/MacOS"

# Create the launcher script
cat > "$DESKTOP_PATH/$APP_NAME.app/Contents/MacOS/applet" << EOF
#!/bin/bash
"$APP_PATH"
EOF

chmod +x "$DESKTOP_PATH/$APP_NAME.app/Contents/MacOS/applet"

# Use the application icon if available
if [ -f "$ICON_PATH" ]; then
    # Create an icns file from the png
    mkdir -p "$DESKTOP_PATH/$APP_NAME.app/Contents/Resources/icons.iconset"
    sips -z 16 16 "$ICON_PATH" --out "$DESKTOP_PATH/$APP_NAME.app/Contents/Resources/icons.iconset/icon_16x16.png"
    sips -z 32 32 "$ICON_PATH" --out "$DESKTOP_PATH/$APP_NAME.app/Contents/Resources/icons.iconset/icon_32x32.png"
    sips -z 128 128 "$ICON_PATH" --out "$DESKTOP_PATH/$APP_NAME.app/Contents/Resources/icons.iconset/icon_128x128.png"
    sips -z 256 256 "$ICON_PATH" --out "$DESKTOP_PATH/$APP_NAME.app/Contents/Resources/icons.iconset/icon_256x256.png"
    sips -z 512 512 "$ICON_PATH" --out "$DESKTOP_PATH/$APP_NAME.app/Contents/Resources/icons.iconset/icon_512x512.png"
    
    iconutil -c icns "$DESKTOP_PATH/$APP_NAME.app/Contents/Resources/icons.iconset" -o "$DESKTOP_PATH/$APP_NAME.app/Contents/Resources/applet.icns"
    rm -rf "$DESKTOP_PATH/$APP_NAME.app/Contents/Resources/icons.iconset"
else
    echo "Icon not found at $ICON_PATH"
fi

echo "Desktop shortcut created at $DESKTOP_PATH/$APP_NAME.app"
echo "You can now launch Audio Router from your desktop!"
