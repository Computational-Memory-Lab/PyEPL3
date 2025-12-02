## PyEPL to PyEPL3 Migration Guide

This guide helps you convert experiments from PyEPL (Python 2) to PyEPL3 (Python 3).

### Quick Start

**Old PyEPL:**
```python
from pyepl.locals import *

exp = Experiment()
vt = VideoTrack("video")
kt = KeyTrack("key")
clk = PresentationClock()

stim = Text("Hello")
stim.present(clk=clk, duration=2000)
```

**New PyEPL3:**
```python
from pyepl3 import *

exp = Experiment()
video = VideoTrack("video")
keyboard = KeyTrack("keyboard")
clock = PresentationClock()

text = Text("Hello")
video.showCentered(text, clock)
video.updateScreen(clock)
clock.delay(2000)
```

---

### Major Differences

#### 1. Import Changes

**Old:**
```python
from pyepl.locals import *
```

**New:**
```python
from pyepl3 import *
# Or import specific classes:
from pyepl3 import Experiment, VideoTrack, KeyTrack, PresentationClock
```

#### 2. Display System

**Old PyEPL:**
```python
stim = Text("Hello World")
timestamp, button, rt = stim.present(clk=clk, duration=2000, bc=bc)
```

**New PyEPL3:**
```python
text = Text("Hello World")
video.showCentered(text, clock)
video.updateScreen(clock)

# For timed presentation:
clock.delay(2000)

# Or with button chooser:
bc = ButtonChooser(Key("SPACE"))
button, timestamp = bc.waitWithTime(clock, timeout=2000)
```

**Key changes:**
- Stimuli don't present themselves; use `VideoTrack.show()` or `showCentered()`
- Must call `updateScreen()` after showing stimuli
- Use `clock.delay()` for timed presentations
- Button waiting is separate from presentation

#### 3. Keyboard Input

**Old:**
```python
bc = ButtonChooser(Key("SPACE"))
timestamp, button, rt = bc.wait(clk=clk)
```

**New:**
```python
bc = ButtonChooser(Key("SPACE"), track=keyboard)
button, timestamp = bc.waitWithTime(clock)
```

**Key changes:**
- Can optionally pass `track` parameter for logging
- Returns `(button, timestamp)` instead of `(timestamp, button, rt)`
- Calculate RT yourself: `rt = timestamp - start_time`

#### 4. Audio

**Old:**
```python
sound = FileAudioClip("beep.wav")
sound.present(clk=clk)
```

**New:**
```python
sound = FileAudioClip("beep.wav")
sound.present(clk=clock, track=audio)
```

**Key changes:**
- Optionally pass `track` parameter for logging
- Use `block=True` (default) to wait for playback, `block=False` for async

#### 5. Pools

**Old:**
```python
pool = TextPool("words.txt")
shuffle(pool)
word = pool.pop(0)
```

**New:**
```python
pool = TextPool("words.txt")
pool.shuffle()
word = pool.pop(0)
```

**Key changes:**
- Pools have a `.shuffle()` method (no need for external shuffle)
- Otherwise mostly compatible

#### 6. Configuration

**Old:**
```python
config = exp.getConfig()
value = config.some_setting
```

**New:**
```python
config = exp.getConfig()
value = config.some_setting  # Same!

# Can also use dictionary access:
value = config['some_setting']
```

**Key changes:**
- Configuration works the same
- Config files are still Python files
- Can use attribute or dictionary access

#### 7. EEG

**Old:**
```python
eeg = EEGTrack("eeg")
eeg.pulse()
```

**New:**
```python
eeg = EEGTrack("eeg")
eeg.pulse(clock)  # Pass clock for timing

# Alignment markers:
eeg.alignmentMarker("TRIAL_START", clock)
```

**Key changes:**
- Stub implementation for now (logs events)
- Hardware implementations (parallel port, etc.) coming later
- Pass clock for consistent timing

---

### Python 2 to Python 3 Syntax Changes

#### Print Statements → Print Functions

**Old:**
```python
print "Hello"
print "Value:", x
```

**New:**
```python
print("Hello")
print("Value:", x)
# Or use f-strings:
print(f"Value: {x}")
```

#### String Formatting

**Old:**
```python
msg = '%s\t%d' % ('TEXT', 123)
```

