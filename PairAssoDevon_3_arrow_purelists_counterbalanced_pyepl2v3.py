# pylint: skip-file
# type: ignore
#########################################
# Paired Associate Recognition EEG Experiment - PyEPL2 Version (Counterbalanced)
#
# Adapted from PairAssoDevon_3_arrow_purelists_counterbalanced.py (PyEPL3) to PyEPL2.
#
# Sequential word presentation with item and associative recognition tests.
# Uses arrow distractor task. Tests are counterbalanced within triplets.
#
# USAGE:
#   python PairAssoDevon_3_arrow_purelists_counterbalanced_pyepl2.py -s <subject_id>
#
# EMERGENCY EXIT:
#   Press ESCAPE + F1 simultaneously at any time to immediately end the experiment
#   This will exit without saving incomplete trial data
#
# CONFIG: Requires config.py in experiment directory
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

    # EMERGENCY EXIT: Press ESCAPE + F1 simultaneously to immediately end the experiment
    # This works at any stage and will exit without saving incomplete data
    # Default PyEPL break key combination
    exp.setBreak()

    # Alternative: To use ESCAPE key alone as emergency exit, uncomment the line below:
    # exp.setBreak(Key('ESCAPE'))

    # get the subject configuration
    # Note: Config is loaded from config.py in the experiment directory
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

    print "Key choice:", keychoice

    #########################################
    # Font size variables
    #########################################
    WORD_SIZE = 0.1             	# Size for study words
    ARROW_STIM_SIZE = 0.15      	# Size for arrow stimuli (<- and ->)
    ARROW_LABEL_SIZE = 0.04    		# Size for arrow key instruction labels (reduced)
    RECOG_LABEL_SIZE = 0.03     	# Size for recognition test instruction labels
    RECOG_WORD_SIZE = 0.08      	# Size for words during recognition test
    FIXATION_SIZE = 0.15        	# Size for fixation cross
    INSTRUCT_SIZE = 0.045      		# Size for instruction screens (reduced)
    INSTRUCT_TEST_SIZE = 0.027		# Size for instruction screens for test instructions
    INSTRUCT_ARROW_SIZE = 0.045  	# Size for arrow task instructions
    PRACTICE_LABEL_SIZE = 0.05  	# Size for PRACTICE label

    # Helper function to show practice label
    def show_practice_label():
        """Show PRACTICE label in top left corner"""
        practice_text = Text("PRACTICE", font=Font("resources/courbd.ttf"), size=PRACTICE_LABEL_SIZE, color=(255, 255, 255))
        vt.showProportional(practice_text, 0.10, 0.05)

    # Counterbalance test type order within each group of 3 lists
    # Each group of 3 has 2 associative and 1 item test
    test_patterns = [
        ['assoc', 'assoc', 'item'],  # Pattern 0: Item in position 3
        ['assoc', 'item', 'assoc'],  # Pattern 1: Item in position 2
        ['item', 'assoc', 'assoc'],  # Pattern 2: Item in position 1
    ]


