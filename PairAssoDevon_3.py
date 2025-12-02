#!/usr/bin/env python3
"""
Paired Associate Recognition EEG Experiment - PyEPL3 Version

Converted from Python 2 PyEPL to Python 3 PyEPL3.
Sequential word presentation with item and associative recognition tests.
"""

import sys
import random
import time
import math
from pathlib import Path

# Import PyEPL3
from pyepl3 import (
    Experiment, VideoTrack, KeyTrack, LogTrack, EEGTrack,
    PresentationClock, Text, Key, ButtonChooser,
    WHITE, BLACK, RED, GREEN, BLUE, Color,
    TextPool, mathDistract
)


#########################################
# Initialization
#########################################

# Create experiment object
exp = Experiment(name="PairAssocRecog")

# Allow users to break out with escape key
exp.setBreak()

# Load configuration
exp.loadConfig("config_pairassoc.py")

# Get the subject configuration
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

# Reset display to black
video.clear(BLACK)

# Create PresentationClock
clock = PresentationClock()

video.updateScreen(clock)


##################
# Testing condition counterbalance keys
##################

subjectID = int(sys.argv[sys.argv.index('-s') + 1])

keychoice = subjectID % 4
if keychoice == 0:
    KeyR = config.keyLeft
    KeyNR = config.keyRight
    instMleft = "INTACT"
    instMright = "RECOMBINED"
else:
    KeyR = config.keyLeft
    KeyNR = config.keyRight
    instMleft = "RECOMBINED"
    instMright = "INTACT"

print(keychoice)


######################################
## Build Pools
######################################

probe_disp_pool = TextPool("raw_pools/nouns.txt")
probe_disp_pool_id = TextPool("raw_pools/nouns.txt")

random.shuffle(probe_disp_pool)

list_count = 1


#################################
# Paired association learning
#################################

