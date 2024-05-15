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
from StateUtils import *
from TextItemUtils import *

# TBD: change all "Full" strings to "Whole" strings (mainly in file name symbols) (180320)
 

# TBD: create method <fill from array>

 # to indicate, that caller shall not pass anything yet

# http://stackoverflow.com/questions/29214888/typeerror-cannot-create-a-consistent-method-resolution-order-mro

# there are different "levels" of file handling:
#  FILTER:  configuration data is in JSON file. input and output files can come and go anywhere
#  EDIT:    configuration data and output template data are in same JSON file
#			input lines are from this class object main buffer and output lines are written to given file
#  REPORT:  extraction data and output template data are in separate JSON files

# the term "extract" shall exist only in <REPORT UTILS> file


# 170610: eg, graphviz  diagramming is done now:
#|feed file|-->(filtering) --> |filtered file| --> (editing) --> |edited file| ---> (report generation) ---> |<file.dot>|



#=============================================================
class ex_RETURN_TO_CALLER(Exception):    # !: Python: making own exception to get "goto" -alike exit from nested loops
	def __init__(me):
		pass
#=============================================================


class clTextStorage(clTextItems):   
# uses JSON configuration file

# PURPOSE:
# read from files
# write to file

# generate new buffers from manipulated and data
# combine multiple files contents
# read configuration files to manipulate buffer contents
# similar to JSON usage: https://wiki.python.org/moin/UsingPickle
# https://pythontips.com/2013/08/02/what-is-pickle-in-python/

# TBD: versatile methods to filter lines when reading, copying and writing files
#----- by external configuration (JSON) file object --------------------
# most comprehensive extract & report operations are done in "ReportingUtils.py"
# the operations in this module can be used for preprocessing files to make actual reporting easier and more versatile


	#=========================================================
	def __init__(me, sDuty, oTrace, sTheseDriveLetter="N/A", sCreatorPath="N/A", sCreatorName="N/A"):  # python constructor
	#=========================================================
		# trace file opens/closes are handled by main script, not in objects
		#TBD: buffer type setting in constructor to reduce accidental writing to input files


		me.oTrace = oTrace
		me.sDuty = sDuty  # means the "task" or "role" of the object. Mainly used to improve Trace Log


		#====================================================================
		# TBD: why these are not visible in child-child -class ???
		me.nFlowAbsoluteLineNbr = 0  # e.g. original feed file line number
		me.nFlowRelativeLineNbr = 0 # some subset of ignored or picked lines
		# =================================================================== TODO
		
		#clParams.__init__(me, sDuty, oTrace)  #
		clTextItems.__init__(me, sDuty, oTrace)  # # - parent class contains already 'clParams'

		me.oTrace.INFO("started constructor for '" + sDuty + "'","kick")
		me.setOperability(True, "initial quess")  # initial quess
		me.sTheseDriveLetter = sTheseDriveLetter
		me.sCreatorPath = sCreatorPath
		me.sCreatorName = sCreatorName  # creator script name
		
		me.asMainBuffer = []
		me.nMainBufferSize = 0
		me.nMainBufferLastPos = 0
		me.nMainBufferPos = -1
		me.sMainBufferPos = ""
		me.nMainBufferBookmarkPos = -1  # for navigation
		me.asSwapBuffer = []  # workspace when removing lines etc.
		me.bMainBufferLinesEnded = False  # (= "EOB" not found)
		# -----------------------------------
		me.dThisObjParams = {}  # local configuration data
		
		me.bAllowWritingToAttachedFile = True  # initial quess
		# ---------------------------------------------
		me.clearAll()
		
		
		# me.sDateTime = datetime.now()
		# e,g. for enable/disable rnput or output lines amount evaluation
		
		
		me.XoYextractorsRoot = 0  # JSON-to-python conversion result "anchor" # TBD: add method usage
		me.XoYtemplatesRoot = 0	  # JSON-to-python conversion result "anchor" # TBD: add method usage

		me.sAttachedInFileName = "" # TBD: activate
		me.sAttachedOutFileName = "" # TBD: activate
		me.fhOutFile=0  # created via wrapper methods, but I/O is done via built-in methods
						# ---> better error check and tracing
		me.fhInFile=0	# created via wrapper methods, but I/O is done via built-in methods
		# TBD: maybe similar for <input file>
		me.oTrace.INFO("ended constructor for '" + sDuty + "'","kick")

	#################################################################################################
	#=========================================================
	def returnToCaller(me, sComment):     # simulates "goto" -command
	# =========================================================
		me.oTrace.INFO("raised exception for: '" + sComment + "'", "kick")
		raise ex_RETURN_TO_CALLER  # !: Python: explicit generation of exception
    ######################################################################################################

	# TBD: collect all file IO in this class 170826

	# versatile I/O: https://docs.python.org/2/tutorial/inputoutput.html

