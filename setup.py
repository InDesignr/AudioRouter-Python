#!/usr/bin/env python3
"""
Setup script for the Audio Router application
"""
from setuptools import setup, find_packages

setup(
    name="audiorouter",
    version="0.1.0",
    description="MacOS Audio Routing Application",
    author="Audio Router Team",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pyaudio",
        "pyqt6",
        "numpy",
        "pyobjc",
        "sounddevice",
        "soundcard",
        "pystray",
        "pillow",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "audiorouter=audiorouter.app:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    package_data={
        "audiorouter": ["resources/*.png"],
    },
)
