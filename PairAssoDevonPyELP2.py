# pylint: skip-file
# type: ignore
#################################
#Associative Recognition EEG Exp#
#################################

#########################################
#Initialization
if 1 == 1: # if statement to help sort the code into blocks
	import sys, random,time,math#,mathDistract2
	
	# get access to pyepl objects & functions
	from pyepl.locals import *
	
	# define & load required modules
	loadmodules = 'echoBuffer2','TextPool2','mathDistract3'
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
	config = exp.getConfig()
	
	# Create a VideoTrack object for interfacing 
	# with monitor, and a KeyTrack object for
	# interfacing with keyboard
	vt = VideoTrack("video")
	kt = KeyTrack("key")
	EEGs = EEGTrack("eeg")
	

	stimlog = LogTrack("stimlog") # used for scoring-only (is non-human readable)
	recoglog = LogTrack("recoglog")

        #myList = WordList(probe_pool, config, isNoOrder, isNoOrderFinal)
        TIPI_outputfile = "data/" + str(exp.options["subject"]) + "/" + "TIPI_output"
	
	# reset the display to black
	vt.clear("black")
	
	# create a PresentationClock object
	# for timing
	clk = PresentationClock()
	
	vt.updateScreen(clk)


	##################
	#Testing condition counter balance keys
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
	print keychoice
	######################################
	## Build Pools
if 1 == 1: # if statement to help sort the code into blocks
	#list_count = 1
	#disp_count = 0
	log = LogTrack("session") # used for logging all useful data
	probe_disp_pool = TextPool2("raw_pools/filtered_words.txt", .1, (0,0,0)) #get all high freq words
	probe_disp_pool_id = TextPool2("raw_pools/filtered_words.txt", .1, (0,0,0)) # get ids from here
	
	probe_pool = TextPool2("raw_pools/emptypool.txt")

	random.shuffle(probe_disp_pool)
	
	# okay, probe is built!
	
	
	list_count = 1
