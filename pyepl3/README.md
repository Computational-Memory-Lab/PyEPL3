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
- ✅ Keyboard/mouse input
- ✅ Pool management
- ✅ Logging system
- ✅ PresentationClock

## Future Features

- EEG synchronization (pulse-based and hardware)
- Audio recording
- Joystick support
- VR/3D environment
- Advanced mechanical input features

## Compatibility

PyEPL3 aims to provide a similar API to original PyEPL where practical, allowing existing experiments to be migrated with minimal changes.

## License

TBD
