#
# all "line capture regex" and "fill template line" functions shall be reside here
#	-	can be called from any object, not just from "ReportUtils"

import os, sys
import os.path
import re
import json
import time
#import datetime

from ParamUtils import *
from datetime import datetime
import subprocess
from itertools import *


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