import sys
import os
import inspect
import logging
import traceback
import re
from TrickUtils import *
from ParamUtils import *
from TextItemUtils import *
from TextStorageUtils import *
from NotetabUtils import *


#from StringIO import StringIO



# TBD: config file for filter regexes 
# has automatic indention incrementing
# TBD: automatic indention decrementing (search from caller names stack)
#	-	so far uses "RET()" -function
# https://opensourcehacker.com/2011/02/23/temporarily-capturing-python-logging-output-to-a-string-buffer/
# TBD: add logger module as parent

# !: python: http://code.activestate.com/recipes/411791-automatic-indentation-of-output-based-on-frame-sta/


# http://code.activestate.com/recipes/412603-stack-based-indentation-of-formatted-logging/
#class clTrace(clParams):
#class clTrace(clTextItems):   # activated 170809
#class clTrace(clTextStorage):  # activated 170827
# TBD: another <trace> module, which has only standard library dependencies and non-notetab features
class clTraceOtl(clNotetab):  # activated 170827
	# TBD: evaluate, if this module should not inherit anything, so be more generic for "any" python application
	#asPickRegexesByConf = []
	#nCallStackDepthPrev = 0

	#m_bInitCalled = False
	# wrapper to "logger" module
	#	-	combines logger configurability with higher level (eg. Notetab OTL file syntax) operations
	#TBD: add array size value to all trace calls which tell about array operations (180113)

	#=========================================================
	def __init__(me, sMainScriptName, sTraceFileRelOrFullPath):  # python constructor
	#=========================================================
		# -does: trace file name is generated from caller script name 
		# TBD: add usage of configuration JSON file to select traceable strings as regexes
		me.bOtlFileHeadingCreated = False
		me.asMATCHES_ALL_LINES_REGEX = [".*"]
		me.oTrace = me   # this object is tracing object
		me.sDuty = "program execution tracing"

		#me.sTraceFileFocusTopicName 		= p_sNOTHING  # for eg. sidekick file usage
		#me.sTraceSidekickFileFocusTopicName = p_sNOTHING
		
		me.sTraceFileFocusTopicName 		= "NOT_INITIALIZED"  # for eg. sidekick file usage
		me.sTraceSidekickFileFocusTopicName = "NOT_INITIALIZED"

		me.bSidekickUpdateOngoing	= False
		
		me.sCallerFuncPrev = " "
		me.oTraceLogger = 0

		me.bThisObjectIsOperable = False
	
		#me.setOperability(True, "initial quess")
		me.asPickRegexesByConf   = []
		#me.setOperability(False, "initial quess")
		
		# no comment parameter this early, because then would use the "...oTrace.INFO(..."
		if not os.path.exists(sTraceFileRelOrFullPath): # any string that is not existing path disables tracing
			# TBD: ALLWAYS create the trace file
			#  - write just few lines when THIS object is inoperable
			print ("Trace log file for '" + sMainScriptName + "' is not created, because path '"+sTraceFileRelOrFullPath+"' does not exist")
			# me.setOperability(False, sTraceFileRelOrFullPath) # no comment parameter this early, because then would use the "...oTrace.INFO(..."
			return
		else:
			print ("Trace log file for '" + sMainScriptName + "' is created, because path '" + sTraceFileRelOrFullPath + "' exists")
			# me.setOperability(True, sTraceFileRelOrFullPath)
		

			# trace file name is now built based on main script name for easier finding
		me.sTraceFileWholeName = ""
		me.sTraceFilePlainName = ""
	
		#====================================================================
		me.nFlowAbsoluteLineNbr = 0  # e.g. original feed file line number
		me.nFlowRelativeLineNbr = 0  # some subset of ignored or picked lines
		#===================================================================
		me.oSidekick = 0

		me.oTraceLogger = 0
		

		me.oTraceConf = 0
		#me.setOperability(False,"initial quess") # initial quess
		me.nSidekickTopicPosNbr = 0
		me.nCallStackDepthPosNow = 0
		me.sCallStackDepthPosNowAsStr = ""
		me.nCallStackDepthPrev = 0
		me.sCallStackDepthPosPravAsStr = ""
		
		me.asCallerFunctionNames = ["---empty---", "---empty---", "---empty---", "---empty---", "---empty---",
									"---empty---", "---empty---", "---empty---"]  # for saving

		me.nIndentLevel = 0
		me.sIndent = ""
		me.sTraceLine = ""
		me.sPickRe = "^.*$" # initialization: all texts are written

		me.dLatestCallLineByFile = {}  # for link printouts
	
		 #me.sTraceFileWholeName = "E:\\tmp\\KUKKUU.TXT"
		# - file names are assigned to object members within the method


		#==============================================================================
		me.createTraceFileNamesByScriptName(sMainScriptName, sTraceFileRelOrFullPath)
		#==============================================================================
	#
	#	print ("Trace file: " + me.sTraceFileWholeName)
	# -----------creates Notetab top ---------------------
		# me.oLogCapture = StringIO()
		logging.basicConfig(format='%(message)s',
							datefmt='%m/%d/%Y %I:%M:%S %p',
							filename=me.sTraceFileWholeName,
							filemode='a',  # !: appends to existing file
							level=logging.INFO)

		me.oTraceLogger = logging.getLogger('logger')
	
		
		clNotetab.__init__(me, me.sDuty, me)  # this position caused Python Errors to disappear (why ?)
		bStatus = me.openWriteFile(me.sTraceFileWholeName)  # TBD: remove back to stand-alone
		if bStatus == False:
			print("trace file '"+me.sTraceFileWholeName+"'"
														" open failed\n")
			return
		if me.isNotOperable():
			print("trace object is not operable\n")
			return
			
		me.bThisObjectIsOperable = True
		#me.oTrace.INFO(p_sNOTETAB_OUTLINE_FILE_HEADING + "\n")
	

		me.bOtlFileHeadingCreated = True
		me.oTrace.INFO(p_sNOTETAB_OUTLINE_FILE_HEADING + "\n")
	

		sTopicNameLine = createOtlTopicHeading("The Log")
	
		me.oTrace.INFO("\n" + sTopicNameLine + "\n\n")
	
		me.oTrace.INFO("\nSTARTED: " + timeStamp('%Y-%m-%d %H:%M:%S') + "\n\n")
		#me.INFO("create trace sidekick file  [" + me.sTraceSidekickFileWholeName + "]", "constructor")
		#me.fhOutFile.write("\n sidekick file link ["+me.sSidekickTraceFilePlainName+"]")
		### 171206 me.closeOutFile()

		me.fhSidekickFile = 0
		# TBD: change constants to object params

		#print ("pick RE = '"+me.sPickRe+"'")
		# trace file opens/closes are handled by main script, not in objects
		#me.setOperability(True, "initial quess")
		me.oTrace.INFO("created trace sidekick file  [" + me.oSidekick.getFileWholeName() + "]")

		#bclNotetab.__init__(me, me.sDuty, me)
		print ("trace sidekick file " + me.oSidekick.getFileWholeName())
		#me.createSidekickOtlFile()

		#me.m_bInitCalled = True
	#=========================================================	
	def INFO_OLD(me, sText, sConf=""):  # generic function
	#=========================================================
		# NOTE: if text contains LF:s then output does not appear in trace log file
		#   ---> TBD: add 'sText' "linefying" 170310
		#return # to reduce slowness
		# http://stackoverflow.com/questions/11799290/get-function-callers-information-in-python
		# !: __FILE__, __LINE__, __FUNCTION__ : pythonhttp://stackoverflow.com/questions/6810999/how-to-determine-file-function-and-line-number
		# TBD: IF text contents > NN THEN create new topic to peer OTL file and put link to trace file
		bLoggingDone 	= False
		nLineSeqNbr 	= 0
		bStatus 		= False
		#if me.m_bInitCalled == False:
		#	return
		#if 'Run started' in sText:  # simple hard-coded debugging 'filter'
		#	print("INFO :"+sText)
		sTopicHeadingCreationLocation = "MISSING"
		if me.isNotOperable():
			#print ("TRACE OBJECT IS NOT OPERABLE")
			return
	
		me.incFlowAbsoluteLineNbr()
		if me.asPickRegexesByConf:  # got from trace conf JSON file via assignment call
			bStatus = me.tryMatchAnyInRegexArray(sText, me.asPickRegexesByConf)
			if bStatus == False:  # for trace log reduction
				return   # configuration Regex match failed, so skip current trace
			else:
				pass # configuration Regex match occurred, so executes this trace
		else:
			pass  # no configuration defined at all, so executes ALL traces

		#print ("TRACE text '"+sText+"'")
		nLineSeqNbr = me.getFlowAbsoluteLineNbr()
		sLineSeqNbr = str(nLineSeqNbr)
		bIgnoreIndention		= False
		sOtlLinkToSidekickTopic = ""
		#sFunctionCallHierarcy = '->'.join(me.asCallerFunctionNames)  # for debugging the trace itself
	
		aoCallerFrameRecord = inspect.stack()[1]
		# aoCallerFrameRecord 	= inspect.stack()[2]  				# "index out of range"
		# aoCallerFrameRecord 	= inspect.stack()[0]				# takes THIS method as "root"
		# oFrame				= aoCallerFrameRecord[1] 				# "... no attribute ..."
		oFrame = aoCallerFrameRecord[0]
		oInfo = inspect.getframeinfo(oFrame)
		__sFILE__ = oInfo.filename  # __FILE__
		__sFUNC__ = oInfo.function  # __FUNCTION__
		__sLINE__ = str(oInfo.lineno)  # __LINE__
		# TBD: add more "keyword" controls
		sFileLineLink = "["+__sFILE__+"::"+__sLINE__+"^L]"
		if "exception" in sConf:
			exctype, value = sys.exc_info()[:2]
			sExceptionText = str(exctype)+" "+str(value)
			sText = sText + " --- "+sExceptionText + " "+__sFUNC__+"()"
		elif "topic" in sConf:  # indention must be ignored
			# TBD: add more <conf> parameter alternatives to form the trace file
			sText = "h=\""+ sText +"\""
			sTopicHeadingCreationLocation = sFileLineLink
			#print ("creates heading for "+sText+"\n")
			bIgnoreIndention		= True
		elif "function" in sConf:
			sText = sText + "   function: "+__sFUNC__+"()"
		else:
			abc = 123

		sNOTETAB_HYPERLINK_LINE_TAG = "::"+__sLINE__+"^L"
		sCOLORIZER_TAG 		= "://"
		sFunctionName 		= ""
		bPutFunctionName 	= False  # initial quess

		me.nCallStackDepthPosNow = 0
		#----------- COLLECTS CALL STACK ----------------
		oFrame = inspect.currentframe()
		while True:
			try:
				oFrame = oFrame.f_back
				me.nCallStackDepthPosNow += 1
			except:
				break
		#------------------------------------------------
		me.sCallStackDepthPosNow = str(me.nCallStackDepthPosNow)
		sEmptyIndent = sEMPTY_BRICK * me.nCallStackDepthPosNow
		sLinedIndent = sLINED_BRICK * me.nCallStackDepthPosNow
		sDepth = str(me.nCallStackDepthPosNow)

		if me.nCallStackDepthPosNow < me.nCallStackDepthPrev:
			for i in range(me.nCallStackDepthPosNow, me.nCallStackDepthPosPrev): # clears "downstream" when return occurs
				me.asCallerFunctionNames[i] = "---empty---"

		try:
			#me.oTraceLogger.info(arrayToStr(me.asCallerFunctionNames,"","caller stack: ", ))  # feature for debugging purposes
			if me.asCallerFunctionNames[me.nCallStackDepthPosNow] != __sFUNC__:
				bPutFunctionName = True
		except:
			bPutFunctionName = False
	
		# bPutFunctionName = True # to debug the trace operation itself. REMOVE FINALLY
						
		# me.oTraceLogger.info(sEmptyIndent+sEMPTY_OFFSET_BRICK+"============= stack.depth/caller.function/caller.function.prev = '"+str(nCallStackDepth)+"'/'"+__sFUNCT__+"'/'"+me.sCallerFunctionPrevName+"'")
		if bPutFunctionName == True: 
			me.oTraceLogger.info(sEmptyIndent+__sFUNC__+sCOLORIZER_TAG+" ["+sDepth+"] -------------<>["+__sFILE__+sNOTETAB_HYPERLINK_LINE_TAG+"]")
			bLoggingDone = True
		#if 'Run started' in sText:  # simple hard-coded debugging 'filter'
		#	print("INFO :"+sText)
		
		if (len(sText) > 11111 or sConf == "exception") and (sConf != "forced"):
			me.nSidekickTopicPosNbr += 1
			sTopicPosNbr = str(me.nSidekickTopicPosNbr)
			sTopicName = __sFUNC__+"_"+sConf+"_"+sTopicPosNbr
			sSidekickFileName = me.oSidekick.getFilePlainName()
			sOtlLinkToSidekickTopic = me.createOtlLink(sSidekickFileName, sTopicName)
			bLoggingDone = True
			me.oTraceLogger.info(sEmptyIndent+sEMPTY_OFFSET_BRICK+sOtlLinkToSidekickTopic+ "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
			#me.createTopicToOtlSidekickFile(sText, sTopicName)
			me.oSidekick.createAddNewTopic(sText, sTopicName)    # updates sidekick file object
		else:
			if bIgnoreIndention == True:
				#print ("Tries to log "+sText\n")
				bLoggingDone = True
				#if 'Run started' in sText:  # simple hard-coded debugging 'filter'
				#	print("INFO :" + sText)
				me.oTraceLogger.info("\n\n")
				#me.oTraceLogger.info(sFunctionCallHierarcy+" "+sText)  # for debugging the trace itself. REMOVE FINALLY
				me.oTraceLogger.info(sText+ "   ("+ sLineSeqNbr+")")   # no indention: eg. for notetab outline topic heading creation
				me.oTraceLogger.info("\n\n")
				if sTopicHeadingCreationLocation != "MISSING":
					me.oTraceLogger.info(sTopicHeadingCreationLocation+"\n")
			else:
				#me.oTraceLogger.info(sEmptyIndent+sEMPTY_OFFSET_BRICK+"============= stack.depth/caller.function = '"+str(nCallStackDepth)+"'/'"+__sFUNCT__+"/")
				me.oTraceLogger.info(sEmptyIndent+sEMPTY_OFFSET_BRICK+sText + "   ("+ sLineSeqNbr+")")
				bLoggingDone = True
			# me.oTraceLogger.log(me.TRON, me.sIndent+sEMPTY_OFFSET_BRICK+sText)

		try:
			me.asCallerFunctionNames[me.nCallStackDepthPosNow] = __sFUNC__
		except:
			pass
		me.nCallStackDepthPosPrev = me.nCallStackDepthPosNow
		me.sCallStackDepthPosPrev = str(me.nCallStackDepthPosPrev)
		if bLoggingDone == False:
			pass
			#print (sText+ "IS NOT WRITTEN TO TRACE FILE")
	
	#=========================================================
	def INFO(me, sText, sType=""):  # for debugging the trace itself
	#=========================================================
		if me.isNotOperable():
			return

	
		if me.bOtlFileHeadingCreated == False:  # added to prevent to early logging (why does that happen ?)
			return
		bLoggingDone = False
		nLineSeqNbr = 0
		bStatus = False
		sTraceLine = ""

		sINDENT_STEP = "        "
		asCallStack 		= []
		asCallStackReverse	= []
		sCallerFileLine = ""
	
		sCallTree = ""
		oFrame = inspect.currentframe()
		oInfo = inspect.getframeinfo(oFrame)
		__sTHIS_FUNC__ = oInfo.function
		__sTHIS_FILE__ = oInfo.filename
		__sLINE_XXX__ = str(oInfo.lineno)  # __LINE__
	
		oFrame = oFrame.f_back
		oInfo = inspect.getframeinfo(oFrame)
		__sCALLER_FUNC__ 	= oInfo.function
		__sCALLER_FILE__	= oInfo.filename


		#stack = inspect.stack()
		#__sCALLER_CLASS__ 	= stack[1][0].f_locals["me"].__class__
		#https: // stackoverflow.com / questions / 17065086 / how - to - get - the - caller -class -name-inside-a-function-of-another- class - in -python

		__sCALLER_LINE__ 	= str(oInfo.lineno)

		me.dLatestCallLineByFile[__sCALLER_FILE__] = __sCALLER_LINE__
		asCallStackReverse.append(__sCALLER_FUNC__)

		while True:
			try:
				oFrame = oFrame.f_back
				oInfo = inspect.getframeinfo(oFrame)
				__sFILE__ = oInfo.filename
				__sFUNC__ = oInfo.function
				asCallStackReverse.append(__sFUNC__)
			except:
				break

		for sFunctionName in asCallStackReverse:
			sCallTree = sCallTree + sFunctionName + "()<---"
		sCallerFileLine = "[" + __sCALLER_FILE__ + "::" + __sCALLER_LINE__ + "^L]"
		if __sCALLER_FUNC__ == me.sCallerFuncPrev:
			pass
			# sCallTree = ""
		else:
			pass
			# sCallTree = sCallTree + "\n"

		me.sCallerFuncPrev = __sCALLER_FUNC__

		# __sCALLER_CLASS__  TBD: find a way to get this !!!
		bUpdateSidekickFile = False  # initial quess

		if sType:
			if "exception" in sType:
				exctype, value = sys.exc_info()[:2]
				sExceptionText = str(exctype) + " " + str(value)
				sText = sText+" "+sExceptionText  + __sFUNC__ + "()"
			# TBD: add choices
			elif "constructor" in sType:
				sText = sText  # TBD: add __sCALLER_CLASS__ here
			elif "topic" in sType:
				sType = ""

			elif "kick" in sType:
				bUpdateSidekickFile = True
				if me.bSidekickUpdateOngoing == False:
					me.oSidekick.createAddNewTopic(sText, me.sTraceFileFocusTopicName)
					me.oSidekick.addReverseLink(me.sTraceFilePlainName, me.sTraceFileFocusTopicName)
					sSidekickFileName = me.oSidekick.getFilePlainName()
					sOtlLinkToSidekickTopic = me.createOtlLink(sSidekickFileName, me.sTraceFileFocusTopicName							   )
					me.oTraceLogger.info(sOtlLinkToSidekickTopic)
					me.bSidekickUpdateOngoing = True
				else:
					me.oSidekick.addToFocusTopic(sText + "\n          " + sCallerFileLine+"    " + sCallTree)
					
			else:
				pass

			if bUpdateSidekickFile == False:  # creates new roled topic to trace OTL file
				me.bSidekickUpdateOngoing = False
				me.sTraceFileFocusTopicName = sType +" "+ sText
				sTopicName = "\n\nh=\"" + me.sTraceFileFocusTopicName + "\"\n"
				me.oTraceLogger.info(sTopicName)
				# me.oTraceLogger.info(sCallTree + "\n                " + sCallerFileLine)
				me.oTraceLogger.info("          " + sCallerFileLine+"    " + sCallTree+"\n\n")
			else:  # adds sidekick OTL file link to trace OTL file focus topic
				sSidekickFileName = me.oSidekick.getFilePlainName()
				sOtlLinkToSidekickTopic = me.createOtlLink(sSidekickFileName, me.sTraceFileFocusTopicName
														   )
				# me.oTraceLogger.info(sOtlLinkToSidekickTopic)
		else:  # adds text to trace OTL file focus topic
			# me.oTraceLogger.info(sCallTree + "        " + sText + "\n                " + sCallerFileLine)
			me.oTraceLogger.info(sText + "\n          " + sCallerFileLine+"    " + sCallTree)


	#=========================================================	
	def CLOSE(me):
	#=========================================================
		me.closeOutFile()

	#=========================================================	
	def decIndent(me):
	#=========================================================
		if me.nIndentLevel >= nINDENT_STEP_WIDTH:  #  no negative indents
			me.nIndentLevel -=	nINDENT_STEP_WIDTH	# !: Python
		else:
			a=123
			# TBD: Trace ERROR here
		me.sIndent = ''.join([' ' for s in range(me.nIndentLevel)])	 # !: Python string multiplication
	#=========================================================	
	def incIndent(me):
	#=========================================================
		me.nIndentLevel +=	nINDENT_STEP_WIDTH
		me.sIndent = ''.join([' ' for s in range(me.nIndentLevel)])	 # !: Python string multiplication

	# =============================================
	def createTraceFileNamesByScriptName(me, sMainScriptName, sTraceFileRelOrFullPath):
	# =============================================
		# trace file path name can be relative to script path or totally on another drive
		# TBD: create also trace sidekick file name here 170405
		
		
		sScriptPathName = os.path.dirname(sMainScriptName)+"\\"
		if os.path.exists(sTraceFileRelOrFullPath):
			sTraceFilePathName = sTraceFileRelOrFullPath
		else:
			sTraceFilePathName = sScriptPathName + "\\" + sTraceFileRelOrFullPath

		#print("script: " + sMainScriptName)   # IDEA: All file names and end result status shall be printed to console
		#print("script path name  " + sScriptPathName)
	
		#print("trace file path name  " + sTraceFilePathName )

		sScriptName = os.path.basename(sMainScriptName)
		sScriptExt = os.path.splitext(sMainScriptName)[1]
		sTraceFileBody = sScriptName.replace(sScriptExt, "")
	
		me.sTraceFilePlainName = sTraceFileBody + sTRACE_FILE_EXT
		me.sTraceFileWholeName = sTraceFilePathName + "\\" + me.sTraceFilePlainName
		
	
		#print("trace file: " + me.sTraceFileWholeName)

		
		sTraceSidekickFilePlainName = sTraceFileBody + sSIDEKICK_FILE_NAME_TAG + sTRACE_FILE_EXT
		sTraceSidekickFileWholeName = sTraceFilePathName + "\\" + sTraceSidekickFilePlainName
	
		
		me.oSidekick = clTraceSidekick(sTraceSidekickFileWholeName,sTraceSidekickFilePlainName)      # creates sidekicck file object
	#=========================================================
	def assignTraceConfByJson(me, oTraceConfByJsonFile):
	#=========================================================
		# versatile filtering operations lines are passed, modified,expanded, combined etc.
		# can be used when writing from buffer to file
		asArray = []
		# TBD: add also trace output formatting to configuration JSON file
		print ("assign configuration JSON object to TRACE operations")


		try:
			me.oTraceConf = oTraceConfByJsonFile
			if me.isOperable():
				print("Trace is operable")
				if me.oTraceConf.isOperable():
					me.INFO("Selected traces are filed")
					print("Trace conf is operable")
					XoYroot = me.oTraceConf.getXoYroot()
					asArray = XoYroot.get("PickFilter_", ["All_"])
					me.oTraceConf.createNamedArray("PickFilter_", asArray)
					me.asPickRegexesByConf = me.oTraceConf.getWholeNamedArray("PickFilter_")
					sPythonStructAsStr = print.pformat(me.asPickRegexesByConf)
					me.oTrace.INFO("Trace output lines containing any of strings: -" + sPythonStructAsStr)
					print ("TRACE file 'PickFilter_' " + str(me.asPickRegexesByConf))
				# sConfDuty 				= oTraceConfByJson.getDuty()
				else: #
					me.INFO("All traces are filed")
					me.asPickRegexesByConf = me.asMATCHES_ALL_LINES_REGEX
					#me.setOperability(False, "tracing disabled")
					#print("Tracing ended")
			else:
				print("Trace object is not operable")

			me.oTrace.INFO("assignment attempt ended")
		except:
			exctype, value = sys.exc_info()[:2]  # !: very comprehensive output
			errorText = str(exctype) + " " + str(value)
			me.oTrace.INFO("ERROR: object '" + me.sDuty + "' '" + errorText + "'")
			#print("ERROR: Trace object: '" + me.sDuty + "' '" + errorText + "'")

		me.oTrace.INFO("function ended")
		
	#=========================================================
	def getTraceFileWholeName(me):
	#=========================================================
		return me.sTraceFileWholeName
	
#########################################################################
class clTraceSidekick:		# for creating object to be used only within clTraceOtl

	#=========================================================
	def __init__(me, sSidekickOtlFileWholeName, sSidekickOtlFilePlainName):  # python constructor
	#=========================================================
		#me.oTrace = oTrace
		me.sSidekickOtlFileWholeName 	= sSidekickOtlFileWholeName
		me.sSidekickOtlFilePlainName 	= sSidekickOtlFilePlainName
		
		me.fhSidekickFile = open(me.sSidekickOtlFileWholeName, "w")  # overwrites old file
		me.fhSidekickFile.write(p_sNOTETAB_OUTLINE_FILE_HEADING + "\n")
	#=========================================================
	def createAddNewTopic(me, sText, sOngoingContext):
	#=========================================================
		sTopicNameLine = createOtlTopicHeading(sOngoingContext)
		me.fhSidekickFile.write("\n" + sTopicNameLine + "\n")
		me.fhSidekickFile.write("\n" + sText + "\n")
	#=========================================================
	def addToFocusTopic(me, sText
						):
	#=========================================================
		me.fhSidekickFile.write("\n" + sText + "\n")

	#=========================================================
	def addReverseLink(me, sTraceFilePlainName, sTraceFileTopic):
	#=========================================================
		me.fhSidekickFile.write("\n[" + sTraceFilePlainName +"::"+sTraceFileTopic+"]\n")
	
	#=========================================================
	def getFilePlainName(me):
	#=========================================================
		return me.sSidekickOtlFilePlainName
	#=========================================================
	def getFileWholeName(me):
	#=========================================================
		return me.sSidekickOtlFileWholeName

#======================= YARD =============================================

'''
			if sFunctionName == __sCALLER_FUNC__:

				if __sCALLER_FUNC__ == me.sCallerFuncPrev:
					sTraceLine = sIndentStr + sINDENT_STEP + "INFO : " + sText+ "  "+sCallerFileLine
				else:
					sTraceLine = sIndentStr + __sCALLER_FUNC__ + "() " + "INFO : " + sText+ "  "+sCallerFileLine
				me.sCallerFuncPrev = __sCALLER_FUNC__
				break
'''