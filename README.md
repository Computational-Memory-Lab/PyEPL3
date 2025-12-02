# PyEPL3

**Python Experiment Programming Library for Python 3**

PyEPL3 is a modern reimplementation of PyEPL with full Python 3 support, designed for creating psychology and neuroscience experiments.

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
A complete example experiment is included:
- **PairAssoDevon_pyepl3.py** - Full paired associate recognition experiment
- **PairAssoDevon_3.py** - Converted version from original PyEPL

Run the experiment:
```bash
python PairAssoDevon_pyepl3.py -s 1001
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
├── pyepl3/              # Main PyEPL3 library
│   └── pyepl3/
│       ├── __init__.py
│       ├── experiment.py
│       ├── display.py
│       ├── keyboard.py
│       ├── pool.py
│       ├── utils.py     # mathDistract, etc.
│       └── ...
├── PairAssoDevon_pyepl3.py  # Example experiment
├── config_pairassoc.py       # Example config
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

## Contributing

Contributions welcome! This is a community-maintained project for psychology and neuroscience researchers.

## License

BSD-3-Clause (same as original PyEPL)

## Credits

- Original PyEPL by Per Sederberg and others
- PyEPL3 modernization and Python 3 port

## Support

For issues and questions: https://github.com/Computational-Memory-Lab/PyEPL3
