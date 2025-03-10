#!/usr/bin/env python3
"""
MacOS Audio Router - Main Entry Point
Routes audio from BlackHole virtual audio driver to user-selected output devices
"""

import sys
import os
import logging
from pathlib import Path

def main():
    # Setup logging
    log_dir = Path.home() / ".audiorouter"
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=log_dir / "audiorouter.log",
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("audiorouter")

    # Add console handler for development
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    # Check for BlackHole driver
    try:
        from audiorouter.utils.system import check_blackhole_installed
        if not check_blackhole_installed():
            logger.warning("BlackHole audio driver not detected. The application may not work correctly.")
            print("Warning: BlackHole audio driver not detected. The application may not work correctly.")
            print("Please install BlackHole from: https://github.com/ExistentialAudio/BlackHole")
    except Exception as e:
        logger.error(f"Error checking for BlackHole driver: {e}")

    try:
        logger.info("Starting Audio Router application")
        from audiorouter.app import AudioRouterApp

        app = AudioRouterApp(sys.argv)
        return app.exec()
    except Exception as e:
        logger.error(f"Application crashed: {e}", exc_info=True)
        print(f"Error: Application crashed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
