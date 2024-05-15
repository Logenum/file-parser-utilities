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


# 170717 DONE all <join> features removed TBD: move to <edit> phase operations

# =============================================================
class clFilterTextStorage(clTextStorage):   # NOTE: seems to be unused class !!!    (180822)
# =========================================================
    def __init__(me, sDuty, oTrace, sTheseDriveLetter="N/A", sCreatorPath="N/A",
                 sCreatorName="N/A"):  # python constructor
    # =========================================================
        me.oTrace = oTrace
        me.oTrace.INFO("constructor for '" + sDuty + "'","kick")
        clTextStorage.__init__(me, sDuty, oTrace)  # # - parent class contains already 'clParams'
        me.setOperability(True, "initial quess")  # initial quess
        me.sTheseDriveLetter = sTheseDriveLetter
        me.sCreatorPath = sCreatorPath
        me.sCreatorName = sCreatorName  # creator script name
        me.sDuty = sDuty  # means the "task" or "role" of the object. Mainly used to improve Trace Log


        me.XoYfilterRoot = 0  # JSON-to-python conversion result "anchor" # TBD: add method usage
        me.asFilterPickByCfg = []    # TBD: keep
        me.asFilterSkipByCfg = []    # TBD: keep
        me.adEnableDisableByCfg  = {}    # TBD: keep
        me.oFilteringConf = 0   # TBD: keep

        me.oStEnabling = clState("enable or disable", me.oTrace)
        me.oStEnabling.setState("st_PASSING_NOT_ENABLED", "initialization")  # initial quess
        
        me.oTrace.INFO("Ended constructor for '" + sDuty + "'","kick")
        # ---------------------------------------------
        # addings from 171023
        me.nPickedLinesTotalCount     = 0
       
        me.sCurrentEnableStartRe        = "NONE"  # regex
        #----------- NEXT or PAST --------------------
        me.nEnablePassedLinesAmountGoal         = 0   # goal amount of passed lines from current line forwards or backwards
        me.nEnablePassedLinesCount              = 0   # current amount of pass lines
        me.sEnablePassedEndRegex                = "NONE"  # regex
        me.sEnablePassedTempora                 = "NONE"  # keyword: from now to next or from past to now
        #-------------------------------------------------------
        me.oPickRing = clPickedRing("fixed amount of latest picked lines", me.oTrace, 1024)
    
        # - "past" lines are already in ring collector, "next" lines are still in <feed file>
       
    #====================================================
    def assignFilterConfByJson(me, oFilteringConfByJsonFile):  # called by "STD" level scripts
    #=========================================================
        # simple filtering operations: lines are just passed, not modified at all
        # can ne used whe reading and writing of files and between buffer copying
        # TBD: replace this method with version  which uses generic navigation functions
        #   -   'PickFilter_' and 'EnableFilter_' shall be similar to current structure <DoA>
        #   -   'EnableRange_' shall be structure <DoAoD>
        #       -   the deepest dictionary shall be role-value -pairs:
        #           -   eg. [{"StartAt_":"^.*abc123.*$","EndAt_":".*666.*","Tempora" :"NEXT_"},

       try:
            me.oFilteringConf = oFilteringConfByJsonFile
            me.XoYfilterRoot = me.oFilteringConf.getXoYroot()
            #me.oTrace.setOperability(True)
            
            sConfFile = me.oFilteringConf.getAssignedFileName()
            if os.path.exists(sConfFile):
            
                sConfDuty = me.oFilteringConf.getDuty()
                print("read config JSON data from file '" + sConfFile + "'")
                me.oTrace.INFO("read config JSON data from file '"+sConfFile+"'")
    
                asArray = me.XoYfilterRoot.get("PickFilter_",["All_"])
                me.oFilteringConf.createNamedArray("PickFilter_", asArray)
                me.asFilterPickByCfg = me.oFilteringConf.getWholeNamedArray("PickFilter_")
                # - array of stringsretrieved in this object for faster looping
    
                asArray = me.XoYfilterRoot.get("SkipFilter_",["None_"])
                me.oFilteringConf.createNamedArray("SkipFilter_", asArray)
                me.asFilterSkipByCfg = me.oFilteringConf.getWholeNamedArray("SkipFilter_")
                # - array of strings retrieved in this object for faster looping
                # -------------------------------------
                adArray = me.XoYfilterRoot.get("EnableRange_","MISSING")  # point to wanted item within python data structure tree
                # - TBD: see here https://stackoverflow.com/questions/16003408/python-dict-get-with-multidimensional-dict
                me.oFilteringConf.createNamedArray("EnableRange_", adArray)
                me.adEnableDisableByCfg = me.oFilteringConf.getWholeNamedArray("EnableRange_")
                # - array of dictionaries retrieved in this object for faster looping
                me.oTrace.INFO("duty '" + sConfDuty + "' by file '" + sConfFile + "'")
            else:
                sText = "config JSON data from file '" + sConfFile + "' does NOT exist"
                me.oTrace.INFO(sText)
                #print(sText)
       except:
           exctype, value = sys.exc_info()[:2]  # !: very comprehensive output
           errorText = str(exctype) + " " + str(value)
           me.oTrace.INFO("ERROR: duty '" + me.sDuty + "' '" + errorText+"'","exception")

    # =========================================================
    def subCheckLineToPickOrSkip(me, sFeedLine):
    # =========================================================
        # TBD: evaluate this first
        #   -   if collection is not enabled, then push passed lines to ring buffer
        #   -   if collection is enabled, then append passed lines to main buffer
        #
        # TBD: add checkings for "None_" and "All_" in skip/pick cases 180216
        try:
            sRetLine = ""
            for sPassSkipRe in me.asFilterSkipByCfg:  #
                me.oTrace.INFO("pass skip regex = '"+sPassSkipRe+"' , line = '"+sFeedLine+"'")
                if sPassSkipRe == "None_":  # no lines are skipped
                    sRetLine = sFeedLine
                    break
                oMatch = re.search(sPassSkipRe, sFeedLine)
                if oMatch:  # pass
                    sRetLine = p_sIGNORABLE_LINE
                    me.oTrace.INFO("passes line '" + p_sIGNORABLE_LINE + "'")
                    return sRetLine
            for sPassPickRe in me.asFilterPickByCfg:  # tries to match first matching regex to start pass
                me.oTrace.INFO("pass pick regex = '" + sPassPickRe + "' , line = '" + sFeedLine + "'")
                if sPassPickRe == "All_":  # all lines are picked
                    sRetLine = sFeedLine
                    break
                oMatch = re.search(sPassPickRe, sFeedLine)
                if oMatch:  # pass
                    sRetLine = sFeedLine
                    me.oTrace.INFO("picks line '" + sRetLine + "'")
                    break
        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype) + " " + str(value)
            me.oTrace.INFO("subCheckLineToPickOrSkip() "+errorText)
        finally:
            if sRetLine == "":
                sRetLine = p_sIGNORABLE_LINE
            me.oTrace.INFO("returns line '"+sRetLine+"'")
        return sRetLine

    # =========================================================
    def subCheckLineIfAnyEnableOrDisable(me, sFeedLine): # for saving match lines to pick ring
    # =========================================================
        # TBD: compare feed line with all non-integer string enable/disable -values
        bStatus = False
        dEnable = me.findFirstDictByKeyMatchVal(me.adEnableDisableByCfg, "start_", sFeedLine)  # resides in <text item utils>
        if not bool(dEnable):
            dDisable = me.findFirstDictByKeyMatchVal(me.adEnableDisableByCfg, "stop_", sFeedLine)
            if bool(dDisable):
                bStatus = True
        else:
            bStatus = True
        
        return bStatus
        


    # =========================================================
    def appendFromFile(me, sFileFullName):
    # =========================================================
        return me.passFromFile(sFileFullName, "a")
    # =========================================================
    def fillFromStore(me, oStore):
    # =========================================================
        return me.passFromStore(oStore, "f")
    # =========================================================
    def appendFromStore(me, oStore):
    # =========================================================
        return me.passFromStore(oStore, "a")

    # =========================================================
    def detachPassFiltersCfg(me):  #
        # =========================================================
        me.oTrace.INFO("...")
        me.oFilteringConf = 0
    # =========================================================
    def passFromStore(me, oSource,
                      sBufferInMode):  # filtering from buffer to buffer (TBD: replace "fill" with "append")
    # =========================================================
        # uses stop/skip/do/start- regex patterns set by a specific class method
        # picks selected part of selected lines from file
        # start and stop criterias shall usually be time stamp etc. matches
        bOperStatus = False  # initial quess: will fail
        
        sBufferLine = ""
        asSrcBuffer = oSource.getContents(me)
        if sBufferInMode == "f":  # means here "fill"
            me.resetMainBuffer()

        if me.oFilteringConf == 0:  # configuration assignment check
            me.oTrace.INFO("filter configuration file is not assigned to object '" + me.sDuty + "'")
            return bOperStatus
        for sBufferLine in asSrcBuffer:
            me.incTotalFlowLineSeqNbr()
            if sBufferLine == "EOB":
                return bOperStatus
            bOperStatus = False  # initial quess
            sFilterLine = me.checkLineByFilterCfg(sBufferLine)

            if sFilterLine == p_sIGNORABLE_LINE:
                continue
            else:
                me.oTrace.INFO("line to save: '" + sFilterLine + "'")
                me.asMainBuffer.append(sFilterLine)
                me.updateEndPos()
                bOperStatus = True
        return bOperStatus

    # =========================================================
    def appendToFile(me, sFileFullName):
    # =========================================================
        return me.passToFile(sFileFullName, "a")

    # =========================================================
    def passToFile(me, sFileFullName, sFileOutMode):  # filtering from buffer to file
    # =========================================================
        # uses stop/skip/do/start- regex patterns set by a specific class method
        # TBD: add some flag usage to select fill vs. append
        me.oTrace.INFO("target file: '" + sFileFullName + "', mode='" + sFileOutMode + "'")
        bOperStatus = False
        if not isReasonableFileName(sFileFullName, me.oTrace):
            return bOperStatus
        me.sAttachedFileFullName = sFileFullName
        if not me.isFileWriteAllowed():
            return bOperStatus
        if me.oFilteringConf == 0:  # configuration assignment check
            me.oTrace.INFO("filter configuration file is not assigned to object '" + me.sDuty + "'")
            return bOperStatus
        # sFileFullName = "J:/KIT/Python/TRAY/DotAutogenMain.cfg"

        me.oTrace.INFO("write to file '" + sFileFullName + "', mode = '" + sFileOutMode + "'")

        me.fhOutFile = open(sFileFullName, sFileOutMode)  # "w" or "a" # TBD; replace with parent class file I/O


        for sBufferLine in me.asMainBuffer:
            me.incTotalFlowLineNbr()
            if sBufferLine == "EOB":
                return bOperStatus
            bOperStatus = False  # initial quess
            # print ("line = -------------------------------------- "+str(sLine)+"\n")
            sWriteLine = me.checkLineByFilterCfg(sBufferLine)

            if sWriteLine == p_sIGNORABLE_LINE:
                continue
            else:
                me.oTrace.INFO("line to write: '" + sWriteLine + "'")
                me.asMainBuffer.append(sWriteLine)
                me.updateEndPos()
                bOperStatus = True
        me.closeOutFile()

        return bOperStatus
    # =========================================================
    def passFromFileToFile(me, sFeedFileName, sTargetFileName, sWriteMode):
    # =========================================================
        # for extracting lines from huge file to easonable sized file
        # uses stop/skip/do/start- regex patterns set by a specific class method
        # picks selected part of selected lines from file
        # start and stop criterias shall usually be time stamp etc. matches
        bOperStatus = False
        if not doesFileExist(sFeedFileName):
            me.oTrace.INFO("'" + me.sDuty + "' object access file '" + sFeedFileName + "' is missing")
            me.setOperability(False, "'" + me.sDuty + "' object access file '" + sFeedFileName + "' is missing")
            return bOperStatus
        if not isReasonableFileName(sTargetFileName, me.oTrace):
            return bOperStatus
        # TBD: change to source-filter-target (=no buffer caching)
        bOperStatus = me.passFromFile(sFeedFileName, me.sBufferInMode)  # filtering occurs here
        if bOperStatus:
            bOperStatus = me.rawWriteToFile(sTargetFileName)  # already filtered lines
            if bOperStatus:
                me.oTrace.INFO(
                    "read from file '" + sFeedFileName + "' to buffer and write it to '" + sTargetFileName + "'   for '" + me.sDuty + "' ")
        return bOperStatus
        #	# TODO: add possible error check

    # =========================================================
    def passFromFile(me, sFileFullName, sBufferInMode="f"):  # filtering from file to buffer
    # =========================================================
        # uses stop/skip/do/start- regex patterns set by a specific class method
        # picks selected part of selected lines from file
        # start and stop criterias shall usually be time stamp etc. matches
        bOperStatus = False
        asFilterLines = []
        sStatus = "FAIL"  # initial quess
        if not doesFileExist(sFileFullName):
            me.oTrace.INFO("'" + me.sDuty + "' object access file '" + sFileFullName + "' is missing")
            me.setOperability(False,"'" + me.sDuty + "' object access file '" + sFileFullName + "' is missing")
            return bOperStatus
        else:
            pass
            # me.oTrace.INFO("read from file '" + sFileFullName + "' for '" + me.sDuty + "' ")

        if me.oFilteringConf == 0:  # configuration assignment check
            me.oTrace.INFO("filter configuration file is not assigned to object '" + me.sDuty + "'")
            return bOperStatus
        if sBufferInMode == "f":  # "f" means here "fill"
            me.resetMainBuffer()
        # raw Feed File can be HUGE, so buffer is not filled with it
        try:
            me.fhInFile = open(sFileFullName)  # file may be huge, so it is not fully stored
            me.oTrace.INFO("start reading lines from file '[" + sFileFullName + "]'")
            for sFeedLine in me.fhInFile:
                 ###me.incTotalFlowLineNbr()
                sFeedLine = sFeedLine.rstrip()   # Python: removes line feed (https://stackoverflow.com/questions/275018/how-can-i-remove-chomp-a-newline-in-python)
                bOperStatus = False  # initial quess
                #me.oTrace.INFO("line '" + sFeedLine + "' from file '"+sFileFullName+"'")
                #print ("sFeedLine = '"+sFeedLine+"'")
                asFilterLines = me.checkLineByFilterCfg(sFeedLine)
                if asFilterLines == [p_sIGNORABLE_LINE]:
                    #me.oTrace.INFO("line NOT to save: '" + sFilterLine + "'")
                    continue
                else:
                    #me.oTrace.INFO("line to save: '" + sFilterLine + "'")
                    # me.asMainBuffer.append(sFilterLine)
                    me.oTrace.INFO("append array to buffer")
                    me.asMainBuffer = me.asMainBuffer + asFilterLines
                    #me.asMainBuffer.append(sFilterLine)
                    me.updateEndPos()
                    bOperStatus = True
            me.sAttachedFileFullName = sFileFullName
            me.fhInFile.close()
        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype) + " " + str(value)
            me.oTrace.INFO(errorText, "exception")
        return bOperStatus

    #	# TODO: add possible error check

    #=========================================================
    def checkLineByFilterCfg_OLD(me, sFeedLine):  # contains configuration file array loopings
    # =========================================================
        # structure: multi-level state machine, which calls sidekick-subroutines and ordinary functions
        # pass filter values are arrays which are downloaded from configuration JSON file
        # passes, ignores
        # the source of the <FEED LINE> ant target of <RET LINE> unknown within this function
        bHandling = True
        
        asRetLines = [p_sIGNORABLE_LINE]  # array of single string
        # sRetLine = p_sIGNORABLE_LINE  # initial quess: file is ignored
        # me.oTrace.INFO("sFeedLine = '" + sFeedLine + "'","topic")
        # print("sFeedLine = '" + sFeedLine + "'\n")
        try:
           
            # me.oTrace.INFO("...")
            
            sFeedLine = sFeedLine.rstrip()  # !: Python way for a "chomp"
            sPickCheckLine = me.subCheckLineToPickOrSkip(sFeedLine)
            me.oTrace.INFO("sPick.Check.Line = '" + sPickCheckLine + "'")
            if sPickCheckLine == p_sIGNORABLE_LINE: # this "OLD" function uses pich
                pass
            else:
                me.oTrace.INFO("append line '" + sPickCheckLine + "' to pick ring")
                me.oPickRing.append(sPickCheckLine)
                # me.appendToPastRingCollector(sPickCheckLine)  # fixed amount of latest picked lines are saved here
                # print ("sPickCheckLine raw = " + sPickCheckLine)
                # -----------------------------------------
                if me.oStEnabling.isState("st_PASSING_NOT_ENABLED") == True:
                    # -----------------------------------------
                    # print ("sPickCheckLine first  = " + sPickCheckLine)
                    # me.subCheckIfEnableStart(sPickCheckLine) # for single-type JSON
                    me.subCheckIfEnableStart(sPickCheckLine)
    
                # -----------------------------------------
                if me.oStEnabling.isState("st_PASSING_NOT_ENABLED") == False:  # some picking Enabled
                    # -----------------------------------------
                    # print ("sPickCheckLine last = " + sPickCheckLine)
                    asRetLines = me.subCollectUpToEnableEnd(sPickCheckLine)
                
                if me.asRetLines != [p_sIGNORABLE_LINE]:
                    me.oTrace.INFO("asRetLines = '" + str(asRetLines) + "'")
                    # return sRetLine  # TBD: add indication string to tell caller if to append ring buffer to lines buffer
        
        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype) + " " + str(value)
            me.oTrace.INFO(errorText, "exception")
        finally:
            me.oTrace.INFO("return array " + arrayToStr(asRetLines) + " ")
            return asRetLines
        
        
        # TBD: now caller assumes status !  TBD change to return 0 0r 1 lines
    # Returns usually an array of single string. Longer arrays are ring buffer collections
    # when enabling terminator is negative integer
    #=========================================================
    def checkLineByFilterCfg(me, sFeedLine):  # contains configuration file array loopings
    #=========================================================
        # structure: multi-level state machine, which calls sidekick-subroutines and ordinary functions
        # pass filter values are arrays which are downloaded from configuration JSON file
        # passes, ignores
        # the source of the <FEED LINE> ant target of <RET LINE> unknown within this function
        bHandling = True
        bAppendLineToRing = False
        
        asRetLines = [p_sIGNORABLE_LINE]  # array of single string

        try:
        # TBD: change enable/disable line check done BEFORE pick/skip check
        # me.oTrace.INFO("...")
         
            sFeedLine = sFeedLine.rstrip()  # !: Python way for a "chomp"

            if me.subCheckLineIfAnyEnableOrDisable(sFeedLine): #  limiter lines are always added to pick ring
                bAppendLineToRing = True
                me.oTrace.INFO("append trigger line '" + sFeedLine + "' to pick ring")
            else:
                sPickCheckLine = me.subCheckLineToPickOrSkip(sFeedLine)
                if sPickCheckLine != p_sIGNORABLE_LINE:
                    bAppendLineToRing = True
                    me.oTrace.INFO("append pass line '" + sFeedLine + "' to pick ring")

            if bAppendLineToRing:
                me.oPickRing.append(sFeedLine)
                #me.appendToPastRingCollector(sPickCheckLine)  # fixed amount of latest picked lines are saved here
                #print ("sPickCheckLine raw = " + sPickCheckLine)
                #-----------------------------------------
                if me.oStEnabling.isState("st_PASSING_NOT_ENABLED"):
                #-----------------------------------------
                    #print ("sPickCheckLine first  = " + sPickCheckLine)
                    #me.subCheckIfEnableStart(sPickCheckLine) # for single-type JSON
                    me.subCheckIfEnableStart(sFeedLine)
                 
                #-----------------------------------------
                if me.oStEnabling.isStateNot("st_PASSING_NOT_ENABLED"):  # some picking Enabled
                #-----------------------------------------
                    #print ("sPickCheckLine last = " + sPickCheckLine)
                    asRetLines = me.subCollectUpToEnableEnd(sFeedLine)
                    
                if me.asRetLines != [p_sIGNORABLE_LINE]:
                    me.oTrace.INFO("asRetLines = '" + str(asRetLines) + "'")
                # return sRetLine  # TBD: add indication string to tell caller if to append ring buffer to lines buffer

        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype) + " " + str(value)
            me.oTrace.INFO(errorText,"exception")
        finally:
            me.oTrace.INFO("return array "+arrayToStr(asRetLines)+" ")
            return asRetLines


    # TBD: now caller assumes status !  TBD change to return 0 0r 1 lines
    # Returns usually an array of single string. Longer arrays are ring buffer collections when enabling terminator is negative integer

    #=========================================================
    def setEnablePassedEndRegex(me, sRegex):
    #=========================================================
        me.sEnablePassedEndRegex =  sRegex
        me.oTrace.INFO("shall pass up to '" + sRegex + ", direction is "+me.sEnablePassedTempora)

    #=========================================================
    def getEnablePassedEndRegex(me):
    #=========================================================
        return me.sEnablePassedEndRegex
    # =========================================================
    def setEnablePassedLinesAmountGoal(me, sCnt):
    # =========================================================
        me.nEnablePassedLinesAmountGoal = int(sCnt)
        me.oTrace.INFO("shall pass '" + sCnt + "' picked lines, direction is "+me.sEnablePassedTempora)
        me.nEnablePassedLinesCount = 0


    # =========================================================
    def getEnablePassedLinesAmountGoal(me):
    # =========================================================
        return me.nEnablePassedLinesAmountGoal
    # =========================================================
    def getEnablePassedLinesAmountGoalAsStr(me):
    # =========================================================
        return str(me.nEnablePassedLinesAmountGoal)

    # =========================================================
    def checkIncEnablePassedLinesCount(me):
    #=========================================================
        bRetVal = False
        me.nEnablePassedLinesCount = me.nEnablePassedLinesCount + 1
        if me.nEnablePassedLinesCount >= me.nEnablePassedLinesAmountGoal:
            me.oTrace.INFO("Now passed all " + str(me.nEnablePassedLinesAmountGoal) + " picked lines to direction '"+me.sEnablePassedTempora+"'")
            bRetVal = True
        else:
            me.oTrace.INFO("Now passed " + str(me.nEnablePassedLinesCount) + " picked lines to direction '"+me.sEnablePassedTempora+"'")
            bRetVal = False

        return bRetVal

    #=========================================================
    def setEnablePassedTempora(me, sTempora):
    #=========================================================
        me.sEnablePassedTempora = sTempora
        me.oTrace.INFO("enable passed direction = '" + me.sEnablePassedTempora+"'")

    #=========================================================
    def getEnablePassedTempora(me, sTempora):
    #=========================================================
        return me.sEnablePassedTempora
    #=========================================================
    def isEnablePassedTempora(me, sTempora):
    #=========================================================
        if me.sEnablePassedTempora == sTempora:
            return True
        else:
            return False

    #=========================================================
    def setEnablePassedStartRegex(me, sRegex):
    #=========================================================
        me.sCurrentEnableStartRe = sRegex
        me.oTrace.INFO("start enable passing if '"+me.sCurrentEnableStartRe+"' encountered")

    # =========================================================
    def subCheckIfEnableStart_OLD(me, sFeedLine):  # IDEA: prefix "sub" indicates old-fashioned "subroutine"
    # =========================================================
        try:
            sEnableStartRe, sEnableEndReOrCnt, sEnableTempora = me.findKeyMatchWithDualValues(sFeedLine) # TBD: replace this !!!!

            me.oTrace.INFO(" '"+sEnableStartRe+"' '"+ sEnableEndReOrCnt+"' '"+ sEnableTempora+"' by feed line '"+sFeedLine+"'")
            if sEnableStartRe != "NONE":
                me.setEnablePassedTempora(sEnableTempora)
                me.setEnablePassedStartRegex(sEnableStartRe)
                if isIntStr(sEnableEndReOrCnt):
                    me.setEnablePassedLinesAmountGoal(sEnableEndReOrCnt)
                    if me.isEnablePassedTempora(p_sOPER_TO_NEXT):
                        me.oStEnabling.setState("st_ENABLE_UP_TO_NEXT_COUNT")
                    elif me.isEnablePassedTempora(p_sOPER_FROM_PAST):
                        me.oStEnabling.setState("st_ENABLE_FROM_PAST_COUNT")  # uses sidekick ring buffer
                    else:
                        me.oTrace.INFO("no lines-count collection because direction is '" + sEnableTempora + "'")
                else:  # enable end is regex
                    me.setEnablePassedEndRegex(sEnableEndReOrCnt)
                    if me.isEnablePassedTempora(p_sOPER_TO_NEXT):
                        me.oStEnabling.setState("st_ENABLE_UP_TO_NEXT_REGEX")
                    elif  me.isEnablePassedTempora(p_sOPER_FROM_PAST):
                        me.oStEnabling.setState("st_ENABLE_FROM_PAST_REGEX")  # uses sidekick ring buffer
                    else:
                        me.oTrace.INFO("no regex-target collection because direction is '" + sEnableTempora + "'")
            else:
                pass  # no enable start
        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype) + " " + str(value)

            me.oTrace.INFO(errorText,"exception")

    # =========================================================
    def subCheckIfEnableStart(me, sFeedLine):  # IDEA: prefix "sub" indicates old-fashioned "subroutine"
    # =========================================================
        me.oTrace.INFO("sFeed Line = "+sFeedLine)
        try:
            dEnable = me.findFirstDictByKeyMatchVal(me.adEnableDisableByCfg, "start_", sFeedLine)  # resides in <text item utils>
            if dEnable == 0:
                return
            sEnableStartRe      = dEnable.get("start_","NONE")
            sEnableEndReOrCnt   = dEnable.get("stop_","NONE")
            sEnableTempora      = dEnable.get("dir_","NONE")
            me.oTrace.INFO(" '"+sEnableStartRe+"' '"+ sEnableEndReOrCnt+"' '"+ sEnableTempora+"' by feed line '"+sFeedLine+"'")
            if sEnableStartRe != "NONE":
                me.setEnablePassedTempora(sEnableTempora)
                me.setEnablePassedStartRegex(sEnableStartRe)
                if isIntStr(sEnableEndReOrCnt):  # numeric value to back or forth
                    me.setEnablePassedLinesAmountGoal(sEnableEndReOrCnt)
                    if me.isEnablePassedTempora("NEXT_"):
                        me.oStEnabling.setState("st_ENABLE_UP_TO_NEXT_COUNT")
                    elif me.isEnablePassedTempora("PREV_"):
                        me.oStEnabling.setState("st_ENABLE_FROM_PAST_COUNT")  # uses pick ring
                    else:
                        me.oTrace.INFO("no lines-count collection because direction is '" + sEnableTempora + "'")
                else:  # enable end is regex
                    me.setEnablePassedEndRegex(sEnableEndReOrCnt)
                    if me.isEnablePassedTempora("NEXT_"):
                        me.oStEnabling.setState("st_ENABLE_UP_TO_NEXT_REGEX")
                    elif  me.isEnablePassedTempora("PREV_"):
                        me.oStEnabling.setState("st_ENABLE_FROM_PAST_REGEX")  # uses pick ring
                    else:
                        me.oTrace.INFO("no regex-target collection because direction is '" + sEnableTempora + "'")
            else:
                pass  # no enable start
        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype) + " " + str(value)
            me.oTrace.INFO(errorText,"exception")

    # =========================================================
    def subCollectUpToEnableEnd(me, sFeedLine):  # IDEA: prefix "sbr" indicates old-fashioned "subroutine"
    # =========================================================
        # hendles fresh lines one by one
        # handles array of past lines within called method
        # this method will return an ARRAY of lines
        asRet=[]
        try:
            sState = me.oStEnabling.getState()
            me.oTrace.INFO("the state: '" + sState + "'")
            if sState == "st_ENABLE_UP_TO_NEXT_COUNT":
                if me.checkIncEnablePassedLinesCount():
                    me.oStEnabling.setState("st_PASSING_NOT_ENABLED")
                asRet = [sFeedLine]  # single item array
            elif sState == "st_ENABLE_FROM_PAST_COUNT":
                asRet = me.oPickRing.copyRangeFromPastToNow(me.getEnablePassedLinesAmountGoalAsStr())
                me.oStEnabling.setState("st_PASSING_NOT_ENABLED")
            elif sState == "st_ENABLE_UP_TO_NEXT_REGEX":
                if me.tryMatchWithoutCatch(sFeedLine, me.getEnablePassedEndRegex()):
                    me.oStEnabling.setState("st_PASSING_NOT_ENABLED")
                asRet = [sFeedLine]  # single item array
            elif sState == "st_ENABLE_FROM_PAST_REGEX":
                asRet = me.oPickRing.copyFromLatestReToEnd(me.getEnablePassedEndRegex())
                me.oStEnabling.setState("st_PASSING_NOT_ENABLED")
            else:
                me.oTrace.INFO("ERROR: unknown state '" + sState + "'")
        except:
            exctype, value = sys.exc_info()[:2]
            errorText = str(exctype) + " " + str(value)
            me.oTrace.INFO(errorText, "exception")
        return asRet