######################################
## Build Pools
if 1 == 1:  # if statement to help sort the code into blocks
    log = LogTrack("session")  # used for logging all useful data
    probe_disp_pool = TextPool2("raw_pools/filtered_words.txt", .1, (0, 0, 0))
    probe_disp_pool_id = TextPool2("raw_pools/filtered_words.txt", .1, (0, 0, 0))

    random.shuffle(probe_disp_pool)


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
\n
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
# Optional Practice Lists
#################################
if config.RUN_PRACTICE > 0:
    ### Practice 1 (Associative) ###
    log.logMessage('LIST\tP1', clk)
    instructions_text = INSTRUCT_PRACTICE
    title = "Get ready for the Practice Round!"
    num_pairs = config.NPAIRS_PRACTICE

    print "\n=== LIST P1: Showing instructions ==="
    instruct(instructions_text, clk=clk, size=INSTRUCT_SIZE)

    # reset the display to black
    vt.clear("black")
    stim = Text(title)
    bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
    ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

    ### Study Phase - Sequential word presentation ###
    studied_words = []  # All words presented
    studied_pairs = []  # All pairs for associative test
    pair_count = 1

    print "\n=== STARTING STUDY PHASE: %d pairs ===" % num_pairs

    while pair_count <= num_pairs:
        print "\n--- Pair %d/%d ---" % (pair_count, num_pairs)

        # Get two words for this pair
        probe1 = probe_disp_pool.pop(0)
        probe2 = probe_disp_pool.pop(0)

        # Get word IDs for logging
        word1_id = probe_disp_pool_id.isInPool(name=probe1.name) + 1
        word2_id = probe_disp_pool_id.isInPool(name=probe2.name) + 1

        print "  Word 1: %s (ID: %d)" % (probe1.name, word1_id)
        print "  Word 2: %s (ID: %d)" % (probe2.name, word2_id)

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
        IPIvalue = range(config.IPI_lower, (config.IPI_upper + 1))
        random.shuffle(IPIvalue)
        IPI = IPIvalue.pop(0)

        # Clear screen before presenting first word
        vt.clear("black")
        show_practice_label()
        vt.updateScreen(clk)

        # Present first word
        stim = Text(probe1.name, font=Font("resources/courbd.ttf"), size=WORD_SIZE)
        bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
        ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

        # 0ms gap (immediately clear and show next word)
        vt.clear("black")
        show_practice_label()
        vt.updateScreen(clk)

        # Present second word
        stim = Text(probe2.name, font=Font("resources/courbd.ttf"), size=WORD_SIZE)
        bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
        ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

        # Show fixation cross during jittered IPI
        vt.clear("black")
        fixation = Text("+", font=Font("resources/courbd.ttf"), size=FIXATION_SIZE)
        vt.showProportional(fixation, 0.5, 0.49)
        show_practice_label()
        vt.updateScreen(clk)
        clk.delay(IPI)
        clk.wait()

        # Log this pair presentation
        log.logMessage('%s\t%d' % ('P1' + '\t' + str(pair_count) + '\t' + probe1.name + '\t' + str(word1_id) + '\t' + probe2.name + '\t' + str(word2_id), IPI), clk)
        stimlog.logMessage('%s\t%d' % ('P1' + '\t' + str(pair_count) + '\t' + str(word1_id) + '\t' + str(word2_id), IPI), clk)

        pair_count += 1

    print "\n=== STUDY PHASE COMPLETE ===\n"

    ### Distractor Task - Arrow Response ###
    arrow_distract.logMessage("START", clk)

    if config.NDIST > 0:
        vt.clear("black")
        vt.updateScreen(clk)
        instruct(INSTRUCT_ARROW_TASK, clk=clk, size=INSTRUCT_ARROW_SIZE)
        left_arrowLabel = Text("<- [left arrow key]", font=Font("resources/courbd.ttf"), size=ARROW_LABEL_SIZE)
        right_arrowLabel = Text("-> [right arrow key]", font=Font("resources/courbd.ttf"), size=ARROW_LABEL_SIZE)
        print "\n=== STARTING ARROW DISTRACTOR: %d trials ===" % config.NDIST

        for arrow_trial in range(config.NDIST):
            # Randomly choose left or right arrow
            is_left = random.choice([True, False])
            arrow_char = "<-" if is_left else "->"
            correct_key = "LEFT" if is_left else "RIGHT"

            # Clear screen
            vt.clear("black")

            # Show arrow (centered)
            arrow_text = Text(arrow_char, font=Font("resources/courbd.ttf"), size=ARROW_STIM_SIZE)
            vt.showProportional(arrow_text, 0.5, 0.45)

            # Labels
            vt.showProportional(left_arrowLabel, 0.20, 0.90)
            vt.showProportional(right_arrowLabel, 0.80, 0.90)
            show_practice_label()
            pres_time = vt.updateScreen(clk)

            # Create button chooser for arrow responses
            arrow_bc = ButtonChooser(Key("LEFT"), Key("RIGHT"))

            # Wait for response with timeout
            button, bc_time = arrow_bc.waitWithTime(None, config.D_RESP_TIME, clk)

            if button is not None:
                user_response = button.name
                # Show response arrow below prompt (keep all original elements on screen)
                response_arrow = "<-" if user_response == "LEFT" else "->"

                # Redraw original arrow stimulus
                vt.showProportional(arrow_text, 0.5, 0.45)
                # Show response arrow below
                response_text = Text(response_arrow, font=Font("resources/courbd.ttf"), size=ARROW_STIM_SIZE)
                vt.showProportional(response_text, 0.5, 0.60)
                # Redraw instruction labels
                vt.showProportional(left_arrowLabel, 0.20, 0.90)
                vt.showProportional(right_arrowLabel, 0.80, 0.90)
                show_practice_label()
                vt.updateScreen(clk)

                # Wait remaining time
                remaining = config.D_RESP_TIME - (bc_time[0] - pres_time[0])
                if remaining > 0:
                    clk.delay(remaining)
            else:
                user_response = None

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
            show_practice_label()
            vt.updateScreen(clk)
            clk.delay(config.D_BLANK_TIME)

        print "=== ARROW DISTRACTOR COMPLETE ===\n"

        # Reset display
        vt.clear("black")
        vt.updateScreen(clk)
        clk.delay(500)

    ### Test Phase - Pure List Recognition (Assoc) ###
    instruct(INSTRUCT_RECOGNITION_ASSOC, clk=clk, size=INSTRUCT_TEST_SIZE)

    # Create test trials - Pure Associative List
    test_trials = []

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

    # Shuffle all test trials
    random.shuffle(test_trials)

    vt.clear("black")
    show_practice_label()
    vt.updateScreen(clk)
    clk.delay(500)

    ### Present test trials ###
    test_trial_count = 1

    for trial in test_trials:
        vt.clear("black")
        show_practice_label()
        vt.updateScreen(clk)

        # Associative Recognition: Show two words
        stim = Text(trial['word1'] + "  " + trial['word2'], font=Font("resources/courbd.ttf"), size=RECOG_WORD_SIZE)
        do_pres = vt.showProportional(stim, 0.5, 0.5)
        # Labels
        leftinstruct_print = vt.showProportional(Text(inst_assoc_left + " [z]", color="darkgrey", size=RECOG_LABEL_SIZE), 0.20, 0.90)
        rightinstruct_print = vt.showProportional(Text(inst_assoc_right + " [/]", color="darkgrey", size=RECOG_LABEL_SIZE), 0.80, 0.90)

        stim = Text('')
        bc = ButtonChooser(Key(config.keyLeft), Key(config.keyRight))
        pres_time, b, bc_time = stim.present(clk=clk, duration=config.C_RESP_TIME, bc=bc)
        show_practice_label()
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

        # Score
        recog_acc = 1 if response == trial['target'] else 0

        # Log
        log.logMessage('%s\t%d' % ('P1' + '\t' + str(test_trial_count) + '\tASSOC\t' + trial['word1'] + '\t' + str(trial['word1_id']) + '\t' + trial['word2'] + '\t' + str(trial['word2_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)
        recoglog.logMessage('%s\t%d' % ('P1' + '\t' + str(test_trial_count) + '\tASSOC\t' + str(trial['word1_id']) + '\t' + str(trial['word2_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)

        vt.clear("black")
        show_practice_label()
        vt.updateScreen(clk)
        clk.delay(config.C_BLANK_TIME)

        test_trial_count += 1

    ### Practice 2 (Item) ###
    log.logMessage('LIST\tP2', clk)
    instructions_text = INSTRUCT_PRACTICE
    title = "Get ready for the Practice Round!"
    num_pairs = config.NPAIRS_PRACTICE

    print "\n=== LIST P2: Showing instructions ==="
    vt.clear("black")
    vt.updateScreen(clk)
    instruct(instructions_text, clk=clk, size=INSTRUCT_SIZE)

    # reset the display to black
    vt.clear("black")
    stim = Text(title)
    bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
    ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

    ### Study Phase - Sequential word presentation ###
    studied_words = []  # All words presented
    studied_pairs = []  # All pairs for associative test
    pair_count = 1

    print "\n=== STARTING STUDY PHASE: %d pairs ===" % num_pairs

    while pair_count <= num_pairs:
        print "\n--- Pair %d/%d ---" % (pair_count, num_pairs)

        # Get two words for this pair
        probe1 = probe_disp_pool.pop(0)
        probe2 = probe_disp_pool.pop(0)

        # Get word IDs for logging
        word1_id = probe_disp_pool_id.isInPool(name=probe1.name) + 1
        word2_id = probe_disp_pool_id.isInPool(name=probe2.name) + 1

        print "  Word 1: %s (ID: %d)" % (probe1.name, word1_id)
        print "  Word 2: %s (ID: %d)" % (probe2.name, word2_id)

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
        IPIvalue = range(config.IPI_lower, (config.IPI_upper + 1))
        random.shuffle(IPIvalue)
        IPI = IPIvalue.pop(0)

        # Clear screen before presenting first word
        vt.clear("black")
        show_practice_label()
        vt.updateScreen(clk)

        # Present first word
        stim = Text(probe1.name, font=Font("resources/courbd.ttf"), size=WORD_SIZE)
        bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
        ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

        # 0ms gap
        vt.clear("black")
        show_practice_label()
        vt.updateScreen(clk)

        # Present second word
        stim = Text(probe2.name, font=Font("resources/courbd.ttf"), size=WORD_SIZE)
        bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
        ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

        # Show fixation cross during jittered IPI
        vt.clear("black")
        fixation = Text("+", font=Font("resources/courbd.ttf"), size=FIXATION_SIZE)
        vt.showProportional(fixation, 0.5, 0.49)
        show_practice_label()
        vt.updateScreen(clk)
        clk.delay(IPI)
        clk.wait()

        # Log this pair presentation
        log.logMessage('%s\t%d' % ('P2' + '\t' + str(pair_count) + '\t' + probe1.name + '\t' + str(word1_id) + '\t' + probe2.name + '\t' + str(word2_id), IPI), clk)
        stimlog.logMessage('%s\t%d' % ('P2' + '\t' + str(pair_count) + '\t' + str(word1_id) + '\t' + str(word2_id), IPI), clk)

        pair_count += 1

    print "\n=== STUDY PHASE COMPLETE ===\n"

    ### Distractor Task - Arrow Response ###
    arrow_distract.logMessage("START", clk)

    if config.NDIST > 0:
        vt.clear("black")
        vt.updateScreen(clk)
        instruct(INSTRUCT_ARROW_TASK, clk=clk, size=INSTRUCT_ARROW_SIZE)
        left_arrowLabel = Text("<- [left arrow key]", font=Font("resources/courbd.ttf"), size=ARROW_LABEL_SIZE)
        right_arrowLabel = Text("-> [right arrow key]", font=Font("resources/courbd.ttf"), size=ARROW_LABEL_SIZE)
        print "\n=== STARTING ARROW DISTRACTOR: %d trials ===" % config.NDIST

        for arrow_trial in range(config.NDIST):
            # Randomly choose left or right arrow
            is_left = random.choice([True, False])
            arrow_char = "<-" if is_left else "->"
            correct_key = "LEFT" if is_left else "RIGHT"

            # Clear screen
            vt.clear("black")

            # Show arrow (centered)
            arrow_text = Text(arrow_char, font=Font("resources/courbd.ttf"), size=ARROW_STIM_SIZE)
            vt.showProportional(arrow_text, 0.5, 0.45)

            # Labels
            vt.showProportional(left_arrowLabel, 0.20, 0.90)
            vt.showProportional(right_arrowLabel, 0.80, 0.90)
            show_practice_label()
            pres_time = vt.updateScreen(clk)

            # Create button chooser for arrow responses
            arrow_bc = ButtonChooser(Key("LEFT"), Key("RIGHT"))

            # Wait for response with timeout
            button, bc_time = arrow_bc.waitWithTime(None, config.D_RESP_TIME, clk)

            if button is not None:
                user_response = button.name
                # Show response arrow below prompt (keep all original elements on screen)
                response_arrow = "<-" if user_response == "LEFT" else "->"

                # Redraw original arrow stimulus
                vt.showProportional(arrow_text, 0.5, 0.45)
                # Show response arrow below
                response_text = Text(response_arrow, font=Font("resources/courbd.ttf"), size=ARROW_STIM_SIZE)
                vt.showProportional(response_text, 0.5, 0.60)
                # Redraw instruction labels
                vt.showProportional(left_arrowLabel, 0.20, 0.90)
                vt.showProportional(right_arrowLabel, 0.80, 0.90)
                show_practice_label()
                vt.updateScreen(clk)

                # Wait remaining time
                remaining = config.D_RESP_TIME - (bc_time[0] - pres_time[0])
                if remaining > 0:
                    clk.delay(remaining)
            else:
                user_response = None

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
            show_practice_label()
            vt.updateScreen(clk)
            clk.delay(config.D_BLANK_TIME)

        print "=== ARROW DISTRACTOR COMPLETE ===\n"

        vt.clear("black")
        vt.updateScreen(clk)
        clk.delay(500)

    ### Test Phase - Item Recognition ###
    instruct(INSTRUCT_RECOGNITION_ITEM, clk=clk, size=INSTRUCT_TEST_SIZE)

    # Build OLD items (all studied words)
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
    print "Item test trials: %d (%d old, %d new)" % (len(item_test_trials), n_old, n_old)

    vt.clear("black")
    show_practice_label()
    vt.updateScreen(clk)
    clk.delay(500)

    # Present item test trials
    test_trial_count = 1
    for trial in item_test_trials:
        vt.clear("black")
        show_practice_label()
        vt.updateScreen(clk)

        stim = Text(trial['word'], font=Font("resources/courbd.ttf"), size=RECOG_WORD_SIZE)
        do_pres = vt.showProportional(stim, 0.5, 0.5)
        leftinstruct_print = vt.showProportional(Text(inst_item_left + " [z]", color="darkgrey", size=RECOG_LABEL_SIZE), 0.20, 0.90)
        rightinstruct_print = vt.showProportional(Text(inst_item_right + " [/]", color="darkgrey", size=RECOG_LABEL_SIZE), 0.80, 0.90)

        stim = Text('')
        bc = ButtonChooser(Key(config.keyLeft), Key(config.keyRight))
        pres_time, b, bc_time = stim.present(clk=clk, duration=config.C_RESP_TIME, bc=bc)
        show_practice_label()
        vt.updateScreen(clk)

        rt = bc_time[0] - pres_time[0]
        if (b == None):
            response = -1
        else:
            if keychoice == 0:
                response = 1 if b.name == config.keyLeft else 0  # left=OLD
            else:
                response = 0 if b.name == config.keyLeft else 1  # left=NEW

        recog_acc = 1 if response == trial['target'] else 0

        log.logMessage('%s\t%d' % ('P2' + '\t' + str(test_trial_count) + '\tITEM\t' + trial['word'] + '\t' + str(trial['word_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)
        recoglog.logMessage('%s\t%d' % ('P2' + '\t' + str(test_trial_count) + '\tITEM\t' + str(trial['word_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)

        vt.clear("black")
        show_practice_label()
        vt.updateScreen(clk)
        clk.delay(config.C_BLANK_TIME)

        test_trial_count += 1


#################################################
# Actual Task - Lists come in randomized triplets
#################################################

list_count = 1

print "\n=== STARTING MAIN EXPERIMENT ==="
print "Will run %d lists in triplets" % config.NLISTS

while list_count <= config.NLISTS:
    # Select random test pattern for this triplet
    test_pattern_idx = random.randint(0, 2)
    test_pattern = test_patterns[test_pattern_idx]
    print "\n=== TRIPLET starting at list %d, test pattern: %s ===" % (list_count, str(test_pattern))

    #########################################
    # List 1 of triplet
    #########################################
    log.logMessage('LIST\t%d' % list_count, clk)
    instructions_text = INSTRUCT_ROUNDN_ARROW
    title = "Get ready for Round %d of %d!" % (list_count, config.NLISTS)
    num_pairs = config.NPAIRS

    print "\n=== LIST %d: Showing instructions ===" % list_count
    vt.clear("black")
    vt.updateScreen(clk)
    instruct(instructions_text, clk=clk, size=INSTRUCT_SIZE)

    vt.clear("black")
    stim = Text(title)
    bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
    ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

    ### Study Phase ###
    studied_words = []
    studied_pairs = []
    pair_count = 1

    print "\n=== STARTING STUDY PHASE: %d pairs ===" % num_pairs

    while pair_count <= num_pairs:
        probe1 = probe_disp_pool.pop(0)
        probe2 = probe_disp_pool.pop(0)

        word1_id = probe_disp_pool_id.isInPool(name=probe1.name) + 1
        word2_id = probe_disp_pool_id.isInPool(name=probe2.name) + 1

        studied_pairs.append({
            'pair_num': pair_count,
            'word1': probe1.name,
            'word1_id': word1_id,
            'word2': probe2.name,
            'word2_id': word2_id
        })

        studied_words.append({'word': probe1.name, 'word_id': word1_id})
        studied_words.append({'word': probe2.name, 'word_id': word2_id})

        IPIvalue = range(config.IPI_lower, (config.IPI_upper + 1))
        random.shuffle(IPIvalue)
        IPI = IPIvalue.pop(0)

        vt.clear("black")
        vt.updateScreen(clk)

        stim = Text(probe1.name, font=Font("resources/courbd.ttf"), size=WORD_SIZE)
        bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
        ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

        vt.clear("black")
        vt.updateScreen(clk)

        stim = Text(probe2.name, font=Font("resources/courbd.ttf"), size=WORD_SIZE)
        bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
        ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

        vt.clear("black")
        fixation = Text("+", font=Font("resources/courbd.ttf"), size=FIXATION_SIZE)
        vt.showProportional(fixation, 0.5, 0.49)
        vt.updateScreen(clk)
        clk.delay(IPI)
        clk.wait()

        log.logMessage('%s\t%d' % (str(list_count) + '\t' + str(pair_count) + '\t' + probe1.name + '\t' + str(word1_id) + '\t' + probe2.name + '\t' + str(word2_id), IPI), clk)
        stimlog.logMessage('%s\t%d' % (str(list_count) + '\t' + str(pair_count) + '\t' + str(word1_id) + '\t' + str(word2_id), IPI), clk)

        pair_count += 1

    print "\n=== STUDY PHASE COMPLETE ===\n"

    ### Distractor Task ###
    arrow_distract.logMessage("START", clk)

    if config.NDIST > 0:
        print "\n=== STARTING ARROW DISTRACTOR: %d trials ===" % config.NDIST

        for arrow_trial in range(config.NDIST):
            is_left = random.choice([True, False])
            arrow_char = "<-" if is_left else "->"
            correct_key = "LEFT" if is_left else "RIGHT"

            vt.clear("black")
            arrow_text = Text(arrow_char, font=Font("resources/courbd.ttf"), size=ARROW_STIM_SIZE)
            vt.showProportional(arrow_text, 0.5, 0.45)
            left_arrowLabel = Text("<- [left arrow key]", font=Font("resources/courbd.ttf"), size=ARROW_LABEL_SIZE)
            right_arrowLabel = Text("-> [right arrow key]", font=Font("resources/courbd.ttf"), size=ARROW_LABEL_SIZE)
            vt.showProportional(left_arrowLabel, 0.20, 0.90)
            vt.showProportional(right_arrowLabel, 0.80, 0.90)
            pres_time = vt.updateScreen(clk)

            arrow_bc = ButtonChooser(Key("LEFT"), Key("RIGHT"))
            button, bc_time = arrow_bc.waitWithTime(None, config.D_RESP_TIME, clk)

            if button is not None:
                user_response = button.name
                response_arrow = "<-" if user_response == "LEFT" else "->"

                # Redraw original arrow stimulus
                vt.showProportional(arrow_text, 0.5, 0.45)
                # Show response arrow below
                response_text = Text(response_arrow, font=Font("resources/courbd.ttf"), size=ARROW_STIM_SIZE)
                vt.showProportional(response_text, 0.5, 0.60)
                # Redraw instruction labels
                vt.showProportional(left_arrowLabel, 0.20, 0.90)
                vt.showProportional(right_arrowLabel, 0.80, 0.90)
                vt.updateScreen(clk)
                remaining = config.D_RESP_TIME - (bc_time[0] - pres_time[0])
                if remaining > 0:
                    clk.delay(remaining)
            else:
                user_response = None

            if user_response is not None:
                is_correct = (user_response == correct_key)
                correct_str = "correct" if is_correct else "incorrect"
            else:
                is_correct = False
                correct_str = "no response"

            arrow_distract.logMessage("ARROW\t%d\t%s\t%s\t%s\t%d" % (arrow_trial + 1, arrow_char, correct_key, user_response if user_response else 'NONE', 1 if is_correct else 0), clk)

            vt.clear("black")
            vt.updateScreen(clk)
            clk.delay(config.D_BLANK_TIME)

        print "=== ARROW DISTRACTOR COMPLETE ===\n"
        vt.clear("black")
        vt.updateScreen(clk)
        clk.delay(500)

    ### Test Phase ###
    current_test_type = test_pattern[0]
    print "Test type for list %d: %s" % (list_count, current_test_type)

    if current_test_type == 'assoc':
        instruct(INSTRUCT_RECOGNITION_ASSOC, clk=clk, size=INSTRUCT_TEST_SIZE)
    else:
        instruct(INSTRUCT_RECOGNITION_ITEM, clk=clk, size=INSTRUCT_TEST_SIZE)

    test_trials = []

    if current_test_type == 'assoc':
        # Associative Recognition
        pair_indices = range(len(studied_pairs))
        random.shuffle(pair_indices)

        n_intact = len(pair_indices) // 2
        intact_indices = pair_indices[:n_intact]
        recombined_indices = pair_indices[n_intact:]

        for idx in intact_indices:
            pair = studied_pairs[idx]
            test_trials.append({
                'type': 'assoc',
                'word1': pair['word1'],
                'word1_id': pair['word1_id'],
                'word2': pair['word2'],
                'word2_id': pair['word2_id'],
                'target': 1,
                'is_intact': True,
                'pair_num': pair['pair_num']
            })

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
                'target': 0,
                'is_intact': False,
                'pair_num1': pair1['pair_num'],
                'pair_num2': pair2['pair_num']
            })

        print "Test trials: %d associative" % len(test_trials)
    else:
        # Item Recognition
        item_words = []
        for pair in studied_pairs:
            item_words.append({'word': pair['word1'], 'word_id': pair['word1_id']})
            item_words.append({'word': pair['word2'], 'word_id': pair['word2_id']})

        random.shuffle(item_words)
        n_old = len(item_words)

        for word_info in item_words:
            test_trials.append({
                'type': 'item',
                'word': word_info['word'],
                'word_id': word_info['word_id'],
                'target': 1,
                'is_old': True
            })

        for i in range(n_old):
            foil_word = probe_disp_pool.pop(0)
            foil_id = probe_disp_pool_id.isInPool(name=foil_word.name) + 1
            test_trials.append({
                'type': 'item',
                'word': foil_word.name,
                'word_id': foil_id,
                'target': 0,
                'is_old': False
            })

        print "Test trials: %d item recognition (%d old, %d new)" % (len(test_trials), n_old, n_old)

    random.shuffle(test_trials)
    vt.clear("black")
    vt.updateScreen(clk)
    clk.delay(500)

    test_trial_count = 1

    for trial in test_trials:
        vt.clear("black")
        vt.updateScreen(clk)

        if trial['type'] == 'item':
            stim = Text(trial['word'], font=Font("resources/courbd.ttf"), size=RECOG_WORD_SIZE)
            do_pres = vt.showProportional(stim, 0.5, 0.5)
            leftinstruct_print = vt.showProportional(Text(inst_item_left + " [z]", color="darkgrey", size=RECOG_LABEL_SIZE), 0.20, 0.90)
            rightinstruct_print = vt.showProportional(Text(inst_item_right + " [/]", color="darkgrey", size=RECOG_LABEL_SIZE), 0.80, 0.90)

            stim = Text('')
            bc = ButtonChooser(Key(config.keyLeft), Key(config.keyRight))
            pres_time, b, bc_time = stim.present(clk=clk, duration=config.C_RESP_TIME, bc=bc)
            vt.updateScreen(clk)

            rt = bc_time[0] - pres_time[0]
            if (b == None):
                response = -1
            else:
                if keychoice == 0:
                    response = 1 if b.name == config.keyLeft else 0
                else:
                    response = 0 if b.name == config.keyLeft else 1

            recog_acc = 1 if response == trial['target'] else 0

            log.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tITEM\t' + trial['word'] + '\t' + str(trial['word_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)
            recoglog.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tITEM\t' + str(trial['word_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)
        else:
            stim = Text(trial['word1'] + "  " + trial['word2'], font=Font("resources/courbd.ttf"), size=RECOG_WORD_SIZE)
            do_pres = vt.showProportional(stim, 0.5, 0.5)
            leftinstruct_print = vt.showProportional(Text(inst_assoc_left + " [z]", color="darkgrey", size=RECOG_LABEL_SIZE), 0.20, 0.90)
            rightinstruct_print = vt.showProportional(Text(inst_assoc_right + " [/]", color="darkgrey", size=RECOG_LABEL_SIZE), 0.80, 0.90)

            stim = Text('')
            bc = ButtonChooser(Key(config.keyLeft), Key(config.keyRight))
            pres_time, b, bc_time = stim.present(clk=clk, duration=config.C_RESP_TIME, bc=bc)
            vt.updateScreen(clk)

            rt = bc_time[0] - pres_time[0]
            if (b == None):
                response = -1
            else:
                if keychoice == 0:
                    if (b.name == config.keyLeft):
                        response = 1
                    elif (b.name == config.keyRight):
                        response = 0
                else:
                    if (b.name == config.keyLeft):
                        response = 0
                    elif (b.name == config.keyRight):
                        response = 1

            recog_acc = 1 if response == trial['target'] else 0

            log.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tASSOC\t' + trial['word1'] + '\t' + str(trial['word1_id']) + '\t' + trial['word2'] + '\t' + str(trial['word2_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)
            recoglog.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tASSOC\t' + str(trial['word1_id']) + '\t' + str(trial['word2_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)

        vt.clear("black")
        vt.updateScreen(clk)
        clk.delay(config.C_BLANK_TIME)

        test_trial_count += 1

    list_count += 1

    # Check if we should continue (need at least 2 more lists for a full triplet)
    if list_count > config.NLISTS:
        break

    #########################################
    # List 2 of triplet (same pattern as List 1, just uses test_pattern[1])
    #########################################
    log.logMessage('LIST\t%d' % list_count, clk)
    instructions_text = INSTRUCT_ROUNDN_ARROW
    title = "Get ready for Round %d of %d!" % (list_count, config.NLISTS)
    num_pairs = config.NPAIRS

    print "\n=== LIST %d: Showing instructions ===" % list_count
    vt.clear("black")
    vt.updateScreen(clk)
    instruct(instructions_text, clk=clk, size=INSTRUCT_SIZE)

    vt.clear("black")
    stim = Text(title)
    bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
    ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

    ### Study Phase ###
    studied_words = []
    studied_pairs = []
    pair_count = 1

    while pair_count <= num_pairs:
        probe1 = probe_disp_pool.pop(0)
        probe2 = probe_disp_pool.pop(0)

        word1_id = probe_disp_pool_id.isInPool(name=probe1.name) + 1
        word2_id = probe_disp_pool_id.isInPool(name=probe2.name) + 1

        studied_pairs.append({
            'pair_num': pair_count,
            'word1': probe1.name,
            'word1_id': word1_id,
            'word2': probe2.name,
            'word2_id': word2_id
        })

        studied_words.append({'word': probe1.name, 'word_id': word1_id})
        studied_words.append({'word': probe2.name, 'word_id': word2_id})

        IPIvalue = range(config.IPI_lower, (config.IPI_upper + 1))
        random.shuffle(IPIvalue)
        IPI = IPIvalue.pop(0)

        vt.clear("black")
        vt.updateScreen(clk)

        stim = Text(probe1.name, font=Font("resources/courbd.ttf"), size=WORD_SIZE)
        bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
        ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

        vt.clear("black")
        vt.updateScreen(clk)

        stim = Text(probe2.name, font=Font("resources/courbd.ttf"), size=WORD_SIZE)
        bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
        ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

        vt.clear("black")
        fixation = Text("+", font=Font("resources/courbd.ttf"), size=FIXATION_SIZE)
        vt.showProportional(fixation, 0.5, 0.49)
        vt.updateScreen(clk)
        clk.delay(IPI)
        clk.wait()

        log.logMessage('%s\t%d' % (str(list_count) + '\t' + str(pair_count) + '\t' + probe1.name + '\t' + str(word1_id) + '\t' + probe2.name + '\t' + str(word2_id), IPI), clk)
        stimlog.logMessage('%s\t%d' % (str(list_count) + '\t' + str(pair_count) + '\t' + str(word1_id) + '\t' + str(word2_id), IPI), clk)

        pair_count += 1

    ### Distractor Task ###
    arrow_distract.logMessage("START", clk)

    if config.NDIST > 0:
        for arrow_trial in range(config.NDIST):
            is_left = random.choice([True, False])
            arrow_char = "<-" if is_left else "->"
            correct_key = "LEFT" if is_left else "RIGHT"

            vt.clear("black")
            arrow_text = Text(arrow_char, font=Font("resources/courbd.ttf"), size=ARROW_STIM_SIZE)
            vt.showProportional(arrow_text, 0.5, 0.45)
            left_arrowLabel = Text("<- [left arrow key]", font=Font("resources/courbd.ttf"), size=ARROW_LABEL_SIZE)
            right_arrowLabel = Text("-> [right arrow key]", font=Font("resources/courbd.ttf"), size=ARROW_LABEL_SIZE)
            vt.showProportional(left_arrowLabel, 0.20, 0.90)
            vt.showProportional(right_arrowLabel, 0.80, 0.90)
            pres_time = vt.updateScreen(clk)

            arrow_bc = ButtonChooser(Key("LEFT"), Key("RIGHT"))
            button, bc_time = arrow_bc.waitWithTime(None, config.D_RESP_TIME, clk)

            if button is not None:
                user_response = button.name
                response_arrow = "<-" if user_response == "LEFT" else "->"

                # Redraw original arrow stimulus
                vt.showProportional(arrow_text, 0.5, 0.45)
                # Show response arrow below
                response_text = Text(response_arrow, font=Font("resources/courbd.ttf"), size=ARROW_STIM_SIZE)
                vt.showProportional(response_text, 0.5, 0.60)
                # Redraw instruction labels
                vt.showProportional(left_arrowLabel, 0.20, 0.90)
                vt.showProportional(right_arrowLabel, 0.80, 0.90)
                vt.updateScreen(clk)
                remaining = config.D_RESP_TIME - (bc_time[0] - pres_time[0])
                if remaining > 0:
                    clk.delay(remaining)
            else:
                user_response = None

            if user_response is not None:
                is_correct = (user_response == correct_key)
            else:
                is_correct = False

            arrow_distract.logMessage("ARROW\t%d\t%s\t%s\t%s\t%d" % (arrow_trial + 1, arrow_char, correct_key, user_response if user_response else 'NONE', 1 if is_correct else 0), clk)

            vt.clear("black")
            vt.updateScreen(clk)
            clk.delay(config.D_BLANK_TIME)

        vt.clear("black")
        vt.updateScreen(clk)
        clk.delay(500)

    ### Test Phase (uses test_pattern[1]) ###
    current_test_type = test_pattern[1]
    print "Test type for list %d: %s" % (list_count, current_test_type)

    if current_test_type == 'assoc':
        instruct(INSTRUCT_RECOGNITION_ASSOC, clk=clk, size=INSTRUCT_TEST_SIZE)
    else:
        instruct(INSTRUCT_RECOGNITION_ITEM, clk=clk, size=INSTRUCT_TEST_SIZE)

    test_trials = []

    if current_test_type == 'assoc':
        pair_indices = range(len(studied_pairs))
        random.shuffle(pair_indices)

        n_intact = len(pair_indices) // 2
        intact_indices = pair_indices[:n_intact]
        recombined_indices = pair_indices[n_intact:]

        for idx in intact_indices:
            pair = studied_pairs[idx]
            test_trials.append({
                'type': 'assoc',
                'word1': pair['word1'],
                'word1_id': pair['word1_id'],
                'word2': pair['word2'],
                'word2_id': pair['word2_id'],
                'target': 1,
                'is_intact': True,
                'pair_num': pair['pair_num']
            })

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
                'target': 0,
                'is_intact': False,
                'pair_num1': pair1['pair_num'],
                'pair_num2': pair2['pair_num']
            })
    else:
        item_words = []
        for pair in studied_pairs:
            item_words.append({'word': pair['word1'], 'word_id': pair['word1_id']})
            item_words.append({'word': pair['word2'], 'word_id': pair['word2_id']})

        random.shuffle(item_words)
        n_old = len(item_words)

        for word_info in item_words:
            test_trials.append({
                'type': 'item',
                'word': word_info['word'],
                'word_id': word_info['word_id'],
                'target': 1,
                'is_old': True
            })

        for i in range(n_old):
            foil_word = probe_disp_pool.pop(0)
            foil_id = probe_disp_pool_id.isInPool(name=foil_word.name) + 1
            test_trials.append({
                'type': 'item',
                'word': foil_word.name,
                'word_id': foil_id,
                'target': 0,
                'is_old': False
            })

    random.shuffle(test_trials)
    vt.clear("black")
    vt.updateScreen(clk)
    clk.delay(500)

    test_trial_count = 1

    for trial in test_trials:
        vt.clear("black")
        vt.updateScreen(clk)

        if trial['type'] == 'item':
            stim = Text(trial['word'], font=Font("resources/courbd.ttf"), size=RECOG_WORD_SIZE)
            do_pres = vt.showProportional(stim, 0.5, 0.5)
            leftinstruct_print = vt.showProportional(Text(inst_item_left + " [z]", color="darkgrey", size=RECOG_LABEL_SIZE), 0.20, 0.90)
            rightinstruct_print = vt.showProportional(Text(inst_item_right + " [/]", color="darkgrey", size=RECOG_LABEL_SIZE), 0.80, 0.90)

            stim = Text('')
            bc = ButtonChooser(Key(config.keyLeft), Key(config.keyRight))
            pres_time, b, bc_time = stim.present(clk=clk, duration=config.C_RESP_TIME, bc=bc)
            vt.updateScreen(clk)

            rt = bc_time[0] - pres_time[0]
            if (b == None):
                response = -1
            else:
                if keychoice == 0:
                    response = 1 if b.name == config.keyLeft else 0
                else:
                    response = 0 if b.name == config.keyLeft else 1

            recog_acc = 1 if response == trial['target'] else 0

            log.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tITEM\t' + trial['word'] + '\t' + str(trial['word_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)
            recoglog.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tITEM\t' + str(trial['word_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)
        else:
            stim = Text(trial['word1'] + "  " + trial['word2'], font=Font("resources/courbd.ttf"), size=RECOG_WORD_SIZE)
            do_pres = vt.showProportional(stim, 0.5, 0.5)
            leftinstruct_print = vt.showProportional(Text(inst_assoc_left + " [z]", color="darkgrey", size=RECOG_LABEL_SIZE), 0.20, 0.90)
            rightinstruct_print = vt.showProportional(Text(inst_assoc_right + " [/]", color="darkgrey", size=RECOG_LABEL_SIZE), 0.80, 0.90)

            stim = Text('')
            bc = ButtonChooser(Key(config.keyLeft), Key(config.keyRight))
            pres_time, b, bc_time = stim.present(clk=clk, duration=config.C_RESP_TIME, bc=bc)
            vt.updateScreen(clk)

            rt = bc_time[0] - pres_time[0]
            if (b == None):
                response = -1
            else:
                if keychoice == 0:
                    if (b.name == config.keyLeft):
                        response = 1
                    elif (b.name == config.keyRight):
                        response = 0
                else:
                    if (b.name == config.keyLeft):
                        response = 0
                    elif (b.name == config.keyRight):
                        response = 1

            recog_acc = 1 if response == trial['target'] else 0

            log.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tASSOC\t' + trial['word1'] + '\t' + str(trial['word1_id']) + '\t' + trial['word2'] + '\t' + str(trial['word2_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)
            recoglog.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tASSOC\t' + str(trial['word1_id']) + '\t' + str(trial['word2_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)

        vt.clear("black")
        vt.updateScreen(clk)
        clk.delay(config.C_BLANK_TIME)

        test_trial_count += 1

    list_count += 1

    # Check if we need list 3
    if list_count > config.NLISTS:
        break

    #########################################
    # List 3 of triplet
    #########################################
    log.logMessage('LIST\t%d' % list_count, clk)
    instructions_text = INSTRUCT_ROUNDN_ARROW
    title = "Get ready for Round %d of %d!" % (list_count, config.NLISTS)
    num_pairs = config.NPAIRS

    print "\n=== LIST %d: Showing instructions ===" % list_count
    vt.clear("black")
    vt.updateScreen(clk)
    instruct(instructions_text, clk=clk, size=INSTRUCT_SIZE)

    vt.clear("black")
    stim = Text(title)
    bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
    ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

    ### Study Phase ###
    studied_words = []
    studied_pairs = []
    pair_count = 1

    while pair_count <= num_pairs:
        probe1 = probe_disp_pool.pop(0)
        probe2 = probe_disp_pool.pop(0)

        word1_id = probe_disp_pool_id.isInPool(name=probe1.name) + 1
        word2_id = probe_disp_pool_id.isInPool(name=probe2.name) + 1

        studied_pairs.append({
            'pair_num': pair_count,
            'word1': probe1.name,
            'word1_id': word1_id,
            'word2': probe2.name,
            'word2_id': word2_id
        })

        studied_words.append({'word': probe1.name, 'word_id': word1_id})
        studied_words.append({'word': probe2.name, 'word_id': word2_id})

        IPIvalue = range(config.IPI_lower, (config.IPI_upper + 1))
        random.shuffle(IPIvalue)
        IPI = IPIvalue.pop(0)

        vt.clear("black")
        vt.updateScreen(clk)

        stim = Text(probe1.name, font=Font("resources/courbd.ttf"), size=WORD_SIZE)
        bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
        ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

        vt.clear("black")
        vt.updateScreen(clk)

        stim = Text(probe2.name, font=Font("resources/courbd.ttf"), size=WORD_SIZE)
        bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
        ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

        vt.clear("black")
        fixation = Text("+", font=Font("resources/courbd.ttf"), size=FIXATION_SIZE)
        vt.showProportional(fixation, 0.5, 0.49)
        vt.updateScreen(clk)
        clk.delay(IPI)
        clk.wait()

        log.logMessage('%s\t%d' % (str(list_count) + '\t' + str(pair_count) + '\t' + probe1.name + '\t' + str(word1_id) + '\t' + probe2.name + '\t' + str(word2_id), IPI), clk)
        stimlog.logMessage('%s\t%d' % (str(list_count) + '\t' + str(pair_count) + '\t' + str(word1_id) + '\t' + str(word2_id), IPI), clk)

        pair_count += 1

    ### Distractor Task ###
    arrow_distract.logMessage("START", clk)

    if config.NDIST > 0:
        for arrow_trial in range(config.NDIST):
            is_left = random.choice([True, False])
            arrow_char = "<-" if is_left else "->"
            correct_key = "LEFT" if is_left else "RIGHT"

            vt.clear("black")
            arrow_text = Text(arrow_char, font=Font("resources/courbd.ttf"), size=ARROW_STIM_SIZE)
            vt.showProportional(arrow_text, 0.5, 0.45)
            left_arrowLabel = Text("<- [left arrow key]", font=Font("resources/courbd.ttf"), size=ARROW_LABEL_SIZE)
            right_arrowLabel = Text("-> [right arrow key]", font=Font("resources/courbd.ttf"), size=ARROW_LABEL_SIZE)
            vt.showProportional(left_arrowLabel, 0.20, 0.90)
            vt.showProportional(right_arrowLabel, 0.80, 0.90)
            pres_time = vt.updateScreen(clk)

            arrow_bc = ButtonChooser(Key("LEFT"), Key("RIGHT"))
            button, bc_time = arrow_bc.waitWithTime(None, config.D_RESP_TIME, clk)

            if button is not None:
                user_response = button.name
                response_arrow = "<-" if user_response == "LEFT" else "->"

                # Redraw original arrow stimulus
                vt.showProportional(arrow_text, 0.5, 0.45)
                # Show response arrow below
                response_text = Text(response_arrow, font=Font("resources/courbd.ttf"), size=ARROW_STIM_SIZE)
                vt.showProportional(response_text, 0.5, 0.60)
                # Redraw instruction labels
                vt.showProportional(left_arrowLabel, 0.20, 0.90)
                vt.showProportional(right_arrowLabel, 0.80, 0.90)
                vt.updateScreen(clk)
                remaining = config.D_RESP_TIME - (bc_time[0] - pres_time[0])
                if remaining > 0:
                    clk.delay(remaining)
            else:
                user_response = None

            if user_response is not None:
                is_correct = (user_response == correct_key)
            else:
                is_correct = False

            arrow_distract.logMessage("ARROW\t%d\t%s\t%s\t%s\t%d" % (arrow_trial + 1, arrow_char, correct_key, user_response if user_response else 'NONE', 1 if is_correct else 0), clk)

            vt.clear("black")
            vt.updateScreen(clk)
            clk.delay(config.D_BLANK_TIME)

        vt.clear("black")
        vt.updateScreen(clk)
        clk.delay(500)

    ### Test Phase (uses test_pattern[2]) ###
    current_test_type = test_pattern[2]
    print "Test type for list %d: %s" % (list_count, current_test_type)

    if current_test_type == 'assoc':
        instruct(INSTRUCT_RECOGNITION_ASSOC, clk=clk, size=INSTRUCT_TEST_SIZE)
    else:
        instruct(INSTRUCT_RECOGNITION_ITEM, clk=clk, size=INSTRUCT_TEST_SIZE)

    test_trials = []

    if current_test_type == 'assoc':
        pair_indices = range(len(studied_pairs))
        random.shuffle(pair_indices)

        n_intact = len(pair_indices) // 2
        intact_indices = pair_indices[:n_intact]
        recombined_indices = pair_indices[n_intact:]

        for idx in intact_indices:
            pair = studied_pairs[idx]
            test_trials.append({
                'type': 'assoc',
                'word1': pair['word1'],
                'word1_id': pair['word1_id'],
                'word2': pair['word2'],
                'word2_id': pair['word2_id'],
                'target': 1,
                'is_intact': True,
                'pair_num': pair['pair_num']
            })

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
                'target': 0,
                'is_intact': False,
                'pair_num1': pair1['pair_num'],
                'pair_num2': pair2['pair_num']
            })
    else:
        item_words = []
        for pair in studied_pairs:
            item_words.append({'word': pair['word1'], 'word_id': pair['word1_id']})
            item_words.append({'word': pair['word2'], 'word_id': pair['word2_id']})

        random.shuffle(item_words)
        n_old = len(item_words)

        for word_info in item_words:
            test_trials.append({
                'type': 'item',
                'word': word_info['word'],
                'word_id': word_info['word_id'],
                'target': 1,
                'is_old': True
            })

        for i in range(n_old):
            foil_word = probe_disp_pool.pop(0)
            foil_id = probe_disp_pool_id.isInPool(name=foil_word.name) + 1
            test_trials.append({
                'type': 'item',
                'word': foil_word.name,
                'word_id': foil_id,
                'target': 0,
                'is_old': False
            })

    random.shuffle(test_trials)
    vt.clear("black")
    vt.updateScreen(clk)
    clk.delay(500)

    test_trial_count = 1

    for trial in test_trials:
        vt.clear("black")
        vt.updateScreen(clk)

        if trial['type'] == 'item':
            stim = Text(trial['word'], font=Font("resources/courbd.ttf"), size=RECOG_WORD_SIZE)
            do_pres = vt.showProportional(stim, 0.5, 0.5)
            leftinstruct_print = vt.showProportional(Text(inst_item_left + " [z]", color="darkgrey", size=RECOG_LABEL_SIZE), 0.20, 0.90)
            rightinstruct_print = vt.showProportional(Text(inst_item_right + " [/]", color="darkgrey", size=RECOG_LABEL_SIZE), 0.80, 0.90)

            stim = Text('')
            bc = ButtonChooser(Key(config.keyLeft), Key(config.keyRight))
            pres_time, b, bc_time = stim.present(clk=clk, duration=config.C_RESP_TIME, bc=bc)
            vt.updateScreen(clk)

            rt = bc_time[0] - pres_time[0]
            if (b == None):
                response = -1
            else:
                if keychoice == 0:
                    response = 1 if b.name == config.keyLeft else 0
                else:
                    response = 0 if b.name == config.keyLeft else 1

            recog_acc = 1 if response == trial['target'] else 0

            log.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tITEM\t' + trial['word'] + '\t' + str(trial['word_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)
            recoglog.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tITEM\t' + str(trial['word_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)
        else:
            stim = Text(trial['word1'] + "  " + trial['word2'], font=Font("resources/courbd.ttf"), size=RECOG_WORD_SIZE)
            do_pres = vt.showProportional(stim, 0.5, 0.5)
            leftinstruct_print = vt.showProportional(Text(inst_assoc_left + " [z]", color="darkgrey", size=RECOG_LABEL_SIZE), 0.20, 0.90)
            rightinstruct_print = vt.showProportional(Text(inst_assoc_right + " [/]", color="darkgrey", size=RECOG_LABEL_SIZE), 0.80, 0.90)

            stim = Text('')
            bc = ButtonChooser(Key(config.keyLeft), Key(config.keyRight))
            pres_time, b, bc_time = stim.present(clk=clk, duration=config.C_RESP_TIME, bc=bc)
            vt.updateScreen(clk)

            rt = bc_time[0] - pres_time[0]
            if (b == None):
                response = -1
            else:
                if keychoice == 0:
                    if (b.name == config.keyLeft):
                        response = 1
                    elif (b.name == config.keyRight):
                        response = 0
                else:
                    if (b.name == config.keyLeft):
                        response = 0
                    elif (b.name == config.keyRight):
                        response = 1

            recog_acc = 1 if response == trial['target'] else 0

            log.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tASSOC\t' + trial['word1'] + '\t' + str(trial['word1_id']) + '\t' + trial['word2'] + '\t' + str(trial['word2_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)
            recoglog.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tASSOC\t' + str(trial['word1_id']) + '\t' + str(trial['word2_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)

        vt.clear("black")
        vt.updateScreen(clk)
        clk.delay(config.C_BLANK_TIME)

        test_trial_count += 1

    list_count += 1


## All done!
if 1 == 1:
    clk.wait()
    vt.clear("black")

    completion_text = """
Experiment Complete!
\n
Thank you for participating.
\n
Press ENTER to continue"""

    instruct(completion_text, clk=clk, size=INSTRUCT_SIZE)

    vt.clear("black")
    stim = Text("Please get the experimenter \n to complete this session.")
    bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
    ts, b, rt = stim.present(clk=clk, duration=1800000, bc=bc)
