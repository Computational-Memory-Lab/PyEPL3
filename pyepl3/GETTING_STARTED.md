# PyEPL3 - Getting Started

## What is PyEPL3?

PyEPL3 is a modern Python 3 reimplementation of PyEPL (Python Experiment Programming Library), designed for running psychology and neuroscience experiments. It provides the core functionality needed for most experiments while being easier to install and maintain than the original PyEPL.

## What's Included (Tier 1 Features)

✅ **Experiment Framework**
- Session and subject management
- Configuration system
- Data archiving and organization
- State save/restore

✅ **Display System**
- Text rendering with fonts
- Image display with scaling
- Compound stimuli with flexible positioning
- Screen management and updates

✅ **Audio System**
- Multi-format audio playback (WAV, AIFF, etc.)
- Beep generation
- Precise timing synchronization

✅ **Input System**
- Keyboard input with event logging
- Mouse input support
- ButtonChooser for waiting on responses

✅ **Timing System**
- High-precision PresentationClock
- Virtual time management
- Jitter support
- Error tracking

✅ **Data Management**
- Pool system for stimulus collections
- Text, Image, and Sound pools
- Shuffling and sampling

✅ **EEG Support (Stub)**
- Event logging for EEG sync
- Ready for hardware integration

## Installation

```bash
cd pyepl3
pip install -e .
```

This will install PyEPL3 and all dependencies:
- pygame (graphics and input)
- Pillow (image processing)
- sounddevice (audio playback)
- soundfile (audio file I/O)
- numpy, scipy (data processing)

## Quick Example

```python
from pyepl3 import *

# Create experiment
exp = Experiment(name="MyExperiment", use_args=False)

# Create tracks
video = VideoTrack("video", resolution=(1024, 768))
keyboard = KeyTrack("keyboard")

# Start logging
video.startLogging()
keyboard.startLogging()

# Create clock
clock = PresentationClock()

# Show text
text = Text("Hello, World!", size=48, color=WHITE)
video.showCentered(text, clock)
video.updateScreen(clock)

# Wait for keypress
bc = ButtonChooser(Key("SPACE"))
bc.wait(clock)

# Clean up
video.stopLogging()
keyboard.stopLogging()
video.close()
```

## Running the Example Experiment

```bash
cd pyepl3
python example_experiment.py
```

This runs a simple paired-associate memory experiment that demonstrates:
- Showing instructions
- Study phase with word pairs
- Distractor task
- Test phase with intact/recombined pairs
- Response collection
- EEG markers

## File Structure

```
pyepl3/
├── setup.py              # Installation script
├── README.md             # Package overview
├── MIGRATION_GUIDE.md    # PyEPL → PyEPL3 conversion help
├── GETTING_STARTED.md    # This file
├── example_experiment.py # Full example experiment
├── test_basic.py        # Basic functionality test
└── pyepl3/              # Source code
    ├── __init__.py      # Main exports
    ├── base.py          # Base classes (Track, LogTrack)
    ├── timing.py        # PresentationClock and timing
    ├── experiment.py    # Experiment and Configuration
    ├── display.py       # VideoTrack, Image, Text
    ├── audio.py         # AudioTrack, sounds
    ├── keyboard.py      # Keyboard input
    ├── mouse.py         # Mouse input
    ├── pool.py          # Stimulus pools
    ├── eeg.py           # EEG stub
    └── exceptions.py    # Custom exceptions
```

## Core Concepts

### 1. Experiment Object

The `Experiment` object manages your experiment:

```python
exp = Experiment(name="MyExp", use_args=True)
```

- Parses command-line arguments (subject ID, session)
- Creates data directories
- Manages configuration
- Handles state save/restore

Run with: `python my_experiment.py <subject_id>`

### 2. Tracks

Tracks handle I/O and logging:

```python
video = VideoTrack("video", archive_dir=exp.getArchive())
keyboard = KeyTrack("keyboard", archive_dir=exp.getArchive())
audio = AudioTrack("audio", archive_dir=exp.getArchive())

# Start logging
video.startLogging()
keyboard.startLogging()
audio.startLogging()

# ... experiment ...

# Stop logging
video.stopLogging()
keyboard.stopLogging()
audio.stopLogging()
```

