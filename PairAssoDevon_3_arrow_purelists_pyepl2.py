# pylint: skip-file
# type: ignore
#########################################
# Paired Associate Recognition EEG Experiment - PyEPL2 Version
#
# Adapted from PairAssoDevon_3_arrow_purelists.py (PyEPL3) to PyEPL2.
#
# Sequential word presentation with item and associative recognition tests.
# Uses arrow distractor task instead of math distractor.
#
# USAGE:
#   python PairAssoDevon_3_arrow_purelists_pyepl2.py -s <subject_id>
#   OR with explicit config:
#   python PairAssoDevon_3_arrow_purelists_pyepl2.py -s <subject_id> --config config_pairassoc_pyepl2.py
#
# CONFIG: Requires config.py in experiment directory (or use --config flag)
#   Required parameters: NLISTS, RUN_PRACTICE, NPAIRS, NPAIRS_PRACTICE,
#   PRES_TIME, IPI_lower, IPI_upper, NDIST, D_RESP_TIME, D_BLANK_TIME,
#   C_RESP_TIME, C_BLANK_TIME, keyLeft, keyRight
#
# SETUP: cp config_pairassoc_pyepl2.py config.py
#########################################

#########################################
# Initialization
if 1 == 1:  # if statement to help sort the code into blocks
    import sys, random, time, math

    # get access to pyepl objects & functions
    from pyepl.locals import *

    # define & load required modules
    loadmodules = 'TextPool2',
    sys.path.append('modules')
    for module in loadmodules:
        exec "from " + module + " import *"

    # create an experiment object:
    # parse command-line arguments
    # & initialize pyepl subsystems
    exp = Experiment()

    # allow users to break out of the experiment with escape-F1
    # (the default key combo)
    exp.setBreak()

    # get the subject configuration
    # Note: Config is loaded from config.py in the experiment directory
    # Copy config_pairassoc_pyepl2.py to config.py before running
    config = exp.getConfig()

    # Debug: Print config values to verify they loaded correctly
    print "=== CONFIG VALUES ==="
    print "NLISTS:", config.NLISTS
    print "RUN_PRACTICE:", config.RUN_PRACTICE
    print "NPAIRS:", config.NPAIRS
    print "NPAIRS_PRACTICE:", config.NPAIRS_PRACTICE
    print "PRES_TIME:", config.PRES_TIME
    print "NDIST:", config.NDIST
    print "===================="

    # Create a VideoTrack object for interfacing
    # with monitor, and a KeyTrack object for
    # interfacing with keyboard
    vt = VideoTrack("video")
    kt = KeyTrack("key")
    EEGs = EEGTrack("eeg")

    stimlog = LogTrack("stimlog")  # used for scoring-only (is non-human readable)
    recoglog = LogTrack("recoglog")
    arrow_distract = LogTrack("arrow_distract")

    # reset the display to black
    vt.clear("black")

    # create a PresentationClock object
    # for timing
    clk = PresentationClock()

    vt.updateScreen(clk)


    ##################
    # Testing condition counter balance keys
    subjectID = int(sys.argv[sys.argv.index('-s') + 1])

    keychoice = subjectID % 2
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

    print keychoice

    # Counterbalance test type order within each group of 3 lists
    # Each group of 3 has 2 associative and 1 item test
    # Pattern determined by subject_id % 3
    test_patterns = [
        ['assoc', 'assoc', 'item'],  # Pattern 0: Item in position 3
        ['assoc', 'item', 'assoc'],  # Pattern 1: Item in position 2
        ['item', 'assoc', 'assoc'],  # Pattern 2: Item in position 1
    ]
    test_pattern = test_patterns[subjectID % 3]
    print "Test pattern: %s (subject %d %% 3 = %d)" % (str(test_pattern), subjectID, subjectID % 3)

    def get_test_type(list_num):
        """Get the test type for a given list number (1-indexed, excluding practice)."""
        position_in_group = (list_num - 1) % 3
        return test_pattern[position_in_group]


######################################
## Build Pools
if 1 == 1:  # if statement to help sort the code into blocks
    log = LogTrack("session")  # used for logging all useful data
    #probe_disp_pool = TextPool2("raw_pools/nouns.txt", .1, (0, 0, 0))  # get all high freq words
    #probe_disp_pool_id = TextPool2("raw_pools/nouns.txt", .1, (0, 0, 0))  # get ids from here
    probe_disp_pool = TextPool2("raw_pools/filtered_words.txt", .1, (0, 0, 0))
    probe_disp_pool_id = TextPool2("raw_pools/filtered_words.txt", .1, (0, 0, 0))

    random.shuffle(probe_disp_pool)

    # okay, probe is built!

    list_count = 1


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
For example, for the word pair CAT-DOG, you could
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
You will now see arrows pointing left <- or right ->

