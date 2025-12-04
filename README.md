# PyEPL3

**Python Experiment Programming Library for Python 3**

PyEPL3 is a modern Python 3 port of the original PyEPL (Python Experiment Programming Library), designed for creating psychology and neuroscience experiments with precise timing and stimulus control.

## About PyEPL

This library is based on the original PyEPL developed by Geller et al. (2007):

> Geller, A. S., Schleifer, I. K., Sederberg, P. B., Jacobs, J., & Kahana, M. J. (2007). *PyEPL: A cross-platform experiment-programming library*. Behavior Research Methods, 39(4), 950-958. [https://doi.org/10.3758/BF03192990](https://link.springer.com/article/10.3758/BF03192990)

PyEPL3 modernizes the original framework for Python 3, while maintaining compatibility with the core experimental design patterns.

## Features

- ✅ **Full Python 3 support** - Modern Python syntax and libraries
- ✅ **Video display** - Flexible text and image presentation with precise timing
- ✅ **Keyboard input** - Response collection with timestamps
- ✅ **EEG integration** - EEG event logging and synchronization
- ✅ **Stimulus pools** - Easy management of word lists, images, and sounds
- ✅ **Logging system** - Automatic logging of all experimental events
- ✅ **Math distractor** - Built-in math distractor task
- ✅ **Presentation clock** - Precise timing control for experiments

## Installation

### Requirements
- Python 3.8+
- pygame 2.x
- numpy
- Pillow

### Install PyEPL3

```bash
cd pyepl3
pip install -e .
```

## Quick Start

```python
from pyepl3 import (
    Experiment, VideoTrack, KeyTrack, PresentationClock,
    Text, WHITE, BLACK
)

# Create experiment
exp = Experiment(name="MyExperiment")
exp.loadConfig("config.py")

# Create tracks
archive_dir = exp.getArchive()
video = VideoTrack("video", archive_dir=archive_dir)
keyboard = KeyTrack("keyboard", archive_dir=archive_dir)

# Start logging
video.startLogging()
keyboard.startLogging()

# Create clock
clock = PresentationClock()

# Show text
text = Text("Hello, World!", size=48, color=WHITE)
video.clear(BLACK)
video.showCentered(text, clock)
video.updateScreen(clock)

# Wait for keypress
from pyepl3 import Key, ButtonChooser
bc = ButtonChooser(Key("SPACE"), track=keyboard)
button, timestamp = bc.waitWithTime(clock)

# Clean up
video.stopLogging()
keyboard.stopLogging()
video.close()
```

## Example Experiments

### Paired Associate Recognition Task
Complete example experiments are included:
- **PairAssoDevon_3_math.py** - Paired associate recognition with math distractor
- **PairAssoDevon_3_arrows.py** - Paired associate recognition with arrow response distractor

Run the experiment:
```bash
python PairAssoDevon_3_math.py -s 1001
python PairAssoDevon_3_arrows.py -s 1001
```

## API Overview

### Core Components

- **Experiment** - Main experiment management
- **VideoTrack** - Display and visual presentation
- **KeyTrack** - Keyboard input
- **AudioTrack** - Audio playback
- **EEGTrack** - EEG event logging
- **LogTrack** - General-purpose logging

### Stimulus Objects

- **Text** - Text display with font, size, color
- **Image** - Image display
- **CompoundStimulus** - Combined stimuli

### Utilities

- **TextPool** - Word list management with `.name` attribute and `isInPool()`
- **mathDistract()** - Math distractor task
- **PresentationClock** - Precise timing control

### Built-in Features

PyEPL3 includes features that previously required helper files:
- `TextPool` with `isInPool()` method
- `video.showInstructions()` for instruction screens
- `mathDistract()` for distractor tasks
- Automatic `WordObject` conversion with `.name` attribute

## Configuration

Create a `config.py` file:

```python
# Experiment parameters
NLISTS = 1
NPAIRS = 16
PRES_TIME = 2000  # milliseconds

# Response keys
keyLeft = "Z"
keyRight = "/"

# Display
fullscreen = False
resolution = (1024, 768)
```

## Architecture

```
PyEPL3/
├── pyepl3/                    # Main PyEPL3 library
│   └── pyepl3/
│       ├── __init__.py
│       ├── experiment.py
│       ├── display.py
│       ├── keyboard.py
│       ├── pool.py
│       ├── utils.py           # mathDistract, etc.
│       └── ...
├── PairAssoDevon_3_math.py    # Example: math distractor
├── PairAssoDevon_3_arrows.py  # Example: arrow distractor
├── config_pairassoc.py        # Example config
└── README.md
```

## Migration from PyEPL

Key differences from original PyEPL:

### Presentation Model
**Old (PyEPL):**
```python
ts, b, rt = stim.present(clk=clk, duration=2000, bc=bc)
```

**New (PyEPL3):**
```python
video.showCentered(stim, clock)
pres_time = video.updateScreen(clock)
button, timestamp = bc.waitWithTime(clock, timeout=2000)
rt = timestamp - pres_time
```

### Built-in Features
No need for separate helper files - TextPool, mathDistract, and instruct are built-in.

## Implementation Status

### Currently Implemented (Tier 1)

PyEPL3 includes all core features needed for most psychology experiments:

- ✅ **Experiment framework** - Session management, configuration, data archiving
- ✅ **Display system** - Text, images, flexible positioning, precise timing
- ✅ **Audio playback** - Multi-format file playback, beep generation
- ✅ **Keyboard input** - Key tracking, response collection, timestamps
- ✅ **Mouse input** - Button and position tracking
- ✅ **Timing system** - PresentationClock with millisecond precision
- ✅ **Stimulus pools** - TextPool, ImagePool, SoundPool with filtering/sampling
- ✅ **Logging system** - Automatic event logging for all tracks
- ✅ **EEG markers** - Event logging and timestamps (ready for hardware integration)

### Not Yet Implemented

The following features from the original PyEPL are planned for future releases:

- ❌ **Audio recording** - Microphone input (e.g., for verbal response recording)
- ❌ **Joystick/gamepad support** - For specialized input devices
- ❌ **Hardware EEG synchronization** - Parallel port or audio pulse sync
- ❌ **VR/3D environments** - Specialized display modes
- ❌ **VirtualTrack** - Advanced log file merging

For most memory and cognitive experiments, the currently implemented features (Tier 1) are sufficient. Additional features can be added as needed—contact us if you require specific functionality.

See [PYEPL3_BUILD_SUMMARY.md](PYEPL3_BUILD_SUMMARY.md) for detailed implementation notes.

## Contributing

Contributions welcome! This is a community-maintained project for psychology and neuroscience researchers.

## License

BSD-3-Clause (same as original PyEPL)

## Credits

### Original PyEPL
- **Aaron S. Geller**
- **Ian K. Schleifer**
- **Per B. Sederberg**
- **Joshua Jacobs**
- **Michael J. Kahana**

Citation: Geller, A. S., Schleifer, I. K., Sederberg, P. B., Jacobs, J., & Kahana, M. J. (2007). PyEPL: A cross-platform experiment-programming library. *Behavior Research Methods*, 39(4), 950-958.

### PyEPL3 Port
- Python 3 modernization and enhanced features
- Maintained by the Computational Memory Lab

## Support

For issues and questions: https://github.com/Computational-Memory-Lab/PyEPL3
