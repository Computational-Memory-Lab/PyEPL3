#!/usr/bin/env python3
"""
Basic test script for PyEPL3

Tests core functionality without requiring subject ID or complex setup.
"""

import sys
sys.path.insert(0, '/Users/devon7y/VS Code/pyepl_testing/pyepl3')

import pyepl3
from pyepl3 import (
    Experiment, VideoTrack, KeyTrack, AudioTrack, EEGTrack,
    PresentationClock, Text, Key, ButtonChooser, WHITE, TextPool
)

print(f"PyEPL3 version: {pyepl3.__version__}")
print("Testing basic functionality...\n")

# Test 1: Create experiment without subject
print("Test 1: Creating experiment...")
exp = Experiment(name="test", use_args=False)
print("✓ Experiment created")

# Test 2: Create tracks
print("\nTest 2: Creating tracks...")
video = VideoTrack("video", resolution=(800, 600), fullscreen=False)
keyboard = KeyTrack("keyboard")
audio = AudioTrack("audio")
eeg = EEGTrack("eeg")
print("✓ Tracks created")

# Test 3: Start logging
print("\nTest 3: Starting logging...")
video.startLogging()
keyboard.startLogging()
audio.startLogging()
eeg.startLogging()
print("✓ Logging started")

# Test 4: PresentationClock
print("\nTest 4: Testing PresentationClock...")
clock = PresentationClock()
print(f"✓ Clock created at {clock.get()}ms")

# Test 5: Display text
print("\nTest 5: Displaying text...")
text = Text("PyEPL3 Test\n\nPress SPACE to continue", size=40, color=WHITE)
timestamp = video.showCentered(text, clock)
video.updateScreen(clock)
print(f"✓ Text displayed at {timestamp}ms")

# Test 6: Wait for keypress
print("\nTest 6: Waiting for SPACE key...")
bc = ButtonChooser(Key("SPACE"), track=keyboard)
button, press_time = bc.waitWithTime(clock, timeout=5000)

if button:
    print(f"✓ Key pressed at {press_time}ms")
    clock.delay(500)  # Brief delay
else:
    print("⚠ Timeout (no key pressed)")

# Test 7: Clear screen
print("\nTest 7: Clearing screen...")
video.unshowAll()
video.updateScreen(clock)
print("✓ Screen cleared")

# Test 8: TextPool
print("\nTest 8: Testing TextPool...")
pool = TextPool("apple", "banana", "cherry", "date")
pool.shuffle()
print(f"✓ Created pool with {len(pool)} items")
print(f"  Random choice: {pool.randomChoice()}")

# Test 9: EEG pulse
print("\nTest 9: Testing EEG pulse...")
pulse_time = eeg.pulse(clock)
print(f"✓ EEG pulse sent at {pulse_time}ms")

# Test 10: Stop logging
print("\nTest 10: Stopping logging...")
video.stopLogging()
keyboard.stopLogging()
audio.stopLogging()
eeg.stopLogging()
print("✓ Logging stopped")

# Close display
print("\nClosing display...")
video.close()
print("✓ Display closed")

print("\n" + "="*50)
print("All basic tests completed successfully!")
print("="*50)