#################################
#Paired association learning
#################################
if 1 == 1:
	########################
	# set the instructions
	while list_count <= (config.NLISTS + config.RUN_PRACTICE):
		log.logMessage('%s\t%d' % ('LIST',list_count),clk)
		if list_count == config.RUN_PRACTICE:
			# open the instructions file
			instructions = open("instruct/instruct0.txt")
			title = "Get ready for the Practice Round!"
		elif list_count == (1 + config.RUN_PRACTICE):
			# open the instructions file
			instructions = open("instruct/instruct1.txt")
			title = "Get ready for Round 1 of " + str(config.NLISTS) + "!"
		elif list_count > (1 + config.RUN_PRACTICE):
			# open the instructions file
			instructions = open("instruct/instructN.txt")
			title = "Get ready for Round " + str(list_count-config.RUN_PRACTICE) + " of " + str(config.NLISTS) + "!"		
		
		#####################################
		# show the experiment instructions
		instruct(instructions.read(), clk=clk) ## comment out this line to have the program run on it's own (after the practice is complete) -- ideal for testing
	
		# reset the display to black
		vt.clear("black")
		
		stim = Text(title)
		
	
		# create a ButtonChooser object
		# to watch for specific keys
		# Hidden Instruction: Press K to skip to next pair
		bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
	
		ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

		#####################
		## Interactive Imagery Instructions
		# TODO: Insert interactive imagery instructions here

		#####################
		## Study phase - sequential word presentation
		if 1==1:
			# Track all studied words and pairs for test phase
			studied_words = []  # All 32 words presented
			studied_pairs = []  # All 16 pairs for associative test

			word_count = 0
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

				####Set jittered IPI for after second word
				IPIvalue = range(config.IPI_lower, (config.IPI_upper + 1))
				random.shuffle(IPIvalue)
				IPI = IPIvalue.pop(0)

				# Present first word (2000ms)
				stim = Text(probe1.name, font = Font("resources/courbd.ttf"))
				bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
				ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

				# 0ms gap (immediately clear and show next word)
				vt.clear("black")
				vt.updateScreen(clk)

				# Present second word (2000ms)
				stim = Text(probe2.name, font = Font("resources/courbd.ttf"))
				bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))
				ts, b, rt = stim.present(clk=clk, duration=config.PRES_TIME, bc=bc)

				# Clear screen and wait jittered IPI
				vt.clear("black")
				vt.updateScreen(clk)
				clk.delay(IPI)

				# Log this pair presentation
				log.logMessage('%s\t%d' % (str(list_count) + '\t' + str(pair_count) + '\t' + probe1.name + '\t' + str(word1_id) + '\t' + probe2.name + '\t' + str(word2_id), IPI),clk)
				stimlog.logMessage('%s\t%d' % (str(list_count) + '\t' + str(pair_count) + '\t' + str(word1_id) + '\t' + str(word2_id), IPI),clk)

				pair_count += 1

		# Test stimuli will be created in the test phase below




		####################
		## distractor		
		if config.NDIST > 0:
			if list_count == 1 and config.RUN_PRACTICE == 1:
				# open the instructions file
				instructions = open("instruct/distractor.txt")
	
				# show the experiment instructions
				instruct(instructions.read(), clk=clk)
			
			mathDistract2(clk=clk,
							  problemTimeLimit = config.D_RESP_TIME,
							  numVars = 3,
							  maxNum = config.DIST_MAX,
							  minNum = config.DIST_MIN,
							  maxProbs = config.NDIST,
							  minDuration = ( (config.D_RESP_TIME + config.D_BLANK_TIME) * config.NDIST),
							  blanktime = config.D_BLANK_TIME)

			# reset the display to black
			vt.clear("black")
			vt.updateScreen(clk)
		
		####################
		## Test phase - Item + Associative Recognition
		if 1==1:
			if list_count == config.RUN_PRACTICE:
				instructions = open("instruct/recognition_noorder.txt")
				title = "Get ready for the Practice Round!"
				# show the experiment instructions
				instruct(instructions.read(), clk=clk)
				start = clk.get()
			elif list_count > 1:
				title = "Get ready for recognition"

			vt.clear("black")
			stim = Text(title)

			############################
			## Create test trials
			test_trials = []

			# 1. Create 8 Item Recognition trials (4 old, 4 new)
			# Select 4 random old words from studied words (avoid duplicates)
			indices_list = range(len(studied_words))
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
			foil_words = []
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
			# Select 4 random intact pairs from studied pairs
			pair_indices_list = range(len(studied_pairs))
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
			remaining_pairs = [studied_pairs[i] for i in range(len(studied_pairs)) if i not in intact_pair_indices]
			for i in range(4):
				# Get two different pairs and swap their second words
				pair1 = remaining_pairs[i]
				pair2 = remaining_pairs[(i+1) % len(remaining_pairs)]
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
			test_trial_count = 1

			for trial in test_trials:
				vt.clear("black")
				vt.updateScreen(clk)

				if trial['type'] == 'item':
					# Item Recognition: Show single word
					stim = Text(trial['word'], font = Font("resources/courbd.ttf"))
					do_pres = vt.showProportional(stim, 0.5, 0.5)
					# Labels: OLD (Z) vs NEW (/)
					leftinstruct_print = vt.showProportional(Text("OLD", color="darkgrey", size=0.08), 0.20, 0.90)
					rightinstruct_print = vt.showProportional(Text("NEW", color="darkgrey", size=0.08), 0.80, 0.90)

					stim = Text('')
					bc = ButtonChooser(Key(config.keyLeft),Key(config.keyRight))
					pres_time, b, bc_time = stim.present(clk=clk, duration=config.C_RESP_TIME, bc=bc)
					vt.updateScreen(clk)

					rt = bc_time[0]-pres_time[0]
					# Find response: Z=OLD(1), /=NEW(0)
					if (b == None):
						response = -1
					elif (b.name == config.keyLeft):
						response = 1  # OLD
					elif (b.name == config.keyRight):
						response = 0  # NEW

					# Score: correct if response matches target
					recog_acc = 1 if response == trial['target'] else 0

					# Log item trial
					log.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tITEM\t' + trial['word'] + '\t' + str(trial['word_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)
					recoglog.logMessage('%s\t%d' % (str(list_count) + '\t' + str(test_trial_count) + '\tITEM\t' + str(trial['word_id']) + '\t' + str(trial['target']) + '\t' + str(response) + '\t' + str(recog_acc), rt), clk)

				else:  # trial['type'] == 'assoc'
					# Associative Recognition: Show two words
					stim = Text(trial['word1'] + "  " + trial['word2'], font = Font("resources/courbd.ttf"))
					do_pres = vt.showProportional(stim, 0.5, 0.5)
					# Labels: INTACT (Z) vs RECOMBINED (/)
					leftinstruct_print = vt.showProportional(Text("INTACT", color="darkgrey", size=0.08), 0.20, 0.90)
					rightinstruct_print = vt.showProportional(Text("RECOMBINED", color="darkgrey", size=0.08), 0.80, 0.90)

					stim = Text('')
					bc = ButtonChooser(Key(config.keyLeft),Key(config.keyRight))
					pres_time, b, bc_time = stim.present(clk=clk, duration=config.C_RESP_TIME, bc=bc)
					vt.updateScreen(clk)

					rt = bc_time[0]-pres_time[0]
					# Find response: Z=INTACT(1), /=RECOMBINED(0)
					if (b == None):
						response = -1
					elif (b.name == config.keyLeft):
						response = 1  # INTACT
					elif (b.name == config.keyRight):
						response = 0  # RECOMBINED

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


