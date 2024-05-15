import os, sys
import os.path
import re
import json
import time
import datetime
import pickle
# from StringUtils import *
from TrickUtils import *
from ParamUtils import *
from TextItemUtils import *


# is in ParamUtilsp_nVERY_IMPROBABLE_INTEGER = -9999    # !: Python "global" variables shall be here (outside class definion)
sEVERYTHING_MATCH_re = "^.*$"  # for filter defaults
sVERY_IMPROBABLE_MATCH_re = "^this regex shall not match anything$" # for filter defaults
# http://stackoverflow.com/questions/29214888/typeerror-cannot-create-a-consistent-method-resolution-order-mro

class clStoreModifier():

# read Data input via ConfigUtils and build an array of config items
# for each store line
#	for each config item
#		try match
#			if match then
#				convert, add or reduce lines
#				update storeend position
#				continue
	pass





class clTextStore(clTextItems):   # class name changed to distinguish it better from module (=file) name
	# - parent class contains already 'clParams'

# PURPOSE:
# read from files
# write to file
# manipulate and eExtract contents
# generate new buffers from manipulated and eExtracted data
# combine multiple files contents
# read configuration files to manipulate buffer contents
# similar to JSON usage: https://wiki.python.org/moin/UsingPickle
# https://pythontips.com/2013/08/02/what-is-pickle-in-python/

