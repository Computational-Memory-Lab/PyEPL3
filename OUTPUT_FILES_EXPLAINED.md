# Experiment Output Files Explained (Subject 6969)

## Overview
When you run `PairAssoDevon_refactored.py -s 6969`, PyEPL automatically creates a subject directory `6969/` (or `data/6969/`) with all experiment output files. Here's what each file contains and why it's important.

---

## Directory Contents

```
6969/
├── config.py               [Configuration parameters]
├── configbackup/           [Config version history]
├── sconfig.py              [Session-specific config]
├── sconfigbackup/          [Session config history]
├── state/                  [Experiment state data]
├── session.log             [PRIMARY DATA: Human-readable experiment log]
├── recoglog.log            [PRIMARY DATA: Recognition test results]
├── stimlog.log             [PRIMARY DATA: Stimulus presentation log]
├── eeg.eeglog              [EEG timing markers]
├── key.keylog              [All keyboard presses]
├── video.vidlog            [Video display timing]
├── instruct.log            [Instruction screen timing]
├── math_distract.log       [Math distractor responses]
└── experiment.log          [General experiment events]
```

---

## PRIMARY DATA FILES (Most Important)

### 1. **session.log** - Main Experiment Log (Human-Readable)

**Purpose:** Complete human-readable record of all experimental events.

**Format:** Tab-delimited columns
```
timestamp  msoffset  event_type  [event-specific columns]
```

**Study Phase Entries (Lines 3-10):**
```
1763075838106  0  1  1  SQUIRREL  407  ANCHOR  8  2  718
│              │  │  │  │         │    │       │  │  │
│              │  │  │  │         │    │       │  │  └─ IPI duration (ms)
│              │  │  │  │         │    │       │  └─── Last digit unknown
│              │  │  │  │         │    │       └────── Word2 ID
│              │  │  │  │         │    └────────────── Word2
│              │  │  │  │         └─────────────────── Word1 ID
│              │  │  │  └───────────────────────────── Word1
│              │  │  └──────────────────────────────── Pair number
│              │  └─────────────────────────────────── List number
│              └────────────────────────────────────── Millisecond offset
└───────────────────────────────────────────────────── Unix timestamp
```

**Example Study Entry:**
- **List 1, Pair 1:** SQUIRREL (ID 407) + ANCHOR (ID 8)
- **IPI:** 718ms (jittered delay between pairs)

**Test Phase Entries (Lines 11-18):**

**Associative Recognition:**
```
1763075882718  0  1  1  7  7  KITCHEN  210  SERIES  386  1  1  1  0  3647
│              │  │  │  │  │  │        │    │       │    │  │  │  │  │
│              │  │  │  │  │  │        │    │       │    │  │  │  │  └─ RT (ms)
│              │  │  │  │  │  │        │    │       │    │  │  │  └──── Accuracy (0/1)
│              │  │  │  │  │  │        │    │       │    │  │  └─────── Response (1=INTACT, 0=RECOMBINED, -1=timeout)
│              │  │  │  │  │  │        │    │       │    │  └────────── Target (1=INTACT, 0=RECOMBINED)
│              │  │  │  │  │  │        │    │       │    └───────────── Word2 ID
│              │  │  │  │  │  │        │    │       └────────────────── Word2
│              │  │  │  │  │  │        │    └────────────────────────── Word1 ID
│              │  │  │  │  │  │        └─────────────────────────────── Word1
│              │  │  │  │  │  └──────────────────────────────────────── Pair number (study)
│              │  │  │  │  └─────────────────────────────────────────── Pair number (study)
│              │  │  │  └────────────────────────────────────────────── Trial number (test)
│              │  │  └───────────────────────────────────────────────── List number
│              │  └──────────────────────────────────────────────────── Millisecond offset
└─────────────────────────────────────────────────────────────────────── Unix timestamp
```

**Example Test Entry:**
- **Trial 1:** KITCHEN + SERIES (Pair 7) shown
- **Target:** 1 (INTACT pair from study)
- **Response:** 1 (participant said INTACT)
- **Accuracy:** 0 (INCORRECT - they got it wrong!)
- **RT:** 3647ms

