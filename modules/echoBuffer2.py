#!/usr/bin/python

from pyepl.locals import *
		
class echoBuffer2:
	def __init__(self, init_str='', color=None, font = None, maxDuration=None, size=None, x=.5, y=.5, clk=None):
		"""
		Set up the buffer: optionally pre-load a string init_str, and
		set the text size to size, and set the buffer's x and y
		locations on the screen to x, y.
		"""
		self._v = VideoTrack.lastInstance()
		self._currentStr = init_str
		self._font = font
		self._color = color
		self._size = size
		self._shown = self._v.showProportional(Text(self._currentStr, size=size), x,y)
		self.startTime = self._v.updateScreen(clk)
		self._maxDuration = maxDuration

		k = KeyTrack.lastInstance()
		self._responseChooser = k.keyChooser()

	def keyProcessLoop(self, clk=None):
		if clk is None:
			# if no PresentationClock is given, create one
			clk = exputils.PresentationClock()
		probeStart = timing.now()
		if self._maxDuration:
		   	probeEnd = probeStart + self._maxDuration
		   	curProbeTimeLimit = probeEnd - probeStart
		else:
			curProbeTimeLimit = None

		# wait for keypress
		kret, timestamp = self._responseChooser.waitWithTime(maxDuration=curProbeTimeLimit, clock=clk)
		firstkeypress = timing.now() - probeStart

		## we don't want to accept ENTER/RETURN unless there is at least 4 characters, right?
		
		while kret and (len(self._currentStr) < 2):
			# process the response
			kret.name = kret.name.strip('[]') # for numpad keys
			if kret.name == 'BACKSPACE':
				# remove last char
				if len(self._currentStr) > 0:
					self._currentStr = self._currentStr[:-1]
			elif len(kret.name) != 1:
				# do nothing, this will skip over things like 'LEFT SHIFT'
				self._currentStr = self._currentStr
			else:
				# just append
				newstr = kret.name.strip('[]')
				self._currentStr = self._currentStr + newstr

			# update the text
			self._shown = self._v.replace(self._shown, Text(self._currentStr, color = self._color, font = self._font, size = self._size))
			self._v.updateScreen(clk)

			# wait for another response
			if self._maxDuration:
				curProbeTimeLimit = probeEnd - timing.now()
			else:
				curProbeTimeLimit = None
			kret, timestamp = self._responseChooser.waitWithTime(maxDuration=curProbeTimeLimit, clock=clk)
				
		while kret and (kret.name != "RETURN" and kret.name != "ENTER"):
			# process the response
			kret.name = kret.name.strip('[]') # for numpad keys
			if kret.name == 'BACKSPACE':
				# remove last char
				if len(self._currentStr) > 0:
					self._currentStr = self._currentStr[:-1]
			elif len(kret.name) != 1:
				# do nothing, this will skip over things like 'LEFT SHIFT'
				self._currentStr = self._currentStr
			else:
				# just append
				newstr = kret.name.strip('[]')
				self._currentStr = self._currentStr + newstr

			# update the text
			self._shown = self._v.replace(self._shown, Text(self._currentStr, color = self._color, font = self._font, size = self._size))
			self._v.updateScreen(clk)

			# wait for another response
			if self._maxDuration:
				curProbeTimeLimit = probeEnd - timing.now()
			else:
				curProbeTimeLimit = None
			kret, timestamp = self._responseChooser.waitWithTime(maxDuration=curProbeTimeLimit, clock=clk)

		return self._currentStr, firstkeypress+33, timing.now()-self.startTime[0]


# Sample experiment begins here...
if __name__ == "__main__":
	# set up the experiment...
	exp = Experiment()

	# allow users to break out of the experiment with escape-F1 
	# (the default key combo)
	exp.setBreak()

	# create tracks...
	video = VideoTrack("video")
	keyboard = KeyTrack("keyboard")
	
	# create a PresentationClock to handle timing
	clock = PresentationClock()

	video.clear("black")

	# display the "cross-hairs":
	video.showCentered(Text("+", size = 0.2))
	video.showLeft(Text("-", size = 0.2))
	video.updateScreen(clock)
	
	# wait before presenting the first beep:
	clock.delay(1000)

	video.clear("black")
	eb = echoBuffer("foo", clk=clock)
	(str, time) = eb.keyProcessLoop(clock)
	print str, time
