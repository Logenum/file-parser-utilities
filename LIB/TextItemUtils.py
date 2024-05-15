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