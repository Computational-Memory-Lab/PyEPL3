"""
PyEPL3 - Python Experiment Programming Library for Python 3
Modern reimplementation of PyEPL with Python 3 support
"""

from setuptools import setup, find_packages

setup(
    name="pyepl3",
    version="0.1.0",
    description="Python Experiment Programming Library for Python 3",
    author="PyEPL3 Development Team",
    python_requires=">=3.7",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.0.0",           # Graphics, input, event handling
        "Pillow>=8.0.0",           # Image loading and manipulation
        "numpy>=1.19.0",           # Numerical operations, audio processing
        "scipy>=1.5.0",            # Audio file I/O (soundfile)
        "sounddevice>=0.4.0",      # Audio playback and recording
        "soundfile>=0.10.0",       # Multi-format audio file support
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=20.8b1",
            "mypy>=0.800",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    package_data={
        "pyepl3": ["fonts/*.ttf"],  # Include default fonts
    },
)
