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


#
# all "line capture regex" and "fill template line" functions shall be reside here
#	-	can be called from any object, not just from "ReportUtils"


import os.path
import re
import json
import time
#import datetime

from ParamUtils import *
from datetime import datetime
import subprocess
from itertools import *





###########################################################################################################
############# TRICKUTILS REGION ###########################################################################
###########################################################################################################

#TBD: remove functions here when moving them to "TextItemUtils" 170302

# TERMS:
#------------------------------------------------------------------
# "match" and "catch" (=verbs): operations
# "group"/"groups" (substantives): result of "catch"
# "trap"/"traps" (=substantives): storage of a single group "group"

#=============================================	
def doesFileExist(sAbsOrRelFileName):   # function is copied here for easier access than in "FileManage" object
#=============================================
	bFileStatus = False  # initial quess
	sFileName = sAbsOrRelFileName.strip()   # !: assures leading and trailing white characters absence
	if os.path.isfile(sFileName):
		bFileStatus = True
	return bFileStatus

#=============================================	
def isReasonableFileName(sAbsOrRelFileName,oTrace):   # for output file names
#=============================================
	bFileStatus = False  # initial quess
	sFileName = sAbsOrRelFileName.strip()   # !: assures leading and trailing white characters absence
	if sFileName != "" and sFileName != "MISSING":
		bFileStatus = True
	else:
		oTrace.INFO("string "+sFileName+" is not reasonable file name")
		
	return bFileStatus	
	
#=============================================	
def removePossiblePairChars(sText):
#=============================================
	sText = sText.replace("(", "")
	sText = sText.replace(")", "")
	sText = sText.replace("[", "")
	sText = sText.replace("]", "")
	sText = sText.replace("{", "")
	sText = sText.replace("}", "")
	return sText

#=============================================	
def findFirstInList(reMatchStr, asList):
#=============================================
	# TBD: change to handle regex
	nItemNbr=-1  # initial quess: not found
	for sStr in asList:
		nItemNbr = nItemNbr + 1
		if reMatchStr in sStr:
			continue
	return nItemNbr

#=============================================	
def createOtlTopicHeading(sName):   # transferred here because even TraceUtils may use this
#=============================================
	# TBD: transfer to NotetabUtils.py
	sTopicNameLine = p_sOtlTopicNameTpl.replace("__topic_name__", sName)   # TBD: better topic heading
	return sTopicNameLine

#=============================================	
def createOtlLink_remove(sFileName, sTopicName):   # transferred here because even TraceUtils may use this
#=============================================
	# TBD: transfer to NotetabUtils.py
	sOtlLinkToSidekickTopic = "["+sFileName+"::"+sTopicName+"]"
	return sOtlLinkToSidekickTopic	

# =============================================
def getFileNameParts(sPossibleFileFullName):  # transferred here because even TraceUtils may use this
	# =============================================
	sPathName = os.path.dirname(sPossibleFileFullName)
	sFileName = os.path.basename(sPossibleFileFullName)
	sFileExt = os.path.splitext(sPossibleFileFullName)[1]
	sFileBody = sFileName.replace(sFileExt, "")
	if sPathName != "":
		if not sPathName.endswith('"'):
			sPathName += "/"  # "standardizes" path name ending to contain a slash

	return (sPathName, sFileName, sFileBody, sFileExt)


# =============================================
def getFileNameBody(sPossibleFileFullName):
# =============================================
	# used eg. when building dos bat named similar to the script called in that bat

	sFileName = os.path.basename(sPossibleFileFullName)
	sFileExt = os.path.splitext(sPossibleFileFullName)[1]
	sFileNameBody = sFileName.replace(sFileExt, "")

	return sFileNameBody
# =============================================
def getTraceFileNamesByScriptNameRENAMED(sPossibleScriptFullName, sTraceFileRelDir):
# =============================================
	sScriptName = os.path.basename(sPossibleScriptFullName)
	sScriptExt = os.path.splitext(sPossibleScriptFullName)[1]
	sScriptBody = sScriptName.replace(sScriptExt, "")
	sTraceFileRelName = sTraceFileRelDir+"/"+sScriptBody+".trace"
	return (sTraceFileRelName)

#=============================================
def assureFileFullName(sPossibleFileName, sDefaultPathName):   # transferred here because even TraceUtils may use this
#=============================================
#   given file name is assumed to be either PLAIN or FULL
#	-	TBD: add handling of relative and partial path names
#   IF file name is not full THEN the path part is taken from the default path name
	sFileFullNameRet = sPossibleFileName # initial quess
	(sPathName, sFileName) = os.path.split(sPossibleFileName)
	if sPathName == "":  # path part is totally missing
		sFileFullNameRet = sDefaultPathName+"/"+sFileName
	elif not re.match(r"^s*\W\:.*", sPathName):  # path part is relative
		sFileFullNameRet = sDefaultPathName+"\\"+sPossibleFileName
	else:
		sFileFullNameRet = sPossibleFileName

	

	return sFileFullNameRet
	
'''
# TBD: delete these, because are transferred to <text item utils>
#  -    new modifier functions there like <seq number> require storable data
#=============================================
def lbl(sStr):
#=============================================
# converts or removes characters which are not valid within eg. Graphviz labels
# -	  long single line is divided to multiple short lines ( to make a compact "label" eg. for Graphviz nodes/edges)
# TBD: tester function
	# nPartMaxLen = 32  
	sLbl = sStr.replace("\\","\\\\\\\\")
	#TRACE("labellable string before modifications: '$sLbl'");
	sLbl = sLbl.replace("\\\\\\\\","\\\\\\\\ ")
	#TRACE("labellable string after possible backslashes added printable: '$sLbl'");
	
	sLbl = sLbl.replace("\/","\/ ")
	sLbl = sLbl.replace("_","_ ")
	sLbl = sLbl.replace("\""," ")
	# $sLbl =~ s/_/\_ /g;
	
	if sLbl == "":
		sLbl = "EMPTY"
		return sLbl
	#TBD: add conversion of TAGS, (eg. "<NL>"  to  "\\n")
    #TRACE("labellable string after cutting spaces adding: '$sLbl'");

	asParts = sLbl.split("\s+")
	sResultStr = ""
	nNextStepPos = nLABEL_PART_SPLICE_LEN_MAX
	
	for sPart in asParts:
		sResultStr = sResultStr + " " +sPart
		
		nTotalLen = len(sResultStr)
		if nTotalLen > nNextStepPos:
			sResultStr = sResultStr+"\\\\n"
			nTotalLen = len(sResultStr)
			nNextStepPos = nTotalLen + nLABEL_PART_SPLICE_LEN_MAX


    #TRACE("labelled string before removing cutting spaces '$ResultStr'");
	
	sResultStr = sResultStr.replace("\\\\ ", "\\\\") # to return non-splitted positions to original
	sResultStr = sResultStr.replace("\\n ", "\\n")
	sResultStr = sResultStr.replace("\/ ", "\/")

	#TRACE("string '$s' labelled to '$ResultStr'");
	#TRACE_RET();
	return sResultStr


#=============================================
def lnf(sStr, sTag="<NL>"):
#=============================================
# changes given tags to line feeds
# for linefying tagged texts
	print("try linefy flattened text: "+sStr)
	sLinefiedStr = sStr.replace(sTag, sLINE_FEED)
	return sLinefiedStr
	
#=============================================
def sym(sStr):
#=============================================
# converts or removes characters which are not valid for symbol names within most programming languages (or Graphviz names)

	nStrLen = len(sStr) # symbol name size limited for case of long (= multi-line) texts
	if nStrLen > nSYMBOL_NAME_LEN_MAX:
		sStrForSym = sStr[:nSYMBOL_NAME_LEN_MAX]
	else:
		sStrForSym = sStr
		
	sStrAsSym = re.sub('\W','_',sStrForSym)    # !: Python: regex in substitution: use 're' -module, NOT 'replace()' -function !!!!!!
	sStrAsSym = re.sub("^\d","_",sStrAsSym)   # leading numeric chars
	if sStrAsSym == "":
		sStrAsSym = "EMPTY"
	return sStrAsSym
'''
#=============================================
def trimThrough(sStr):  # Removes leading and trailing spaces. Reduces multiple white chars
#=============================================
	sStr = re.sub("^\s+","",sStr)
	sStr = re.sub("\s+$","",sStr)
	sStr = re.sub("\s+"," ",sStr)
	sStr = re.sub("\R"," ",sStr)
	return sStr	
#=============================================
def timeStamp(sFormatStr="%Y-%m-%d %H:%M:%S"):  # Removes leading and trailing spaces. Reduces multiple white chars
#=============================================	
	#return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	return datetime.now().strftime(sFormatStr)
#=============================================	
def isIntStr(s):
#=============================================
    try: 
        int(s)
        return True
    except ValueError:
        return False

#=============================================
def isBlankStr(sStr):
#=============================================
	if re.match("^.*$", sStr):
		return True
	else:
		return False

#=============================================	
def arrayToStr(axParts, sDelim="", sCommentPrefix=""):
#=============================================
	sRetStr = ""
	nCnt = 0
	#sRetStr = sCommentPrefix + axParts.pop(0)  # first element
	# no leading or trailing delimiter inserted
	for xPart in axParts:
		sPart = str(xPart)
		sPart = sPart.rstrip()  # !: Python: removes <NL>,<CR>, <LF>  and "\s+"
		if nCnt == 0:
			sRetStr = sPart
		else:
			sRetStr = sRetStr + sDelim + sPart
		#print("sRetStr = " + sRetStr)
		nCnt += 1
	return sRetStr.rstrip()
#=============================================
def getStrArrayVal(asArray,nPos, sDefaultVal="DEFAULT"):
#=============================================
# DUTY: returns value even the index is out of range
	sRetVal =""
	try:
		sRetVal = asArray[nPos]
	except IndexError:
		sRetVal = sDefaultVal
	return sRetVal


#=============================================
def seqDictValuesToStr(dBySeqNbr, sDelim="", sCommentPrefix=""):
#=============================================
	# joins values from dictionary, where key  names are integer strings
	sRetStr = sCommentPrefix 
	for xKey, xVal in dBySeqNbr.items():
		sVal = str(xVal)
		sRetStr = sRetStr + sDelim + sVal
	return sRetStr
	
	
# http://stackoverflow.com/questions/10472907/how-to-convert-dictionary-into-string	


#=============================================
def anyDictToStr(dDict):
#=============================================
	sRetStr = ""
	if type(dDict) is dict:   # SEE: https://bytes.com/topic/python/answers/779377-checking-if-variable-dictionary
		for sKey, sVal in dDict.items():
			sKeyValPair = "'"+sKey+"':'"+sVal+"', "
			sRetStr += sKeyValPair
	else:
		print("ERROR: given data structure is NOT dictionary")

	return sRetStr

# #===============================================================================	
# def handleException(oTrace, sComment=""):  # TBD: activate (why was commented away ???) 170627
# #===============================================================================
	# exctype, value = sys.exc_info()[:2]
	# errorText = str(exctype)+" "+str(value)
	# oTrace.INFO("EXECPTION: '"+errorText+"' when '"+sComment+"'")
	


	
#===============================================================================
def handleArgs(sys, sType="DEFAULT"):	
#===============================================================================
	
	# sys.argv is the list of command-line arguments.
	# len(sys.argv) is the number of command-line arguments.
	# Here sys.argv[0] is allways the program ie. script name.
	# TBD: change so, that trace file name body is identical to main script body
	asArguments = sys.argv	
	# TBD add more choices
	nArgumentsCount = len(asArguments)
	print ("arg 0 = "+ asArguments[0]+"\n")
	print ("arg 1 = "+ asArguments[1]+"\n")
	print ("arg 2 = "+ asArguments[2]+"\n")
	print ("arg 3 = "+ asArguments[3]+"\n")
	if sType == "FILE_CONV_BY_TRIPOD":
		nArgumentsCount = len(asArguments)
		sThisScriptName = asArguments[0]
		print("arguments count = "+str(nArgumentsCount))
		if nArgumentsCount < 2:  # TBD: function for argument handling
			print("usage: python <this script name>   <master config file name> <trace file name>")
			exit()

		sBASE_PATH           					= asArguments[1]
		sCONFIG_FILE_REL_NAME					= asArguments[2]
		sTRACE_FILE_REL_NAME           			= asArguments[3]
						
		return  sBASE_PATH, sCONFIG_FILE_REL_NAME, sTRACE_FILE_REL_NAME

	# TBD: more choices
	elif sType == "DEFAULT":# default case
		if nArgumentsCount > 0:
			#asArguments.pop(0)
			return nArgumentsCount, asArguments
		else:
			print ("caller arguments are missing")
	else:
		if nArgumentCount > 0:
			#asArguments.pop(0)
			return nArgumentsCount, asArguments

#===============================================================================
def getDriveLetter():	
#===============================================================================
	# https://docs.python.org/2/library/os.path.html
	sFullPath = os.getcwd()	
	# http://stackoverflow.com/questions/5137497/find-current-directory-and-files-directory
	sDriveLetter, sPathName = os.path.splitdrive(sFullPath)
	return sDriveLetter


#=============================================
def addStrToFileIfNotAlready(sStr, sFileFullName, oTrace):  # for SMALL files, because would take time with large ones
#=============================================
# eg. for adding file names to a file, which will later be used to configure a pack/zip program
	bStatus = False
	sTraceLine = ""
	if os.path.exists(sFileFullName):
		with open(sFileFullName) as oFile:
			for sLine in oFile.readlines():
				if sStr in sLine:
					sTraceLine = "string '" + sStr + "' is already in file '" + sFileFullName + "'"
					bStatus = True
					break
		if bStatus == False:
			oFile = open(sFileFullName, 'a')
			sTraceLine = "string '" + sStr + "' added to existing file '" + sFileFullName + "'"
			oFile.write(sStr+"\n")
			oFile.close()
	else:
		try:
			oFile = open(sFileFullName, 'w')
			sTraceLine = "string '" + sStr + "' added to new file '" + sFileFullName + "'"
			oFile.write(sStr + "\n")
			oFile.close()
		except:
			sTraceLine = "string '" + sStr + "' not added to new file '" + sFileFullName + "'"
	oTrace.INFO(sTraceLine)


#=============================================
def checkIfStrIsInFile(sStr, sFileFullName, oTrace):  # for SMALL files
#=============================================
	sStatus = "NO_FILE"
	if os.path.exists(sFileFullName):
		with open(sFileFullName) as oFile:
			sStatus = "NOT_FOUND"  # quess
			sTraceLine = "string '" + sStr + "' is NOT in file '" + sFileFullName + "'"
			for sLine in oFile.readlines():
				if sStr in sLine:
					sTraceLine = "string '" + sStr + "' is already in file '" + sFileFullName + "'"
					sStatus = "YES_FOUND"
					break
		oTrace.INFO(sTraceLine)
	else:
		oTrace.INFO("file '" + sFileFullName + "' does not exist")
	return sStatus