**Item Recognition:**
```
1763075886270  0  1  2  8  1  FEELING  156  ANCHOR  8  2  0  0  0  3285
│              │  │  │  │  │  │        │    │       │  │  │  │  │  │
│              │  │  │  │  │  │        │    │       │  │  │  │  │  └─ RT (ms)
│              │  │  │  │  │  │        │    │       │  │  │  │  └──── Accuracy (0/1)
│              │  │  │  │  │  │        │    │       │  │  │  └─────── Response (1=OLD, 0=NEW)
│              │  │  │  │  │  │        │    │       │  │  └────────── Target (1=OLD, 0=NEW)
│              │  │  │  │  │  │        │    │       │  └───────────── Word2 ID (for assoc only)
│              │  │  │  │  │  │        │    │       └────────────────── Word2
│              │  │  │  │  │  │        │    └────────────────────────── Word1 ID
│              │  │  │  │  │  │        └─────────────────────────────── Word1
│              │  │  │  │  │  └──────────────────────────────────────── Unknown counter
│              │  │  │  │  └─────────────────────────────────────────── Unknown counter
│              │  │  │  └────────────────────────────────────────────── Trial number
│              │  │  └───────────────────────────────────────────────── List number
│              │  └──────────────────────────────────────────────────── Millisecond offset
└─────────────────────────────────────────────────────────────────────── Unix timestamp
```

**Example Item Entry:**
- **Trial 2:** FEELING + ANCHOR shown (recombined from two different pairs)
- **Target:** 2 (appears to be recombined pair code)
- **Response:** 0 (NEW/RECOMBINED)
- **Accuracy:** 0 (INCORRECT)
- **RT:** 3285ms

---

### 2. **recoglog.log** - Recognition Test Data (Machine-Readable)

**Purpose:** Compact, machine-readable version of recognition test results for easier data analysis.

**Format:** Same structure as session.log test phase, but uses **word IDs instead of word text**.

**Example Entry:**
```
1763075882718  0  1  1  7  7  210  386  1  1  1  0  3647
│              │  │  │  │  │  │    │    │  │  │  │  │
│              │  │  │  │  │  │    │    │  │  │  │  └─ RT (ms)
│              │  │  │  │  │  │    │    │  │  │  └──── Accuracy
│              │  │  │  │  │  │    │    │  │  └─────── Response
│              │  │  │  │  │  │    │    │  └────────── Target
│              │  │  │  │  │  │    │    └───────────── Word2 ID
│              │  │  │  │  │  │    └────────────────── Word1 ID
│              │  │  │  │  │  └─────────────────────── Pair number
│              │  │  │  │  └────────────────────────── Pair number
│              │  │  │  └───────────────────────────── Trial number
│              │  │  └──────────────────────────────── List number
│              │  └─────────────────────────────────── Millisecond offset
└────────────────────────────────────────────────────── Unix timestamp
```

**Why it exists:** Easier for statistical software (R, Python, MATLAB) to process IDs than text strings.

**Latest run (lines 26-42) shows ITEM vs ASSOC explicitly:**
```
1763080217492  0  1  1  ITEM  101  1  1  1  4587
│              │  │  │  │     │    │  │  │  │
│              │  │  │  │     │    │  │  │  └─ RT
│              │  │  │  │     │    │  │  └──── Accuracy
│              │  │  │  │     │    │  └─────── Response
│              │  │  │  │     │    └────────── Target
│              │  │  │  │     └─────────────── Word ID
│              │  │  │  └───────────────────── Trial type (ITEM/ASSOC)
│              │  │  └──────────────────────── Trial number
│              │  └─────────────────────────── List number
│              └────────────────────────────── Millisecond offset
└───────────────────────────────────────────── Unix timestamp
```

---

### 3. **stimlog.log** - Stimulus Presentation Log

**Purpose:** Compact log of **what was shown during study phase** (for scoring and analysis).

**Format:** Machine-readable, IDs only (no word text).

**Example Entry:**
```
1763075838106  0  1  1  407  8  2  718
│              │  │  │  │    │  │  │
│              │  │  │  │    │  │  └─ IPI duration (ms)
│              │  │  │  │    │  └──── Unknown parameter
│              │  │  │  │    └─────── Word2 ID
│              │  │  │  └──────────── Word1 ID
│              │  │  └─────────────── Pair number
│              │  └────────────────── List number
│              └───────────────────── Millisecond offset
└──────────────────────────────────── Unix timestamp
```

**Why it exists:** Fast lookup of "what pairs did the participant study?" for scoring algorithms.

---

## TIMING & SYNCHRONIZATION FILES

### 4. **eeg.eeglog** - EEG Synchronization Markers

