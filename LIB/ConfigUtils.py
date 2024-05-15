import os, sys
import os.path
import re
import time
import datetime
import json
# TBD: try "json5" https://stackoverflow.com/questions/27885397/how-do-i-install-a-python-package-with-a-whl-file
# C:\LOT>Pip install json5-0.2.4-py2.py3-none-any.whl installed it to c:\Python35 !!!
import copy   # !: Python for copying complex data structures
import pprint   #!: Python "Dumper" (https://docs.python.org/2/library/pprint.html)
# import commentjson     # !: pip install commentjson<cr> ; works or not ??????

#from TextStoreUtils import *
from NotetabUtils import *
from StateUtils import *
# from StringUtils import *
from TrickUtils import *

from TextStorageUtils import *

# PURPOSE: converts various ("standard") configuration files to Python data structures
# TBD: add classes for XML, HTML, INI etc. files
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class clByJson(clNotetab):  # because Notetab shall be the "IDE"
#class clByJson(clTextStorage):  # because Notetab shall be the "IDE"
# https://commentjson.readthedocs.io/en/latest/
# -		makes it possible to include comments in JSON file
# https://docs.python.org/2/library/json.html

# TBD: change clNotetab as a parent class 170120
# shall contain methods, which make "flattened" copies of (complex) data structure level parts
#	-	called at initialization phase by peer level modules
# shall contain methods which access and or iterates those "flattened" copies of data
#	-	called at runtime by peer level modules
	#=========================================================
	def __init__(me, sConfigFileName, sDuty, oTrace, sTheseDriveLetter="N/A", sCreatorPath="N/A", sCreatorName="N/A"):  # python constructor
	#=========================================================
		# IDEA: JSON file is read and buffer filled immediately in constructor, because each object is devoted to a single input JSON file
	    # TBD: add possibility for single object to manage several configuration files, which are splitted by parent class 170121 
		# TBD: remove "sStructType" parameters (171108)
		#  - JSON structure conversion result shall be saved to "me.XoYtreeFromCfgJsonFile"
		#	-	each using LIB module shall have hard-coded parsing logic of "cfg....()" functions

		#  TBD: copy structure arrays as 'flatteded' array objects
		# 	-	see https://stackoverflow.com/questions/13368498/python-object-as-dictionary-value
		me.oTrace = oTrace
		me.sDuty = sDuty
		#me.setOperability(False, "Initial Quess")

		me.sConfigFileName = sConfigFileName
		clNotetab.__init__(me, sDuty, me.oTrace)
		if not os.path.exists(sConfigFileName):  # eg. for optional rewording configuration file
			if 'json' in sConfigFileName:
				sText = "Configuration JSON file " + sConfigFileName + "' does NOT exist"
				me.oTrace.INFO("ERROR: "+sText+", end configuration")
				#print(sText)
			me.setOperability(False, "'" + sDuty + "' object access file '" + sConfigFileName + "'")
			return None

		
		me.oTrace.INFO("Configuration file '" + sConfigFileName + "'","topic")
		
		# TBD: add part "Branch" to symbol names to indicate focus node in data structure

		me.XoYtreeFromCfgJsonFile			= 0  # root of whole data structure
		me.XoYfocusBranch					= 0  # changeable reference location for <get AoD> -type functions
		me.XoYfocusBranchType				= "" # for checking and tracing purposes
		me.dNamedArrayXoYobjects 				= {}  # type is 'DoX'
		
		me.aCfgFocusArray			= []  # used when navigating arbitrary complex data structure (XoY)
		me.dCfgFocusDict			= {}  # used when navigating arbitrary complex data structure (XoY)
		me.nCfgFocusArrayPos		= 0
		me.nCgfFocusArrayLastPos 	= 0
		me.aCfgFocusAoD 			= []   # e.g. collection start,stop and dir

		me.nArrayPos 		= 0
		me.nAoDPosLast 		= 0
		me.nAoDPosNow 		= -1
		# me.bSomeDKeyValFailed 	= False  # for script interruption usage
		me.bUsedLastInAoD 	= False  # to indicate array end
		me.dNowD 			= 0		# IDEA: naming convention: using "now" instead of "focus"

		
		# clTextStorage.__init__(me, "config JSON handler", me.oTrace)  # !: initializing parent class early
		# file access check transferred here after member definitions
		# -	makes it possible to create object and call its methods (which will return "0" etc. )
		# ---> 	e.g. Reword configuration file can be disabled in main configuration JSON file
		#		without needing to disable object creation and method call in application script


		#clNotetab.__init__(me, sDuty , me.oTrace)
		#me.setOperability(True,"initial quess")   # initial ques
		if not doesFileExist(sConfigFileName):
			me.setOperability(False,"'"+sDuty+ "' object access file '" + sConfigFileName + "' is missing")
			return
		else:
			pass
			#print("uses file '"+sConfigFileName+"' for '"+sDuty+"'")
		me.sConfigFileName = sConfigFileName

		sPathName, sFileName, sFileBody, sFileExt = getFileNameParts(sConfigFileName)
		sConfigJsonFileName = sPathName+sFileBody+p_sWORK_FILE_NAME_IND_STR+".JSON"

		# TBD: wrap JSON preprocessing into a new function
		#sPureJsonWorkFileFullName = sConfigFileName+".tmp"
		me.rawFillFromFile(sConfigFileName)  # assumed to be JSON file with possible line comments
		me.pickLinesBetweenTags(p_sTAGGY_FILE_ACTIVE_PART_START_IND_CATCH_re, p_sTAGGY_FILE_ACTIVE_PART_END_IND_CATCH_re)
		me.removeLineTailsByTags(["#", "//"])  # removes possible line comments
		me.removePossibleOtlArtifacts() # eg. Notetab links, headings, etc.
		me.rawWriteToFile(sConfigJsonFileName) # JSON file without line comments




