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
import argparse
from pathlib import Path
import pygame


# Import PyEPL3
from pyepl3.pyepl3 import (
    Experiment, VideoTrack, KeyTrack, LogTrack, EEGTrack,
    PresentationClock, Text, Key, ButtonChooser,
    WHITE, BLACK, RED, GREEN, BLUE, Color,
    TextPool
)

# Get font path relative to this script (works on any device)
FONT_PATH = str(Path(__file__).parent / "resources" / "LucidaGrande.ttc")

#########################################
# Instruction Text
#########################################

INSTRUCT_PRACTICE = """
You will see a list of words, grouped in pairs

Study the word pairs and try to remember them.
Studies have indicated that forming mental images of words 
significantly improves one's memory for them. 
Please try this technique for the next word pairs. 
Form a mental image with both of the words interacting together 
when you are presented with a word pair. 
For example, for the word pair 

CAT–DOG

you could 
imagine the cat chasing the dog.

After, you will be tested on the words

THIS IS PRACTICE

Press ENTER to continue"""

INSTRUCT_ROUND1_ARROW = """
You will now study a new list of words
Remember to form mental images of the word pairs

THIS IS NO LONGER PRACTICE

Press ENTER to continue"""

INSTRUCT_ROUNDN_ARROW = """
You will now study a new list of words
Remember to form mental images of the word pairs

Press ENTER to continue"""

INSTRUCT_ARROW_TASK = """
You will now see arrows pointing left ← or right →

Press the LEFT ARROW key when you see ←
Press the RIGHT ARROW key when you see →

Respond as quickly as you can

Press ENTER to continue"""

INSTRUCT_RECOGNITION_ASSOC = """
Now you will see pairs of words based on pairs you just learned

If the test pair is the same as you learned, press the corresponding key to SAME PAIR
If the test pair words come from different pairs, press corresponding key to DIFFERENT PAIR

For example, if you studied pairs:

 APE DOT then, CAT SKY

and if you see:

 APE DOT

this would be INTACT.

If you see:

 APE SKY

this would be RECOMBINED.

Press "z" for left and "/" for right

Answer as quickly as possible without sacrificing accuracy

Press ENTER to continue"""