# TBD: versatile methods to filter lines when reading, copying and writing files

	#=========================================================
	def __init__(me, sDuty, oTrace, sTheseDriveLetter="N/A", sCreatorPath="N/A", sCreatorName="N/A"):  # python constructor
	#=========================================================
		# trace file opens/closes are handled by main script, not in objects
		#TBD: buffer type setting in constructor to reduce accidental writing to input files
		
		#clParams.__init__(me, sDuty, oTrace)  #
		clTextItems.__init__(me, sDuty, oTrace)  # # - parent class contains already 'clParams'
		me.setObjectOperability(True)   # initial quess
		me.sTheseDriveLetter = sTheseDriveLetter
		me.sCreatorPath 	= sCreatorPath
		me.sCreatorName 	= sCreatorName  # creator script name
		me.oTrace 			= oTrace
		me.asMainBuffer 	= []
		me.nMainBufferSize  	= 0
		me.nMainBufferLastPos	= 0 
		me.nMainBufferPos		= -1
		me.sMainBufferPos		= ""
		me.nMainBufferBookmarkPos = -1   # for navigation
		me.asSwapBuffer 		= []   # workspace when removing lines etc.
		
		me.sDuty 			= sDuty  # means the "task" or "role" of the object. Mainly used to improve Trace Log 
		me.sStartPassRe 		= ""  # TBD: edit some file I/O -functions to use these
		me.sDoPassRe			= ""
		me.sSkipPassRe			= ""
		me.sStopPassRe 			= ""
		me.bPassActive			= False
		me.bPassOccurred		= False
		
		#----- by external configuration (JSON) file object --------------------
		me.oPassFilterConfByJson 	= 0
		me.asStartPassChoicesByCfg	= []
		me.asDoPassChoicesByCfg		= []
		me.asSkipPassChoicesByCfg	= []
		me.asStopPassChoicesByCfg	= []
		me.dThisObjParams			= {} # local configuration data
		
		me.sAttachedFileName		= "" # for write access check usage
		me.bAllowWritingToAttachedFile = True # initial quess
				
		me.clearAll()
		me.oTrace.INFO("'"+sDuty+"' object created")
		#me.sDateTime = datetime.now()


		me.fhOutFile=0
		me.fhInFile=0
		# TBD: maybe similar for <input file>

	#=========================================================
	def getMainBufferPosInfo(me): 
	#=========================================================
		sPosNow = str(me.nMainBufferPos)
		sPosLast = str(me.nMainBufferLastPos)
		sRet = sPosNow+"/"+sPosLast
		return sRet
	
	#=========================================================
	def resetMainBuffer(me):
	#=========================================================
		me.asMainBuffer 		= []
		me.nMainBufferSize  	= 0
		me.nMainBufferLastPos	= 0 
		me.nMainBufferPos		= -1
		me.sMainBufferPos		= ""
		me.nMainBufferBookmarkPos = -1   # for navigation
	#=========================================================
	def setReadOnly(me):
	#=========================================================
		me.bAllowWritingToAttachedFile = False # to prevent accidental writing to typically read-only files (source code, configuration,...)
			
	#=========================================================
	def isFileWriteAllowed(me):  
	#=========================================================
		bStatus = me.bAllowWritingToAttachedFile
		if bStatus == False:
			me.oTrace.INFO("prevented attemption to write file '"+me.sAttachedFileName+"'")
		return bStatus
	
	#=========================================================
	def getContents(me):  
	#=========================================================
		return me.asMainBuffer
	
	#=========================================================
	def fillFromFile(me, sFileFullName): 
	#=========================================================
		me.resetPassFilter()	
		return me.passFromFile(sFileFullName,"f")
	#=========================================================
	def appendFromFile(me, sFileFullName): 
	#=========================================================
		me.resetPassFilter()	
		return me.passFromFile(sFileFullName,"a")
	#=========================================================
	def fillFromStore(me, oStore): 
	#=========================================================
		me.resetPassFilter()	
		return me.passFromStore(oStore,"f")
	#=========================================================
	def appendFromStore(me, oStore): 
	#=========================================================
		me.resetPassFilter()	
		return me.passFromStore(sFileFullName,"a")
		
	#=========================================================
	def writeToFile(me, sFileFullName): 
	#=========================================================
		me.resetPassFilter()	
		return me.passToFile(sFileFullName,"w")
		
	#=========================================================
	def appendToFile(me, sFileFullName): 
	#=========================================================
		me.resetPassFilter()	
		return me.passToFile(sFileFullName,"a")

	#=========================================================
	def passFromFile(me, sFileFullName, sBufferInMode):  # filtering from file to buffer
	#=========================================================
	# uses stop/skip/do/start- regex patterns set by a specific class method
	# picks selected part of selected lines from file
	# start and stop criterias shall usually be time stamp etc. matches
		bOperStatus = False
		sStatus = "FAIL"  # initial quess
		if not doesFileExist(sFileFullName):
			me.oTrace.INFO("'"+me.sDuty+ "' object access file '"+ sFileFullName +"' is missing")
			me.setObjectOperability(False)
			return bOperStatus
		else:
			me.oTrace.INFO("fill from file '"+ sFileFullName+"' for '"+me.sDuty+ "' ")

		if sBufferInMode == "f":  # "f" means here "fill"
			me.resetMainBuffer()
			
		fhInFile = open(sFileFullName)
		me.oTrace.INFO("start reading lines from file '" + sFileFullName + "'")
		for sLine in fhInFile:
			me.oTrace.INFO("line from file: '"+sLine+"'")
			if me.oPassFilterConfByJson != 0:   # configuration assignment check
				sStatus = me.checkLineByCfgPasses(sLine)
			else:
				sStatus = me.checkLineByPass(sLine) 
				if sStatus != "PASS":  # TO reduce log stuff
					me.oTrace.INFO("caller received status '"+sStatus+"'")
				
			if sStatus == "PASS":
				#print("line to save: '"+sLine+"'")
				me.oTrace.INFO("line to save: '"+sLine+"'")
				me.asMainBuffer.append(sLine)
				bOperStatus = True
			elif sStatus == "SKIP":
				continue  # next .i "for..."
			else:
				break # stopped, so end loop
		me.oTrace.INFO("final status '"+sStatus+"'")		
		me.updateEndPos()
		me.sAttachedFileName = sFileFullName		
		fhInFile.close()
		return bOperStatus

		# TODO: add possible error check
		
	#=========================================================
	def passFromStore(me, oSource, sBufferInMode):  # filtering from buffer to buffer (TBD: replace "fill" with "append")
	#=========================================================
	# uses stop/skip/do/start- regex patterns set by a specific class method
	# picks selected part of selected lines from file
	# start and stop criterias shall usually be time stamp etc. matches
		bOperStatus = False  # initial quess: will fail
		asSrcBuffer = oSource.getContents(me) 
		if sBufferInMode == "f":  # means here "fill"
			me.resetMainBuffer()

		for sLine in asSrcBuffer:
			if sLine == "EOB":
				return
			if me.oPassFilterConfByJson != 0:  # configuration assignment check
				sStatus = me.checkLineByCfgPasses(sLine)
			else:
				sStatus = me.checkLineByPass(sLine)
				
			if sStatus == "PASS":
				bOperStatus = True
				me.asMainBuffer.append(sLine)
			elif sStatus == "SKIP":
				continue  # next .i "for..."
			else:
				break # stopped, so end loop	
		me.updateEndPos()
		return bOperStatus

	#=========================================================
	def passToFile(me, sFileFullName, sFileOutMode):  # filtering from buffer to file
	#=========================================================
		# uses stop/skip/do/start- regex patterns set by a specific class method
		# TBD: add some flag usage to select fill vs. append
		me.oTrace.INFO("target file: '"+sFileFullName+"', mode='"+sFileOutMode+"'")
		bOperStatus = False
		if not isReasonableFileName(sFileFullName, me.oTrace):
			return bOperStatus
		me.sAttachedFileName = sFileFullName
		if not me.isFileWriteAllowed():
			return bOperStatus
			
		#sFileFullName = "J:/KIT/Python/TRAY/DotAutogenMain.cfg"

		me.oTrace.INFO("write to file '"+sFileFullName+"', mode = '"+sFileOutMode+"'")

		fhOutFile = open(sFileFullName,sFileOutMode) # "w" or "a"

		for sLine in me.asMainBuffer:
			if sLine == "EOB":
				return bOperStatus
			# print ("line = -------------------------------------- "+str(sLine)+"\n")
			if me.oPassFilterConfByJson != 0:   # configuration assignment check
				sStatus = me.checkLineByCfgPasses(sLine)
			else:
				sStatus = me.checkLineByPass(sLine)
				
			if sStatus == "PASS":
				bOperStatus = True
				fhOutFile.write(sLine)
			elif sStatus == "SKIP":
				continue  # next .i "for..."
			else:
				break # stopped, so end loop
		fhOutFile.close()
		
		return bOperStatus
		# TODO: add possible error check

	#=========================================================
	def checkLineByPass(me, sLine):  # 
	#=========================================================
		# pass filter values are scalars which are set by function calls
		sLinePassStatus = "STOP"
		sLine = sLine.rstrip()   # !: Python way for a "chomp"
		bLooping = True
		while bLooping == True:  # !: Pythonic way to exit from indented if-then-else constructions: a loop "wrapper"
			bLooping = False
			if me.bPassActive == True:
				oMatch = re.search(me.sStopPassRe, sLine)
				if oMatch:  # passing has been active but is stopped now
					#print("--------------stop collecting------------")
					#me.oTrace.INFO("---------------stop collecting -----------------------------")
					me.oTrace.INFO("stop collecting, because "+me.sStopPassRe+" did match to line '"+sLine+"'") # TBD: solve, why is missing in Trace file
					me.bPassActive = False
					sLinePassStatus = "STOP"
					break
				oMatch = re.search(me.sSkipPassRe, sLine)
				if oMatch:  # passing is active, but focus line is skipped
					sLinePassStatus = "SKIP"
					break
					#me.oTrace.INFO("'"+sCollectByRe+"' did NOT match to line '"+sLine+"'")
				oMatch = re.search(me.sDoPassRe, sLine)
				if oMatch: # passing is active and focus line is passed
					#me.oTrace.INFO("'"+sCollectByRe+"' did NOT match to line '"+sLine+"'")
					sLinePassStatus = "PASS"
					break
				else:
					abc = 123
					me.oTrace.INFO("collect, because '"+me.sDoPassRe+"' matches to line '"+sLine+"'")	
			else:   # passing has not been started at all 
				oMatch = re.search(me.sStartPassRe, sLine)
				if oMatch:   # passing started now
					me.oTrace.INFO("'start collecting, because "+me.sStartPassRe+" did match to line '"+sLine+"'")
					me.bPassActive = True
					me.bPassOccurred = True
					sLinePassStatus = "PASS"
					break
				
				else:   # passing not started
					#me.oTrace.INFO("'does not start collecting '"+sStartCollectingRe+"' did NOT match to line '"+sLine+"'")
					sLinePassStatus = "SKIP"
					break
		
		#me.oTrace.INFO("'"+sLine+"' caused status '"+sLinePassStatus+"'")
		return sLinePassStatus # for sure
		# TODO: add possible error check

	#=========================================================
	def assignPassFiltersCfg(me, oPassFilterConfByJson):  # 
	#=========================================================
		# TBD: make new version of THIS file, which uses preprocessing (=more complicated) JSON 170316
		me.oTrace.INFO("...")

		me.oPassFilterConfByJson 	= oPassFilterConfByJson
		me.asStartPassChoicesByCfg 	= me.oPassFilterConfByJson.getArrayInDoA("StartPassChoices") # must match the names in 
		me.asDoPassChoicesByCfg 	= me.oPassFilterConfByJson.getArrayInDoA("DoPassChoices")
		me.asSkipPassChoicesByCfg 	= me.oPassFilterConfByJson.getArrayInDoA("SkipPassChoices")
		me.asStopPassChoicesByCfg 	= me.oPassFilterConfByJson.getArrayInDoA("StopPassChoices")
		
	#=========================================================
	def detachPassFiltersCfg(me):  # 
	#=========================================================
		me.oTrace.INFO("...")
		me.oPassFilterConfByJson 	= 0
		
	#=========================================================
	def checkLineByCfgPasses(me, sLine):  # 
	#=========================================================
		# pass filter values are arrays which are downloaded from configuration JSON file
		me.oTrace.INFO("...")
		
		sLine = sLine.rstrip()   # !: Python way for a "chomp"
		if me.bPassActive == True:
			for sStopPassRe in me.asStopPassChoicesByCfg:
				oMatch = re.search(sStopPassRe, sLine)
				if oMatch:  # passing has been active but is stopped now
				#print("--------------stop collecting------------")
					#me.oTrace.INFO("---------------stop collecting -----------------------------")
					me.oTrace.INFO("stop collecting, because "+me.sStopPassRe+" did match to line '"+sLine+"'") # TBD: solve, why is missing in Trace file
					me.bPassActive = False
					return "STOP"
			for sSkipPassRe in me.asSkipPassChoicesByCfg:
				oMatch = re.search(sSkipPassRe, sLine)
				if oMatch:  # passing is active, but focus line is skipped
					return "SKIP"
					#me.oTrace.INFO("'"+sCollectByRe+"' did NOT match to line '"+sLine+"'")
			 
			for sDoPassRe in me.asDoPassChoicesByCfg:
				oMatch = re.search(sDoPassRe, sLine)
				if oMatch: # passing is active and focus line is passed
					#me.oTrace.INFO("'"+sCollectByRe+"' did NOT match to line '"+sLine+"'")
					return "PASS"

		else:   # passing has not been started at all 
			for sStartPassRe in me.asStartPassChoicesByCfg:
				oMatch = re.search(sStartPassRe, sLine)
				if oMatch:   # passing started now
					me.oTrace.INFO("'start collecting, because "+me.sStartPassRe+" did match to line '"+sLine+"'")
					me.bPassActive = True
					me.bPassOccurred = True
					return "PASS"
			
		return "SKIP" # default: no matches did occurr
		# TODO: add possible error check
		
	#=========================================================	
	def setPassFilter(me, sStartPassRe, sDoPassRe, sSkipPassRe, sStopPassRe):	
	#=========================================================
		# this has no effect, if pass configuration (JSON) object is assigned
		me.sStartPassRe 		= sStartPassRe
		me.sDoPassRe			= sDoPassRe
		me.sSkipPassRe			= sSkipPassRe
		me.sStopPassRe 			= sStopPassRe
		me.oTrace.INFO("pass filter: '"+me.sStartPassRe+"'/'"+me.sDoPassRe+"'/'"+me.sSkipPassRe+"'/'"+me.sStopPassRe+"'")
		me.bPassActive			= False
		me.bPassOccurred		= False
		me.detachPassFiltersCfg()
	
	#=========================================================	
	def resetPassFilter(me): 
	#=========================================================
	
		me.sStartPassRe 		= sEVERYTHING_MATCH_re # every possible line
		me.sDoPassRe			= sEVERYTHING_MATCH_re  # every possible line
		me.sSkipPassRe			= sVERY_IMPROBABLE_MATCH_re # impossible line
		me.sStopPassRe 			= sVERY_IMPROBABLE_MATCH_re # impossible line
		me.oTrace.INFO("pass filter: '"+me.sStartPassRe+"'/'"+me.sDoPassRe+"'/'"+me.sSkipPassRe+"'/'"+me.sStopPassRe+"'")
		me.bPassActive			= False
		me.bPassOccurred		= False
		me.detachPassFiltersCfg()
	
	#=========================================================
	def rawFillFromFile(me, sFileFullName): 
	#=========================================================
	# TBD: replace with proper call to filters setting and call to "fillPassFromFile()"
		if not doesFileExist(sFileFullName):
			print("'"+me.sDuty+ "' object access file is missing")
			me.bThisObjectIsOperable = False
			return False
			
		me.oTrace.INFO("file name '"+sFileFullName+"'")
		fhInFile = open(sFileFullName)
		me.asMainBuffer = fhInFile.read().splitlines()
		me.updateEndPos()    
		me.sAttachedFileName = sFileFullName
		fhInFile.close()
		return True

	#=========================================================
	def rawAppendFromFile(me, sFileFullName):  
	#=========================================================
		if not doesFileExist(sFileFullName):
			print("'"+me.sDuty+ "' object access file is missing")
			me.bThisObjectIsOperable = False
			return False
		me.oTrace.INFO("file name '"+sFileFullName+"'")
		fhInFile = open(sFileFullName)
		asAddBuffer = fhInFile.read().splitlines()
		me.asMainBuffer.extend(asAddBuffer)   # !: Python: arrays concatenation 
		me.updateEndPos()    
		me.sAttachedFileName = sFileFullName
		fhInFile.close()
		return True
		# TODO: add possible error check
				
	#=========================================================
	def rawWriteToFile(me, sFileFullName): 
	#=========================================================
		if not isReasonableFileName(sFileFullName, me.oTrace):
			return False
		me.sAttachedFileName = sFileFullName
		if not me.isFileWriteAllowed():
			return False
			
		me.oTrace.INFO("file name '"+sFileFullName+"'")
		fhOutFile = open(sFileFullName,"w")
		#fhOutFile.write("\n".join(me.asMainBuffer))
		#me.oTrace.INFO("---------------------------------------------------------------------")
		#for sLine in me.asMainBuffer:
			#me.oTrace.INFO(sLine)
		print("writes buffer of '"+me.sDuty+"' to file '"+sFileFullName+"'")
		fhOutFile.write("\n".join(map(str, me.asMainBuffer)))
		fhOutFile.close()
		
		return True
		
	#=========================================================
	def rawAppendToFile(me, sFileFullName):  # python constructor  # TODO: modify
	#=========================================================
		if not isReasonableFileName(sFileFullName, me.oTrace):
			return False
		me.sAttachedFileName = sFileFullName
		if not isFileWriteAllowed():
			return False
		me.oTrace.INFO("file name '"+sFileFullName+"'")
		fhOutFile = open(sFileFullName,"w+")
		fhOutFile.write("\n".join(me.asMainBuffer))
		fhOutFile.close()
		
		return True
	#=========================================================
	def clearAll(me): 
	#=========================================================
		me.rewind()
		me.asMainBuffer = []
		me.nMainBufferLastPos = 0
		me.nMainBufferSize = 0
		me.resetPassFilter()
		me.clearBookmark()
	#=========================================================
	def rewind(me, nOffsetPos =p_nVERY_IMPROBABLE_INTEGER):
	#=========================================================
		# goes to main buffer start or to position relative to latest bookmark
		if nOffsetPos == p_nVERY_IMPROBABLE_INTEGER:
			me.nMainBufferPos = -1 # goes to buffer start "getStoreNextLine()" gives line 0
		else:
			me.nMainBufferPos = me.nMainBufferBookmarkPos + nOffsetPos # zero gives bookmark line "N", after that "getStoreNextLine()" gives line "N+1"
		me.oTrace.INFO("pos to "+str(me.nMainBufferPos))
			# if bookmark is not set, then the offset position is same as absolute position
	#=========================================================
	def setBookmark(me):  
	#=========================================================
		me.nMainBufferBookmarkPos = me.asMainBufferPos
		
	#=========================================================
	def clearBookmark(me):  
	#=========================================================
		me.nMainBufferBookmarkPos = -1
	
	#=========================================================
	def updateEndPos(me): 
	#=========================================================
		#me.asMainBuffer.append("EOB") # to indicate buffer end 
		me.nMainBufferSize = len(me.asMainBuffer)
		me.nMainBufferLastPos = me.nMainBufferSize-1    # if size = 4, then last pos = 3  (0,1,2,3)
		me.oTrace.INFO("'"+me.sDuty+"' text buffer last position: '"+str(me.nMainBufferLastPos)+"'")
	
	#=========================================================
	def getStoreNextLine(me):
	#=========================================================
		if me.nMainBufferSize == 0:  # buffer not filled at all
			me.oTrace.INFO("FAIL: main buffer is empty")
			return "EOB"
		me.nMainBufferPos += 1
		me.oTrace.INFO("main buffer pos/last = "+str(me.nMainBufferPos)+"/"+str(me.nMainBufferLastPos))
		if me.nMainBufferPos > me.nMainBufferLastPos:
			sRet = "EOB"   # End Of Buffer
		else:
			sRet = (me.asMainBuffer[me.nMainBufferPos]).rstrip()
			me.sMainBufferPos = str(me.nMainBufferPos)
		me.oTrace.INFO("sRet = '"+sRet+"'")
		nPosRet = me.nMainBufferPos
		sPosRet = str(nPosRet) # for logging purposes
		#return sRet, nPosRet, sPosRet   # TBD: return only the line
		return sRet
	#=========================================================
	def getStoreNextLinesArray(me,nCount):
	#=========================================================
		asRetLines = ()
		if me.nMainBufferSize == 0:  # buffer not filled at all
			me.oTrace.INFO("FAIL: main buffer is empty")
			return "EOB"
		for pos in range(0, nCount):
			sline = me.getStoreNextLine()
			if sLine == "EOB":
				return 0
			else:
				asRetLines.append(sline)
		return asRetLines

	#=========================================================
	def replaceNowNextLinesWithSingleTaggedLine(me,nCount):  # TBD: make unit test
	#=========================================================
		asLines = me.getStoreNextLinesArray(nCount)
		sSingleTaggedLine = me.buildSingleLineFromMultipleLines(asLines)
		removeArray(me.nMainBufferPos, nCount)
		me.nMainBuffer[me.nMainBufferPos] =  sSingleTaggedLine
		return sSingleTaggedLine

	#=========================================================
	def getStoreSameLineAgain(me):
	#=========================================================
		if (me.nMainBufferPos < 0):
			sRet = me.goStartGetLine()
		else:
			sRet = (me.asMainBuffer[me.nMainBufferPos]).rstrip()
		return sRet
	#=========================================================
	def goStartGetLine(me): 
	#=========================================================
		me.oTrace.INFO("rewind main buffer")
		me.nMainBufferPos = -1
		sLine = me.getStoreNextLine()
		return sLine
	#=========================================================
	def goRelPosGetLine(me, nOffset): 
	#=========================================================
		# to navigate to given pos after match eg.
		nNewAbsPos = nOffset - 1 + me.nMainBufferPos #  '1' substracted because "getStoreNextLine()" will increase it
		me.oTrace.INFO("set main buffer position '"+str(nNewAbsPos)+"'")
		if nNewAbsPos > -1:
			me.nMainBufferPos = nNewAbsPos
			sLine = me.getStoreNextLine()
		else:
			sline = "EOB"
		return sLine

	#TBD: method, which replaces those multiple lines with single flattened file (if regex match)
	#TBD: method, which replaces focus line with given string (if regex match)
	#TBD: method, which replaces focus line with line of sequence of captures (if regex match)
	#TBD: method, which replaces focus line with multiple lines generated if array in regex match
	#=========================================================
	def getCurrentPos(me): 
	#=========================================================
		return me.nMainBufferPos

	#=========================================================
	def addText(me, sText): 
	#=========================================================
		me.asMainBuffer.append(sText)   # can contain multiple '\n' -terminated lines !!!
		me.updateEndPos() 
		
	#=========================================================
	def addArray(me, asText): 
	#=========================================================
		# https://codecomments.wordpress.com/2008/03/19/append-a-list-to-a-list-in-python/
		for sText in asText:
			me.oTrace.INFO("add to result: '"+sText+"'")
			me.asMainBuffer.append(sText) # !: Python: appending list to list 
		me.updateEndPos() 

	#=========================================================
	def insertLine(me, sLine, nPos):  #
	#=========================================================
		me.oTrace.INFO("insert line to buffer pos "+str(nPos))
		me.asMainBuffer.insert(sLine, nPos) #
		me.updateEndPos()
	#=========================================================
	def removeLine(me, nPos):  #
	#=========================================================
		sLine = me.asMainBuffer[nPos]
		me.oTrace.INFO("removes '"+sLine+"'["+str(nPos)+"]")
		me.asMainBuffer.pop(nPos)
		me.updateEndPos()
	#=========================================================
	def insertArray(me, asAddBlock, nPos):  # 
	#=========================================================
		me.oTrace.INFO("insert array to buffer pos "+str(nPos))
		me.asMainBuffer[nPos:nPos] = asAddBlock # Python "splice" (see Perl)
		me.updateEndPos()

	#=========================================================
	def removeArray(me, nPos, nCount):  #
	#=========================================================
		me.oTrace.INFO("remove "+str(nCount)+" lines starting at pos"+str(nPos))
		for i in range (nCount-1):
			me.asMainBuffer.pop(i) # !: TBD: check, if transfers rest stuff backwards
		me.updateEndPos()
	#=========================================================
	def replaceNowLineWithLinesSeq(me, sRE, sTrapTagsWithPrefixes):  #
	#=========================================================
		# DOES: replaces focus line with lines which are built from regex captures
		# some trap tags can have array indication prefixes "@"
		# the total amount of result lines is equal of combinations of those arrays
		sNowLine = me.asMainBuffer[me.nMainBufferPos]
		sNowLine = sNowLine.rstrip()
		asAddLinesArray = me.buildMultipleLinesFromSingleLine(sNowLine, sRE, sTrapTagsWithPrefixes)
		sAddBlockAsStr = arrayToStr(asAddLinesArray,"<NL>")
		me.oTrace.INFO("replace buffer line '" + sNowLine + "' with array '" + sAddBlockAsStr + "\n")
		me.asMainBuffer[me.nMainBufferPos] = "" # clears the seed line
		me.insertArray(asAddLinesArray, me.nMainBufferPos+1)
	#=========================================================
	def pickChangedLines(me, sCompareRe, sInfoLineTpl, sTagIndRe): # TBD
	#=========================================================
	#  TBD: add here template usage for repeated-info line
	#	-	a "leaner" way than usage of the actual "ReportUtils"
	# - the feed buffer here can be a raw file input or a reporting operation output
	# - separate regex filtering here is necessary to ignore effect of instantiative data (eg time stamps)
	# 	and still be able to present that data in instance line which presents the first line of sequences
	# DOES: collects lines which are not similar to previous line
	# - a regex defines the parts which form the difference criteria
	# - a template defines the form which picked line is converted
	#  - multiple similar sequential lines will result an indication of the amount of similar lines

		asChangedLineItems = []
		sBaledPrevLine = ""
		nRepeatedCnt = 1  # initialization
		a=123  # Python: any function needs some code to prevent an error
		me.rewind()
		#TBD: add usage of object parameters
		while True:
			sLine = me.getStoreNextLine()
			if sLine == "EOB":
				break
			# TBD: change to use TrickUtils method tryMatchAndTrap()
			sStatus, dValByPosNbrKeys =  tryMatchAndTrap(sLine, sCompareRe, me.oTrace)
			#sStatus, dValByPosNbrKeys =  tryMatchOrCatchToDict(sLine, sCompareRe, me.oTrace)
			if sStatus != "NOT_MATCH":
				sBaledLine = seqDictValuesToStr(dValByPosNbrKeys, "","")
			if sBaledLine == sBaledPrevLine:
				nRepeatedCnt += 1
			if nRepeatedCnt > 1:
				sRepeatedCnt = str(nRepeatedCnt)
				dValues["RepeatedCount"] = sRepeatedCnt  # following template must contain identically named tag 
				# TBD: change to use TrickUtils method
				sInfoLine =  fillAndOrEvaluateTemplateItem(dValByPosNbrKeys, sInfoLineTpl, sTagIndRe, me.oTrace)
				asChangedLineItems.append(sInfoLine)
			asChangedLineItems.append(sLine)
			nRepeatedCnt = 1
			
			sBaledPrevLine = sBaledLine

		return asChangedLineItems
			
	#=========================================================
	def removePairedAreas(me, sStartPair, sEndPair): 				# eg. "/*"  and "*/"
	#=========================================================
		me.asSwapBuffer = []
		# TBD
		for sBufferLine in me.asMainBuffer:
			me.asSwapBuffer.append(sText)   # can contain multiple '\n' -terminated lines !!!
		me.asMainBuffer = me.asSwapBuffer
		me.updateEndPos() 

	#=========================================================
	def removeLineTailsByTags(me, asTailStartTags): 				# eg. "//" and "#"
	#=========================================================
	# TBD: removes possible tags and line contents after the tags
	# can be used to remove typical line end comments
	# see. http://stackoverflow.com/questions/1706198/python-how-to-ignore-comment-lines-when-reading-in-a-file
	
		me.oTrace.INFO("removes possible tails")
		me.asSwapBuffer = []
		for sBufferLine in me.asMainBuffer:
			for sTailStartTag in asTailStartTags:  # for each tag in array
				#me.oTrace.INFO("removes possible tail started by '"+sTailStartTag+"' from line '"+sBufferLine+"'" )
				sPrefixLine = sBufferLine.split(sTailStartTag, 1)[0]
				sPrefixLine = sPrefixLine.rstrip()
				if sPrefixLine != sBufferLine:  # tagged tail removed, so no need to search other tail tag
					break
			if sPrefixLine != "":  # final or original empty lines
				me.asSwapBuffer.append(sPrefixLine) 
		me.asMainBuffer = me.asSwapBuffer
		me.updateEndPos() 
	
	
	# http://stackoverflow.com/questions/3589615/how-do-i-store-then-retrieve-python-native-data-structures-into-and-from-a-file
	
	#=========================================================
	def findNext(me, sSearchRe):  # 
	#=========================================================
	# a "pos" means here the position in buffer (one "line" may contain multiple '\n' -terminated lines)
	# searches next Line by given regex  in BufferLines -array
	# TBD: add return of array of groups
		nPosRet = -1
		sLine = ""
		oRE = re.compile(sSearchRe)
		
		me.oTrace.INFO("")
		while True:
			sLine = me.getStoreNextLine() # 'sLine' changed to 'sLine', because it can contain '\n' -separated strings
			if sLine == "EOB": 
				break  
			oMatch = oRE.match(sLine)
			if oMatch:
				nPosRet = me.nMainBufferPos
				break  # skips out of for -loop
			
	
		return (nPosRet, sLine)
	#=========================================================
	def findAnyNext(me, asSearchRe):  # 
	#=========================================================
	# a "pos" means here the position in buffer (one "line" may contain multiple '\n' -terminated lines)
	# searches next Line by given regex  in BufferLines -array
	# TBD: add return of array of groups
		nPosRet = -1
		sLine = ""
		bLooping = True
		sSearchRe = "MISSING"
		
		while bLooping:
			sLine  = me.getStoreNextLine() # 'sLine' changed to 'sLine', because it can contain '\n' -separated strings
			if sLine == "EOB":
				bLooping = False
				break
			for sSearchRe in asSearchRe:
				oRE = re.compile(sSearchRe)
				oMatch = oRE.match(sLine)
				if oMatch:
					nPosRet = me.nMainBufferPos
					bLooping = False
					break  # skips out of for -loop
			
		return nPosRet, sSearchRe, sLine

	#============================================================	
	def findByIncSearch(me, sIncrementalSearchSeq):   # 
	#============================================================
	
		asAllSearchStr = sIncrementalSearchSeq.split('|')
		me.oTrace.INFO("search sequence splitted to "+str(asAllSearchStr))
		sFirstEmptyIten = asAllSearchStr.pop(0)
		nSearchStrCnt = len(asAllSearchStr)
		nRetPos = -1  # initialization

		nSearchStrPos = 0
		bAllFound = False
		me.oTrace.INFO("try pop search str")
		
		sSearchStr = asAllSearchStr.pop(0)  # !: "pop()" without index returns from array end !!! 
		me.oTrace.INFO("popped first search string: '"+sSearchStr+"'")
		while True:
			sLine  = me.getStoreNextLine()
			if sLine == "EOB": 
				break
			me.oTrace.INFO("try find '"+ sSearchStr + "' at Line ["+sPos+"] "+sLine)
			if sSearchStr in sLine:
				me.oTrace.INFO("string "+ sSearchStr + " found at Line ["+sPos+"] "+sLine)
				if len(asAllSearchStr) != 0:
					sSearchStr = asAllSearchStr.pop(0)
				else:
					bAllFound = True
					nRetPos = me.nMainBufferPos
					me.oTrace.INFO("all search strings found OK, buffer pos = "+sPos)
					break
		if bAllFound == False:
			me.oTrace.INFO("all search strings NOT found")
		

		return nRetPos
		
# TODO: add method which updates notetab otl daily topic file filled buffer