**Purpose:** Synchronize experiment events with EEG recording system.

**Format:** Timing pulses sent to EEG amplifier

**Example:**
```
1763075656601  0  EXPSTART_TRAIN
1763075656601  1  TRAIN_UP
1763075656611  1  TRAIN_DN
1763075656621  1  TRAIN_UP
...
```

**Key Events:**
- `EXPSTART_TRAIN` - Experiment starts, begin calibration pulse train
- `TRAIN_UP` / `TRAIN_DN` - Calibration pulses (alternating high/low)
- Additional markers sent at word onsets, responses, etc.

**Why it exists:** Allows researchers to align EEG brainwave data with specific experimental events (e.g., "what were the brain waves when they saw SQUIRREL?").

---

### 5. **key.keylog** - Keyboard Input Log

**Purpose:** Record every single keypress with precise timing.

**Format:**
```
timestamp  msoffset  event  key
```

**Example:**
```
1763075835598  0  P  RETURN          ← Key pressed
1763075835686  0  R  RETURN          ← Key released
1763075865247  0  P  6               ← Press "6"
1763075865367  0  R  6               ← Release "6"
1763075882464  0  P  Z               ← Press "Z" (LEFT response)
1763075882552  0  R  Z               ← Release "Z"
```

**Event codes:**
- `P` = Key press
- `R` = Key release

**Why it exists:**
- Precise reaction time measurement
- Verify participant responses
- Detect accidental key presses
- Quality control

---

### 6. **video.vidlog** - Display Timing Log

**Purpose:** Record when things appeared/disappeared on screen.

**Size:** 224 KB (binary format, not human-readable)

**Contains:**
- Word presentation timestamps
- Screen refresh synchronization
- Display buffer swaps
- Visual onset/offset times

**Why it exists:** Ensures accurate timing for cognitive research (millisecond precision matters).

---

## TASK-SPECIFIC LOGS

### 7. **math_distract.log** - Distractor Task Performance

**Purpose:** Record responses to math problems during the distractor phase.

**Format:**
```
timestamp  msoffset  event  problem         response  correct  timeout  RT
```

**Example:**
```
1763075863397  0  PROB  '2 + 7 + 7 = '  '67'     0        5000    2684
│              │  │     │               │        │        │       │
│              │  │     │               │        │        │       └─ Reaction time
│              │  │     │               │        │        └───────── Max allowed time
│              │  │     │               │        └────────────────── Correct? (0=no, 1=yes)
│              │  │     │               └─────────────────────────── Participant's answer
│              │  │     └─────────────────────────────────────────── Math problem
│              │  └───────────────────────────────────────────────── Event type (PROB)
│              └──────────────────────────────────────────────────── Millisecond offset
└─────────────────────────────────────────────────────────────────── Unix timestamp
```

**Example Problems:**
- `2 + 7 + 7 = ?` → Answered "67" (WRONG, should be 16)
- `7 + 5 + 2 = ?` → No answer (timed out)
- `5 + 7 + 7 = ?` → Answered "4" (WRONG, should be 19)

**Why it exists:**
- Verify participant was engaged during distractor phase
- Ensures sufficient interference between study and test
- Quality control (detect inattentive participants)

---

### 8. **instruct.log** - Instruction Screen Timing

**Purpose:** Track when instruction screens were shown.

**Format:**
```
timestamp  msoffset  event
```

**Example:**
```
1763075655363  0  SETUP      ← Instructions displayed
1763075656727  0  EXIT       ← Participant pressed key to continue
```

**Why it exists:**
- Verify participant read instructions
- Calculate time spent on instructions
- Detect if participant rushed through

---

### 9. **experiment.log** - General Experiment Events

**Purpose:** High-level experiment flow tracking.

**Contains:**
- Experiment start/stop
- List transitions
- Phase changes
- Errors or warnings

**Why it exists:** Debugging and quality control.

---

## CONFIGURATION FILES

### 10. **config.py** - Experiment Configuration

**Purpose:** Store all experimental parameters for this run.

