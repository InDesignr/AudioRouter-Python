#!/usr/bin/env python3
"""
Build and test utilities for Audio Router
"""

import os
import sys
import subprocess
import platform
import argparse
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and print output"""
    print(f"Running: {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd
    )
    stdout, stderr = process.communicate()
    
    if stdout:
        print(stdout)
    if stderr:
        print(stderr)
    
    return process.returncode == 0

def check_venv():
    """Check if running in virtual environment"""
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Warning: Not running in a virtual environment. It's recommended to use a virtual environment.")
        response = input("Do you want to create and activate a virtual environment now? (y/n): ")
        if response.lower() == 'y':
            run_command(['python3', '-m', 'venv', 'venv'])
            # Suggest activation command since we can't activate from within Python
            if platform.system() == 'Windows':
                print("Please activate the virtual environment with: venv\\Scripts\\activate")
            else:
                print("Please activate the virtual environment with: source venv/bin/activate")
            sys.exit(0)

def install_deps():
    """Install dependencies"""
    print("Installing dependencies...")
    return run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def run_app():
    """Run the application for testing"""
    print("Running application for testing...")
    return run_command([sys.executable, 'main.py'])

def build_app():
    """Build application using PyInstaller"""
    print("Building application using PyInstaller...")
    
    # First, ensure PyInstaller is installed
    run_command([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Build the application
    icon_path = os.path.join('audiorouter', 'resources', 'icon.png')
    app_name = 'AudioRouter'
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name', app_name,
        '--windowed',
        '--onefile',
        '--add-data', f'{icon_path}:audiorouter/resources',
        'main.py'
    ]
    
    if platform.system() == 'Darwin':  # macOS
        cmd.extend(['--icon', icon_path])
    
    return run_command(cmd)

def main():
    parser = argparse.ArgumentParser(description="Build and test utilities for Audio Router")
    parser.add_argument('action', choices=['run', 'build', 'deps'], 
                       help='Action to perform: run app, build app, or install dependencies')
    
    args = parser.parse_args()
    
    # Check if we're in a virtual environment
    check_venv()
    
    if args.action == 'deps':
        install_deps()
    elif args.action == 'run':
        run_app()
    elif args.action == 'build':
        # Install dependencies first
        if install_deps():
            build_app()
        else:
            print("Failed to install dependencies. Build aborted.")

if __name__ == "__main__":
    main()
