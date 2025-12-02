#!/usr/bin/env python3
"""
Example PyEPL3 Experiment

Demonstrates a simple paired-associate memory experiment using PyEPL3.
This shows the basic structure for migrating PyEPL experiments to PyEPL3.
"""

import random
import sys
from pathlib import Path

# Import PyEPL3
from pyepl3 import (
    Experiment, VideoTrack, KeyTrack, AudioTrack, EEGTrack,
    PresentationClock, Text, Image, Key, ButtonChooser,
    TextPool, WHITE, BLACK
)


def show_instructions(text_content, video_track, clock):
    """Display instructions and wait for keypress."""
    # Create instruction text
    instruction_text = Text(text_content, size=24, color=WHITE)

    # Show centered
    video_track.showCentered(instruction_text, clock)
    video_track.updateScreen(clock)

    # Wait for SPACE to continue
    bc = ButtonChooser(Key("SPACE"))
    bc.wait(clock)

    # Clear screen
    video_track.unshowAll()
    video_track.updateScreen(clock)


def main():
    """Run the experiment."""

    # Create experiment
    # Note: In PyEPL3, use use_args=True to get subject from command line
    # For testing, set use_args=False and it won't require subject argument
    exp = Experiment(name="PairedAssociate", use_args=False)

    # For real experiments, you'd use:
    # exp = Experiment(name="PairedAssociate", use_args=True)
    # Then run: python example_experiment.py <subject_id>

    # Set up break key (Escape+F1)
    exp.setBreak()

    # Get configuration
    config = exp.getConfig()

    # Set some default config values if not specified
    if 'n_pairs' not in config:
        config.n_pairs = 10
    if 'study_time' not in config:
        config.study_time = 3000  # ms
    if 'test_delay' not in config:
        config.test_delay = 1000  # ms

    # Create tracks
    video = VideoTrack("video", resolution=(1024, 768), fullscreen=False,
                      archive_dir=exp.getArchive())
    keyboard = KeyTrack("keyboard", archive_dir=exp.getArchive())
    audio = AudioTrack("audio", archive_dir=exp.getArchive())
    eeg = EEGTrack("eeg", archive_dir=exp.getArchive())

    # Start logging
    video.startLogging()
    keyboard.startLogging()
    audio.startLogging()
    eeg.startLogging()

    # Create clock
    clock = PresentationClock()

    # Clear screen
    video.clear(BLACK)
    video.updateScreen(clock)

    # Show welcome instructions
    welcome = """
    Paired Associate Memory Experiment

    You will study word pairs, then be tested on your memory.

    Press SPACE to continue
    """
    show_instructions(welcome, video, clock)

    # EEG alignment pulse
    eeg.pulse(clock)

    # Create stimulus pool
    # In a real experiment, you'd load from a file
    words = ["apple", "table", "mountain", "river", "guitar",
             "pencil", "window", "garden", "bicycle", "coffee",
             "sunset", "piano", "ocean", "forest", "laptop",
             "sandwich", "library", "umbrella", "camera", "dolphin"]

    word_pool = TextPool(*words)
    word_pool.shuffle()

    # STUDY PHASE
    study_instructions = """
    STUDY PHASE

    You will see pairs of words.
    Try to remember which words go together.

    Press SPACE to begin
    """
    show_instructions(study_instructions, video, clock)

    # Study pairs
    studied_pairs = []
    for pair_num in range(config.n_pairs):
        # Get two words
        word1 = word_pool.pop()
        word2 = word_pool.pop()

        studied_pairs.append((word1, word2))

        # Create pair display
        pair_text = Text(f"{word1}  -  {word2}", size=36, color=WHITE)

        # Show pair
        timestamp = video.showCentered(pair_text, clock)
        video.updateScreen(clock)

        # EEG marker for pair onset
        eeg.alignmentMarker(f"PAIR_{pair_num}", clock)

        # Wait for study duration
        clock.delay(config.study_time)

        # Clear screen
        video.unshowAll()
        video.updateScreen(clock)

        # Inter-pair interval with jitter
        clock.delay(config.test_delay, jitter=500)

    # DISTRACTOR TASK
    distractor_instructions = """
    DISTRACTOR TASK

    Count backwards from 100 by 3s for 30 seconds.

    Press SPACE when ready
    """
    show_instructions(distractor_instructions, video, clock)

    # Show countdown
    countdown_text = Text("Count backwards: 100, 97, 94...", size=30, color=WHITE)
    video.showCentered(countdown_text, clock)
    video.updateScreen(clock)
    clock.delay(30000)  # 30 seconds

    video.unshowAll()
    video.updateScreen(clock)

    # TEST PHASE
    test_instructions = """
    TEST PHASE

    You will see word pairs.
    Press LEFT ARROW if the pair is INTACT (same as study)
    Press RIGHT ARROW if the pair is REARRANGED (different)

    Press SPACE to begin
    """
    show_instructions(test_instructions, video, clock)

    # Create test items (half intact, half recombined)
    test_items = []

    # Intact pairs
    for pair in studied_pairs[:config.n_pairs // 2]:
        test_items.append((pair[0], pair[1], "intact"))

    # Recombined pairs
    remaining_pairs = studied_pairs[config.n_pairs // 2:]
    words_1 = [p[0] for p in remaining_pairs]
    words_2 = [p[1] for p in remaining_pairs]
    random.shuffle(words_2)  # Shuffle second words to recombine

    for i, word1 in enumerate(words_1):
        test_items.append((word1, words_2[i], "recombined"))

    # Shuffle test order
    random.shuffle(test_items)

    # Test each pair
    results = []
    for test_num, (word1, word2, condition) in enumerate(test_items):
        # Create test display
        test_text = Text(f"{word1}  -  {word2}", size=36, color=WHITE)

        # Show pair
        timestamp = video.showCentered(test_text, clock)
        video.updateScreen(clock)

        # EEG marker
        eeg.alignmentMarker(f"TEST_{test_num}_{condition}", clock)

        # Wait for response
        bc = ButtonChooser(Key("LEFT"), Key("RIGHT"), track=keyboard)
        button, response_time = bc.waitWithTime(clock)

        # Record response
        if button:
            response = "intact" if button.key_name == "LEFT" else "recombined"
            correct = (response == condition)
            results.append({
                'test_num': test_num,
                'word1': word1,
                'word2': word2,
                'condition': condition,
                'response': response,
                'correct': correct,
                'rt': response_time - timestamp
            })
        else:
            results.append({
                'test_num': test_num,
                'word1': word1,
                'word2': word2,
                'condition': condition,
                'response': 'timeout',
                'correct': False,
                'rt': -1
            })

        # Clear screen
        video.unshowAll()
        video.updateScreen(clock)

        # Inter-trial interval
        clock.delay(500)

    # Calculate accuracy
    correct_count = sum(1 for r in results if r['correct'])
    accuracy = correct_count / len(results) * 100

    # Show results
    results_text = f"""
    EXPERIMENT COMPLETE

    Accuracy: {accuracy:.1f}%
    ({correct_count} out of {len(results)} correct)

    Thank you for participating!

    Press SPACE to exit
    """
    show_instructions(results_text, video, clock)

    # Stop logging
    video.stopLogging()
    keyboard.stopLogging()
    audio.stopLogging()
    eeg.stopLogging()

    # Save experiment state
    exp.state.accuracy = accuracy
    exp.state.results = results
    if exp.subject:
        exp.saveState()

    # Close display
    video.close()

    print(f"\nExperiment complete! Accuracy: {accuracy:.1f}%")


if __name__ == "__main__":
    main()