**Key Parameters:**
```python
NPAIRS = 8              # 8 word pairs per list
NLISTS = 1              # 1 list total
NDIST = 3               # 3 math distractor problems
DIST_MIN = 2            # Min digit in math problems
DIST_MAX = 8            # Max digit in math problems
PRES_TIME = 2500        # Word display duration (2500ms = 2.5s)
IPI_lower = 500         # Min inter-pair interval
IPI_upper = 800         # Max inter-pair interval
C_RESP_TIME = 7000      # Response window (7000ms = 7s)
C_BLANK_TIME = 250      # Blank screen between trials
keyLeft = 'Z'           # Left response key (OLD/INTACT)
keyRight = '/'          # Right response key (NEW/RECOMBINED)
RUN_PRACTICE = 0        # Practice trials disabled
```

**Why it exists:**
- Document exact experimental parameters
- Replicate experiments
- Verify correct settings were used

---

### 11. **configbackup/** - Configuration Version History

**Purpose:** Keep backups of config changes during the experiment.

**Why it exists:** Allows you to see if config was modified mid-experiment.

---

### 12. **sconfig.py** - Session-Specific Configuration

**Purpose:** Settings that vary by session (usually empty or minimal).

---

### 13. **state/** - Experiment State Directory

**Purpose:** Store internal PyEPL state information (for resuming interrupted experiments).

---

## Data Analysis Quick Reference

### To analyze recognition memory performance:
**Use:** `recoglog.log` or `session.log`

**Calculate:**
- **Item Recognition Accuracy:** % correct on ITEM trials
- **Associative Recognition Accuracy:** % correct on ASSOC trials
- **Hit Rate:** % of OLD items correctly identified
- **False Alarm Rate:** % of NEW items incorrectly called OLD
- **d' (d-prime):** Sensitivity measure = Z(hit rate) - Z(false alarm rate)

### To analyze reaction times:
**Use:** `session.log` or `recoglog.log` (last column)

**Calculate:**
- Mean RT for correct vs incorrect trials
- RT distributions
- Speed-accuracy tradeoffs

### To analyze study phase:
**Use:** `stimlog.log`

**Check:**
- Which pairs were presented
- Presentation order
- IPI variability

### To synchronize with EEG:
**Use:** `eeg.eeglog` + `session.log` + `video.vidlog`

**Align:** EEG markers with word presentation timestamps

---

## Subject 6969 Performance Summary

Based on the data in your files:

### Study Phase (List 1):
- **8 pairs studied:** SQUIRREL-ANCHOR, APPLE-VALUE, MAYOR-SPEAKER, etc.
- **IPI range:** 514-766ms (properly jittered)

### Test Phase (Visible in latest run):
- **16 trials total:** 8 ITEM + 8 ASSOC
- **Mix of old and new items**
- **Mix of intact and recombined pairs**

### Distractor Performance:
- **Math accuracy:** 0% (all problems answered incorrectly or timed out)
- **Engagement:** Questionable (may need stricter distractor instructions)

---

## File Size Reference

```
config.py           2.1 KB    (text config)
eeg.eeglog         19 KB      (timing markers)
experiment.log     535 bytes  (minimal events)
instruct.log       15 KB      (instruction timing)
key.keylog         28 KB      (all keypresses)
math_distract.log  1.1 KB     (3 problems × 4 runs)
recoglog.log       1.7 KB     (16 test trials × 4 runs)
session.log        3.6 KB     (complete log)
stimlog.log        1.3 KB     (8 pairs × 4 runs)
video.vidlog       224 KB     (binary timing data)
```

**Total:** ~300 KB per subject

---

## Troubleshooting

**Q: Why are there multiple "LIST 1" entries?**
**A:** Participant ran the experiment 4 separate times (possibly testing/debugging).

**Q: Why are some RT values 7000ms?**
**A:** Participant didn't respond within the 7-second window (timeout).

**Q: What does "B" and "E" mean in logs?**
**A:** `B` = Logging Begins, `E` = Logging Ends (session markers).

**Q: Can I delete any of these files?**
**A:** Keep ALL files. Even seemingly minor logs are valuable for quality control and debugging. Standard practice: archive everything.

---

## Best Practices

1. **Back up immediately** - Copy entire subject directory to secure storage
2. **Never edit** - Original data files should remain untouched
3. **Version control** - Use git or similar for analysis scripts, not data
4. **Document** - Note any unusual circumstances in a separate README
5. **Analyze systematically** - Use scripted analysis (Python/R) for reproducibility

---

## Need More Help?

- **PyEPL Documentation:** `PYEPLDOC.PDF` in your directory
- **Log Format Questions:** Check `pyepl-1.0.29/code/textlog.py`
- **Code Reference:** See refactored script for how logs are created