Each track creates a log file with timestamps for all events.

### 3. PresentationClock

The clock controls experiment timing:

```python
clock = PresentationClock()

# Show stimulus
video.showCentered(text, clock)
video.updateScreen(clock)

# Wait 2000ms
clock.delay(2000)

# Wait with jitter (±250ms)
clock.delay(1000, jitter=500)

# Random delay between 500-1500ms
clock.jitter(500, 1500)
```

### 4. Display System

Show stimuli on screen:

```python
# Text
text = Text("Hello", size=36, color=WHITE)
video.showCentered(text, clock)
video.updateScreen(clock)

# Image
image = Image("stim.jpg", propysize=0.3)  # 30% of screen height
video.show(image, (100, 100), clock)
video.updateScreen(clock)

# Remove stimuli
video.unshow(text)
video.unshowAll()
video.updateScreen(clock)

# Clear screen
video.clear(BLACK)
video.updateScreen(clock)
```

### 5. Input

Collect responses:

```python
# Single key
bc = ButtonChooser(Key("SPACE"), track=keyboard)
button, timestamp = bc.waitWithTime(clock)

# Multiple keys
bc = ButtonChooser(Key("Y"), Key("N"), track=keyboard)
button, timestamp = bc.waitWithTime(clock)

if button and button.key_name == "Y":
    print("Yes response")

# With timeout (5 seconds)
button, timestamp = bc.waitWithTime(clock, timeout=5000)
if button is None:
    print("Timeout!")
```

### 6. Audio

Play sounds:

```python
# From file
sound = FileAudioClip("beep.wav")
sound.present(clk=clock, track=audio, block=True)

# Generate beep
beep = Beep(frequency=440, duration_ms=500)
beep.present(clk=clock, track=audio)
```

### 7. Pools

Manage stimulus collections:

```python
# Text pool from file
words = TextPool("word_list.txt")
words.shuffle()

word1 = words.pop()
word2 = words.randomChoice()

# Image pool from directory
images = ImagePool("stimuli/")
images.shuffle()

# Filter
subset = words.findAllBy("category", "animal")
```

### 8. Configuration

Use configuration files:

```python
# In your experiment:
config = exp.getConfig()
n_trials = config.n_trials
study_time = config.study_time

# In config.py file:
n_trials = 100
study_time = 3000  # milliseconds
key_left = Key("LEFT")
key_right = Key("RIGHT")
```

## Logging Output

PyEPL3 creates structured data directories:

```
data/
└── <subject_id>/
    ├── state/              # Saved states
    ├── configbackup/       # Config backups
    └── session_<name>/     # Session data
        ├── video.vidlog    # Display events
        ├── keyboard.keylog # Key presses
        ├── audio.sndlog    # Audio events
        └── eeg.eeglog      # EEG sync events
```

Log files are tab-delimited with:
- Timestamp (milliseconds)
- Tick (within-timestamp ordering)
- Event type
- Event details

## Future Enhancements

These features will be added in future releases:

- **Audio Recording** - Microphone input
- **Joystick Support** - Full gamepad/joystick input
- **VR System** - 3D virtual environments
- **Hardware EEG** - Parallel port, scalp EEG interfaces
- **Advanced Timing** - Real-time thread priorities
- **VirtualTrack** - Log file merging

## Need Help?

1. **Migration:** See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for PyEPL → PyEPL3 conversion
2. **Examples:** Run [example_experiment.py](example_experiment.py) to see PyEPL3 in action
3. **Source Code:** The PyEPL3 source is well-commented and readable

## Hardware Requirements

- **Graphics:** Any display (tested with 800x600 to 1920x1080)
- **Audio:** Standard audio output (speakers/headphones)
- **Input:** Standard keyboard and mouse
- **EEG:** Currently logs events only; hardware support coming soon

## Tested On

- macOS (Apple Silicon and Intel)
- Python 3.7+
- pygame 2.0+

Should also work on Linux and Windows (not yet extensively tested).

## License

TBD

## Credits

PyEPL3 is a modern reimplementation inspired by the original PyEPL, developed for running psychology experiments with Python 3.
