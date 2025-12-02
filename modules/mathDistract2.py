#!/usr/bin/python

from pyepl.locals import *
#import RandomArray, Numeric
from numpy import *
		
def mathDistract2(clk = None,
                 mathlog = None,
                 problemTimeLimit = None,
                 numVars = 2,
                 maxNum = 9,
                 minNum = 1,
                 maxProbs = 50,
                 plusAndMinus = False,
                 minDuration = 20000,
                 blanktime = 100,
                 textSize = None,
                 tfKeys = None,
                 ansMod = [0,1,-1,10,-10],
                 ansProb = [.5,.125,.125,.125,.125]):
    """
    Math distractor 2 for specified period of time.  Logs to a math_distract.log
    if no log is passed in.

    INPUT ARGS:
      clk - Optional PresentationClock for timing.
      mathlog - Optional Logtrack for logging.
      problemTimeLimit - set this param for non-self-paced distractor;
                         buzzer sounds when time's up; you get at least
                         minDuration/problemTimeLimit problems.
      numVars - Number of variables in the problem.
      maxNum - Max possible number for each variable.
      minNum - Min possible number for each varialbe.
      maxProbs - Max number of problems.
      plusAndMinus - True will have both plus and minus.
      minDuration - Minimum duration of distractor.
      blanktime - time between distractor questions.
      textSize - Vertical height of the text.
      tfKeys - Tuple of keys for true/false problems. e.g., tfKeys = ('T','F')
      ansMod - For True/False problems, the possible values to add to correct answer.
      ansProb - The probability of each modifer on ansMod (must add to 1).
      
    """

    # start the timing
    start_time = timing.now()

    # get the tracks
    v = VideoTrack.lastInstance()
    k = KeyTrack.lastInstance()

    # see if need logtrack
    if mathlog is None:
        mathlog = LogTrack('math_distract')

    # log the start
    mathlog.logMessage('START')
    
    # start timing
    if clk is None:
        clk = exputils.PresentationClock()

    # set the stop time
    if not minDuration is None:
        stop_time = start_time + minDuration
    else:
        stop_time = None
    	    
    # clear the screen (now left up to caller of function)
    #v.clear("black")

    # generate a bunch of math problems
    #vars = RandomArray.uniform(minNum,maxNum,[maxProbs, numVars]).astype(Numeric.Int16)
    vars = random.uniform(minNum,maxNum,[maxProbs, numVars]).astype(int)
    if plusAndMinus:
        #pm = Numeric.sign(RandomArray.uniform(-1,1,[maxProbs, numVars-1]))
	pm = sign(random.uniform(-1,1,[maxProbs, numVars-1]))
    else:
        pm = ones([maxProbs, numVars-1])

    # see if T/F or numeric answers
    if isinstance(tfKeys,tuple):
        # do true/false problems
        tfProblems = True

        # check the ansMod and ansProb
        if len(ansMod) != len(ansProb):
            # raise error
            pass
        if sum(ansProb) != 1.0:
            # raise error
            pass
        ansProb = cumsum(ansProb)
    else:
        tfProblems = False

    # set up the answer button
    if tfProblems:
        # set up t/f keys
        ans_but = k.keyChooser(*tfKeys)
    else:
        # set up numeric entry
        ans_but = k.keyChooser('0','1','2','3','4','5','6','7','8','9','-',
                               '[0]','[1]','[2]','[3]','[4]','[5]','[6]',
                               '[7]','[8]','[9]','[-]','BACKSPACE')
    
    # do equations till the time is up
    curProb = 0
    while not (not stop_time is None and timing.now() >= stop_time) and curProb < maxProbs:
        # generate the string and result

        # loop over each variable to generate the problem
        probtxt = ''
        for i,x in enumerate(vars[curProb,:]):
            if i > 0:
                # add the sign
                if pm[curProb,i-1] > 0:
                    probtxt += ' + '
                else:
                    probtxt += ' - '

            # add the number
            probtxt += str(x)

        # calc the correct answer
        cor_ans = eval(probtxt)

        # add the equal sign
        probtxt += ' = '

        # do tf or numeric problem
        if tfProblems:
            # determine the displayed answer
            # see which answermod
            #ansInd = min(Numeric.nonzero(ansProb >= RandomArray.uniform(0,1)))
            ansInd = min(nonzero(ansProb >= random.uniform(0,1)))
            disp_ans = cor_ans + ansMod[ansInd]

            # see if is True or False
            if disp_ans == cor_ans:
                # correct response is true
                corRsp = tfKeys[0]
            else:
                # correct response is false
                corRsp = tfKeys[1]

            # set response str
            rstr = str(disp_ans)
        else:
            rstr = ''

        # display it on the screen
        pt = v.showProportional(Text(probtxt,size = textSize),.4,.5)
        rt = v.showRelative(Text(rstr, size = textSize),RIGHT,pt)
        probstart = v.updateScreen(clk)
        
        # wait for input
        answer = .12345  # not an int
        hasMinus = False
	if problemTimeLimit:
	    probStart = timing.now()
	    probEnd = probStart + problemTimeLimit
	    curProbTimeLimit = probEnd - probStart
	else:
	    curProbTimeLimit = None

        # wait for keypress
        kret,timestamp = ans_but.waitWithTime(maxDuration = curProbTimeLimit, clock=clk)

        # process as T/F or as numeric answer
        if tfProblems:            
            # check the answer
            if not kret is None and kret.name == corRsp:
                isCorrect = 1
            else:
                isCorrect = 0
        else:
            # is part of numeric answer
            while kret and ((kret.name != "RETURN" and kret.name != "ENTER") or (hasMinus is True and len(rstr)<=1) or (len(rstr)==0)):
                # process the response
                if kret.name == 'BACKSPACE':
                    # remove last char
                    if len(rstr) > 0:
                        rstr = rstr[:-1]
                        if len(rstr) == 0:
                            hasMinus = False
                elif kret.name == '-' or kret.name == '[-]':
                    if len(rstr) == 0 and plusAndMinus:
                        # append it
                        rstr = '-'
                        hasMinus = True
                elif kret.name == 'RETURN' or kret.name == 'ENTER':
                    # ignore cause have minus without number
                    continue
                elif len(rstr) == 0 and (kret.name == '0' or kret.name == '[0]'):
                # Can't start a number with 0, so pass
                	pass
                else:
                    # if its a number, just append
                    numstr = kret.name.strip('[]')
                    rstr = rstr + numstr

                # update the text
                rt = v.replace(rt,Text(rstr,size = textSize))
                v.updateScreen(clk)


                # wait for another response
                if problemTimeLimit:
                    curProbTimeLimit = probEnd - timing.now()
                else:
                    curProbTimeLimit = None
                kret,timestamp = ans_but.waitWithTime(maxDuration = curProbTimeLimit,clock=clk)


	# check the answer

	try:
		len(rstr)==0 | eval(rstr) != cor_ans
	except (SyntaxError, NameError):
		isCorrect = 0
	else:
		if eval(rstr) == cor_ans:
	    		isCorrect = 1
		else:
			isCorrect = 0

        
        # calc the RT as (RT, maxlatency)
        prob_rt = (timestamp[0]-probstart[0],timestamp[1]+probstart[1])
        
        # log it
        # probstart, PROB, prob_txt, ans_txt, Correct(1/0), RT
        mathlog.logMessage('PROB\t%r\t%r\t%d\t%ld\t%d' %
                           (probtxt,rstr,isCorrect,prob_rt[0],curProbTimeLimit),
                           probstart[0])
        
        # clear the problem
        v.unshow(pt,rt)
        v.updateScreen(clk)

	v.clear("black")
	clk.delay(blanktime)
        
        # increment the curprob
        curProb+=1

    # log the end
    mathlog.logMessage('STOP',timestamp)

    # tare the clock
    clk.tare(timestamp)
