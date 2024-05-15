
import os, sys
import os.path
import re
import json
import time
import datetime
import pickle
import copy 

# sys.path has been already updated by the utilizer of these LIB files
# "Mappings" changed to "Transforcomms"
# "Store..." changed to "Report..."
#print ("\n=========="+str(sys.path)+"===========================")

from TextStorageUtils import *
from StateUtils import *
# import StringUtils 
from TrickUtils import *
from TextItemUtils import *





# TBD: add "Role" for LABEL (= sidestep without additional "tap" node, just edge from latest node)
# this file shall be used with "TextStorageUtils.py", so it is edited simpler than the "ReportUtils.py"
# - no <start collect> and <end collect> roles or <array> tags

class clReporting(clTextItems):  # !: inheritance: https://docs.python.org/2/tutorial/classes.html

	#=========================================================
	def __init__(me, sDuty, oTrace):  # python constructor
	#=========================================================
		me.oTrace 						= oTrace
		me.oTrace.INFO("constructor: '"+sDuty+"'","kick")
		me.sDuty 						= sDuty

		clTextItems.__init__(me, sDuty, oTrace)
		me.dTrapsByExtraction    		= {}
		me.dTrapsByExtractionPrev    	= {}			# for template filling usage
		me.dLabeledTrapsCollection		= {}  			# updated by single or multiple extractions
		me.aoExtractors 				= []   			# list of all extractor objects based on configuration items
		me.oNowExtractor				= []			# current focus extractor
		me.oTemplates					= 0
		me.oRwdConf						= 0
		me.nExtrItemPos					= -1
		me.nExtrItemLastPos				= 0
		me.bRequestBeyondLastExtr 		= False

		me.sMatchStatusLatest			= "NOT_MATCH"
		
		me.sLatestSymbolifiedName 			= "MISSING"  # updated by template filling operation (can be activity, state, or service)
		me.sNodeContextNameNow				= "MISSING"  # eg. Graphviz "cluster" name TBD: take in use
		me.sNodeContextNamePrev 			= "MISSING"  # eg. Graphviz "cluster" name TBD: take in use
		me.dNodeContextByNodeName			= {}   # TBD: take in use
		
		# DIRECTIVES ===================================================================

		me.sFeedShiftNowWhenMatch 	= "MISSING"  	
		me.sFeedShiftNowWhenFail 	= "MISSING" 	
		me.sExtrShiftNowWhenMatch 	= "MISSING"  	
		me.sExtrShiftNowWhenFail 	= "MISSING"  	
		me.sCmdOperWhenMatch		= "MISSING"  
		me.sCmdOperWhenFail			= "MISSING" 
		
		me.sFeedShiftWhenLastExtrPos = "MISSING"
		me.sExtrShiftWhenLastExtrPos= "MISSING"
		
		me.sINITIAL_FEED_SHIFT		= "MISSING"  	
		me.sINITIAL_EXTR_SHIFT		= "MISSING" 	
		me.sINITIAL_CMD_OPER		= "MISSING" 	
		
		# =====================================================================
		me.sProperFeedLine				= "MISSING"
		me.oFocusExtrItem				= 0
		me.nLoopRepetitionCounter 		= 0
		me.sMatchRolePrevForReporting	= "MISSING"  # used when distillment session is ended
		me.sMatchRoleNowForReporting	= "MISSING"  # used when distillment session is ended
		# all extractor objects are assigned to an array
		
		me.CollectionMode = "NONE"
		me.CollectionStarted = False
		
		#me.sScanDetectionMode 	= "USE_ALL" # TBD: replaced with clState
		#me.bScanningIsStarted = False	# TBD: replaced with clState
		me.resetToDefaultDirectives("by constructor")
		me.oDistilling 					= clState("distillment session", me.oTrace)
		#clTextStore.__init__(me, me.sDuty, me.oTrace)  # !: initializing parent class
		
		
	# >> called only when conf-to-extractor -data contains corresponding definitions
	
	#===================================================================
	def updateDirectivesIfChanged (me,sFeedMatch, sFeedFail, sExtrMatch, sExtrFail, sCmdWhenMatch, sCmdWhenFail):
	#===================================================================
	# data is updated by cfg-to-extractor data
	# if some data hereb is "MISSING", previous definition stays in use
		if sFeedMatch != "MISSING":
			me.sFeedShiftNowWhenMatch 	= sFeedMatch
		if sFeedFail != "MISSING":
			me.sFeedShiftNowWhenFail 	= sFeedFail
		if sExtrMatch != "MISSING":
			me.sExtrShiftNowWhenMatch 	= sExtrMatch
		if sExtrFail != "MISSING":
			me.sExtrShiftNowWhenFail 	= sExtrFail
		if sCmdWhenMatch != "MISSING":
			me.sCmdOperWhenMatch 		= sCmdWhenMatch
		if sCmdWhenFail != "MISSING":
			me.sCmdOperWhenFail 		= sCmdWhenFail
		#! IDEA: tag strings #1,#2, #3,... into trace texts: ---> concice grep results
		me.oTrace.INFO("directives by cfg: feed.match: "+str(sFeedMatch)+"/ feed.fail: "+str(sFeedFail)+"/ extr.match: "+str(sExtrMatch)+"/ extr.fail: "+str(sExtrFail)+"/ cmd.match: "+str(sCmdWhenMatch)+"/ cmd.fail: "+str(sCmdWhenFail),"kick")
		me.oTrace.INFO("directives in use to: feed.match: "+me.sFeedShiftNowWhenMatch+"/ feed.fail: "+me.sFeedShiftNowWhenFail+"/ extr.match: "+me.sExtrShiftNowWhenMatch+"/ extr.fail: "+me.sExtrShiftNowWhenFail+"/ cmd.match: "+me.sCmdOperWhenMatch+"/ cmd.fail: "+me.sCmdOperWhenFail,"kick")
	
	#===================================================================
	def resetToDefaultDirectives(me, sComment):
	#===================================================================
		me.sFeedShiftNowWhenMatch 		= "NEXT"  	# default initialization
		me.sFeedShiftNowWhenFail 		= "KEEP" 	# default initialization
		me.sExtrShiftNowWhenMatch 		= "FIRST"  	# default initialization
		me.sExtrShiftNowWhenFail 		= "NEXT"  	# default initialization
		me.sCmdOperWhenMatch			= "REPORT"  # default initialization
		me.sCmdOperWhenFail				= "CONTINUE"  # default initialization
		me.sFeedShiftWhenLastExtrPos 	= "KEEP"
		me.sExtrShiftWhenLastExtrPos	= "FIRST"
		me.sINITIAL_FEED_SHIFT			= "FIRST"  	# initialzation for very first matching attempt
		me.sINITIAL_EXTR_SHIFT			= "FIRST" 	# initialzation for very first matching attempt
		me.sINITIAL_CMD_OPER			= "REPORT" 	# initialzation for very first matching attempt
	
	#===================================================================
	def getExtrItemPosInfo(me):
	#===================================================================	
		sRet = str(me.nExtrItemPos)+"/"+str(me.nExtrItemLastPos)
		return sRet
		
	#===================================================================
	def wasLastExtrItem(me):
	#===================================================================
		if me.nExtrItemPos == me.nExtrItemLastPos:
			me.oTrace.INFO("extraction items was last at position: "+str(me.nExtrItemPos))
			return True
		else:
			return False

	#===================================================================
	def setNowExtractor(me, oExtractor):  # use e.g. to ignore "NOTE" roled symbol when setting latest symbol
	#===================================================================
		me.oTrace.INFO("set now extractor as item of pos "+str(me.nExtrItemPos)+" in extractors array")
		me.oNowExtractor = oExtractor
	#===================================================================
	def getNowExtractorRole(me):  # use e.g. to ignore "NOTE" roled symbol when setting latest symbol
	#===================================================================	
		sRetRole = "MISSING"    
		if me.oNowExtractor:
			sRetRole = me.oNowExtractor.getMatchRole()
		me.oTrace.INFO("extractor role = '"+sRetRole+"'","kick")
		return sRetRole
			
	
	#===================================================================
	def getNextFeedShift(me):
	#===================================================================
		sRet = "MISSING"
		if me.oNowExtractor:
			if me.oNowExtractor.getMatchStatus() == True:  # tries to call method of non-existing object TBD: FIX
				sRet = me.sFeedShiftNowWhenMatch
			else:
				sRet = me.sFeedShiftNowWhenFail
			me.oTrace.INFO("#1 feed shift used next: '"+sRet+"'")
		else: # no extractor object created yet
			#sRet = me.sINITIAL_FEED_SHIFT
			sRet = "NEXT"
			me.oTrace.INFO("#1 extractor object '"+me.getExtrItemPosInfo()  +"' undefined, so feed shift is set to '"+sRet+"'")

		return sRet
			
	#===================================================================
	def getNextExtrShift(me):
	#===================================================================
		sRet = "MISSING"
		if me.oNowExtractor:
			if me.oNowExtractor.getMatchStatus() == True:  
				sRet = me.sExtrShiftNowWhenMatch
			else:
				sRet = me.sExtrShiftNowWhenFail
			me.oTrace.INFO("#1 extr shift used next: '"+sRet+"'")
		else:  # no extractor object created yet
			sRet = me.sINITIAL_EXTR_SHIFT
			#sRet = "NEXT"
			me.oTrace.INFO("#1 extractor object '" + me.getExtrItemPosInfo() + "' undefined, so feed shift is set to '" + sRet + "'")

		return sRet
		
	#===================================================================
	def checkIfReportingNeeded(me):
	#===================================================================
		sRet = "MISSING"
		if me.oNowExtractor:
			if me.oNowExtractor.getMatchStatus():  # TBD: change call to Extractor object
				sRet = me.sCmdOperWhenMatch
			else:
				sRet = me.sCmdOperWhenFail
		else:
			sRet = me.sINITIAL_CMD_OPER
		me.oTrace.INFO("sets value to '"+sRet+"'")
		return sRet
		
	#=========================================================
	def ifRepetitionWatchdogExceeds(me, nMaxCount):  
	#=========================================================
		me.nLoopRepetitionCounter += 1
			#-------- TERMINATION CHECK -----------
		if me.nLoopRepetitionCounter > nMaxCount:
			me.oTrace.INFO("loop watchdog counter exceeded '"+str(me.nLoopRepetitionCounter)+"'")
			return True
		else:
			False
			
	#=========================================================
	def repetitionWatchdogReset(me):  
	#=========================================================
		me.nLoopRepetitionCounter =0

	#=========================================================
	def assignFeeding(me, oFeedSource):  
	#=========================================================
		me.oTrace.INFO("part of initialization")
		me.oFeedSource = oFeedSource
		me.sFocusFeedLine = me.oFeedSource.goStartGetLine()  # initialization for first extraction attempt

	#=========================================================
	def assignTemplatesConfByJson(me, oTemplatesByCfg):
	#=========================================================
		me.oTrace.INFO("part of initialization")
		me.oTemplates = oTemplatesByCfg


		
	#=========================================================
	def getTemplateByState(me, sProcState):
	#=========================================================
		asTemplates =  me.oTemplates.getArrayInDoA(sProcState)

		me.oTrace.INFO("fetches template items for state "+sProcState,"topic")
		return asTemplates
		
	#=========================================================
	def getFocusFeedLineByShift(me):  
	#=========================================================
		me.oTrace.INFO("...")
		sShiftType = me.getNextFeedShift()


		sFeedLine = "MISSING" # initial quess: will fail
		bStatus = True
		if sShiftType == "FIRST":
			sFeedLine = me.oFeedSource.goStartGetLine()
		elif sShiftType == "NEXT":
			sFeedLine = me.oFeedSource.getStoreNextLine()
		elif sShiftType ==  "KEEP":
			if me.wasLastExtrItem():
				sFeedLine = me.oFeedSource.getStoreNextLine()
			else:
				sFeedLine = me.oFeedSource.getStoreSameLineAgain()
		elif isIntStr(sShiftType):
			nOffsetPos = str(sShiftType)
			sFeedLine = me.oFeedSource.goRelPosGetLine(nOffsetPos)
		else:
			bStatus = False
			
		if bStatus == True:
			abc = 123
			#me.oTrace.INFO("got shift type '"+str(sShiftType)+"'")
		else:
			me.oTrace.INFO("error: unknown shift type '"+str(sShiftType)+"'")
		return sFeedLine
		
	#=========================================================
	def getFocusExtrItemByShift(me):  
	#=========================================================
	
		sShiftType = me.getNextExtrShift()
		#sShiftType = me.sExtrShiftNow
		oExtractor = 0 # initial quess: will fail
		me.oTrace.INFO("shift type = '"+str(sShiftType)+"'")
		bStatus = True
		if sShiftType == "FIRST":
			oExtractor = me.getFirstExtrItem()
		elif sShiftType == "NEXT":
			if me.wasLastExtrItem():
				oExtractor = me.getFirstExtrItem()
			else:
				oExtractor = me.getNextExtrItem()
		elif sShiftType ==  "KEEP": 
			oExtractor = me.getAgainSameExtrItem()
		elif isIntStr(sShiftType):
			nOffsetPos = str(sShiftType)
			oExtractor = me.getExtrItemByPos(nOffsetPos + me.nExtrItemPos)
		else:
			me.oTrace.INFO("error: unknown shift type")

		return oExtractor

				

	# #=========================================================
	# def setFocusFeedLine():  
	# #=========================================================
	# # TBD: add here logic for 'first', 'next',...
		# me.sFocusFeedLine
	
	# #=========================================================
	# def setFocusExtrItem():  
	# #=========================================================
	# # TBD: add here logic for 'first', 'next',...
	
	
	#=========================================================
	def assignExtractConfByJson(me, oExtrConfByJson):
	#=========================================================
		me.oTrace.INFO("=== creates extractor objects", "topic")
		bLooping = True
	
		sExtractorObjectsCount = "0"
		me.bRequestBeyondLastExtractor = False
		sPos = "MISSING"
	
		me.oExtractorConf = oExtrConfByJson
		AoD = me.oExtractorConf.getXoYroot()   # whole data structure is just "Array of Directorios"
		me.oExtractorConf.createNamedArray("extractors_", AoD)
		me.adExtractorsByCfg = me.oExtractorConf.getWholeNamedArray("extractors_")

		try:
			for dItem in me.adExtractorsByCfg:   #
				me.nExtrItemPos += 1    # initially -1
				sPos = str(me.nExtrItemPos)
				oExtractor = clExtractor("extractor item created to array pos'" + sPos + "'", me.oTrace)
				# oExtractor.createConfByAoD(dItem)
				oExtractor.createConfByAoDD(dItem)
				me.oTrace.INFO("assign extractor object to position " + sPos)
				# me.aoExtractors[me.nExtrItemPos] = oExtractor # !: P	thon: not possible to navigate in empty array
				me.aoExtractors.append(oExtractor)  # array of objects to store configuration status and data originaaly
			me.nExtrItemLastPos = me.nExtrItemPos # - 1
			me.oTrace.INFO("extractor items ended at pos " + str(me.nExtrItemLastPos))
			sExtractorObjectsCount = str(me.nExtrItemLastPos+1)
		except:
			exctype, value = sys.exc_info()[:2]
			errorText = str(exctype) + " " + str(value)
			me.oTrace.INFO(errorText,"exception")

		#me.resetNowExtractorPos()
		me.oTrace.INFO("--- '" + sExtractorObjectsCount + "' extractor objects created", "topic")

		me.setNowExtractor(me.getFirstExtrItem())  # initialization for first extraction attempt
	#=========================================================
	def getExtrItemByPos(me, nPos):  
	#=========================================================
		if nPos > me.nExtrItemLastPos:
			me.oTrace.INFO("error: trying to get item at pos '"+str(nPos)+"', but last pos is '"+str(me.nExtrItemLastPos)+"'")
			me.bRequestBeyondLastExtractor = True
			return 0
		else:
			oExtractor = me.aoExtractors[nPos]
		return oExtractor

	#=========================================================
	def getFirstExtrItem(me):  
	#=========================================================
		me.nExtrItemPos = 0
		oExtractor = 0
		me.bRequestBeyondLastExtractor = False
		try:
			oExtractor = me.aoExtractors[me.nExtrItemPos]
		except: 
			me.oTrace.INFO("no extractor at pos","exception") 
			
		return oExtractor
		
	#=========================================================
	def getAgainSameExtrItem(me):  
	#=========================================================
		oExtractor = me.aoExtractors[me.nExtrItemPos]
		return oExtractor
			
	#=========================================================
	def focusExtrRequestBeyondLast(me):   # TBD: better name
	#=========================================================
		return me.bRequestBeyondLastExtractor
	
	#=========================================================
	def getNextExtrItem(me):  
	#=========================================================
		me.nExtrItemPos += 1
		if me.nExtrItemPos > me.nExtrItemLastPos:
			me.bRequestBeyondLastExtractor = True
			me.oTrace.INFO("error: trying to get item at pos '"+str(me.nExtrItemPos)+"', but last pos is '"+str(me.nExtrItemLastPos)+"'")
			return 0
		else:
			me.oTrace.INFO("#1 uses extractor item at pos "+str(me.nExtrItemPos))
			oExtractor = me.aoExtractors[me.nExtrItemPos]
		return oExtractor
 		
	#=========================================================
	def assignRewordingByConfJson(me, oRwdConf):
	#=========================================================	
		me.oRwdConf = oRwdConf

	#=========================================================
	def doesExist(me, sKey):   # caught or saved
	#=========================================================	
		sVal = me.dLabeledTrapsCollection.get(sKey,"MISSING")
		if sVal == "MISSING":
			sVal = me.dSavesValues.get(sKey,"MISSING")
		if sVal != "MISSING":
			return True
		else:
			return False

	#=========================================================
	def finishReporting(me):  
	#=========================================================
		me.bFinishReporting = True
		
	#=========================================================
	def reportingFinished(me):  
	#=========================================================
		return me.bFinishReporting
	
	#=========================================================
	def setMatchRoleNowForReporting(me, sType):  # for initialization
	#=========================================================
		me.oTrace.INFO("set now match type to '"+sType+"'")
		me.sMatchRoleNowForReporting = sType
		
	#=========================================================
	def getMatchRoleNowForReporting(me):  # for  saving eg."NodeName" to "NodeNamePrev" for template filling access
	#=========================================================
		return me.sMatchRoleNowForReporting 		
		
	#=========================================================
	def setMatchRolePrevForReporting(me, sType):  # for initialization
	#=========================================================
		me.oTrace.INFO("set previous match type to '"+sType+"'")
		me.sMatchRolePrevForReporting = sType
			
	#=========================================================
	def getMatchRolePrevForReporting(me):  # for  saving eg."NodeName" to "NodeNamePrev" for template filling access
	#=========================================================
		return me.sMatchRolePrevForReporting

	#=========================================================
	def traceSigleFeedLineActualizedExtractionResultInfo(me,sFeedLine, dTrapsByExtraction):
	#=========================================================
		sSingleFeedLineExtractionTrapsDictAsStr = anyDictToStr(dTrapsByExtraction)
		sCollectedExtractionTrapsDictAsStr = anyDictToStr(me.dLabeledTrapsCollection)

		me.oTrace.INFO("feed line '" + sFeedLine + "' trapped","topic")
		me.oTrace.INFO("extracted traps: "+sSingleFeedLineExtractionTrapsDictAsStr)
		me.oTrace.INFO("all collected traps: " + sCollectedExtractionTrapsDictAsStr)

	#=========================================================	
	def appendTrapsToCollection(me, dTrapsByExtraction):
	#=========================================================
		me.dLabeledTrapsCollection.update(dTrapsByExtraction) # !: python dictionaries "append"
	
	#=========================================================	
	def clearTrapsCollection(me):
	#=========================================================
		me.dLabeledTrapsCollection = {}
	
	#=========================================================	
	def setCommandByExtractionSuccess(me):
	#=========================================================
		bStatus = me.oNowExtractor.getMatchStatus()
		if bStatus == True:
			sCommand = me.sCmdOperWhenMatch
		else:
			sCommand = me.sCmdOperWhenFail
			
		me.oStDistill.setState(sCommand)
		

	#=========================================================
	def getNextDistillment(me):
	#=========================================================
		# from now on, preprocessing handles following cases
		# 	-	<START> and <END> criteria by <FILTER> or <EDIT>
		#	-	multiple lines flattening by <EDIT>
		#TBD: add clState object usage here to increase needed complexity
		#sResultCommand 	= "CONTINUE"
		# feed file is not edited here in <EXTRACT>: it must be done before in <FILTER> or <EDIT>
		bRepeat 		= True
		sSingleKey 		= ""
		sResultCommand 	= ""

		 # some object within extractor array
	
		me.nLoopRepetitionCounter 	= 0

		me.oStExtrStatus = clState("for extraction success", me.oTrace)
		me.oStExtrStatus.setState("SUCCESS")
		
		me.oStDistill = clState("for extraction/reporting sync", me.oTrace)
		me.oStDistill.setState("CONTINUE")
		
		me.oStScan = clState("for processing", me.oTrace)
		me.oStScan.setState("USE_ALL") # intial quess: <start log> extractor is not assemed to exist
		
		me.oStCollect = clState("for lines grouping", me.oTrace)
		me.oStCollect.setState("NONE")
		
		sPile = "" # a string joined from sequential lines
		while bRepeat:
			# program execution runs in this loop until <REPORT> or <FINISH> is returned
			# - if <REPORT> is returned, 
			#		-	the main script will call this function again
			# 		-	the main script shall call <extractor>::<result command()>  to control report formation
			if me.ifRepetitionWatchdogExceeds(p_nLOOP_COUNT_MAX):
				sResultCommand = "FINISH"
				break
			#---------- FEED -------------------------
			sFeedLine = me.getFocusFeedLineByShift()

			# TBD: add check of start/stop scanning
			if sFeedLine == "EOB":
				sResultCommand = "FINISH"
				break
			#--------- EXTRACTORS -------------------------
			me.setNowExtractor(me.getFocusExtrItemByShift())
			if me.oNowExtractor == 0:
				sResultCommand = "FINISH"
				break
			sRegex = me.oNowExtractor.getMatchRegex()
			#sTraps = me.oNowExtractor.getTraps()
			sNowRole = me.oNowExtractor.getMatchRole()
			#me.oTrace.INFO("role/regex/traps = "+ sNowRole +"/"+ sRegex + "/" + sTraps)
			# -	gets extractor object based on data from previous extraction attempt

			sExtrItemPosInfo 	= me.getExtrItemPosInfo()
			sFeedLinePosInfo	= me.oFeedSource.getMainBufferPosInfo()
			me.oTrace.INFO("tries to extract feed line '"+sFeedLine +"' "+ sFeedLinePosInfo+", regex '"+sRegex+"' "+sExtrItemPosInfo)
			# TBD: add feature: if trap symbol prefix is "@" instead of "$", multiple catches are assumed to be saved from single line 
			try:
				# ----- me.dTrapsByExtraction = me.oNowExtractor.tryExtractByCfgAoD(sFeedLine) # TBD: replace with trap template filler
				me.dTrapsByExtraction = me.oNowExtractor.tryExtractByCfgAoDD(sFeedLine)

				if bool(me.dTrapsByExtraction):
					#me.oTrace.INFO("made extractions at feed line '" + sFeedLine + "'","topic")
					#-------------------------------------------------------
					# TBD: add handling of roles, which manipulate the feed data (to be caught later by other extractor blocks"
					me.appendTrapsToCollection(me.dTrapsByExtraction)
					me.appendTrapsToCollection(me.dTrapsByExtractionPrev)
					dAttrib = me.oNowExtractor.getAttribDict()
					me.appendTrapsToCollection(dAttrib)
					me.traceSigleFeedLineActualizedExtractionResultInfo(sFeedLine, me.dTrapsByExtraction)
				else:
					me.oTrace.INFO("no extractions at feed line '"+sFeedLine+"'","topic")
					me.oStExtrStatus.setState("FAILED")
					me.oStDistill.setState("SKIP_REPORT")
				
					#---------------------------------------------------------
			except:
				me.oTrace.INFO(sFeedLine,"exception")
				return "FINISH"
				
			#------------------------------------------------------------
			
			sFeedMatch, sFeedFail, sExtrMatch, sExtrFail, sReportingPass, sReportingFail = me.oNowExtractor.getDirectivesByCfg()
			me.updateDirectivesIfChanged(sFeedMatch, sFeedFail, sExtrMatch, sExtrFail, sReportingPass, sReportingFail)

			# data for tracing purposes
			#me.saveNextFeedShift() # by extraction pass/fail
			#me.saveNextExtrShift() # by extraction pass/fail
			#me.oTrace.INFO("feed.shift/extr.shift/result.state = "+me.sFocusFeedShift+"/"+me.sFocusExtrShift+"/"+me.oNowExtractor.getResultCommand())
			#me.oTrace.INFO("passed phase "+str(me.nLoopRepetitionCounter)+", distillment continues")
			if me.oStExtrStatus.isState("SUCCESS"):
				me.setMatchRoleNowForReporting(me.oNowExtractor.getMatchRole())
				me.setCommandByExtractionSuccess()
				#sResultCommand =  me.oNowExtractor.getResultCommand()

				
			sResultCommand = me.oStDistill.getState()
			
			me.oTrace.INFO("result command: "+sResultCommand,"topic")
			if sResultCommand 	== "REPORT":
				break
			elif sResultCommand == "SKIP_REPORT":
				break
			elif sResultCommand == "FINISH":
				break
			elif sResultCommand == "MISSING":
				me.oTrace.INFO("INVALID result command is '"+sResultCommand+"' so execution will terminate")
				sResultCommand 	= "FINISH"
				break
			else: # continues looping
				abc = 123
				
		me.oTrace.INFO("distillment ended after '"+str(me.nLoopRepetitionCounter)+ "' loopings")
		return sResultCommand
		
	#===============================================================================
	def  getFilledTemplateItems(me, asTemplates):   # tags are keys to values ---> single line will be generated
	#===============================================================================
		# TBD: keep  this method here
		asFilledTemplateItems 	= []
		sFilledTemplate 	= ""
		dRewording 			= {}
		# TBD: ??? me.dTplTagFrames.clear()  # removes previus execution data
		s_REJECTION_INDICATION_PREFIX = "// "
	
		sTplTagCatchRe = me.getParam(p_kSCALAR_TAG_CATCH) # to match every tag within a template   # defined in main script
		# sConditionBlockCatchRe = me.getParam(p_kCOND_BLOCK_CATCH) # TBD: continue... 180928

	#   - tag prefix shall be "$" here
		# TBD: add <ARRAY TAG CATCH> regex usage ???
		# - http://stackoverflow.com/questions/369898/difference-between-dict-clear-and-assigning-in-python
		sItemStatus = ""# initial quess
		
		if me.oRwdConf != 0:
			dRewording = me.oRwdConf.getWholeDict()
			me.oTrace.INFO("rewording configuration is in use")
		else:
			dRewording = 0
			# me.oTrace.INFO("rewording configuration is NOT in use")

		me.oTrace.INFO("-----------------------------------------------","topic")
		for sTemplate in asTemplates:
			# me.oTrace.INFO("#1 ----------------------------------")
			#me.oTrace.INFO("fill template '"+sTemplate+"' with dictionary '"+str(me.dLabeledTrapsCollection)+"'")
			###sFilledTemplate, bStatus = me.getFilledTemplateItem(sTemplate)
			sItemStatus, sLatestSymbolifiedName, sFilledTemplate = me.fillAndOrEvaluateTemplateItem(me.dLabeledTrapsCollection, sTemplate,  sTplTagCatchRe, dRewording)
			
			sLatestRole = me.getNowExtractorRole()
			if sLatestRole != "NOTE":   # TBD: see, if this is necessary
				if sLatestSymbolifiedName != "MISSING":  # TBD: find out reason for that value
					me.sLatestSymbolifiedName = sLatestSymbolifiedName
				me.oTrace.INFO("latest.symbolified.name = '"+me.sLatestSymbolifiedName+"'","kick")
				# - lowest level template filler function is not any class member, so it can be called even from simple applications
				me.dLabeledTrapsCollection["AnyLatestNode"] = me.sLatestSymbolifiedName  # can be used to add comment node to any type node
				# TBD: configure extractor JSON to join note box to that node 170210
			else:
				me.oTrace.INFO("extractor role is '"+sLatestRole+"' , so latest node is not updated")
			
			if sItemStatus == "stsAcceptItem":
				asFilledTemplateItems.append(sFilledTemplate)
			elif sItemStatus == "stsRejectItem":
				asFilledTemplateItems.append(s_REJECTION_INDICATION_PREFIX+sFilledTemplate) # initially hard-coded commenting: TBD: make prefix and postfix configurable
				me.oTrace.INFO("inadequately filled template '" + sFilledTemplate + "'")
			elif sItemStatus == "stsRejectRemainingItems":
				break
			else:
				me.oTrace.INFO("unknown status "+sItemStatus+" when filling template '"+sFilledTemplate+"'")
		me.dTrapsByExtractionPrev = me.copyDictByKeyNamePostfixes(me.dTrapsByExtraction, "."+p_sPREV_TAG_REF_DIRECTIVE)

		for sItem in asFilledTemplateItems:
			me.oTrace.INFO("filled template item: '"+sItem +"'","topic")

		return asFilledTemplateItems