#=============================================
def checkFileExistence(sFileFullName,oTrace):
#=============================================
	sFileFullName = sFileFullName.strip()  # !: assures leading and trailing white characters absence
	sFileExistenceStatus = "NOT_EXIST"
	if os.path.isfile(sFileFullName):
		sFileExistenceStatus = "YES_EXIST"
		#oTrace.INFO("file '" + sFileFullName + " 'exists")
	else:
		oTrace.INFO("file '" + sFileFullName + " ' does NOT exist")
	return sFileExistenceStatus

#=============================================
def checkIfPropablyFileName(sPossibleFileName, oTrace):
#=============================================
	sRetStatus = ""
	# TBD: add checks to rule out:
	#	-	existing directories
	#	-	very short names

	if len(sPossibleFileName) < p_SEVEN:  # from HAT
		sRetStatus = "Short"  # string is not a file name
	else:
		sPossibleFileName = sPossibleFileName.replace("\\","/")
		try:
			oCatch = re.compile(p_sFILE_PROPABLY_NAME_CATCH_re)

			oM = oCatch.match(sPossibleFileName)
			if oM:
				if os.path.isdir(sPossibleFileName):
					sRetStatus = "Path"   # is a path name, so it is not a file name
				else:
					sRetStatus = "File"
			else:
				sRetStatus = "None"  # string is not a file name
		except:
			exctype, value = sys.exc_info()[:2]  # !: very comprehensive output
			sErrorText = str(exctype) + " " + str(value)
			sRetStatus = "Error"
			oTrace.INFO(sErrorText)

	oTrace.INFO("file name candidate '" + sPossibleFileName + "' was evaluated as '" + sRetStatus + "' by regex '"+p_sFILE_PROPABLY_NAME_CATCH_re+"'")
	
	return sRetStatus

#=======================================================
def tryEvaluatePythonComparison(sStatement, oTrace):
#=======================================================
	sRetVal = ""
	bRetVal = False
	try:
		bRetVal = eval(sStatement)  # prefix 'if' and postfix ':' are NOT needed !!!
		sRetVal = str(bRetVal)  # 'True' or 'False'
	except:
		sRetVal = "Error"
	oTrace.INFO("statement '"+sStatement+"' was evaluated as '"+sRetVal+"'")
	return sRetVal

#=============================================
def getFileAttributes(sFileFullName, oTrace):   # DONE: 180120
#=============================================
	dRetFileAttr = {}

	if checkFileExistence(sFileFullName,oTrace) == "YES_EXIST":
		# https://www.w3resource.com/python-exercises/python-basic-exercise-107.php
		sAccessTime  	= str(time.ctime(os.path.getatime(sFileFullName)))
		sModifiedTime	= str(time.ctime(os.path.getmtime(sFileFullName)))
		sChangedTime	= str(time.ctime(os.path.getctime(sFileFullName)))
		sSize 			= str(os.path.getsize(sFileFullName))
		dRetFileAttr['AccessTime_'] 	= sAccessTime
		dRetFileAttr['ModifTime_']  	= sModifiedTime
		dRetFileAttr['ChangeTime_']		= sChangedTime
		dRetFileAttr['Size_'] 			= sSize

	return dRetFileAttr

#=============================================
def getFileAttributesAsStr(sFileFullName,oTrace):   # DONE: 180120
#=============================================
	# eg. for adding info to file name line when names are written to a file
	#	-	then RCS can be used to version the file names file and thus detect computer context changes
	#		-	unwanted files/directories can  be ignored  by "clFilterTextStorage" instance usage
	sFileAttrAsStr = "NONE"
	if checkFileExistence(sFileFullName,oTrace) == "YES_EXIST":
		# https://www.w3resource.com/python-exercises/python-basic-exercise-107.php
		sAccessTimeStamp 		= str(time.ctime(os.path.getatime(sFileFullName)))
		sModificationTimeStamp  = str(time.ctime(os.path.getmtime(sFileFullName)))
		sChangeTimeStamp		= str(time.ctime(os.path.getctime(sFileFullName)))
		sFileSize 				= str(os.path.getsize(sFileFullName))

		sFileAttrAsStr = " (ATTRIBUTES: Accessed: "+sAccessTimeStamp + ", Modified="+ sModificationTimeStamp + ", Changed="+sChangeTimeStamp + ", Size="+sFileSize+")"

	return sFileAttrAsStr
# =============================================
def checkPathExistence(sPathName, oTrace):
# =============================================
	sPathName = sPathName.strip()  # !: assures leading and trailing white characters absence
	sPathStatus = "NOT_EXIST"
	if os.path.ispath(sPathName):
		sPathStatus = "YES_EXIST"
		oTrace.INFO("path '" + sPathName + "'exists")
	else:
		oTrace.INFO("path '" + sPathName + "' does NOT exist")
	return sPathStatus
	
# =============================================
def assureForwardsSlashedName(sPartOrFullName, oTrace):
# =============================================
	# removes problems caused by single or multiple "\" characters  (seems, that also DOS and Windows accept "/" -characters in path names !!!)
	sAssuredName = sPartOrFullName
	sAssuredName = sAssuredName.replace("\\", "/")
	sAssuredName = sAssuredName.replace("//", "/")
	
	oTrace.INFO("name '" + sPartOrFullName + "' assured to '" + sAssuredName + "'")
	return sAssuredName


# =============================================
def assureBackwardsSlashesAtLine(sLine, oTrace):
	# =============================================
	# removes problems caused by single or multiple "\" characters  (seems, that also DOS and Windows accept "/" -characters in path names !!!)
	sAssuredLine = sLine
	sAssuredLine = sAssuredLine.replace("/", "\\")
	sAssuredLine = sAssuredLine.replace("//", "\\")
	
	oTrace.INFO("name '" + sLine + "' assured to '" + sAssuredLine + "'")
	return sAssuredLine

'''		
#==================================================================================
def collectSelectedFileNames(me, 
							sEntryPathsSeq, 
							reIgnoreAny,
							reIgnoreAny, 
							sSelectDirSeq,
							sIgnoreDirSeq,
							sSelectFileBodySeq,
							sIgnoreFileBodySeq,							
							sSelectFileExtSeq, 
							sIgnoreFileExtSeq, 
							oTrace):
#==================================================================================
	# this method is transferred here for non-class usages (170117)
	# edited from (working) solitary script file (160816)   TBD: test in this class context
	# TBD: set filter parameters:
	#	-	select file names by file name extension
	# 	-	ignore file names by file name extension
	#	-	select path names names by containing directory names 
	# 	- 	ignore path names names by containing directory names

	asAllFoundFileFullNames = []
	oTrace.INFO("entry paths sequence = "+sEntryPathsSeq)
	oTrace.INFO("ignore filename extensions sequence = "+sIgnoreFileExtSeq)
	oTrace.INFO("result file name ="+sResultFile)
	
	# super().addText("h=\""+sParentPath+"\"\n\n")
	asEntryPaths 		= sEntryPathsSeq.split(',')
	asSelectByFileExt 	= sSelectFileExtSeq.split(',')
	asIgnoreByFileExt 	= sIgnoreFileExtSeq.split(',')
	asSelectByFileBody 	= sSelectFileBodySeq.split(',')
	asIgnoreByFileBody 	= sIgnoreFileBodySeq.split(',')
	asSelectByDirInPath = sSelectDirSeq.split(',')
	asIgnoreByDirInPath = sIgnoreDirSeq.split(',')
	
	
	for sEntryPath in asEntryPaths:
		oTrace.INFO("entry path ="+sEntryPath)
		for sFocusPath, asDirNames, asFileNames in os.walk(sEntryPath):
			#dirname = os.path.basename(os.path.dirname(path))
			oTrace.INFO("    focus path ="+sFocusPath)
			asDirChain = sFocusPath.split("\\")
			for sDir in asDirChain:
				for sIgnoreDir in asIgnoreByDirInPath:
					if sIgnoreDir.tolower() == sDir.tolower():
						bIgnoreFile = True
						break
			
			if bIgnoreFile == True:
				for 
				
			
			sFileType = "UNKNOWN"
			for sFileName in asFileNames:
				bIgnoreFile = 0						
				(sPathAndBody, sExtension) = os.path.splitext(sFileName)
				
				sFileFullName =  sFocusPath+sFileName
				
				for sIgnoreExt in asIgnoreByFileExts:
					if sExtension.lower() == sIgnoreExt.lower():
						bIgnoreFile = 1  # ignorable file extension found, so file is ignored
						continue
				if bIgnoreFile == 1:
					continue 
				if sFocusDir=="OTL":
					# why this ???? sFileName = sFileFullName
					sFileType = "OTL_FILE"
				if reMatchStr == "ALL_FILES":
					hFileNames{sFileFullName} = sFileType   
				else:
					# tries to find specified string in file
					if me.findInFile(reMatchStr, sFileFullName) > 0:
						hFileNames{sFileFullName} = sFileType
						
	# what should return ???????????????????

		'''
#=========================================================
def trimRemoveLineTailsByTags(sRawLine, asTailStartTags):  # eg. "//" and "#" from given, single line

#=========================================================
	# TBD: removes possible tags and line contents after the tags
	# can be used to remove typical line end comments
	sPrefixLine = ""
	sRetLine = sRawLine # initial quess no comment tails or lines
	# see. http://stackoverflow.com/questions/1706198/python-how-to-ignore-comment-lines-when-reading-in-a-file
	for sTailStartTag in asTailStartTags:  # for each tag in array
		# me.oTrace.INFO("removes possible tail started by '"+sTailStartTag+"' from line '"+sRawLine+"'" )
		sPrefixLine =  sRawLine.split(sTailStartTag, 1)[0]
		sPrefixLine = sPrefixLine.rstrip()
		if sPrefixLine != sRawLine:  # tagged tail found and removed
			sRetLine = sPrefixLine
			break
	sRetLine = trimThrough(sRetLine) # removes multiple spaces
	return sRetLine
		
# Started to create short methods for capturer templates
#==============================================================
def buildDosCommandLine(sLineRval, dSetupValuesForTags, sTAG_re, oTrace):  # tne <line LVAL) is a keyword which caused calling here
#==============================================================
	oTrace.INFO("sLineRval = '"+sLineRval+"'")
	# called from top level scripts, where certain values are collected at first and used in later phases
	# sTAG_re can be eg. gsTAIL_UNDERSCORE_TAG_re
	for sKey, sVal in dSetupValuesForTags.items(): # were saved at [1.SETUP] phase
		sLineRval = sLineRval.replace(sKey, sVal)


	oTrace.INFO("sLineRval = '" + sLineRval + "'")
	sLineRval = sLineRval.replace("[", "")  # removes possible notetab hyperlink frames
	sLineRval = sLineRval.replace("]", "") # removes possible notetab hyperlink frames
	oMatch = re.search(sTAG_re, sLineRval)
	# if oMatch:
	# 	oTrace.INFO("FAIL: tags '"+sTagRe+"' still remained at string '"+sLineRval+"'")
	# 	return "MISSING"
	# else:
	oTrace.INFO("sLineRval = '"+sLineRval+"'")
	return sLineRval
	# eg. for creating single dos command line

#==============================================================
def buildMultipleDosCommandLines(oStPhase, dValuesForTags, sTAG_re, oTrace):  # tne <line LVAL) is a keyword which caused calling here
#==============================================================
	asBatLines = []

	# called from top level scripts, where certain values are collected at first and used in later phases
	# sTAG_re can be eg. gsTAIL_UNDERSCORE_TAG_re
	while True:
		sLineRval = oStPhase.popOldestValBy(gsCONSOLE_COMMAND_LINE_KEYWORD)
		oTrace.INFO("prepare for bat lines = '" + sLineRval + "'")
		if sLineRval == "":
			break
		for sKey, sVal in dValuesForTags.items(): # were saved at [1.SETUP] phase
			sLineRval = sLineRval.replace(sKey, sVal)
			sLineRval = sLineRval.replace("[", "")  # removes possible notetab hyperlink frames
			sLineRval = sLineRval.replace("]", "") # removes possible notetab hyperlink frames
		oTrace.INFO("append to bat lines = '" + sLineRval + "'")
		asBatLines.append(sLineRval)
		oMatch = re.search(sTAG_re, sLineRval)
		if oMatch:
			oTrace.INFO("FAIL: tags '"+sTAG_re+"' still remained at string '"+sLineRval+"'")
			asBatLines = []


	sStr = arrayToStr(asBatLines, "<cr>")
	oTrace.INFO("bat xxx lines array as str '" + sStr + "'")
	return asBatLines
	# eg. for creating single dos command line

	# =============================================
	def deleteFilesInDir(me, sPathName):
	# =============================================
		# https: // stackoverflow.com / questions / 14176166 / list - only - files - in -a - directory
		for sFileName in os.listdir(sPathName):
			sFileFullName = os.path.join(sPathName, sFileName)
			if os.path.isfile(sFileFullName):
				os.remove(sFileFullName)
				
				
###########################################################################################################
############# PARAMUTILS REGION ###########################################################################
###########################################################################################################

import os, sys
import os.path
import re
import time
import datetime

# a parent class to parametrize any class within this LIB directory

# TBD: change these global variable prefixes to "p_"   ("p" indicates <param> and same prefix is used also in NoteTab)
# - "p_k" prefix shall indicate global keyword
#	-	TBD: change all hard-coded keywords to assigned variables

# "_re" postfix indicates a regex string

p_ZERO = 0
p_ONE = 1
p_TWO = 2
p_THREE = 3
p_FOUR = 4
p_FIVE = 5
p_SIX = 6
p_SEVEN = 7
p_EIGHT = 8
p_NINE = 9

p_NO_GROUPS = 0

p_sANY_STRING_MATCH_re = "^.*$"
p_sNO_STRING_MATCH_re = "^Lorem.Ipsum.Simsala.Bim$"
# TBD: collect global constants here
p_cSCALAR_TAG_PREFIX = "$"
p_cARRAY_TAG_PREFIX = "@"
p_cLITERAL_TAG_PREFIX = "&"  # TBD: is this needed ???
p_sLINE_SPLITTER_TAG_re = "\\|" # for generating several fixed amount/format edition lines from single feed line

p_sTEMPLATE_TAG_CATCH_re = "\\$\\S+" # added 170723

p_sIGNORABLE_LINE = "IGNORE THIS LINE"
# TBD: classify the global variables by <FILTER>, <EDIT>, <REPORT> and <GENERAL>
p_sSCALAR_TAG_IND_re = "\\"+p_cSCALAR_TAG_PREFIX+"\\w+"
p_sARRAY_TAG_IND_re = "\\"+p_cARRAY_TAG_PREFIX+"\\w+"
p_sLITERAL_TAG_IND_re = "\\"+p_cLITERAL_TAG_PREFIX+"\\w+"
p_sREPORT_TEMPLATE_ITEM_SPLITTERS_re = "\\(%|%\\)"