while list_count <= (config.NLISTS + config.RUN_PRACTICE):
    log.logMessage(f'LIST\t{list_count}')

    ########################
    # Set the instructions
    ########################
    if list_count == config.RUN_PRACTICE:
        with open("instruct/instruct0.txt") as f:
            instructions = f.read()
        title = "Get ready for the Practice Round!"
    elif list_count == (1 + config.RUN_PRACTICE):
        with open("instruct/instruct1.txt") as f:
            instructions = f.read()
        title = f"Get ready for Round 1 of {config.NLISTS}!"
    elif list_count > (1 + config.RUN_PRACTICE):
        with open("instruct/instructN.txt") as f:
            instructions = f.read()
        title = f"Get ready for Round {list_count - config.RUN_PRACTICE} of {config.NLISTS}!"

    #####################################
    # Show the experiment instructions
    #####################################
    video.showInstructions(instructions, clk=clock)

    # Reset the display to black
    video.clear(BLACK)

    stim = Text(title, size=36, color=WHITE)
    video.showCentered(stim, clock)
    video.updateScreen(clock)

    # Wait for experimenter to continue
    bc = ButtonChooser(Key("LSHIFT"), Key("RSHIFT"), Key("BACKSLASH"), track=keyboard)
    button, timestamp = bc.waitWithTime(clock, timeout=config.PRES_TIME)

    #####################
    ## Study phase - sequential word presentation
    #####################

    # Track all studied words and pairs for test phase
    studied_words = []  # All 32 words presented
    studied_pairs = []  # All 16 pairs for associative test

    pair_count = 1

    # Present words sequentially: W1, W2 (pair 1), W3, W4 (pair 2), etc.
    while pair_count <= config.NPAIRS:
        # Get two words for this pair
        probe1 = probe_disp_pool.pop(0)
        probe2 = probe_disp_pool.pop(0)

        # Get word IDs for logging
        word1_id = probe_disp_pool_id.isInPool(name=probe1.name) + 1
        word2_id = probe_disp_pool_id.isInPool(name=probe2.name) + 1

        # Store this pair for associative test
        studied_pairs.append({
            'pair_num': pair_count,
            'word1': probe1.name,
            'word1_id': word1_id,
            'word2': probe2.name,
            'word2_id': word2_id
        })

        # Add both words to studied list for item test
        studied_words.append({'word': probe1.name, 'word_id': word1_id})
        studied_words.append({'word': probe2.name, 'word_id': word2_id})

        # Set jittered IPI for after second word
        IPIvalue = list(range(config.IPI_lower, config.IPI_upper + 1))
        random.shuffle(IPIvalue)
        IPI = IPIvalue.pop(0)

        # Present first word (2000ms)
        stim1 = Text(probe1.name, size=72, color=WHITE)
        video.clear(BLACK)
        video.showCentered(stim1, clock)
        video.updateScreen(clock)
        clock.delay(config.PRES_TIME)

        # 0ms gap (immediately clear and show next word)
        video.clear(BLACK)
        video.updateScreen(clock)

        # Present second word (2000ms)
        stim2 = Text(probe2.name, size=72, color=WHITE)
        video.clear(BLACK)
        video.showCentered(stim2, clock)
        video.updateScreen(clock)
        clock.delay(config.PRES_TIME)

        # Clear screen and wait jittered IPI
        video.clear(BLACK)
        video.updateScreen(clock)
        clock.delay(IPI)

        # Log this pair presentation
        log.logMessage(f'{list_count}\t{pair_count}\t{probe1.name}\t{word1_id}\t{probe2.name}\t{word2_id}\t{IPI}')
        stimlog.logMessage(f'{list_count}\t{pair_count}\t{word1_id}\t{word2_id}\t{IPI}')

        pair_count += 1

    ####################
    ## Distractor
    ####################

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
            minDuration=((config.D_RESP_TIME + config.D_BLANK_TIME) * config.NDIST),
            blanktime=config.D_BLANK_TIME
        )

        # Reset the display to black
        video.clear(BLACK)
        video.updateScreen(clock)

    ####################
    ## Test phase - Item + Associative Recognition
    ####################

    if list_count == config.RUN_PRACTICE:
        with open("instruct/recognition_noorder.txt") as f:
            instructions = f.read()
        video.showInstructions(instructions, clk=clock)
        start = clock.get()
    elif list_count > 1:
        title = "Get ready for recognition"
        video.clear(BLACK)
        stim = Text(title, size=36, color=WHITE)
        video.showCentered(stim, clock)
        video.updateScreen(clock)

    video.clear(BLACK)
    video.updateScreen(clock)

    ############################
    ## Create test trials
    ############################

    test_trials = []

    # 1. Create 8 Item Recognition trials (4 old, 4 new)
    indices_list = list(range(len(studied_words)))
    random.shuffle(indices_list)
    old_word_indices = indices_list[:4]

    for idx in old_word_indices:
        test_trials.append({
            'type': 'item',
            'word': studied_words[idx]['word'],
            'word_id': studied_words[idx]['word_id'],
            'target': 1,  # OLD
            'is_old': True
        })

    # Select 4 new foil words (not in studied words)
    for i in range(4):
        foil_word = probe_disp_pool.pop(0)
        foil_id = probe_disp_pool_id.isInPool(name=foil_word.name) + 1
        test_trials.append({
            'type': 'item',
            'word': foil_word.name,
            'word_id': foil_id,
            'target': 0,  # NEW
            'is_old': False
        })

    # 2. Create 8 Associative Recognition trials (4 intact, 4 recombined)
    pair_indices_list = list(range(len(studied_pairs)))
    random.shuffle(pair_indices_list)
    intact_pair_indices = pair_indices_list[:4]

    for idx in intact_pair_indices:
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

    # Create 4 recombined pairs from remaining pairs
    remaining_pairs = [studied_pairs[i] for i in range(len(studied_pairs))
                      if i not in intact_pair_indices]

    for i in range(4):
        # Get two different pairs and swap their second words
        pair1 = remaining_pairs[i]
        pair2 = remaining_pairs[(i + 1) % len(remaining_pairs)]
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

    # Shuffle all 16 test trials together
    random.shuffle(test_trials)

    ############################
    ## Present test trials
    ############################

    test_trial_count = 1

    for trial in test_trials:
        video.clear(BLACK)
        video.updateScreen(clock)

        if trial['type'] == 'item':
            # Item Recognition: Show single word
            stim = Text(trial['word'], size=48, color=WHITE)

            # Calculate center position for main stimulus
            screen_width, screen_height = video.getResolution()
            stim_width, stim_height = stim.getSize()
            x = (screen_width - stim_width) // 2
            y = (screen_height - stim_height) // 2
            video.show(stim, (x, y), clock)

            # Labels: OLD (left) vs NEW (right)
            leftinstruct = Text("OLD", size=24, color=Color(128, 128, 128))
            left_x = int(screen_width * 0.20) - (leftinstruct.getSize()[0] // 2)
            left_y = int(screen_height * 0.90) - (leftinstruct.getSize()[1] // 2)
            video.show(leftinstruct, (left_x, left_y), clock)

            rightinstruct = Text("NEW", size=24, color=Color(128, 128, 128))
            right_x = int(screen_width * 0.80) - (rightinstruct.getSize()[0] // 2)
            right_y = int(screen_height * 0.90) - (rightinstruct.getSize()[1] // 2)
            video.show(rightinstruct, (right_x, right_y), clock)

            pres_time = video.updateScreen(clock)

            # Wait for response
            bc = ButtonChooser(Key(config.keyLeft), Key(config.keyRight), track=keyboard)
            button, bc_time = bc.waitWithTime(clock, timeout=config.C_RESP_TIME)

            if button is None:
                response = -1
                rt = -1
            elif button.key_name == config.keyLeft:
                response = 1  # OLD
                rt = bc_time - pres_time
            elif button.key_name == config.keyRight:
                response = 0  # NEW
                rt = bc_time - pres_time
            else:
                response = -1
                rt = -1

            # Score: correct if response matches target
            recog_acc = 1 if response == trial['target'] else 0

            # Log item trial
            log.logMessage(f"{list_count}\t{test_trial_count}\tITEM\t{trial['word']}\t{trial['word_id']}\t{trial['target']}\t{response}\t{recog_acc}\t{rt}")
            recoglog.logMessage(f"{list_count}\t{test_trial_count}\tITEM\t{trial['word_id']}\t{trial['target']}\t{response}\t{recog_acc}\t{rt}")

        else:  # trial['type'] == 'assoc'
            # Associative Recognition: Show two words
            stim = Text(f"{trial['word1']}  {trial['word2']}", size=48, color=WHITE)

            # Calculate center position
            screen_width, screen_height = video.getResolution()
            stim_width, stim_height = stim.getSize()
            x = (screen_width - stim_width) // 2
            y = (screen_height - stim_height) // 2
            video.show(stim, (x, y), clock)

            # Labels: INTACT (left) vs RECOMBINED (right)
            leftinstruct = Text("INTACT", size=24, color=Color(128, 128, 128))
            left_x = int(screen_width * 0.20) - (leftinstruct.getSize()[0] // 2)
            left_y = int(screen_height * 0.90) - (leftinstruct.getSize()[1] // 2)
            video.show(leftinstruct, (left_x, left_y), clock)

            rightinstruct = Text("RECOMBINED", size=24, color=Color(128, 128, 128))
            right_x = int(screen_width * 0.80) - (rightinstruct.getSize()[0] // 2)
            right_y = int(screen_height * 0.90) - (rightinstruct.getSize()[1] // 2)
            video.show(rightinstruct, (right_x, right_y), clock)

            pres_time = video.updateScreen(clock)

            # Wait for response
            bc = ButtonChooser(Key(config.keyLeft), Key(config.keyRight), track=keyboard)
            button, bc_time = bc.waitWithTime(clock, timeout=config.C_RESP_TIME)

            if button is None:
                response = -1
                rt = -1
            elif button.key_name == config.keyLeft:
                response = 1  # INTACT
                rt = bc_time - pres_time
            elif button.key_name == config.keyRight:
                response = 0  # RECOMBINED
                rt = bc_time - pres_time
            else:
                response = -1
                rt = -1

            # Score: correct if response matches target
            recog_acc = 1 if response == trial['target'] else 0

            # Log associative trial
            log.logMessage(f"{list_count}\t{test_trial_count}\tASSOC\t{trial['word1']}\t{trial['word1_id']}\t{trial['word2']}\t{trial['word2_id']}\t{trial['target']}\t{response}\t{recog_acc}\t{rt}")
            recoglog.logMessage(f"{list_count}\t{test_trial_count}\tASSOC\t{trial['word1_id']}\t{trial['word2_id']}\t{trial['target']}\t{response}\t{recog_acc}\t{rt}")

        video.clear(BLACK)
        video.updateScreen(clock)
        clock.delay(config.C_BLANK_TIME)

        test_trial_count += 1

    list_count += 1


####################
## All done!
####################

clock.delay(1000)

# Reset the display to black
video.clear(BLACK)

# Show thank you message
with open("instruct/thankyou.txt") as f:
    instructions = f.read()
video.showInstructions(instructions, clk=clock)

# Reset the display to black
video.clear(BLACK)

# Final message
stim = Text("Please get the experimenter\nto complete this session.", size=36, color=WHITE)
video.showCentered(stim, clock)
video.updateScreen(clock)

# Wait for experimenter
bc = ButtonChooser(Key("LSHIFT"), Key("RSHIFT"), Key("BACKSLASH"), track=keyboard)
button, timestamp = bc.waitWithTime(clock, timeout=1800000)

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