INSTRUCT_RECOGNITION_ITEM = """
Now you will see individual words from the pairs you just learned

If the word was in the list you just studied, press corresponding key to OLD
If the word was NOT in the list you just studied, press corresponding key to NEW

For example, if you studied pairs:

 APE DOT then, CAT SKY

and if you see:

 APE

this would be OLD.

If you see:

 NEON

this would be NEW.

Press "z" for left and "/" for right

Answer as quickly as possible without sacrificing accuracy

Press ENTER to continue"""

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

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Paired Associate Recognition EEG Experiment")
    parser.add_argument("-s", "--subject", type=str, help="Subject ID")
    args = parser.parse_args()

    # Create experiment
    exp = Experiment(name="PairAssocRecog")

    # Set break key
    exp.setBreak()

    # Load configuration
    exp.loadConfig("config_pairassoc.py")
    config = exp.getConfig()

    # Create tracks
    archive_dir = Path("archive_logs/arrow_distractor")

    # Get subject ID from command line or prompt
    if args.subject:
        subject_id = args.subject
    else:
        subject_id = input("Enter subject ID: ")
    archive_dir = "".join([str(archive_dir), "/subject_", str(subject_id)])

    video = VideoTrack("video", archive_dir=archive_dir,
                      resolution=config.resolution,
                      fullscreen=config.fullscreen)
    keyboard = KeyTrack("key", archive_dir=archive_dir)
    eeg = EEGTrack("eeg", archive_dir=archive_dir)
    stimlog = LogTrack("stimlog", archive_dir=archive_dir)
    recoglog = LogTrack("recoglog", archive_dir=archive_dir)
    log = LogTrack("session", archive_dir=archive_dir)
    arrow_distract = LogTrack("arrow_distract", archive_dir=archive_dir)
    
    # Start logging
    video.startLogging()
    keyboard.startLogging()
    eeg.startLogging()
    stimlog.startLogging()
    recoglog.startLogging()
    log.startLogging()
    arrow_distract.startLogging()


    # Create clock
    clock = PresentationClock()

    # Clear screen
    video.clear(BLACK)
    video.updateScreen(clock)

    #########################################
    # Counterbalancing
    #########################################

    # Get subject ID from command line
    subject_id = int(subject_id)
    

    keychoice = subject_id % 2
    if keychoice == 0:
        key_left = config.keyLeft
        key_right = config.keyRight
        # Associative test labels
        inst_assoc_left = "INTACT"
        inst_assoc_right = "RECOMBINED"
        # Item test labels
        inst_item_left = "OLD"
        inst_item_right = "NEW"
    else:
        key_left = config.keyLeft
        key_right = config.keyRight
        # Associative test labels
        inst_assoc_left = "RECOMBINED"
        inst_assoc_right = "INTACT"
        # Item test labels
        inst_item_left = "NEW"
        inst_item_right = "OLD"

    print(f"Key choice: {keychoice}")

    # Counterbalance test type order within each group of 3 lists
    # Each group of 3 has 2 associative and 1 item test
    test_patterns = [
        ['assoc', 'assoc', 'item'],  # Pattern 0: Item in position 3
        ['assoc', 'item', 'assoc'],  # Pattern 1: Item in position 2
        ['item', 'assoc', 'assoc'],  # Pattern 2: Item in position 1
    ]

    #########################################
    # Build Stimulus Pools
    #########################################

    #probe_disp_pool = TextPool("raw_pools/nouns.txt")
    #probe_disp_pool_id = TextPool("raw_pools/nouns.txt")
    probe_disp_pool = TextPool("raw_pools/filtered_words.txt")
    probe_disp_pool_id = TextPool("raw_pools/filtered_words.txt")

    random.shuffle(probe_disp_pool)

    #########################################
    # Main Experiment Loop
    #########################################

        #########################################
        # Optional Practice Lists
        #########################################
        if config.RUN_PRACTICE > 0:
        ### Practice 1 (Associative) ###
    
        # Show instructions
        log.logMessage(f'LIST\tP1')
        instructions = INSTRUCT_PRACTICE
        title = "Get ready for the Practice Round!"
        num_pairs=config.NPAIRS_PRACTICE
        print(f"\n=== LIST P1: Showing instructions ===")
        video.showInstructions(instructions, clk=clock, font=FONT_PATH)

        # Show title
        print(f"=== Showing title screen ===")
        video.clear(BLACK)
        title_text = Text(title, size=36, color=WHITE, font=FONT_PATH)
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

        ### Study Phase - Sequential word presentation ###

        studied_words = []  # All words presented
        studied_pairs = []  # All pairs for associative test

        pair_count = 1

        print(f"\n=== STARTING STUDY PHASE: {config.NPAIRS} pairs ===")

        while pair_count <= num_pairs:
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

            stim1 = Text(probe1.name, size=72, color=WHITE, font=FONT_PATH)
            video.clear(BLACK)
            show_proportional(video, stim1, 0.5, 0.5, clock)
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

            stim2 = Text(probe2.name, size=72, color=WHITE, font=FONT_PATH)
            video.clear(BLACK)
            show_proportional(video, stim2, 0.5, 0.5, clock)
            video.updateScreen(clock)

            print(f"  Waiting {config.PRES_TIME}ms for word 2...")
            # Use delay_with_skip() to allow skipping with key combination
            delay_with_skip(clock, config.PRES_TIME)
            end_time = clock.get()

            elapsed = end_time - start_time
            print(f"  Word 2 displayed for {elapsed}ms")

            # Show fixation cross during jittered IPI
            video.clear(BLACK)
            fixation = Text("+", size=92, color=WHITE, font=FONT_PATH)
            show_proportional(video, fixation, 0.5, 0.49, clock)
            video.updateScreen(clock)

            print(f"  Inter-pair interval: {ipi}ms")
            delay_with_skip(clock, ipi)

            # Log this pair presentation
            log.logMessage(f'P1\t{pair_count}\t{probe1.name}\t{word1_id}\t{probe2.name}\t{word2_id}\t{ipi}')
            stimlog.logMessage(f'P1\t{pair_count}\t{word1_id}\t{word2_id}\t{ipi}') 

            pair_count += 1

        print("\n=== STUDY PHASE COMPLETE ===\n")

        ### Distractor Task - Arrow Response ###

        # Log start
        arrow_distract.logMessage("START")

        if config.NDIST > 0:

            video.showInstructions(INSTRUCT_ARROW_TASK, clk=clock, font=FONT_PATH)
            
            print(f"\n=== STARTING ARROW DISTRACTOR: {config.NDIST} trials ===")

            # Create button chooser for arrow responses (arrow keys)
            arrow_bc = ButtonChooser(Key("LEFT"), Key("RIGHT"), track=keyboard)

            for arrow_trial in range(config.NDIST):
                # Randomly choose left or right arrow
                is_left = random.choice([True, False])
                arrow_char = "←" if is_left else "→"
                correct_key = "LEFT" if is_left else "RIGHT"

                # Show arrow (centered, fixed position)
                video.clear(BLACK)
                arrow_text = Text(arrow_char, size=120, color=WHITE, font=FONT_PATH)
                show_proportional(video, arrow_text, 0.5, 0.45, clock)
                # Labels
                left_arrowLabel = Text("← [left arrow key]", size=28, color=WHITE, font=FONT_PATH)
                right_arrowLabel = Text("→ [right arrow key]", size=28, color=WHITE, font=FONT_PATH)
                show_proportional(video, left_arrowLabel, 0.20, 0.90, clock)
                show_proportional(video, right_arrowLabel, 0.80, 0.90, clock)
                video.updateScreen(clock)

                # Get presentation time
                pres_time = clock.get()
                prob_end = pres_time + config.D_RESP_TIME

                # Variables for response
                user_response = None

                # Wait for first keypress only
                button, _ = arrow_bc.waitWithTime(clock, timeout=config.D_RESP_TIME)

                if button is not None:
                    user_response = button.key_name
                    # Convert key to arrow character
                    response_arrow = "←" if user_response == "LEFT" else "→"

                    # Show response arrow below prompt (prompt stays in same position)
                    response_text = Text(response_arrow, size=120, color=WHITE, font=FONT_PATH)
                    show_proportional(video, response_text, 0.5, 0.60, clock)
                    video.updateScreen(clock)

                # Wait remaining time using pygame directly (no cursor spin)
                current_time = clock.get()
                remaining = prob_end - current_time
                if remaining > 0:
                    pygame.time.wait(int(remaining))
                    clock._virtual_time = prob_end  # Sync virtual clock

                # Score response
                if user_response is not None:
                    is_correct = (user_response == correct_key)
                    correct_str = "correct" if is_correct else "incorrect"
                else:
                    is_correct = False
                    correct_str = "no response"

                print(f"[ARROW] Trial {arrow_trial + 1}/{config.NDIST}: {arrow_char} | Response: {user_response or 'none'} | {correct_str}")

                # Log arrow trial
                arrow_distract.logMessage(f"ARROW\t{arrow_trial + 1}\t{arrow_char}\t{correct_key}\t{user_response or 'NONE'}\t{1 if is_correct else 0}")

                # Blank screen between trials
                video.clear(BLACK)
                video.updateScreen(clock)
                clock.delay(config.D_BLANK_TIME)

                # Clear event queue
                pygame.event.clear()

            print(f"=== ARROW DISTRACTOR COMPLETE ===\n")

            # Reset display and clear events
            pygame.event.clear()
            video.clear(BLACK)
            video.updateScreen(clock)
            clock.delay(500)  # Brief pause after distractor

        ### Test Phase - Pure List Recognition (Assoc) ###

        # Show appropriate instruction
        video.showInstructions(INSTRUCT_RECOGNITION_ASSOC, clk=clock, font=FONT_PATH, size=20)

        # Create test trials - Pure Associative List

        test_trials = []

        # Associative Recognition: half intact, half recombined
        pair_indices = list(range(len(studied_pairs)))
        random.shuffle(pair_indices)

        n_intact = len(pair_indices) // 2
        intact_indices = pair_indices[:n_intact]
        recombined_indices = pair_indices[n_intact:]

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

        # Create recombined pairs
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

        print(f"Test trials: {len(test_trials)} associative")

        # Shuffle all test trials
        random.shuffle(test_trials)

        # Clear events before test phase
        pygame.event.clear()
        video.clear(BLACK)
        video.updateScreen(clock)
        clock.delay(500)  # Brief pause before test

        ### Present test trials ###

        test_trial_count = 1

        for trial in test_trials:
            video.clear(BLACK)
            video.updateScreen(clock)

            # Associative Recognition: Show two words
            stim = Text(f"{trial['word1']}  {trial['word2']}", size=48, color=WHITE, font=FONT_PATH)
            show_proportional(video, stim, 0.5, 0.5, clock)

            # Labels
            left_label = Text(f"{inst_assoc_left} [z]", size=28, color=WHITE, font=FONT_PATH)
            right_label = Text(f"{inst_assoc_right} [/]", size=28, color=WHITE, font=FONT_PATH)
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
                # Response coding based on counterbalancing
                if keychoice == 0:
                    # Left=INTACT(1), Right=RECOMBINED(0)
                    if button.key_name == config.keyLeft:
                        response = 1  # INTACT
                    else:
                        response = 0  # RECOMBINED
                else:
                    # Left=RECOMBINED(0), Right=INTACT(1)
                    if button.key_name == config.keyLeft:
                        response = 0  # RECOMBINED
                    else:
                        response = 1  # INTACT
            else:
                rt = -1
                response = -1

            # Score
            recog_acc = 1 if response == trial['target'] else 0

            # Log
            log.logMessage(f"P1\t{test_trial_count}\tASSOC\t{trial['word1']}\t{trial['word1_id']}\t{trial['word2']}\t{trial['word2_id']}\t{trial['target']}\t{response}\t{recog_acc}\t{rt}")
            recoglog.logMessage(f"P1\t{test_trial_count}\tASSOC\t{trial['word1_id']}\t{trial['word2_id']}\t{trial['target']}\t{response}\t{recog_acc}\t{rt}")
             
            # Clear and wait
            video.clear(BLACK)
            video.updateScreen(clock)
            clock.delay(config.C_BLANK_TIME)

            # Clear pygame event queue to prevent progressive lag across test trials
            pygame.event.clear()

            test_trial_count += 1  
        
        ### Practice 2 (Item) ###
    
        # Show instructions
        log.logMessage(f'LIST\tP2')
        instructions = INSTRUCT_PRACTICE
        title = "Get ready for the Practice Round!"
        num_pairs=config.NPAIRS_PRACTICE
        print(f"\n=== LIST P2: Showing instructions ===")
        video.showInstructions(instructions, clk=clock, font=FONT_PATH)

        # Show title
        print(f"=== Showing title screen ===")
        video.clear(BLACK)
        title_text = Text(title, size=36, color=WHITE, font=FONT_PATH)
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

        ### Study Phase - Sequential word presentation ###

        studied_words = []  # All words presented
        studied_pairs = []  # All pairs for associative test

        pair_count = 1

        print(f"\n=== STARTING STUDY PHASE: {config.NPAIRS} pairs ===")

        while pair_count <= num_pairs:
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

            stim1 = Text(probe1.name, size=72, color=WHITE, font=FONT_PATH)
            video.clear(BLACK)
            show_proportional(video, stim1, 0.5, 0.5, clock)
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

            stim2 = Text(probe2.name, size=72, color=WHITE, font=FONT_PATH)
            video.clear(BLACK)
            show_proportional(video, stim2, 0.5, 0.5, clock)
            video.updateScreen(clock)

            print(f"  Waiting {config.PRES_TIME}ms for word 2...")
            # Use delay_with_skip() to allow skipping with key combination
            delay_with_skip(clock, config.PRES_TIME)
            end_time = clock.get()

            elapsed = end_time - start_time
            print(f"  Word 2 displayed for {elapsed}ms")

            # Show fixation cross during jittered IPI
            video.clear(BLACK)
            fixation = Text("+", size=92, color=WHITE, font=FONT_PATH)
            show_proportional(video, fixation, 0.5, 0.49, clock)
            video.updateScreen(clock)

            print(f"  Inter-pair interval: {ipi}ms")
            delay_with_skip(clock, ipi)

            # Log this pair presentation
            log.logMessage(f'P2\t{pair_count}\t{probe1.name}\t{word1_id}\t{probe2.name}\t{word2_id}\t{ipi}')
            stimlog.logMessage(f'P2\t{pair_count}\t{word1_id}\t{word2_id}\t{ipi}') 

            pair_count += 1

        print("\n=== STUDY PHASE COMPLETE ===\n")

        ### Distractor Task - Arrow Response ###

        # Log start
        arrow_distract.logMessage("START")

        if config.NDIST > 0:

            video.showInstructions(INSTRUCT_ARROW_TASK, clk=clock, font=FONT_PATH)
            
            print(f"\n=== STARTING ARROW DISTRACTOR: {config.NDIST} trials ===")

            # Create button chooser for arrow responses (arrow keys)
            arrow_bc = ButtonChooser(Key("LEFT"), Key("RIGHT"), track=keyboard)

            for arrow_trial in range(config.NDIST):
                # Randomly choose left or right arrow
                is_left = random.choice([True, False])
                arrow_char = "←" if is_left else "→"
                correct_key = "LEFT" if is_left else "RIGHT"

                # Show arrow (centered, fixed position)
                video.clear(BLACK)
                arrow_text = Text(arrow_char, size=120, color=WHITE, font=FONT_PATH)
                show_proportional(video, arrow_text, 0.5, 0.45, clock)
                # Labels
                left_arrowLabel = Text("← [left arrow key]", size=28, color=WHITE, font=FONT_PATH)
                right_arrowLabel = Text("→ [right arrow key]", size=28, color=WHITE, font=FONT_PATH)
                show_proportional(video, left_arrowLabel, 0.20, 0.90, clock)
                show_proportional(video, right_arrowLabel, 0.80, 0.90, clock)
                video.updateScreen(clock)

                # Get presentation time
                pres_time = clock.get()
                prob_end = pres_time + config.D_RESP_TIME

                # Variables for response
                user_response = None

                # Wait for first keypress only
                button, _ = arrow_bc.waitWithTime(clock, timeout=config.D_RESP_TIME)

                if button is not None:
                    user_response = button.key_name
                    # Convert key to arrow character
                    response_arrow = "←" if user_response == "LEFT" else "→"

                    # Show response arrow below prompt (prompt stays in same position)
                    response_text = Text(response_arrow, size=120, color=WHITE, font=FONT_PATH)
                    show_proportional(video, response_text, 0.5, 0.60, clock)
                    video.updateScreen(clock)

                # Wait remaining time using pygame directly (no cursor spin)
                current_time = clock.get()
                remaining = prob_end - current_time
                if remaining > 0:
                    pygame.time.wait(int(remaining))
                    clock._virtual_time = prob_end  # Sync virtual clock

                # Score response
                if user_response is not None:
                    is_correct = (user_response == correct_key)
                    correct_str = "correct" if is_correct else "incorrect"
                else:
                    is_correct = False
                    correct_str = "no response"

                print(f"[ARROW] Trial {arrow_trial + 1}/{config.NDIST}: {arrow_char} | Response: {user_response or 'none'} | {correct_str}")

                # Log arrow trial
                arrow_distract.logMessage(f"ARROW\t{arrow_trial + 1}\t{arrow_char}\t{correct_key}\t{user_response or 'NONE'}\t{1 if is_correct else 0}")

                # Blank screen between trials
                video.clear(BLACK)
                video.updateScreen(clock)
                clock.delay(config.D_BLANK_TIME)

                # Clear event queue
                pygame.event.clear()

            print(f"=== ARROW DISTRACTOR COMPLETE ===\n")

            # Reset display and clear events
            pygame.event.clear()
            video.clear(BLACK)
            video.updateScreen(clock)
            clock.delay(500)  # Brief pause after distractor

        # Item Recognition: all studied words (OLD) + equal NEW foils
        video.showInstructions(INSTRUCT_RECOGNITION_ITEM, clk=clock, font=FONT_PATH, size=20)

        # --- Build OLD items (all studied words) ---
        item_words = []
        for pair in studied_pairs:
            item_words.append({'word': pair['word1'], 'word_id': pair['word1_id']})
            item_words.append({'word': pair['word2'], 'word_id': pair['word2_id']})

        random.shuffle(item_words)
        n_old = len(item_words)

        item_test_trials = []

        # OLD trials
        for wi in item_words:
            item_test_trials.append({
                'type': 'item',
                'word': wi['word'],
                'word_id': wi['word_id'],
                'target': 1,   # OLD
                'is_old': True
            })

        # NEW foil trials (equal count)
        for _ in range(n_old):
            foil_word = probe_disp_pool.pop(0)
            foil_id = probe_disp_pool_id.isInPool(name=foil_word.name) + 1
            item_test_trials.append({
                'type': 'item',
                'word': foil_word.name,
                'word_id': foil_id,
                'target': 0,   # NEW
                'is_old': False
            })

        random.shuffle(item_test_trials)
        print(f"Item test trials: {len(item_test_trials)} ({n_old} old, {n_old} new)")

        # --- Present item test trials ---
        for trial in item_test_trials:
            pygame.event.clear()
            video.clear(BLACK)
            video.updateScreen(clock)

            # Debug (optional)
            # print("TRIAL KEYS:", trial.keys())
            # print("TRIAL:", trial)

            stim = Text(trial['word'], size=48, color=WHITE, font=FONT_PATH)
            show_proportional(video, stim, 0.5, 0.5, clock)

            left_label = Text(f"{inst_item_left} [z]", size=28, color=WHITE, font=FONT_PATH)
            right_label = Text(f"{inst_item_right} [/]", size=28, color=WHITE, font=FONT_PATH)
            show_proportional(video, left_label, 0.20, 0.90, clock)
            show_proportional(video, right_label, 0.80, 0.90, clock)

            video.updateScreen(clock)

            pres_time = clock.get()

            bc = ButtonChooser(Key(config.keyLeft), Key(config.keyRight), track=keyboard)
            button, button_time = bc.waitWithTime(clock, timeout=config.C_RESP_TIME)

            if button:
                rt = button_time - pres_time
                if keychoice == 0:
                    response = 1 if button.key_name == config.keyLeft else 0  # left=OLD
                else:
                    response = 0 if button.key_name == config.keyLeft else 1  # left=NEW
            else:
                rt = -1
                response = -1

            recog_acc = 1 if response == trial['target'] else 0

            log.logMessage(
                f"P2\t{test_trial_count}\tITEM\t{trial['word']}\t{trial['word_id']}\t"
                f"{trial['target']}\t{response}\t{recog_acc}\t{rt}"
            )
            recoglog.logMessage(
                f"P2\t{test_trial_count}\tITEM\t{trial['word_id']}\t{trial['target']}\t"
                f"{response}\t{recog_acc}\t{rt}"
            )

            video.clear(BLACK)
            video.updateScreen(clock)
            clock.delay(config.C_BLANK_TIME)

            # Clear pygame event queue to prevent progressive lag across test trials
            pygame.event.clear()

            test_trial_count += 1
    #################################################
    # Actual Task - Lists come in randomized triplets
    #################################################
    
    list_count = 1

    while list_count <= config.NLISTS:

        test_pattern_idx = random.randint(0, 2)
        test_pattern = test_patterns[test_pattern_idx]

        # Show instructions based on list number
        log.logMessage(f'LIST\t{list_count}')
        instructions = INSTRUCT_ROUNDN_ARROW
        title = f"Get ready for Round {list_count} of {config.NLISTS}!"
        num_pairs=config.NPAIRS

        # Show instructions
        print(f"\n=== LIST {list_count}: Showing instructions ===")
        video.showInstructions(instructions, clk=clock, font=FONT_PATH)

        # Show title
        print(f"=== Showing title screen ===")
        video.clear(BLACK)
        title_text = Text(title, size=36, color=WHITE, font=FONT_PATH)
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

        while pair_count <= num_pairs:
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

            stim1 = Text(probe1.name, size=72, color=WHITE, font=FONT_PATH)
            video.clear(BLACK)
            show_proportional(video, stim1, 0.5, 0.5, clock)
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

            stim2 = Text(probe2.name, size=72, color=WHITE, font=FONT_PATH)
            video.clear(BLACK)
            show_proportional(video, stim2, 0.5, 0.5, clock)
            video.updateScreen(clock)

            print(f"  Waiting {config.PRES_TIME}ms for word 2...")
            # Use delay_with_skip() to allow skipping with key combination
            delay_with_skip(clock, config.PRES_TIME)
            end_time = clock.get()

            elapsed = end_time - start_time
            print(f"  Word 2 displayed for {elapsed}ms")

            # Show fixation cross during jittered IPI
            video.clear(BLACK)
            fixation = Text("+", size=92, color=WHITE, font=FONT_PATH)
            show_proportional(video, fixation, 0.5, 0.49, clock)
            video.updateScreen(clock)

            print(f"  Inter-pair interval: {ipi}ms")
            delay_with_skip(clock, ipi)

            # Log this pair presentation
            log.logMessage(f'{list_count}\t{pair_count}\t{probe1.name}\t{word1_id}\t{probe2.name}\t{word2_id}\t{ipi}')
            stimlog.logMessage(f'{list_count}\t{pair_count}\t{word1_id}\t{word2_id}\t{ipi}') 

            pair_count += 1

        print("\n=== STUDY PHASE COMPLETE ===\n")

        #########################################
        # Distractor Task - Arrow Response
        #########################################

        # Log start
        arrow_distract.logMessage("START")

        if config.NDIST > 0:
            
            print(f"\n=== STARTING ARROW DISTRACTOR: {config.NDIST} trials ===")

            # Create button chooser for arrow responses (arrow keys)
            arrow_bc = ButtonChooser(Key("LEFT"), Key("RIGHT"), track=keyboard)

            for arrow_trial in range(config.NDIST):
                # Randomly choose left or right arrow
                is_left = random.choice([True, False])
                arrow_char = "←" if is_left else "→"
                correct_key = "LEFT" if is_left else "RIGHT"

                # Show arrow (centered, fixed position)
                video.clear(BLACK)
                arrow_text = Text(arrow_char, size=120, color=WHITE, font=FONT_PATH)
                show_proportional(video, arrow_text, 0.5, 0.45, clock)
                # Labels
                left_arrowLabel = Text("← [left arrow key]", size=28, color=WHITE, font=FONT_PATH)
                right_arrowLabel = Text("→ [right arrow key]", size=28, color=WHITE, font=FONT_PATH)
                show_proportional(video, left_arrowLabel, 0.20, 0.90, clock)
                show_proportional(video, right_arrowLabel, 0.80, 0.90, clock)
                video.updateScreen(clock)

                # Get presentation time
                pres_time = clock.get()
                prob_end = pres_time + config.D_RESP_TIME

                # Variables for response
                user_response = None

                # Wait for first keypress only
                button, _ = arrow_bc.waitWithTime(clock, timeout=config.D_RESP_TIME)

                if button is not None:
                    user_response = button.key_name
                    # Convert key to arrow character
                    response_arrow = "←" if user_response == "LEFT" else "→"

                    # Show response arrow below prompt (prompt stays in same position)
                    response_text = Text(response_arrow, size=120, color=WHITE, font=FONT_PATH)
                    show_proportional(video, response_text, 0.5, 0.60, clock)
                    video.updateScreen(clock)

                # Wait remaining time using pygame directly (no cursor spin)
                current_time = clock.get()
                remaining = prob_end - current_time
                if remaining > 0:
                    pygame.time.wait(int(remaining))
                    clock._virtual_time = prob_end  # Sync virtual clock

                # Score response
                if user_response is not None:
                    is_correct = (user_response == correct_key)
                    correct_str = "correct" if is_correct else "incorrect"
                else:
                    is_correct = False
                    correct_str = "no response"

                print(f"[ARROW] Trial {arrow_trial + 1}/{config.NDIST}: {arrow_char} | Response: {user_response or 'none'} | {correct_str}")

                # Log arrow trial
                arrow_distract.logMessage(f"ARROW\t{arrow_trial + 1}\t{arrow_char}\t{correct_key}\t{user_response or 'NONE'}\t{1 if is_correct else 0}")

                # Blank screen between trials
                video.clear(BLACK)
                video.updateScreen(clock)
                clock.delay(config.D_BLANK_TIME)

                # Clear event queue
                pygame.event.clear()

            print(f"=== ARROW DISTRACTOR COMPLETE ===\n")

            # Reset display and clear events
            pygame.event.clear()
            video.clear(BLACK)
            video.updateScreen(clock)
            clock.delay(500)  # Brief pause after distractor

        #########################################
        # Test Phase - Pure List Recognition (Assoc OR Item)
        #########################################

        # Determine test type for this list
        current_test_type = test_pattern[0]

        print(f"Test type for list {list_count}: {current_test_type}")

        # Show appropriate instruction
        if current_test_type == 'assoc':
            video.showInstructions(INSTRUCT_RECOGNITION_ASSOC, clk=clock, font=FONT_PATH, size=20)
        else:
            video.showInstructions(INSTRUCT_RECOGNITION_ITEM, clk=clock, font=FONT_PATH, size=20)

        #########################################
        # Create test trials - Pure Lists
        # Only create trials for the current test type
        #########################################

        test_trials = []

        if current_test_type == 'assoc':
            # Associative Recognition: half intact, half recombined
            pair_indices = list(range(len(studied_pairs)))
            random.shuffle(pair_indices)

            n_intact = len(pair_indices) // 2
            intact_indices = pair_indices[:n_intact]
            recombined_indices = pair_indices[n_intact:]

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

            # Create recombined pairs
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

            print(f"Test trials: {len(test_trials)} associative")

        else:  # item recognition
            # Item Recognition: all studied words (OLD) + equal NEW foils
            item_words = []
            for pair in studied_pairs:
                item_words.append({'word': pair['word1'], 'word_id': pair['word1_id']})
                item_words.append({'word': pair['word2'], 'word_id': pair['word2_id']})

            random.shuffle(item_words)
            n_old = len(item_words)

            # Add OLD item trials
            for word_info in item_words:
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

            print(f"Test trials: {len(test_trials)} item recognition ({n_old} old, {n_old} new)")

        # Shuffle all test trials
        random.shuffle(test_trials)

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

            if current_test_type == 'item':
                # Item Recognition: Show single word
                stim = Text(trial['word'], size=48, color=WHITE, font=FONT_PATH)
                show_proportional(video, stim, 0.5, 0.5, clock)

                # Labels
                left_label = Text(f"{inst_item_left} [z]", size=28, color=WHITE, font=FONT_PATH)
                right_label = Text(f"{inst_item_right} [/]", size=28, color=WHITE, font=FONT_PATH)
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
                    # Response coding based on counterbalancing
                    if keychoice == 0:
                        # Left=OLD(1), Right=NEW(0)
                        if button.key_name == config.keyLeft:
                            response = 1  # OLD
                        else:
                            response = 0  # NEW
                    else:
                        # Left=NEW(0), Right=OLD(1)
                        if button.key_name == config.keyLeft:
                            response = 0  # NEW
                        else:
                            response = 1  # OLD
                else:
                    rt = -1
                    response = -1

                # Score
                recog_acc = 1 if response == trial['target'] else 0

                # Log
                log.logMessage(f"{list_count}\t{test_trial_count}\tITEM\t{trial['word']}\t{trial['word_id']}\t{trial['target']}\t{response}\t{recog_acc}\t{rt}")
                recoglog.logMessage(f"{list_count}\t{test_trial_count}\tITEM\t{trial['word_id']}\t{trial['target']}\t{response}\t{recog_acc}\t{rt}")

            else:  # current_test_type == 'assoc'
                # Associative Recognition: Show two words
                stim = Text(f"{trial['word1']}  {trial['word2']}", size=48, color=WHITE, font=FONT_PATH)
                show_proportional(video, stim, 0.5, 0.5, clock)

                # Labels
                left_label = Text(f"{inst_assoc_left} [z]", size=28, color=WHITE, font=FONT_PATH)
                right_label = Text(f"{inst_assoc_right} [/]", size=28, color=WHITE, font=FONT_PATH)
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
                    # Response coding based on counterbalancing
                    if keychoice == 0:
                        # Left=INTACT(1), Right=RECOMBINED(0)
                        if button.key_name == config.keyLeft:
                            response = 1  # INTACT
                        else:
                            response = 0  # RECOMBINED
                    else:
                        # Left=RECOMBINED(0), Right=INTACT(1)
                        if button.key_name == config.keyLeft:
                            response = 0  # RECOMBINED
                        else:
                            response = 1  # INTACT
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

        list_count+=1
            
        # Show instructions based on list number
        log.logMessage(f'LIST\t{list_count}')
        instructions = INSTRUCT_ROUNDN_ARROW
        title = f"Get ready for Round {list_count + 1} of {config.NLISTS}!"
        num_pairs=config.NPAIRS

        # Show instructions
        print(f"\n=== LIST {list_count}: Showing instructions ===")
        video.showInstructions(instructions, clk=clock, font=FONT_PATH)

        # Show title
        print(f"=== Showing title screen ===")
        video.clear(BLACK)
        title_text = Text(title, size=36, color=WHITE, font=FONT_PATH)
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

        while pair_count <= num_pairs:
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

            stim1 = Text(probe1.name, size=72, color=WHITE, font=FONT_PATH)
            video.clear(BLACK)
            show_proportional(video, stim1, 0.5, 0.5, clock)
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

            stim2 = Text(probe2.name, size=72, color=WHITE, font=FONT_PATH)
            video.clear(BLACK)
            show_proportional(video, stim2, 0.5, 0.5, clock)
            video.updateScreen(clock)

            print(f"  Waiting {config.PRES_TIME}ms for word 2...")
            # Use delay_with_skip() to allow skipping with key combination
            delay_with_skip(clock, config.PRES_TIME)
            end_time = clock.get()

            elapsed = end_time - start_time
            print(f"  Word 2 displayed for {elapsed}ms")

            # Show fixation cross during jittered IPI
            video.clear(BLACK)
            fixation = Text("+", size=92, color=WHITE, font=FONT_PATH)
            show_proportional(video, fixation, 0.5, 0.49, clock)
            video.updateScreen(clock)

            print(f"  Inter-pair interval: {ipi}ms")
            delay_with_skip(clock, ipi)

            # Log this pair presentation
            log.logMessage(f'{list_count}\t{pair_count}\t{probe1.name}\t{word1_id}\t{probe2.name}\t{word2_id}\t{ipi}')
            stimlog.logMessage(f'{list_count}\t{pair_count}\t{word1_id}\t{word2_id}\t{ipi}') 

            pair_count += 1

        print("\n=== STUDY PHASE COMPLETE ===\n")

        #########################################
        # Distractor Task - Arrow Response
        #########################################

        # Log start
        arrow_distract.logMessage("START")

        if config.NDIST > 0:
            
            print(f"\n=== STARTING ARROW DISTRACTOR: {config.NDIST} trials ===")

            # Create button chooser for arrow responses (arrow keys)
            arrow_bc = ButtonChooser(Key("LEFT"), Key("RIGHT"), track=keyboard)

            for arrow_trial in range(config.NDIST):
                # Randomly choose left or right arrow
                is_left = random.choice([True, False])
                arrow_char = "←" if is_left else "→"
                correct_key = "LEFT" if is_left else "RIGHT"

                # Show arrow (centered, fixed position)
                video.clear(BLACK)
                arrow_text = Text(arrow_char, size=120, color=WHITE, font=FONT_PATH)
                show_proportional(video, arrow_text, 0.5, 0.45, clock)
                # Labels
                left_arrowLabel = Text("← [left arrow key]", size=28, color=WHITE, font=FONT_PATH)
                right_arrowLabel = Text("→ [right arrow key]", size=28, color=WHITE, font=FONT_PATH)
                show_proportional(video, left_arrowLabel, 0.20, 0.90, clock)
                show_proportional(video, right_arrowLabel, 0.80, 0.90, clock)
                video.updateScreen(clock)

                # Get presentation time
                pres_time = clock.get()
                prob_end = pres_time + config.D_RESP_TIME

                # Variables for response
                user_response = None

                # Wait for first keypress only
                button, _ = arrow_bc.waitWithTime(clock, timeout=config.D_RESP_TIME)

                if button is not None:
                    user_response = button.key_name
                    # Convert key to arrow character
                    response_arrow = "←" if user_response == "LEFT" else "→"

                    # Show response arrow below prompt (prompt stays in same position)
                    response_text = Text(response_arrow, size=120, color=WHITE, font=FONT_PATH)
                    show_proportional(video, response_text, 0.5, 0.60, clock)
                    video.updateScreen(clock)

                # Wait remaining time using pygame directly (no cursor spin)
                current_time = clock.get()
                remaining = prob_end - current_time
                if remaining > 0:
                    pygame.time.wait(int(remaining))
                    clock._virtual_time = prob_end  # Sync virtual clock

                # Score response
                if user_response is not None:
                    is_correct = (user_response == correct_key)
                    correct_str = "correct" if is_correct else "incorrect"
                else:
                    is_correct = False
                    correct_str = "no response"

                print(f"[ARROW] Trial {arrow_trial + 1}/{config.NDIST}: {arrow_char} | Response: {user_response or 'none'} | {correct_str}")

                # Log arrow trial
                arrow_distract.logMessage(f"ARROW\t{arrow_trial + 1}\t{arrow_char}\t{correct_key}\t{user_response or 'NONE'}\t{1 if is_correct else 0}")

                # Blank screen between trials
                video.clear(BLACK)
                video.updateScreen(clock)
                clock.delay(config.D_BLANK_TIME)

                # Clear event queue
                pygame.event.clear()

            print(f"=== ARROW DISTRACTOR COMPLETE ===\n")

            # Reset display and clear events
            pygame.event.clear()
            video.clear(BLACK)
            video.updateScreen(clock)
            clock.delay(500)  # Brief pause after distractor

        #########################################
        # Test Phase - Pure List Recognition (Assoc OR Item)
        #########################################

        # Determine test type for this list
        current_test_type = test_pattern[1]

        print(f"Test type for list {list_count}: {current_test_type}")

        # Show appropriate instruction
        if current_test_type == 'assoc':
            video.showInstructions(INSTRUCT_RECOGNITION_ASSOC, clk=clock, font=FONT_PATH, size=20)
        else:
            video.showInstructions(INSTRUCT_RECOGNITION_ITEM, clk=clock, font=FONT_PATH, size=20)

        #########################################
        # Create test trials - Pure Lists
        # Only create trials for the current test type
        #########################################

        test_trials = []

        if current_test_type == 'assoc':
            # Associative Recognition: half intact, half recombined
            pair_indices = list(range(len(studied_pairs)))
            random.shuffle(pair_indices)

            n_intact = len(pair_indices) // 2
            intact_indices = pair_indices[:n_intact]
            recombined_indices = pair_indices[n_intact:]

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

            # Create recombined pairs
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

            print(f"Test trials: {len(test_trials)} associative")

        else:  # item recognition
            # Item Recognition: all studied words (OLD) + equal NEW foils
            item_words = []
            for pair in studied_pairs:
                item_words.append({'word': pair['word1'], 'word_id': pair['word1_id']})
                item_words.append({'word': pair['word2'], 'word_id': pair['word2_id']})

            random.shuffle(item_words)
            n_old = len(item_words)

            # Add OLD item trials
            for word_info in item_words:
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

            print(f"Test trials: {len(test_trials)} item recognition ({n_old} old, {n_old} new)")

        # Shuffle all test trials
        random.shuffle(test_trials)

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

            if current_test_type == 'item':
                # Item Recognition: Show single word
                stim = Text(trial['word'], size=48, color=WHITE, font=FONT_PATH)
                show_proportional(video, stim, 0.5, 0.5, clock)

                # Labels
                left_label = Text(f"{inst_item_left} [z]", size=28, color=WHITE, font=FONT_PATH)
                right_label = Text(f"{inst_item_right} [/]", size=28, color=WHITE, font=FONT_PATH)
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
                    # Response coding based on counterbalancing
                    if keychoice == 0:
                        # Left=OLD(1), Right=NEW(0)
                        if button.key_name == config.keyLeft:
                            response = 1  # OLD
                        else:
                            response = 0  # NEW
                    else:
                        # Left=NEW(0), Right=OLD(1)
                        if button.key_name == config.keyLeft:
                            response = 0  # NEW
                        else:
                            response = 1  # OLD
                else:
                    rt = -1
                    response = -1

                # Score
                recog_acc = 1 if response == trial['target'] else 0

                # Log
                log.logMessage(f"{list_count}\t{test_trial_count}\tITEM\t{trial['word']}\t{trial['word_id']}\t{trial['target']}\t{response}\t{recog_acc}\t{rt}")
                recoglog.logMessage(f"{list_count}\t{test_trial_count}\tITEM\t{trial['word_id']}\t{trial['target']}\t{response}\t{recog_acc}\t{rt}")

            else:  # current_test_type == 'assoc'
                # Associative Recognition: Show two words
                stim = Text(f"{trial['word1']}  {trial['word2']}", size=48, color=WHITE, font=FONT_PATH)
                show_proportional(video, stim, 0.5, 0.5, clock)

                # Labels
                left_label = Text(f"{inst_assoc_left} [z]", size=28, color=WHITE, font=FONT_PATH)
                right_label = Text(f"{inst_assoc_right} [/]", size=28, color=WHITE, font=FONT_PATH)
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
                    # Response coding based on counterbalancing
                    if keychoice == 0:
                        # Left=INTACT(1), Right=RECOMBINED(0)
                        if button.key_name == config.keyLeft:
                            response = 1  # INTACT
                        else:
                            response = 0  # RECOMBINED
                    else:
                        # Left=RECOMBINED(0), Right=INTACT(1)
                        if button.key_name == config.keyLeft:
                            response = 0  # RECOMBINED
                        else:
                            response = 1  # INTACT
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

        list_count+=1
            
        # Show instructions based on list number
        log.logMessage(f'LIST\t{list_count}')
        instructions = INSTRUCT_ROUNDN_ARROW
        title = f"Get ready for Round {list_count + 2} of {config.NLISTS}!"
        num_pairs=config.NPAIRS

        # Show instructions
        print(f"\n=== LIST {list_count}: Showing instructions ===")
        video.showInstructions(instructions, clk=clock, font=FONT_PATH)

        # Show title
        print(f"=== Showing title screen ===")
        video.clear(BLACK)
        title_text = Text(title, size=36, color=WHITE, font=FONT_PATH)
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

        while pair_count <= num_pairs:
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

            stim1 = Text(probe1.name, size=72, color=WHITE, font=FONT_PATH)
            video.clear(BLACK)
            show_proportional(video, stim1, 0.5, 0.5, clock)
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

            stim2 = Text(probe2.name, size=72, color=WHITE, font=FONT_PATH)
            video.clear(BLACK)
            show_proportional(video, stim2, 0.5, 0.5, clock)
            video.updateScreen(clock)

            print(f"  Waiting {config.PRES_TIME}ms for word 2...")
            # Use delay_with_skip() to allow skipping with key combination
            delay_with_skip(clock, config.PRES_TIME)
            end_time = clock.get()

            elapsed = end_time - start_time
            print(f"  Word 2 displayed for {elapsed}ms")

            # Show fixation cross during jittered IPI
            video.clear(BLACK)
            fixation = Text("+", size=92, color=WHITE, font=FONT_PATH)
            show_proportional(video, fixation, 0.5, 0.49, clock)
            video.updateScreen(clock)

            print(f"  Inter-pair interval: {ipi}ms")
            delay_with_skip(clock, ipi)

            # Log this pair presentation
            log.logMessage(f'{list_count}\t{pair_count}\t{probe1.name}\t{word1_id}\t{probe2.name}\t{word2_id}\t{ipi}')
            stimlog.logMessage(f'{list_count}\t{pair_count}\t{word1_id}\t{word2_id}\t{ipi}') 

            pair_count += 1

        print("\n=== STUDY PHASE COMPLETE ===\n")

        #########################################
        # Distractor Task - Arrow Response
        #########################################

        # Log start
        arrow_distract.logMessage("START")

        if config.NDIST > 0:
            
            print(f"\n=== STARTING ARROW DISTRACTOR: {config.NDIST} trials ===")

            # Create button chooser for arrow responses (arrow keys)
            arrow_bc = ButtonChooser(Key("LEFT"), Key("RIGHT"), track=keyboard)

            for arrow_trial in range(config.NDIST):
                # Randomly choose left or right arrow
                is_left = random.choice([True, False])
                arrow_char = "←" if is_left else "→"
                correct_key = "LEFT" if is_left else "RIGHT"

                # Show arrow (centered, fixed position)
                video.clear(BLACK)
                arrow_text = Text(arrow_char, size=120, color=WHITE, font=FONT_PATH)
                show_proportional(video, arrow_text, 0.5, 0.45, clock)
                # Labels
                left_arrowLabel = Text("← [left arrow key]", size=28, color=WHITE, font=FONT_PATH)
                right_arrowLabel = Text("→ [right arrow key]", size=28, color=WHITE, font=FONT_PATH)
                show_proportional(video, left_arrowLabel, 0.20, 0.90, clock)
                show_proportional(video, right_arrowLabel, 0.80, 0.90, clock)
                video.updateScreen(clock)

                # Get presentation time
                pres_time = clock.get()
                prob_end = pres_time + config.D_RESP_TIME

                # Variables for response
                user_response = None

                # Wait for first keypress only
                button, _ = arrow_bc.waitWithTime(clock, timeout=config.D_RESP_TIME)

                if button is not None:
                    user_response = button.key_name
                    # Convert key to arrow character
                    response_arrow = "←" if user_response == "LEFT" else "→"

                    # Show response arrow below prompt (prompt stays in same position)
                    response_text = Text(response_arrow, size=120, color=WHITE, font=FONT_PATH)
                    show_proportional(video, response_text, 0.5, 0.60, clock)
                    video.updateScreen(clock)

                # Wait remaining time using pygame directly (no cursor spin)
                current_time = clock.get()
                remaining = prob_end - current_time
                if remaining > 0:
                    pygame.time.wait(int(remaining))
                    clock._virtual_time = prob_end  # Sync virtual clock

                # Score response
                if user_response is not None:
                    is_correct = (user_response == correct_key)
                    correct_str = "correct" if is_correct else "incorrect"
                else:
                    is_correct = False
                    correct_str = "no response"

                print(f"[ARROW] Trial {arrow_trial + 1}/{config.NDIST}: {arrow_char} | Response: {user_response or 'none'} | {correct_str}")

                # Log arrow trial
                arrow_distract.logMessage(f"ARROW\t{arrow_trial + 1}\t{arrow_char}\t{correct_key}\t{user_response or 'NONE'}\t{1 if is_correct else 0}")

                # Blank screen between trials
                video.clear(BLACK)
                video.updateScreen(clock)
                clock.delay(config.D_BLANK_TIME)

                # Clear event queue
                pygame.event.clear()

            print(f"=== ARROW DISTRACTOR COMPLETE ===\n")

            # Reset display and clear events
            pygame.event.clear()
            video.clear(BLACK)
            video.updateScreen(clock)
            clock.delay(500)  # Brief pause after distractor

        #########################################
        # Test Phase - Pure List Recognition (Assoc OR Item)
        #########################################

        # Determine test type for this list
        current_test_type = test_pattern[2]

        print(f"Test type for list {list_count}: {current_test_type}")

        # Show appropriate instruction
        if current_test_type == 'assoc':
            video.showInstructions(INSTRUCT_RECOGNITION_ASSOC, clk=clock, font=FONT_PATH, size=20)
        else:
            video.showInstructions(INSTRUCT_RECOGNITION_ITEM, clk=clock, font=FONT_PATH, size=20)

        #########################################
        # Create test trials - Pure Lists
        # Only create trials for the current test type
        #########################################

        test_trials = []

        if current_test_type == 'assoc':
            # Associative Recognition: half intact, half recombined
            pair_indices = list(range(len(studied_pairs)))
            random.shuffle(pair_indices)

            n_intact = len(pair_indices) // 2
            intact_indices = pair_indices[:n_intact]
            recombined_indices = pair_indices[n_intact:]

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

            # Create recombined pairs
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

            print(f"Test trials: {len(test_trials)} associative")

        else:  # item recognition
            # Item Recognition: all studied words (OLD) + equal NEW foils
            item_words = []
            for pair in studied_pairs:
                item_words.append({'word': pair['word1'], 'word_id': pair['word1_id']})
                item_words.append({'word': pair['word2'], 'word_id': pair['word2_id']})

            random.shuffle(item_words)
            n_old = len(item_words)

            # Add OLD item trials
            for word_info in item_words:
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

            print(f"Test trials: {len(test_trials)} item recognition ({n_old} old, {n_old} new)")

        # Shuffle all test trials
        random.shuffle(test_trials)

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

            if current_test_type == 'item':
                # Item Recognition: Show single word
                stim = Text(trial['word'], size=48, color=WHITE, font=FONT_PATH)
                show_proportional(video, stim, 0.5, 0.5, clock)

                # Labels
                left_label = Text(f"{inst_item_left} [z]", size=28, color=WHITE, font=FONT_PATH)
                right_label = Text(f"{inst_item_right} [/]", size=28, color=WHITE, font=FONT_PATH)
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
                    # Response coding based on counterbalancing
                    if keychoice == 0:
                        # Left=OLD(1), Right=NEW(0)
                        if button.key_name == config.keyLeft:
                            response = 1  # OLD
                        else:
                            response = 0  # NEW
                    else:
                        # Left=NEW(0), Right=OLD(1)
                        if button.key_name == config.keyLeft:
                            response = 0  # NEW
                        else:
                            response = 1  # OLD
                else:
                    rt = -1
                    response = -1

                # Score
                recog_acc = 1 if response == trial['target'] else 0

                # Log
                log.logMessage(f"{list_count}\t{test_trial_count}\tITEM\t{trial['word']}\t{trial['word_id']}\t{trial['target']}\t{response}\t{recog_acc}\t{rt}")
                recoglog.logMessage(f"{list_count}\t{test_trial_count}\tITEM\t{trial['word_id']}\t{trial['target']}\t{response}\t{recog_acc}\t{rt}")

            else:  # current_test_type == 'assoc'
                # Associative Recognition: Show two words
                stim = Text(f"{trial['word1']}  {trial['word2']}", size=48, color=WHITE, font=FONT_PATH)
                show_proportional(video, stim, 0.5, 0.5, clock)

                # Labels
                left_label = Text(f"{inst_assoc_left} [z]", size=28, color=WHITE, font=FONT_PATH)
                right_label = Text(f"{inst_assoc_right} [/]", size=28, color=WHITE, font=FONT_PATH)
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
                    # Response coding based on counterbalancing
                    if keychoice == 0:
                        # Left=INTACT(1), Right=RECOMBINED(0)
                        if button.key_name == config.keyLeft:
                            response = 1  # INTACT
                        else:
                            response = 0  # RECOMBINED
                    else:
                        # Left=RECOMBINED(0), Right=INTACT(1)
                        if button.key_name == config.keyLeft:
                            response = 0  # RECOMBINED
                        else:
                            response = 1  # INTACT
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
                          size=36, color=WHITE, font=FONT_PATH)
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