**New:**
```python
msg = f'{text}\t{number}'
# Or:
msg = '{}\t{}'.format('TEXT', 123)
```

#### Dictionary Methods

**Old:**
```python
for key, value in dict.iteritems():
    pass

if dict.has_key(key):
    pass
```

**New:**
```python
for key, value in dict.items():
    pass

if key in dict:
    pass
```

#### Integer Division

**Old:**
```python
result = 10 / 3  # Returns 3 (integer division)
```

**New:**
```python
result = 10 // 3  # Returns 3 (integer division)
result = 10 / 3   # Returns 3.333... (float division)
```

#### Exec Statement

**Old:**
```python
exec "from module import *"
```

**New:**
```python
# Use importlib instead:
import importlib
module = importlib.import_module('module_name')
```

---

### Complete Example Migration

**Original PyEPL Experiment:**
```python
from pyepl.locals import *

exp = Experiment()
exp.setBreak()
config = exp.getConfig()

vt = VideoTrack("video")
kt = KeyTrack("key")
log = LogTrack("session")

clk = PresentationClock()
vt.clear("black")

# Study phase
for word in word_list:
    stim = Text(word)
    ts, b, rt = stim.present(clk=clk, duration=2000)
    log.logMessage('WORD\t%s' % word, clk)
    clk.delay(500)

# Test phase
bc = ButtonChooser(Key("Y"), Key("N"))
for word in test_list:
    stim = Text(word)
    ts, b, rt = stim.present(clk=clk, bc=bc)
    log.logMessage('RESPONSE\t%s\t%s' % (word, b), clk)
```

**Migrated to PyEPL3:**
```python
from pyepl3 import *

exp = Experiment()
exp.setBreak()
config = exp.getConfig()

video = VideoTrack("video", archive_dir=exp.getArchive())
keyboard = KeyTrack("keyboard", archive_dir=exp.getArchive())

video.startLogging()
keyboard.startLogging()

clock = PresentationClock()
video.clear(BLACK)
video.updateScreen(clock)

# Study phase
for word in word_list:
    text = Text(word)
    video.showCentered(text, clock)
    ts = video.updateScreen(clock)

    keyboard.logMessage(f'WORD\t{word}', ts)

    clock.delay(2000)
    video.unshowAll()
    video.updateScreen(clock)
    clock.delay(500)

# Test phase
bc = ButtonChooser(Key("Y"), Key("N"), track=keyboard)
for word in test_list:
    text = Text(word)
    video.showCentered(text, clock)
    video.updateScreen(clock)

    button, timestamp = bc.waitWithTime(clock)
    keyboard.logMessage(f'RESPONSE\t{word}\t{button.key_name}', timestamp)

    video.unshowAll()
    video.updateScreen(clock)

video.stopLogging()
keyboard.stopLogging()
video.close()
```

---

### Track Archive Directories

In PyEPL3, tracks should be told where to save their log files:

```python
# Create experiment first
exp = Experiment(use_args=True)

# Pass archive directory to tracks
archive_dir = exp.getArchive()

video = VideoTrack("video", archive_dir=archive_dir)
keyboard = KeyTrack("keyboard", archive_dir=archive_dir)
audio = AudioTrack("audio", archive_dir=archive_dir)

# Start logging
video.startLogging()
keyboard.startLogging()
audio.startLogging()

# ... experiment code ...

# Stop logging
video.stopLogging()
keyboard.stopLogging()
audio.stopLogging()
```

---

### Not Yet Implemented (Future)

These features are planned but not yet in Tier 1:

- **Audio Recording** - Microphone input
- **Joystick Support** - Full joystick/gamepad input
- **VR System** - 3D virtual reality environments
- **Advanced Mechanical Input** - Throttled rollers, complex combinations
- **Hardware EEG** - Parallel port, scalp EEG interfaces
- **VirtualTrack** - Merging multiple log tracks

For now, focus on core features: display, audio playback, keyboard/mouse, timing, and basic EEG logging.

---

### Getting Help

If you encounter issues migrating your experiment:

1. Check this guide for common patterns
2. Look at [example_experiment.py](example_experiment.py) for a complete example
3. Review the PyEPL3 source code (it's well-commented)
4. Test incrementally - migrate one section at a time

Good luck with your migration!