# TBD: JSON configuration file usage for feed file data manipulation
#	-	start, end, <edit feed> etc. removed from actual <extractor> JSON/extractor


sARRAY_TAG_re = "\@\\w+"  # already defined in main script TBD: remove this redundancy


class clExtractor(clTextItems):
	# ReportUtils generates an array of objects of this class
	# TBD: transfer this kind of functionlity to <ConfigUtils> (171117)
	# ===================================================================
	def __init__(me, sDuty, oTrace):
	# ===========================================================
		me.oTrace = oTrace
		me.oTrace.INFO("constructor " + sDuty,"kick")
		me.dActorsByCfg = {}  # catcher regex and trap labels
		me.dAttribByCfg = {}  # ready data for reports eg. graphviz node attributes
		me.dDirectivesByCfg = {}  # ready control data which is selected according to catch pass/fail
		me.dTrapsByPos = {}  # auto-named storages from results of single regex-catch-save attempt
		me.dOnceTrapsByLabels = {}  # final, labeled storage of single regex-catch result
		me.bConfigurationUpdated = False
		me.sDuty = sDuty
		me.sNextFeedShift = "MISSING"
		me.sNextExtrShift = "MISSING"
		me.sStateNext = "MISSING"
		
		me.sMatchStatusLatest = "NOT_MATCH"
		# me.bLatestExtrType = False
		
		oTrace.INFO("constructor; creates extractor for '" + me.sDuty + "'","kick")
		
		clTextItems.__init__(me, me.sDuty, oTrace)
	
	# ===================================================================
	def createConfByAoD(me, dSingleExtractConf):  # one for each "D" in JSON "AoD"
	# ===================================================================
		# saves extraction configuration (from JSON) block for any extraction trial pass/fail - purposes
		# each configuration block does not need to contain all (eg. navigation) metadata. in that case previous metadata is used
		# TBD: refractoring to functions (to simplify these)
		# saves metadata to object variables
		# uses previous object-saved values, if new ones are not defined in JSON file
		''''''''' EXAMPLE: type: "AoD"
			[
				{"Match": "(^\\sTBD: regex here.*$)",
				 "Role": "COLLECT",
				 "Traps": "TheCollection"},
				{"Match": "^\\s*(=.*$)",
				 "Role": "NOTE",
				 "Traps": "$NoteNode",
				 "EntryEdgeAttr": "none",
				 "NoteNodeEntryEdgeAttr": "style=dotted",
				 "NoteNodeAttr": ", shape=note, style=filled, fillcolor=red"},
				{"Match": "^\\s*set\\s+state\\s+(\\w+)\\s*$",
			]	
			


		'''''
		# ======================================================================================================================
		
		
		sMatch = dSingleExtractConf.get("Match", "MISSING")  # required
		sTraps = dSingleExtractConf.get("Traps", "MISSING")  # required
		sRole = dSingleExtractConf.get("Role", "MISSING")
		
		me.dActorsByCfg["Match"] = sMatch  # required
		me.dActorsByCfg["Traps"] = sTraps  # required
		
		me.oTrace.INFO("saved extractor for configuration: role/match/trap = " + sRole + "/" + sMatch + "/" + sTraps)
		# ======================================================================================================================
		
		# optional (default
		me.dDirectivesByCfg["Role"] = sRole
		me.dDirectivesByCfg["FeedShiftWhenMatch"] = dSingleExtractConf.get("FeedShiftWhenMatch",
																		   "MISSING")  # optional (default shift: next when match or Extrs ended)
		me.dDirectivesByCfg["FeedShiftWhenFail"] = dSingleExtractConf.get("FeedShiftWhenFail", "MISSING")
		me.dDirectivesByCfg["ExtrShiftWhenMatch"] = dSingleExtractConf.get("ExtrShiftWhenMatch",
																		   "MISSING")  # optional (default shift: go to first eExtraction item)
		me.dDirectivesByCfg["ExtrShiftWhenFail"] = dSingleExtractConf.get("ExtrShiftWhenFail", "MISSING")
		me.dDirectivesByCfg["CommandWhenMatch"] = dSingleExtractConf.get("CommandWhenMatch", "MISSING")
		me.dDirectivesByCfg["CommandWhenFail"] = dSingleExtractConf.get("CommandWhenFail", "MISSING")
		
		me.oTrace.INFO("saved directive configurations: " + anyDictToStr(me.dDirectivesByCfg))
		
		# ================================================================================================================
		me.oTrace.INFO("removes consumed items from input onfigurations. only attributal data is left")
		# SEE: http://stackoverflow.com/questions/15411107/delete-a-dictionary-item-if-the-key-exists
		# "reserved word" data items are already utilized and are deleted here before saving "paramemeter" data items
		dSingleExtractConf.pop("Match",
							   None)  # removes "used" item before looping to save possible other data (eg. node shape, color etc.)
		dSingleExtractConf.pop("Role", None)  # !: Python: Dictionary item access: brackets !!!
		dSingleExtractConf.pop("Traps",
							   None)  # removes "used" item before looping to save possible other data (eg. node shape, color etc.)
		dSingleExtractConf.pop("FeedShiftWhenMatch", None)  # can be deleted here, because value is already saved
		dSingleExtractConf.pop("FeedShiftWhenFail", None)  # can be deleted here, because value is already saved
		dSingleExtractConf.pop("ExtrShiftWhenMatch", None)  # can be deleted here, because value is already saved
		dSingleExtractConf.pop("ExtrShiftWhenFail", None)  # can be deleted here, because value is already saved
		dSingleExtractConf.pop("CommandWhenMatch", None)  # can be deleted here, because value is already saved
		dSingleExtractConf.pop("CommandWhenFail", None)  # can be deleted here, because value is already saved
		
		# ====================================================================================================================
		
		nAttribCnt = len(dSingleExtractConf)
		
		# me.oTrace.INFO("saves rest of configurations as '"+str(nAttribCnt) + "' attributal configurations")
		for sKey, sVal in dSingleExtractConf.items():
			me.dAttribByCfg[sKey] = sVal
		
		me.oTrace.INFO("saved attrib configurations: " + anyDictToStr(me.dAttribByCfg))
		me.oTrace.INFO("single extraction item creation done")
		
		
	#===================================================================
	def createConfByAoDD(me, dSingleExtractConf):
	#===================================================================
		# saves extraction configuration (from JSON) block for any extraction trial pass/fail - purposes
		# each configuration block does not need to contain all (eg. navigation) metadata. in that case previous metadata is used
		# TBD: refractoring to functions (to simplify these)
		# saves metadata to object variables
		# uses previous object-saved values, if new ones are not defined in JSON file

		'''''
				NEW structure "AoDD" (181111)
	
			[
				{"Match":"^\\s*(\\w+)\\s+moveto\\s+state+\\s+(\\w+)\\s+\\-\\>\\s(\\w+)\\s*$",
				"Role":"STATE",
				"Traps":{"$MotorName":"EKA $1",
					"$SourceState":"TOKA $2",
					"$TargetState":"KOLMAS $3"},
				"StateTransferEdgeAttr":"penwidth=1",
				"StateNodeAttr":" , shape=box, style=filled, fillcolor=green, fontsize=10"}
			]
		'''''
		# ======================================================================================================================
		
		
		sMatch = dSingleExtractConf.get("Match", "MISSING")  # required
		dTraps = dSingleExtractConf.get("Traps", None)  # value is a dictionary of items <trap name>:<template with default tags>
		sRole = dSingleExtractConf.get("Role", "MISSING")
		
		me.dActorsByCfg["Match"] = sMatch  # required
		me.dActorsByCfg["Traps"] = dTraps
		
		# me.oTrace.INFO("saved extractor for configuration: role/match/trap = " + sRole + "/" + sMatch + "/" + sTraps)
		# ======================================================================================================================
		
		# optional (default
		me.dDirectivesByCfg["Role"] = sRole
		me.dDirectivesByCfg["FeedShiftWhenMatch"] = dSingleExtractConf.get("FeedShiftWhenMatch",
																		   "MISSING")  # optional (default shift: next when match or Extrs ended)
		me.dDirectivesByCfg["FeedShiftWhenFail"] = dSingleExtractConf.get("FeedShiftWhenFail", "MISSING")
		me.dDirectivesByCfg["ExtrShiftWhenMatch"] = dSingleExtractConf.get("ExtrShiftWhenMatch",
																		   "MISSING")  # optional (default shift: go to first eExtraction item)
		me.dDirectivesByCfg["ExtrShiftWhenFail"] = dSingleExtractConf.get("ExtrShiftWhenFail", "MISSING")
		me.dDirectivesByCfg["CommandWhenMatch"] = dSingleExtractConf.get("CommandWhenMatch", "MISSING")
		me.dDirectivesByCfg["CommandWhenFail"] = dSingleExtractConf.get("CommandWhenFail", "MISSING")
		
		me.oTrace.INFO("saved directive configurations: " + anyDictToStr(me.dDirectivesByCfg))
		
		# ================================================================================================================
		me.oTrace.INFO("removes consumed items from input onfigurations. only attributal data is left")
		# SEE: http://stackoverflow.com/questions/15411107/delete-a-dictionary-item-if-the-key-exists
		# "reserved word" data items are already utilized and are deleted here before saving "paramemeter" data items
		dSingleExtractConf.pop("Match",
							   None)  # removes "used" item before looping to save possible other data (eg. node shape, color etc.)
		dSingleExtractConf.pop("Role", None)  # !: Python: Dictionary item access: brackets !!!
		dSingleExtractConf.pop("Traps",
							   None)  # removes "used" item before looping to save possible other data (eg. node shape, color etc.)
		dSingleExtractConf.pop("FeedShiftWhenMatch", None)  # can be deleted here, because value is already saved
		dSingleExtractConf.pop("FeedShiftWhenFail", None)  # can be deleted here, because value is already saved
		dSingleExtractConf.pop("ExtrShiftWhenMatch", None)  # can be deleted here, because value is already saved
		dSingleExtractConf.pop("ExtrShiftWhenFail", None)  # can be deleted here, because value is already saved
		dSingleExtractConf.pop("CommandWhenMatch", None)  # can be deleted here, because value is already saved
		dSingleExtractConf.pop("CommandWhenFail", None)  # can be deleted here, because value is already saved
		
		# ====================================================================================================================
		
		nAttribCnt = len(dSingleExtractConf)
		
		# me.oTrace.INFO("saves rest of configurations as '"+str(nAttribCnt) + "' attributal configurations")
		for sKey, sVal in dSingleExtractConf.items():
			me.dAttribByCfg[sKey] = sVal
		
		me.oTrace.INFO("saved attrib configurations: " + anyDictToStr(me.dAttribByCfg))
		me.oTrace.INFO("single extraction item creation done")
	
	
	#===================================================================
	def tryExtractByCfgAoDD(me, sFeedLine):
	#===================================================================
		TODO = 181109
		sMatchStatus = "NOT_CATCH"
		try:
			me.sMatchStatusLatest = sMatchStatus  # initial quess
			sMatchRegex = me.dActorsByCfg.get("Match", "MISSING")
			sMatchStatus, me.dTrapsByPos = me.tryCatchAtOnce(sFeedLine, sMatchRegex)
			if sMatchStatus == "YES_CATCH":
				# me.oTrace.INFO("regex '"+sMatchRegex+"' did match to line '"+sFeedLine+"'")
				nTrapsCount = len(me.dTrapsByPos)
				dTrapWithExtrTpl = me.dActorsByCfg.get("Traps",None) # returns "D" <key name>:<built value>
				if dTrapWithExtrTpl:
					for sKeyTrapTag, sValExtrTpl in dTrapWithExtrTpl.items(): # eg.
						for nPos in range(1,nTrapsCount+1):
							sPos = str(nPos)
							sPosTag = "$"+sPos
							sPosVal = me.dTrapsByPos.get(sPos,"no_pos_val")
							# me.oTrace.INFO("pos/key/val = "+sPos+"/"+sKeyTrapTag+"/"+sPosVal)
							sValExtrTpl = sValExtrTpl.replace(sPosTag, sPosVal)
							# me.oTrace.INFO("pos/key_trap/val_tpl: '"+sPos+"'/'"+sKeyTrapTag+"'/'"+sValExtrTpl+"' filled extraction")
						me.dOnceTrapsByLabels[sKeyTrapTag] = sValExtrTpl
				else:
					me.oTrace.INFO("no traps in extraction result template")
			else:
				me.dOnceTrapsByLabels = {}
				me.oTrace.INFO("regex '"+sMatchRegex+"' did not match to feed line '"+sFeedLine+"'")
			return me.dOnceTrapsByLabels
		except:
			me.oTrace.INFO("tried to extract", "exception")

		return 0  # no catch

	'''''
	// ---------------- example item to be handled by THIS function -----------------
	{
		"Match": "^\\s*(\\w+)\\s+moveto\\s+state+\\s+(\\w+)\\s+\\-\\>\\s(\\w+)\\s*$",
		"Role": "STATE",
		"Traps": {
			"MotorName": "MOTOR $1",  # traps can be built using atomic captures and constant strings with
			"SourceState": "STATE $2",
			"TargetState": "STATE $3"
		},
		"StateTransferEdgeAttr": "penwidth=1",
		"StateNodeAttr": " , shape=box, style=filled, fillcolor=green, fontsize=10"
	}
	'''''

	# ===================================================================
	def tryExtractByCfgAoD(me, sFeedLine):
	# ===================================================================
		# TBD: coherent names to "catch", "match", "extract" etc.
		# tries to match given feed line to current "match regex"
		#	-	 various actions are done depending on pass/fail -result
		try:
			sMatchRegex = me.dActorsByCfg.get("Match", "MISSING")
			# me.dActorsByCfg.get("Traps") TBD: add check: if some actor has "@" prefix, use "findall" to split it to scalars
			
			sMatchStatus, me.dTrapsByPos = me.tryCatchAtOnce(sFeedLine, sMatchRegex)
			# "enum" of "NOT_MATCH", "YES_CATCH" and "YES_MATCH" for "sExtrResultType" and "sExtrResultTypeLatest"
			# TBD: correct
			me.sMatchStatusLatest = sMatchStatus  # initial quess
			me.oTrace.INFO("#1 match status was: " + sMatchStatus)
			if sMatchStatus == "YES_CATCH":
				bCountMatch, me.dOnceTrapsByLabels = me.copyPosDictToLabelDict(me.dTrapsByPos,
																			   me.dActorsByCfg.get("Traps"))
				if not bCountMatch:
					me.oTrace.INFO("TBD: handle this error case")
				else:
					return me.dOnceTrapsByLabels
		except:
			me.oTrace.INFO("tried to extract", "exception")
		return 0  # no catch
	
	# ===================================================================
	def isMatchStatus(me, sRefStatus):
		# ===================================================================
		if me.sMatchStatusLatest == sRefStatus:
			return True
		else:
			return False
	
	# ===================================================================
	def getMatchStatus(me):
		# ===================================================================
		if me.sMatchStatusLatest != "NOT_MATCH":
			return True
		else:
			return False
	
	# ===================================================================
	def getAttribDict(me):
		# ===================================================================
		# this configuration is updated only in object creation phase
		return me.dAttribByCfg
	
	# ===================================================================
	def getMatchRole(me):
		# ===================================================================
		# this configuration is updated only in object creation phase
		return me.dDirectivesByCfg.get("Role", "MISSING")
	
	# ===================================================================
	def getMatchRegex(me):
		# ===================================================================
		# this configuration is updated only in object creation phase
		return me.dActorsByCfg.get("Match", "MISSING")
	
	# ===================================================================
	def getTraps(me):
		# ===================================================================
		# this configuration is updated only in object creation phase
		return me.dActorsByCfg.get("Traps", "MISSING")
	
	# ===================================================================
	def changeMatchRole(me, sNewRole):  # eg. when integer is generalized to "NOTE"
		# ===================================================================
		# this configuration is updated only in object creation phase
		me.oTrace.INFO("match role changed to ," + sNewRole + "'")
		
		me.dDirectivesByCfg["Role"] = sNewRole
	
	# ===================================================================
	def getDirectivesByCfg(me):  # TBD: remove, because is now in <report> object
		# ===================================================================
		sFeedMatch = me.dDirectivesByCfg.get("FeedShiftWhenMatch")
		sFeedFail = me.dDirectivesByCfg.get("FeedShiftWhenFail")
		sExtrMatch = me.dDirectivesByCfg.get("ExtrShiftWhenMatch")
		sExtrFail = me.dDirectivesByCfg.get("ExtrShiftWhenFail")
		sExtrMatch = me.dDirectivesByCfg.get("ExtrShiftWhenMatch")
		sExtrFail = me.dDirectivesByCfg.get("ExtrShiftWhenFail")
		sCmdWhenMatch = me.dDirectivesByCfg.get("CommandWhenMatch")
		sCmdWhenFail = me.dDirectivesByCfg.get("CommandWhenFail")
		return sFeedMatch, sFeedFail, sExtrMatch, sExtrFail, sCmdWhenMatch, sCmdWhenFail
	
	# ===================================================================
	def getResultCommand(me):
		# ===================================================================
		sRet = "MISSING"
		if me.sMatchStatusLatest != "NOT_MATCH":
			sRet = me.dDirectivesByCfg.get("CommandWhenMatch", "FINISH")
		else:
			sRet = me.dDirectivesByCfg.get("CommandWhenFail", "FINISH")
		return sRet
	
	# ===================================================================
	def ifContainsArrayCaptureTag(me):
		# ===================================================================
		# if extractor item capture tags contain array indication
		sTrapsSeq = me.dActorsByCfg["Traps"]
		if re.search(sARRAY_TAG_re, sTrapsSeq):
			return True
		else:
			return False

		
		
		

	