#fhJson = open(sConfigJsonFileName,"r")

	#============================================================================
		bStatus = me.openInFile(sConfigJsonFileName)  # file open wrapper added 170826
		if bStatus == False:
			return

		me.oTrace.INFO("starts load data from JSON file '"+sConfigJsonFileName+"'")
		me.XoYtreeFromCfgJsonFile = json.load(me.fhInFile)
		me.XoYfocusBranch = me.XoYtreeFromCfgJsonFile
	
		

		#me.cfgSetRoot(me.XoYtreeFromCfgJsonFile,"initialization")

		me.closeInFile()
	#================================================================================

		sPythonStructAsStr = pprint.pformat(me.XoYtreeFromCfgJsonFile)
		#pprint.pprint(me.AoX)    # STATUS: works OK: prints non-commented Python Struct
		#print("Python struct from JSON "+sPythonStructAsStr) # TBD working

		me.oTrace.INFO("Python struct from JSON " + sPythonStructAsStr)  # TBD working
		# TBD: remove single type definitions like "AoD" to allow multi-type JSON structures



	#=========================================================
	def getAoDPosInfo(me):
	#=========================================================
		sPosNow = str(me.nAoDPosNow)
		sPosLast = str(me.nAoDPosLast)
		sRet = sPosNow+"/"+sPosLast
		return sRet

	#=========================================================
	def getDuty(me):
	#=========================================================
		return me.sDuty

	#=========================================================
	def getAssignedFileName(me):
	#=========================================================
		return me.sConfigFileName

	#=========================================================
	def getNextInAoD(me): # next dictionary member of Python array
	#=========================================================
		#me.bUsedLastInAoD = False
		dRet = 0  # initial quess: overflow
		#me.oTrace.INFO("position now/last = "+str(me.nAoDPosNow)+"/"+ str(me.nAoDPosLast))
		if me.bUsedLastInAoD == True:
			me.oTrace.INFO("#1: last item at pos '"+str(me.nAoDPosLast)+"' getting already done, so nothing to get now. (object duty:'"+me.sDuty+"')")
			dRet=0
		else:
			me.nAoDPosNow += 1    # !: Python: incrementation: plus BEFORE assign
			#me.oTrace.INFO("get dict at array position "+str(me.nAoDPosNow))
			if me.nAoDPosNow == me.nAoDPosLast:
				me.bUsedLastInAoD = True		# dRet = 0
			dRet = me.AoD[me.nAoDPosNow]
			sDictAsStr = anyDictToStr(dRet)
			me.oTrace.INFO("#1: "+str(me.nAoDPosNow)+"["+ str(me.nAoDPosLast)+"] = '"+sDictAsStr+"'")
			#me.oTrace.INFO("from position '"+str(me.nAoDPosNow)+"'")
		me.dNowD = dRet
		return dRet

	#=========================================================
	def findFirstByKeyWithValInAoD(me, sTryKey, sTryVal):  # TBD: change to match to role/value pair
	#=========================================================
		me.oTrace.INFO("try key = '"+sTryKey+"'")
		me.rewindAoD()
		dDictInA = 0
		bLooping=True
		while bLooping:
			dDictInA = me.getNextInAoD()
			sDictInA = anyDictToStr(dDictInA)
			me.oTrace.INFO("dict = " + sDictInA)
			if me.alreadyUsedLastInAoD():
				break
			for sKey, sVal in dDictInA.items():
				if sKey == sTryKey:
					if sVal == sTryVal:
						me.oTrace.INFO("key/tryKey/val/tryVal = " + sKey + "/" + sTryKey + "/" + sVal + "/" + sTryVal)
						bLooping = False
					break
		return dDictInA

	#=========================================================
	def findAndRemoveFirstByKeyWithValInAoD(me, sTryKey, sTryVal):  # TBD: change to match to role/value pair
	#=========================================================
		me.oTrace.INFO("try key = '"+sTryKey+"'")
		me.rewind()
		dDictInA = 0
		while True:
			dDictInA = me.getNextInAoD()
			sDictInA = anyDictToStr(dDictInA)
			me.oTrace.INFO("dict = " + sDictInA)
			if me.alreadyUsedLastInAoD():
				break
			for sKey, sVal in dDictInA.items():
				if sKey == sTryKey:
					if sVal == sTryVal:
						me.oTrace.INFO("key/tryKey/val/tryVal = " + sKey + "/" + sTryKey + "/" + sVal + "/" + sTryVal)
						me.removeDfromAoD(me.nAoDPosNow)   # !: removes item from array
					break
		return dDictInA

	# =========================================================
	def removeDfromAoD(me, nPos): # for special values which are stored and not involved in loopings
	# =========================================================
		#me.oTrace.INFO("pops away 'AoD[" + str(me.nPos) + "]'")
		#me.AoD.pop(me.nPos)
		#me.nAoDPosLast -= 1
		pass

	#=========================================================
	def getSameAgainInAoD(me): # next dictionary member of Python array
	#=========================================================
		dRet = me.XoYfocusBranch[me.nAoDPosNow]
		sDictAsStr = anyDictToStr(dRet)
		me.oTrace.INFO("#1: " + str(me.nAoDPosNow) + "[" + str(me.nAoDPosLast) + "] = '" + sDictAsStr + "'")

		return dRet

	#=========================================================
	def rewindAoD(me): # next dictionary member of Python array
	#=========================================================
		me.nAoDPosNow = -1
		me.oTrace.INFO("#1: " + str(me.nAoDPosNow) + "[" + str(me.nAoDPosLast))
		me.bUsedLastInAoD = False
	#=========================================================
	def goGetFirstInAoD(me): # next dictionary member of Python array
	#=========================================================
		me.oTrace.INFO("called")
		me.rewindAoD()
		dRet = me.getNextInAoD()
		return dRet
	#=========================================================
	def getValInNowD(me, sKey): # e.g. getting eExtractor <next shift> -parameter before calling the actual eExtraction method
	#=========================================================
		sRetVal = me.XoYfocusBranch.get(sKey, "MISSING")
		return sRetVal
	
	#=========================================================
	def getWholeDict(me): # whole dictionary of D
	#=========================================================
		if me.isNotOperable():
			return 0
		if me.sStructType == "D":
			me.dNowD = me.D
			return me.D
		else:
			me.oTrace.INFO("ERROR: this method call is not valid for struct type '"+me.sStructType+"'")
			return 0
	
	#=========================================================
	def getWholeAoD(me): # 
	#=========================================================
		if me.isNotOperable():
			return 0
		if me.sStructType == "AoD":
			return me.XoYfocusBranch
		else:
			me.oTrace.INFO("ERROR: this method call is not valid for struct type '"+me.sStructType+"'")
			return 0
	
	#=========================================================
	def getWholeDoA(me): # 
	#=========================================================
		if me.isNotOperable():
			return 0
		if me.sStructType == "DoA":
			return me.XoYfocusBranch
		else:
			me.oTrace.INFO("ERROR: this method call is not valid for struct type '"+me.sStructType+"'")
			return 0
	#=========================================================
	def getWholeA(me): #
	#=========================================================
		if me.isNotOperable():
			return 0
		if me.sStructType == "A":
			return me.XoYfocusBranch
		else:
			me.oTrace.INFO("ERROR: this method call is not valid for struct type '"+me.sStructType+"'")
			return 0



	#=========================================================
	def getArrayInDoA(me, sKey): # next dictionary member of Python array
	#=========================================================
		asRet = []  # initial quess: empty array
		asNone = ["MISSING"]  # TBD: change to ["MISSING"]
		asRet = me.XoYfocusBranch.get(sKey, asNone)
		sArrayAsStr = '<cr>'.join(asRet)
		me.oTrace.INFO("key '"+sKey+"' gave array ~"+sArrayAsStr+"~")
		return asRet
		
	#=========================================================
	def alreadyUsedLastInAoD(me): # next dictionary member of Python array
	#=========================================================
		me.oTrace.INFO("already used: "+str(me.bUsedLastInAoD))

		return me.bUsedLastInAoD
		
	#=========================================================
	def getInD(me, sKey): 
	#=========================================================
		sRet = me.XoYfocusBranch.get(sKey, "MISSING")
		
		if sRet == "MISSING":
			#print("No value for '"+sKey+"' found in file '"+me.sConfigFileName+"'")
			me.oTrace.INFO("key '"+sKey+ "' returned value '"+sRet+"'")
			# me.bSomeDKeyValFailed = True # TBD: more usages # no error generation, because "reword" configuration must be robust
				#TBD ...continue
		return sRet
	#=========================================================
	#def someDKeyValFailed(me): 
	#=========================================================
		#me.bSomeDKeyValFailed