#################################################################################################################################
# ALL FILE OPEN/CLOSE operations are done in this group of functions


#===== START: line flow counters ===========================================
	#========================================================
	def incFlowAbsoluteLineNbr(me):  # plain assignment of file name is justpractical in some cases
	#=========================================================
		me.nFlowAbsoluteLineNbr += 1
	#=========================================================
	def getFlowAbsoluteLineNbr(me):  # plain assignment of file name is justpractical in some cases
	#=========================================================
		return me.nFlowAbsoluteLineNbr
	#=========================================================
	def incFlowRelativeLineNbr(me):  # plain assignment of file name is justpractical in some cases
	#=========================================================
		me.nFlowRelativeLineNbr += 1
	#=========================================================
	def getAndResetFlowRelativeLineNbr(me):  # plain assignment of file name is justpractical in some cases
	#=========================================================
		nRetVal = me.nFlowRelativeLineNbr
		if nRetVal == 0:
			me.oTrace.INFO("'"+me.sDuty+ "':value has not been updated since previous request !!!")
		me.nFlowRelativeLineNbr =0
		return nRetVal
	#=========================================================
	def getAndResetPeriodFlowLineSeqNbr(me):  # plain assignment of file name is justpractical in some cases
	#=========================================================
		me.nFlowRelativeLineNbr = 0
	#===== END: line flow counters ===========================================
	
	
	#=========================================================
	def getAttachFileNamesInfo(me, sFileName="DEFAULT"):  # plain assignment of file name is justpractical in some cases
	#=========================================================
		sInputRetInfo 	= ""
		sOutputRetInfo  	= ""
		if me.sAttachedInFileName != "":
			sInputRetInfo = "input file: [" + me.sAttachedInFileName + "]"
			
		if me.sAttachedOutFileName != "":
			sOutputRetInfo = "output file: [" + me.sAttachedOutFileName + "]"
		return sInputRetInfo + " " + sOutputRetInfo

	#=========================================================
	def attachReadFile(me, sFileName="DEFAULT"):  # plain assignment of file name is justpractical in some cases
	#=========================================================
		if sFileName == "DEFAULT":  # file name is already attached
			sFileName = me.sAttachedInFileName
			
		else:
			me.attachInputFile(sFileName)

		if not doesFileExist(sFileName):
			print("'" + me.sDuty + "' object access file '" + sFileName + "' is missing")
			me.oTrace.INFO("'" + me.sDuty + "' object access file '" + sFileName + "' is missing")
			me.setOperability(False,"File '"+sFileName +"' does not exist")
			bRetStatus = False
		else:
			me.oTrace.INFO("file ["+sFileName+"] is available")
			
			bRetStatus = True
		return bRetStatus

	#=========================================================
	def openInFile(me, sFileName="DEFAULT"):  # file name can be attached here or use previously attached file name
	#=========================================================
		if sFileName == "DEFAULT":  # file name is already attached
			sFileName = me.sAttachedInFileName
		bRetStatus = True
		if not doesFileExist(sFileName):
			
			me.oTrace.INFO("'" + me.sDuty + "' object access file '" + sFileName + "' is missing")
			me.setOperability(False,"'" + me.sDuty + "' object access file '" + sFileName + "' is missing")
			bRetStatus = False
		else:
			me.oTrace.INFO("file [" + sFileName + "] is available")
			try:
				me.fhInFile = open(sFileName)
				me.attachInputFile(sFileName)
				me.setOperability(True)
				me.bAllowWritingToAttachedFile = False
				me.oTrace.INFO("'" + me.sDuty + "' object succeeded to open read file '[" + sFileName + "]'")
			except:
				exctype, value = sys.exc_info()[:2]  # !: very comprehensive output
				errorText = str(exctype) + " " + str(value)
				me.oTrace.INFO(errorText,"except")
				me.fhInFile = 0
				me.setOperability(False," failed to open read file '[" + sFileName + "]' because " + errorText)
		return bRetStatus

	#=========================================================
	def closeInFile(me):
	#=========================================================
		if me.isOperable():
			me.fhInFile.close()
			me.oTrace.INFO("'" + me.sDuty + "' closed input file ["+ me.sAttachedInFileName +"]")
		else:
			me.oTrace.INFO("'" + me.sDuty + "' tried to close inoperable input file [" + me.sAttachedInFileName + "]")
	#=========================================================
	def closeOutFile(me):  # for both "write" and "append"
	#=========================================================
		if me.isOperable():
			me.oTrace.INFO("'" + me.sDuty + "' object:  closed output file '["+ me.sAttachedOutFileName+"]' " )
			me.fhOutFile.close()
		else:
			me.oTrace.INFO("'" + me.sDuty + "' object:  tried to close inoperable output file '" + me.sAttachedOutFileName + "' ")


	#=========================================================
	def attachWriteFile(me, sFileName="DEFAULT"):  # for either "write" or "Append"
	#=========================================================
		me.attachOutputFile(sFileName)

	#=========================================================
	def attachInputFile(me, sFileName="DEFAULT"):
	#=========================================================
		# TBD: add assuring an absolute path name
		if me.sAttachedInFileName != sFileName:
			print("attach input file name: '" + sFileName + "'\n")
			me.sAttachedInFileName = sFileName
			me.oTrace.INFO("attach file for INPUT: '" + me.sAttachedInFileName+ "' at object '"+me.sDuty+"'")
			#addStrToFileIfNotAlready(sFileName, me.getParam('parFileNamesFile'), me.oTrace)
			#addStrToFileIfNotAlready(sFileName, clParams.p_sFileNamesFile, me.oTrace)     # Class variable access
			
	
	#=========================================================
	def attachOutputFile(me, sFileName="DEFAULT"):  #
	#=========================================================
		# TBD: add assuring an absolute path name
		if me.sAttachedOutFileName != sFileName:
			print("attach output file name: '" + sFileName + "'\n")
			me.oTrace.INFO("attach file for OUTPUT: '" + me.sAttachedOutFileName + "' at object '" + me.sDuty + "'")
			me.sAttachedOutFileName = sFileName

	#=========================================================
	def openWriteFile(me, sFileName= "DEFAULT"):  # file name can be attached here or use previously attached file name
	#=========================================================
		if sFileName == "DEFAULT":  # file name is already attached
			sFileName = me.sAttachedOutFileName
		bRetStatus = True
		if isReasonableFileName(sFileName, me.oTrace):
			try:
				me.attachOutputFile(sFileName)
				me.fhOutFile = open(sFileName,"w")
				me.setOperability(True)
				me.bAllowWritingToAttachedFile = True
				
				# me.oTrace.INFO("'" + me.sDuty + "' object succeeded to open write file '" + sFileName + "'")
			except:
				exctype, value = sys.exc_info()[:2]  # !: very comprehensive output
				errorText = str(exctype) + " " + str(value)
				me.oTrace.INFO(errorText,"except")
				me.fhOutFile = 0
				me.setOperability(False," failed to open write file '" + sFileName + "' because " + errorText)
		return bRetStatus

	#=========================================================
	def openAppendFile(me, sFileName):   # file name can be attached here or use previously attached file name
	#=========================================================
		if sFileName == "DEFAULT":  # file name is already attached
			sFileName = me.sAttachedOutFileName
		bRetStatus = True
		if not doesFileExist(sFileName):  # 'append' assumes existing file

			me.setOperability(False," append file '" + sFileName + "' is missing")
			bRetStatus = False
		else:
			me.oTrace.INFO("file [" + sFileName + "] is available")
			try:
				me.fhOutFile = open(sFileName,"w+")
				
				me.attachOutputFile(sFileName)
				
				me.setOperability(True)
				me.bAllowWritingToAttachedFile = True
				
				me.oTrace.INFO("'" + me.sDuty + "' object succeeded to open append file '" + sFileName + "'")
			except:
				exctype, value = sys.exc_info()[:2]  # !: very comprehensive output
				errorText = str(exctype) + " " + str(value)
				me.oTrace.INFO(errorText,"except")
				me.fhOutFile = 0
				me.setOperability(False," failed to open append file '" + sFileName + "' because " + errorText)
		return bRetStatus


