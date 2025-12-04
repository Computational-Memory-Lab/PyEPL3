# Running PairAssoDevon with PyEPL3

## Overview

`PairAssoDevon_3_math.py` (and `PairAssoDevon_3_arrows.py`) are PyEPL3 adaptations of your paired associate recognition experiment. They include:

- **Sequential word presentation** (W1, then W2)
- **Item recognition test** (old vs. new words)
- **Associative recognition test** (intact vs. recombined pairs)
- **Distraction task** (math or arrow response variants)
- **EEG event logging**
- **Fixation cross** during inter-pair intervals

## Files Created

### Main Experiment
- `PairAssoDevon_3_math.py` - Main experiment script with math distractor
- `PairAssoDevon_3_arrows.py` - Alternative version with arrow response distractor
- `config_pairassoc.py` - Configuration file
- `pyepl3_helpers.py` - Helper functions (TextPool2, instruct, mathDistract2)

### Existing Files Used
- `instruct/instruct0.txt` - Practice instructions
- `instruct/instruct1.txt` - First round instructions
- `instruct/instructN.txt` - Subsequent round instructions
- `instruct/distractor.txt` - Distractor task instructions
- `instruct/recognition_noorder.txt` - Recognition test instructions
- `raw_pools/nouns.txt` - Word stimulus pool

## Installation

PyEPL3 is already installed. No additional setup needed!

## Running the Experiment

### Basic Test Run (No Subject ID)

For testing without subject argument:

```bash
cd /Users/devon7y/VS\ Code/pyepl_testing
python3 PairAssoDevon_3_math.py
```

This will run with default subject ID = 1.

### Full Experiment Run (With Subject)

```bash
cd /Users/devon7y/VS\ Code/PyEPL3
python3 PairAssoDevon_3_math.py <subject_id>
```

Or use the `-s` flag (compatible with original PyEPL):
```bash
python3 PairAssoDevon_3_math.py -s <subject_id>
```

Example:
```bash
python3 PairAssoDevon_3_math.py 101
python3 PairAssoDevon_3_math.py -s 101
```

The subject ID determines key counterbalancing (subject_id % 4).

## Experiment Flow

### 1. **Instructions**
- Practice round instructions (if RUN_PRACTICE = 1)
- Subsequent round instructions

### 2. **Study Phase**
For each of 16 pairs:
- Show word 1 for 2000ms
- Clear screen (0ms gap)
- Show word 2 for 2000ms
- Fixation cross (+) during jittered inter-pair interval (800-1200ms)

### 3. **Distractor Task**
Two variants available:

**Math Distractor** (`PairAssoDevon_3_math.py`):
- Addition problems with 3 numbers
- Type answer using number keys, press ENTER to submit
- 5 second response time per problem

**Arrow Distractor** (`PairAssoDevon_3_arrows.py`):
- Shows < or > arrow on screen
- Respond with `,` for left or `.` for right
- Response arrow shown below prompt
- Fixed response time per trial (D_RESP_TIME)

### 4. **Test Phase**
16 trials total (randomized order):
- **8 Item Recognition trials:**
  - 4 old words (from study)
  - 4 new words (foils)
  - Response: Z = OLD, / = NEW

- **8 Associative Recognition trials:**
  - 4 intact pairs (same as study)
  - 4 recombined pairs (words rearranged)
  - Response: Z = INTACT, / = RECOMBINED

**Note:** Words used in item recognition trials are never reused in associative recognition trials (and vice versa). Study pairs are split into two groups to ensure no overlap.

### 5. **Repeat**
- Repeat for NLISTS rounds (default = 3)

## Configuration Parameters

Edit `config_pairassoc.py` to adjust:

```python
NLISTS = 3          # Number of study-test rounds
RUN_PRACTICE = 1    # Include practice round (1) or not (0)
NPAIRS = 16         # Word pairs per list

PRES_TIME = 2000    # Word display duration (ms)
IPI_lower = 800     # Inter-pair interval min (ms)
IPI_upper = 1200    # Inter-pair interval max (ms)

NDIST = 20          # Number of distractor problems
C_RESP_TIME = 5000  # Recognition response time (ms)

keyLeft = "Z"       # Left response key
keyRight = "/"      # Right response key

fullscreen = False  # Windowed mode for testing
resolution = (1024, 768)
```

## Data Output

Data is saved to:
```
data/<subject_id>/session_<name>/
├── video.vidlog      # Display events
├── key.keylog        # Keyboard responses
├── eeg.eeglog        # EEG sync events
├── session.log       # Detailed trial data
├── stimlog.log       # Stimulus IDs (for scoring)
└── recoglog.log      # Recognition responses
```

### Log File Formats

**session.log** - Main event log:
```
timestamp  tick  event_data
```