p_kREPORT_TEMPLATE_ITEM_SPLITTERS = "REPORT_TEMPLATE_ELEMENT_SPLITTERS"

p_REPORT_TEMPLATE_ITEM_PART_MATCH_re = "<\w+>.*" # <FILL>, <IF>, <THEN>, <EVAL>, ...
p_REPORT_TEMPLATE_ITEM_PART_PAIR_CATCH_re = "^<(\w+)>(.*)$" # "FILL", "IF", "THEN", "EVAL", ...

p_sARRAY_TAG_SPLITTERS = ",|\\s+and\\s+|\\s+"  # !: Python: multiple splitters and multiple characters in single splitter
p_sTAG_VALUE_PAIR_ATTACHER = ":"
p_sLINE_SEPARATOR_TAG = "<CR>"
p_nIMPOSSIBLE_POS = -1

p_nPICKED_LINES_RING_BUFFER_SIZE = 99 #

p_sNOTHING = ""


p_kSCALAR_TAG_CATCH = "CATCH_TAG_SCALAR"
#p_sTEMPLATE_SCALAR_TAG_MATCH_CATCH_re = "(\$(\w+[.]{0,1}\w+[.]{0,1}\w+))" # TBD: take this in use

p_sTEMPLATE_SCALAR_TAG_MATCH_CATCH_re = "(\$([a-zA-Z0-9]+[.]{0,1}[a-zA-Z0-9]+[.]{0,1}[a-zA-Z0-9]+))" # starts with '$' and last character shall NOT be underscore
#	=	shall contain 0,1 or 2 "." -separated modifiers

p_sFILE_PROPABLY_NAME_CATCH_re = r"^.*(\\|/)(\w{2,}\.\w{2,}){1,}\s*$"

p_sTEMPLATE_ITEM_PART_IF_MATCH_CATCH_re = "^\\s*IF\\s+(.*)$"
p_sTEMPLATE_ITEM_PART_ELSE_MATCH_re 	= "^\\s*ELSE\\s*$"
p_sNON_BLANK_DETECT_MATCH_re 			= "^.*\\w+.*$"
p_sPYTHON_COMMAND_LINE_MATCH_re 		= "^.*python.*\\s+.*\\.py.*$"

p_sTAGGY_FILE_ACTIVE_PART_START_IND_CATCH_re	= "^\\s*@begin\\s*.*$"
p_sTAGGY_FILE_ACTIVE_PART_END_IND_CATCH_re  	= "^\\s*@end\\s*.*$"  # matching shall skip rest of the jsoncomm file

p_sOTL_FILE_HEADING_MATCH_re = "^\\s*=\\s+V\\w+\\s+Outline\\s+MultiLine.*$"
# "= V4 Outline MultiLine NoSorting TabWidth=30"
p_sOTL_TOPIC_CATCH_re = "H=\"(.*)\""

p_sOTL_TOPIC_LINK_CATCH_re = "^.*\\[(\\S+)::(\\S+)\\].*$"

p_sOTL_TOPIC_LINK_CATCH_AND_WRITE_FILE_re = "^.*\\[(\\S+)::(\\S+)\\]\\s+=>\\s+(\\S+).*$" # TODO: add usage into function "expandOrFileByOtlLinks()"
	# eg. [<file name>::<topic name>] => <topic active part file name>
p_sOTL_PROPABLY_FILE_LINK_CATCH_re = "^.*\\[" + p_sFILE_PROPABLY_NAME_CATCH_re + "\\].*$"
p_sTAIL_UNDERSCORE_TAG_re = "\\w+_\\s+"

p_nVERY_IMPROBABLE_INTEGER 	= -9999    # !: Python "global" variables shall be here (outside class definion)
sEVERYTHING_MATCH_re 		= "^.*$"  # for filter defaults
sVERY_IMPROBABLE_MATCH_re 	= "^this regex shall not match anything$" # for filter defaults
p_sCONSOLE_COMMAND_LINE_KEYWORD = "bat_"   # Must

p_sMASTER_BAT_PLAIN_NAME = "MAIN.BAT"

p_sWORK_FILE_NAME_IND_STR = ".tmp" # to indicate eg. JSON file which is cleaned from original (=commented) pseudo-JSON file

p_sFILE_FULL_NAME_CATCH_re 	= "^(.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$))"
p_sFILE_PLAIN_NAME_CATCH_re 	= ""  # TBD
#p_sFILE_PROPABLY_NAME_CATCH_re = "^(.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$))"  # at least one slash preceding symbol-name valid string incluning one or more dot chars "."

	# -	at least one slash preceding symbol-name valid string including one or more solitary dot chars "."
	# -	each dot-separated "\w" -part has minimum length
# https://techtavern.wordpress.com/2009/04/06/regex-that-matches-path-filename-and-extension/
#=================TRACE UTILS =================================
nINDENT_STEP_WIDTH = 8	# TBD: transfer to config file
sEMPTY_BRICK = "    "
sEMPTY_OFFSET_BRICK = "    "
sLINED_BRICK = "----"
sSIDEKICK_FILE_NAME_TAG = "_"
#================= NOTETAB UTILS =================================
# TBD: move these literal definitions to <params> module 170809
p_sNOTETAB_OUTLINE_FILE_HEADING = "= V4 Outline MultiLine NoSorting TabWidth=30"
sLINE_JOINER = "__NL__"
sTopicNameLineMatchPattern = "H=\".*\""
sTopicNameLineCatchPattern = "H=\"(.*)\""
sNAME_PATTERN = "\".*\""

sNOTETAB_HYPERLINK_TAGGED_START = "%["   # for renovable notetab hyperlinks in jsontxt -files
sNOTETAB_HYPERLINK_TAGGED_END 	= "]%"   # for renovable notetab hyperlinks in jsontxt -files

p_sEXPANDED_TOPIC_CONTENTS_FILE_NAME = "TopicContents.cfg"  # contains single topic text where hyperlink topic texts are inserted
p_sAPPLICATION_SESSION_INFO_FILE_NAME = "ApplicationSessionInfo.txt"  # shall contain date/time, top script name, I/O file names etc.

#============== MASTER COLLECTOR SCRIPTS =====================================
p_sPHASE_TITLE_CATCH_re       = "^\\[\\d+\\.(\\S+)\\]$"
p_sFILE_ROLE_NAME_CATCH_re    = "^(\\S+_)\\s*=\\s*\\[(\\S+)\\.*]"
p_sBAT_COMMAND_NAME_CATCH_re = "^\\s*bat_\\s*=\\s*(\\w+)(.*)$"   # for dos command lines etc.
								# eg. 'bat_ = python PhaseScript_ FeedFile_ ExtractConfFile_ ReportConfFile_ ResultFile_'
p_asLINE_TAIL_COMMENTS = ["#"]  # TBD add others (?)

p_sTOPIC_JOURNAL_STACK_START_re = "^\s*\[-----"
p_sOtlTopicNameTpl = "H=\"__topic_name__\""

p_sSYMBOLIFIER_DIRECTIVE = "sym"
p_sLABELIFIER_DIRECTIVE  = "lbl"
p_sLINEFIER_DIRECTIVE    = "lnf" # to convert <TAG> to <line feed>
p_sPREV_TAG_REF_DIRECTIVE  = "prev"
p_sSEQ_NBR_TAG 		 	= "SEQ"
p_sINT_INCREMENTER_DIRECTIVE = "inc"

sLINE_FEED 	= "\\n"
nSYMBOL_NAME_LEN_MAX 		= 32  # from hat
nLABEL_PART_SPLICE_LEN_MAX 	= 16  #	from hat

sTRACE_FILE_EXT = ".TRACE"
sDEFAULT_TRACE_FILE_NAME = "DEFAULT"+sTRACE_FILE_EXT

p_nLOOP_COUNT_MAX		 	= 999
p_sMATCH_EVERY_LINE_re 		= "^.*$"
p_sMATCH_NONE_LINE_re 		= "^.*fwefewtwtwffwetwtt.*$"

p_sLINE_FEED_TAG = "<NL>"

p_nDEQUE_LAST_POS_INDEX = 0   # why not "-1" as in plain arrays ?????

p_sDIR_FORWARDS_OPERATION_re 	= "==>"
p_sDIR_BACKWARDS_OPERATION_re = "<=="

p_sOPER_TO_NEXT = "NEXT_"     # e.g. for filtering enable/disable -range detection
p_sOPER_FROM_PAST = "PREV_"	  # e.g. for filtering enable/disable -range detection

p_CSV_SEPARATOR = ", "   		#  comma with space
#================== STATE UTILS ==================================================
p_nPOS_LATEST = -1
p_nPOS_PREV	= -2



class clParams:   # ancestor class for everything in THIS directory
	
	p_sFileNamesFile = ""  # class variable for all inherited objects to save names of attached INPUT/OUTPUT files
	p_sScriptPathName = ""  # class variable
	def __init__(me, sDuty, oTrace, sTheseDriveLetter="N/A", sCreatorPath="N/A", sCreatorName="N/A"):  # python constructor
	#=========================================================
	# TBD: edit
		try:
			me.oTrace 			= oTrace
			me.sDuty			= sDuty
			me.bThisObjectIsOperable = False   # initial quess which affects to whole inheritance hierarchy
			#me.bOperabilityStatusWrittenToConsole = False
			#me.setOperability(False,"initial quess")# initial quess
			me.oTrace.INFO("constructor "+sDuty,"kick")
			me.dParams 	= {}
			# me.oTrace.INFO("ended constructor for '"+sDuty+"'")
		except:
			exctype, value = sys.exc_info()[:2]  # !: very comprehensive output
			errorText = str(exctype) + " " + str(value)
			me.oTrace.INFO("'" + me.sDuty + "' '" + errorText + "'", "exception")
	#=========================================================
	def updateParams(me, dParams):
	#=========================================================
	# adds or updates parametric data which will be used within this class
	# given key names must match the requested (=hard coded) key names
		me.oTrace.INFO("...")
		me.dParams.update(dParams) # !: Python dictionary "overlap/append"
		
	#=========================================================
	def setParam(me, sKey, sVal):
	#=========================================================
		me.oTrace.INFO("object '"+me.sDuty+"' set parameter '"+sVal+"' by key '"+sKey+"'")
		me.dParams[sKey] = sVal	
		
	#=========================================================
	def getParam(me, sKey, sDefaultVal="MISSING"):
	#=========================================================
		sParam = me.dParams.get(sKey, sDefaultVal)
		if sParam == sDefaultVal:
			me.oTrace.INFO("object '"+me.sDuty+"' does not contain value for '"+sKey+"', so "+sDefaultVal+ "' is used")
		return sParam
		
	#=========================================================
	def isParam(me, sKey):
	#=========================================================
		sParam = me.dParams.get(sKey, "MISSING")
		if sParam == "MISSING":
			return False
		else:
			return True
	
	# TBD: take in use in ALL child classes 171012
	#=========================================================
	def setOperability(me, bVal, sReason=""):
	#=========================================================
		# if stays "False", depending on context object can be ignored or some default data used
		#if me.bThisObjectIsOperable != bVal:
		#	pass
			# print("object '" + me.sDuty + "' operability changed to '" + str(bVal) + "' " + sReason)
		me.oTrace.INFO("object '" + me.sDuty + "' operability set to '" + str(bVal) + "' due to " + sReason)
		me.bThisObjectIsOperable = bVal

		# me.oTrace.INFO("object '" + me.sDuty + "' operability set to '"+ str(bVal)+"' "+sReason)

	#=========================================================
	def isOperable(me):
	#=========================================================
		return me.bThisObjectIsOperable
	
	#=========================================================
	def isNotOperable(me):
	#=========================================================
		if me.bThisObjectIsOperable == True:
			return False
		else:
			return True

		
		# if result


###########################################################################################################
############# TEXT ITEM UTILS REGION ######################################################################
###########################################################################################################

import os, sys
import os.path
import re
import json
import time
import datetime
# TODO; add traces if necessary
# Added value save/restore methods to add traceability usage 160725
from itertools import *	   # just added here, works OK (no explicit installation was needed !!!)
from ParamUtils import *
from TrickUtils import *
from collections  import * # for ring buffers etc	 https://stackoverflow.com/questions/4151320/efficient-circular-buffer
# contains also <ordered dict>


# class clItemsArray(clParams): # mainly for configuration data storage
class clItemsArray:	 # mainly for configuration data storage
	#=========================================================
	def __init__(me, sDuty, oTrace):  # python constructor
	#=========================================================
		me.sDuty	= sDuty
		me.oTrace	= oTrace

		#clParams.__init__(me, sDuty, oTrace)
		me.oTrace.INFO("constructor: '" + me.sDuty + "'","kick")
		me.nLastPos = 0
		me.nItemsCount = 0
		me.nCurrentPos=-1
		me.axItems = []
	#=========================================================
	def fillArrayItems(me, axFillItems):
	#=========================================================
		try:
			me.oTrace.INFO("duty: '" + me.sDuty + "' fill with '"+str(axFillItems)+"'")
			for xFillItem in axFillItems:
				me.nItemsCount = me.nItemsCount + 1
				me.axItems.append(xFillItem)
			me.nLastPos = me.nItemsCount-1
			me.oTrace.INFO("filling done")
		except:
			exctype, value = sys.exc_info()[:2]	 # !: very comprehensive output
			errorText = str(exctype) + " " + str(value)
			me.oTrace.INFO("ERROR: duty '" + me.sDuty + "' '" + errorText + "'", "exception")

	#=========================================================
	def getNextArrayItem(me):
	#=========================================================
		xRetVal = 0
		nNewPos = me.nCurrentPos + 1
		if nNewPos > me.nLastPos:
			me.oTrace.INFO("all "+str(me.nItemsCount)+ " already handled")
		else:
			xRetVal = me.axItems[nNewPos]
			me.nCurrentPos = nNewPos
		return xRetVal

	#=========================================================
	def getWholeArray(me):	 # to make faster looping in caller
	#=========================================================
		try:
			return me.axItems
		except:
			exctype, value = sys.exc_info()[:2]	 # !: very comprehensive output
			errorText = str(exctype) + " " + str(value)
			me.oTrace.INFO("ERROR: duty '" + me.sDuty + "' '" + errorText + "'", "exception")
			return 0

	#=========================================================
	def rewind(me):
	#=========================================================
		me.nCurrentPos = -1

