"""
PyEPL3 - Python Experiment Programming Library for Python 3

A modern reimplementation of PyEPL with full Python 3 support.
"""

__version__ = "0.1.0"

# Core experiment framework
from .experiment import Experiment, Configuration, State

# Timing
from .timing import PresentationClock, now, delay, wait

# Display
from .display import (
    VideoTrack,
    Image,
    Text,
    CompoundStimulus,
    Color,
    Showable,
    Anchor,
    # Colors
    BLACK, WHITE, RED, GREEN, BLUE,
    # Positioning
    ABOVE, BELOW, LEFT, RIGHT, OVER,
)

# Audio
from .audio import AudioTrack, FileAudioClip, Beep

# Keyboard input
from .keyboard import KeyTrack, Key, ButtonChooser

# Mouse input
from .mouse import (
    MouseTrack,
    MouseButton,
    MouseAxis,
    LEFT_BUTTON,
    MIDDLE_BUTTON,
    RIGHT_BUTTON,
)

# Pools
from .pool import Pool, TextPool, ImagePool, SoundPool, PoolDict, WordObject

# Utilities
from .utils import mathDistract

# EEG (stub for now)
from .eeg import EEGTrack

# Base classes
from .base import Track, LogTrack

# Exceptions
from .exceptions import (
    PyEPL3Error,
    TrackError,
    DisplayError,
    AudioError,
    InputError,
    ConfigurationError,
    TimingError,
    PoolError,
)


__all__ = [
    # Version
    '__version__',

    # Core
    'Experiment',
    'Configuration',
    'State',

    # Timing
    'PresentationClock',
    'now',
    'delay',
    'wait',

    # Display
    'VideoTrack',
    'Image',
    'Text',
    'CompoundStimulus',
    'Color',
    'Showable',
    'Anchor',
    'BLACK', 'WHITE', 'RED', 'GREEN', 'BLUE',
    'ABOVE', 'BELOW', 'LEFT', 'RIGHT', 'OVER',

    # Audio
    'AudioTrack',
    'FileAudioClip',
    'Beep',

    # Input
    'KeyTrack',
    'Key',
    'ButtonChooser',
    'MouseTrack',
    'MouseButton',
    'MouseAxis',
    'LEFT_BUTTON',
    'MIDDLE_BUTTON',
    'RIGHT_BUTTON',

    # Pools
    'Pool',
    'TextPool',
    'ImagePool',
    'SoundPool',
    'PoolDict',
    'WordObject',

    # Utilities
    'mathDistract',

    # EEG
    'EEGTrack',

    # Base
    'Track',
    'LogTrack',

    # Exceptions
    'PyEPL3Error',
    'TrackError',
    'DisplayError',
    'AudioError',
    'InputError',
    'ConfigurationError',
    'TimingError',
    'PoolError',
]
