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