# =========================================================
class clPickedRing(clParams):
	#=========================================================
	def __init__(me, sDuty, oTrace, nMaxLen=2048,sTheseDriveLetter="N/A", sCreatorPath="N/A", sCreatorName="N/A"):	# python constructor
	#=========================================================
		# can be used to avoid reading HUGE feed files into computer memory at once
		#TBD: make this as a wrapper around "deque" - class
		me.oTrace			= oTrace
		me.sDuty			= sDuty

		clParams.__init__(me, sDuty, me.oTrace)
		me.nMaxLen			= sDuty
		me.nLastPos			= nMaxLen-1
		me.nCopiedLen		= 0
		me.nAllUpdatesCnt	= 0 # total amount of <append> operations
		me.oTrace.INFO("started constructor for '" + me.sDuty + "', maximum size = "+str(me.nMaxLen),"kick")
	
		#me.oDeque = deque.__init__([],nMaxLen)	 # the core inside the wrap

		me.oDeque = deque([], nMaxLen)

	#=========================================================
	def append(me, sLine):
	#=========================================================
		me.oDeque.append(sLine)
		
	#=========================================================
	def copyFromLatestReToEnd(me, sRe):
	#=========================================================
		asRet = []
		nPos = -1
		while True:
			sRingLine =	 me.oDeque[nPos]
			asRet.append(sRingLine)
			if re.match(sRe, sRingLine):
				asRet.reverse()
				break
			nPos = nPos - 1
		me.nCopiedLen = -nPos
		return asRet

	#=========================================================
	def copyRangeFromPastToNow(me, sPastOffsetPos):
	#=========================================================
		nPastOffsetPos = int(sPastOffsetPos)
		asRet = []
		nTrueOffsetPos = -nPastOffsetPos
		for nPos in range(nTrueOffsetPos, p_nDEQUE_LAST_POS_INDEX):
			sPastLine = me.oDeque[nPos]
			asRet.append(sPastLine)
		me.nCopiedLen = nPastOffsetPos
	
		return asRet
	#=========================================================
	def getCopiedLen(me):
	#=========================================================
		return me.nCopiedLen
	
		


# contains methods for complex line or text part processing

# all "tags" -specific operations and definitions shall reside here
#  a parent class at least for "TexttStoreUtils"  and "ReportUtils"


