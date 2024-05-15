





	#=========================================================
	def getNextDistillment(me):
	#=========================================================
		# a "Distillment" contains results from one or more "EExtractors"
		# an "EExtractor" contains one "matcher" or "catcher", a set of "catch keys" and one or more "attributes"
		

		# {"MatchRegex":"^\\s*(\\S+).*$",  # eg. "initialize"
				# "MatchRole":"ACTIVITY",
				# "CatchKeys":"$ActivityNode",  # here the value is a string, not an array
				# <THIS LINE>,
				# "ActivityNodeAttr":" , shape=ellipse, style=filled, fillcolor=yellow"} 
		# <THIS_LINE> = "NextShift":<SHIFT_TAG>,
		# <SHIFT_TAG> =
		#
		#IF hosting eExtraction matches THEN
		#	"FINISH" ==========================================================
		#		return END to main level
		#   "<integer>" ====================================================
		#		 	gets feed line at offset position from focus feed line
		#			takes next eExtraction item
		#			IF match fails THEN
		#				return END to main level
		#			ELSE
		#				return OK to main level
		#			END

		#	"NEXT" ===================================================
		#			take next eExtraction item
		#			WHILE feed lines left DO
		#				get next feed line
		#				IF eExtraction item matches THEN 
		#					return OK to main level
		#			END
		#			return END to main level (because no match)
		#	-	continues getting feed lines after focus feed line 
		#	-	if feed lines end without match, program shall terminate
		#   "START" =================================================
		#			rewind eExtraction items
		#			get next feed line
		#
		# executes navigations within feed lines and within eExtraction items until eExtraction event or script termination occurs
		#	tries to match a sequence of 1...N eExtraction regexes feed (file) lines
		#	when all single sequence match attempts are done, this function ends and returns 
		#	match type to main script
		#   ---> the main script then generates 1...N reports according to state maintained by a state machine at main script
		# if  match occurs an feed line "n" and matching step of EExtraction Item "N" is "NEXT" then 
		# -	gets EExtraction item "N+1" and starts trying to match it to feed lines
		#	-	if does not occurs (="EOB" of feed lines) then
		#		-	rewinds back to feed line "n+1"
		#		-	goes to EExtraction Item "N+2"
		#
		bRepeat 		= True
		sNextEExtractionShift  = "MISSING"

	
		while bRepeat:
		
			if me.reportingFinished()
				return "FINISH"
			
			if me.oFeeding.isState("stProceed")
				sFeedLine = me.oFeedSource.getStoreNextLine()
			if me.oEExtracting.isState("stProceed")
				dEExtractor = me.oEExtractorConf.getNextInAoD()
			sMatchRole 		= me.tryPerformSingleEExtractor(sFeedLine, dEExtractor)
			if sMatchRole == "NOT_MATCH":
				if me.isNowExtrShiftType("OFFSET")  "offset match failed"
					return "FINISH"
			else:
				sNextEExtractionShift = me.oEExtractorConf.getValInNowD("NextShift")
				me.setNowExtrShiftType(sNextEExtractionShift)
				if isIntStr(sNextEExtractionShift):
					nOffsetPos = str(sNextEExtractionShift)
					sFeedLine = me.oFeedSource.goRelPosGetLinenOffsetPos()
					me.oFeeding.setState("stStay")
					me.oEExtracting.setState("stStay")
				elif sNextEExtractionShift == "NEXT":
					me.oEExtracting.setState("stStay")
				elif sNextEExtractionShift == "END"
					me.finishReporting()
				else:
			
			
			if me.oFeeding.setState("stStay"):
				if me.oEExtracting.setState("stStay"):
					break # fixed position match done, so end whether passed or failed
			
			
			

			
			
				if sFeedLine == "EOB":
					if me.oEExtractorConf.alreadyUsedLastInAoD()
						bRepeat = False  # both feed lines and eExtraction items are all used
						break
			
			
			
			
			
			if me.oFeeding.isState("stProceed")
			sMatchRole 		= me.tryPerformSingleEExtractor(sFeedLine, oNextDict)
			if oFeeding.isState("stProceed"):
				sFeedLine = me.oFeedSource.getStoreNextLine()
				
			
			
			sNextEExtractionShift = me.oEExtractorConf.getValInNowD("NextShift") # key string must be equal to that in eExtraction JSON
			# D in eExtraction configuration AoD contains:
			# -		actual eExtraction item (parsing regex and capture keys)
			# - 	constant data (eg. Graphviz node attributes)
			# -		control data (shift tags)
			if sNextEExtractionShift == "END":
				bRepeat = False  # both feed lines and eExtraction items are all used
				break
			if oFeeding.isState("stProceed")
				sLine = me.oFeedSource.getStoreNextLine()
				if sLine == "EOB":
					if me.oEExtractorConf.alreadyUsedLastInAoD()
						bRepeat = False  # both feed lines and eExtraction items are all used
						break
			if oEExtracting.isState("stProceed"):
				dEExtractor = me.oEExtractorConf.getNextInAoD()			
				if me.oEExtractorConf.alreadyUsedLastInAoD()
					me.oEExtractorConf.rewindAoD()
					dEExtractor = me.oEExtractorConf.getNextInAoD()

			elif sNextEExtractionShift == "NEXT":
				if oEExtracting.getState("stStay"):
					dEExtractor = me.oEExtractorConf.getNextInAoD()
				oEExtracting.setState("stStay")
				oFeeding.setState("stProceed")
				

			
			
			
				else: # still feed lines to be processed
					if me.oEExtractorConf.alreadyUsedLastInAoD()
						if sNextEExtractionShift == "END":
							# if 'incremental search, then terminates here 
							# else rewinds eExtraction item
							bRepeat = False 
							break
					else:  
						if 
						me.oEExtractorConf.rewindAoD()	
				# TBD; if last feed line was handled and latest eExtraction item is the last one, then terminates the application
			else: # current feed line is kept, so next eExtract item is used 
				abc=123  
						dEExtractor = me.oEExtractorConf.getNextInAoD()
				sLine = oFeed.getStoreNextLine()
				me.tryPerformSingleEExtractor(sLine, dEExtractor)
		dEExtractor = me.oEExtractorConf.getNextInAoD()
		
			me.tryPerformSingleEExtractor(sLine, dEExtractor):
	
		
		
		
		# bEExtractionOngoing = True
		# sFeedLine = me.oFeedSource.getStoreNextLine()
		# if sFeedLine == "EOB":
			# return "EOB" # shall cause termination in main script
		# while bEExtractionOngoing:
			# oNextDict = me.oEExtractor.getNextDictInArray()
			# if oNextDict:
				# sMatchRole 		= me.tryPerformSingleEExtractor(sLine, oNextDict)
				# sMatchingStep = me.getNextMatchingStep()
				# if isIntStr(sMatchingStep):
				# elif sMatchingStep == "NEXT":
				# else:
				
				
			# else:
				# me.oEExtractor.rewindAoD()
				# continue
				
				
		
	
		return sMatchRole






