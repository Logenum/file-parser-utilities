import os, sys
import os.path
import re
import time
import datetime

# sys.path has been already updated by the utilizer of these LIB files

#print ("\n========== "+str(sys.path)+"===========================")
#from TextStoreUtils import *   # TBD: freeze this "TextStoreUtils" module name for Freeplane "F1" script GUI usage.
from TextStorageUtils import *
from StateUtils import *
from TrickUtils import *

# TBD: function which parses OTL file to a "DoA" (170804)
# - every key is a topic name
# - every array contains lines within that topic
# ---> for getting data from hyperlink
# TBD: add possibility to split each topic to a separate (eg. JSON) file 170121
# !: Python, inheritance: parent object stuff is accessed by "me.", "super()." is used to access class stuff
#class clNotetab (clTextStore):  # !: inheritance: https://docs.python.org/2/tutorial/classes.html

class clNotetab(clTextStorage):  # !: inheritance: https://docs.python.org/2/tutorial/classes.html
 # class name changed to distinguish it better from module (=file) name
	#=========================================================
	def __init__(me, sDuty, oTrace, sTheseDriveLetter="N/A", sCreatorPath="N/A", sCreatorName="N/A"):  # python constructor
	#=========================================================
		me.oTrace = oTrace
		me.sDuty = sDuty




		me.dOaCreatedByContents = {}
		dOaTopicLines = {}   # keys are topic names, values are arrays of topic lines
		#clTextStore.__init__(me, me.sDuty, me.oTrace)  # !: initializing parent class
		clTextStorage.__init__(me, me.sDuty, me.oTrace)  # !: initializing parent class

	#=========================================================
	def addTextToGivenFirstTopicEnd(me, sGivenTopicName, sDelimLine, sAddText):  # if Topic is not found, it is created as first topic
	#=========================================================
		#  "aaaa bbbb 111" 	# topic name
		#TBD: add checking of possible TAGS (etc. <printout> for replacing with printout sequence number )
		sAddText = sAddText.replace(sLINE_JOINER, "\n")
		oProc = clState("text to topic", me.oTrace)
		sTopicNameLineMatchPattern = "H=\".*\""
		sNAME_PATTERN = "\".*\""
		sAddText = sDelimLine+"\n"+sAddText
		sGivenTopicNameLine = sTopicNameLineMatchPattern
		sGivenTopicNameLine = sGivenTopicNameLine.replace(sNAME_PATTERN,"\""+sGivenTopicName+"\"")
		sAddText = sAddText.replace("\"","")

		me.oTrace.INFO("sGivenTopicNameLine = '"+sGivenTopicNameLine+"'")
		me.oTrace.INFO("sTopicNameLineMatchPattern = '"+sTopicNameLineMatchPattern+"'")
		me.oTrace.INFO("sAddText = '"+sAddText+"'")

		nOverWriteLen = 0
		sCurrentState	= "stNotInitialized"
		nPrevState 		= "stNotInitialized"

		asAddBlock =[]
		sState = "stFindGivenHeading"
		nLineNbr = -1
		nInsertionPos=0
		nFocusLinePos=-1
		nLastNonEmptyLinePos = 0
		bSomeTopicFound = 0 # initial quess
		oProc.setState("stFindGivenHeading", "initialization")

		reNonEmptyLine = re.compile("^.*\S+.*$")
		reGivenTopicName = re.compile(sGivenTopicNameLine)
		reAnyTopicNameLine = re.compile(sTopicNameLineMatchPattern)

		sLine =""
		for sLine in me.asMainBuffer: #  !: accessing parent class attribute
			sState = oProc.getState()
			
			m = reAnyTopicNameLine.match(sLine)
			if m:
				me.oTrace.INFO("topic found at line ["+str(nFocusLinePos)+"] = "+sLine)
			nFocusLinePos = nFocusLinePos + 1 
			m = reNonEmptyLine.match(sLine)
			if m:
				nLastNonEmptyLinePos = nFocusLinePos
				# me.oTrace.INFO(last non-empty line at pos["+str(nFocusLinePos)+"] = '"+sLine+"'")
			if (sState == "stFindGivenHeading"):
				m = reGivenTopicName.match(sLine)
				if m:
					bSomeTopicFound = 1
					oProc.setState("stFindNextHeading", "given heading found in "+sGivenTopicNameLine)
			elif (sState == "stFindNextHeading"):
				m = reAnyTopicNameLine.match(sLine)
				if m:
					bSomeTopicFound = 1
					asAddBlock.append(sAddText)
					#asAddBlock.append("")
					nInsertionPos = nFocusLinePos - 1
					oProc.setState("stAddingDone", "given topic '"+sGivenTopicName+"' found at '"+sLine+"'")
			else:
				a=1
		#  statuses when file ended
		sState = oProc.getState()
		if (sState == "stFindGivenHeading"):
			me.oTrace.INFO("given heading was not found, so heading and text are added to file start")
			if (bSomeTopicFound == 0):
				asAddBlock.append("")   # !: empty "append()" seems to add a "\n" !!!
				nInsertionPos = 2 # just after top line and empty line
			asAddBlock.append(sGivenTopicNameLine)
			asAddBlock.append("")   # !: empty "append()" seems to add a "\n" !!!
			asAddBlock.append(sAddText)
			asAddBlock.append("")
		elif (sState == "stFindNextHeading"):  # given heading was last heading
			me.oTrace.INFO("given heading was found but next heading not found, so insert text to end of first topic")
			nInsertionPos = nLastNonEmptyLinePos+1
			asAddBlock.append(sAddText)
		else:
			a=1
		me.insertArray(asAddBlock, nInsertionPos) 	# !: a Python way to call parent class method
		
		
		
	#=========================================================
	def addTextToGivenAlphabetTopicEnd(me, sGivenTopicName, sAddText, sAddPostfix):  # if Topic is not found, it is created within alphabet order
	#=========================================================
		#  "aaaa bbbb 111" 	# topic name
		sAddText = sAddText.replace(sLINE_JOINER, "\n")
		oProc = clState("text to topic", me.oTrace)
		
		sGivenTopicNameLine = sTopicNameLineMatchPattern
		sGivenTopicNameLine = sGivenTopicNameLine.replace(sNAME_PATTERN,"\""+sGivenTopicName+"\"")
		sAddText = sAddText.replace("\"","")

		me.oTrace.INFO("sGivenTopicNameLine = '"+sGivenTopicNameLine+"'")
		me.oTrace.INFO("sTopicNameLineMatchPattern = '"+sTopicNameLineMatchPattern+"'")
		me.oTrace.INFO("sAddText = '"+sAddText+"'")
		me.oTrace.INFO("sAddPostfix = '"+sAddPostfix+"'")   # e.g. date/time -stamp
		
		sAddText = sAddText + "          " + sAddPostfix
		nOverWriteLen = 0
		sCurrentState	= "stNotInitialized"
		nPrevState 		= "stNotInitialized"
		asAddBlock =[]
		
		sState = "stFindGivenHeading"
		nLineNbr = -1
		nInsertionPos=0
		nFocusLinePos=-1
		nLastNonEmptyLinePos = 0
		bSomeTopicFound = 0 # initial quess
		oProc.setState("stFindGivenHeading", "initialization")
		sLatestTopicName = ""  # used for alphabetical comparison
		nLatestTopicNameLinePos = 0  # will be used for add text insertion base in certain cases

		reNonEmptyLine = re.compile("^.*\S+.*$")
		reGivenTopicName = re.compile(sGivenTopicNameLine)
		reAnyTopicNameLine = re.compile(sTopicNameLineMatchPattern)
		reAnyTopicName = re.compile(sTopicNameLineCatchPattern)
		oProc.saveVal("evLineIsTopicName", "FALSE")

		sLine =""
		sLtUp = ""
		sGtUp = ""
		for sLine in me.asMainBuffer: #  !: accessing parent class attribute
			sState = oProc.getState()
			m = reAnyTopicName.match(sLine)
			if m:
				oProc.saveVal("evLineIsTopicName", "TRUE")
				sLatestTopicName 		= m.group(1)
				nLatestTopicNameLinePos = nFocusLinePos
				me.oTrace.INFO(" topic "+sLatestTopicName+" found at line ["+str(nFocusLinePos)+"] = "+sLine)
			else:
				oProc.saveVal("evLineIsTopicName", "FALSE")
			nFocusLinePos = nFocusLinePos + 1 
			m = reNonEmptyLine.match(sLine)
			if m:
				nLastNonEmptyLinePos = nFocusLinePos
				# me.oTrace.INFO(last non-empty line at pos["+str(nFocusLinePos)+"] = '"+sLine+"'")
			if (sState == "stFindGivenHeading"):
				m = reGivenTopicName.match(sLine)
				if m:
					oProc.setState("stFindNextHeading", "given heading found in "+sGivenTopicNameLine)
				else:
					if oProc.isVal("evLineIsTopicName", "TRUE"):
						sLtUp = sLatestTopicName.upper()
						sGtUp = sGivenTopicName.upper()
						# TBD: block insertion just before latest topic h
						if sLtUp > sGtUp:
							# TBD: block insertion just before latest topic heading
							oProc.setState("stDoEndActions", "higher alphabetical order topic '"+sLatestTopicName+"' found at '"+sLine+"'")
							asAddBlock = me.createAddNewTopic(sGivenTopicName, sAddText)
							nInsertionPos = nLatestTopicNameLinePos
							break
						else:
							me.oTrace.INFO("topic name '"+sLtUp+ "' is alphabetically lower than topic name '"+sGtUp+"'")
					else:
						ab=123
						
			elif (sState == "stFindNextHeading"):
				m = reAnyTopicNameLine.match(sLine)
				if m:
					asAddBlock = me.addToExistingTopic(sLatestTopicName, sAddText)
					nInsertionPos = nFocusLinePos - 1
					oProc.setState("stDoEndActions", "given topic '"+sGivenTopicName+"' found at '"+sLine+"'")
					break
			else:
				a=1
		# ... for loop ...
		
		sState = oProc.getState()
		
		# TBD: functions for "create topic" and "insert to topic" 160808
		if (sState == "stFindGivenHeading"): # given heading not found at all
			asAddBlock = me.createAddNewTopic(sGivenTopicName, sAddText)
			nInsertionPos = nLastNonEmptyLinePos+1
		elif (sState == "stFindNextHeading"):  # given heading was last heading
			me.oTrace.INFO("given heading was found but next heading not found, so insert text to end of first topic")
			asAddBlock = me.addToExistingTopic(sLatestTopicName, sAddText)
			nInsertionPos = nLastNonEmptyLinePos+1
			
		else:
			a=1
		me.insertArray(asAddBlock, nInsertionPos) # !: a Python way to call parent class method
		

	#=====================================================================	
	def createAddNewTopic(me, sGivenTopicName, sTextToBeAdded):
	#=====================================================================
		asTopicArray =[]
		sTextToBeAdded = sTextToBeAdded.replace(sLINE_JOINER, "\n")
		me.oTrace.INFO("Create new topic '"+sGivenTopicName+ "' and add text to it")
		sTopicNameLine = sTopicNameLineMatchPattern
		sTopicNameLine = sTopicNameLine.replace(sNAME_PATTERN,"\""+sGivenTopicName+"\"")
		asTopicArray.append("")   # !: empty "append()" seems to add a "\n" !!!
		asTopicArray.append(sTopicNameLine)
		asTopicArray.append("")   # !: empty "append()" seems to add a "\n" !!!
		asTopicArray.append(sTextToBeAdded)
		asTopicArray.append("")
		return asTopicArray
		
	#=====================================================================	
	def addToExistingTopic(me, sTopicName, sTextToBeAdded):
	#=====================================================================
		asTopicArray =[]
		sTextToBeAdded = sTextToBeAdded.replace(sLINE_JOINER, "\n")
		me.oTrace.INFO("Existing topic '"+sTopicName+ "', add text to it")
		asTopicArray.append(sTextToBeAdded)
		return asTopicArray

	#=====================================================================
	def saveTopicLinesByTopicNameDict(me):   # pushes all topics and lines to AoD
	#=====================================================================
		# every KEY will be a topic name
		# every VAL will be an array of lines within that topic

		me.oTrace.INFO("start link lines saving")

		oTopicProc = clState("build DoA by OTL file", me.oTrace)
		oTopicProc.setState("stFindFileHeading","initialization")
		reAnyTopicName = re.compile(p_sOTL_TOPIC_CATCH_re)
		reOtlFileHeading = re.compile(p_sOTL_FILE_HEADING_MATCH_re)

	
		sPrevTopicName = "MISSING"
		sNowTopicName = "MISSING"
		bContinueLoop = True

		while bContinueLoop:
			sLine = me.getStoreNextLine()
			if sLine == "EOB":
				break
			oMatch = reOtlFileHeading.match(sLine)
			if oMatch:
				me.oTrace.INFO("OTL file heading found by '"+p_sOTL_FILE_HEADING_MATCH_re+"'")
				if oTopicProc.isState("stFindFileHeading"):
					oTopicProc.setState("stStoreTopics","OTL file heading found")
				continue
			else:
				pass   # OTL file heading not yet found
			if oTopicProc.isState("stStoreTopics"):  # OTL file heading found, so searches topics
				oMatch = reAnyTopicName.match(sLine)
				if oMatch: # new topic found
					sNowTopicName = oMatch.group(1)
				else:  # ordinary within new topic
					me.dOaCreatedByContents.setdefault(sNowTopicName, []).append(sLine)    # add to array in DoA
					# me.oTrace.INFO("KEY='" + sNowTopicName + "' , append VAL='" + sLine + "'")

		me.oTrace.INFO("stop link lines saving")
	#=====================================================================
	def getTopicLinesByTopicName(me, sTopicNameAsKey): # pops Topic Lines By Topic Name
	#=====================================================================
		asRet = []  # initial quess: empty array
		asNone = ["MISSING"]  # TBD: change to ["MISSING"]
		asRet = me.dOaCreatedByContents.get(sTopicNameAsKey, asNone)
		sArrayAsStr = '\n'.join(asRet)
		me.oTrace.INFO("key '" + sTopicNameAsKey + "' gave array ~" + sArrayAsStr + "~")
		# TBD: add ignoring JOURNAL stack section
		return asRet

	#=====================================================================
	def getTopicLinesRangeByTopicName(me, sTopicNameAsKey,sStartRe,sEndRe):
	#=====================================================================
		asRet = []  # initial quess: empty array
		asNone = ["MISSING"]
		asTmp = me.dOaCreatedByContents.get(sTopicNameAsKey, asNone)
		asRet = me.getRangeFromArray(asTmp, sStartRe, sEndRe)  # in <text items>
		sArrayAsStr = '\n'.join(asRet)
		me.oTrace.INFO("key '" + sTopicNameAsKey + "' gave array ~" + sArrayAsStr + "~")

		return asRet




	#=========================================================
	def removePossibleOtlArtifacts(me): 				
	#=========================================================
		# TBD: transfer this to clNotetab 
		# removes non-JSON stuff from child cConfig Class contents
		me.asSwapBuffer = []
		# TBD
		for sBufferLine in me.asMainBuffer:
			sBufferLine = sBufferLine.replace(p_sNOTETAB_OUTLINE_FILE_HEADING,"")
			sBufferLine = re.sub("^h=\".*$","",sBufferLine)
			# "[text.....]"
			sBufferLine = sBufferLine.replace("\""+sNOTETAB_HYPERLINK_TAGGED_START, "\"")  # eg. Notetab link string start
			sBufferLine = sBufferLine.replace(sNOTETAB_HYPERLINK_TAGGED_END, "")  # eg. Notetab link string end
			me.asSwapBuffer.append(sBufferLine)   # can contain multiple '\n' -terminated lines !!!
			#TBD: if line starts with
		me.asMainBuffer = me.asSwapBuffer
		me.updateEndPos() 

	#==================================================================================
	def buildTopicsByDirectories(me, sEntryPathsSeq, reMatchStr, sIgnoreFileExtSeq):
	#==================================================================================
		# edited from (working) solitary script file (160816)   TBD: test in this class context
		# TBD: modify this method as a generic file name collector into FileManageUtils.py (160817)
		me.oTrace.INFO("entry paths sequence = "+sEntryPathsSeq)
		me.oTrace.INFO("ignore filename extensions sequence = "+sIgnoreFileExtSeq)
		me.oTrace.INFO("result file name ="+sResultFile)
		
		me.addText(p_sNOTETAB_OUTLINE_FILE_HEADING+"\n\n")
		# me.addText("h=\""+sParentPath+"\"\n\n")
		asEntryPaths = sEntryPathsSeq.split(',')
		asIgnoreExts = sIgnoreFileExtSeq.split(',')

		for sEntryPath in asEntryPaths:
				me.oTrace.INFO("entry path ="+sEntryPath)
				for sFocusPath, asDirNames, asFileNames in os.walk(sEntryPath):
						#dirname = os.path.basename(os.path.dirname(path))
						sFocusPath = sFocusPath+"\\"
						me.oTrace.INFO("    focus path ="+sFocusPath)
						(sParentPath, sFocusDir) = os.path.split(os.path.dirname(sFocusPath))
						me.oTrace.INFO("    parent path = "+sParentPath)
						me.oTrace.INFO("    focus dir ="+sFocusDir)
						bTopicNameWritten = 0
						
						sFileType = "SOME_FILE"
						for sFileName in asFileNames:
							bIgnoreFile = 0						
							(sPathAndBody, sExtension) = os.path.splitext(sFileName)				
							sFileFullName =  sFocusPath+sFileName
							for sIgnoreExt in asIgnoreExts:
								if sExtension.lower() == sIgnoreExt:
									bIgnoreFile = 1
									continue
							if bIgnoreFile == 1:
								continue
				
							if sFocusDir=="OTL":
								# why this ???? sFileName = sFileFullName
								sFileType = "OTL_FILE"
			
							if reMatchStr == "ALL_FILES":
									if bTopicNameWritten == 0:
											me.addText("\n\nh=\""+sFocusDir+"\"\n\n")
											me.addText("[\"explorer.exe\" "+sFocusPath+"]\n\n")
											#  - "explorer.exe" prefix causes double click to open windows explorer
											bTopicNameWritten = 1
									me.addText("        ["+sFileName+"]\n")
							else:
									hfText = open(sFileFullName, 'r')
									me.oTrace.INFO("searches '"+reMatchStr+"' in file '"+sFileFullName+"'")
									asLines = hfText.readlines()
									bFileNameWritten = 0
									nLineNbr = 0
									for sLine in asLines:
											nLineNbr = nLineNbr + 1
											sLineNbr = str(nLineNbr)
											if reMatchStr in sLine:
													sTrimmedLine = sLine.strip()
													if bTopicNameWritten == 0:
															me.addText("\n\nh=\""+sFocusDir+"\"\n\n")
															me.addText("[\"explorer.exe\" "+sFocusPath+"]\n\n")
															#  - "explorer.exe" prefix causes double click to open windows explorer
															bTopicNameWritten = 1
													if bFileNameWritten == 0:
															me().addText("        ["+sFileName+"]\n")
															bFileNameWritten = 1
													me.addText("            ["+sLineNbr+"]   "+sTrimmedLine+"\n")
													

									hfText.close()
							
	#==================================================================================
	def copySubtopicActiveContentsToFile(me, sFocusFilePathName):  # TODO: between "@begin" and "@end"
	#==================================================================================
	# TODO: for eg 7ZIP packing "include" and "exclude" files   190425
		pass
 
	#==================================================================================
	def expandOrFileByOtlLinks(me, sFocusFilePathName):  # TBD: add <start> and <stop> call parameter regexes
	#==================================================================================
	# assumes, that stored text may contain Notetab hyperlinks [<FILE>::<TOPIC>]
	#  -	if found, opens the <FILE>
	
	# TODO: idea: if link line is of format "[<otl file name>::<topic name>] => <FILE NAME>", then the
	# link topic ACTIVE contents will be copied to file <FILE NAME> 190425

		bStartAlreadyFound = False
		asExpandedRetLines = []

		oTxtUt = clTextItems("refine text operations", me.oTrace)
		oLinkOtlFile = clNotetab("any file behind the link", me.oTrace)

		sStartRe = 	me.getParam("TopicUsableStartTag_")		# TBD: add "setParam()" call to application level
		sEndRe 	 = 	me.getParam("TopicUsableEndTag_")   	# TBD: add "setParam()" call to application level

		oStartRe 	= re.compile(sStartRe)
		oEndRe 		= re.compile(sEndRe)
		
		me.oTrace.INFO("'"+me.sDuty+"': Contents file scanning started")
		bContinueLoop = True
		while bContinueLoop:
			sFeedRow = me.getStoreNextLine()  # inpup has already been read from a file
			me.oTrace.INFO("handle line '"+sFeedRow+"'")
			# first does the capture attempts to single line
			if sFeedRow == "EOB":
				me.oTrace.INFO("handle line '" + sFeedRow + "'")
				break
			if bStartAlreadyFound == True:
				oMatch = oEndRe.match(sFeedRow)  # TBD: add 'oStartRe' -usage
				if oMatch:
					me.oTrace.INFO("end '"+sEndRe+"' found, so skip rest of topic")
					break
				else:
					pass   # process present feed line
			else: # start not yet found
				oMatch = oStartRe.match(sFeedRow)  # TBD: add 'oStartRe' -usage
				if oMatch:
					bStartAlreadyFound = True
					me.oTrace.INFO("start '"+sStartRe+"' found, so get next line")
				else:
					me.oTrace.INFO("start '"+sStartRe+"' not yet found, so get next line")
				continue # goto get next feed line
				# me.oTrace.INFO("start alreadyfound")
			if oTxtUt.tuneUsableLine(sFeedRow, p_asLINE_TAIL_COMMENTS):  # removes empty lines and line end comments
				sFeedRow = oTxtUt.dRet.get('Line_',"MISSING")  # dictionary (and key) created in called function
			else:
				me.oTrace.INFO("line tuning failed, so get next line")
				continue  # line is empty or full comment so goes to get next line
			if oTxtUt.isOtlLink(sFeedRow):  # if OTL link is detected, then destination topic is inserted to contents level
				sDestFileName = oTxtUt.dRet['_DestFileName_']
				sDestTopicName = oTxtUt.dRet['_DestTopicName_']
				me.oTrace.INFO("Tries to get lines from ["+sDestFileName+"::"+sDestTopicName+"]")
				sLinkFileFullName = sFocusFilePathName + "\\" + sDestFileName
				if checkFileExistence(sLinkFileFullName, me.oTrace) == "YES_EXIST":
					me.oTrace.INFO("Link File '" + sLinkFileFullName + "' DOES exist")
					oLinkOtlFile.rawFillFromFile(sLinkFileFullName)
					oLinkOtlFile.saveTopicLinesByTopicNameDict()
					asTopicLines = oLinkOtlFile.getTopicLinesRangeByTopicName(sDestTopicName, sStartRe, sEndRe) # gets limited section of lines from given subtopic
					asTopicLines = oTxtUt.tuneUsableLinesArray(asTopicLines, p_asLINE_TAIL_COMMENTS)
					me.oTrace.INFO("Subtopic lines: "+arrayToStr(asTopicLines))
					asExpandedRetLines.extend(asTopicLines) # https://stackoverflow.com/questions/252703/append-vs-extend
				else:
					me.oTrace.INFO("Link File '"+sLinkFileFullName+"' does NOT exist")
			else:
				me.oTrace.INFO("no subfocus topic expansion, just append line "+sFeedRow+"'")
				asExpandedRetLines.append(sFeedRow)
			# TBD: add removal of tail JOURNAL stack 171211

		return asExpandedRetLines