Press the LEFT ARROW key when you see <-
Press the RIGHT ARROW key when you see ->

Respond as quickly as you can

Press ENTER to continue"""

INSTRUCT_RECOGNITION_ASSOC = """
Now you will see pairs of words based on pairs you just learned

If the test pair is the same as you learned, press corresponding key to INTACT
If the test pair words come from different pairs, press corresponding key to RECOMBINED

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


#################################
# Paired association learning
#################################
if 1 == 1:
    ########################
    # set the instructions
    print "=== STARTING MAIN LOOP ==="
    print "Will run %d lists total (%d practice + %d experimental)" % (config.NLISTS + config.RUN_PRACTICE, config.RUN_PRACTICE, config.NLISTS)

    while list_count <= (config.NLISTS + config.RUN_PRACTICE):
        print "\n=== LIST %d of %d ===" % (list_count, config.NLISTS + config.RUN_PRACTICE)
        log.logMessage('%s\t%d' % ('LIST', list_count), clk)

        # Determine number of pairs for this list
        if list_count <= config.RUN_PRACTICE:
            num_pairs = config.NPAIRS_PRACTICE
        else:
            num_pairs = config.NPAIRS

        if list_count <= config.RUN_PRACTICE:
            instructions_text = INSTRUCT_PRACTICE
            title = "Get ready for the Practice Round!"
            print "  -> PRACTICE list (list_count=%d <= RUN_PRACTICE=%d)" % (list_count, config.RUN_PRACTICE)
        elif list_count == (1 + config.RUN_PRACTICE):
            instructions_text = INSTRUCT_ROUND1_ARROW
            title = "Get ready for Round 1 of " + str(config.NLISTS) + "!"
            print "  -> ROUND 1 (list_count=%d == 1+RUN_PRACTICE=%d)" % (list_count, 1 + config.RUN_PRACTICE)
        elif list_count > (1 + config.RUN_PRACTICE):
            instructions_text = INSTRUCT_ROUNDN_ARROW
            title = "Get ready for Round " + str(list_count - config.RUN_PRACTICE) + " of " + str(config.NLISTS) + "!"
            print "  -> ROUND %d (list_count=%d > 1+RUN_PRACTICE=%d)" % (list_count - config.RUN_PRACTICE, list_count, 1 + config.RUN_PRACTICE)

        print "  -> num_pairs=%d, title='%s'" % (num_pairs, title)

        #####################################
        # show the experiment instructions
        instruct(instructions_text, clk=clk)

        # reset the display to black
        vt.clear("black")

        stim = Text(title)

        # create a ButtonChooser object
        # to watch for specific keys
        # Hidden Instruction: Press K to skip to next pair
        bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))

        ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

        #####################
        ## Study phase - sequential word presentation
        if 1 == 1:
            # Track all studied words and pairs for test phase
            studied_words = []  # All words presented
            studied_pairs = []  # All pairs for associative test

            pair_count = 1

            # Present words sequentially: W1, W2 (pair 1), W3, W4 (pair 2), etc.
            while pair_count <= num_pairs:
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

                ####Set jittered IPI for after second word
                IPIvalue = range(config.IPI_lower, (config.IPI_upper + 1))
                random.shuffle(IPIvalue)
                IPI = IPIvalue.pop(0)

                # Clear screen before presenting first word
                vt.clear("black")
                vt.updateScreen(clk)

                # Present first word (PRES_TIME ms)
                stim = Text(probe1.name, font=Font("resources/courbd.ttf"))
                bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
                ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

                # 0ms gap (immediately clear and show next word)
                vt.clear("black")
                vt.updateScreen(clk)

                # Present second word (PRES_TIME ms)
                stim = Text(probe2.name, font=Font("resources/courbd.ttf"))
                bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
                ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

                # Show fixation cross during jittered IPI
                vt.clear("black")
                fixation = Text("+", font=Font("resources/courbd.ttf"), size=0.15)
                vt.showProportional(fixation, 0.5, 0.49)
                vt.updateScreen(clk)
                clk.delay(IPI)

                # Log this pair presentation
                log.logMessage('%s\t%d' % (str(list_count) + '\t' + str(pair_count) + '\t' + probe1.name + '\t' + str(word1_id) + '\t' + probe2.name + '\t' + str(word2_id), IPI), clk)
                stimlog.logMessage('%s\t%d' % (str(list_count) + '\t' + str(pair_count) + '\t' + str(word1_id) + '\t' + str(word2_id), IPI), clk)

                pair_count += 1


        ####################
        ## Arrow Distractor Task
        if config.NDIST > 0:
            arrow_distract.logMessage("START", clk)

            if list_count == 1 and config.RUN_PRACTICE > 0:
                # Show arrow task instructions
                instruct(INSTRUCT_ARROW_TASK, clk=clk)

            for arrow_trial in range(config.NDIST):
                # Randomly choose left or right arrow
                is_left = random.choice([True, False])
                # Use ASCII arrows for PyEPL2 compatibility
                arrow_char = "<-" if is_left else "->"
                correct_key = "LEFT" if is_left else "RIGHT"

                # Clear screen
                vt.clear("black")

                # Show arrow (centered)
                arrow_text = Text(arrow_char, font=Font("resources/courbd.ttf"), size=0.15)
                vt.showProportional(arrow_text, 0.5, 0.45)

                # Labels
                left_arrowLabel = Text("<- [left arrow key]", font=Font("resources/courbd.ttf"), size=0.05)
                right_arrowLabel = Text("-> [right arrow key]", font=Font("resources/courbd.ttf"), size=0.05)
                vt.showProportional(left_arrowLabel, 0.20, 0.90)
                vt.showProportional(right_arrowLabel, 0.80, 0.90)
                pres_time = vt.updateScreen(clk)

                # Create button chooser for arrow responses (arrow keys)
                arrow_bc = ButtonChooser(Key("LEFT"), Key("RIGHT"))

                # Wait for response with timeout
                button, bc_time = arrow_bc.waitWithTime(None, config.D_RESP_TIME, clk)

                if button is not None:
                    user_response = button.name
                    # Show response arrow below prompt
                    response_arrow = "<-" if user_response == "LEFT" else "->"
                    response_text = Text(response_arrow, font=Font("resources/courbd.ttf"), size=0.15)
                    vt.showProportional(response_text, 0.5, 0.60)
                    vt.updateScreen(clk)

                    # Wait remaining time so each trial has consistent duration
                    remaining = config.D_RESP_TIME - (bc_time[0] - pres_time[0])
                    if remaining > 0:
                        clk.delay(remaining)
                else:
                    user_response = None
                    # Timeout - already waited full D_RESP_TIME

                # Score response
                if user_response is not None:
                    is_correct = (user_response == correct_key)
                    correct_str = "correct" if is_correct else "incorrect"
                else:
                    is_correct = False
                    correct_str = "no response"

                print "[ARROW] Trial %d/%d: %s | Response: %s | %s" % (arrow_trial + 1, config.NDIST, arrow_char, user_response if user_response else 'none', correct_str)

                # Log arrow trial
                arrow_distract.logMessage("ARROW\t%d\t%s\t%s\t%s\t%d" % (arrow_trial + 1, arrow_char, correct_key, user_response if user_response else 'NONE', 1 if is_correct else 0), clk)

                # Blank screen between trials
                vt.clear("black")
                vt.updateScreen(clk)
                clk.delay(config.D_BLANK_TIME)

            # Reset display
            vt.clear("black")
            vt.updateScreen(clk)
            clk.delay(500)  # Brief pause after distractor


        ####################
        ## Test phase - Pure List Recognition (Assoc OR Item)
        if 1 == 1:
            # Determine test type for this list
            if list_count <= config.RUN_PRACTICE - 1:
                # Practice 1 uses associative test
                current_test_type = 'assoc'
            elif list_count <= config.RUN_PRACTICE:
                # Practice 2 uses item test
                current_test_type = 'item'
            else:
                current_test_type = get_test_type(list_count - config.RUN_PRACTICE)

            print "Test type for list %d: %s" % (list_count, current_test_type)

            # Show appropriate instruction
            if current_test_type == 'assoc':
                instruct(INSTRUCT_RECOGNITION_ASSOC, clk=clk)
            else:
                instruct(INSTRUCT_RECOGNITION_ITEM, clk=clk)

            vt.clear("black")

            ############################
            ## Create test trials - Pure Lists
            # Only create trials for the current test type
            test_trials = []

            if current_test_type == 'assoc':
                # Associative Recognition: half intact, half recombined
                pair_indices = range(len(studied_pairs))
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

                print "Test trials: %d associative" % len(test_trials)

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

                print "Test trials: %d item recognition (%d old, %d new)" % (len(test_trials), n_old, n_old)

            # Shuffle all test trials
            random.shuffle(test_trials)

            vt.clear("black")
            vt.updateScreen(clk)
            clk.delay(500)  # Brief pause before test

            ############################
            ## Present test trials
            test_trial_count = 1

            for trial in test_trials:
                vt.clear("black")
                vt.updateScreen(clk)

                if trial['type'] == 'item':
                    # Item Recognition: Show single word
                    stim = Text(trial['word'], font=Font("resources/courbd.ttf"))
                    do_pres = vt.showProportional(stim, 0.5, 0.5)
                    # Labels: OLD (Z) vs NEW (/)
                    leftinstruct_print = vt.showProportional(Text(inst_item_left + " [z]", color="darkgrey", size=0.05), 0.20, 0.90)
                    rightinstruct_print = vt.showProportional(Text(inst_item_right + " [/]", color="darkgrey", size=0.05), 0.80, 0.90)

                    stim = Text('')
                    bc = ButtonChooser(Key(config.keyLeft), Key(config.keyRight))
                    pres_time, b, bc_time = stim.present(clk=clk, duration=config.C_RESP_TIME, bc=bc)
                    vt.updateScreen(clk)

                    rt = bc_time[0] - pres_time[0]
                    # Find response based on counterbalancing
                    if (b == None):
                        response = -1
                    else:
                        if keychoice == 0:
                            # Left=OLD(1), Right=NEW(0)
                            if (b.name == config.keyLeft):
                                response = 1  # OLD
                            elif (b.name == config.keyRight):
                                response = 0  # NEW
                        else:
                            # Left=NEW(0), Right=OLD(1)
                            if (b.name == config.keyLeft):
                                response = 0  # NEW
                            elif (b.name == config.keyRight):
                                response = 1  # OLD

                    # Score: correct if response matches target
                    recog_acc = 1 if response == trial['target'] else 0

                    # Log item trial
                    log.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tITEM\t' + trial['word'] + '\t' + str(trial['word_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)
                    recoglog.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tITEM\t' + str(trial['word_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)

                else:  # trial['type'] == 'assoc'
                    # Associative Recognition: Show two words
                    stim = Text(trial['word1'] + "  " + trial['word2'], font=Font("resources/courbd.ttf"))
                    do_pres = vt.showProportional(stim, 0.5, 0.5)
                    # Labels: INTACT (Z) vs RECOMBINED (/)
                    leftinstruct_print = vt.showProportional(Text(inst_assoc_left + " [z]", color="darkgrey", size=0.05), 0.20, 0.90)
                    rightinstruct_print = vt.showProportional(Text(inst_assoc_right + " [/]", color="darkgrey", size=0.05), 0.80, 0.90)

                    stim = Text('')
                    bc = ButtonChooser(Key(config.keyLeft), Key(config.keyRight))
                    pres_time, b, bc_time = stim.present(clk=clk, duration=config.C_RESP_TIME, bc=bc)
                    vt.updateScreen(clk)

                    rt = bc_time[0] - pres_time[0]
                    # Find response based on counterbalancing
                    if (b == None):
                        response = -1
                    else:
                        if keychoice == 0:
                            # Left=INTACT(1), Right=RECOMBINED(0)
                            if (b.name == config.keyLeft):
                                response = 1  # INTACT
                            elif (b.name == config.keyRight):
                                response = 0  # RECOMBINED
                        else:
                            # Left=RECOMBINED(0), Right=INTACT(1)
                            if (b.name == config.keyLeft):
                                response = 0  # RECOMBINED
                            elif (b.name == config.keyRight):
                                response = 1  # INTACT

                    # Score: correct if response matches target
                    recog_acc = 1 if response == trial['target'] else 0

                    # Log associative trial
                    log.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tASSOC\t' + trial['word1'] + '\t' + str(trial['word1_id']) + '\t' + trial['word2'] + '\t' + str(trial['word2_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)
                    recoglog.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tASSOC\t' + str(trial['word1_id']) + '\t' + str(trial['word2_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)

                vt.clear("black")
                vt.updateScreen(clk)
                clk.delay(config.C_BLANK_TIME)

                test_trial_count += 1

        list_count += 1


## All done!
if 1 == 1:  # if statement to help sort the code into blocks
    clk.wait()

    # reset the display to black
    vt.clear("black")

    ## DONE!!

    # show completion message
    completion_text = """
Experiment Complete!

Thank you for participating.

Press ENTER to continue"""

    instruct(completion_text, clk=clk)

    # reset the display to black
    vt.clear("black")

    # provide the final message
    stim = Text("Please get the experimenter \n to complete this session.")

    # create a ButtonChooser object
    # to watch for specific keys
    # Hidden Instruction: Press K to skip
    bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))

    ts, b, rt = stim.present(clk=clk, duration=1800000, bc=bc)