Study phase events:
```
list_num  pair_num  word1  word1_id  word2  word2_id  IPI
```

Test phase events:
```
list_num  trial_num  ITEM  word  word_id  target  response  accuracy  RT
list_num  trial_num  ASSOC  word1  word1_id  word2  word2_id  target  response  accuracy  RT
```

**recoglog.log** - Recognition responses (numeric IDs only):
```
list_num  trial_num  type  [word_ids]  target  response  accuracy  RT
```

## Response Keys

### Item Recognition
- **Z** = OLD (word was studied)
- **/** = NEW (word is a foil)

### Associative Recognition
- **Z** = INTACT (pair studied together)
- **/** = RECOMBINED (words studied but not together)

### Experimenter Controls
- **SPACE** = Continue from instructions
- **LEFT SHIFT + RIGHT SHIFT** = Skip current study trial (hidden)
- **ESC + F1** = Emergency exit

## Differences from Original PyEPL Version

### Python 3 Syntax
- ✅ Print functions instead of statements
- ✅ Modern string formatting (f-strings)
- ✅ `with` statements for file opening
- ✅ No `exec` statements

### Display System
- ✅ Explicit `updateScreen()` calls
- ✅ `show_proportional()` helper function for positioning
- ✅ Separate stimulus creation and display

### Input System
- ✅ `ButtonChooser.waitWithTime()` returns (button, timestamp)
- ✅ Calculate RT manually: `rt = button_time - pres_time`
- ✅ Check `button.key_name` for response

### Helper Functions
- ✅ `TextPool2` - Enhanced pool with `isInPool()` method
- ✅ `instruct()` - Shows instructions, waits for SPACE
- ✅ `mathDistract2()` - Math distraction task
- ✅ `Font()` - Font path helper

## Recent Changes

### Bug Fixes
- **Math distractor input**: Fixed to properly accept digit keys (0-9) and show user input on screen
- **Clock timing**: Fixed timing bugs that caused freezes when virtual time drifted from real time
- **Subject ID argument**: `-s` flag now works for subject ID (compatible with original PyEPL)

### New Features
- **Arrow distractor variant**: `PairAssoDevon_3_arrows.py` - respond to arrow direction instead of math
- **Fixation cross**: Shows "+" during inter-pair intervals instead of blank screen
- **Skip trials**: Press LEFT SHIFT + RIGHT SHIFT to skip study phase trials (for testing)
- **No word overlap**: Words in item recognition trials are never reused in associative trials

## Troubleshooting

### "No such file or directory: raw_pools/nouns.txt"
Make sure you're running from the correct directory:
```bash
cd /Users/devon7y/VS\ Code/pyepl_testing
```

### "No VideoTrack found"
The helper functions expect a VideoTrack to exist. Make sure the experiment creates tracks before calling `instruct()` or `mathDistract2()`.

### Keys not responding
- Check that the correct keys are configured in `config_pairassoc.py`
- On some keyboards, "/" might be a different key
- Try using `SLASH` instead of "/" if needed

### Window not appearing
If running headless or on remote server:
- Set `fullscreen = False` in config
- Make sure X11 forwarding is enabled (if SSH)
- Or run locally with display

## Testing the Experiment

### Quick Test (Minimal)

Edit `config_pairassoc.py` temporarily:
```python
NLISTS = 1          # Just one round
RUN_PRACTICE = 0    # Skip practice
NPAIRS = 2          # Just 2 pairs
NDIST = 2           # Just 2 distractor problems
```

This will create:
- 2 study pairs (4 words total)
- 2 distractor problems
- 8 test trials (2 item old, 2 item new, 2 assoc intact, 2 assoc recombined)

### Full Practice Run

```python
NLISTS = 1
RUN_PRACTICE = 1    # Include practice
NPAIRS = 16
NDIST = 20
```

## Next Steps

### EEG Hardware Integration

The experiment currently logs EEG events to `eeg.eeglog`. To add hardware sync:

1. Determine your sync method (parallel port, audio pulse, serial)
2. Extend `EEGTrack` in PyEPL3
3. Add sync pulses at key events:
   - Study word onset
   - Test stimulus onset
   - Response events

### Custom Modifications

To modify the experiment:

1. **Change timing:** Edit values in `config_pairassoc.py`
2. **Change stimuli:** Replace `raw_pools/nouns.txt` with your word list
3. **Change test format:** Modify test trial creation in main script
4. **Add EEG markers:** Add `eeg.alignmentMarker()` calls at key events

## Support

If you encounter issues:
1. Check this guide
2. Review error messages carefully
3. Test with minimal config (NPAIRS=2, NDIST=2)
4. Ask me for help!

Good luck with your experiment! 🧠
