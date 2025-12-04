#!/usr/bin/env python3
"""
Paired Associate Recognition EEG Experiment - PyEPL3 Version

Adapted from PairAssoDevon.py for PyEPL3.

Sequential word presentation with item and associative recognition tests.
"""

import sys
import random
import time
import math
from pathlib import Path
import pygame

# Import PyEPL3
from pyepl3 import (
    Experiment, VideoTrack, KeyTrack, LogTrack, EEGTrack,
    PresentationClock, Text, Key, ButtonChooser,
    WHITE, BLACK, RED, GREEN, BLUE, Color,
    TextPool, mathDistract
)


def show_proportional(video, showable, x_prop, y_prop, clk=None):
    """
    Show stimulus at proportional position on screen.

    Args:
        video: VideoTrack
        showable: Showable object
        x_prop: X position as proportion of screen width (0.0 to 1.0)
        y_prop: Y position as proportion of screen height (0.0 to 1.0)
        clk: PresentationClock (optional)

    Returns:
        Timestamp when shown
    """
    width, height = video.getResolution()
    x = int(width * x_prop) - (showable.getSize()[0] // 2)
    y = int(height * y_prop) - (showable.getSize()[1] // 2)
    return video.show(showable, (x, y), clk)


def check_skip_combination():
    """
    Check if the skip combination (L SHIFT + R SHIFT) is pressed.

    Returns:
        True if both shift keys are currently pressed, False otherwise
    """
    keys = pygame.key.get_pressed()
    lshift = keys[pygame.K_LSHIFT]
    rshift = keys[pygame.K_RSHIFT]

    return lshift and rshift


def delay_with_skip(clock, duration_ms, check_interval=50):
    """
    Delay for a specified duration, but allow skipping with key combination.

    Args:
        clock: PresentationClock
        duration_ms: Duration to wait in milliseconds
        check_interval: How often to check for skip combination (ms)

    Returns:
        True if skipped, False if completed normally
    """
    start_time = clock.get()
    target_time = start_time + duration_ms

    while clock.get() < target_time:
        # Process pygame events to update key states
        pygame.event.pump()

        # Check for skip combination
        if check_skip_combination():
            print("  >>> SKIP COMBINATION DETECTED <<<")
            # Fast forward the virtual clock WITHOUT waiting
            clock._virtual_time = target_time
            # Sync real base so future waits don't try to catch up to skipped time
            import time as time_module
            clock._real_base = time_module.perf_counter() - (target_time / 1000.0)
            return True

        # Wait a bit before checking again
        wait_time = min(check_interval, target_time - clock.get())
        if wait_time > 0:
            clock.delay(wait_time)

    return False


def main():
    """Run the experiment."""

    #########################################
    # Initialization
    #########################################

    # Create experiment
    exp = Experiment(name="PairAssocRecog")

    # Set break key
    exp.setBreak()

    # Load configuration
    exp.loadConfig("config_pairassoc.py")
    config = exp.getConfig()

    # Create tracks
    archive_dir = exp.getArchive()
    video = VideoTrack("video", archive_dir=archive_dir,
                      resolution=config.resolution,
                      fullscreen=config.fullscreen)
    keyboard = KeyTrack("key", archive_dir=archive_dir)
    eeg = EEGTrack("eeg", archive_dir=archive_dir)
    stimlog = LogTrack("stimlog", archive_dir=archive_dir)
    recoglog = LogTrack("recoglog", archive_dir=archive_dir)
    log = LogTrack("session", archive_dir=archive_dir)

    # Start logging
    video.startLogging()
    keyboard.startLogging()
    eeg.startLogging()
    stimlog.startLogging()
    recoglog.startLogging()
    log.startLogging()

    # Create clock
    clock = PresentationClock()

    # Clear screen
    video.clear(BLACK)
    video.updateScreen(clock)

    #########################################
    # Counterbalancing
    #########################################

    # Get subject ID from command line
    if exp.subject:
        subject_id = int(exp.subject)
    else:
        subject_id = 1  # Default for testing

    keychoice = subject_id % 4
    if keychoice == 0:
        key_left = config.keyLeft
        key_right = config.keyRight
        inst_m_left = "INTACT"
        inst_m_right = "RECOMBINED"
    else:
        key_left = config.keyLeft
        key_right = config.keyRight
        inst_m_left = "RECOMBINED"
        inst_m_right = "INTACT"

    print(f"Key choice: {keychoice}")

    #########################################
    # Build Stimulus Pools
    #########################################

    probe_disp_pool = TextPool("raw_pools/nouns.txt")
    probe_disp_pool_id = TextPool("raw_pools/nouns.txt")

    random.shuffle(probe_disp_pool)

    #########################################
    # Main Experiment Loop
    #########################################

    list_count = 1

    while list_count <= (config.NLISTS + config.RUN_PRACTICE):
        log.logMessage(f'LIST\t{list_count}')

        # Show instructions based on list number
        if list_count == config.RUN_PRACTICE:
            with open("instruct/instruct0.txt") as f:
                instructions = f.read()
            title = "Get ready for the Practice Round!"
        elif list_count == (1 + config.RUN_PRACTICE):
            with open("instruct/instruct1.txt") as f:
                instructions = f.read()
            title = f"Get ready for Round 1 of {config.NLISTS}!"
        else:
            with open("instruct/instructN.txt") as f:
                instructions = f.read()
            title = f"Get ready for Round {list_count - config.RUN_PRACTICE} of {config.NLISTS}!"

        # Show instructions
        print(f"\n=== LIST {list_count}: Showing instructions ===")
        video.showInstructions(instructions, clk=clock)

        # Show title
        print(f"=== Showing title screen ===")
        video.clear(BLACK)
        title_text = Text(title, size=36, color=WHITE)
        video.showCentered(title_text, clock)
        video.updateScreen(clock)

        # Wait for experimenter to advance (or skip button)
        print(f"Waiting for experimenter to continue (or {config.PRES_TIME}ms timeout)...")
        bc = ButtonChooser(Key("LSHIFT"), Key("RSHIFT"), Key("BACKSLASH"), track=keyboard)
        button, timestamp = bc.waitWithTime(clock, timeout=config.PRES_TIME)
        print(f"Continue button pressed: {button}")

        # Clear any remaining events before study phase
        pygame.event.clear()
        video.clear(BLACK)
        video.updateScreen(clock)
        clock.delay(500)  # Brief pause before study

        #########################################
        # Study Phase - Sequential word presentation
        #########################################

        studied_words = []  # All words presented
        studied_pairs = []  # All pairs for associative test

        pair_count = 1

        print(f"\n=== STARTING STUDY PHASE: {config.NPAIRS} pairs ===")

        while pair_count <= config.NPAIRS:
            print(f"\n--- Pair {pair_count}/{config.NPAIRS} ---")

            # Get two words for this pair
            probe1 = probe_disp_pool.pop(0)
            probe2 = probe_disp_pool.pop(0)

            # Get word IDs for logging
            word1_id = probe_disp_pool_id.isInPool(name=probe1.name) + 1
            word2_id = probe_disp_pool_id.isInPool(name=probe2.name) + 1

            print(f"  Word 1: {probe1.name} (ID: {word1_id})")
            print(f"  Word 2: {probe2.name} (ID: {word2_id})")

            # Store pair and individual words
            studied_pairs.append({
                'pair_num': pair_count,
                'word1': probe1.name,
                'word1_id': word1_id,
                'word2': probe2.name,
                'word2_id': word2_id
            })

            studied_words.append({'word': probe1.name, 'word_id': word1_id})
            studied_words.append({'word': probe2.name, 'word_id': word2_id})

            # Set jittered IPI
            ipi_values = list(range(config.IPI_lower, config.IPI_upper + 1))
            random.shuffle(ipi_values)
            ipi = ipi_values.pop(0)

            # Present first word
            print(f"  Showing word 1: {probe1.name}")
            start_time = clock.get()

            stim1 = Text(probe1.name, size=72, color=WHITE)
            video.clear(BLACK)
            video.showCentered(stim1, clock)
            video.updateScreen(clock)

            print(f"  Waiting {config.PRES_TIME}ms for word 1...")
            # Use delay_with_skip() to allow skipping with key combination
            delay_with_skip(clock, config.PRES_TIME)
            end_time = clock.get()

            elapsed = end_time - start_time
            print(f"  Word 1 displayed for {elapsed}ms")
            print(f"    Virtual time: {clock.get()}ms")

            print(f"  Showing word 2: {probe2.name}")
            start_time = clock.get()

            stim2 = Text(probe2.name, size=72, color=WHITE)
            video.clear(BLACK)
            video.showCentered(stim2, clock)
            video.updateScreen(clock)

            print(f"  Waiting {config.PRES_TIME}ms for word 2...")
            # Use delay_with_skip() to allow skipping with key combination
            delay_with_skip(clock, config.PRES_TIME)
            end_time = clock.get()

            elapsed = end_time - start_time
            print(f"  Word 2 displayed for {elapsed}ms")

            # Show fixation cross during jittered IPI
            video.clear(BLACK)
            fixation = Text("+", size=72, color=WHITE)
            video.showCentered(fixation, clock)
            video.updateScreen(clock)

            print(f"  Inter-pair interval: {ipi}ms")
            delay_with_skip(clock, ipi)

            # Log this pair presentation
            log.logMessage(f'{list_count}\t{pair_count}\t{probe1.name}\t{word1_id}\t{probe2.name}\t{word2_id}\t{ipi}')
            stimlog.logMessage(f'{list_count}\t{pair_count}\t{word1_id}\t{word2_id}\t{ipi}')

            pair_count += 1

        print("\n=== STUDY PHASE COMPLETE ===\n")

        #########################################
        # Distractor Task
        #########################################

        if config.NDIST > 0:
            if list_count == 1 and config.RUN_PRACTICE == 1:
                with open("instruct/distractor.txt") as f:
                    instructions = f.read()
                video.showInstructions(instructions, clk=clock)

            mathDistract(
                clk=clock,
                problemTimeLimit=config.D_RESP_TIME,
                numVars=3,
                maxNum=config.DIST_MAX,
                minNum=config.DIST_MIN,
                maxProbs=config.NDIST,
                minDuration=(config.D_RESP_TIME + config.D_BLANK_TIME) * config.NDIST,
                blanktime=config.D_BLANK_TIME
            )

            # Reset display and clear events
            pygame.event.clear()
            video.clear(BLACK)
            video.updateScreen(clock)
            clock.delay(500)  # Brief pause after distractor

        #########################################
        # Test Phase - Item + Associative Recognition
        #########################################

        if list_count == config.RUN_PRACTICE:
            with open("instruct/recognition_noorder.txt") as f:
                instructions = f.read()
            video.showInstructions(instructions, clk=clock)
            start = clock.get()
        elif list_count > 1:
            title = "Get ready for recognition"
            video.clear(BLACK)
            title_text = Text(title, size=36, color=WHITE)
            video.showCentered(title_text, clock)
            video.updateScreen(clock)
            clock.delay(2000)

        #########################################
        # Create test trials
        # Split pairs: half for associative, half for item recognition
        # No word overlap between trial types
        #########################################

        test_trials = []

        # Shuffle and split pairs into two groups
        pair_indices = list(range(len(studied_pairs)))
        random.shuffle(pair_indices)
        half = len(pair_indices) // 2

        # Group A: pairs for associative recognition (half for intact, half for recombined)
        assoc_pair_indices = pair_indices[:half]
        # Group B: pairs for item recognition (words become old items)
        item_pair_indices = pair_indices[half:]

        # 1. Associative Recognition trials from Group A
        # Split into intact and recombined
        n_intact = len(assoc_pair_indices) // 2
        intact_indices = assoc_pair_indices[:n_intact]
        recombined_indices = assoc_pair_indices[n_intact:]

        # Add intact pairs
        for idx in intact_indices:
            pair = studied_pairs[idx]
            test_trials.append({
                'type': 'assoc',
                'word1': pair['word1'],
                'word1_id': pair['word1_id'],
                'word2': pair['word2'],
                'word2_id': pair['word2_id'],
                'target': 1,  # INTACT
                'is_intact': True,
                'pair_num': pair['pair_num']
            })

        # Create recombined pairs from remaining assoc pairs
        recombined_pairs = [studied_pairs[i] for i in recombined_indices]
        for i in range(len(recombined_pairs)):
            pair1 = recombined_pairs[i]
            pair2 = recombined_pairs[(i + 1) % len(recombined_pairs)]
            test_trials.append({
                'type': 'assoc',
                'word1': pair1['word1'],
                'word1_id': pair1['word1_id'],
                'word2': pair2['word2'],
                'word2_id': pair2['word2_id'],
                'target': 0,  # RECOMBINED
                'is_intact': False,
                'pair_num1': pair1['pair_num'],
                'pair_num2': pair2['pair_num']
            })

        # 2. Item Recognition trials from Group B
        # Collect all words from item pairs
        item_words = []
        for idx in item_pair_indices:
            pair = studied_pairs[idx]
            item_words.append({'word': pair['word1'], 'word_id': pair['word1_id']})
            item_words.append({'word': pair['word2'], 'word_id': pair['word2_id']})

        # Use half as OLD items, get equal number of NEW foils
        random.shuffle(item_words)
        n_old = len(item_words) // 2
        old_words = item_words[:n_old]

        # Add OLD item trials
        for word_info in old_words:
            test_trials.append({
                'type': 'item',
                'word': word_info['word'],
                'word_id': word_info['word_id'],
                'target': 1,  # OLD
                'is_old': True
            })

        # Add NEW foil trials (equal to number of old)
        for i in range(n_old):
            foil_word = probe_disp_pool.pop(0)
            foil_id = probe_disp_pool_id.isInPool(name=foil_word.name) + 1
            test_trials.append({
                'type': 'item',
                'word': foil_word.name,
                'word_id': foil_id,
                'target': 0,  # NEW
                'is_old': False
            })

        # Shuffle all test trials
        random.shuffle(test_trials)

        n_assoc = len([t for t in test_trials if t['type'] == 'assoc'])
        n_item = len([t for t in test_trials if t['type'] == 'item'])
        print(f"Test trials: {n_assoc} associative, {n_item} item recognition")

        # Clear events before test phase
        pygame.event.clear()
        video.clear(BLACK)
        video.updateScreen(clock)
        clock.delay(500)  # Brief pause before test

        #########################################
        # Present test trials
        #########################################

        test_trial_count = 1

        for trial in test_trials:
            video.clear(BLACK)
            video.updateScreen(clock)

            if trial['type'] == 'item':
                # Item Recognition: Show single word
                stim = Text(trial['word'], size=48, color=WHITE)
                show_proportional(video, stim, 0.5, 0.5, clock)

                # Labels
                left_label = Text("OLD", size=24, color=Color(128, 128, 128))
                right_label = Text("NEW", size=24, color=Color(128, 128, 128))
                show_proportional(video, left_label, 0.20, 0.90, clock)
                show_proportional(video, right_label, 0.80, 0.90, clock)

                video.updateScreen(clock)

                # Get timestamp BEFORE waiting for response
                pres_time = clock.get()
                print(f"[TEST] Trial {test_trial_count} ITEM: {trial['word']} | PresentTime: {pres_time}ms | Timeout: {config.C_RESP_TIME}ms")

                # Wait for response
                bc = ButtonChooser(Key(config.keyLeft), Key(config.keyRight), track=keyboard)
                button, button_time = bc.waitWithTime(clock, timeout=config.C_RESP_TIME)

                print(f"[TEST] Response: {button.key_name if button else 'TIMEOUT'} | ResponseTime: {button_time}ms | RT: {button_time - pres_time if button else -1}ms")

                # Calculate RT
                if button:
                    rt = button_time - pres_time
                    if button.key_name == config.keyLeft:
                        response = 1  # OLD
                    else:
                        response = 0  # NEW
                else:
                    rt = -1
                    response = -1

                # Score
                recog_acc = 1 if response == trial['target'] else 0

                # Log
                log.logMessage(f"{list_count}\t{test_trial_count}\tITEM\t{trial['word']}\t{trial['word_id']}\t{trial['target']}\t{response}\t{recog_acc}\t{rt}")
                recoglog.logMessage(f"{list_count}\t{test_trial_count}\tITEM\t{trial['word_id']}\t{trial['target']}\t{response}\t{recog_acc}\t{rt}")

            else:  # Associative recognition
                # Show two words
                stim = Text(f"{trial['word1']}  {trial['word2']}", size=48,
                           color=WHITE)
                show_proportional(video, stim, 0.5, 0.5, clock)

                # Labels
                left_label = Text("INTACT", size=24, color=Color(128, 128, 128))
                right_label = Text("RECOMBINED", size=24, color=Color(128, 128, 128))
                show_proportional(video, left_label, 0.20, 0.90, clock)
                show_proportional(video, right_label, 0.80, 0.90, clock)

                video.updateScreen(clock)

                # Get timestamp BEFORE waiting for response
                pres_time = clock.get()
                print(f"[TEST] Trial {test_trial_count} ASSOC: {trial['word1']} {trial['word2']} | PresentTime: {pres_time}ms | Timeout: {config.C_RESP_TIME}ms")

                # Wait for response
                bc = ButtonChooser(Key(config.keyLeft), Key(config.keyRight), track=keyboard)
                button, button_time = bc.waitWithTime(clock, timeout=config.C_RESP_TIME)

                print(f"[TEST] Response: {button.key_name if button else 'TIMEOUT'} | ResponseTime: {button_time}ms | RT: {button_time - pres_time if button else -1}ms")

                # Calculate RT
                if button:
                    rt = button_time - pres_time
                    if button.key_name == config.keyLeft:
                        response = 1  # INTACT
                    else:
                        response = 0  # RECOMBINED
                else:
                    rt = -1
                    response = -1

                # Score
                recog_acc = 1 if response == trial['target'] else 0

                # Log
                log.logMessage(f"{list_count}\t{test_trial_count}\tASSOC\t{trial['word1']}\t{trial['word1_id']}\t{trial['word2']}\t{trial['word2_id']}\t{trial['target']}\t{response}\t{recog_acc}\t{rt}")
                recoglog.logMessage(f"{list_count}\t{test_trial_count}\tASSOC\t{trial['word1_id']}\t{trial['word2_id']}\t{trial['target']}\t{response}\t{recog_acc}\t{rt}")

            # Clear and wait
            video.clear(BLACK)
            video.updateScreen(clock)
            clock.delay(config.C_BLANK_TIME)

            # Clear pygame event queue to prevent progressive lag across test trials
            pygame.event.clear()

            test_trial_count += 1

        list_count += 1

    #########################################
    # End of Experiment
    #########################################

    # Show completion message
    completion_text = Text("Experiment Complete!\n\nThank you for participating.",
                          size=36, color=WHITE)
    video.clear(BLACK)
    video.showCentered(completion_text, clock)
    video.updateScreen(clock)
    clock.delay(3000)

    # Stop logging
    video.stopLogging()
    keyboard.stopLogging()
    eeg.stopLogging()
    stimlog.stopLogging()
    recoglog.stopLogging()
    log.stopLogging()

    # Close display
    video.close()

    print("Experiment completed successfully!")


if __name__ == "__main__":
    main()