class clTextItems(clParams):   # inherited by <text storage utils>
	#=========================================================
	def __init__(me, sDuty, oTrace, sTheseDriveLetter="N/A", sCreatorPath="N/A", sCreatorName="N/A"):  # python constructor
	#=========================================================
		me.sEvent			= "N/A"
		me.oTrace			= oTrace

		try:
			me.sDuty			= sDuty
			clParams.__init__(me, sDuty, me.oTrace)
			me.hValues			= {}   # a dictionary
			me.AoDTplData		= []  #
			me.asRetLines = []
			me.dictOfDualArrays = {}  # each key returns array of two values
			me.oPastRingCollector = 0 # mainly for <FILTER> phase operations
			#	  https://docs.python.org/2/library/collections.html
			# https: // stackoverflow.com / questions / 4151320 / efficient - circular - buffer
			me.asInLinesCopied = []	  # every "out" -line is also copied here. TBD: add check if already contains
			me.asOutLinesCopied = []  # every "out" -line is also copied here. TBD: add check if already contains
	
			me.m_dLatestRet				= {}		# generic dictionary updated by latest operation
											#	- functions can return status 'True' or 'False'.
											#		-	the function will update the actual "return" values to this dictionary
											#	- the caller can then retrieve the "return" values from this dictionary
											# BENEFIT: functions calls can be put straight into if..elsif...elsif...elsif... -code structure
			me.m_dLatestCaptures        = {}
			me.sReCapturePrev		= ""	# used. if only changed lines (actually patterns) are meant to be written target file
			me.sTplLineWithTagsPrev	= ""	# used. if only changed lines (actually patterns) are meant to be written target file
			me.nRepeatLineCnt = 0
			me.bLatestOperPassed = False	# for regex wrappers etc.
			me.dGeneratedValues = {}		# for values which are NOT achieved by extraction eg. Graphviz edge sequence numbers
			me.sConfFileName = ""			# 180216: added here to be usable to all objects in inheritance tree
			me.oTrace.INFO("constructor: '"+sDuty+"'","kick")
		except:
			exctype, value = sys.exc_info()[:2]	 # !: very comprehensive output
			errorText = str(exctype) + " " + str(value)
			me.oTrace.INFO("'" + me.sDuty + "' '"+ errorText+"'", "exception")

		# TBD: move all capture operations and template fillings in this class
		#  - set parent class for ReportUtils and TextStoreUtils


	#===============================================================================
	def processTemplateItem(me, dValuesToSubstituteTags, sTaggedTpl, sTplTagCatchRe, dOptRewordDef):   # practically single element within "A" in "DoA" (from configuration JSON file)
	#===============================================================================
		# TBD: do version, which splits item by tag "<\w+>" and processes the template item part by tag keyword
		# <IF_>, <ELSE_>, <FILL_> and <EVAL_>
		AoApairs = []
	
		nCount, AoApairs = me.tryCatchRepeatPairs(sTaggedTpl, p_REPORT_TEMPLATE_ITEM_PART_MATCH_re, p_REPORT_TEMPLATE_ITEM_PART_PAIR_CATCH_re)
		#  returned an array of two-member arrays

		if nCount == P_ZERO:
			return
		if nCount > p_FOUR:
			return



		if nCount == p_ONE:
			sFirstType = AoAPairs[p_ZERO][p_ZERO]
			sFirstPart = AoAPairs[p_ZERO][p_ONE]
			pass
		elif nCount == p_TWO:
			pass
		elif nCount == p_THREE:
			pass
		elif nCount == p_FOUR:
			pass
		else:
			# ERROR
			pass

	#===============================================================================
	def fillAndOrEvaluateTemplateItem(me, dValuesToSubstituteTags, sTaggedTpl, sTplTagCatchRe, dOptRewordDef):   # practically single element within "A" in "DoA" (from configuration JSON file)
	#===============================================================================
		# INPUT:
		#	Tag dictionary containing values: keys are tag labels
		#	Reword dictionary: keys are values from tag dictionary
		#	Regex for capturing tags from template
	
		# TBD: add keywords for conditional filling 180927
		#	-	eg.	 %IF $ActivityNode.sym CHANGED% $ActivityNode.prev.sym -> $activityNode.sym
	

		# tag frame = string starting with '$' and ending to white space
		nIntVal = 0	 # generic integer value usable within this method
		sLatestSymbolNameRet = "MISSING"
		dTagFramesInTpl = {}
		bFillingSuccess = False	 # initial quess: filling fails
		bCheckElseCond = False
		sRetStatus = "stsRejectItem" # initial quess
	
		sSplittersRe = me.getParam(p_kREPORT_TEMPLATE_ITEM_SPLITTERS)
		asTplItemRawParts = re.split(sSplittersRe, sTaggedTpl)
	
		oIfCondCatchRe = re.compile(p_sTEMPLATE_ITEM_PART_IF_MATCH_CATCH_re)  # at least one non-white character
		oElseCondMatchRe = re.compile(p_sTEMPLATE_ITEM_PART_ELSE_MATCH_re)	# at least one non-white character
	
		oNonBlankRe = re.compile(p_sNON_BLANK_DETECT_MATCH_re)	# at least one non-white character
	
		#tryEvaluatePythonComparison(...) in TrickUtils.py
		# TBD: replace splitting by using tryCatchRepeat("<\w+>.*", sLine) # for <IF>, <ELSE>, <FILL>, <EVAL>
	
		asTaggedTplItemParts	= [sStr for sStr in asTplItemRawParts if oNonBlankRe.match(sStr)]  # removes 'white-only" parts
		nTplItemPartsCnt		= len(asTaggedTplItemParts)
		sTplItemPartsCnt		= str(nTplItemPartsCnt)



		#==============================================================================================================
		if nTplItemPartsCnt == p_ONE:  # "(% IF $aaa != $bbb %)"  OR  "$AAA -> $BBB"
		#==============================================================================================================
			sTaggedWholeItemPart	= asTaggedTplItemParts[p_ZERO]
			oMatch = oIfCondCatchRe.match(sTaggedWholeItemPart)	 # whole item is an "IF" -condition
			if oMatch:
				sIfCondCore = oMatch.group(p_ONE)
				# TBD: add IF -part tag replacement values to be wrapped with quotation chars
				bFillingSuccess, sLatestSymbolNameRet, sFilledTpl = me.processTemplateItemPart("IF",dValuesToSubstituteTags,
																								ssTaggedWholeItemPart,
																								sTplTagCatchRe,
																								dOptRewordDef)
				if bFillingSuccess:
					sEvalStatus = tryEvaluatePythonComparison(sFilledTpl)
					if sEvalStatus == "True":
						sRetStatus = "stsRejectItem"  # = do NOT output this item
					elif sEvalStatus == "False":
						sRetStatus = "stsRejectRemainingItems"	# whole item is an "IF" -item and evaluation produced "True"
					else:
						sRetStatus = "stsRejectItem"
			else: # basic case: no condition, just report template item
				bFillingSuccess, sLatestSymbolNameRet, sFilledTpl = me.processTemplateItemPart("PLAIN", dValuesToSubstituteTags,
																								sTaggedWholeItemPart,
																								sTplTagCatchRe,
																								dOptRewordDef)
				if bFillingSuccess:
					sRetStatus = "stsAcceptItem" # whole item is a template item and evaluation produced "True"
				else:
					sRetStatus = "stsRejectItem"

		# TBD: add case type  "(% IF $aaa < 123 %) % $aaa.inc %" // does not generate any template
		#==============================================================================================================
		elif nTplItemPartsCnt == p_TWO:	 # "(% IF $aaa != $bbb %) $AAA -> $BBB"
		#==============================================================================================================
			sTaggedIfCondPart	= asTaggedTplItemParts[p_ZERO]
			sTaggedIfReportPart = asTaggedTplItemParts[p_ONE]
			oMatch = oIfCondCatchRe.match(sTaggedIfCondPart)
			if oMatch:
				# TBD: try fill if cond part
				sIfCondCore = oMatch.group(p_ONE)
				bFillingSuccess, sLatestSymbolNameRet, sFilledTpl = me.processTemplateItemPart("IF",dValuesToSubstituteTags,sIfCondCore, sTplTagCatchRe, dOptRewordDef)
				if bFillingSuccess:
					sEvalStatus = tryEvaluatePythonComparison(sFilledTpl,me.oTrace)
					if sEvalStatus == "True":
						bFillingSuccess, sLatestSymbolNameRet, sFilledTpl = me.processTemplateItemPart("PLAIN", dValuesToSubstituteTags, sTaggedIfReportPart, sTplTagCatchRe, dOptRewordDef)
						if bFillingSuccess:
							sRetStatus = "stsAcceptItem"  # output to report
					elif sEvalStatus == "False":
						sRetStatus = "stsRejectItem"
					else:
						sRetStatus = "stsRejectItem"
						
				else:
					sRetStatus = "stsRejectItem"
			else:
				me.oTrace.INFO("ERROR: invalid 'if' condition phrase in '"+sIfCondPart+"'")
				sRetStatus = "stsRejectItem"
		#==============================================================================================================
		elif nTplItemPartsCnt == p_FOUR:  # "(% IF $aaa != $bbb %) $AAA -> $BBB (% ELSE %) $CCC -> $DDD"
		#==============================================================================================================
			sTaggedIfCondPart		= asTaggedTplItemParts[p_ZERO]
			sTaggedIfReportPart		= asTaggedTplItemParts[p_ONE]
			sPlainElseCondPart		= asTaggedTplItemParts[p_TWO]
			sTaggedElseReportPart	= asTaggedTplItemParts[p_THREE]
			
			oMatch = oIfCondCatchRe.match(sTaggedIfCondPart)
			if oMatch:
				# TBD: try fill if cond part
				sIfCondCore = oMatch.group(p_ONE)
				bFillingSuccess, sLatestSymbolNameRet, sFilledTpl = me.processTemplateItemPart("IF",dValuesToSubstituteTags,sIfCondCore, sTplTagCatchRe, dOptRewordDef)
				if bFillingSuccess:
					bFillingSuccess = False
					sEvalStatus = tryEvaluatePythonComparison(sFilledTpl)
					if sEvalStatus == "True":
						bFillingSuccess, sLatestSymbolNameRet, sFilledTpl = me.processTemplateItemPart("PLAIN",dValuesToSubstituteTags, sTaggedIfReportPart, sTplTagCatchRe, dOptRewordDef)
						if bFillingSuccess == True:
							sRetStatus = "stsAcceptItem"
						else:
							sRetStatus = "stsRejectItem"
					elif sEvalStatus == "False":
						bCheckElseCond = True
					else:
						# TBD: trace error message here
						sRetStatus = "stsRejectItem"
			if CheckElseCond == True:
				oMatch = oElseCondCatchRe.match(sPlainElseCondPart)
				if oMatch:
					bFillingSuccess, sLatestSymbolNameRet, sFilledTpl = me.processTemplateItemPart("PLAIN", dValuesToSubstituteTags,sTaggedElseReportPart, sTplTagCatchRe, dOptRewordDef)
					if bFillingSuccess:
						sRetStatus = "stsAcceptItem"
					else:
						sRetStatus = "stsRejectItem"
				else:
					sRetStatus = "stsRejectItem"
			
			
		else:
			me.oTrace.INFO("invalid number '"+sTplItemPartsCnt+"' of parts in element '"+sTaggedTpl+"' (splitted by '"+sSplittersRe+"')")

		#me.oTrace.INFO("filled template item: '"+sFilledTpl+"'","topic")
		return sRetStatus, sLatestSymbolNameRet, sFilledTpl	  # TBD: replace with 'me.m_dLatestRet' -usage to simplify caller
	

	#===============================================================================
	def processTemplateItemPart(me, sType, dValuesToSubstituteTags, sTaggedTplItemPart, sTplTagCatchRe, dOptRewordDef):	 # can be template part or condition part
	#===============================================================================
		# template can be Report Template or Condition Template
		sLatestSymbolNameRet = "MISSING"
		dTagFramesInTplItemPart = {}
		bFillingSuccess = False	 # initial quess: filling fails

		(nGroupsCnt, tTagsInTplItemPart) = me.tryCatchRepeat(sTaggedTplItemPart, sTplTagCatchRe)  # tags from fresh template
		# <tag catch regex> is exposed in caller script and delivered here
		
		if nGroupsCnt == p_NO_GROUPS:
			return False, "EMPTY", sLatestSymbolNameRet
		
		sFilledTplItemPart = sTaggedTplItemPart
		# oTrace.INFO("collects tags from template")
		for asTagItem in tTagsInTplItemPart:  # when regex string contains indented parentheses (tag frame catch and tag catch), ToT has been returned
			sTagFrameInTplItemPart = asTagItem[0]  # starts from prefix and ends to last non-white-space
			sTagWholeInTplItemPart = asTagItem[1]  # = tag + 0,1 or 2 modifiers
			dTagFramesInTplItemPart[sTagWholeInTplItemPart] = sTagFrameInTplItemPart  # building a dictionary: keys are used to get values from
			# me.oTrace.INFO("caught tag from template item part:	 dTagFramesInTplItemPart[" + sTagWholeInTplItemPart + "] = " + sTagFrameInTplItemPart)
		
		for sTagWholeInTplItemPart in dTagFramesInTplItemPart:	# !: Python: looping keys within dictionary
			sTagFrameInTplItemPart = dTagFramesInTplItemPart[sTagWholeInTplItemPart]
			sTagCoreInTplItemPart, sSpecifier, sFormatter = me.getTagParts(sTagWholeInTplItemPart)	# picks "lbl", "sym" ,"prev", "inc" etc.
			
			if sSpecifier == p_sPREV_TAG_REF_DIRECTIVE:
				me.oTrace.INFO(sTagCoreInTplItemPart + " = dValuesToSubstituteTags[" + sTagCoreInTplItemPart + "]","kick")
				sTagCoreInTplItemPart = sTagCoreInTplItemPart + "." + p_sPREV_TAG_REF_DIRECTIVE
			# TBD: add specifier "changed", which causes comparison of new tag walue to previous tag value
			#	-	if values are same, tag is not substituted and template is not completely filled
			sTagSubstitutionFromTrap = dValuesToSubstituteTags.get(sTagCoreInTplItemPart, "MISSING")
			me.oTrace.INFO(sTagSubstitutionFromTrap + " = dValuesToSubstituteTags[" + sTagCoreInTplItemPart + "]","kick")
			
			# if dOptionalRewords:
			if dOptRewordDef != 0:
				sTagSubstitutionFinal = dOptRewordDef.get(sTagSubstitutionFromTrap, sTagSubstitutionFromTrap)
			else:  # reword object is not assigned
				sTagSubstitutionFinal = sTagSubstitutionFromTrap
			
			if sFormatter == p_sSYMBOLIFIER_DIRECTIVE:
				sTagSubstitutionFinal = me.sym(sTagSubstitutionFinal)
				sLatestSymbolNameRet = sTagSubstitutionFinal  # to be able to add note boxes to any node
			# me.oTrace.INFO("symbolified '"+sTagReplaceRawVal+"' to '"+sTagReplaceVal+"'","kick")
			elif sFormatter == p_sLABELIFIER_DIRECTIVE:
				me.oTrace.INFO("labelify " + sTagSubstitutionFinal,"kick")
				sTagSubstitutionFinal = me.lbl(sTagSubstitutionFinal)
			
			elif sFormatter == p_sLINEFIER_DIRECTIVE:
				sTagSubstitutionFinal = me.lnf(sTagSubstitutionFinal)
			
			elif sFormatter == p_sINT_INCREMENTER_DIRECTIVE:
				# TBD: add incrementing of tag variable without producing a template
				sTagSubstitutionFinal = me.inc(sTagCoreInTplItemPart)  # Tag shall exist only in report-side JSON file
				
			else:
				pass
			
			
			if sType == "IF":
				sTagSubstitutionFinal = "\'"+sTagSubstitutionFinal+"\'"	 # evaluable comparison string must be wrapped with quotes
			me.oTrace.INFO(
				"template item part filling: tries to replace " + sTagFrameInTplItemPart + " with '" + sTagSubstitutionFinal + "' in template item part'" + sFilledTplItemPart + "'","kick")
			sFilledTplItemPart = sFilledTplItemPart.replace(sTagFrameInTplItemPart, sTagSubstitutionFinal)	# replaces all instances
		
		# TBD: add returning of latest symbolified node id (to be able to attach "label" node if needed)
		me.oTrace.INFO("template item part before checking: '" + sFilledTplItemPart + "'","kick")
		if "MISSING" not in sFilledTplItemPart:
			(nGroupsCnt, tPossiblyMissingKeys) = me.tryCatchRepeat(sFilledTplItemPart,
																sTplTagCatchRe)	 # search for possible leftover tags

			if nGroupsCnt == p_NO_GROUPS:
				bFillingSuccess = True
			else:
				me.oTrace.INFO("failed to fill template item part'" + sFilledTplItemPart + "'","kick")
			
			# me.oTrace.INFO("#1 success/latest.symbol/template: '" + str(bFillingSuccess) + "'/'" + sLatestSymbolNameRet + "'/'" + sFilledTpl + "'")
		
		sFilledTplItemPart = sFilledTplItemPart.replace("\\\\n\"", "\"")  # added due to observation in S2Terminal output capture parsing
		
		return bFillingSuccess, sLatestSymbolNameRet, sFilledTplItemPart  # TBD: replace with 'me.m_dLatestRet' -usage to simplify caller
	
	# ===============================================================================
	def assignPreProcConf(me, TBD):
	# ===============================================================================
		pass

	# =============================================
	def createOtlLink(me, sFileName, sTopicName):  # transferred here because even TraceUtils may use this
	# =============================================
		# TBD: transfer to NotetabUtils.py
		sOtlLinkToSidekickTopic = "[" + sFileName + "::" + sTopicName + "]"
		return sOtlLinkToSidekickTopic
	
	# =============================================
	def tryMatchAnyInRegexArray(me, sLine, asRegexes):
	# ============================================
		# input: string, array of regexes
		# output: True or false
		bRetStatus = False
		sRegexesAsOrChain = "(" + ")|(".join(asRegexes) + ")"
		if sRegexesAsOrChain == "All_":
			bRetStatus = True
		else:
			if re.match(sRegexesAsOrChain, sLine):
				bRetStatus = True
		#https: // stackoverflow.com / questions / 3040716 / python - elegant - way - to - check - if -at - least - one - regex - in -list - matches - a - string
		return bRetStatus

	#==============================================================
	def tryCatchRepeatPairs(me,sText, sSplitMatchRE, sPairCatchRE):
	#==============================================================
		# first regex splits to parts
		# second regex splits each part to prefix/data -pair
		nGroups = p_NO_GROUPS
		sSplitGroupsAsStr = " "
		AoApairs = []  # array of arrays
		# -----------------------------------------------------
		tSplitGroups = re.findall(sSplitRE, sText)  # !: returns all matches: capturing parentheses have no effect
		# -----------------------------------------------------
		if tSplitGroups:
			nSplitGroups = len(tSplitGroups)
			sSplitGroupsAsStr = str(tSplitGroups)	 # !: tuple to string
			for sPart in tSplitGroups:
				asPair = []
				oMatch = re.search(sPairCatchRE, sPart)
				if oMatch:
					asPair.append(oMatch.group(0)) # prefix
					asPair.append(oMatch.group(1)) # data
					AoApairs.append(asPair)
		else:
			me.oTrace.INFO(me.sDuty + ": regex '" + sRE + "' caught nothing from '" + sText + "'","kick")

		return nGroups, AoApairs	# !: returns a tuple (=immutable array)

	# =============================================
	def tryCatchRepeat(me,sText, sRE):	# is a generic Matcher/Catcher
	# ============================================

		# !: Python,regex,match,groups: http://www.tutorialspoint.com/python/python_reg_expressions.htm
		# !: http://www.tutorialspoint.com/python/python_tuples.htm
		# !: http://pythoncentral.io/how-to-check-if-a-list-tuple-or-dictionary-is-empty-in-python/
		nGroups = p_NO_GROUPS  # initial quess
		sGroupsAsStr = " "
		# -----------------------------------------------------
		tGroups = re.findall(sRE, sText)  # !: returns all matches: capturing parentheses have no effect
		# -----------------------------------------------------


		if tGroups:
			nGroups = len(tGroups)
			sGroupsAsStr = str(tGroups)	 # !: tuple to string

			me.oTrace.INFO(me.sDuty + ": regex '" + sRE + "' caught " + sGroupsAsStr + "' from '" + sText + "'","kick")
		else:
			me.oTrace.INFO(me.sDuty + ": regex '" + sRE + "' caught nothing from '" + sText + "'","kick")

		return nGroups, tGroups	# !: returns a tuple (=immutable array)

	# =============================================
	def tryCatchAtOnce(me, sText, sRE):
	# =============================================
		# this is the frontline "catcher"
		# adds captured values to dictionary where key names are formed by position numbers
		#	-	key values within this function are formed by order number "1", "2",...
		#	-	caller can then add "metadata" key/val -pairs (eg. sequence numbers) to returned dictionary
		#		-	can be used for filling templates which require also other than just captured data
		#

		# !: Python: catching result defacto "reserved word" is "group"

		dSeqGroups = {}	 # dictionary, where keys are integer strings "1", "2", "3", ...
		nGroupPos = 0
		oRE = re.compile(sRE)
		sRetStatus = "NOT_MATCH"  # initial quess

		# -----------------------------------------------------
		oMatch = oRE.match(sText)
		# -----------------------------------------------------
		if oMatch:
			tGroups = oMatch.groups()  # !: Python: returns all captures in a tuple http://www.tutorialspoint.com/python/python_tuples.htm
			# me.oTrace.INFO("succeeded to  match '" + sRE + "' to '" + sText + "'")
			if tGroups:	 # !: Python way to check if something (here a tuple) is empty
				for sGroup in tGroups:
					nGroupPos += 1
					sKey = str(nGroupPos)  # creates integer string key by captured group order number
					dSeqGroups[sKey] = sGroup
					me.oTrace.INFO("dSeqGroups[" + sKey + "] = " + sGroup,"kick")

				sRetStatus = "YES_CATCH"
			else:
				# oTrace.INFO("just match, no captures was requested")
				sRetStatus = "YES_MATCH"
		else:
			# oTrace.INFO("failed to match '"+sRE+"' to '"+sText+"'")
			a = 123
		sSeqGroupsAsStr = seqDictValuesToStr(dSeqGroups, ", ")
		me.oTrace.INFO("tried to match '" + sRE + "' to '" + sText + "', status='" + sRetStatus + "', caught contents='" + sSeqGroupsAsStr + "'","kick")

		return sRetStatus, dSeqGroups
	
	#=============================================
	def tryMatchOrCatch(me, sText, sRE):	# created 170912
	#=============================================
		# this is the frontline "catcher"
		me.m_dLatestCaptures = {}  # object member, where keys are integer strings "1", "2", "3", ...
		nGroupPos = -1	# so first found group pos = 0
		nGroupCount = 0
		oRE = re.compile(sRE)
		sRetStatus = "MISMATCH"

		# -----------------------------------------------------
		oMatch = oRE.match(sText)
		# -----------------------------------------------------
		if oMatch:
			tGroups = oMatch.groups()  # !: Python: returns all captures in a tuple http://www.tutorialspoint.com/python/python_tuples.htm
			me.oTrace.INFO("succeeded to  match '" + sRE + "' to '" + sText + "'","kick")
			if tGroups:	 # !: Python way to check if something (here a tuple) is empty
				for sGroup in tGroups:
					nGroupPos += 1
					sKeyName = str(nGroupPos+1) # creates integer string key by captured group order  number
					me.m_dLatestCaptures[sKeyName] = sGroup
					me.oTrace.INFO("e.m_dLatestCaptures[" + sKeyName + "] = " + sGroup,"kick")
				sRetStatus = "CATCH"   # one or more pair of capturing parentheses
			else:
				# oTrace.INFO("just match, no captures was requested")
				sRetStatus = "MATCH"   # = no capturing parentheses
		else:
			me.oTrace.INFO("FAILED to match '" + sRE + "' to '" + sText + "'","kick")
			sRetStatus = "MISMATCH"

		#me.oTrace.INFO("return status '"+sRetStatus+"'")
		return sRetStatus  #
	# TBD: parser, which puts catch results to "me.m_dLatestRet" and returns the amount of captures
	#=============================================
	def getLatestCapBy(me, sPos):
	#=============================================
		sRetVal = me.m_dLatestCaptures.get(sPos,"MISSING")
		return sRetVal
		
	#=============================================
	def tryMatchWithoutCatch(me, sText, sRE):
	#=============================================
		bRetStatus = False
		oRE = re.compile(sRE)
		# -----------------------------------------------------
		oMatch = oRE.match(sText)
		# -----------------------------------------------------
		if oMatch:
			bRetStatus = True
			me.oTrace.INFO("succeeded to match '" + sRE + "' to '" + sText + "'","kick")
		else:
			pass
			# me.oTrace.INFO("FAILED to match '" + sRE + "' to '" + sText + "'")

		#me.oTrace.INFO("tried to  match '" + sRE + "' to '" + sText + "' status = "+str(bRetStatus))
		return bRetStatus

	#=============================================
	def replaceNumericTagsWithOrderNumberValues(me, dValues, sTaggedLine):
	#=============================================
	# - simple "template filling" for text-to-text conversion
	#  - (complex) text-to-graph template filling shall occur via ReportUtils.py
		pass

	#=============================================
	def extractRemoveDirectionIndicator(me, sRegex):
	#=============================================
		# e.g. regex start
		pass


	#=============================================
	def checkIfMapContainsArrayTags(me, sMapTags):
	#=============================================
		bRetStatus = False
		oMatch = re.search(p_sARRAY_TAG_IND_re, sMapTags)
		if oMatch:
			bRetStatus = True
		return bRetStatus

	#=============================================
	def checkIfMapContainsLiteralTags(me, sMapTags):
	#=============================================
		# captured group in literal group position shall be replaced with literal tag contents
		bRetStatus = False
		oMmatch = re.search(p_sLITERAL_TAG_IND_re, sMapTags)
		if oMatch:
			bRetStatus = True
		return bRetStatus

	#=============================================
	def copyPosDictToLabelDict(me, dFeed, sDestKeys):
	#============================================
		# source dictionary: key names are based on position numbers 1...N
		# result Dictionary: key names selected by order within trap labels

		me.oTrace.INFO("...","kick")
		bStatus = False
		dTrapsByLabels = {}
		asDestKeys = sDestKeys.split()
		nDestKeysCnt = len(asDestKeys)
		nFeedDictValCnt = len(dFeed)

		if nDestKeysCnt != nFeedDictValCnt:
			me.oTrace.INFO(
				"mismatch: " + str(nFeedDictValCnt) + " feed values but " + str(nDestKeysCnt) + " destination keys","kick")
		else:
			me.oTrace.INFO("match: '" + str(nFeedDictValCnt) + "' feed values equals to '" + str(
				nDestKeysCnt) + "' destination keys","kick")
			bStatus = True
			nValCnt = nFeedDictValCnt
			for nPos in range(0, nValCnt):
				sFeedKey = str(nPos + 1)
				sFeedVal = dFeed[sFeedKey]
				sDestKey = asDestKeys[nPos]
				sDestKey = sDestKey.replace("$", "")  # TBD make more robust
				sDestVal = sFeedVal
				dTrapsByLabels[sDestKey] = sDestVal
				me.oTrace.INFO("dTrapsByLabels[" + sDestKey + "] = " + sDestVal,"kick")

		return bStatus, dTrapsByLabels

	# ===============================================================================
	def getTagParts(me, sTagWithPostfixes):
	# ===============================================================================
	
		#tag structure alternatives
		#	<prefix><tagname>
		#	<prefix><tagname>"."<modifier>
		#	<prefix><tagname>"."<reference>"."<modifier>
		sTag = ""
		sModifier = "N/A"  # eg. "sym"
		sRefTag = "N/A"	 # eg. "prev"
		asTagParts = sTagWithPostfixes.split(".")  # picks "lbl", "sym" etc.
		nTagPartsCnt = len(asTagParts)
		bLoop = True

		sTag = asTagParts[0]  # allways

		while bLoop == True:  # !: just to make it possible to break out of if-then-else -construction
			bLoop = False
			if nTagPartsCnt > 3:
				me.oTrace.INFO("EROR:too many parts " + str(nTagPartsCnt) + "in tag '" + sTagWithPostfixes + "'","kick")
				break
			if nTagPartsCnt == 3:
				sRefTag = asTagParts[1]	  # eg. previous node
				sModifier = asTagParts[2]
				break
			if nTagPartsCnt == 2:
				sModifier = asTagParts[1]

		me.oTrace.INFO("original.tag/tag/ref.tag/modifier = '" + sTagWithPostfixes + "'/'" + sTag + "'/'" + sRefTag + "'/'" + sModifier + "'","kick")

		return sTag, sRefTag, sModifier

	# ==============================================================================
	def copyDictByKeyNamePostfixes(me, dDict, sPostfix):
	# ===============================================================================
		# copies a dictonary to a new one, where key names will contain given postfix
		dRetDict = {}
		try:
			for sKey, sVal in dDict.items():
				sNewKey = sKey + sPostfix
				dRetDict[sNewKey] = sVal
			me.oTrace.INFO("created postfixed dictionary >>> " + anyDictToStr(dRetDict),"kick")
		except:
			exctype, value = sys.exc_info()[:2]
			errorText = str(exctype) + " " + str(value)
			me.oTrace.INFO(errorText, "exception")
		return dRetDict

	#========================================================
	def buildSingleLineFromMultipleLines(me, asLinesArray, sTag="<NL>"):
	#"====================================================
	# NOTE: is inherited to <TextStorageUtils> which is then inherited to <EditTextStorageUtils>

		sFlattenedLines = ""
		sLine = ""
		for sLine in asLinesArray:
			if sLine == "EOB":
				sFlattenedLines = "EOB"
				break
			else:
				sRetLine = sFlattenedLines + sTag + sLine

		me.oTrace.INFO("whole flattened line group: " + sFlattenedLines,"kick")
		return sFlattenedLines
	# http://stackoverflow.com/questions/17078403/multi-symbol-string-splitter-in-python

	#=============================================
	def replaceTemplateTagsWithCapturedValues(me, sFeedLine, sReCapture, sTplLineWithTags, sOption="N/A"):
	#=============================================
		AoACatches = []
		asAllCombinations = []
		asUnstickedValues  = []
		sStickedValues = ""
	
		me.oTrace.INFO("......","kick")
		asRetLines = []
		sARRAY_SPLITTERS_par = me.getParam("ArraySplitters_")	# parameter was created after creation of focus object
		#print(sARRAY_SPLITTERS_par)

		nGroupCnt, asCapturedStrByPosNbr	= me.getRegexCatchGroups(sFeedLine, sReCapture)
		if nGroupCnt == 0:
			return
		nTplTagsCnt,  AoDTplData			= me.getTemplateTagsByTypes(sTplLineWithTags)

		#  TBD: tags count can be greater than line capture groups count, because:
		#	-	same tag can exist more than once in the template
		#	-	some tags can be:
		#		-	line split tags
		#		-	constant text strings
		dplData = {}
	
		me.oTrace.INFO("tags/groups = '"+ str(nTplTagsCnt)+"'/'"+str(nGroupCnt)+"'","kick")
		if nTplTagsCnt == -1:
			return asRetLines
		if nGroupCnt == 0:
			return asRetLines

		if 1 == True: # if nTplTagsCnt >= nGroupCnt:
			#if nTplTagsCnt >= nGroupCnt:
			for nTagSeqPosInTpl in range(0,nTplTagsCnt+1):	# seems to require the "+1"
				dTplData = AoDTplData[nTagSeqPosInTpl]
				
				sTplTagType = dTplData.get("type_", "MISSING")
				nTrapIdAtTplPos = dTplData.get("TrapId_", "MISSING")
				
				me.oTrace.INFO("TAG TYPE = " + sTplTagType,"kick")
				try:
					value = int(nTrapIdAtTplPos)
					sSomeValByCapture = asCapturedStrByPosNbr[nTrapIdAtTplPos - 1]
				except ValueError:
					sSomeValByCapture = nTrapIdAtTplPos
				
				me.oTrace.INFO("tpl.pos/group.pos/group.contents/group.type = "+ str(nTagSeqPosInTpl) +"'/'"+ str(nTrapIdAtTplPos) +"'/'"+sSomeValByCapture+"'/'"+sTplTagType+"'","kick")
				
				if sTplTagType == "MISSING":
					me.oTrace.INFO("Tag type is MISSING","kick")
					break
				
				if nTrapIdAtTplPos	== "MISSING":
					me.oTrace.INFO("Trap id is MISSING","kick")
					break

				if sTplTagType == "SCALAR":
					asScalarVal = [sSomeValByCapture]
					me.oTrace.INFO("APPEND SCALAR: "+sSomeValByCapture,"kick")
					AoACatches.append(asScalarVal)

				elif sTplTagType == "ARRAY":	#  template contained "@" characters
					asUnstickedValues = re.split(sARRAY_SPLITTERS_par, sSomeValByCapture)
					asUnstickedValuesForAppend = filter(None, asUnstickedValues)
					   # Python: removes empty strings. seems to need I/O -difference
					AoACatches.append(asUnstickedValuesForAppend)

				elif sTplTagType == "SPLITTER":
					me.oTrace.INFO("TBD: add usage","kick")

				elif sTplTagType == "LITERAL":
					asScalarVal = [sSomeValByCapture]	# !:
					AoACatches.append(asScalarVal)
					
				else:
					me.oTrace.INFO("ERROR: unknown template tag type '"+sTplTagType+"'","kick")
					break
			bIsEqual = me.updateInfoByEqualityToPrevLine(sReCapture, sTplLineWithTags)
			# TBD:
			if sOption == "DIFF": # to write only changed lines to edition file
				if bIsEqual:
					me.oTrace.INFO("lines are not written to result file, because previous capture and template equal to current ones","kick")
				else:
					# TBD: add extra return line which contains amount of similar lines if any line is ignored

					nCnt = me.getSequentialFeedLinesSimilarityCount()
					if nCnt > 0:
						pass  # TBD: add here adding of count information line

					asRetLines = me.buildLinesByCombinations(AoACatches)   # here filling templates
			else:
				asRetLines = me.buildLinesByCombinations(AoACatches) # here filling templates
		else:
			me.oTrace.INFO("Mismatch: template has "+str(nTplTagsCnt)+" tags but "+str(nGroupCnt)+ " was captured from line","kick")

		return asRetLines  # reutrns array of lines generated by "itertools" library methods

	#=============================================
	def getRegexCatchGroups(me, sFeedLine, sReCapture):
	#=============================================
		# every regex catch group has implicit left-to-right order number	0 ... N
		
		oRE = re.compile(sReCapture)
		oMatch = oRE.match(sFeedLine)
		asCapturedStrByPos = []
		dCapturedStrByPos = {}
	
		me.oTrace.INFO("Feed.Line/Capture.Regex = '"+sFeedLine+"'/'"+ sReCapture+"'","kick")
		nCatchCnt = 0
		if oMatch:	# !: Python way to check if something (here a tuple) is empty
			tCatches = oMatch.groups()
			nCatchCnt = len(oMatch.groups())
			me.oTrace.INFO("succeeded to catch " + str(nCatchCnt) + " groups by '" + sReCapture + "' from line '" + sFeedLine + "'","kick")
			for i in range(0, nCatchCnt):	# left-to-right catches
				nCatchGroupPos = i + 1	#  group(0) is the WHOLE regex
				sCapturedStr =	oMatch.group(nCatchGroupPos)
				asCapturedStrByPos.append(sCapturedStr)
				me.oTrace.INFO("asCapturedStrByPos["+str(nCatchGroupPos-1)+"] = '"+sCapturedStr+"'")
		else:
			me.oTrace.INFO("failed to catch any groups by '" + sReCapture + "' from line '" + sFeedLine + "'","kick")
		return nCatchCnt, asCapturedStrByPos

	#=============================================
	def getTemplateTagsByTypes(me, sTplLineWithTags):
	#=============================================

		# every template tag has implicit left-to-right order number   0 ... N
		# every template tag has also explicit number, which refers to caopture group implicit order number 0...N

		asAllTaggishParts = sTplLineWithTags.split()
		nTaggishParts = len(asAllTaggishParts)

		me.oTrace.INFO("template line ['"+sTplLineWithTags+"'] contains'"+str(nTaggishParts)+"'taggish parts ","kick")
		  # split by spaces. Can contain prefixes
		nTagPos = -1
		nTagsCnt = 0
		# TBD: add more types than "SCALAR" and "ARRAY"

		me.AoDTplData = []	 # raised to object variable for easier debugging
		# collects all tags from template line
		# every collected tag item contains: required catch group pos id number and tag type prefix
		for sTplPart in asAllTaggishParts:	# collects all tags from template line
			#me.oTrace.INFO("assign to taggish part in template")
			if re.match(p_sSCALAR_TAG_IND_re, sTplPart):
				sTagAsNbr = sTplPart.replace("$","")
				nTrapNbrId = int(sTagAsNbr)
				dAddDict = {'type_': 'SCALAR', 'TrapId_': nTrapNbrId}
				# https: // bytes.com / topic / python / answers / 781432 - how - create - list - dictionaries
				me.AoDTplData.append(dict(dAddDict))
				nTagPos += 1
			elif re.match(p_sARRAY_TAG_IND_re, sTplPart):
				sTagAsNbr = sTplPart.replace("@", "")
				nTrapNbrId = int(sTagAsNbr)
				dAddDict = {'type_': 'ARRAY', 'TrapId_': nTrapNbrId}
				me.AoDTplData.append(dict(dAddDict))

				# everything between {...} goes to single location of array
				nTagPos += 1
			elif re.match(p_sLINE_SPLITTER_TAG_re, sTplPart):  # for building multiple different lines from single line
				dAddDict = {'type_': 'SPLITTER', 'TrapId_': sTplPart}	# the "TrapId_" is not used here as "ID" saver purpose but as the value saver purpose

				me.AoDTplData.append(dict(dAddDict))
				nTagPos += 1
			else:
				dAddDict = {'type_': 'LITERAL', 'TrapId_': sTplPart}	# the "TrapId_" is not used here as "ID" saver purpose but as the value saver purpose
				me.AoDTplData.append(dict(dAddDict))
				nTagPos += 1
			me.oTrace.INFO("add tag order pos '" + str(nTagPos) + "'  " + str(dAddDict),"kick")

		nTagsCnt = nTagPos
		return nTagsCnt, me.AoDTplData	# used only if attached regex capture succeeds

	#=================================================================
	def buildLinesByCombinations(me, AoACatches):	# uses "product() method
	#=================================================================
		me.oTrace.INFO("....","kick")
		try:
			asAllCombinations=[]
			# AoACatches tracing loop located here prevented following operations for some reason !!!!!!!
			AoTallCombinations = list(product(*AoACatches))	  # uses "itertools"
			me.oTrace.INFO("contents = "+arrayToStr(AoTallCombinations))
			for tCombinationInstance in AoTallCombinations:
				me.oTrace.INFO("single combination of all combinations","kick")
				sInstance = ""
				for sInstancePart in tCombinationInstance:
					#me.oTrace.INFO("part of single combinations")
					me.oTrace.INFO("combination instance part = "+sInstancePart,"kick")
					sInstance = sInstance + " " + sInstancePart
				asAllCombinations.append(sInstance)
		except:
			me.oTrace.INFO("building combinations", "exception","kick")
		return asAllCombinations

	#=============================================
	def isCaptureSimilarToPrevCapture(me, sReCapture, sTplLineWithTags):  # TBD: take in use in <EDIT>
	#=============================================
		bIsSimilar = False
		if (me.sReCapturePrev == sReCapture and me.sTplLineWithTagsPrev == sTplLineWithTags):
			me.oTrace.INFO("capture regex '"+sReCapture+"' and template '"+ sTplLineWithTagsequal+"' are similar to previous ones","kick")
			me.nRepeatLineCnt += 1
			bIsSimilar = True
		else:
			me.oTrace.INFO("previous capture and template differ from current ones","kick")
			nRetCnt = me.nRepeatLineCnt	  # final amount of repetitions is now known
			me.nRepeatLineCnt = 0	# initialized for next usage
			bIsSimilar = True
		me.sReCapturePrev = sReCapture	# used. if only changed lines (actually patterns) are meant to be written target file
		me.sTplLineWithTagsPrev = sTplLineWithTags
		return bIsSimilar

	#=============================================
	def getSequentialFeedLinesSimilarityCount(me):
	#=============================================
	# can be used to indicate amount of sequential similar feed lines, if only changed lines are configured
	# to be written to edition file
		return me.nRepeatLineCnt

	#=============================================
	def getRangeFromArray(me, asArray, sStartRe, sEndRe):	 # for 'lightweight' filtering
	#=============================================
		asRet = ["MISSING"]	 # initiel quess
		bStartAlreadyFound = False
		for sStr in asArray:
			me.oTrace.INFO("array item: '" + sStr + "'","kick")
			xResult = re.match(sEndRe, sStr)  # terminates collecting
			if xResult:
				if bStartAlreadyFound:
					me.oTrace.INFO("range collecting ended, because '" + sEndRe + "' did match to string '" + sStr + "'","kick")
					break
				else:
					me.oTrace.INFO("ERROR: end found by "+sEndRe+" before start found by "+sStartRe,"kick")
					break
			else:
				xResult = re.match(sStartRe, sStr)
				if xResult:
					bStartAlreadyFound = True
					me.oTrace.INFO("range collecting started, because '" + sStartRe + "' did match to '" + sStr + "'","kick")
					asRet = [] # initialization
				else:
					if bStartAlreadyFound:
						asRet.append(sStr)
					else:
						pass # do nothing
	
		me.oTrace.INFO("returns array '" + arrayToStr(asRet)+"'","kick")
		return asRet
	
	# =============================================
	def buildMultipleLinesFromSingleLine(me, sText, sRE, sTrapTagsWithPrefixes):   # returned here frob "bak" file (170611) why was removed ???
	# ============================================
	# if one or more tags contain an array tag prefix, combinations of all scalar and array tag capture joints are produced as an array

		AoACatches = []
		# !: Python: "[...]" are lists, but "(...)" are tuples
		asMainCatches = []	  # !: Python: array intialization by brackets

		AoTallCombinations = []
		asAllCombinations = []

		#sSCALAR_TAG_IND_re = me.getParam("kScalarTagRe")  # idea: "k" prefix for Python Dictionary keys
		#sARRAY_TAG_IND_re = me.getParam("kArrayTagRe")
		#sSPLITTER_ALTERNATIVES = me.getParam("kArraySplitters")
		try:

			me.oTrace.INFO("tags sequence: " + sTrapTagsWithPrefixes)
			me.oTrace.INFO("scalar.re/array.re./splitter.alternatives = "+p_sSCALAR_TAG_IND_re+"/"+ p_sARRAY_TAG_IND_re+"/"+ p_sARRAY_TAG_SPLITTERS)
			me.oTrace.INFO("text to be multified: "+sText)
			asMainTags = sTrapTagsWithPrefixes.split()	# split by spaces. Each one must contain "%" or "@" prefix
			nMainTagsCnt = len(asMainTags)
			me.oTrace.INFO("tags count: " + str(nMainTagsCnt))
			oMainRE = re.compile(sRE)
			oMainMatch = oMainRE.match(sText)
			tMainCatches = oMainMatch.groups()	# !: Python: returns all captures in a tuple http://www.tutorialspoint.com/python/python_tuples.htm


			if tMainCatches:  # !: Python way to check if something (here a tuple) is empty
				nMainCatchCnt = len(oMainMatch.groups())
				if nMainCatchCnt != nMainTagsCnt:
					me.oTrace.INFO("fail: '" + nMainTagsCnt + "' main captures expected but '" + nMainCatchCnt + "' main tags caught")
				else:
					me.oTrace.INFO("succeeded to  match '" + sRE + "' to '" + sText + "', groups count = '"+str(nMainCatchCnt)+"'")
				nMainPos = 0
				for sMainCatch in tMainCatches:
					asMainCatches.append(sMainCatch)  # traps are inserted in array
					me.oTrace.INFO("catch pos '"+str(nMainPos) +"' = '"+sMainCatch+"'")
					nMainPos += 1
				me.oTrace.INFO("start checking tag types")
				nPos = 0
				for sTag in asMainTags:
					me.oTrace.INFO("tag = "+sTag)
					if re.match(p_sSCALAR_TAG_IND_re, sTag):
						# http: // stackoverflow.com / questions / 12066054 / how - to - convert - a - str - to - a - single - element - list - in -python
						asSingleCatch = [asMainCatches[nPos]]  # creating array of single string
						AoACatches.append(asSingleCatch)
					elif re.match(p_sARRAY_TAG_IND_re, sTag):
						asMultipleSubCatches = re.split(p_sARRAY_TAG_SPLITTERS, asMainCatches[nPos])  # creating array of multiple strings
						AoACatches.append(asMultipleSubCatches)
					else:
						me.oTrace.INFO("ERROR: neither '"+p_sSCALAR_TAG_IND_re+"' nor '"+p_sARRAY_TAG_IND_re+"' did match to '" + sTag + "'")
						break
					nPos += 1
				AoTallCombinations = list(itertools.product(*AoACatches))	 # !: python: a star '*' is needed here !!! Seems to return array of tuples
				#asAllCombinations = itertools.product(AoACatches)
				for tMember in AoTallCombinations:
					sJoined = ""
					for sPart in tMember:
						me.oTrace.INFO("part = "+sPart)
						sJoined = sJoined + " "+ sPart
					asAllCombinations.append(sJoined)
					#print(tMember)
			else:
				me.oTrace.INFO("no catches")
				#TBD: add handling

			me.oTrace.INFO("done")

		except:
			me.oTrace.INFO("multiplying lines","exception")


		return asAllCombinations
	#=========================================================
	def tuneUsableLinesArray(me, asRawLines, asTailStartTags):	# eg. "//" and "#"
	#=========================================================
		me.m_dLatestRet = {}
		me.asRetLines = []
		me.oTrace.INFO("removes possible tails and ignores empty lines")

		for sRawLine in asRawLines:
			if me.tuneUsableLine(sRawLine, asTailStartTags):
				sLine = me.m_dLatestRet['Line_']
				asRetLines = me.asRetLines.append(sLine)

		return me.asRetLines

	#=========================================================
	def tuneUsableLine(me, sRawLine, asTailStartTags):	# eg. "//" and "#"
	#=========================================================
		me.m_dLatestRet = {}
		me.oTrace.INFO("removes possible tails and ignores empty line")

		me.oTrace.INFO("raw line: '"+sRawLine+"'")
		for sTailStartTag in asTailStartTags:  # for each tag in array
			me.oTrace.INFO("removes possible tail started by '"+sTailStartTag+"' from line '"+sRawLine+"'" )
			sPrefixLine = sRawLine.split(sTailStartTag, 1)[0]
			sPrefixLine = sPrefixLine.rstrip()
			if sPrefixLine != sRawLine:	 # tagged tail removed, so no need to search other tail tag
				break

		if re.search(r"^\s+$", sPrefixLine):   # !: Python check for all-spaces line
			sPrefixLine = ""
		if sPrefixLine != "":  # final or original empty lines
			me.m_dLatestRet['Line_'] = sPrefixLine
		return me.m_dLatestRet


	#=========================================================
	def BACKUP_removeLineTailsByTags(me, asTailStartTags):	# eg. "//" and "#"
	#=========================================================
		# TBD: removes possible tags and line contents after the tags
		# can be used to remove typical line end comments
		# see. http://stackoverflow.com/questions/1706198/python-how-to-ignore-comment-lines-when-reading-in-a-file

		me.oTrace.INFO("removes possible tails")
		me.asSwapBuffer = []
		for sBufferLine in me.asMainBuffer:
			me.oTrace.INFO("buffer line: '"+sBufferLine+"'")
			for sTailStartTag in asTailStartTags:  # for each tag in array
				me.oTrace.INFO("removes possible tail started by '"+sTailStartTag+"' from line '"+sBufferLine+"'" )
				sPrefixLine = sBufferLine.split(sTailStartTag, 1)[0]
				sPrefixLine = sPrefixLine.rstrip()
				if sPrefixLine != sBufferLine:	# tagged tail removed, so no need to search other tail tag
					break
			if sPrefixLine != "":  # final or original empty lines
				me.asSwapBuffer.append(sPrefixLine)
		me.asMainBuffer = me.asSwapBuffer
		me.updateEndPos()

	#----------------------------------------------------------------------------------------
	#  SPECIFIC CATC/MATCH methods
	#=============================================
	def isOtlLink(me,sLine):  # resides here because focus file is not necessarily complete OTL file
	#=============================================
		# !: Python: example of function which returns False OR <multiple values
		me.m_dLatestRet = {}  # initial quess: will fail

		oOtlLinkRE = re.compile(p_sOTL_TOPIC_LINK_CATCH_re)
		# TODO: add usage of "p_sOTL_TOPIC_LINK_CATCH_AND_WRITE_FILE_re" ~190426~
		oMatch = oOtlLinkRE.match(sLine)
		if oMatch:
			me.oTrace.INFO("regex '"+p_sOTL_TOPIC_LINK_CATCH_re+"' matches to string '"+sLine+"'")
			me.m_dLatestRet['_DestFileName_'] = oMatch.group(1)
			me.m_dLatestRet['_DestTopicName_'] = oMatch.group(2)
			return True
		else:
			return False
	#=========================================================
	def isConversionPhaseTitle(me, sLine):
	#=========================================================
		me.m_dLatestRet = {}
		oCatch = re.match(p_sPHASE_TITLE_CATCH_re, sLine)
		if oCatch:
			me.m_dLatestRet["_Phase_"]		= oCatch.group(1)	 # eg. "[2.FILTER]"
			me.oTrace.INFO("regex '" + p_sPHASE_TITLE_CATCH_re + "' matches to string '" + sLine + "'")
			return True
		else:
			return False
	#=========================================================
	def isFileRoleAndName(me, sLine):
	#=========================================================
		me.m_dLatestRet = {}
		oCatch = re.match(p_sFILE_ROLE_NAME_CATCH_re, sLine)
		if oCatch:
			me.m_dLatestRet["_Role_"]	= oCatch.group(1)			# leading "_" -characters added to separate from configuration file tags notation (with tail-only "_" -characters)
			me.m_dLatestRet["_Name_"]	= oCatch.group(2)	# eg. "..\AUT\foo.txt"
			me.oTrace.INFO("regex '" + p_sFILE_ROLE_NAME_CATCH_re + "' matches to string '" + sLine + "'")
			return True
		else:
			return False
	#=========================================================
	def isBatCommandLine(me, sLine):
	#=========================================================
		me.m_dLatestRet = {}
		oCatch = re.match(p_sBAT_COMMAND_NAME_CATCH_re , sLine)
		if oCatch:
			me.m_dLatestRet["_CommandName_"]		= oCatch.group(1)  # eg. 'Python'
			me.m_dLatestRet["_CommandLineContents_"]	= oCatch.group(2)  # eg. <TAGS>
			me.oTrace.INFO("regex '" + p_sBAT_COMMAND_NAME_CATCH_re	 + "' matches to string '" + sLine + "' at '"+me.sDuty+"'")
			return True
		else:
			return False

	#=========================================================
	def isPythonScriptExecutionLine(me, sLine):
	#=========================================================
		oMatch = re.match(p_sPYTHON_COMMAND_LINE_MATCH_re , sLine)
		if oMatch:
			me.oTrace.INFO("regex '" + p_sPYTHON_COMMAND_LINE_MATCH_re + "' matches to string '" + sLine + "' at '"+me.sDuty+"'")
			return True
		else:
			return False

	#=========================================================
	def replaceCommandTagParamsWithValues(me, sTaggyCommandParams, dTagValues):
	#=========================================================
		me.oTrace.INFO("try to replace tags in '"+sTaggyCommandParams+"'","kick")
		sxParams = sTaggyCommandParams
		for sTag, sVal in dTagValues.items():
			sxReplaced = sxParams.replace(sTag, sVal)
			if sxReplaced != sxParams:
				me.oTrace.INFO("replaced '" + sTag + "' with '" + sVal + "'","kick")
			sxParams = sxReplaced
		me.oTrace.INFO("replaced result = '" + sxParams+"'","kick")
		sTaglessCommandParams = sxParams
		return sTaglessCommandParams
	
	



	# =============================================
	def lbl(me, sStr):
	# =============================================
		# converts or removes characters which are not valid within eg. Graphviz labels
		# -	  long single line is divided to multiple short lines ( to make a compact "label" eg. for Graphviz nodes/edges)
		# TBD: tester function
		# nPartMaxLen = 32
		sLbl = sStr.replace("\\", "\\\\\\\\")
		# TRACE("labellable string before modifications: '$sLbl'");
		sLbl = sLbl.replace("\\\\\\\\", "\\\\\\\\ ")
		# TRACE("labellable string after possible backslashes added printable: '$sLbl'");
		asParts = []
		sLbl = sLbl.replace("\/", "\/ ")
		sLbl = sLbl.replace("_", "_ ")
		sLbl = sLbl.replace("\"", " ")
		# $sLbl =~ s/_/\_ /g;
		
		if sLbl == "":
			sLbl = "EMPTY"
			return sLbl
		# TBD: add conversion of TAGS, (eg. "<NL>"	to	"\\n")
		# TRACE("labellable string after cutting spaces adding: '$sLbl'");
		
		asParts = sLbl.split("\s+")	  # TBD: why this splitting doesn't work ? 180821
		sResultStr = ""
		nNextStepPos = nLABEL_PART_SPLICE_LEN_MAX
	
		#print("label parts length = "+str(nLABEL_PART_SPLICE_LEN_MAX)+" label parts = " + '---'.join(asParts))
		
		for sPart in asParts:
			sResultStr = sResultStr + " " + sPart
			
			nTotalLen = len(sResultStr)
			if nTotalLen > nNextStepPos:
				sResultStr = sResultStr + "\\\\n"
				nTotalLen = len(sResultStr)
				nNextStepPos = nTotalLen + nLABEL_PART_SPLICE_LEN_MAX
			
			
			# TRACE("labelled string before removing cutting spaces '$ResultStr'");
		
		sResultStr = sResultStr.replace("\\\\ ", "\\\\")  # to return non-splitted positions to original
		sResultStr = sResultStr.replace("\\n ", "\\n")
		sResultStr = sResultStr.replace("\/ ", "\/")
		
		# TRACE("string '$s' labelled to '$ResultStr'");
		# TRACE_RET();
		return sResultStr
	
	
	# =============================================
	def lnf(me, sStr, sTag="<NL>"):
	# =============================================
		# changes given tags to line feeds
		# for linefying tagged texts
		#print("try linefy flattened text: " + sStr)
		sLinefiedStr = sStr.replace(sTag, sLINE_FEED)
		return sLinefiedStr
	
	
	# =============================================
	def sym(me,sStr):
	# =============================================
		# converts or removes characters which are not valid for symbol names within most programming languages (or Graphviz names)
		
		nStrLen = len(sStr)	 # symbol name size limited for case of long (= multi-line) texts
		if nStrLen > nSYMBOL_NAME_LEN_MAX:
			sStrForSym = sStr[:nSYMBOL_NAME_LEN_MAX]
		else:
			sStrForSym = sStr
		
		sStrAsSym = re.sub('\W', '_',
						   sStrForSym)	# !: Python: regex in substitution: use 're' -module, NOT 'replace()' -function !!!!!!
		sStrAsSym = re.sub("^\d", "_", sStrAsSym)  # leading numeric chars
		if sStrAsSym == "":
			sStrAsSym = "EMPTY"
		return sStrAsSym
	#================================
	def inc(me, sKey):
	#================================
		# can be used to add:
		# -	 sequence numbers to eg. Graphviz edge labels
		# -	 individualizing postfixes for eg. Graphviz various type node names
		nIntVal = me.dGeneratedValues.get(sKey, 0)
		nIntVal = nIntVal + 1
		me.dGeneratedValues[sKey] = nIntVal
		return	str(nIntVal)
	
	#=============================================
	def arrayToScalarDict(me, asArray):
	#=============================================
		# https://stackoverflow.com/questions/4576115/convert-a-list-to-a-dictionary-in-python
		# every even pos 0,2,4,... value is <KEY>, odd pos 1,3,5,... value is <VAL>
		# can interpret "DoD" items in actually "DoA" (JSON) data structure
		dRet = {}
		for nPos, sItem in enumerate(asArray):
			if nPos % 2 == 0:
				dRet[sItem] = asArray[nPos + 1]
		me.oTrace.INFO("conversion result "+anyDictToStr(dRet),"kick")
		return dRet
	
	#=============================================
	def arrayToDictOfDualArrays(me, asArray):
	#=============================================
		# https://stackoverflow.com/questions/4576115/convert-a-list-to-a-dictionary-in-python
		# pos 0,3,6,...		is <KEY>, eg. enable condition regex
		# pos 1,4,7,...		is <VAL> eg. disable condition regex
		# pos 2,5,8,...		is <VAL> eg. disable condition search direction indicator
		# can interpret "DoD" items in actually "DoA" (JSON) data structure
		#TBD key IS start regex, array members are rnd regex and picking direction
		nSetPos = -1
		sKey = ""
		sVal1= ""
		sVal2= ""
		asStr = []
		#dictOfDualArrays = {}
		try:
			for sStr in asArray:
				#print (sStr)
				nSetPos = nSetPos + 1
				if nSetPos == 0:
					sKey = sStr
				elif nSetPos == 1:
					sVal1= sStr
				elif nSetPos == 2:
					sVal2 = sStr
					asStr.append(sVal1)
					asStr.append(sVal2)
					#print (asStr)
					me.dictOfDualArrays[sKey] = asStr
					nSetPos= -1
					asTmp = ""
					asStr = []
		except:
			exctype, value = sys.exc_info()[:2]
			errorText = str(exctype) + " " + str(value)
			me.oTrace.INFO(errorText)
		#return dictOfDualArrays

		#print ("conversion result "+anyDictToStr(me.dictOfDualArrays))
	
	#=============================================
	def getDualValuesByKey(me, sKey):
	#=============================================
		asStr = []
		asStr = me.dictOfDualArrays[sKey]
		pass
		return asStr[0], asStr[1]

	#=============================================
	def findKeyMatchWithDualValues(me, sLine):
	#=============================================
		try:
			me.oTrace.INFO("sLine = "+sLine,"kick")
			sVal1	= "NONE"
			sVal2	= "NONE"
			sKey	= "NONE"
			for sKey, asValPair in me.dictOfDualArrays.items():
				oMatch = re.search(sKey, sLine)
				if oMatch:
					sVal1 = asValPair[0]
					sVal2 = asValPair[1]
		except:
			exctype, value = sys.exc_info()[:2]
			errorText = str(exctype) + " " + str(value)
			me.oTrace.INFO(errorText,"exception")
		return sKey, sVal1, sVal2

	#=====================================================================
	def findFirstDictByKeyMatchVal(me, adCfg, sKeyForMatchVal, sLine):
	#=====================================================================
	# if value of given key is a regex which matches to given line, the focus dictionary is returned
	#	-	input key name is hard-coded in caller and in input AoD
		dRetDict = {}
		try:
			for dDict in adCfg:
				sMatchRe = dDict.get(sKeyForMatchVal, "MISSING")
				if sMatchRe != "MISSING":
					bStatus = me.tryMatchWithoutCatch(sLine, sMatchRe)
					# me.oTrace.INFO("tried match dict regex '" + sMatchRe + "' to line '" + sLine + "' ,status = "+str(bStatus))
					if bStatus == False:
						next
					else:
						dRetDict = dDict
				else:
					me.oTrace.INFO("ERROR: key name " + sKeyForMatchVal + " 'does not exist in focus dictionary")
					break
		except:
			exctype, value = sys.exc_info()[:2]
			errorText = str(exctype) + " " + str(value)
			me.oTrace.INFO(errorText, "exception")
		finally:
			return dRetDict

