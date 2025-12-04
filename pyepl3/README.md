# PyEPL3 - Python Experiment Programming Library for Python 3

A modern reimplementation of PyEPL (Python Experiment Programming Library) with full Python 3 support.

## Features

- **Experiment Framework**: Configuration management, session handling, data archiving
- **Display System**: Images, text, compound stimuli with flexible positioning
- **Audio System**: Multi-format playback with precise timing
- **Input System**: Keyboard, mouse with mechanical input abstractions
- **Logging**: Comprehensive event logging with timestamps
- **Timing**: High-precision PresentationClock for experiment timing
- **Pool Management**: Stimulus collections with filtering and randomization

## Installation

```bash
cd pyepl3
pip install -e .
```

## Quick Start

```python
from pyepl3 import Experiment, VideoTrack, KeyTrack, PresentationClock
from pyepl3 import Text, Image, Key, ButtonChooser

# Initialize experiment
exp = Experiment()
config = exp.getConfig()

# Create tracks
video = VideoTrack("video")
keyboard = KeyTrack("keyboard")

# Create clock
clock = PresentationClock()

# Display text
text = Text("Hello, World!")
text.present(clk=clock, duration=2000)

# Wait for keypress
bc = ButtonChooser(Key("SPACE"))
button, timestamp = bc.waitWithTime(clk=clock)
```

## Tier 1 Features (Current)

- ✅ Core experiment framework
- ✅ Display system (images, text, positioning)
- ✅ Audio playback
- ✅ Keyboard/mouse input with ButtonChooser
- ✅ Pool management
- ✅ Logging system with LogTrack
- ✅ PresentationClock with error correction
- ✅ mathDistract utility for distractor tasks

## Future Features

- EEG synchronization (pulse-based and hardware)
- Audio recording
- Joystick support
- VR/3D environment
- Advanced mechanical input features

## Compatibility

PyEPL3 aims to provide a similar API to original PyEPL where practical, allowing existing experiments to be migrated with minimal changes.

### Command Line Arguments
- Subject ID can be passed as positional argument or with `-s` flag (compatible with original PyEPL)
- Session name can be passed with `--session` flag

## Recent Bug Fixes

- **PresentationClock timing**: Fixed error correction in `wait()` that could cause freezes when virtual time drifted from real time. The clock now properly synchronizes `_real_base` when correcting timing drift.
- **mathDistract numeric input**: Fixed to properly accept digit keys (0-9), backspace, and minus sign. User input is now displayed on screen in real-time.
- **Experiment argument parsing**: Fixed `-s` flag to work for subject ID (like original PyEPL) instead of session name.

## License

TBD
