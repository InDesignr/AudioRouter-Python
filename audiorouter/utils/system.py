"""
System utilities for the Audio Router application
"""

import logging
import os
import sys
import platform
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

def get_app_path():
    """Get the path to the application executable"""
    if getattr(sys, 'frozen', False):
        # Running as a bundled app
        return Path(sys.executable)
    else:
        # Running as a script
        return Path(sys.argv[0]).resolve()

def setup_login_item(enable: bool = True) -> bool:
    """
    Set up or remove the application as a login item on macOS
    """
    if platform.system() != 'Darwin':
        logger.warning("Login item setup is only supported on macOS")
        return False
    
    app_path = get_app_path()
    
    try:
        if enable:
            # Create a LaunchAgents plist file for auto-start
            launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
            launch_agents_dir.mkdir(exist_ok=True)
            
            plist_path = launch_agents_dir / "com.audiorouter.launcher.plist"
            
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.audiorouter.launcher</string>
    <key>ProgramArguments</key>
    <array>
        <string>{app_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
"""
            
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            
            # Load the plist
            subprocess.run(['launchctl', 'load', str(plist_path)], check=True)
            logger.info("Application set to start at login")
            return True
            
        else:
            # Remove launch agent plist
            plist_path = Path.home() / "Library" / "LaunchAgents" / "com.audiorouter.launcher.plist"
            
            if plist_path.exists():
                # Unload the plist
                subprocess.run(['launchctl', 'unload', str(plist_path)], check=True)
                # Remove the file
                plist_path.unlink()
                logger.info("Application removed from login items")
                return True
            
            return True
    
    except Exception as e:
        logger.error(f"Error setting up login item: {e}")
        return False

def check_blackhole_installed() -> bool:
    """
    Check if BlackHole audio driver is installed
    """
    try:
        # On macOS, check for the existence of the BlackHole kernel extension
        if platform.system() == 'Darwin':
            kext_path = Path('/Library/Audio/Plug-Ins/HAL/BlackHole.driver')
            component_path = Path('/Library/Audio/Plug-Ins/Components/BlackHole.component')
            
            return kext_path.exists() or component_path.exists()
        
        return False
    except Exception as e:
        logger.error(f"Error checking BlackHole installation: {e}")
        return False