###########################################################################################################
############# TEXT STORAGE UTILS REGION ###################################################################
###########################################################################################################

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


###########################################################################################################
############# NOTETAB UTILS REGION ########################################################################
###########################################################################################################

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


###########################################################################################################
############# EDIT TEXT STORAGE UTILS REGION ##############################################################
###########################################################################################################

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
from TextStorageUtils import *

# Removed edit <start>/<end> checkings (shall be done in <FILTER> module)

#=============================================================
class ex_END_EDITED_FILE_WRITING(Exception):    # !: Python: making own exception to get "goto" -alike exit from nested loops
	def __init__(me):
		pass

# TBD: transfer <rewording> in this file
class clEditTextStorage(clTextStorage):
    # =========================================================
    def __init__(me, sDuty, oTrace, sTheseDriveLetter="N/A", sCreatorPath="N/A",
                 sCreatorName="N/A"):  # python constructor
    # =========================================================
#
        me.oTrace = oTrace
        me.oTrace.INFO("constructor for '" + sDuty + "'","kick")
        clTextStorage.__init__(me, sDuty, oTrace)  # # - parent class contains already 'clParams'

        me.setOperability(True,"initial quess")  # initial quess
        me.sTheseDriveLetter = sTheseDriveLetter
        me.sCreatorPath = sCreatorPath
        me.sCreatorName = sCreatorName  # creator script name

        me.sDuty = sDuty  # means the "task" or "role" of the object. Mainly used to improve Trace Log
        me.oEditConfByJson = 0
        me.oRewordConfByJson = 0   # added 170717
        me.sJoinedLines = ""
        me.oStFilterJoin = clState("lines joining", me.oTrace)
        me.oStFilterJoinType = clState("joining by regex or line count", me.oTrace)

        me.sConfDuty = "MISSING"
        me.sConfFile = "MISSING"

    #=========================================================
    def assignEditConfByJson(me, oEditConfByJson):
    #=========================================================
		# versatile filtering operations lines are passed, modified,expanded, combined etc.
		# can be used only when writing from buffer to file
        me.oEditConfByJson 	=  oEditConfByJson
        me.sConfDuty = me.oEditConfByJson.getDuty()
        me.sConfFile = me.oEditConfByJson.getAssignedFileName()
        me.oTrace.INFO("duty '"+me.sConfDuty+"' by file '"+me.sConfFile+"'")

    # =========================================================
    def assignRewordConfByJson(me, oRewordConfByJson):
    # =========================================================
        # versatile filtering operations lines are passed, modified,expanded, combined etc.
        # can be used only when writing from buffer to file
        me.oRewordConfByJson = oRewordConfByJson
        sConfDuty = me.RewordConfByJson.getDuty()
        sConfFile = me.oRewordConfByJson.getAssignedFileName()
        me.oTrace.INFO("duty '" + sConfDuty + "' by file '" + sConfFile + "'")

    # =========================================================
    def writeToFileByEditConf(me, sResultFileFullName):
    # =========================================================
        # <EDIT>: just from buffer to file (for simplicity)
        # https:// www.daniweb.com / programming / software - development / code / 216789 / breaking - out - of - nested -oops - python
        # python !: exit from nested loops
        # whole storage buffer is handled within this function
        if not isReasonableFileName(sResultFileFullName, me.oTrace):
            return False

       
        me.sResultFileFullName = sResultFileFullName
        fhResultFile = open(sResultFileFullName, "w")  # TBD: change to use parent class file operations
        oStWriting = clState("file writing by config JSON", me.oTrace)
        oStEdit = clState("edit items retrieval", me.oTrace)
        oStFeed = clState("feed lines retrieval", me.oTrace)

        oStWriting.setState("st_EDIT_AHEAD","initialization")

        oStFeed.setState("st_GET_NEXT", "feed initialization")
        oStEdit.setState("st_GET_NEXT", "edit initialization")
        # no  fhResultFile writes at all ????
        me.rewind()
        bLinesLeft = True

        sFeedLine   = "MISSING"
        sNowRegex   = "IDLE"
        sNowRole    = "IDLE"
        sNowTarget  = "IDLE"

        me.oTrace.INFO("start checking feed lines for config operations", "topic")

        try:
            while bLinesLeft:
                asAddLines = []
                if oStFeed.isState("st_GET_NEXT"):
                    sFeedLine = me.getStoreNextLine()  # TBD: use <FILTER> to produce the buffer lines
                    me.oTrace.INFO("sFeedLine = '"+sFeedLine+"'")
                    # TBD: add rewording check here
                    if me.checkIfLinesEnded():
                       me.terminateEditing("feed lines ended")
                        
                if oStWriting.isState("st_EDIT_AHEAD"):
                        #if me.checkIfEditConfItemsEnded():
                         #   me.rewindEditConf("for unhandled feed lines")
                    if oStEdit.isState("st_GET_NEXT"):  # TBD: correct bug
                        if me.getNextEditConfData("main retrieval"):
                            sNowRegex   = me.dRet["_Match_"]
                            sNowRole    = me.dRet["_Role_"]
                            sNowTarget  = me.dRet["_Target_"]
                        else:
                            me.oTrace.INFO("All edit config items handled")
                            break
                        oStEdit.setState("st_KEEP_CURRENT","default behaviour")
                        # NOTE: just these tree types
                        # TBD: incremental search and relative position feed line match
                        me.oTrace.INFO("Edit conf item role is now = '"+sNowRole+"'")
                    if sNowRole == "CATCH":
                        asAddLines = me.replaceTemplateTagsWithCapturedValues(sFeedLine, sNowRegex,sNowTarget)  # 'itertools' used at the bottom
                        if not asAddLines:
                            oStEdit.setState("st_GET_NEXT")
                    elif sNowRole == "INC_SEARCH":
                        nFeedLinePos = me.findByIncSearch(sNowRegex)  # getStoreNextLine() -calls are repeated inside the callee
                        # - the "sNowRegex" must here be a "|" char separated sequence of regexes
                        if nFeedLinePos == p_nIMPOSSIBLE_POS:
                            me.terminateEditing("incremental search failed")
                        else:
                            oStEdit.setState("st_GET_NEXT", "default direction")
                    elif sNowRole == "JOIN":
                        if me.tryMatchOrCatch(sFeedLine, sNowRegex) != "MISMATCH":
                            asAddLines = me.joinLinesUpTo(sFeedLine, sNowTarget)
                    elif sNowRole == "EXACT":
                        sLineAtOffset = me.goRelPosGetLine(int(sNowTarget))
                        asAddLines = me.replaceTemplateTagsWithCapturedValues(sLineAtOffset, sNowRegex, sNowMaps)
                        if not asAddLines:
                            me.terminateEditing("exact line capture failed '" + sLineAtOffset + "'/'" + sNowRegex + "'")
                    elif sNowRole == "CHANGED":  # TBD: use "updateInfoIfSimilarToPrevLine()"
                            # if feed line differs enough from previous one, it is written to result file
                            if me.tryMatchOrCatch(sFeedLine, sNowRegex) != "MISMATCH":
                                if me.isCaptureSimilarToPrevCapture(sNowRegex, sNowTarget):
                                    pass # target file is NOT updated
                                else:
                                    pass  # target file IS updated
                                #
                            pass
                    elif sNowRole == "PASS":  # TBD: feed file to result file without any modifications
                        pass
                    else:
                        me.oTrace.INFO("unknown editing step role '"+ sNowRole+"'")
                       
                        # asAddLines = me.tryBuildProperAmountOfLinesBySingleFeedLine(sLine, sNowRegex, sNowMaps) # non-structured function
                    me.appendToFileIfLinesExist(sResultFileFullName, asAddLines)
                    # TBD add scalar outputs 170421
                else:
                    pass
                   # me.oTrace.INFO("duty '" + me.sConfDuty + "' by file '" + me.sConfFile + "'")

        except ex_END_EDITED_FILE_WRITING:
            pass
        finally:
            pass
       # me.fhResultFile.close()  # writeToFileByConf(e)

    # =========================================================
    def joinLinesUpTo(me, sFeedLine, sTerminatingReOrInt):  # start join line is included as first subline
    # =========================================================
        sJoinedLines = ""
        # runs within this function until <end regex>, <lines count> or "EOB" is detected
        sLinesJoinerTag = me.getParam("LinesJoiner_", p_sLINE_SEPARATOR_TAG )  # if not defined, then uses the "p_..." - constant string
        if isIntStr(sTerminatingReOrInt):  # integer means amount of joinable lines
            me.oTrace.INFO("join "+sTerminatingReOrInt+" following lines to single line")
            nLinesCount = int(sTerminatingReOrInt)

            for nOffset in range(nLinesCount):  # number of lines after first line
                sFeedLine = me.getStoreNextLine()
                if me.checkIfLinesEnded():
                    sJoinedLines = "EOB"
                    me.oTrace.INFO("Detected '" + sJoinedLines + "' when " + str(
                        nOffset) + " lines of '" + sTerminatingReOrInt + "' reached")
                    break
                me.sJoinedLines = me.sJoinedLines + sLinesJoinerTag + sFeedLine
        else:  # non-integer means terminating regex
            me.oTrace.INFO("join following lines to single line until '"+ sTerminatingReOrInt+"' matches")
            while True:
                sFeedLine = me.getStoreNextLine()
                if me.checkIfLinesEnded():
                    me.sJoinedLines = "EOB"
                    me.oTrace.INFO(
                        "Detected '" + sJoinedLines + "' before edit join end regex '" + sTerminatingReOrInt + "' found")
                    break
                else:
                    me.sJoinedLines = me.JoinedLines + sLinesJoinerTag + sFeedLine
                    if re.match(sTerminatingReOrInt, sFeedLine):  # end join line is included as last subline
                        break
        return [me.sJoinedLines]   # array of single line

    # ====================================================
    def getNextEditConfData(me, sPurpose):
    # =====================================================
        me.oTrace.INFO("------------")
        dItem = me.getEditConfNextItem()

        if dItem:
            me.oTrace.INFO("got conf items for '" + sPurpose + "'")
            me.dRet["_Match_"]   = dItem.get("_Match_","MISSING")
            me.dRet["_Role_"]    = dItem.get("_Role_", "MISSING")
            me.dRet["_Target_"]  = dItem.get("_Target_", "MISSING")
            return True
        else:
            me.oTrace.INFO("no more conf items for '"+sPurpose+"'")
            return False

    # =========================================================
    def checkIfEditConfItemsEnded(me):
    # =========================================================
      
        # This wrapper method is for making caller method "cleaner"
        bStatus = me.oEditConfByJson.alreadyUsedLastInAoD()

        me.oTrace.INFO("status = '"+str(bStatus)+"'")
        return bStatus

    # =========================================================
    def getEditConfNextItem(me):
    # =========================================================
        
        dRetItem = me.oEditConfByJson.getNextInAoD()
        me.oTrace.INFO("returns '"+anyDictToStr(dRetItem)+"' ")
        return dRetItem

    # =========================================================
    def rewindEditConf(me, sComment):
    # =========================================================
        if me.oRewordConfByJson:
            me.oTrace.INFO(sComment)
            me.oEditConfByJson.rewindAoD()
        else:
            me.oTrace.INFO("Reword configuration file is not configured to be used")

    # =========================================================
    def terminateEditing(me, sComment):
    # =========================================================
        me.oTrace.INFO("raised error to jump out of possibly nested loops: '" + sComment + "'")
        raise ex_END_EDITED_FILE_WRITING  # !: Python: explicit generation of exception

TODO: continue adding rest of library files to this file 191220
###########################################################################################################
############# XXXKUTILS REGION ###########################################################################
###########################################################################################################