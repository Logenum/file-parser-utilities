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