##################################################################################################################
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
		me.bMainBufferLinesEnded = False
	#=========================================================
	def setReadOnly(me):
	#=========================================================
		me.bAllowWritingToAttachedFile = False # to prevent accidental writing to typically read-only files (source code, configuration,...)
			
	#=========================================================
	def isFileWriteAllowed(me):  
	#=========================================================
		bStatus = me.bAllowWritingToAttachedFile
		if bStatus == False:
			me.oTrace.INFO("prevented attemption to write file '"+me.sAttachedOutFileName+"'")
		return bStatus
	#=========================================================
	def getContents(me):  
	#=========================================================
		return me.asMainBuffer

	#=========================================================
	def CopyFromFileToFile(me, oStore):
	#=========================================================
		pass
	#====================================================
	def appendToFileIfLinesExist(me, sFileName, asAddLines):
	#=====================================================
		if asAddLines:
			me.oTrace.INFO("add array to file '" + sFileName + "'","topic")
			me.arrayWriteToFile(asAddLines, sFileName)
		else:
			me.oTrace.INFO("empty array not added to file '"+sFileName+"'")

	#=========================================================
	def checkIfLinesEnded(me):
	#=========================================================
		if me.bMainBufferLinesEnded == True:
			me.oTrace.INFO("last feed line was already used")
			return True
		else:
			return False

	#=========================================================
	def rawFillFromFile(me, sFileName="DEFAULT"):
	#=========================================================

		if sFileName == "DEFAULT":
			sFileName = me.sAttachedInFileName
		
		if not doesFileExist(sFileName):  # 'append' assumes existing file
			me.setOperability(False,"'" + me.sDuty + "' raw input file '" + sFileName + "' is missing")
			return False
		else:
			me.oTrace.INFO("file [" + sFileName + "] is available")
		# me.attachInputFile(sFileName)

	

		bStatus = me.openInFile(sFileName)  # wrapper for file open -operation added 170826
		if bStatus == False:
			return False
	
		me.asMainBuffer = me.fhInFile.read().splitlines() # no wrapper for I/O operations
		me.updateEndPos()

		sBufferSize = str(me.nMainBufferSize)

		me.oTrace.INFO("retrieved '"+sBufferSize+"' lines from file [" + sFileName + "]")
		me.closeInFile()    # wrapper for file close -operation
		return True

	#=========================================================
	def rawAppendFromFile(me, sFileName="DEFAULT"):
	#=========================================================
		if sFileName == "DEFAULT":
			sFileName = me.sAttachedInFileName
		bStatus = me.openInFile(sFileName)  # wrapper for file open -operation added 170826
		if bStatus == False:
			return False


		me.attachInputFile(sFileName)

		asAddBuffer = me.fhInFile.read().splitlines()    # no wrapper for I/O operations
		sBufferSize = str(len(asAddBuffer))
		me.oTrace.INFO("retrieved '" + sBufferSize + "' lines from file [" + sFileName + "]")
		me.asMainBuffer.extend(asAddBuffer)   # !: Python: arrays concatenation 
		me.updateEndPos()


		me.attachInputFile(sFileName)



		

		me.closeInFile()  # wrapper for file close -operation

		return True
		# TODO: add possible error check
				
	#=========================================================
	def rawWriteToFile(me, sFileName="DEFAULT"):
	#=========================================================
		if sFileName == "DEFAULT":
			sFileName = me.sAttachedOutFileName

		#me.attachOutputFile(sFileName)
		bStatus = me.openWriteFile(sFileName)  # wrapper for file open -operation added 170826
		if bStatus == False:
			return False



		sArraySize = str(len(me.asMainBuffer))


		me.oTrace.INFO("writes file '" + sFileName + "'","topic")
		me.oTrace.INFO("writes buffer of '"+sArraySize+"' items from '"+me.sDuty+"' to file ["+sFileName+"] and closes it")
		me.fhOutFile.write("\n".join(map(str, me.asMainBuffer)))
		me.closeOutFile()
		return True

	#=========================================================
	def arrayWriteToFile(me, asArray, sFileName="DEFAULT"):
	#=========================================================
	# here file is created from external array, not from object storage buffer
	
		if sFileName == "DEFAULT":
			sFileName = me.sAttachedOutFileName
		
		bStatus = me.openWriteFile(sFileName)  # wrapper for file open -operation added 170826
		if bStatus == False:
			return False

		me.attachOutputFile(sFileName)
		sArraySize = str(len(asArray))
		me.oTrace.INFO("'" + me.sDuty +"' writes given array of '"+sArraySize+"' items to file [" + sFileName + "] and closes it")
		me.fhOutFile.write("\n".join(map(str, asArray)))
		
		me.closeOutFile()
		
		return True

	# =========================================================
	def appendLineToFile(me, sLine):  # single line to already opened file
	# =========================================================
		if me.fhOutFile:
			me.fhOutFile.write(sLine+"\n")
		else:
			me.oTrace.INFO("object '" + me.sDuty + "': failed to append '"+ sLine+"' to file [" + me.sAttachedOutFileName+"]")
		return True

	#=========================================================
	def rawAppendToFile(me, sFileName="DEFAULT"):  # python constructor  # TODO: modify
	#=========================================================
		if sFileName == "DEFAULT":
			sFileName = me.sAttachedOutFileName

		bStatus = me.openAppendFile(sFileName)  # wrapper for file open -operation added 170826
		if bStatus == False:
			return False

		me.attachOutputFile(sFileName)

		me.fhOutFile.write("\n".join(me.asMainBuffer))
		me.closeOutFile()
		return True

	#=========================================================
	def clearAll(me): 
	#=========================================================
		me.rewind()
		me.asMainBuffer = []
		me.nMainBufferLastPos = 0
		me.nMainBufferSize = 0

		me.clearBookmark()
	#=========================================================
	def rewind(me, nOffsetPos = p_nVERY_IMPROBABLE_INTEGER):
	#=========================================================
		# goes to main buffer start or to position relative to latest bookmark
		if nOffsetPos == p_nVERY_IMPROBABLE_INTEGER:
			me.nMainBufferPos = -1 # goes to buffer start "getStoreNextLine()" gives line 0
		else:
			me.nMainBufferPos = me.nMainBufferBookmarkPos + nOffsetPos # zero gives bookmark line "N", after that "getStoreNextLine()" gives line "N+1"
		#me.oTrace.INFO("pos to "+str(me.nMainBufferPos))
			# if bookmark is not set, then the offset position is same as absolute position
	#=========================================================
	def setBookmark(me):  
	#=========================================================
		me.nMainBufferBookmarkPos = me.asMainBufferPos
		me.oTrace.INFO("pos to " + str(me.nMainBufferPos))
		
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
		me.bMainBufferLinesEnded = False
		me.oTrace.INFO("'"+me.sDuty+"' text buffer last position: '"+str(me.nMainBufferLastPos)+"'","kick")
	
	#=========================================================
	def getStoreNextLine(me):
	#=========================================================
		if me.nMainBufferSize == 0:  # buffer not filled at all
			me.oTrace.INFO("FAIL: main buffer is empty, attached file =  "+me.getAttachFileNamesInfo())
			me.bMainBufferLinesEnded = True
			return "EOB"
		me.nMainBufferPos += 1

		if me.nMainBufferPos > me.nMainBufferLastPos:
			me.bMainBufferLinesEnded = True
			sRet = "EOB"   # End Of Buffer
		else:
			sRet = (me.asMainBuffer[me.nMainBufferPos]).rstrip()
			me.sMainBufferPos = str(me.nMainBufferPos)

		# me.oTrace.INFO("#1:  "+str(me.nMainBufferPos) + "/" + str(me.nMainBufferLastPos)+ "= '"+sRet+"'")
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
			me.bMainBufferLinesEnded = True
			return "EOB"
		for pos in range(0, nCount):
			sLine = me.getStoreNextLine()
			if me.checkIfLinesEnded():
				return 0
			else:
				asRetLines.append(sline)
		return asRetLines

	#=========================================================
	def replaceNowNextLinesWithSingleTaggedLine(me,nCount):  # TBD: make unit test
	#=========================================================
		asLines = me.getStoreNextLinesArray(nCount)
		sSingleTaggedLine = me.buildSingleLineFromMultipleLines(asLines)
		removeArray(me.nMainBufferPos, nCount)  # TBD: what ???
		me.nMainBuffer[me.nMainBufferPos] =  sSingleTaggedLine
		me.updateEndPos()
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
		me.bMainBufferLinesEnded = True
		sLine = me.getStoreNextLine()
		if me.checkIfLinesEnded():
			return "EOB"
		return sLine
	#=========================================================
	def goRelPosGetLine(me, nOffset): 
	#=========================================================
		# to navigate to given pos after match eg.
		nNewAbsPos = me.nMainBufferPos + nOffset - 1#  '1' substracted because "getStoreNextLine()" will increase it
		me.oTrace.INFO("set main buffer position '"+str(nNewAbsPos)+"'")
		if nNewAbsPos > - 1:
			me.nMainBufferPos = nNewAbsPos
			sLine = me.getStoreNextLine()
			if me.checkIfLinesEnded():
				return "EOB"
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
	def appendLine(me, sLine):
	#=========================================================
		me.asMainBuffer.append(sLine)   # for single line
		me.oTrace.INFO("add '" + sLine + "' within '"+me.sDuty+"'")
		me.updateEndPos()
	#=========================================================
	def appendArray(me, asLines):
	#=========================================================
		for sLine in asLines:
			me.oTrace.INFO("add to result: '"+sLine+"'")
			me.asMainBuffer.append(sLine) # !: Python: appending scalar to list
		me.updateEndPos()
	#=========================================================
	def addArray(me, asText): 
	#=========================================================
		# https://codecomments.wordpress.com/2008/03/19/append-a-list-to-a-list-in-python/
		for sText in asText:
			# me.oTrace.INFO("add to result: '"+sText+"'")
			me.asMainBuffer.append(sText) # !: Python: appending scalar to list
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
		asAddLinesArray = me.buildMultipleLinesFromSingleLine(sNowLine, sRE, sTrapTagsWithPrefixes)   # why does not exist ???
		sAddBlockAsStr = arrayToStr(asAddLinesArray,"<NL>")
		me.oTrace.INFO("replace buffer line '" + sNowLine + "' with array '" + sAddBlockAsStr + "\n")
		me.asMainBuffer[me.nMainBufferPos] = "" # clears the seed line
		me.insertArray(asAddLinesArray, me.nMainBufferPos+1)
	#=========================================================
	def pickChangedLines(me, sCompareRe, sInfoLineTpl, sTagIndRe): # TBD: remove this or move it to TextItemUtils
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
			if me.checkIfLinesEnded():
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
	def pickLinesBetweenTags(me, sStartTagRe, sEndTagRe ):
	#=========================================================
		# DUTY: collects all lines between start and end tags
		# for small (configuration) files, e.g. for picking <jsoncomm> lines between "@start" and "@end"
		bStartTagFound = False
		bEndTagFound = False
		oStartRe = re.compile(sStartTagRe)
		oEndRe = re.compile(sEndTagRe)
		me.asSwapBuffer = []

		# TBD
		for sBufferLine in me.asMainBuffer:
			me.oTrace.INFO("file line: "+sBufferLine)
			oMatch = oEndRe.match(sBufferLine)
			if oMatch:
				bEndTagFound = True
				if bStartTagFound == True:
					break # jumps out of loop
				else:
					continue
			oMatch = oStartRe.match(sBufferLine)
			if oMatch:
				bStartTagFound = True
				continue  # goes to next "for"
			if bStartTagFound:
				me.asSwapBuffer.append(sBufferLine)  # can contain multiple '\n' -terminated lines !!!
		# TBD: if line starts with
		if bStartTagFound == False:
			me.oTrace.INFO("ERROR: start tag not found by regex '"+sStartTagRe+"'")
		if bEndTagFound == False:
			me.oTrace.INFO("ERROR: end tag not found by regex '" + sEndTagRe + "'")

		me.asMainBuffer = me.asSwapBuffer
		me.updateEndPos()
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
			if me.checkIfLinesEnded():
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
			if me.checkIfLinesEnded():
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
	
		asAllSearchStr = sIncrementalSearchSeq.split("|")
		for sRE in asAllSearchStr:
			me.oTrace.INFO("search regex '" + sRE +"'")

		sFirstEmptyItem = asAllSearchStr.pop(0)
		nSearchStrCnt = len(asAllSearchStr)
		nRetPos = p_nIMPOSSIBLE_POS # initialization

		nSearchStrPos = 0
		bAllFound = False
		me.oTrace.INFO("try pop search str")
		try:
			sSearchStr = asAllSearchStr.pop(0)  # !: "pop()" without index returns from array end !!!
		except:
			me.oTrace.INFO("trying to get search regex","exception")
			sys.exit()
			
		me.oTrace.INFO("popped first search string: '"+sSearchStr+"'")
		try:
			while True:
				sLine  = me.getStoreNextLine()
				sPos =  str(me.getCurrentPos())
				if me.checkIfLinesEnded():
					break

				#me.oTrace.INFO("try find '"+ sSearchStr + "' at Line ["+sPos+"] "+sLine)
				if re.search(sSearchStr, sLine):
					me.oTrace.INFO("string "+ sSearchStr + " found at Line ["+sPos+"] "+sLine)
					if len(asAllSearchStr) != 0:
						sSearchStr = asAllSearchStr.pop(0)
					else:
						bAllFound = True
						nRetPos = me.nMainBufferPos
						me.oTrace.INFO("all search strings found OK, buffer pos = "+sPos)
						break
				else:
					me.oTrace.INFO("string " + sSearchStr + " NOT found at Line [" + sPos + "] " + sLine)
		except:
			me.oTrace.INFO("EXCEPTION", "exception")
		if bAllFound == False:
			me.oTrace.INFO("all search strings NOT found")
		return nRetPos
		
# TODO: add method which updates notetab otl daily topic file filled buffer
