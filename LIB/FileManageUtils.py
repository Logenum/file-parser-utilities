import os, sys
import os.path
import re
import json
import time
import datetime
import subprocess

# PURPOSE:
# check, create, copy (and delete) directories and files
# generate automatic directory and file names
# detect file types (text vs. image) and make corresponding actions

from TextStorageUtils import *
from TrickUtils import * # !: python import of non-class module

# TODO: add some JOURNAL file update for every path/file creation

# sFILE_FULL_NAME_CATCH_re 	= "^(.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$))"  # transferred to ParamUtils 180120
# https://techtavern.wordpress.com/2009/04/06/regex-that-matches-path-filename-and-extension/

# TBD: a "STD" -script which collects file names 180121

#class clFileManage(clTextStorage): # TBD: use rather "clFilterTextStorage"

class clManageFiles(clTextStorage):
	#=========================================================
	def __init__(me, sDuty, oTrace, sTheseDriveLetter="N/A", sCreatorPath="N/A", sCreatorName="N/A"):  # python constructor
	#=========================================================
		# trace file opens/closes are handled by main script, not in objects
		me.sTheseDriveLetter = sTheseDriveLetter
		me.sCreatorPath = sCreatorPath
		me.sCreatorName = sCreatorName  # creator script name
		me.oTrace 	=    oTrace
		me.sDuty = sDuty
	
		
		me.oEnlistmentConfByJson = 0
	
		me.XoYenlistmentRoot = 0  # JSON-to-python conversion result "anchor" # TBD: add method usage

		# files and paths Enlistment conditions from configuration JSON  file
		me.asEnlistmentBasePaths 	= []
		me.asEnlistmentFilesPickRe 	= []
		me.asEnlistmentFilesSkipRe 	= []
		me.asEnlistmentFilesAttrLbl = []
		me.asEnlistmentPathsPickRe	= []
		me.asEnlistmentPathsSkipRe 	= []
		
		clTextStorage.__init__(me, sDuty, me.oTrace)  # !: initializing parent class
		#me.sDateTime = datetime.now()
		#-----------------------------------
		me.sFocusFileFullName 	= "UNKNOWN"
		me.sFocusPathName 		= "UNKNOWN"
		me.sFocusFilePlainName 	= "UNKNOWN"
		me.sFocusFileNameBody 	= "UNKNOWN"
		me.sFocusFileNameExt 	= "UNKNOWN"

		# TBD: use rather "clFilterTextStorage"
		#me.oFileNamesCollection = clTextStorage("file names",me.oTrace)   # specific instance for file names
		#-----------------------------------

	# =============================================
	def assignResultFile(me, sResultFileFullName):
	# =============================================
		me.oFileFullNames.attachWriteFile(sResultFileFullName)
		# an instance created for better encapsulation
		# even though instanced class is already the parent class

	# =============================================
	def assignEnlistConfByJson(me, oEnlistmentConfByJsonFile):
	# =============================================
		sConfDuty = ""
		sConfFile = ""
		try:
			me.oEnlistmentConf = oEnlistmentConfByJsonFile
			#sConfDuty = me.oEnlistmentConf.getDuty()
			sConfFile = me.oEnlistmentConf.getAssignedFileName()
			me.oTrace.INFO("duty '" + sConfDuty + "' by file '" + sConfFile + "'")

			me.XoYenlistmentRoot = me.oEnlistmentConf.getXoYroot()
			# me.oTrace.setOperability(True)

			#print("read config JSON data from file '" + sConfFile + "'")
			me.oTrace.INFO("read config JSON data from file '" + sConfFile + "'")
			
			
			asArray = me.XoYenlistmentRoot.get("FileAttr_", ["None_"]) # implicit default: no attributes requested
			me.oEnlistmentConf.createNamedArray("FileAttr_", asArray)
			me.asEnlistmentFilesAttrLbl = me.oEnlistmentConf.getWholeNamedArray("FileAttr_")

			asArray = me.XoYenlistmentRoot.get("BasePaths_", "MISSING")
			me.oEnlistmentConf.createNamedArray("BasePaths_", asArray)
			me.asEnlistmentBasePaths = me.oEnlistmentConf.getWholeNamedArray("BasePaths_")
			# - array of strings retrieved in this object for faster looping

			asArray = me.XoYenlistmentRoot.get("PickFiles_", ["All_"]) # implicit default: all file names are picked
			me.oEnlistmentConf.createNamedArray("PickFiles_", asArray)
			me.asEnlistmentFilesPickRe = me.oEnlistmentConf.getWholeNamedArray("PickFiles_")
			# - array of strings retrieved in this object for faster looping

			asArray = me.XoYenlistmentRoot.get("SkipFiles_", ["None_"]) # implicit default: no file names are skipped
			me.oEnlistmentConf.createNamedArray("SkipFiles_", asArray)
			me.asEnlistmentFilesSkipRe = me.oEnlistmentConf.getWholeNamedArray("SkipFiles_")
			# - array of strings retrieved in this object for faster looping

			asArray = me.XoYenlistmentRoot.get("PickPaths_", ["All_"]) # implicit default: all path names are picked
			me.oEnlistmentConf.createNamedArray("PickPaths_", asArray)
			me.asEnlistmentPathsPickRe = me.oEnlistmentConf.getWholeNamedArray("PickPaths_")
			# - array of strings retrieved in this object for faster looping

			asArray = me.XoYenlistmentRoot.get("SkipPaths_", ["None_"])   # implicit default: no path names are skipped
			me.oEnlistmentConf.createNamedArray("SkipPaths_", asArray)
			me.asEnlistmentPathsSkipRe = me.oEnlistmentConf.getWholeNamedArray("SkipPaths_")
			# - array of strings retrieved in this object for faster looping

			me.oTrace.INFO("duty '" + sConfDuty + "' by file '" + sConfFile + "'")
		except:
			exctype, value = sys.exc_info()[:2]  # !: very comprehensive output
			errorText = str(exctype) + " " + str(value)
			me.oTrace.INFO("ERROR: duty '" + sConfDuty + "' '" + errorText + "'", "exception")
			#print("ERROR: duty '" + sConfDuty + "' '" + errorText + "'")
			#print(errorText)

	#=============================================	
	def setFocusFileFullName(me, sFileFullName):
	#=============================================
		me.sFocusFileFullName = sFileFullName
		me.oTrace.INFO("file '" + sFileFullName + "'")

	#=============================================	
	def checkCreatePath(me, sPathName):
	#=============================================
		sPathName = sPathName.strip()   # !: assures leading and trailing white characters absence
		if not os.path.exists(sPathName):
			me.oTrace.INFO("path '"+sPathName+"' does not exist, so it is created now")
			os.makedirs(sPathName)
		else:
			me.oTrace.INFO("path '"+sPathName+"' exists already")
	
	#=============================================	
	def tryExtractExistingPathOrFileName(me, sAnyString):
	#=============================================
		# DOES: tries to parse existing file full name from given string
		# 	-	IF found THEN returns it
		#	-	ELSE IF not found THEN tries to find string which combined with default path name forms such
		#	-	ELSE returns default file full name
		sFoundRetStatus = "NOT_EXIST"
		sFullName = "EMPTY"
		sFileName = "EMPTY"
		sFileBody = "EMPTY"
		sFileExt  = "EMPTY"
		
				
		sFileNameCandidate = removePossiblePairChars(sAnyString)  # !: python function call to non-class module
		oFileNameRe = re.compile(p_sFILE_FULL_NAME_CATCH_re)
		oMatch = oFileNameRe.match(sFileNameCandidate)
		if oMatch:
			sFullName = oMatch.group(0)
			(sPathName, sFileName, sFileBody, sFileExt) = getFileNameParts(sFullName)
			if ("YES_EXIST" == checkFileExistence(sFullName)):   # existing file name found
				sFoundRetStatus = "FILE_EXIST"
			elif ("YES_EXIST" == checkPathExistence(sFullName)):
				sFoundRetStatus = "PATH_EXIST"    # existing path name found but no file name found
			elif ("YES_EXIST" == checkPathExistence(sPathName)):
				sFoundRetStatus = "PATH_EXIST"   # existing path name found within not existing file name
			else:
				me.oTrace.INFO("no existing path or file name found in string '"+sFileNameCandidate+"'")
		else:
			me.oTrace.INFO("no valid path or file name found in string '"+sFileNameCandidate+"'")
		
		
		return (sFoundRetStatus, sFullName, sFileName, sFileBody, sFileExt)
		

	
	#=============================================	
	def assureAbsoluteFileName(me, sReferenceFileFullName, sTargetFileLinkPlentyName):   # TODO: transfer to "utils"
	#=============================================
	# converts file name from relative to absolute
	# F:\LOT\CAD\LOFT\MAP\FreeplaneExp.mm
	# href="../../../../KIT/Python/VAULT/justtest.py"
	#       LOFT -> CAD -> LOT -> E:
	# F:\KIT\Python\VAULT\justtest.py
		
		me.oTrace.INFO("BEGIN assureAbsoluteFileName()")
		me.oTrace.INFO("target file link plenty name = "+sTargetFileLinkPlentyName)
		# eg. "../../../../KIT/Python/VAULT/Python01.py>Link to Python file </a>"

		sPart=""
		sLinkAbsPathPrefix = ""
		#--------------------------------------------------------------
		asTargetRelPathParts = sTargetFileLinkPlentyName.split("./")
		nTargetRelPartsLastPos = len(asTargetRelPathParts)-1  # last "../" part
		nTargetRelPartsShiftsLastPos = nTargetRelPartsLastPos - 1 # last position of "../" -strings
		
		for sPart in asTargetRelPathParts:
			me.oTrace.INFO("target part = "+sPart)
		sWholeLinkTailPart = sPart
		me.oTrace.INFO("sWholeLinkTailPart = "+sWholeLinkTailPart)
		me.oTrace.INFO("reference file full name = "+sReferenceFileFullName)
		# eg. "F:\LOT\CAD\LOFT\MAP\FreeplaneExp.mm"
		#--------------------------------------------------------------
		asReferencePathParts 	= sReferenceFileFullName.split("\\")
		nRefFileNamePos 		= len(asReferencePathParts)-1
		nRefFileDirPos 			= nRefFileNamePos - 1
		nRefFileDirParentDirPos 	= nRefFileDirPos - 1
		
		for sPart in asReferencePathParts:
			me.oTrace.INFO("reference path part = "+sPart)
		
		nAddLinkPrefixStartPos = 0
		sAbsPathPrefix =""
		nAddLinkPrefixEndPos = nRefFileDirParentDirPos - nTargetRelPartsShiftsLastPos
		
		me.oTrace.INFO("nRefFileDirParentDirPos = "+str(nRefFileDirParentDirPos))
		me.oTrace.INFO("nTargetRelPartsShiftsLastPos = "+str(nTargetRelPartsShiftsLastPos))
		me.oTrace.INFO("nAddLinkPrefixEndPos = "+str(nAddLinkPrefixEndPos))
		
		# for nPos in range(nRefFileDirParentDirPos, 0, -1):  # steps upwardsin reference file path
			# # eg. "F:\LOT\CAD\LOFT\MAP\FreeplaneExp.mm"
			# sPart = asReferencePathParts[nRefFileParentDirPos-nPos]
			# sAbsPathPrefix = sPart + sAbsPathPrefix
			# # TODO: improve looping so, that collected path prefix can contain more than the drive letter
			
		sTargetPathPrefix  = asReferencePathParts[0]
		# sWholeLinkTailPart = sWholeLinkTailPart.replaceAll("\"","")
		sTargetFileFullName = sTargetPathPrefix + "\\"+sWholeLinkTailPart
		me.oTrace.INFO("target file full name "+sTargetFileFullName)

		# TODO: add splitting and looping ...
		
		
		return sTargetFileFullName
		
	#=============================================	
	def getTheseRootOrDrive(me): 
	#=============================================
		path = sys.executable
		while os.path.split(path)[1]:
			path = os.path.split(path)[0]
		return path


        #=============================================	
	def checkCopyCastFilesToNewDir(me, sCastFileNamesFileName, sTargetDirectory):             # TBD: 181015
	#=============================================
                ebc=123
                # shall skip executable files (*.bin, *.exe, etc.)
                # shall copy also the cast file
		
	#=============================================	
	def generateUniqueHybridFileName(me, sPathName, sFileBodyPart, sExtension):
	#=============================================
	# TODO: add returning also the relative name
		sNewFilePlainName = sFileBodyPart+"."+sExtension
		sNewFileFullName =  sPathName+"/"+sNewFilePlainName
		sFileStatus = "NOT_EXIST"
		nIndex = 1
		while (1):
			sIndex = str(nIndex)
			nIndex = nIndex + 1
			if os.path.isfile(sNewFileFullName):  # file exists already, so tries with adding an index
				sNewFilePlainName = sFileBodyPart+"_"+sIndex+"."+sExtension
				sNewFileFullName =  sPathName+"/"+sNewFilePlainName
				me.oTrace.INFO("file '"+sNewFileFullName+" 'exists already, so tries another")
			else:
				me.oTrace.INFO("file '"+sNewFileFullName+"' does NOT exist, so it can be created")
				break
		sNewFileFullName = assureForwardsSlashedName(sNewFileFullName) # for "standardising" path part delimiters
		return (sNewFileFullName, sNewFilePlainName)
		
	#=============================================	
	def findInFile(me, sReMatch, sFileName): 
	#=============================================
		# IF given regex string found in file THEN positive line number is returned
		oFileContents = clTextStorage("for search in file")
		oFileContents.rawFillFromFile(sFileName)
		(sLineNbr, sLineContents) = oFileContents.findFirst(sReMatch)
		return sLineNbr
	#=============================================
	def collectFileNamesWithInfo(me):
	#=============================================
		pass
		# TBD:add code

	#=============================================
	def writeFileNamesToFileByConf(me, sFileName):
	#=============================================
		pass
		#me.oFileNamesCollection.writeToFileByConf(sFileFullName)
		
		
	#=============================================
	##def copyFilesByNamesToGivenDir(me, sFileNamesFile, sCopyTargetDir):  # TBD: for collecting files
	#=============================================

	#=============================================
	def collectSelectTreeFileNames(me, bAttachFileAttr=False):  # root paths count is 1...N
	#=============================================
	# - to add metatdata lines to
	# http: // www.pythonforbeginners.com / code - snippets - source - code / python - os - walk /
		dAttr = {}
		bSkipPath = True
		bSkipFile = True
		sAttrCsv = ""
	
		me.oTrace.INFO("start collecting file names","topic")
		sFileFullName = ""
		try:
			for sBasePath in me.asEnlistmentBasePaths: # for multiple, separate directory trees
				me.oTrace.INFO("base path: "+sBasePath)
				for sPathFullName, asDirPlainNamesInPathFoot, asFilePlainNamesInPathFoot in os.walk(sBasePath):   # !: really compact way to collect file names
					#sFileFullName = sPathFullName + "\\" + sFilePlainName
					#print("path: " + sPathFullName)

					bSkipPath=False  # initial quess
					for sSkipRe in me.asEnlistmentPathsSkipRe:
						if sSkipRe == "None_":
							bSkipPath = False
							break
						oMatch = re.search(sSkipRe, sPathFullName)
						if oMatch:
							me.oTrace.INFO("skip path '"+sPathFullName+"' by regex '"+sSkipRe+"'")
							bSkipPath = True   #  = path name contents is skippable
							break
					if bSkipPath == False:
						bSkipPath = True # initial quess
						for sPickRe in me.asEnlistmentPathsPickRe:
							if sPickRe == "All_":
								bSkipPath = False
								break
							oMatch = re.search(sPickRe, sPathFullName)
							if oMatch:
								#print("pick path: " + sPathFullName)
								bSkipPath = False #  = path name contents is pickable
								break
					if bSkipPath == False:
						bSkipFile = False
						for sFilePlainName in asFilePlainNamesInPathFoot:
							sFileFullName = sPathFullName + "\\" + sFilePlainName
							#print("file full name: " + sFileFullName)
							for sSkipRe in me.asEnlistmentFilesSkipRe:
								if sSkipRe == "None_":
									bSkipFile = False
									break
								oMatch = re.search(sSkipRe, sFilePlainName)
								if oMatch:
									me.oTrace.INFO("skip file '" +  sFilePlainName + "' by regex '" + sSkipRe + "'")
									bSkipFile = True  # = path name contents is skippable
									break
							if bSkipFile == False:
								bSkipFile = True
								for sPickRe in me.asEnlistmentFilesPickRe:
									if sPickRe == "All_":
										bSkipFile = False
										break
									oMatch = re.search(sPickRe, sFilePlainName)
									if oMatch:
										#print("pick file: " + sFilePlainName)
										bSkipFile = False  # = path name contents is skippable
										break
							if bSkipFile == False:
								sAttrCsv = ""
								sFileFullName = sPathFullName + "\\"+sFilePlainName

								dFileAttr = getFileAttributes(sFileFullName, me.oTrace)
								for sFileAttrLbl in me.asEnlistmentFilesAttrLbl:
									if sFileAttrLbl == "None_":
										sAttrCsv=""
										break
									sNextAttr = dFileAttr.get(sFileAttrLbl,"MISSING")
									if sNextAttr == "MISSING":
										me.oTrace.INFO("file attribute by label "+sFileAttrLbl+"is missing")
										sAttrCsv=""
										break
									else:
										sAttrCsv = sAttrCsv + p_CSV_SEPARATOR + sNextAttr

								sFileFullNameAndAttr	= sFileFullName+sAttrCsv
								#print(sFileFullName)
								me.addText(sFileFullNameAndAttr)  # in parent class

		except:
			exctype, value = sys.exc_info()[:2]
			errorText = str(exctype) + " " + str(value)
			me.oTrace.INFO("collectSelectTreeFileNames() " + errorText)
		finally:
			pass


	
					
					