##Change this all

##START OF TIPI QUESTIONNAIRE

#If using VVIQ as an example:

#Prealocate Lists
TIPI = []
Instructing = []
vt.clear("black")

#Display Initial Instruction	
#instruction = open("TIPIinstruct/preQuestionnaire_instruction.txt")
instruction = open("instruct/TIPIpreQuestionnaire_instruction.txt")		
instruct(instruction.read(), clk=clk)

#Build List of Questions

TIPI.append("I see myself as extraverted, enthusiastic.")
TIPI.append("I See myself as critical, quarrelsome.")
TIPI.append("I see myself as dependable, self-disciplined.")
TIPI.append("I see myself as anxious, easily upset.")
TIPI.append("I see myself as open to new experiences, complex.")
TIPI.append("I see myself as reserved, quiet.")
TIPI.append("I see myself as sympathetic, warm.")
TIPI.append("I see myself as disorganized, careless.")
TIPI.append("I see myself as calm, emotionally stable.")
TIPI.append("I see myself as conventional, uncreative.")

#QUestion 1

outfile = open(TIPI_outputfile, "a") 
instructing= "I see myself as extraverted, enthusiastic." 
for i in range(1):
        vt.updateScreen(clk) 
    	vt.clear("black") 
	vt.showProportional(Text(instructing, font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.1)
   	#vt.showProportional(Text(TIPI[i], font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.4)
  	vt.showProportional(Text("[1] Disagree strongly", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.30)
	vt.showProportional(Text("[2] Disagree moderately", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.35)
  	vt.showProportional(Text("[3] Disagree a little", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.40)  
   	vt.showProportional(Text("[4] Neither agree nor disagree", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.45)
   	vt.showProportional(Text("[5] Agree a little", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.50)
   	vt.showProportional(Text("[6] Agree moderately", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.55)
   	vt.showProportional(Text("[7] Agree strongly", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.60)   
#0.04 is font size, 0.1 is indentation, 0.30 is line from the top to bottom)
   	bc = ButtonChooser(Key("1"),Key("2"),Key("3"),Key("4"),Key("5"),Key("6"),Key("7"))
   	stim = Text("")
   	pres_time, ans, bc_time = stim.present(clk=clk, bc=bc, duration=config.maxRTVVIQ)
   	vt.updateScreen(clk)
   	vt.clear("black")
        outfile.write("%d \n" % int(ans.name))
        vt.updateScreen()
   	u = int(ans.name) 
   	if  u==1:
      		vt.showProportional(Text("[1] Disagree strongly",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.30)
   	if u==2:
      		vt.showProportional(Text("[2] Disagree moderately",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.35)			  
   	if  u==3:
      		vt.showProportional(Text("[3] Disagree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.40)
   	if  u==4:
      		vt.showProportional(Text("[4] Neither agree nor disagree",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.45)
   	if  u==5:
      		vt.showProportional(Text("[5] Agree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.50)
   	if  u==6:
      		vt.showProportional(Text("[6] Agree moderately",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.55)
   	if  u==7:
      		vt.showProportional(Text("[7] Agree strongly",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.60)
#outfile.writelines("%d \n" % int(ans.name)
#outfile.close()
   	vt.updateScreen(clk)
   	vt.clear("black")
   	clk.delay(1000)
   	vt.updateScreen(clk)
   	vt.clear("black")
   	#outfile.close()

#QUestion 2
outfile = open(TIPI_outputfile, "a") 
instructing= "I see myself as critical, quarrelsome." 
for i in range(1):
        vt.updateScreen(clk) 
    	vt.clear("black") 
	vt.showProportional(Text(instructing, font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.1)
   	#vt.showProportional(Text(TIPI[i], font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.4)
  	vt.showProportional(Text("[1] Disagree strongly", font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.30)
	vt.showProportional(Text("[2] Disagree moderately", font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.35)
  	vt.showProportional(Text("[3] Disagree a little", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.40)  
   	vt.showProportional(Text("[4] Neither agree nor disagree", font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.45)
   	vt.showProportional(Text("[5] Agree a little", font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.50)
   	vt.showProportional(Text("[6] Agree moderately", font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.55)
   	vt.showProportional(Text("[7] Agree strongly", font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.60)   
   	bc = ButtonChooser(Key("1"),Key("2"),Key("3"),Key("4"),Key("5"),Key("6"),Key("7"))
   	stim = Text("")
   	pres_time, ans, bc_time = stim.present(clk=clk, bc=bc, duration=config.maxRTVVIQ)
   	vt.updateScreen(clk)
   	vt.clear("black")
        outfile.write("%d \n" % int(ans.name))
        vt.updateScreen()
   	u = int(ans.name) 
   	if  u==1:
      		vt.showProportional(Text("[1] Disagree strongly",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.30)
   	if u==2:
      		vt.showProportional(Text("[2] Disagree moderately",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.35)			  
   	if  u==3:
      		vt.showProportional(Text("[3] Disagree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.40)
   	if  u==4:
      		vt.showProportional(Text("[4] Neither agree nor disagree",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.45)
   	if  u==5:
      		vt.showProportional(Text("[5] Agree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.50)
   	if  u==6:
      		vt.showProportional(Text("[6] Agree moderately",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.55)
   	if  u==7:
      		vt.showProportional(Text("[7] Agree strongly",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.60)
#outfile.writelines("%d \n" % int(ans.name)
#outfile.close()
   	vt.updateScreen(clk)
   	vt.clear("black")
   	clk.delay(1000)
   	vt.updateScreen(clk)
   	vt.clear("black")

#Question 3
outfile = open(TIPI_outputfile, "a") 
instructing= "I see myself as dependable, self-disciplined."
for i in range(1):
        vt.updateScreen(clk) 
    	vt.clear("black") 
	vt.showProportional(Text(instructing, font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.1)
   	#vt.showProportional(Text(TIPI[i], font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.4)
  	vt.showProportional(Text("[1] Disagree strongly", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.30)
	vt.showProportional(Text("[2] Disagree moderately", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.35)
  	vt.showProportional(Text("[3] Disagree a little", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.40)  
   	vt.showProportional(Text("[4] Neither agree nor disagree", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.45)
   	vt.showProportional(Text("[5] Agree a little", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.50)
   	vt.showProportional(Text("[6] Agree moderately", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.55)
   	vt.showProportional(Text("[7] Agree strongly", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.60)   
   	bc = ButtonChooser(Key("1"),Key("2"),Key("3"),Key("4"),Key("5"),Key("6"),Key("7"))
   	stim = Text("")
   	pres_time, ans, bc_time = stim.present(clk=clk, bc=bc, duration=config.maxRTVVIQ)
   	vt.updateScreen(clk)
   	vt.clear("black")
        outfile.write("%d \n" % int(ans.name))
        vt.updateScreen()
   	u = int(ans.name) 
   	if  u==1:
      		vt.showProportional(Text("[1] Disagree strongly",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.30)
   	if u==2:
      		vt.showProportional(Text("[2] Disagree moderately",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.35)			  
   	if  u==3:
      		vt.showProportional(Text("[3] Disagree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.40)
   	if  u==4:
      		vt.showProportional(Text("[4] Neither agree nor disagree",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.45)
   	if  u==5:
      		vt.showProportional(Text("[5] Agree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.50)
   	if  u==6:
      		vt.showProportional(Text("[6] Agree moderately",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.55)
   	if  u==7:
      		vt.showProportional(Text("[7] Agree strongly",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.60)
#outfile.writelines("%d \n" % int(ans.name)
#outfile.close()
   	vt.updateScreen(clk)
   	vt.clear("black")
   	clk.delay(1000)
   	vt.updateScreen(clk)
   	vt.clear("black")

#Question 4
outfile = open(TIPI_outputfile, "a") 
instructing= "I see myself as anxious, easily upset."
for i in range(1):
        vt.updateScreen(clk) 
    	vt.clear("black") 
	vt.showProportional(Text(instructing, font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.1)
   	#vt.showProportional(Text(TIPI[i], font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.4)
  	vt.showProportional(Text("[1] Disagree strongly", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.30)
	vt.showProportional(Text("[2] Disagree moderately", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.35)
  	vt.showProportional(Text("[3] Disagree a little", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.40)  
   	vt.showProportional(Text("[4] Neither agree nor disagree", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.45)
   	vt.showProportional(Text("[5] Agree a little", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.50)
   	vt.showProportional(Text("[6] Agree moderately", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.55)
   	vt.showProportional(Text("[7] Agree strongly", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.60)   
   	bc = ButtonChooser(Key("1"),Key("2"),Key("3"),Key("4"),Key("5"),Key("6"),Key("7"))
   	stim = Text("")
   	pres_time, ans, bc_time = stim.present(clk=clk, bc=bc, duration=config.maxRTVVIQ)
   	vt.updateScreen(clk)
   	vt.clear("black")
        outfile.write("%d \n" % int(ans.name))
        vt.updateScreen()
   	u = int(ans.name) 
   	if  u==1:
      		vt.showProportional(Text("[1] Disagree strongly",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.30)
   	if u==2:
      		vt.showProportional(Text("[2] Disagree moderately",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.35)			  
   	if  u==3:
      		vt.showProportional(Text("[3] Disagree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.40)
   	if  u==4:
      		vt.showProportional(Text("[4] Neither agree nor disagree",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.45)
   	if  u==5:
      		vt.showProportional(Text("[5] Agree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.50)
   	if  u==6:
      		vt.showProportional(Text("[6] Agree moderately",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.55)
   	if  u==7:
      		vt.showProportional(Text("[7] Agree strongly",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.60)
#outfile.writelines("%d \n" % int(ans.name)
#outfile.close()
   	vt.updateScreen(clk)
   	vt.clear("black")
   	clk.delay(1000)
   	vt.updateScreen(clk)
   	vt.clear("black")

#Question 5
outfile = open(TIPI_outputfile, "a") 
instructing= "I see myself as open to new experiences, complex."
for i in range(1):
        vt.updateScreen(clk) 
    	vt.clear("black") 
	vt.showProportional(Text(instructing, font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.1)
   	#vt.showProportional(Text(TIPI[i], font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.4)
  	vt.showProportional(Text("[1] Disagree strongly", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.30)
	vt.showProportional(Text("[2] Disagree moderately", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.35)
  	vt.showProportional(Text("[3] Disagree a little", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.40)  
   	vt.showProportional(Text("[4] Neither agree nor disagree", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.45)
   	vt.showProportional(Text("[5] Agree a little", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.50)
   	vt.showProportional(Text("[6] Agree moderately", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.55)
   	vt.showProportional(Text("[7] Agree strongly", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.60)   
   	bc = ButtonChooser(Key("1"),Key("2"),Key("3"),Key("4"),Key("5"),Key("6"),Key("7"))
   	stim = Text("")
   	pres_time, ans, bc_time = stim.present(clk=clk, bc=bc, duration=config.maxRTVVIQ)
   	vt.updateScreen(clk)
   	vt.clear("black")
        outfile.write("%d \n" % int(ans.name))
        vt.updateScreen()
   	u = int(ans.name) 
   	if  u==1:
      		vt.showProportional(Text("[1] Disagree strongly",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.30)
   	if u==2:
      		vt.showProportional(Text("[2] Disagree moderately",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.35)			  
   	if  u==3:
      		vt.showProportional(Text("[3] Disagree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.40)
   	if  u==4:
      		vt.showProportional(Text("[4] Neither agree nor disagree",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.45)
   	if  u==5:
      		vt.showProportional(Text("[5] Agree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.50)
   	if  u==6:
      		vt.showProportional(Text("[6] Agree moderately",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.55)
   	if  u==7:
      		vt.showProportional(Text("[7] Agree strongly",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.60)
#outfile.writelines("%d \n" % int(ans.name)
#outfile.close()
   	vt.updateScreen(clk)
   	vt.clear("black")
   	clk.delay(1000)
   	vt.updateScreen(clk)
   	vt.clear("black")

#Question 6
outfile = open(TIPI_outputfile, "a") 
instructing= "I see myself as reserved, quiet."
for i in range(1):
        vt.updateScreen(clk) 
    	vt.clear("black") 
	vt.showProportional(Text(instructing, font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.1)
   	#vt.showProportional(Text(TIPI[i], font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.4)
  	vt.showProportional(Text("[1] Disagree strongly", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.30)
	vt.showProportional(Text("[2] Disagree moderately", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.35)
  	vt.showProportional(Text("[3] Disagree a little", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.40)  
   	vt.showProportional(Text("[4] Neither agree nor disagree", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.45)
   	vt.showProportional(Text("[5] Agree a little", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.50)
   	vt.showProportional(Text("[6] Agree moderately", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.55)
   	vt.showProportional(Text("[7] Agree strongly", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.60)   
   	bc = ButtonChooser(Key("1"),Key("2"),Key("3"),Key("4"),Key("5"),Key("6"),Key("7"))
   	stim = Text("")
   	pres_time, ans, bc_time = stim.present(clk=clk, bc=bc, duration=config.maxRTVVIQ)
   	vt.updateScreen(clk)
   	vt.clear("black")
        outfile.write("%d \n" % int(ans.name))
        vt.updateScreen()
   	u = int(ans.name) 
   	if  u==1:
      		vt.showProportional(Text("[1] Disagree strongly",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.30)
   	if u==2:
      		vt.showProportional(Text("[2] Disagree moderately",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.35)			  
   	if  u==3:
      		vt.showProportional(Text("[3] Disagree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.40)
   	if  u==4:
      		vt.showProportional(Text("[4] Neither agree nor disagree",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.45)
   	if  u==5:
      		vt.showProportional(Text("[5] Agree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.50)
   	if  u==6:
      		vt.showProportional(Text("[6] Agree moderately",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.55)
   	if  u==7:
      		vt.showProportional(Text("[7] Agree strongly",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.60)
#outfile.writelines("%d \n" % int(ans.name)
#outfile.close()
   	vt.updateScreen(clk)
   	vt.clear("black")
   	clk.delay(1000)
   	vt.updateScreen(clk)
   	vt.clear("black")

#Question 7
outfile = open(TIPI_outputfile, "a") 
instructing= "I see myself as sympathetic, warm."
for i in range(1):
        vt.updateScreen(clk) 
    	vt.clear("black") 
	vt.showProportional(Text(instructing, font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.1)
   	#vt.showProportional(Text(TIPI[i], font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.4)
  	vt.showProportional(Text("[1] Disagree strongly", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.30)
	vt.showProportional(Text("[2] Disagree moderately", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.35)
  	vt.showProportional(Text("[3] Disagree a little", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.40)  
   	vt.showProportional(Text("[4] Neither agree nor disagree", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.45)
   	vt.showProportional(Text("[5] Agree a little", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.50)
   	vt.showProportional(Text("[6] Agree moderately", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.55)
   	vt.showProportional(Text("[7] Agree strongly", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.60)   
   	bc = ButtonChooser(Key("1"),Key("2"),Key("3"),Key("4"),Key("5"),Key("6"),Key("7"))
   	stim = Text("")
   	pres_time, ans, bc_time = stim.present(clk=clk, bc=bc, duration=config.maxRTVVIQ)
   	vt.updateScreen(clk)
   	vt.clear("black")
        outfile.write("%d \n" % int(ans.name))
        vt.updateScreen()
   	u = int(ans.name) 
   	if  u==1:
      		vt.showProportional(Text("[1] Disagree strongly",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.30)
   	if u==2:
      		vt.showProportional(Text("[2] Disagree moderately",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.35)			  
   	if  u==3:
      		vt.showProportional(Text("[3] Disagree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.40)
   	if  u==4:
      		vt.showProportional(Text("[4] Neither agree nor disagree",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.45)
   	if  u==5:
      		vt.showProportional(Text("[5] Agree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.50)
   	if  u==6:
      		vt.showProportional(Text("[6] Agree moderately",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.55)
   	if  u==7:
      		vt.showProportional(Text("[7] Agree strongly",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.60)
#outfile.writelines("%d \n" % int(ans.name)
#outfile.close()
   	vt.updateScreen(clk)
   	vt.clear("black")
   	clk.delay(1000)
   	vt.updateScreen(clk)
   	vt.clear("black")

#Question 8
outfile = open(TIPI_outputfile, "a") 
instructing= "I see myself as disorganized, careless."
for i in range(1):
        vt.updateScreen(clk) 
    	vt.clear("black") 
	vt.showProportional(Text(instructing, font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.1)
   	#vt.showProportional(Text(TIPI[i], font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.4)
  	vt.showProportional(Text("[1] Disagree strongly", font = Font("resources/courbd.ttf"),size = 0.04), 0.1, 0.30)
	vt.showProportional(Text("[2] Disagree moderately", font = Font("resources/courbd.ttf"),size = 0.04), 0.1, 0.35)
  	vt.showProportional(Text("[3] Disagree a little", font = Font("resources/courbd.ttf"),size = 0.04), 0.1, 0.40)  
   	vt.showProportional(Text("[4] Neither agree nor disagree", font = Font("resources/courbd.ttf"),size = 0.04), 0.1, 0.45)
   	vt.showProportional(Text("[5] Agree a little", font = Font("resources/courbd.ttf"),size = 0.04), 0.1, 0.50)
   	vt.showProportional(Text("[6] Agree moderately", font = Font("resources/courbd.ttf"),size = 0.04), 0.1, 0.55)
   	vt.showProportional(Text("[7] Agree strongly", font = Font("resources/courbd.ttf"),size = 0.04), 0.1, 0.60)   
   	bc = ButtonChooser(Key("1"),Key("2"),Key("3"),Key("4"),Key("5"),Key("6"),Key("7"))
   	stim = Text("")
   	pres_time, ans, bc_time = stim.present(clk=clk, bc=bc, duration=config.maxRTVVIQ)
   	vt.updateScreen(clk)
   	vt.clear("black")
        outfile.write("%d \n" % int(ans.name))
        vt.updateScreen()
   	u = int(ans.name) 
   	if  u==1:
      		vt.showProportional(Text("[1] Disagree strongly",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.30)
   	if u==2:
      		vt.showProportional(Text("[2] Disagree moderately",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.35)			  
   	if  u==3:
      		vt.showProportional(Text("[3] Disagree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.40)
   	if  u==4:
      		vt.showProportional(Text("[4] Neither agree nor disagree",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.45)
   	if  u==5:
      		vt.showProportional(Text("[5] Agree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.50)
   	if  u==6:
      		vt.showProportional(Text("[6] Agree moderately",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.55)
   	if  u==7:
      		vt.showProportional(Text("[7] Agree strongly",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.60)
#outfile.writelines("%d \n" % int(ans.name)
#outfile.close()
   	vt.updateScreen(clk)
   	vt.clear("black")
   	clk.delay(1000)
   	vt.updateScreen(clk)
   	vt.clear("black")

#Question 9
outfile = open(TIPI_outputfile, "a") 
instructing= "I see myself as calm, emotionally stable."
for i in range(1):
        vt.updateScreen(clk) 
    	vt.clear("black") 
	vt.showProportional(Text(instructing, font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.1)
   	#vt.showProportional(Text(TIPI[i], font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.4)
  	vt.showProportional(Text("[1] Disagree strongly", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.30)
	vt.showProportional(Text("[2] Disagree moderately", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.35)
  	vt.showProportional(Text("[3] Disagree a little", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.40)  
   	vt.showProportional(Text("[4] Neither agree nor disagree", font = Font("resources/courbd.ttf"),size = .04), 0.11, 0.45)
   	vt.showProportional(Text("[5] Agree a little", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.50)
   	vt.showProportional(Text("[6] Agree moderately", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.55)
   	vt.showProportional(Text("[7] Agree strongly", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.60)   
   	bc = ButtonChooser(Key("1"),Key("2"),Key("3"),Key("4"),Key("5"),Key("6"),Key("7"))
   	stim = Text("")
   	pres_time, ans, bc_time = stim.present(clk=clk, bc=bc, duration=config.maxRTVVIQ)
   	vt.updateScreen(clk)
   	vt.clear("black")
        outfile.write("%d \n" % int(ans.name))
        vt.updateScreen()
   	u = int(ans.name) 
   	if  u==1:
      		vt.showProportional(Text("[1] Disagree strongly",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.30)
   	if u==2:
      		vt.showProportional(Text("[2] Disagree moderately",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.35)			  
   	if  u==3:
      		vt.showProportional(Text("[3] Disagree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.40)
   	if  u==4:
      		vt.showProportional(Text("[4] Neither agree nor disagree",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.45)
   	if  u==5:
      		vt.showProportional(Text("[5] Agree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.50)
   	if  u==6:
      		vt.showProportional(Text("[6] Agree moderately",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.55)
   	if  u==7:
      		vt.showProportional(Text("[7] Agree strongly",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.60)
#outfile.writelines("%d \n" % int(ans.name)
#outfile.close()
   	vt.updateScreen(clk)
   	vt.clear("black")
   	clk.delay(1000)
   	vt.updateScreen(clk)
   	vt.clear("black")

#Question 10
outfile = open(TIPI_outputfile, "a") 
instructing= "I see myself as conventional, uncreative."
for i in range(1):
        vt.updateScreen(clk) 
    	vt.clear("black") 
	vt.showProportional(Text(instructing, font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.1)
   	#vt.showProportional(Text(TIPI[i], font = Font("resources/courbd.ttf"), size = .04), 0.1, 0.4)
  	vt.showProportional(Text("[1] Disagree strongly", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.30)
	vt.showProportional(Text("[2] Disagree moderately", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.35)
  	vt.showProportional(Text("[3] Disagree a little", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.40)  
   	vt.showProportional(Text("[4] Neither agree nor disagree", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.45)
   	vt.showProportional(Text("[5] Agree a little", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.50)
   	vt.showProportional(Text("[6] Agree moderately", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.55)
   	vt.showProportional(Text("[7] Agree strongly", font = Font("resources/courbd.ttf"),size = .04), 0.1, 0.60)   
   	bc = ButtonChooser(Key("1"),Key("2"),Key("3"),Key("4"),Key("5"),Key("6"),Key("7"))
   	stim = Text("")
   	pres_time, ans, bc_time = stim.present(clk=clk, bc=bc, duration=config.maxRTVVIQ)
   	vt.updateScreen(clk)
   	vt.clear("black")
        outfile.write("%d \n" % int(ans.name))
        vt.updateScreen()
   	u = int(ans.name) 
   	if  u==1:
      		vt.showProportional(Text("[1] Disagree strongly",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.30)
   	if u==2:
      		vt.showProportional(Text("[2] Disagree moderately",color ="green",font = Font("resources/courbd.ttf"),size =.04), 0.1, 0.35)			  
   	if  u==3:
      		vt.showProportional(Text("[3] Disagree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.40)
   	if  u==4:
      		vt.showProportional(Text("[4] Neither agree nor disagree",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.45)
   	if  u==5:
      		vt.showProportional(Text("[5] Agree a little",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.50)
   	if  u==6:
      		vt.showProportional(Text("[6] Agree moderately",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.55)
   	if  u==7:
      		vt.showProportional(Text("[7] Agree strongly",color ="green",font = Font("resources/courbd.ttf"), size =.04), 0.1, 0.60)
#outfile.writelines("%d \n" % int(ans.name)
#outfile.close()
   	vt.updateScreen(clk)
   	vt.clear("black")
   	clk.delay(1000)
   	vt.updateScreen(clk)
   	vt.clear("black")
        outfile.close()

################################################






## All done!
if 1 == 1: # if statement to help sort the code into blocks 
	clk.wait()
	
	# reset the display to black
	vt.clear("black")
	
	## DONE!!
	
	# open the instructions file
	instructions = open("instruct/thankyou.txt")
	
	# show the experiment instructions
	instruct(instructions.read(), clk=clk)

	# reset the display to black
	vt.clear("black")
	
	# provide the 1st practice pair
	stim = Text("Please get the experimenter \n to complete this session.")

	# create a ButtonChooser object
	# to watch for specific keys
	# Hidden Instruction: Press K to skip to next pair
	bc = ButtonChooser(Key("LEFT SHIFT") and Key("RIGHT SHIFT") and Key("\\"))

	ts, b, rt = stim.present(clk=clk, duration=1800000, bc=bc)
	