# https://stackoverflow.com/questions/1867861/python-dictionary-how-to-keep-keys-values-in-same-order-as-declared
#   navigation routines to be used when parsing arbitrary data structute (converted fron JSON)
#	def navGetNextArrayInArray(me):
	#----------------------------------------------------
	def getArrayInDict(me, sKey):                         # TBD: remove ???
	#----------------------------------------------------
		if me.XoYfocusBranchType == "TYPE_DICT":
			asRet = []  # initial quess: empty array
			asNone = ["MISSING"]  # TBD: change to ["MISSING"]
			asRet = me.dCfgFocusDict.get(sKey, asNone)
			sArrayAsStr = '<cr>'.join(asRet)
			me.oTrace.INFO("key '" + sKey + "' gave array ~" + sArrayAsStr + "~")
			return asRet
		else:
			me.oTrace.INFO("error: focus branch is "+me.XoYfocusBranchType)
			return 0
	#-------------------------------------
	def getDictInDict(me,sKey):				# TBD: remove ???
	#-------------------------------------
		dRet = {}  # initial quess: empty array
		dRet = me.dCfgFocusDict.get(sKey, None)
		sDictAsStr = anyDictToStr(dRet)
		me.oTrace.INFO("key '" + sKey + "' gave dictionary ~" + sDictAsStr + "~")
		return dRet
	#-------------------------------------
	def getValsByKeysInFocusAoD(me, asKeys):			# TBD: remove ???
	#-------------------------------------
		asRetVals = []
		dTmp = me.aCfgFocusArray[nFocusAoDpos]
		for sKey in asKeys:  # e.g. "start_", "stop_" and "dir_"
			sVal = dTmp.get(sKey,"MISSING")
			asRetVals.append(sVal)
		return asRetVals
	
	################################################################################################
	################################################################################################
	# TBD: collect all usable data and methods here
	#=======================================================
	def getXoYroot(me):   # caller uses as a starting point when it creates flat arrays back into THIS object  # TBD: remove ???
	#=======================================================
		xRetVal = 0
		if me.isOperable():
			sPythonXoYstructAsStr = pprint.pformat(me.XoYtreeFromCfgJsonFile)
			me.oTrace.INFO("Data structure from JSON '"+sPythonXoYstructAsStr+"'")
			xRetVal = me.XoYtreeFromCfgJsonFile
		else:
			me.oTrace.INFO("ERROR: configuration data structure does not exist")
		return xRetVal
			# TBD: add trace

	#=======================================================
	def setXoYfocusBranch(me, xDictOrArray, sComment = ""):   # TBD: remove ???
	#=======================================================
		me.XoYfocusBranchType = "TYPE_MISSING"
		me.XoYfocusBranch = xDictOrArray
		if type(xDictOrArray) is dict:
			me.XoYfocusBranchType = "TYPE_DICT"
		elif type(xDictOrArray) is list:
			me.XoYfocusBranchType= "TYPE_ARRAY"
		else:
			me.oTrace.INFO("UNKNOWN data type")
			me.setOperability(False, "UNKNOWN data type")
		me.oTrace.INFO("config structure type is '"+me.XoYfocusBranchType+"'")
	
	#=======================================================
	def getXoYfocusBranch(me):   # TBD: remove ???
	#=======================================================
		if me.XoYfocusBranchType == "TYPE_MISSING":
			return me.XoYfocusBranch

	#=======================================================
	def getXoYfocusBranchType(me):   # TBD: remove ???
	#=======================================================
		return me.XoYfocusBranchType
		
	#=======================================================
	def createNamedArray(me, sKeyName, axArray):
	#=======================================================
		sContentsAsStr = str(axArray)
		me.oTrace.INFO("array name/contents as str = '"+sKeyName+"'/'"+sContentsAsStr+"'")
		oItemsArray = clItemsArray(sKeyName, me.oTrace)    # can contain scalar, array, dictionary or object
		oItemsArray.fillArrayItems(axArray)  # fills the array

		me.oTrace.INFO("assign array object to local array")
		me.dNamedArrayXoYobjects[sKeyName] = oItemsArray     # can be scalar, array, dictionary or object
		me.oTrace.INFO("local array '"+sKeyName+"' created")
	#=======================================================
	def	getNamedArrayNextItem(me,sArrayName): 					# TBD: remove ???
	#=======================================================
		oItemsArray = me.dNamedArrayXoYobjects.get(sArrayName)
		xItems = oItemsArray.getNextArrayItem()
		if xItems == 0:
			 oItemsArray.rewind()
		return xItems
	
	#=======================================================
	def	getWholeNamedArray(me,sArrayName): 					# TBD: remove ???
	#=======================================================
		axRet = me.dNamedArrayXoYobjects[sArrayName].getWholeArray()
		return axRet


		

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#class clXmlConv(clTextStore): 

# OTL syntax configuration files data eExtraction occurs in NotetabUtils.py



